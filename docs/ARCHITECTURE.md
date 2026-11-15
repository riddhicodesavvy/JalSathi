# Architecture decisions

The source CSV and prior EDA are immutable inputs. `ml/data.py` validates schema, numeric types, target labels and infinite values. Training writes trusted local joblib pipelines, a JSON registry and PNG plots. The API never retrains, and returns 503 when the five-model registry is unavailable.

React/TypeScript/Vite uses React Router, TanStack Query, React Hook Form/Zod, Recharts, Lucide and Motion. Pages are lazy-loaded. Radix Dialog with shadcn-style Button variants supplies accessible modal focus management; Tailwind and CSS implement original Aqua Glass tokens, waves, droplet/leaf branding and laboratory decoration. The original reference screenshot is not rendered as UI. Component formatting functions, schemas, server state and page views are separate modules.

The typed API client handles fetch errors and binary downloads. Queries are cached by resource and invalidated after persisted inference. Honest empty/loading/error states replace unavailable data. Desktop has a two-column analyzer; narrow layouts stack cards and use a navigation drawer. Reduced-motion preferences disable animation; status is communicated by text and icons as well as color. Tables scroll inside their container.

FastAPI routes use Pydantic for feature and prediction validation. Inference validates all nine finite nonnegative measurements, then calls the same fitted models for single and batch requests. DataFrame columns are explicitly ordered. Probability calculations are vectorized across a batch. Explanations include actual CART node decisions and held-out permutation importance. Guidelines are a separate module and do not alter model classifications.

SQLite/SQLAlchemy persists UUID-keyed analyses, their complete measurements and model snapshots, source, timestamps and report paths. Batches persist aggregate metadata, row-level validation errors and results. Transactions commit a complete successful operation. History remains valid after retraining because prediction metadata is snapshotted. PDF reports regenerate from the saved payload, not the current registry.

CSV filenames are never used as server paths. Exact headers, size, row count, column count and numeric validation bound the input. Original CSV target columns can be present but are ignored for inference. Report and batch URLs validate UUIDs. Plot URLs use a fixed filename allowlist. CORS is restricted to configured frontend origins. Errors do not disclose tracebacks; server logs record method, path, status and elapsed milliseconds without sample bodies.

Model selection is documented in methodology. Additive spline GAM and validation-likelihood averaging are isolated demonstrations and never silently replace the five core classifiers. No remote inference services, paid APIs or credentials are required.
