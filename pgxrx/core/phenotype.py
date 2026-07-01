"""CPIC phenotype determination engine.

Maps diplotypes → activity scores → phenotypes per CPIC guidelines.

Phenotype rules are gene-specific. General framework:
  - PM  (Poor Metabolizer)
  - IM  (Intermediate Metabolizer)
  - NM  (Normal Metabolizer / Extensive Metabolizer)
  - UM  (Ultrarapid Metabolizer)

For non-metabolizing genes (HLA risk alleles):
  - "Positive" / "Negative"
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

from pgxrx.core.variant import Diplotype, PhenotypeResult

logger = logging.getLogger(__name__)

# ── Phenotype rules per gene ───────────────────────────────────────
# Each entry maps activity_score thresholds → phenotype name.
# Format: list of (min_score, max_score_inclusive, phenotype) sorted ascending.

_PHENOTYPE_RULES: dict[str, list[tuple[float, float, str]]] = {
    "CYP2C19": [
        (0.0, 0.0, "Poor Metabolizer"),
        (0.1, 1.0, "Intermediate Metabolizer"),
        (1.1, 2.0, "Normal Metabolizer"),
        (2.1, 3.0, "Ultrarapid Metabolizer"),
    ],
    "CYP2D6": [
        (0.0, 0.0, "Poor Metabolizer"),
        (0.01, 1.3, "Intermediate Metabolizer"),
        (1.31, 2.0, "Normal Metabolizer"),
        (2.01, 4.0, "Ultrarapid Metabolizer"),
    ],
    "CYP2C9": [
        (0.0, 0.2, "Poor Metabolizer"),
        (0.21, 1.3, "Intermediate Metabolizer"),
        (1.31, 2.0, "Normal Metabolizer"),
    ],
    "CYP3A5": [
        (0.0, 0.0, "Non-expresser"),
        (0.1, 1.0, "Reduced expresser"),
        (1.1, 2.0, "Normal expresser"),
    ],
    "SLCO1B1": [
        (0.0, 0.0, "Poor Metabolizer"),
        (0.01, 1.0, "Intermediate Metabolizer"),
        (1.01, 2.0, "Normal Metabolizer"),
    ],
    "DPYD": [
        (0.0, 0.2, "Poor Metabolizer"),
        (0.3, 1.0, "Intermediate Metabolizer"),
        (1.1, 2.0, "Normal Metabolizer"),
    ],
    "TPMT": [
        (0.0, 0.0, "Poor Metabolizer"),
        (0.01, 1.0, "Intermediate Metabolizer"),
        (1.01, 2.0, "Normal Metabolizer"),
    ],
    "NUDT15": [
        (0.0, 0.0, "Poor Metabolizer"),
        (0.1, 0.5, "Intermediate Metabolizer"),
        (0.6, 2.0, "Normal Metabolizer"),
    ],
    "UGT1A1": [
        (0.0, 0.0, "Poor Metabolizer"),
        (0.1, 1.0, "Intermediate Metabolizer"),
        (1.1, 2.0, "Normal Metabolizer"),
        (2.1, 3.0, "Ultrarapid Metabolizer"),
    ],
    "VKORC1": [
        (0.0, 0.5, "Low expresser"),
        (0.6, 1.5, "Intermediate expresser"),
        (1.6, 2.0, "Normal expresser"),
    ],
    "CYP2B6": [
        (0.0, 0.2, "Poor Metabolizer"),
        (0.3, 1.0, "Intermediate Metabolizer"),
        (1.1, 2.0, "Normal Metabolizer"),
    ],
    "CYP2A6": [
        (0.0, 0.0, "Poor Metabolizer"),
        (0.1, 1.0, "Intermediate Metabolizer"),
        (1.1, 2.0, "Normal Metabolizer"),
    ],
    "CYP2C8": [
        (0.0, 0.2, "Poor Metabolizer"),
        (0.3, 1.0, "Intermediate Metabolizer"),
        (1.1, 2.0, "Normal Metabolizer"),
    ],
    "NAT2": [
        (0.0, 0.2, "Poor acetylator"),
        (0.3, 1.0, "Intermediate acetylator"),
        (1.1, 2.0, "Rapid acetylator"),
    ],
    "ABCB1": [
        (0.0, 0.2, "Reduced efflux"),
        (0.3, 1.0, "Intermediate efflux"),
        (1.1, 2.0, "Normal efflux"),
    ],
}


def determine_phenotype(diplotype: Diplotype) -> PhenotypeResult:
    """Determine CPIC phenotype from a diplotype.

    Uses activity score thresholds to assign phenotype category.

    Parameters
    ----------
    diplotype : Diplotype with activity_score set

    Returns
    -------
    PhenotypeResult
    """
    gene = diplotype.gene
    score = diplotype.activity_score

    # Handle risk genes (HLA) separately
    if gene.startswith("HLA-"):
        phenotype_name = _check_hla_risk(gene, diplotype)
        return PhenotypeResult(
            gene=gene,
            diplotype=str(diplotype),
            activity_score=None,
            phenotype=phenotype_name,
            confidence="High",
        )

    # Handle G6PD separately
    if gene == "G6PD":
        phenotype_name = "Normal"
        return PhenotypeResult(
            gene=gene,
            diplotype=str(diplotype),
            activity_score=score,
            phenotype=phenotype_name,
            confidence="High",
        )

    # Standard metabolizer rules
    rules = _PHENOTYPE_RULES.get(gene)
    if rules is None:
        # Fallback generic rules
        rules = [
            (0.0, 0.0, "Poor Metabolizer"),
            (0.1, 1.0, "Intermediate Metabolizer"),
            (1.1, 2.0, "Normal Metabolizer"),
            (2.1, 4.0, "Ultrarapid Metabolizer"),
        ]

    for lo, hi, name in rules:
        if lo <= score <= hi:
            return PhenotypeResult(
                gene=gene,
                diplotype=str(diplotype),
                activity_score=score,
                phenotype=name,
                confidence="High",
            )

    # If score is 0 exactly
    if score == 0.0:
        return PhenotypeResult(
            gene=gene,
            diplotype=str(diplotype),
            activity_score=score,
            phenotype="Poor Metabolizer",
            confidence="High",
        )

    # Default fallback
    logger.warning("No phenotype rule matched for %s score=%s", gene, score)
    return PhenotypeResult(
        gene=gene,
        diplotype=str(diplotype),
        activity_score=score,
        phenotype="Unknown",
        confidence="Low",
    )


def _check_hla_risk(gene: str, diplotype: Diplotype) -> str:
    """Check HLA risk alleles."""
    risk_alleles = {
        "HLA-B": ["*57:01"],
        "HLA-A": ["*31:01", "*32:01", "*33:03"],
    }
    risk_set = risk_alleles.get(gene, [])
    alleles = [diplotype.allele1, diplotype.allele2]

    for a in alleles:
        if a in risk_set:
            return "Positive"
    return "Negative"
