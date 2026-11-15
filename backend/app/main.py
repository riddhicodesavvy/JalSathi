import csv
import io
import json
import logging
import os
import time
from contextlib import asynccontextmanager
from uuid import UUID, uuid4

from fastapi import FastAPI, File, HTTPException, Query, Request, UploadFile
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, Response
from pydantic import ValidationError
from sqlalchemy import select
from starlette.exceptions import HTTPException as StarletteHTTPException

from backend.app.database import Analysis, Batch, Session
from backend.app.csv_export import safe_csv_cell
from backend.app.inference import Registry
from backend.app.reporting import generate_report
from backend.app.schemas import BatchResponse, Prediction, Sample
from backend.app.standards import REFERENCES
from ml.data import FEATURES, ROOT, load_dataset, summarize

logger = logging.getLogger("jalsathi")
logging.basicConfig(level=logging.INFO, format="%(message)s")


@asynccontextmanager
async def lifespan(app):
    app.state.registry = Registry()
    frame, fingerprint = load_dataset()
    app.state.summary = summarize(frame, fingerprint)
    yield


app = FastAPI(title="JalSathi API", version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("JALSATHI_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(","),
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    start = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        logger.exception("Unhandled API failure")
        return JSONResponse(
            status_code=500, content={"error": {"message": "Internal server error. See server logs."}}
        )
    logger.info(
        json.dumps(
            dict(
                method=request.method,
                path=request.url.path,
                status=response.status_code,
                elapsed_ms=round((time.perf_counter() - start) * 1000),
            )
        )
    )
    return response


@app.exception_handler(StarletteHTTPException)
async def http_error(request, exc):
    return JSONResponse(status_code=exc.status_code, content={"error": {"message": exc.detail}})


@app.exception_handler(RequestValidationError)
async def validation_error(request, exc):
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "message": "Invalid request values.",
                "details": [
                    {"field": ".".join(map(str, e["loc"])), "message": e["msg"]} for e in exc.errors()
                ],
            }
        },
    )


@app.get("/api/v1/health")
def health(request: Request):
    registry = request.app.state.registry
    return dict(status="ok", models_available=len(registry.models) == 5, loaded_models=list(registry.models))


@app.get("/api/v1/models")
@app.get("/api/v1/models/metrics")
def models(request: Request):
    registry = request.app.state.registry
    registry.require()
    return {
        k: v for k, v in registry.metadata.items() if k not in ["train_indices", "test_indices", "dataset"]
    }


@app.get("/api/v1/models/{model_id}")
def model_detail(model_id: str, request: Request):
    registry = request.app.state.registry
    registry.require()
    item = next((x for x in registry.metadata["models"] if x["id"] == model_id), None)
    if not item:
        raise HTTPException(404, "Model not found.")
    return item


@app.get("/api/v1/dataset/summary")
def dataset_summary(request: Request):
    return request.app.state.summary


@app.get("/api/v1/features")
def features(request: Request):
    stats = request.app.state.summary["statistics"]
    return [
        dict(
            id=c,
            name=c.replace("_", " "),
            unit="dimensionless" if c == "ph" else "dataset units unverified",
            min=0,
            max=14 if c == "ph" else max(stats[c]["max"] * 1.25, 1),
            default=stats[c]["50%"],
            reference=REFERENCES.get(c),
        )
        for c in FEATURES
    ]


def persist(results, source):
    with Session.begin() as session:
        for result in results:
            session.add(Analysis(id=result["analysis_id"], source=source, payload=result))


@app.post("/api/v1/predict", response_model=Prediction)
def predict(sample: Sample, request: Request):
    result = request.app.state.registry.predict_many([sample])[0]
    persist([result], "single")
    return result


