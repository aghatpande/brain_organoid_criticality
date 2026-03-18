# Contributing to brain_organoid_criticality

Thank you for your interest in contributing! This document explains the project structure, the recommended development workflow, and the areas where help is most needed.

---

## Table of Contents

1. [Project overview](#1-project-overview)
2. [Repository structure](#2-repository-structure)
3. [Development environment setup](#3-development-environment-setup)
4. [Suggested contribution workflow](#4-suggested-contribution-workflow)
5. [Code style and tooling](#5-code-style-and-tooling)
6. [Testing](#6-testing)
7. [Outstanding issues and planned work](#7-outstanding-issues-and-planned-work)
8. [Submitting issues](#8-submitting-issues)
9. [Submitting pull requests](#9-submitting-pull-requests)
10. [License](#10-license)

---

## 1. Project overview

**brain_organoid_criticality** provides open, reproducible tools for benchmarking and measuring critical-like dynamics in neural population recordings, with an initial focus on brain organoid extracellular electrophysiology (eephys).

The long-term goal is an end-to-end workflow that:

- ingests spike-sorted and/or electrode-level neural recordings
- computes candidate criticality metrics (avalanche statistics, distance-from-criticality, etc.)
- benchmarks data sufficiency and quality for those metrics
- generates reproducible figures, reports, and notebooks

The project is in its **early scaffold stage**: directory structure and packaging are established, but most analysis modules are yet to be implemented. This makes it an ideal time to get involved and shape the design from the ground up.

---

## 2. Repository structure

```text
brain_organoid_criticality/
├── src/
│   └── brain_organoid_criticality/   # Installable Python package
│       └── __init__.py
├── tests/                            # pytest test suite
│   └── __init__.py
├── notebooks/                        # Exploratory and tutorial Jupyter notebooks
├── docs/                             # Project documentation and roadmap
│   └── roadmap.md
├── data/                             # Data manifests and lightweight metadata only
│   └── README.md                     # Instructions on data organisation
├── results/                          # Generated outputs and summaries (not tracked)
│   └── README.md
├── CONTRIBUTING.md                   # This file
├── CHANGELOG.md                      # Release history
├── LICENSE                           # Apache License 2.0
├── pyproject.toml                    # Package metadata and tool configuration
└── README.md                         # Project overview
```

### Key directories explained

| Directory | Purpose |
|-----------|---------|
| `src/brain_organoid_criticality/` | All importable Python modules live here. Keep modules focused (one responsibility per module). |
| `tests/` | Mirror the `src/` layout with `test_<module>.py` files. Every new function should have a corresponding test. |
| `notebooks/` | Exploratory notebooks are welcome; keep them self-contained and annotated. Avoid committing large output cells. |
| `docs/` | Narrative documentation and the project roadmap. |
| `data/` | Commit only manifests, checksums, or lightweight metadata — **never raw data files**. |
| `results/` | Generated figures and reports. This directory is listed in `.gitignore` to avoid accidental commits of large binary outputs. |

---

## 3. Development environment setup

### Prerequisites

- Python **3.10 or later**
- [Git](https://git-scm.com/)
- (Recommended) a dedicated virtual environment manager such as `venv`, `conda`, or `pyenv`

### Step-by-step

```bash
# 1. Fork the repository on GitHub, then clone your fork
git clone https://github.com/<your-username>/brain_organoid_criticality.git
cd brain_organoid_criticality

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # On Windows: .venv\Scripts\activate

# 3. Install the package in editable mode with optional dev dependencies
pip install -e ".[dev]"          # once [dev] extras are defined in pyproject.toml
# Until then, install the package itself:
pip install -e .

# 4. (Optional) Install recommended development tools
pip install ruff mypy pytest pytest-cov
```

> **Note:** As the project matures, a `[project.optional-dependencies]` section will be added to `pyproject.toml` to capture all development dependencies in one place. Until then, install tools individually as shown above.

---

## 4. Suggested contribution workflow

We follow a **fork-and-pull-request** model using short-lived feature branches.

```text
upstream/main  (aghatpande/brain_organoid_criticality)
      │
      └──▶ your fork/main  (your-username/brain_organoid_criticality)
                │
                └──▶ feature/my-feature  (your working branch)
```

### Step-by-step

```bash
# 1. Keep your fork up to date
git remote add upstream https://github.com/aghatpande/brain_organoid_criticality.git
git fetch upstream
git checkout main
git merge upstream/main

# 2. Create a descriptive feature branch
git checkout -b feature/avalanche-detection

# 3. Make your changes in small, focused commits
git add <files>
git commit -m "feat: add neuronal avalanche detection module"

# 4. Push to your fork
git push origin feature/avalanche-detection

# 5. Open a pull request against the upstream main branch on GitHub
```

### Commit message convention

We loosely follow the [Conventional Commits](https://www.conventionalcommits.org/) style:

| Prefix | When to use |
|--------|-------------|
| `feat:` | New feature or analysis module |
| `fix:` | Bug fix |
| `docs:` | Documentation only |
| `test:` | Adding or updating tests |
| `refactor:` | Code restructuring without behaviour change |
| `chore:` | Tooling, CI, packaging changes |

Example: `feat: add power-law exponent fitting for avalanche size distributions`

---

## 5. Code style and tooling

The project uses (or plans to use) the following tools. Please run them before submitting a PR.

### Linting and formatting — [Ruff](https://docs.astral.sh/ruff/)

```bash
ruff check src/ tests/          # Check for style and common errors
ruff format src/ tests/         # Auto-format code
```

### Type checking — [mypy](https://mypy.readthedocs.io/)

```bash
mypy src/
```

### General guidelines

- Follow [PEP 8](https://peps.python.org/pep-0008/) style.
- All public functions and classes should have [NumPy-style docstrings](https://numpydoc.readthedocs.io/en/latest/format.html), since this is a scientific project.
- Prefer explicit imports over wildcard imports (`from module import *`).
- Keep functions short and focused; extract helpers where logic becomes complex.
- Avoid hardcoded paths or dataset-specific magic constants — use parameters instead.

---

## 6. Testing

We use [pytest](https://docs.pytest.org/).

```bash
# Run the full test suite
pytest tests/

# Run with coverage report
pytest --cov=brain_organoid_criticality --cov-report=term-missing tests/
```

### What to test

- Every new function in `src/` should have at least one corresponding test in `tests/`.
- Test both expected behaviour (happy path) and edge cases (empty arrays, single spikes, etc.).
- Use synthetic / randomly generated data in unit tests — do not rely on real data files.

---

## 7. Outstanding issues and planned work

The following areas are open for contribution. If you intend to work on one, please open a GitHub issue first so we can coordinate.

### High priority

- [ ] **Data ingestion module** — readers for common eephys formats (NWB, MCS `.h5`, binary + header pairs). Start with a `loaders.py` module under `src/brain_organoid_criticality/`.
- [ ] **Spike-train utilities** — binning, inter-spike interval computation, population rate vectors. Add a `spikes.py` module.
- [ ] **Test infrastructure** — add `pytest` configuration (`pyproject.toml` `[tool.pytest.ini_options]` section), a `conftest.py` with shared fixtures, and a first set of smoke tests.
- [ ] **CI/CD pipeline** — add a GitHub Actions workflow (`.github/workflows/ci.yml`) to run linting and tests automatically on each pull request.

### Medium priority

- [ ] **Avalanche analysis** — implement neuronal avalanche detection (threshold crossings → avalanche catalogues), size and duration distributions, power-law fitting.
- [ ] **Criticality metrics** — branching ratio estimation, distance-from-criticality (DCC) measures, autocorrelation / Debye-Waller factor.
- [ ] **Benchmark notebooks** — Jupyter notebooks demonstrating the full analysis pipeline on a public dataset.
- [ ] **pyproject.toml dev extras** — define a `[project.optional-dependencies]` section (`dev`, `notebooks`) and lock versions.

### Lower priority / nice-to-have

- [ ] **Roadmap** (`docs/roadmap.md`) — fill in planned milestones and timeline.
- [ ] **Changelog** (`CHANGELOG.md`) — adopt [Keep a Changelog](https://keepachangelog.com/) format.
- [ ] **Data README** (`data/README.md`) — document expected data formats and sources.
- [ ] **Results README** (`results/README.md`) — document how results are organised and regenerated.
- [ ] **Documentation site** — set up [MkDocs](https://www.mkdocs.org/) or [Sphinx](https://www.sphinx-doc.org/) for API documentation.
- [ ] **Pre-commit hooks** — add a `.pre-commit-config.yaml` to enforce style checks automatically.

---

## 8. Submitting issues

Before opening a new issue, please search [existing issues](https://github.com/aghatpande/brain_organoid_criticality/issues) to avoid duplicates.

When opening an issue, include:

- **For bug reports:** steps to reproduce, expected vs. actual behaviour, Python version, OS, and any relevant stack trace.
- **For feature requests:** a short description of the use case, a sketch of the desired API or workflow, and any relevant references (papers, existing tools).
- **For questions:** context about what you are trying to do — we are happy to help.

---

## 9. Submitting pull requests

1. Make sure all tests pass locally (`pytest tests/`) and linting is clean (`ruff check src/ tests/`).
2. Add or update tests for any new functionality.
3. Update docstrings for any modified public API.
4. Open the PR against `main` with a clear title and description explaining *what* changed and *why*.
5. Reference any related issue with `Closes #<issue-number>` in the PR description.
6. Be responsive to review comments — we aim to review PRs within a week.

---

## 10. License

By contributing you agree that your contributions will be licensed under the **Apache License 2.0**, the same license that covers this project. See [LICENSE](LICENSE) for details.
