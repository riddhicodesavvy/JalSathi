import type { Prediction } from "../types";
import { percent } from "./format";
export default function HistoryTable({
  items,
  action,
}: {
  items: Prediction[];
  action?: (p: Prediction) => React.ReactNode;
}) {
  return (
    <div className="table-scroll">
      <table>
        <thead>
          <tr>
            <th>Analysis / date</th>
            <th>pH</th>
            <th>Hardness</th>
            <th>Solids</th>
            <th>Prediction</th>
            <th>Model / estimate</th>
            {action && <th>Report</th>}
          </tr>
        </thead>
        <tbody>
          {items.map((p) => (
            <tr key={p.analysis_id}>
              <td>
                <strong title={p.analysis_id}>
                  {p.analysis_id.slice(0, 8)}
                </strong>
                <small className="block muted">
                  {new Date(p.created_at).toLocaleString()}
                </small>
              </td>
              <td>{p.measurements.ph.toFixed(2)}</td>
              <td>{p.measurements.Hardness.toFixed(2)}</td>
              <td>{p.measurements.Solids.toFixed(0)}</td>
              <td>
                <span
                  className={`prediction-pill ${p.predicted_class ? "yes" : "no"}`}
                >
                  {p.label}
                </span>
              </td>
              <td>
                {p.primary_model}
                <small className="block muted">
                  {percent(p.selected_class_probability)} · uncalibrated
                </small>
              </td>
              {action && <td>{action(p)}</td>}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
