import { ArrowRight, BookOpen, Database, FlaskConical } from "lucide-react";
import Extensions from "../components/Extensions";
import { useDataset } from "../api";
import { Card, ErrorState, Header, Loading } from "../components/ui";
import { friendly } from "../components/format";
const topics = [
  [
    "CART",
    "Complete",
    "Recursive Gini-based splitting produces a categorization tree. Inspect the actual tree, predictions, and local decision paths in Model Comparison and Analyze Sample.",
  ],
  [
    "Ensemble Learning",
    "Complete",
    "Random Forest averages bootstrap-trained trees. Soft Voting averages probabilities from four independently fitted classifiers. Inspect model agreement and comparison metrics.",
  ],
  [
    "Boosting",
    "Complete",
    "AdaBoost reweights incorrectly classified samples; Gradient Boosting fits negative loss gradients. Both have training-only hyperparameter search and held-out evaluation.",
  ],
  [
    "Bayesian Model Averaging",
    "Approximation",
    "A rigorous Bayesian average integrates parameter and model uncertainty. The five tree classifiers do not provide Bayesian marginal likelihoods; equal soft voting is not BMA. See methodology documentation for the explicitly labeled approximation.",
  ],
  [
    "Generalized Additive Models",
    "Implemented",
    "An additive logistic spline model can describe separate nonlinear feature effects without interactions. See extension results when generated; this is separate from the five core models.",
  ],
  [
    "Adaptive Basis Function Models",
    "Not implemented",
    "MARS selects and prunes adaptive hinge bases. Random Forest is not MARS. A reliable MARS dependency is not included; this remains a documented extension.",
  ],
];
export default function About() {
  const query = useDataset();
  return (
    <>
      <Header
        title="About JalSathi"
        subtitle="Smarter Water Insights, Powered by Machine Learning."
      />
      <Extensions />
      <div className="two-columns">
        <Card>
          <span className="small-icon">
            <FlaskConical />
          </span>
          <h2>A learning workspace for water intelligence</h2>
          <p>
            JalSathi is a third-year B.Tech Computer Science project
            demonstrating Machine Learning Unit 5 through water potability
            classification. Students, researchers and analysts can explore nine
            measurements, compare genuine classifiers, and inspect reproducible
            evaluation evidence.
          </p>
          <p>
            Potability prediction estimates a dataset label from measured
            features. It cannot establish drinking-water safety, certify
            compliance, or replace a laboratory.
          </p>
        </Card>
        <Card>
          <span className="small-icon">
            <BookOpen />
          </span>
          <h2>Built for a defensible demonstration</h2>
          <p>
            <strong>Practical 1:</strong> Implement CART learning algorithms to
            perform categorization — demonstrated with the fitted decision tree,
            its diagram and per-sample decision paths.
          </p>
          <p>
            <strong>Practical 2:</strong> Implement Ensemble learning models to
            perform classification — demonstrated by Random Forest, AdaBoost,
            Gradient Boosting and Voting.
          </p>
        </Card>
      </div>
      <Card>
        <h2>The ML workflow</h2>
        <div className="workflow">
          {[
            "Water Dataset",
            "Data Validation",
            "Preprocessing",
            "ML Training",
            "Model Evaluation",
            "Ensemble Prediction",
            "Quality Analysis",
            "Report Generation",
          ].map((s, i) => (
            <div key={s}>
              <span>{String(i + 1).padStart(2, "0")}</span>
              <strong>{s}</strong>
              {i < 7 && <ArrowRight size={16} />}
            </div>
          ))}
        </div>
        <p className="muted">
          Stratified 80/20 split, seed 42. Median imputation is fitted inside
          training folds. Bounded three-fold tuning selects the primary model
          using balanced accuracy, with Brier score as a tie-break. Test data is
          reserved for reporting.
        </p>
      </Card>
      <Card>
        <h2>
          <Database size={20} /> Dataset information
        </h2>
        {query.isPending ? (
          <Loading />
        ) : query.isError ? (
          <ErrorState error={query.error} retry={() => void query.refetch()} />
        ) : (
          <>
            <p>
              <a href={query.data.source} target="_blank" rel="noreferrer">
                Aditya Kadiwal · Water Potability · Kaggle
              </a>{" "}
              — local dataset; upstream provenance has not been independently
              authenticated.
            </p>
            <div className="topic-grid">
              <div>
                <strong>{query.data.rows.toLocaleString()}</strong>
                <p>records</p>
              </div>
              <div>
                <strong>{query.data.features.length}</strong>
                <p>input features</p>
              </div>
              <div>
                <strong>{query.data.classes["1"]}</strong>
                <p>potable labels</p>
              </div>
              <div>
                <strong>{query.data.duplicates}</strong>
                <p>duplicate rows</p>
              </div>
            </div>
            <h3>Missing measurements</h3>
            <div className="table-scroll">
              <table>
                <thead>
                  <tr>
                    {query.data.features.map((c) => (
                      <th key={c}>{friendly(c)}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    {query.data.features.map((c) => (
                      <td key={c}>{query.data.missing[c]}</td>
                    ))}
                  </tr>
                </tbody>
              </table>
            </div>
            <p className="fingerprint">SHA-256: {query.data.sha256}</p>
          </>
        )}
      </Card>
      <Card>
        <h2>Machine Learning Unit 5 — Topic Implementation Mapping</h2>
        <div className="syllabus-list">
          {topics.map(([title, status, text]) => (
            <details key={title}>
              <summary>
                <strong>{title}</strong>
                <span
                  className={`pill ${status === "Complete" ? "complete" : ""}`}
                >
                  {status}
                </span>
              </summary>
              <p>{text}</p>
            </details>
          ))}
        </div>
      </Card>
      <Card>
        <h2>Understand the limitations</h2>
        <div className="topic-grid">
          {[
            "Dataset collection and label quality are not independently verified.",
            "Missing measurements are imputed in training, which introduces uncertainty.",
            "Model estimates are uncalibrated and are not safety probabilities.",
            "Microbial, metal, pesticide and other essential tests are missing.",
            "EPA secondary pH guidance is an aesthetic reference, not a health certificate.",
            "Mass-unit checks remain unavailable until measurement units are verified.",
          ].map((s) => (
            <p key={s}>{s}</p>
          ))}
        </div>
        <h3>References</h3>
        <p>
          <a
            href="https://scikit-learn.org/stable/"
            target="_blank"
            rel="noreferrer"
          >
            scikit-learn methodology
          </a>{" "}
          ·{" "}
          <a
            href="https://www.epa.gov/sdwa/secondary-drinking-water-standards-guidance-nuisance-chemicals"
            target="_blank"
            rel="noreferrer"
          >
            US EPA secondary guidance
          </a>{" "}
          ·{" "}
          <a
            href="https://www.who.int/publications/i/item/9789240045064"
            target="_blank"
            rel="noreferrer"
          >
            WHO drinking-water quality guidance
          </a>
        </p>
      </Card>
    </>
  );
}
