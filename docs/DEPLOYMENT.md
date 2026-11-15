# Deployment architecture

JalSathi deploys as one Vercel FastAPI project, with the existing Vite build promoted to Vercel's CDN. The production project is `ridcyber/jalsathi`, linked to `https://github.com/riddhicodesavvy/JalSathi` on `main`. The backend uses the same saved five-model registry and fixed 0.5 threshold as local development. No model training occurs during build or inference.

## Runtime and routing

- Root entrypoint: `main.py`, configured as `main:app` in `pyproject.toml`.
- Python 3.12 with inference-only dependencies declared in `[project.dependencies]` and mirrored in `requirements.txt`; test/render/training tools are excluded from the cloud runtime.
- Build: `npm ci --prefix frontend && npm run build --prefix frontend && python -m scripts.build_frontend`.
- `scripts/build_frontend.py` copies Vite `frontend/dist` into ignored `public/` output.
- `outputDirectory` is explicitly `public`. A tracked original favicon keeps that directory discoverable before the build in a clean Git checkout; generated JS/CSS/HTML remain ignored.
- Vercel serves `public/` through its CDN. Explicit rewrites for the seven SPA entry routes provide history fallback without intercepting `/api/v1/*` or API docs. The Python function does not mount the excluded CDN directory at runtime.
- Python bundle configuration excludes development environments, tests, reports and frontend source while retaining dataset, trusted core pipelines, registry and model plots.
- Node 22.x and a 60-second configured function duration; no paid memory/plan upgrade was selected.

## Durable persistence

The dedicated `jalsathi-db` Neon PostgreSQL database uses the explicitly selected **Free (`free_v3`) plan** in `iad1`. No local SQLite history is copied into production. Vercel holds database credentials in backend environment variables supplied by the native Neon integration. `DATABASE_URL` is normalized to SQLAlchemy's `postgresql+psycopg` driver. Serverless connections use `NullPool` rather than retaining a process-local connection pool.

Production refuses to start with an absent database URL or a SQLite URL, avoiding a false persistence claim. `python -m scripts.migrate_database` applies the idempotent initial schema and records `001_initial` in `jalsathi_schema_versions`; it preserves existing production rows. Local development continues to use SQLite.

PDF files are generated on demand under `/tmp/jalsathi-reports` on Vercel. They are reproducible views of the durable saved analysis, not files relied upon for persistence. A report can be regenerated after a cold start/redeployment. Never set `JALSATHI_REPORTS` to the read-only source directory in production.

## Environment variables

| Variable | Scope | Purpose |
|---|---|---|
| `DATABASE_URL` | Backend secret | PostgreSQL connection, injected by Neon |
| `JALSATHI_DATABASE` | Backend optional override | Used locally; must be durable PostgreSQL if configured in production |
| `JALSATHI_ENV=production` | Backend | Enforce production persistence requirements |
| `VITE_API_URL=/api/v1` | Public frontend setting | Same-origin HTTPS API; no secret and no localhost URL |
| `JALSATHI_ORIGINS` | Backend optional | Approved separate frontend origins; same-origin deployment needs no cross-origin calls |
| `JALSATHI_ARTIFACTS` | Backend optional | Defaults to bundled `ml/artifacts` |
| `JALSATHI_REPORTS` | Backend optional | Defaults to temporary directory on Vercel |

`.env.local`, `.env.production.local`, other real environment files and `.vercel` state are ignored. `.env.example` contains example settings only. Never print connection strings or put backend credentials in a `VITE_` variable.

## Cloud payload limit

The original full 1,000-row batch response was 4,908,491 bytes, above Vercel's 4.5 MB response limit. Batch responses now retain input mappings, all five predictions/probabilities, warnings, agreement, model identity/version and CART paths, while omitting repeated parameter-reference prose and disclaimers. Each result includes a `details_url` pointing to the complete durable analysis snapshot. The full record is preserved in PostgreSQL and CSV/PDF downloads remain unchanged. A regression verifies the maximum batch response fits the platform limit.

## Commands

```powershell
vercel whoami
vercel link --yes --project jalsathi --scope ridcyber
vercel env pull .env.production.local --environment production --yes --scope ridcyber
```

To migrate securely after pulling the ignored env file:

```powershell
./.venv/Scripts/python.exe -c "from scripts.deployment_env import load; load('.env.production.local'); from scripts.migrate_database import main; main()"
```

Deploy from the verified source:

```powershell
vercel deploy --prod --yes --no-wait --scope ridcyber
vercel inspect <actual-deployment-url> --logs --scope ridcyber
```

The GitHub connection also deploys pushes to the production branch. Do not force-push. Run backend tests, frontend lint/component tests and the production build before pushing. Public verification uses the stable production alias, without authentication-bypass tokens, and must exercise real inference rather than relying on a READY build alone.

## Public demo limitations

This is an anonymous shared educational demo. History and reports are visible to visitors; do not submit personal/sensitive information. It is not a private laboratory record system. The model probabilities are uncalibrated, measurement units/provenance are incompletely verified, and essential microbial/contaminant tests are absent. A positive model label does not establish drinking-water safety. Private clinical/laboratory use would require authentication, access controls and additional review.

Vercel's normal production alias is public, while preview/generated deployment URLs retain standard Vercel authentication protection. No security validation or model thresholds were disabled. Free service quotas may suspend availability when exhausted; no automatic paid upgrade was requested.

## Troubleshooting

- `PYTHON_ENTRYPOINT_NOT_FOUND`: check `tool.vercel.entrypoint` and root framework settings.
- Missing Python modules: Vercel prioritizes `pyproject.toml`; runtime dependencies must be in `[project.dependencies]`, not just a separate requirements file.
- Database failures: verify the Neon integration's production environment connection and apply the migration; never replace it with `/tmp` SQLite.
- Route refresh 404: confirm CDN build output and the explicit SPA rewrites are present in `vercel.json`.
- Oversized batch response: keep reference details in the saved analysis endpoint, preserving the compact response contract.
- Model changes: install the pinned scikit-learn/NumPy/SciPy versions and use trusted bundled artifacts. Row 250 must still produce RF class 1, probability 0.6263747470354587 and 3/5 agreement.

Official references: [Vercel getting started](https://vercel.com/get-started.md), [FastAPI deployment](https://vercel.com/docs/frameworks/backend/fastapi), [Python runtime](https://vercel.com/docs/functions/runtimes/python), [function limits](https://vercel.com/docs/functions/limitations), [SQLite limitations](https://vercel.com/kb/guide/is-sqlite-supported-in-vercel), [native integrations](https://vercel.com/docs/cli/integration).
