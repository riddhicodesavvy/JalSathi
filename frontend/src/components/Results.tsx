import {
  ChartColumnIncreasing,
  CheckCircle2,
  CircleHelp,
  Droplets,
  Plus,
  ShieldAlert,
  ShieldCheck,
} from "lucide-react";
import { useState } from "react";
import type { Prediction } from "../types";
import { Button, Card, Modal, ReportButton, Status } from "./ui";
import { friendly, percent } from "./format";

export function Details({ result }: { result: Prediction }) {
  return (
    <>
      <p className="muted">
        Primary: {result.primary_model} · {result.version} ·{" "}
        {result.calibration} probabilities
      </p>
      <div className="table-scroll">
        <table>
          <thead>
            <tr>
              <th>Model</th>
              <th>Classification</th>
              <th>P(potable)</th>
            </tr>
          </thead>
          <tbody>
            {result.models.map((m) => (
              <tr key={m.id}>
                <td>
                  {m.name}
                  {m.id === result.primary_model ? " ★" : ""}
                </td>
                <td>{m.label}</td>
                <td>{percent(m.potable_probability)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <h3>CART decision path</h3>
      <p className="muted">
        Actual fitted tree splits for this sample. Model influence does not
        imply causation.
      </p>
      <ol className="decision-path">
        {result.decision_path.map((p, i) => (
          <li key={i}>{p}</li>
        ))}
      </ol>
      <h3>Warnings & limitations</h3>
      <ul className="warning-list">
        {result.warnings.map((w) => (
          <li key={w}>{w}</li>
        ))}
      </ul>
      <p className="advisory">{result.disclaimer}</p>
    </>
  );
}
export function ParameterTable({ result }: { result: Prediction }) {
  return (
    <div className="table-scroll">
      <table className="parameter-table">
        <thead>
          <tr>
            <th>Parameter</th>
            <th>Your value</th>
            <th>Reference guideline</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {result.parameters.map((p) => (
            <tr key={p.feature}>
              <th scope="row">{friendly(p.feature)}</th>
              <td>
                {p.value.toLocaleString(undefined, {
                  maximumFractionDigits: 2,
                })}
              </td>
              <td>
                {p.source ? (
                  <a
                    href={p.source}
                    target="_blank"
                    rel="noreferrer"
                    title={`${p.jurisdiction}. ${p.reason || "Dimensionless pH reference."}`}
                  >
                    {p.reference}
                  </a>
                ) : (
                  <span title={p.reason || ""}>Unverified</span>
                )}
              </td>
              <td>
                <Status status={p.status} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <p className="table-note">
        pH is dimensionless. All other dataset measurement units are unverified.
      </p>
    </div>
  );
}
export default function Results({
  result,
  onClear,
}: {
  result: Prediction;
  onClear: () => void;
}) {
  const [details, setDetails] = useState(false);
  const p = result.selected_class_probability;
  const counts = {
    within: result.parameters.filter((p) => p.status === "within").length,
    outside: result.parameters.filter((p) => p.status === "outside").length,
    unknown: result.parameters.filter((p) => p.status === "unknown").length,
  };
  const Shield = result.predicted_class ? ShieldCheck : ShieldAlert;
  return (
    <Card className="result-card">
      <h2 className="section-title">
        <span className="small-icon">
          <Droplets />
        </span>
        Prediction Result
      </h2>
      <div
        className={`prediction-banner ${result.predicted_class ? "potable" : "nonpotable"}`}
      >
        <Shield size={62} />
        <div>
          <span className="eyebrow">MODEL-BASED CLASSIFICATION</span>
          <h3>{result.label}</h3>
          <p>Educational estimate · Laboratory testing required</p>
        </div>
      </div>
      <div className="probability-agreement">
        <div className="probability">
          <svg
            viewBox="0 0 120 120"
            aria-label={`Selected-class model estimate ${percent(p)}`}
            role="img"
          >
            <defs>
              <linearGradient id="ring" x2="1" y2="1">
                <stop stopColor="#0674d1" />
                <stop offset="1" stopColor="#05c6a7" />
              </linearGradient>
            </defs>
            <circle cx="60" cy="60" r="49" className="ring-track" />
            <circle
              cx="60"
              cy="60"
              r="49"
              className="ring-value"
              stroke="url(#ring)"
              strokeDasharray={`${p * 308} 308`}
            />
          </svg>
          <div>
            <strong>{percent(p)}</strong>
            <span>Model Estimate</span>
          </div>
          <small>Uncalibrated</small>
        </div>
        <div className="agreement">
          <h3>Model Agreement</h3>
          <p>
            {result.agreement_count} / 5 models predict{" "}
            {result.predicted_class ? "Potable" : "Non-Potable"}
          </p>
          <div className="model-indicators">
            {result.models.map((m) => (
              <button
                key={m.id}
                className="model-indicator"
                onClick={() => setDetails(true)}
                title={`${m.name}: ${m.label}`}
              >
                <span className={m.predicted_class ? "model-yes" : "model-no"}>
                  {m.predicted_class ? (
                    <CheckCircle2 size={23} />
                  ) : (
                    <ShieldAlert size={23} />
                  )}
                </span>
                <small>
                  {
                    (
                      {
                        cart: "CART",
                        rf: "RF",
                        ada: "AdaBoost",
                        gb: "GB",
                        voting: "Voting",
                      } as Record<string, string>
                    )[m.id]
                  }
                </small>
              </button>
            ))}
          </div>
        </div>
      </div>
      <h3 className="section-title sub-title">
        <ChartColumnIncreasing size={21} />
        Parameter Analysis
      </h3>
      <div className="status-summary">
        <span className="within">
          <CheckCircle2 size={17} />
          {counts.within} Within range
        </span>
        <span className="outside">
          <ShieldAlert size={17} />
          {counts.outside} Outside range
        </span>
        <span className="unknown">
          <CircleHelp size={17} />
          {counts.unknown} Unverified
        </span>
      </div>
      <h3 className="section-title sub-title">Parameter Details</h3>
      <ParameterTable result={result} />
      <details className="reference-notes">
        <summary>Reference sources & scientific limitations</summary>
        <ul>
          {result.warnings.map((w) => (
            <li key={w}>{w}</li>
          ))}
        </ul>
      </details>
      <div className="result-actions">
        <Button variant="outline" onClick={() => setDetails(true)}>
          <ChartColumnIncreasing size={16} />
          Model Details
        </Button>
        <ReportButton id={result.analysis_id} />
        <Button onClick={onClear}>
          <Plus size={17} />
          Analyze Another
        </Button>
      </div>
      <p className="disclaimer">{result.disclaimer}</p>
      <Modal
        title="Model prediction details"
        open={details}
        onClose={() => setDetails(false)}
      >
        <Details result={result} />
      </Modal>
    </Card>
  );
}
