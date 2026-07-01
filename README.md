# PGxRx — Pharmacogenomics Prescription Decision Tool

> **VCF → PharmVar → CPIC Phenotype → Dosing Recommendation** in a single pipeline.

PGxRx takes patient VCF genotype data, maps variants to PharmVar drug-metabolizing enzyme
alleles, determines CPIC clinical phenotypes, and outputs evidence-based dosing
recommendations — with full report generation in JSON, CSV, HTML, and PDF.

## Features

- **Variant-to-allele mapping** using PharmVar nomenclature (20+ genes, 200+ alleles)
- **Phenotype determination** per CPIC guidelines with activity score thresholds
- **Dosing recommendations** for 30+ drug-gene pairs (A1/A2 evidence)
- **VCF input** with automatic gene region detection and coordinate normalization
- **Batch processing** of multiple samples and genes
- **Report generation**: JSON, CSV, HTML, PDF (via WeasyPrint)
- **CLI** (`pgxrx`) and **REST API** (FastAPI) interfaces
- **Offline-capable** with bundled reference data
- **Docker** support for reproducible deployments

## Installation

```bash
# From source
git clone https://github.com/example/pgxrx.git
cd pgxrx
pip install -e ".[all]"
```

### Docker

```bash
make docker
docker run -p 8000:8000 pgxrx:latest server
```

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
| ... 20+ more | | |

## Architecture

```
pgxrx/
├── core/              # Core pipeline logic
│   ├── variant.py     # Pydantic data models
│   ├── vcf_parser.py  # VCF parsing with gene detection
│   ├── allele_mapper.py  # Variant → PharmVar allele mapping
│   ├── diplotype.py   # Diplotype & activity score calculation
│   ├── phenotype.py   # CPIC phenotype determination
│   ├── dosing.py      # Dosing recommendation engine (30+ drug-gene pairs)
│   ├── engine.py      # Full pipeline orchestrator
│   └── liftover.py    # GRCh37 ↔ GRCh38 coordinate conversion
├── data/             # Knowledge base
│   ├── database.py    # SQLite database manager
│   ├── pharm_var.py   # PharmVar allele data
│   ├── cpic.py        # CPIC guideline data
│   ├── phargkb.py     # PharmGKB drug data
│   ├── rxnorm.py      # Drug name normalization
│   └── update.py      # Knowledge base updates
├── reports/          # Report generation
│   ├── json_report.py
│   ├── csv_report.py
│   ├── html_report.py
│   ├── pdf_report.py
│   └── templates/     # Jinja2 templates
├── api/              # REST API (FastAPI)
│   └── server.py
├── cli.py            # CLI (Typer)
└── tests/            # Test suite (80+ tests)
```

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

## Docker

```bash
# Build
make docker

# Run API server
docker run -p 8000:8000 pgxrx:latest server

# Run CLI
docker run pgxrx:latest annotate --gene CYP2C19 --allele1 *2 --allele2 *1 --drugs clopidogrel
```

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

## Disclaimer

PGxRx is a research/clinical decision support tool. Recommendations are based on
CPIC guidelines but should not replace clinical judgment. Always verify with the
latest CPIC and PharmVar guidelines before clinical use.

## License

MIT