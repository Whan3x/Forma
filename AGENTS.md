# FORMA development guide

## Scope

Work in this existing checkout. Do not create another Git worktree unless the user explicitly asks for one. FORMA is a dependency-free Python 3.9+ / SQLite server with a vanilla JavaScript PWA in `public/`.

## Run and verify

- Start locally: `FORMA_DATA=/tmp/forma-dev-data python3 server.py`
- Health check: `curl -fsS http://127.0.0.1:8765/api/health`
- Python tests: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v`
- Frontend checks: `node --check public/planner.js && node --check public/app.js && node --check public/sw.js && node tests/test_planner.mjs && node tests/test_frontend_node.mjs`
- Python syntax: `python3 -m py_compile server.py`

Run the relevant checks after every behavioral change and the full set before handoff. A real-device check on iPhone and Android is required before claiming production mobile readiness.

## Product and design constraints

- Preserve user ownership checks for every private record and use parameterized SQL.
- Persist workout priority and exercise order when a workout starts; never reshuffle an active workout.
- Keep the core application functional without third-party packages or an OpenAI API key.
- Use system fonts, 44px minimum touch targets, 16px mobile form controls, safe-area insets, `dvh`, and restrained motion.
- Honor `prefers-reduced-motion`, `prefers-reduced-transparency`, and `prefers-contrast`.
- Keep hover effects inside a fine-pointer hover media query.
- Do not claim Apple/Google login, password recovery, push notifications, AI analysis, deployment, or device testing unless those paths were actually configured and verified.
