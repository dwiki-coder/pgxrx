"""CSV report generation."""

from __future__ import annotations

import csv
import io

from pgxrx.core.variant import InterpretationReport


def to_csv(reports: list[InterpretationReport]) -> str:
    """Serialize interpretation reports to CSV string."""
    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow([
        "sample_id", "gene", "diplotype", "activity_score",
        "phenotype", "phenotype_confidence", "drug", "recommendation",
        "evidence_level", "guideline_version", "timestamp",
    ])

    for r in reports:
        diplotype_str = str(r.diplotype) if r.diplotype else ""
        ascore = r.diplotype.activity_score if r.diplotype else ""
        phenotype = r.phenotype.phenotype if r.phenotype else ""
        confidence = r.phenotype.confidence if r.phenotype else ""

        if not r.dosing:
            # Write row without dosing
            writer.writerow([
                r.sample_id, r.gene, diplotype_str, ascore,
                phenotype, confidence, "", "", "", "", r.timestamp,
            ])
        else:
            for d in r.dosing:
                writer.writerow([
                    r.sample_id, r.gene, diplotype_str, ascore,
                    phenotype, confidence,
                    d.drug, d.recommendation,
                    d.evidence_level, d.guideline_version,
                    r.timestamp,
                ])

    return output.getvalue()


def to_csv_file(reports: list[InterpretationReport], path: str):
    """Write CSV report to file."""
    with open(path, "w", newline="") as f:
        f.write(to_csv(reports))
