## What and why

<!-- What does this change do for users, and why is it needed? Link the issue: "Fixes #…" -->

## How it was verified

<!-- Tests added or run, hand calculations, sources for expected values, screenshots for UI changes. -->

## Checklist

- [ ] Backend tests pass (`cd python-backend && python -m pytest tests/`)
- [ ] Golden outputs unchanged, or re-recorded on purpose and explained above (`python tests/golden/golden_tools.py check`)
- [ ] Frontend lints and builds (`cd electron-app && npm run lint && npm run build`), if the app changed
- [ ] Numerical results are compared with deterministic expected values, with units, and new methods cite their source
- [ ] The **Unreleased** section of `website/_content/geocore/changelog.md` describes the change for users
- [ ] Python 3.10 compatible; no new dependency without discussion
