---
title: PMI-LCA Tool Concept
emoji: 📈
colorFrom: gray
colorTo: green
sdk: docker
pinned: false
license: bsd-3-clause
---

# PMI-LCA Tool Concept

A Panel-based web application for Process Mass Intensity Life Cycle Assessment.

## Pyodide Deployment

This app can be converted to run in the browser using Pyodide. The pyodide files in the `pyodide/` directory contain the necessary configuration.

### Important: Version Consistency

When updating the package version, ensure the following files are kept in sync:
- `panel_lca_app_concept/__init__.py` (`__version__`)
- `app/requirements_pyodide.txt`
- `pyodide/app.js` (wheel URL in `env_spec`)

To regenerate pyodide files after version updates:
```bash
panel convert app/app.py --requirements app/requirements_pyodide.txt --out pyodide --to pyodide-worker
```
