import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useForm, useWatch } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import {
  Atom,
  Droplets,
  FlaskConical,
  Gem,
  Info,
  Leaf,
  LoaderCircle,
  Network,
  RotateCcw,
  Sparkles,
  Waves,
  Zap,
} from "lucide-react";
import { toast } from "sonner";
import { request, useFeatures } from "../api";
import {
  Button,
  Card,
  Empty,
  ErrorState,
  Header,
  Loading,
} from "../components/ui";
import { friendly } from "../components/format";
import Results from "../components/Results";
import type { Feature, Prediction, Sample } from "../types";

const icons = [
  FlaskConical,
  Gem,
  Atom,
  Network,
  FlaskConical,
  Zap,
  Leaf,
  Network,
  Waves,
];
import { sampleSchema, type FormValues } from "../schema";
function AnalyzerForm({ features }: { features: Feature[] }) {
  const defaults = Object.fromEntries(
    features.map((f) => [f.id, Number(f.default.toFixed(3))]),
  ) as FormValues;
  const {
    register,
    handleSubmit,
    control,
    setValue,
    reset,
    setFocus,
    formState: { errors },
  } = useForm<FormValues>({
    resolver: zodResolver(sampleSchema),
    defaultValues: defaults,
  });
  const [result, setResult] = useState<Prediction | null>(null);
  const [edited, setEdited] = useState(false);
  const client = useQueryClient();
  const mutation = useMutation({
    onMutate: () => {
      setResult(null);
      setEdited(false);
    },
    mutationFn: (sample: Sample) =>
      request<Prediction>("/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(sample),
      }),
    onSuccess: (data) => {
      setResult(data);
      setEdited(false);
      void client.invalidateQueries({ queryKey: ["history"] });
      toast.success("Sample analysis completed.");
    },
    onError: (e: Error) => toast.error(e.message),
  });
  const values = useWatch({ control }) as FormValues;
  function clear() {
    setResult(null);
    mutation.reset();
    setEdited(false);
    setFocus("ph");
  }
  return (
    <div className="analyzer-grid">
      <Card className="input-card">
        <div className="card-heading">
          <h2 className="section-title">
            <span className="small-icon teal">
              <Droplets />
            </span>
            Water Quality Parameters
          </h2>
          <span className="pill">9 Parameters</span>
        </div>
        <form onSubmit={handleSubmit((v) => mutation.mutate(v))} noValidate>
          <fieldset
            disabled={mutation.isPending}
            className="parameter-fieldset"
          >
            <div className="parameter-inputs">
              {features.map((feature, i) => {
                const name = feature.id as keyof FormValues;
                const Icon = icons[i];
                return (
                  <div className="parameter-row" key={feature.id}>
                    <Icon className="parameter-icon" size={27} />
                    <label htmlFor={feature.id}>
                      {friendly(feature.id)}
                      <span
                        className="info-tooltip"
                        title={
                          feature.unit === "dimensionless"
                            ? "Acidity or alkalinity, measured on a dimensionless pH scale."
                            : `${friendly(feature.id)} measurement. Dataset units are unverified; use the original dataset scale.`
                        }
                      >
                        <Info size={12} />
                      </span>
                    </label>
                    <div className="slider-wrap">
                      <input
                        aria-label={`${friendly(feature.id)} slider`}
                        type="range"
                        min={feature.min}
                        max={feature.max}
                        step="any"
                        value={
                          Number.isFinite(values[name])
                            ? Math.min(values[name], feature.max)
                            : 0
                        }
                        style={
                          {
                            "--progress": `${Math.min(100, ((values[name] || 0) / feature.max) * 100)}%`,
                          } as React.CSSProperties
                        }
                        onChange={(e) => {
                          setValue(name, Number(e.target.value), {
                            shouldValidate: true,
                          });
                          setEdited(true);
                        }}
                      />
                      <div className="range-labels">
                        <span>{feature.min}</span>
                        <span>
                          {feature.max.toLocaleString(undefined, {
                            maximumFractionDigits: 0,
                          })}
                        </span>
                      </div>
                    </div>
                    <div className="numeric-wrap">
                      <input
                        id={feature.id}
                        type="number"
                        step="any"
                        min="0"
                        max={feature.id === "ph" ? 14 : 1e9}
                        aria-invalid={!!errors[name]}
                        aria-describedby={
                          errors[name] ? `${feature.id}-error` : undefined
                        }
                        {...register(name, {
                          valueAsNumber: true,
                          onChange: () => setEdited(true),
                        })}
                      />
                      {errors[name] && (
                        <span
                          className="field-error"
                          role="alert"
                          id={`${feature.id}-error`}
                        >
                          {errors[name]?.message}
                        </span>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
            <div className="form-note">
              <Info size={14} />
              <span>
                Starts with dataset medians for exploration. Replace with
                measured values.
              </span>
            </div>
            <div className="form-actions">
              <Button
                type="button"
                variant="outline"
                onClick={() => {
                  reset(defaults);
                  clear();
                }}
              >
                <RotateCcw size={18} />
                Reset
              </Button>
              <Button type="submit" disabled={mutation.isPending}>
                {mutation.isPending ? (
                  <LoaderCircle className="spin" size={19} />
                ) : (
                  <Sparkles size={19} />
                )}{" "}
                {mutation.isPending ? "Analyzing…" : "Analyze Sample"}
              </Button>
            </div>
          </fieldset>
        </form>
        {mutation.isError && <ErrorState error={mutation.error} />}
      </Card>
      <div className="result-column">
        {result ? (
          <>
            <Results result={result} onClear={clear} />
            {edited && (
              <p className="advisory" role="status">
                Inputs have changed. Analyze again to update these results.
              </p>
            )}
          </>
        ) : (
          <Card className="result-card">
            <h2 className="section-title">
              <span className="small-icon">
                <Droplets />
              </span>
              Prediction Result
            </h2>
            {mutation.isPending ? (
              <Loading />
            ) : (
              <Empty title="A clearer picture starts with a sample">
                <p>
                  Enter nine water measurements and run an analysis to explore
                  how five trained models classify your sample.
                </p>
                <div className="empty-models">
                  <span>CART</span>
                  <span>Random Forest</span>
                  <span>AdaBoost</span>
                  <span>Gradient Boosting</span>
                  <span>Voting</span>
                </div>
              </Empty>
            )}
            <div className="advisory">
              <Info size={19} />
              <p>
                This is an educational screening tool. A model classification
                cannot certify drinking-water safety. Essential microbial and
                contaminant testing is outside this dataset.
              </p>
            </div>
            <div className="how-it-works">
              <h3>From measurements to insight</h3>
              <ol>
                <li>
                  <span>01</span>Validate nine parameters
                </li>
                <li>
                  <span>02</span>Compare five trained classifiers
                </li>
                <li>
                  <span>03</span>Explore model agreement and reference checks
                </li>
                <li>
                  <span>04</span>Download your analysis report
                </li>
              </ol>
            </div>
          </Card>
        )}
      </div>
    </div>
  );
}
export default function Analyzer() {
  const query = useFeatures();
  return (
    <>
      <Header
        title="Analyze Sample"
        subtitle="Enter the water quality parameters to predict potability"
      />
      {query.isPending ? (
        <Loading />
      ) : query.isError ? (
        <ErrorState error={query.error} retry={() => void query.refetch()} />
      ) : (
        <AnalyzerForm features={query.data} />
      )}
    </>
  );
}
