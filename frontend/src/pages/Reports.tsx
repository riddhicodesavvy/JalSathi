import { useState } from "react";
import { Link } from "react-router-dom";
import { Eye } from "lucide-react";
import { useHistory } from "../api";
import {
  Button,
  Card,
  Empty,
  ErrorState,
  Header,
  Loading,
  Modal,
  ReportButton,
} from "../components/ui";
import HistoryTable from "../components/HistoryTable";
import { Details, ParameterTable } from "../components/Results";
import type { Prediction } from "../types";
export default function Reports() {
  const [offset, setOffset] = useState(0);
  const query = useHistory(offset);
  const [selected, setSelected] = useState<Prediction | null>(null);
  return (
    <>
      <Header
        title="Reports & Analysis History"
        subtitle="Every sample, every insight. Revisit your analyses and download a report."
      />
      <Card>
        <div className="card-heading">
          <h2>Analysis library</h2>
          <span className="pill">{query.data?.total ?? "—"} analyses</span>
        </div>
        <p className="muted">
          PDF reports are generated on demand from saved measurements and model
          results.
        </p>
        {query.isPending ? (
          <Loading />
        ) : query.isError ? (
          <ErrorState error={query.error} retry={() => void query.refetch()} />
        ) : query.data.items.length ? (
          <>
            <HistoryTable
              items={query.data.items}
              action={(p) => (
                <div className="inline-actions">
                  <Button
                    variant="ghost"
                    onClick={() => setSelected(p)}
                    aria-label={`Preview ${p.analysis_id}`}
                  >
                    <Eye size={17} />
                  </Button>
                  <ReportButton id={p.analysis_id} />
                </div>
              )}
            />
            <div className="pagination">
              <Button
                variant="outline"
                disabled={offset === 0}
                onClick={() => setOffset(offset - 10)}
              >
                Previous
              </Button>
              <span>
                {offset + 1}–{Math.min(offset + 10, query.data.total)} of{" "}
                {query.data.total}
              </span>
              <Button
                variant="outline"
                disabled={offset + 10 >= query.data.total}
                onClick={() => setOffset(offset + 10)}
              >
                Next
              </Button>
            </div>
          </>
        ) : (
          <Empty title="No reports generated yet.">
            <Link to="/analyze">Analyze a sample →</Link>
          </Empty>
        )}
      </Card>
      <Modal
        title="Analysis report preview"
        open={!!selected}
        onClose={() => setSelected(null)}
      >
        {selected && (
          <>
            <p>
              {new Date(selected.created_at).toLocaleString()} ·{" "}
              {selected.analysis_id}
            </p>
            <h3>{selected.label}</h3>
            <ParameterTable result={selected} />
            <Details result={selected} />
            <ReportButton id={selected.analysis_id} />
          </>
        )}
      </Modal>
    </>
  );
}
