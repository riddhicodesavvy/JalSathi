import { useRef, useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Download, FileSpreadsheet, LoaderCircle, Upload } from "lucide-react";
import { toast } from "sonner";
import { download, request, useFeatures } from "../api";
import { Button, Card, ErrorState, Header } from "../components/ui";
import { percent } from "../components/format";
import type { BatchResult } from "../types";

export default function Batch() {
  const input = useRef<HTMLInputElement>(null);
  const [result, setResult] = useState<BatchResult | null>(null);
  const [filter, setFilter] = useState("all");
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(0);
  const [sort, setSort] = useState<"row" | "probability">("row");
  const features = useFeatures();
  const client = useQueryClient();
  const [dragging, setDragging] = useState(false);
  const mutation = useMutation({
    mutationFn: async (file: File) => {
      if (!file.name.toLowerCase().endsWith(".csv"))
        throw new Error("Select a .csv file.");
      if (file.size > 2_000_000) throw new Error("Maximum file size is 2 MB.");
      const body = new FormData();
      body.append("file", file);
      return request<BatchResult>("/predict/batch", { method: "POST", body });
    },
    onSuccess: (r) => {
      setResult(r);
      setPage(0);
      setSearch("");
      setFilter("all");
      setSort("row");
      void client.invalidateQueries({ queryKey: ["history"] });
      toast.success(`${r.valid} rows analyzed; ${r.invalid} invalid.`);
    },
    onError: (e: Error) => toast.error(e.message),
  });
  function upload(file?: File) {
    if (file) {
      setResult(null);
      mutation.mutate(file);
    }
  }
  const rows = (result?.results || [])
    .filter(
      (r) =>
        (filter === "all" || String(r.predicted_class) === filter) &&
        `${r.row} ${r.label} ${Object.values(r.measurements).join(" ")}`
          .toLowerCase()
          .includes(search.toLowerCase()),
    )
    .sort((a, b) =>
      sort === "row"
        ? (a.row || 0) - (b.row || 0)
        : b.selected_class_probability - a.selected_class_probability,
    );
  return (
    <>
      <Header
        title="Batch Analysis"
        subtitle="Turn a collection of water samples into a clear, comparable analysis."
      />
      <Card>
        <div
          className={`upload-zone ${dragging ? "dragging" : ""}`}
          onDragOver={(e) => {
            e.preventDefault();
            setDragging(true);
          }}
          onDragLeave={() => setDragging(false)}
          onDrop={(e) => {
            e.preventDefault();
            setDragging(false);
            if (!mutation.isPending) upload(e.dataTransfer.files[0]);
          }}
        >
          <span className="empty-icon">
            <FileSpreadsheet size={42} />
          </span>
          <h2>Drop your sample CSV here</h2>
          <p>Nine feature columns · UTF-8 CSV · Up to 2 MB / 1,000 rows</p>
          <input
            ref={input}
            type="file"
            accept=".csv,text/csv"
            aria-label="CSV file"
            className="sr-only"
            disabled={mutation.isPending}
            onChange={(e) => {
              upload(e.target.files?.[0]);
              e.target.value = "";
            }}
          />
          <Button
            disabled={mutation.isPending}
            onClick={() => input.current?.click()}
          >
            {mutation.isPending ? (
              <LoaderCircle size={18} className="spin" />
            ) : (
              <Upload size={18} />
            )}{" "}
            {mutation.isPending ? "Processing CSV…" : "Browse Files"}
          </Button>
          {mutation.isPending && (
            <div
              role="progressbar"
              aria-label="Batch processing"
              className="indeterminate-progress"
            />
          )}
          <Button
            variant="ghost"
            onClick={() => void download("/samples/csv", "jalsathi-demo.csv")}
          >
            <Download size={15} />
            Download genuine sample CSV
          </Button>
        </div>
        <details className="reference-notes">
          <summary>CSV format & required columns</summary>
          <p>
            Exact headers:{" "}
            {features.data?.map((f) => f.id).join(", ") ||
              "ph, Hardness, Solids, Chloramines, Sulfate, Conductivity, Organic_carbon, Trihalomethanes, Turbidity"}
            . Optional Potability is ignored. Blank, negative and non-finite
            measurements produce row-level errors.
          </p>
        </details>
        {mutation.isError && <ErrorState error={mutation.error} />}
      </Card>
      {result && (
        <>
          <div className="stat-grid">
            {[
              ["Processed", result.total],
              ["Predicted potable", result.potable],
              ["Predicted non-potable", result.non_potable],
              ["Invalid rows", result.invalid],
            ].map(([label, value]) => (
              <Card className="stat-card" key={label}>
                <div>
                  <p>{label}</p>
                  <strong>{value}</strong>
                </div>
              </Card>
            ))}
          </div>
          <Card>
            <div className="card-heading">
              <h2>Analysis results</h2>
              <Button
                variant="outline"
                onClick={() =>
                  void download(
                    `/batches/${result.batch_id}/csv`,
                    "jalsathi-batch.csv",
                  )
                }
              >
                <Download size={16} />
                Export CSV
              </Button>
            </div>
            <div className="table-controls">
              <input
                aria-label="Search samples"
                placeholder="Search rows, values, predictions…"
                value={search}
                onChange={(e) => {
                  setSearch(e.target.value);
                  setPage(0);
                }}
              />
              <select
                aria-label="Filter predictions"
                value={filter}
                onChange={(e) => {
                  setFilter(e.target.value);
                  setPage(0);
                }}
              >
                <option value="all">All predictions</option>
                <option value="1">Predicted Potable</option>
                <option value="0">Predicted Non-Potable</option>
              </select>
              <select
                aria-label="Sort samples"
                value={sort}
                onChange={(e) => setSort(e.target.value as typeof sort)}
              >
                <option value="row">Row order</option>
                <option value="probability">Model estimate ↓</option>
              </select>
            </div>
            <div className="table-scroll">
              <table>
                <thead>
                  <tr>
                    <th>CSV row</th>
                    {features.data?.map((f) => (
                      <th key={f.id}>{f.name}</th>
                    ))}
                    <th>Prediction</th>
                    <th>Estimate</th>
                    <th>Agreement</th>
                    <th>Warnings</th>
                  </tr>
                </thead>
                <tbody>
                  {rows.slice(page * 10, page * 10 + 10).map((r) => (
                    <tr key={r.analysis_id}>
                      <th scope="row">{r.row}</th>
                      {features.data?.map((f) => (
                        <td key={f.id}>{r.measurements[f.id].toFixed(2)}</td>
                      ))}
                      <td>{r.label}</td>
                      <td>{percent(r.selected_class_probability)}</td>
                      <td>{r.agreement_count}/5</td>
                      <td>{r.warnings.length}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="pagination">
              <Button
                variant="outline"
                disabled={page === 0}
                onClick={() => setPage(page - 1)}
              >
                Previous
              </Button>
              <span>
                {rows.length} results · Page {page + 1}
              </span>
              <Button
                variant="outline"
                disabled={(page + 1) * 10 >= rows.length}
                onClick={() => setPage(page + 1)}
              >
                Next
              </Button>
            </div>
          </Card>
          {result.errors.length > 0 && (
            <Card>
              <h2>Rows requiring correction</h2>
              <ul className="warning-list">
                {result.errors.map((e) => (
                  <li key={e.row}>
                    Row {e.row}: {e.message}
                  </li>
                ))}
              </ul>
            </Card>
          )}
        </>
      )}
    </>
  );
}
