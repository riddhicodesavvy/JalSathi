export type Sample = Record<string, number>;
export interface Feature {
  id: string;
  name: string;
  unit: string;
  min: number;
  max: number;
  default: number;
  reference: { reference: string; source: string } | null;
}
export interface ModelPrediction {
  id: string;
  name: string;
  predicted_class: number;
  label: string;
  potable_probability: number;
  selected_class_probability: number;
}
export interface Parameter {
  feature: string;
  value: number;
  unit: string;
  status: "within" | "outside" | "unknown";
  reference: string;
  source: string | null;
  reason: string | null;
  jurisdiction: string | null;
}
export interface Prediction {
  analysis_id: string;
  created_at: string;
  source: string;
  measurements: Sample;
  primary_model: string;
  version: string;
  predicted_class: number;
  label: string;
  selected_class_probability: number;
  calibration: string;
  models: ModelPrediction[];
  agreement_count: number;
  agreement_percentage: number;
  parameters: Parameter[];
  warnings: string[];
  decision_path: string[];
  disclaimer: string;
  row?: number;
}
export interface Metrics {
  accuracy: number;
  precision: number;
  recall: number;
  f1: number;
  balanced_accuracy: number;
  roc_auc: number;
  pr_auc: number;
  brier: number;
  false_potable_rate: number;
  confusion_matrix: number[][];
}
export interface Model {
  id: string;
  name: string;
  metrics: Metrics;
  cv_balanced_accuracy: number;
  cv_brier: number;
  hyperparameters: Record<string, unknown>;
  version: string;
  trained_at: string;
  calibration: string;
  feature_importance?: Record<string, number>;
  permutation_importance: Record<string, number>;
  roc: { x: number; y: number }[];
  pr: { x: number; y: number }[];
  threshold_analysis: {
    threshold: number;
    false_potable_rate: number;
    potable_recall: number;
  }[];
}
export interface Registry {
  primary: string;
  models: Model[];
  version: string;
  selection: string;
  split: string;
  seed: number;
  versions: Record<string, string>;
}
export interface Dataset {
  rows: number;
  features: string[];
  source: string;
  sha256: string;
  classes: Record<string, number>;
  missing: Record<string, number>;
  duplicates: number;
  limitations: string[];
  statistics: Record<string, Record<string, number>>;
}
export interface History {
  total: number;
  items: Prediction[];
}
export interface BatchResult {
  batch_id: string;
  total: number;
  valid: number;
  invalid: number;
  potable: number;
  non_potable: number;
  results: (Omit<Prediction, "parameters" | "disclaimer"> & {
    details_url: string;
  })[];
  errors: { row: number; message: string }[];
}
