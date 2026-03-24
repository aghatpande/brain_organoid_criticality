# AGENTS.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

**brain_organoid_criticality** is an early-stage open-source toolkit for analyzing critical-like dynamics in neural recordings, particularly brain organoid extracellular electrophysiology (eephys) data. The project aims to build an end-to-end reproducible workflow for ingesting recordings, computing criticality metrics, and benchmarking data quality.

The project is intentionally in scaffold stage—directory structure is established but most analysis modules are yet to be implemented, making this an ideal time to shape the design.

## Repository Structure

```
src/brain_organoid_criticality/  — Main Python package
  ├── io.py                       — Path validation and I/O utilities
  ├── avalanches.py               — Spike binning and avalanche analysis
  └── __init__.py

tests/                            — pytest test suite (minimal coverage currently)
notebooks/                        — Exploratory and tutorial Jupyter notebooks
docs/                             — Project documentation (roadmap.md)
data/                             — Metadata and manifests only (no raw data)
results/                          — Generated outputs (.gitignore'd)
scripts/                          — CLI or utility scripts (empty)
```

Key design principle: The `src/` directory contains focused, single-responsibility modules. New analysis functionality should follow the same pattern (e.g., `spikes.py`, `metrics.py`, `loaders.py`).

## Build, Test, and Development Commands

### Setup
```bash
# Install package in editable mode
pip install -e .

# Install recommended dev tools (not yet in pyproject.toml [dev] extras)
pip install ruff mypy pytest pytest-cov numpy
```

### Testing
```bash
# Run full test suite
pytest tests/

# Run with coverage
pytest --cov=brain_organoid_criticality --cov-report=term-missing tests/

# Run a single test file or test function
pytest tests/test_avalanches.py
pytest tests/test_avalanches.py::test_bin_spike_times
```

### Linting and Type Checking
```bash
# Lint and check style
ruff check src/ tests/

# Auto-format code
ruff format src/ tests/

# Type check
mypy src/
```

### Development Workflow Tips
- Use `pip install -e .` in editable mode to pick up code changes immediately without reinstalling.
- Create virtual environment first: `python -m venv .venv && source .venv/bin/activate`.
- Mirror test file structure to source: if you add `src/brain_organoid_criticality/metrics.py`, create `tests/test_metrics.py`.

## Code Architecture and Patterns

### Module Organization
- **io.py**: Data path validation and format handling utilities. Expanding here means adding readers for NWB, MCS h5, and binary formats.
- **avalanches.py**: Core spike-binning logic (`bin_spike_times`) which is foundational for avalanche detection. Future expansion: avalanche cataloguing, power-law fitting, size/duration statistics.

### Key Dependencies
- **numpy**: All spike/data arrays use NumPy for performance (no pandas currently).
- **Dependencies are intentionally minimal** (`pyproject.toml` `dependencies = []`). New analysis modules should follow this principle and only add dependencies as needed. Future candidates: `scipy` (signal processing, statistics), `h5py` (HDF5 I/O), `nwbinspector` (NWB validation).

### Testing and Documentation Strategy
- **Docstrings**: Use NumPy-style docstrings for all public functions (this is a scientific project).
- **Tests**: Use synthetic/generated data only; do not depend on real data files in unit tests. Each new function needs at least one test covering the happy path and edge cases (empty arrays, single elements, boundary conditions).
- **No hardcoded paths or magic constants**: Always parameterize—bad: `bin_size = 0.01`, good: `bin_size: float` as a parameter.

## Notable Implementation Gaps (Near-term)

The CONTRIBUTING.md lists high-priority gaps that future agents may encounter or be asked to fill:

1. **Data loaders** (`loaders.py`): Common eephys formats (NWB, MCS, binary). Critical blocker for real-world use.
2. **Spike utilities** (`spikes.py`): Inter-spike interval computation, population rate vectors beyond basic binning.
3. **Test infrastructure**: `conftest.py` with shared fixtures; `pytest` configuration in `pyproject.toml`.
4. **CI/CD**: `.github/workflows/ci.yml` to enforce linting and tests on every PR.
5. **Avalanche analysis**: Threshold-crossing detection, avalanche catalogues, power-law fitting.
6. **Criticality metrics**: Branching ratio, distance-from-criticality (DCC), autocorrelation measures.
7. **Benchmark notebooks**: Full pipeline demonstrations on public datasets.

## Contribution Conventions

- **Commit messages**: Loosely follow [Conventional Commits](https://www.conventionalcommits.org/). Prefixes: `feat:` (new feature), `fix:` (bug), `docs:` (docs only), `test:` (tests), `refactor:` (restructure), `chore:` (tooling).
- **Branch naming**: Use short feature branches like `feature/avalanche-detection`.
- **Pull requests**: Reference related issues, ensure tests pass and linting is clean before submitting.
- **Code style**: PEP 8, explicit imports (no wildcard imports), keep functions short and focused.

## Key Files for Reference

- `CONTRIBUTING.md` — Detailed development workflow, outstanding work items, and testing guidelines.
- `README.md` — High-level project goals and repository overview.
- `pyproject.toml` — Python 3.10+, minimal dependencies, setuptools build.
