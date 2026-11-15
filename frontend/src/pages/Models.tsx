import { useState } from "react";
import { BarChart3, ExternalLink, GitBranch, Network } from "lucide-react";
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  Bar,
  BarChart,
} from "recharts";
import { API, useModels } from "../api";
import {
  Button,
  Card,
  ErrorState,
  Header,
  Loading,
  Modal,
} from "../components/ui";
import { friendly, percent } from "../components/format";
import { PerformanceChart } from "../components/Charts";
import type { Model, Metrics } from "../types";
const descriptions: Record<
  string,
  {
    text: string;
    topic: string;
    strength: string;
    weakness: string;
    link: string;
  }
> = {
  cart: {
    text: "A decision tree recursively separates observations using Gini impurity.",
    topic: "Classification and Regression Trees",
    strength: "Inspectable paths and nonlinear rules.",
    weakness: "High variance; small changes can change splits.",
    link: "tree",
  },
  rf: {
    text: "Bootstrap samples and random feature subsets train independent trees; predictions are averaged.",
    topic: "Bagging / Ensemble Learning",
    strength:
      "Reduces the variance of individual trees; out-of-bag evaluation.",
    weakness:
      "Less transparent than one tree; probabilities may be uncalibrated.",
    link: "ensemble",
  },
  ada: {
    text: "Weak trees are trained sequentially, giving misclassified observations greater weight.",
    topic: "Boosting",
    strength: "Combines weak learners into a stronger classifier.",
    weakness: "Sensitive to noise and mislabeled observations.",
    link: "ensemble",
  },
  gb: {
    text: "Sequential trees fit the negative gradient of classification loss.",
    topic: "Gradient-based Boosting",
    strength: "Flexible nonlinear interactions.",
    weakness: "Can overfit; needs learning-rate and complexity tuning.",
    link: "ensemble",
  },
  voting: {
    text: "Four independently fitted base classifiers contribute equally to a soft probability vote.",
    topic: "Combining Models / Ensemble Learning",
    strength: "Combines complementary classifiers.",
    weakness:
      "Correlated errors can persist; an ensemble may underperform a base model.",
    link: "ensemble",
  },
};
const metricKeys: (keyof Metrics)[] = [
  "accuracy",
  "precision",
  "recall",
  "f1",
  "balanced_accuracy",
  "roc_auc",
  "pr_auc",
];
const chartColors = ["#087bd1", "#10bfa8", "#9271cb", "#e6a037", "#df637d"];
function ModelDetail({ model }: { model: Model }) {
  const d = descriptions[model.id];
  return (
    <>
      <p>{d.text}</p>
      <p>
        <strong>Unit 5:</strong> {d.topic}
      </p>
      <p>
        <strong>Strengths:</strong> {d.strength}
      </p>
      <p>
        <strong>Limitations:</strong> {d.weakness}
      </p>
      <p className="advisory">
        Chosen for syllabus coverage and a complementary learning strategy.
        Primary model selection uses training cross-validation, never the test
        scores.
      </p>
      <h3>Actual fitted hyperparameters</h3>
      <pre>{JSON.stringify(model.hyperparameters, null, 2)}</pre>
      <p>
        Training CV balanced accuracy: {percent(model.cv_balanced_accuracy)} ·
        Brier: {model.cv_brier.toFixed(3)}
      </p>
      <h3>Safety-oriented threshold analysis</h3>
      <div className="table-scroll">
        <table>
          <thead>
            <tr>
              <th>Threshold</th>
              <th>False-potable rate</th>
              <th>Potable recall</th>
            </tr>
          </thead>
          <tbody>
            {model.threshold_analysis.map((r) => (
              <tr key={r.threshold}>
                <td>{r.threshold}</td>
                <td>{percent(r.false_potable_rate)}</td>
                <td>{percent(r.potable_recall)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="muted">
        Descriptive held-out test analysis, not a tuned deployment threshold.
        False-potable rate = non-potable samples incorrectly predicted potable /
        all actual non-potable samples.
      </p>
      <a
        href={`https://scikit-learn.org/stable/modules/${d.link}.html`}
        target="_blank"
        rel="noreferrer"
      >
        Algorithm documentation <ExternalLink size={13} />
      </a>
    </>
  );
}
export default function Models() {
  const query = useModels();
  const [tab, setTab] = useState("Comparison");
  const [selected, setSelected] = useState<Model | null>(null);
  const [sort, setSort] = useState<keyof Metrics>("balanced_accuracy");
  const [importanceModel, setImportanceModel] = useState("cart");
  if (query.isPending)
    return (
      <>
        <Header
          title="Model Comparison Lab"
          subtitle="Explore the machine learning models powering JalSathi."
        />
        <Loading />
      </>
    );
  if (query.isError)
    return (
      <ErrorState error={query.error} retry={() => void query.refetch()} />
    );
  const data = query.data;
  return (
    <>
      <Header
        title="Model Comparison Lab"
        subtitle="Explore and compare the machine learning models powering JalSathi."
      />
      <p className="context-strip">
        <GitBranch size={16} />
        Primary model:{" "}
        <strong>
          {data.models.find((m) => m.id === data.primary)?.name}
        </strong>{" "}
        · {data.split} · Seed {data.seed}
        <span>{data.selection}</span>
      </p>
      <div className="model-card-grid">
        {data.models.map((m) => (
          <Card key={m.id} className="model-card">
            <span className="small-icon">
              <Network />
            </span>
            <div className="card-heading">
              <h2>{m.name}</h2>
              {m.id === data.primary && <span className="pill">Primary</span>}
            </div>
            <p>{descriptions[m.id].text}</p>
            <div className="mini-metrics">
              <div>
                <strong>{percent(m.metrics.accuracy)}</strong>
                <span>Accuracy</span>
              </div>
              <div>
                <strong>{percent(m.metrics.f1)}</strong>
                <span>F1</span>
              </div>
              <div>
                <strong>{m.metrics.roc_auc.toFixed(3)}</strong>
                <span>ROC-AUC</span>
              </div>
            </div>
            <Button variant="outline" onClick={() => setSelected(m)}>
              View Details <BarChart3 size={16} />
            </Button>
          </Card>
        ))}
      </div>
      <Card>
        <div className="card-heading">
          <h2>Performance comparison</h2>
          <span className="pill">Untouched test partition</span>
        </div>
        <p className="muted">
          Click a metric to sort descending. Positive class = potable (1).
          PR-AUC is average precision.
        </p>
        <div className="table-scroll">
          <table>
            <thead>
              <tr>
                <th>Classifier</th>
                {metricKeys.map((k) => (
                  <th key={k}>
                    <button className="table-sort" onClick={() => setSort(k)}>
                      {k.replaceAll("_", " ")}
                      {sort === k ? " ↓" : ""}
                    </button>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {[...data.models]
                .sort(
                  (a, b) => Number(b.metrics[sort]) - Number(a.metrics[sort]),
                )
                .map((m) => (
                  <tr key={m.id}>
                    <th scope="row">
                      {m.name}
                      {m.id === data.primary ? " ★" : ""}
                    </th>
                    {metricKeys.map((k) => (
                      <td key={k}>{percent(Number(m.metrics[k]))}</td>
                    ))}
                  </tr>
                ))}
            </tbody>
          </table>
        </div>
      </Card>
      <Card className="visualizations">
        <h2>Inside the models</h2>
        <div className="tabs" role="tablist" aria-label="Model visualizations">
          {[
            "Comparison",
            "Confusion Matrices",
            "ROC Curves",
            "Precision-Recall",
            "Feature Importance",
            "CART Tree",
          ].map((t) => (
            <button
              key={t}
              role="tab"
              aria-selected={tab === t}
              onClick={() => setTab(t)}
            >
              {t}
            </button>
          ))}
        </div>
        <div role="tabpanel">
          {tab === "Comparison" && <PerformanceChart models={data.models} />}{" "}
          {tab === "Confusion Matrices" && (
            <div className="matrix-grid">
              {data.models.map((m) => (
                <div key={m.id}>
                  <h3>{m.name}</h3>
                  <span className="muted">
                    Actual ↓ / Predicted → · 0 non-potable, 1 potable
                  </span>
                  <table className="matrix">
                    <thead>
                      <tr>
                        <th>Actual / predicted</th>
                        <th>0</th>
                        <th>1</th>
                      </tr>
                    </thead>
                    <tbody>
                      {m.metrics.confusion_matrix.map((r, i) => (
                        <tr key={i}>
                          <th>{i}</th>
                          {r.map((v, j) => (
                            <td
                              key={j}
                              style={{
                                background: `rgba(8,140,193,${0.07 + v / 700})`,
                              }}
                            >
                              {v}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                  <p className="danger-text">
                    False-potable rate: {percent(m.metrics.false_potable_rate)}
                  </p>
                </div>
              ))}
            </div>
          )}
          {(tab === "ROC Curves" || tab === "Precision-Recall") && (
            <div className="chart large" role="img" aria-label={tab}>
              <ResponsiveContainer width="100%" height="100%">
                <LineChart
                  margin={{ top: 20, right: 30, bottom: 30, left: 20 }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis
                    type="number"
                    dataKey="x"
                    domain={[0, 1]}
                    label={{
                      value:
                        tab === "ROC Curves" ? "False positive rate" : "Recall",
                      position: "bottom",
                    }}
                  />
                  <YAxis
                    type="number"
                    dataKey="y"
                    domain={[0, 1]}
                    label={{
                      value:
                        tab === "ROC Curves"
                          ? "True positive rate"
                          : "Precision",
                      angle: -90,
                      position: "insideLeft",
                    }}
                  />
                  <Tooltip />
                  <Legend verticalAlign="top" />
                  {data.models.map((m, i) => (
                    <Line
                      key={m.id}
                      data={tab === "ROC Curves" ? m.roc : m.pr}
                      dataKey="y"
                      name={m.name}
                      stroke={chartColors[i]}
                      dot={false}
                      strokeWidth={2}
                    />
                  ))}
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}
          {tab === "Feature Importance" && (
            <>
              <select
                aria-label="Feature importance model"
                value={importanceModel}
                onChange={(e) => setImportanceModel(e.target.value)}
              >
                {data.models.map((m) => (
                  <option key={m.id} value={m.id}>
                    {m.name}
                  </option>
                ))}
              </select>
              <p className="muted">
                Held-out permutation importance: mean change in balanced
                accuracy over three repeats. Negative influence changes are
                retained. Descriptive, not causal.
              </p>
              <div
                className="chart large"
                role="img"
                aria-label="Permutation feature importance"
              >
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    layout="vertical"
                    data={Object.entries(
                      data.models.find((m) => m.id === importanceModel)!
                        .permutation_importance,
                    ).map(([name, value]) => ({ name: friendly(name), value }))}
                    margin={{ left: 30, right: 30 }}
                  >
                    <XAxis type="number" />
                    <YAxis
                      type="category"
                      dataKey="name"
                      width={120}
                      fontSize={12}
                    />
                    <Tooltip />
                    <Bar dataKey="value" fill="#0aaea9" radius={[0, 4, 4, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </>
          )}
          {tab === "CART Tree" && (
            <>
              <p className="muted">
                Actual fitted CART, displayed to depth 3. Leaf continuation
                markers indicate deeper branches.
              </p>
              <a
                href={`${API}/plots/cart-tree.png`}
                target="_blank"
                rel="noreferrer"
              >
                <img
                  className="tree-image"
                  src={`${API}/plots/cart-tree.png`}
                  alt="Fitted CART decision tree, depth-limited to three levels"
                />
              </a>
            </>
          )}
        </div>
      </Card>
      <Card>
        <h2>Unit 5 connection</h2>
        <div className="topic-grid">
          {data.models.map((m) => (
            <div key={m.id}>
              <strong>{m.name}</strong>
              <p>{descriptions[m.id].topic}</p>
            </div>
          ))}
        </div>
      </Card>
      <Modal
        title={selected?.name || "Model details"}
        open={!!selected}
        onClose={() => setSelected(null)}
      >
        {selected && <ModelDetail model={selected} />}
      </Modal>
    </>
  );
}
