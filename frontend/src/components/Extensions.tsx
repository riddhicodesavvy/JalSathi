import { useQuery } from "@tanstack/react-query";
import { API, request } from "../api";
import { Card, ErrorState, Loading } from "./ui";
import { percent } from "./format";
interface ExtensionData {
  gam: {
    method: string;
    metrics: { balanced_accuracy: number; roc_auc: number };
    plot: string;
  };
  bayesian_style_average: {
    method: string;
    formula: string;
    limitations: string;
    weights: Record<string, number>;
    metrics: { balanced_accuracy: number };
  };
  adaptive_basis: { status: string; reason: string };
}
export default function Extensions() {
  const q = useQuery({
    queryKey: ["extensions"],
    queryFn: () => request<ExtensionData>("/extensions"),
    retry: false,
  });
  return (
    <Card>
      <h2>Advanced Unit 5 demonstrations</h2>
      {q.isPending ? (
        <Loading />
      ) : q.isError ? (
        <ErrorState error={q.error} retry={() => void q.refetch()} />
      ) : (
        <>
          <h3>Generalized additive model · implemented</h3>
          <p>
            {q.data.gam.method}: independent B-spline effects enter an additive
            logistic link, without feature interactions. Test balanced accuracy:{" "}
            {percent(q.data.gam.metrics.balanced_accuracy)}. This extension does
            not change core model selection.
          </p>
          <img
            className="tree-image"
            src={`${API}/plots/${q.data.gam.plot}`}
            alt="Fitted GAM centered feature effects on the log-odds scale"
          />
          <h3>Bayesian-style averaging · approximation</h3>
          <p>{q.data.bayesian_style_average.method}</p>
          <pre className="formula">{q.data.bayesian_style_average.formula}</pre>
          <p className="muted">{q.data.bayesian_style_average.limitations}</p>
          <div className="table-scroll">
            <table>
              <thead>
                <tr>
                  <th>Candidate</th>
                  <th>Validation-likelihood weight</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(q.data.bayesian_style_average.weights).map(
                  ([key, w]) => (
                    <tr key={key}>
                      <td>{key}</td>
                      <td>{w.toPrecision(4)}</td>
                    </tr>
                  ),
                )}
              </tbody>
            </table>
          </div>
          <p>
            Approximation test balanced accuracy:{" "}
            {percent(q.data.bayesian_style_average.metrics.balanced_accuracy)}
          </p>
          <h3>
            Adaptive basis / MARS · {q.data.adaptive_basis.status.toLowerCase()}
          </h3>
          <p>{q.data.adaptive_basis.reason}</p>
        </>
      )}
    </Card>
  );
}
