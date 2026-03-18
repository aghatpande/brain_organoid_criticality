# brain_organoid_criticality
benchmarking organoid eephys data for criticality


Open, reproducible tools for benchmarking and measuring critical-like dynamics in neural population recordings, with an initial focus on brain organoid extracellular electrophysiology.

## Status

Early-stage project scaffold. The goal is to build an end-to-end open-source workflow for:
- ingesting spike-sorted and/or electrode-level neural recordings
- computing candidate criticality metrics
- benchmarking data sufficiency and quality for those metrics
- generating reproducible figures, reports, and notebooks

## Planned scope

Initial focus areas include:
- data ingestion and metadata normalization
- preprocessing of extracellular electrophysiology datasets
- avalanche-based analyses
- distance-from-criticality style metrics
- validation and robustness checks
- reproducible benchmark notebooks

## Repository structure

```text
src/        Python package source code
tests/      Unit and integration tests
notebooks/  Exploratory and tutorial notebooks
docs/       Project documentation and roadmap
scripts/    Command-line or utility scripts
data/       Data manifests and lightweight metadata only
results/    Generated outputs and summaries
```

## Installation
Clone the repository and install in editable mode:
```bash
git clone https://github.com/YOUR_USERNAME/brain_organoid_criticality.git
cd brain_organoid_criticality
pip install -e .
```
## Development goals
•	build reusable, documented analysis functions
•	support public benchmark datasets where possible
•	keep workflows transparent and reproducible
•	make outputs useful to both computational neuroscientists and experimental labs

## Contributing

Contributions, suggestions, and issue reports are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on the repository layout, recommended workflow, code style, and outstanding areas of work.

## License
This project is licensed under the Apache License 2.0.