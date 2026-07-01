"""JSON report generation."""

from __future__ import annotations

import json
from typing import Optional

from pgxrx.core.variant import InterpretationReport


def to_json(reports: list[InterpretationReport], indent: int = 2) -> str:
    """Serialize interpretation reports to JSON string."""
    data = []
    for r in reports:
        entry = {
            "sample_id": r.sample_id,
            "gene": r.gene,
            "diplotype": str(r.diplotype) if r.diplotype else None,
            "activity_score": r.diplotype.activity_score if r.diplotype else None,
            "phenotype": r.phenotype.phenotype if r.phenotype else None,
            "phenotype_confidence": r.phenotype.confidence if r.phenotype else None,
            "variants": [
                {
                    "allele_symbol": v.allele_symbol,
                    "rs_id": v.rs_id,
                    "genotype": v.genotype,
                }
                for v in r.variants
            ],
            "allele_calls": [
                {
                    "allele_name": ac.allele_name,
                    "rs_ids": ac.rs_ids,
                    "activity_score": ac.activity_score,
                }
                for ac in r.allele_calls
            ],
            "dosing": [
                {
                    "drug": d.drug,
                    "phenotype": d.phenotype,
                    "recommendation": d.recommendation,
                    "evidence_level": d.evidence_level,
                    "guideline_version": d.guideline_version,
                }
                for d in r.dosing
            ],
            "timestamp": r.timestamp,
        }
        data.append(entry)
    return json.dumps(data, indent=indent)


def to_json_file(reports: list[InterpretationReport], path: str):
    """Write JSON report to file."""
    with open(path, "w") as f:
        f.write(to_json(reports))
