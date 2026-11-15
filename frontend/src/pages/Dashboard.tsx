import { useState } from "react";
import { Link } from "react-router-dom";
import {
  ArrowUpRight,
  Database,
  Droplets,
  GitBranch,
  Trophy,
} from "lucide-react";
import { useDataset, useHistory, useModels } from "../api";
import { Card, Empty, ErrorState, Header, Loading } from "../components/ui";
import { percent } from "../components/format";
import { DistributionChart, PerformanceChart } from "../components/Charts";
import HistoryTable from "../components/HistoryTable";
export default function Dashboard() {
  const dataset = useDataset();
  const models = useModels();
  const history = useHistory();
  const [metric, setMetric] = useState<
    "accuracy" | "precision" | "recall" | "f1" | "roc_auc"
  >("accuracy");
  return (
    <>
      <Header
        title="Welcome to JalSathi"
        subtitle="Intelligent Water Quality Analysis & Prediction"
      />
      {dataset.isError ? (
        <ErrorState
          error={dataset.error}
          retry={() => void dataset.refetch()}
        />
      ) : dataset.isPending ? (
        <Loading />
      ) : (
        <>
          <div className="stat-grid">
            {[
              {
                label: "Dataset Samples",
                value: dataset.data.rows.toLocaleString(),
                Icon: Database,
              },
              {
                label: "Water Quality Parameters",
                value: dataset.data.features.length,
                Icon: Droplets,
              },
              {
                label: "Trained ML Models",
                value: models.data?.models.length ?? "Unavailable",
                Icon: GitBranch,
              },
              {
                label: "Primary Model · Test Balanced Accuracy",
                value: models.data
                  ? percent(
                      models.data.models.find(
                        (m) => m.id === models.data.primary,
                      )!.metrics.balanced_accuracy,
                    )
                  : "Unavailable",
                Icon: Trophy,
              },
            ].map(({ label, value, Icon }) => (
              <Card key={label} className="stat-card">
                <span className="small-icon">
                  <Icon />
                </span>
                <div>
                  <p>{label}</p>
                  <strong>{value}</strong>
                </div>
              </Card>
            ))}
          </div>
          <div className="two-columns">
            <Card>
              <h2>Dataset potability distribution</h2>
              <p className="muted">
                Original labels · {dataset.data.rows.toLocaleString()}{" "}
                observations
              </p>
              <DistributionChart classes={dataset.data.classes} />
            </Card>
            <Card>
              <div className="card-heading">
                <h2>Model performance</h2>
                <select
                  aria-label="Performance metric"
                  value={metric}
                  onChange={(e) => setMetric(e.target.value as typeof metric)}
                >
                  {["accuracy", "precision", "recall", "f1", "roc_auc"].map(
                    (m) => (
                      <option key={m} value={m}>
                        {m.replace("_", " ").toUpperCase()}
                      </option>
                    ),
                  )}
                </select>
              </div>
              {models.data ? (
                <PerformanceChart models={models.data.models} metric={metric} />
              ) : models.isError ? (
                <ErrorState
                  error={models.error}
                  retry={() => void models.refetch()}
                />
              ) : (
                <Loading />
              )}
            </Card>
          </div>
        </>
      )}
      <div className="quick-actions">
        {[
          {
            to: "/analyze",
            title: "Analyze new sample",
            text: "Explore nine measurements",
          },
          {
            to: "/batch",
            title: "Upload a CSV",
            text: "Process up to 1,000 samples",
          },
          {
            to: "/models",
            title: "Compare models",
            text: "Inspect real evaluation results",
          },
          {
            to: "/reports",
            title: "View reports",
            text: "Revisit and download analyses",
          },
        ].map((a) => (
          <Link to={a.to} key={a.to} className="quick-action">
            <div>
              <strong>{a.title}</strong>
              <span>{a.text}</span>
            </div>
            <ArrowUpRight size={20} />
          </Link>
        ))}
      </div>
      <Card>
        <h2>Recent analyses</h2>
        {history.isPending ? (
          <Loading />
        ) : history.isError ? (
          <ErrorState
            error={history.error}
            retry={() => void history.refetch()}
          />
        ) : history.data.items.length ? (
          <HistoryTable items={history.data.items} />
        ) : (
          <Empty title="No analyses yet">
            <Link to="/analyze">Analyze your first sample →</Link>
          </Empty>
        )}
      </Card>
    </>
  );
}
