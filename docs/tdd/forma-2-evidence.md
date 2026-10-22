# FORMA 2.0 — TDD evidence

Date: 2026-10-22  
Branch: `work`

## Scope

- Persist a workout priority and stable exercise order.
- Rotate Upper and Lower priorities with deterministic ordering.
- Migrate an existing FORMA 1.0 SQLite database without deleting data.
- Reject foreign, duplicate, wrong-plan, and malformed exercise IDs.
- Reject Host-derived origins when `FORMA_PUBLIC_URL` is configured.
- Keep the frontend renderable and escaped after adding the Plans screen.

## RED

Checkpoint: `60829e6` (`test: define stable workout planning behavior`)

Commands:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
node tests/test_planner.mjs
```

Observed failures before production changes:

- workout response raised `KeyError: 'priority'`;
- migration assertion reported that `priority` was absent from the v1 `workouts` table;
- Node reported `ERR_MODULE_NOT_FOUND` for `public/planner.js`.

The production-origin regression was also run before its fix:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_server.FormaIntegration.test_validation_and_csrf -v
```

Observed failure: configured production mode returned HTTP 200 for the Host-derived local origin where the test required HTTP 403.

## GREEN

Checkpoint: `51a1c36` (`feat: implement FORMA 2 planner and mobile redesign (GREEN)`)

Commands:

```sh
git diff --check
node --check public/planner.js
node --check public/app.js
node --check public/sw.js
node tests/test_planner.mjs
node tests/test_frontend_node.mjs
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
PYTHONDONTWRITEBYTECODE=1 python3 -m py_compile server.py
```

Observed result: planner and frontend render tests passed; Python ran 7 tests successfully with 2 macOS-only JavaScriptCore tests skipped. Their syntax/render coverage is provided in Linux by the explicit Node checks and `test_frontend_node.mjs`.

## Runtime and packaging evidence

- Local `GET /api/health` returned `{"ok": true}`.
- `GET /api/config` returned version `2.0.0`.
- `docker build -t forma:test .` completed successfully from `python:3.12-slim`.
- The built image was started in production mode and its health endpoint returned HTTP 200.
- The container response included HSTS, CSP, `X-Frame-Options: DENY`, COOP, CORP, and Permissions Policy headers.
- Secret-pattern and dynamic-SQL searches returned no findings.

## Limitations

- Coverage percentage was not measured because this dependency-free repository has no coverage tool configured; behavior is covered by integration and pure-function tests.
- Headless Chromium fetched the application shell and assets but did not terminate or emit a screenshot because this cloud container lacks working DBus/zygote support. No visual-browser pass is claimed.
- A real iPhone and Android check remains required before production mobile readiness is claimed.
