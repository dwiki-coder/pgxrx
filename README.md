# PGxRx — Pharmacogenomics Prescription Decision Tool

[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://github.com/dwiki-coder/pgxrx/actions/workflows/test.yml/badge.svg)](https://github.com/dwiki-coder/pgxrx/actions/workflows/test.yml)
[![Coverage](https://img.shields.io/badge/Coverage-87%25-brightgreen)](https://github.com/dwiki-coder/pgxrx)

> **VCF → PharmVar → CPIC Phenotype → Dosing Recommendation** in a single pipeline.

PGxRx takes patient VCF genotype data, maps variants to PharmVar drug-metabolizing
enzyme alleles, determines CPIC clinical phenotypes, and outputs evidence-based
dosing recommendations — with full report generation in JSON, CSV, HTML, and PDF.

---

## Why This Tool

Most pharmacogenomics tools require manual allele lookup followed by guideline
cross-referencing — a slow, error-prone process. PGxRx automates the entire
workflow from raw VCF genotype data through CPIC-compliant dosing recommendations,
eliminating manual interpretation steps. It implements **30+ drug-gene pairs** at
A1/A2 evidence level (CPIC's highest-confidence tier) and works offline with
bundled reference data — ideal for clinical environments without internet access.

---

## Metrics

| Metric | Value |
|--------|-------|
| Automated tests | **166** across 11 test files |
| Genes covered | **20+** (CYP2C19, CYP2D6, CYP2C9, SLCO1B1, TPMT, DPYD, HLA-B, HLA-A, VKORC1, …) |
| Alleles mapped | **200+** using PharmVar nomenclature |
| Drug-gene pairs | **30+** with CPIC A1/A2 evidence-level recommendations |
| Output formats | **4** — JSON, CSV, HTML, PDF |
| REST API endpoints | **9** |
| Source code | **4,604 LOC** across 40 Python files |

---

## Who Should Use This

- **Clinical pharmacists and genetic counselors** interpreting PGx results for patients
- **EHR vendors** building pharmacogenomics decision support modules
- **CROs** offering pharmacogenomics testing and interpretation services
- **Clinical labs** implementing CPIC guidelines for genotype-guided prescribing
- **Biopharma R&D** teams evaluating drug-gene interactions in trial populations

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    User Interface Layer                         │
│  ┌──────────┐  ┌──────────┐  ┌────────────────────────────┐    │
│  │   CLI    │  │  REST    │  │  Python Library (import)    │    │
│  │  (Typer) │  │  API     │  │                              │    │
│  │          │  │(FastAPI) │  │  from pgxrx.core import…    │    │
│  └────┬─────┘  └────┬─────┘  └──────────┬─────────────────┘    │
│       │             │                    │                      │
│       └──────────────┼────────────────────┘                      │
│                      ▼                                           │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Core Pipeline Logic                         │   │
│  │  VCF Parser → Allele Mapper → Diplotype → Phenotype →   │   │
│  │  Dosing Engine → Report Generator                       │   │
│  └─────────────────────────────────────────────────────────┘   │
│                      │                                          │
│  ┌───────────────────┴──────────────────────────────────────┐  │
│  │              Data & Infrastructure Layer                  │  │
│  │  ┌────────┐  ┌──────────┐  ┌─────┐  ┌────────────────┐  │  │
│  │  │SQLite  │  │  Jinja2  │  │Docker│  │GRCh37/38       │  │  │
│  │  │KB      │  │  Templates│  │      │  │ Liftover       │  │  │
│  │  └────────┘  └──────────┘  └─────┘  └────────────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
```

### Pipeline Flow

```
Patient VCF ──► VCF Parser ──► Variant → Allele Mapping ──► Diplotype &
                │                  (PharmVar, 200+ alleles)    │
                ▼                                              ▼
          Gene Region                                Activity Score Calculation
          Detection                                      (CPIC rules)
                │                                              │
                └────────────────► Phenotype ◄─────────────────┘
                                     │
                                     ▼
                              Dosing Recommendation
                              (30+ drug-gene pairs)
                                     │
                                     ▼
                              Multi-format Report
                              (JSON / CSV / HTML / PDF)
```

---

## Features

- **Variant-to-allele mapping** using PharmVar nomenclature (20+ genes, 200+ alleles)
- **Phenotype determination** per CPIC guidelines with activity score thresholds
- **Dosing recommendations** for 30+ drug-gene pairs (A1/A2 evidence)
- **VCF input** with automatic gene region detection and coordinate normalization
- **Batch processing** of multiple samples and genes
- **Report generation**: JSON, CSV, HTML, PDF (via WeasyPrint)
- **CLI** (`pgxrx`) and **REST API** (FastAPI) interfaces
- **Offline-capable** with bundled reference data
- **GRCh37 ↔ GRCh38 liftover** for coordinate normalization
- **Docker** support for reproducible deployments

---

## Installation

```bash
# From source
git clone https://github.com/dwiki-coder/pgxrx.git
cd pgxrx
pip install -e ".[all]"
```

### Docker

```bash
make docker
docker run -p 8000:8000 pgxrx:latest server
```

---

## Quick Start

### CLI

```bash
# Annotate a patient's CYP2C19 genotype
pgxrx annotate \
  --gene CYP2C19 --allele1 *2 --allele2 *1 \
  --drugs clopidogrel

# Determine phenotype only
pgxrx phenotype --gene CYP2C19 --allele1 *2 --allele2 *2

# Get dosing recommendation
pgxrx dose --drug clopidogrel --gene CYP2C19 \
  --phenotype "Intermediate Metabolizer"

# Generate a full report from VCF
pgxrx report \
  --vcf patient.vcf.gz \
  --drugs clopidogrel warfarin codeine \
  --output report.pdf \
  --format pdf \
  --patient "John Doe"
```

### Python API

```python
from pgxrx.core.engine import PGxEngine

engine = PGxEngine()

# Interpret a genotype
report = engine.interpret_direct(
    gene="CYP2C19",
    allele1="*2",
    allele2="*1",
    drugs=["clopidogrel"],
    sample_id="PATIENT001",
)

print(f"Phenotype: {report.phenotype.phenotype}")
for d in report.dosing:
    print(f"  {d.drug}: {d.recommendation}")
```

### REST API

```bash
# Start the server
pgxrx server --port 8000

# Use the API
curl -X POST http://localhost:8000/annotate \
  -H "Content-Type: application/json" \
  -d '{
    "gene": "CYP2C19",
    "allele1": "*2",
    "allele2": "*1",
    "drugs": ["clopidogrel"]
  }'
```

---

## Supported Drug-Gene Pairs

| Drug | Gene | CPIC Guideline |
|------|------|---------------|
| Clopidogrel | CYP2C19 | A1 |
| Codeine | CYP2D6 | A1 |
| Tamoxifen | CYP2D6 | A1 |
| Warfarin | CYP2C9 + VKORC1 | A1 |
| Simvastatin | SLCO1B1 | A1 |
| Abacavir | HLA-B | A1 |
| Mercaptopurine | TPMT | A1 |
| Azathioprine | TPMT | A1 |
| Carbamazepine | HLA-A | A1 |
| Oxcarbazepine | HLA-A | A1 |
| 5-Fluorouracil | DPYD | A2 |
| Irinotecan | DPYD | A2 |
| … 20+ more | | |

---

## API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check |
| `/annotate` | POST | Full annotation + phenotype + dosing |
| `/phenotype` | POST | Phenotype determination only |
| `/dose` | POST | Dosing recommendation for drug-gene-phenotype |
| `/genes` | GET | List supported genes |
| `/drugs` | GET | List supported drugs |
| `/genes/{gene}/drugs` | GET | Drugs for a gene |
| `/drugs/{drug}/genes` | GET | Genes for a drug |
| `/vcf` | POST | Process VCF file |

---

## Reports

Generate publication-ready reports:

```bash
# JSON
pgxrx report --gene CYP2C19 --allele1 *2 --allele2 *1 \
  --drugs clopidogrel --format json --output report.json

# HTML
pgxrx report --gene CYP2C19 --allele1 *2 --allele2 *1 \
  --drugs clopidogrel --format html --output report.html

# PDF (requires WeasyPrint)
pgxrx report --gene CYP2C19 --allele1 *2 --allele2 *1 \
  --drugs clopidogrel --format pdf --output report.pdf

# From VCF
pgxrx report --vcf patient.vcf --drugs clopidogrel warfarin \
  --format pdf --output full_report.pdf --patient "John Doe"
```

---

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Run tests with coverage
pytest tests/ --cov=pgxrx --cov-report=term-missing

# Lint & format
ruff check pgxrx/ tests/
ruff format pgxrx/ tests/
```

---

## Docker

```bash
# Build
make docker

# Run API server
docker run -p 8000:8000 pgxrx:latest server

# Run CLI
docker run pgxrx:latest annotate --gene CYP2C19 --allele1 *2 --allele2 *1 --drugs clopidogrel
```

---

## Citation

```bibtex
@software{pgxrx,
  author       = {David},
  title        = {{PGxRx: Pharmacogenomics Prescription Decision Tool}},
  year         = {2026},
  url          = {https://github.com/dwiki-coder/pgxrx},
  license      = {MIT}
}
```

---

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## Disclaimer

PGxRx is a research/clinical decision support tool. Recommendations are based on
CPIC guidelines but should not replace clinical judgment. Always verify with the
latest CPIC and PharmVar guidelines before clinical use.

---

## License

MIT
