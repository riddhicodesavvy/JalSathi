# JalSathi production verification

Verified on 15 November 2026 against the public production origin, without authentication bypass tokens or mocked API responses.

- Live application: https://jalsathi-ridcyber.vercel.app
- API: https://jalsathi-ridcyber.vercel.app/api/v1
- Health: https://jalsathi-ridcyber.vercel.app/api/v1/health
- Repository: https://github.com/riddhicodesavvy/JalSathi, production branch `main`.
- Vercel project: `ridcyber/jalsathi` (`prj_yyeAAbGMZGMCzSVNcPmmfJ4AdnWi`).
- Verified corrected Git deployment: `dpl_CBZ5iURNFhU6edwjFP1ZbE34Za1w`, status READY, source commit `2e3bf525494c8ada66f1a7aca30c749fd8aac9ce`. Automatic production deployments from `main` were observed. Release evidence: [GIT_RELEASE_VERIFICATION.json](GIT_RELEASE_VERIFICATION.json).

## Architecture and persistence

Vite assets run on Vercel's CDN; the full FastAPI application runs in the Python 3.12 runtime, with all five original core classifiers bundled. A real generated JavaScript asset returned HTTP 200 with `x-vercel-cache: HIT`; favicon and API docs returned 200. API calls use the relative HTTPS `/api/v1` path. Explicit SPA rewrites support the root and all six pages without intercepting API requests. Corrected build output reported a 309.21 MB uncompressed bundle, within the documented current 500 MB Python limit; successful deployment and inference establish compatibility for this release.

The dedicated `jalsathi-db` Neon resource uses the Free (`free_v3`) plan in `iad1`. Backend secrets are stored in Vercel, excluded from Git and frontend bundles. The initial idempotent schema migration was applied. No local user history was copied to the public database. Production rejects missing databases and SQLite rather than silently losing data. Reports regenerate from saved PostgreSQL analyses; temporary PDF files are disposable. No paid upgrade was selected.

## Public functional checks

The reproducible API suite is `python -m tests.verify_production --url https://jalsathi-ridcyber.vercel.app`. Its machine-readable results are in [PRODUCTION_API_RESULTS.json](../testing/PRODUCTION_API_RESULTS.json).

All **35/35 public API checks passed** on the corrected Git deployment. The prior deployment's saved positive analysis remained retrievable after redeployment, confirming history across deployments in addition to fresh-client persistence.

| Check | Observed result |
|---|---|
| Public root and six SPA pages | HTTP 200; real Vite application served |
| Health and model loading | Healthy PostgreSQL connection; CART, RF, AdaBoost, Gradient Boosting and Voting loaded |
| Dataset and metrics | Dataset SHA-256 and all five saved metric records match the local registry |
| Row 250 supplied measurements | Random Forest class 1; class-1 estimate **0.6263747470354587**; agreement **3/5** |
| Genuine negative source record | Class 0; RF class-1 estimate **0.039993588253182236**, matching direct inference |
| Exact inputs | All nine submitted values returned unchanged; no default replacement |
| Five genuine positive CSV samples | Five valid class-1 results; probabilities match original direct inference |
| CSV export / malformed CSV | Five exported rows; missing-column file rejected with HTTP 422 |
| PDF contents | Valid PDF; all nine original values, prediction, model version, analysis identity and scientific limitations verified |
| Model plots | Actual CART tree, GAM effect and RF evaluation PNGs load |
| Saved history | Positive and negative records retrievable; fresh client returns identical durable snapshot |

Browser verification runs with `cd frontend; npx playwright test --config playwright.production.config.ts`. All **three** workflows passed using installed Chrome at desktop 1586×1000, tablet 834×1112 and mobile 390×844. Each visits and refreshes all six pages, submits both genuine prediction states, checks exact request and response mappings, the selected-class estimate ring, all five indicators, model agreement and the independent guideline table. It downloads a PDF, renders the CART tree, uploads and exports the five-row CSV, checks malformed-file feedback and retrieves a saved analysis after navigation and refresh. Mobile navigation and absence of document overflow are checked. No page JavaScript errors were captured.

Screenshots: [desktop](../testing/production-desktop.png), [tablet](../testing/production-tablet.png), [mobile](../testing/production-mobile.png). Browser summary: [PRODUCTION_BROWSER_RESULTS.json](../testing/PRODUCTION_BROWSER_RESULTS.json).

## Repairs and release checks

- Added explicit Python entrypoint and complete pyproject runtime dependencies; the platform prioritizes pyproject over a separate requirements file.
- Fixed static-directory HTTP 500s and clean-Git static packaging failures. The generated Vite frontend is declared through `app.frontend()` with explicit CDN promotion despite logging/CORS middleware. Static files remain in the function as a fallback, and SPA rewrites preserve direct navigation. Merely setting an output directory did not resolve Python static discovery; the corrected Git deployment is verified separately from the CLI candidate.
- Replaced ephemeral SQLite production history with dedicated PostgreSQL and an explicit migration.
- Generated PDFs under the writable temporary directory while retaining durable source records.
- Reduced the maximum batch payload below Vercel's 4.5 MB response limit, retaining all measurements and model outputs. Full guideline/disclaimer details remain available through each analysis URL and in the database.
- Updated vulnerable development tooling; final npm audit reports **zero vulnerabilities**. Lint, four component tests and the production TypeScript/Vite build pass. **43/43 backend tests pass with 97% application coverage**, including the unchanged Row 250 probability and maximum 1,000-row response regression.
- Trained artifacts, data bytes, thresholds and recorded model metrics were preserved. Models were not retrained to produce positive demonstrations.
- Runtime error/fatal logs for the verified candidate returned no entries after the successful public checks. Earlier failed candidates were investigated and replaced.

## Limits

This is an anonymous shared educational demo. Saved analyses and reports are visible to visitors; it is not a private laboratory record system. Predictions are uncalibrated screening estimates, with incomplete dataset unit/provenance verification and weak minority-class recall. Predicted Potable does not certify drinking-water safety. Free Vercel/Neon quotas can limit availability. Optional GAM and likelihood-average explanations use saved metadata/plots; only the five core classifiers are exposed for prediction.

Deployment commands, environment settings, migrations and troubleshooting are documented in [docs/DEPLOYMENT.md](../../docs/DEPLOYMENT.md).