@app.post("/api/v1/predict/batch", response_model=BatchResponse)
async def batch_predict(request: Request, file: UploadFile = File(...)):
    if not (file.filename or "").lower().endswith(".csv"):
        raise HTTPException(415, "Upload a .csv file.")
    raw = await file.read(2_000_001)
    if len(raw) > 2_000_000:
        raise HTTPException(413, "CSV exceeds the 2 MB limit.")
    try:
        reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig")), strict=True)
        if not reader.fieldnames or len(reader.fieldnames) != len(set(reader.fieldnames)):
            raise HTTPException(422, "CSV headers are missing or duplicated.")
        if set(reader.fieldnames) not in (set(FEATURES), set(FEATURES + ["Potability"])):
            raise HTTPException(
                422, "CSV must contain the nine exact feature headers; optional Potability is ignored."
            )
        samples, row_numbers, errors = [], [], []
        total = 0
        for number, row in enumerate(reader, start=2):
            total += 1
            if total > 1000:
                raise HTTPException(413, "Maximum 1,000 CSV rows per batch.")
            try:
                if None in row or any(v is None for v in row.values()):
                    raise ValueError("Column count does not match headers.")
                sample = Sample.model_validate({c: row[c] for c in FEATURES})
                samples.append(sample)
                row_numbers.append(number)
            except (ValidationError, ValueError) as exc:
                message = (
                    "; ".join(f"{e['loc'][0]}: {e['msg']}" for e in exc.errors())
                    if isinstance(exc, ValidationError)
                    else str(exc)
                )
                errors.append(dict(row=number, message=message))
        if not total:
            raise HTTPException(422, "CSV contains no data rows.")
    except (UnicodeError, csv.Error) as exc:
        raise HTTPException(422, "CSV must be well-formed UTF-8 text.") from exc
    results = request.app.state.registry.predict_many(samples, "batch") if samples else []
    for row, result in zip(row_numbers, results):
        result["row"] = row
    payload = dict(
        batch_id=str(uuid4()),
        total=total,
        valid=len(results),
        invalid=len(errors),
        potable=sum(r["predicted_class"] for r in results),
        non_potable=sum(1 - r["predicted_class"] for r in results),
        results=results,
        errors=errors,
    )
    with Session.begin() as session:
        for result in results:
            session.add(Analysis(id=result["analysis_id"], source="batch", payload=result))
        session.add(Batch(id=payload["batch_id"], payload=payload))
    return payload


@app.get("/api/v1/batches/{batch_id}/csv")
def batch_csv(batch_id: UUID):
    with Session() as session:
        item = session.get(Batch, str(batch_id))
        if not item:
            raise HTTPException(404, "Batch not found.")
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["row", *FEATURES, "prediction", "model_probability", "agreement", "warnings"])
        for r in item.payload["results"]:
            writer.writerow(
                [
                    safe_csv_cell(value)
                    for value in [
                        r["row"],
                        *[r["measurements"][c] for c in FEATURES],
                        r["label"],
                        r["selected_class_probability"],
                        r["agreement_count"],
                        len(r["warnings"]),
                    ]
                ]
            )
    return Response(
        output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="jalsathi-batch.csv"'},
    )


@app.get("/api/v1/analyses")
def analyses(limit: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0)):
    from sqlalchemy import func

    with Session() as session:
        total = session.scalar(select(func.count()).select_from(Analysis))
        rows = session.scalars(
            select(Analysis).order_by(Analysis.created_at.desc()).offset(offset).limit(limit)
        ).all()
        return dict(total=total, items=[r.payload for r in rows])


def find_analysis(session, analysis_id):
    item = session.get(Analysis, str(analysis_id))
    if not item:
        raise HTTPException(404, "Analysis not found.")
    return item


@app.get("/api/v1/analyses/{analysis_id}", response_model=Prediction)
def analysis(analysis_id: UUID):
    with Session() as session:
        return find_analysis(session, analysis_id).payload


@app.get("/api/v1/reports/{analysis_id}/pdf")
def pdf(analysis_id: UUID):
    with Session.begin() as session:
        item = find_analysis(session, analysis_id)
        path = generate_report(item.payload)
        item.report_path = str(path)
    return FileResponse(path, media_type="application/pdf", filename=f"JalSathi-{analysis_id}.pdf")


@app.get("/api/v1/plots/{filename}")
def plot(filename: str, request: Request):
    allowed = {"cart-tree.png", "gam-effects.png"} | {
        f"{key}-evaluation.png" for key in ["cart", "rf", "ada", "gb", "voting"]
    }
    if filename not in allowed:
        raise HTTPException(404, "Plot not found.")
    path = request.app.state.registry.directory / "plots" / filename
    if not path.is_file():
        raise HTTPException(404, "Plot unavailable; train models first.")
    return FileResponse(path, media_type="image/png")


@app.get("/api/v1/extensions")
def extensions(request: Request):
    path = request.app.state.registry.directory / "extensions.json"
    if not path.is_file():
        raise HTTPException(404, "Run python -m ml.extensions to generate extension demonstrations.")
    return json.loads(path.read_text())


@app.get("/api/v1/samples/csv")
def sample_csv():
    path = ROOT / "data/samples/demo.csv"
    if not path.exists():
        raise HTTPException(404, "Train models to generate genuine demonstration samples.")
    return FileResponse(path, media_type="text/csv", filename="jalsathi-samples.csv")
