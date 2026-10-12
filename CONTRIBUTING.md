# Contributing to GeoCore

Thank you for helping improve GeoCore. This guide explains how to report problems, propose changes and get a
pull request merged. Everyone taking part is expected to follow the [code of conduct](CODE_OF_CONDUCT.md).

## Ways to contribute

- **Report a bug.** Open an issue with the bug report form. Include the calculator, the inputs, what you expected
  and what you got, and your GeoCore version and operating system.
- **Check a calculation.** Independent hand calculations or published worked examples are very valuable. They become
  benchmark cases in `python-backend/core/catalogue/benchmarks.json`, and a method is shown as *verified* only when it
  reproduces them.
- **Improve the documentation.** User docs live in `website/_content/geocore/*.md`, and the Guide & Theory content
  for GeoCore's own calculators is in `website/_build/bis_docs.py`.
- **Add a calculation.** Open an issue first to agree on the method, the source (standard clause or paper) and the
  inputs.
- **Report a security issue privately.** See [SECURITY.md](SECURITY.md); please do not open a public issue.

## Ground rules for engineering code

GeoCore is an engineering tool, so correctness comes before features.

- **Calculations are deterministic.** Use groundhog where it has the method. Code a method in GeoCore only when
  groundhog does not, and cite the source (standard and clause, or paper) in the docstring.
- **Units are explicit.** Every input and output carries its unit (`"name [unit]"` in results, `[unit]` in
  docstrings). Never convert units silently.
- **Do not invent values.** Missing or out-of-scope inputs raise a clear error; they are never patched with a default
  the user did not choose.
- **GeoAI never calculates.** The model selects tools and explains results; all numbers come from the tool registry.
  The full rules are in [AGENTS.md](AGENTS.md).
- **Existing results must not change by accident.** The golden-output check (`python tests/golden/golden_tools.py
  check`, from `python-backend/`) must pass. Re-record only outputs you changed on purpose, and say so in the pull
  request.

## Development setup

See [Development](README.md#development) in the README. In short: Python 3.10+ for `python-backend/`, Node.js 22 for
`electron-app/`. CI runs Python 3.10, so do not use syntax that needs a newer version.

## Pull requests

1. Fork the repository and create a branch from `main`.
2. Keep the change focused: one fix or feature per pull request.
3. Add or update tests:
   - numerical results are compared against deterministic expected values, never against model output;
   - new tools get schema tests;
   - UI changes are checked in the app.
4. Run the checks before pushing:

   ```bash
   cd python-backend && python -m pytest tests/
   cd electron-app && npm run lint && npm run build
   python website/_build/build.py        # if you changed docs or the website
   ```

5. Add a line to the **Unreleased** section of the [changelog](website/_content/geocore/changelog.md), under
   Added, Changed or Fixed, written for users. Then run `python .github/scripts/changelog.py sync`.
6. Fill in the pull request template and describe how you verified the change.

## Commit messages

Write commit messages that say what changed and why (for example *"Fix settlement error for profiles without Cc"*).
Release notes are written from the changelog, not from commits, but clear messages make review and history easier.

## Licence

GeoCore is licensed under the [GNU GPL v3](LICENSE). By contributing, you agree that your contribution is licensed
under the same terms. Only contribute code and content you have the right to share; do not copy text or tables
from copyrighted standards. Implement the clause and cite it instead.
