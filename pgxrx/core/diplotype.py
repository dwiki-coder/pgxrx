"""Diplotype calculator.

Combines allele calls from two chromosomes into a diplotype
(e.g. *1/*2) and computes the combined activity score.
"""

from __future__ import annotations

import logging
from typing import Optional

from pgxrx.core.variant import AlleleCall, Diplotype

logger = logging.getLogger(__name__)

# Default activity scores per allele for phenotype rules
# Gene → {allele_name: activity_score}
_DEFAULT_ACTIVITY_SCORES: dict[str, dict[str, float]] = {
    "CYP2C19": {
        "*1": 1.0, "*2": 0.0, "*3": 0.0, "*4": 0.0, "*5": 0.0,
        "*6": 0.0, "*7": 0.5, "*8": 0.0, "*10": 0.3, "*11": 1.5,
        "*12": 0.0, "*13": 1.3, "*14": 0.0, "*15": 0.3, "*16": 1.0,
        "*17": 1.3, "*21": 0.5, "*22": 0.0, "*23": 0.0, "*24": 0.0,
    },
    "CYP2D6": {
        "*1": 1.0, "*2": 1.0, "*3": 0.0, "*4": 0.0, "*5": 0.0,
        "*6": 0.0, "*7": 0.3, "*10": 0.3, "*17": 0.3, "*29": 0.3,
        "*36": 0.3, "*41": 0.0, "*46": 0.3, "*1xN": 2.0,
    },
    "CYP2C9": {
        "*1": 1.0, "*2": 0.3, "*3": 0.1, "*5": 0.0, "*6": 0.0, "*8": 0.3,
    },
    "CYP3A5": {
        "*1": 1.0, "*1A": 1.0, "*1B": 1.0, "*1F": 1.0,
        "*2": 0.0, "*3": 0.0, "*4": 0.0,
    },
    "SLCO1B1": {
        "*1": 1.0, "*5": 0.0, "*11": 0.3, "*12": 0.3, "*15": 0.0,
    },
    "DPYD": {
        "*1": 1.0, "*2A": 0.0, "*4": 0.0, "*6": 0.0,
        "*7": 0.3, "*13": 0.0, "c.1679T>G": 0.3,
    },
    "TPMT": {
        "*1": 1.0, "*2": 0.0, "*3A": 0.0, "*3B": 0.0,
        "*3C": 0.0, "*3D": 0.0, "*3F": 0.3, "*3J": 0.0, "*3L": 0.0,
    },
    "NUDT15": {
        "*1": 1.0, "*2": 0.0, "*3": 0.0,
    },
    "UGT1A1": {
        "*1": 1.0, "*6": 0.0, "*28": 0.3, "*29": 1.3,
        "*37": 0.3, "*60": 0.0,
    },
    "VKORC1": {
        "*1": 1.0, "*2": 0.3, "*3": 0.5,
    },
    "CYP2B6": {
        "*1": 1.0, "*4": 0.3, "*6": 0.3,
    },
    "CYP2A6": {
        "*1": 1.0, "*2": 0.3, "*4": 0.0, "*9": 0.0,
        "*10": 0.3, "*12": 0.0, "*13": 0.0, "*14": 0.0,
        "*17": 0.3, "*19": 0.3, "*22": 0.0,
    },
    "CYP2C8": {
        "*1": 1.0, "*3": 0.3, "*4": 0.3,
    },
    "NAT2": {
        "*1": 1.0, "*5": 0.3, "*6": 0.3, "*7": 0.3,
        "*10": 0.3, "*11": 0.3, "*12": 0.3, "*14": 0.3, "*17": 0.3,
    },
    "ABCB1": {
        "*1": 1.0, "*2": 0.7, "*4": 0.7, "*6": 0.7, "*22": 0.3, "*31": 0.3,
    },
}


def _get_activity(gene: str, allele: str) -> float:
    """Look up activity score for a gene-allele pair."""
    scores = _DEFAULT_ACTIVITY_SCORES.get(gene, {})
    return scores.get(allele, 1.0)


def compute_diplotype(
    allele_calls: list[AlleleCall],
    gene: str,
) -> Diplotype:
    """Compute diplotype from allele calls on two chromosomes.

    Parameters
    ----------
    allele_calls : list of AlleleCall objects (typically 2)
    gene : gene symbol

    Returns
    -------
    Diplotype
    """
    if not allele_calls:
        # No variant calls → assume reference
        return Diplotype(
            gene=gene,
            allele1="*1",
            allele2="*1",
            activity_score=2.0,
        )

    # Sort by chrom_source to assign chr1/chr2
    sorted_calls = sorted(allele_calls, key=lambda c: c.chrom_source)

    allele1 = sorted_calls[0].allele_name if len(sorted_calls) > 0 else "*1"
    allele2 = sorted_calls[1].allele_name if len(sorted_calls) > 1 else "*1"

    # Compute combined activity score
    as1 = _get_activity(gene, allele1)
    as2 = _get_activity(gene, allele2)
    total_activity = as1 + as2

    return Diplotype(
        gene=gene,
        allele1=allele1,
        allele2=allele2,
        activity_score=total_activity,
    )


def compute_diplotype_from_alleles(
    allele1: str,
    allele2: str,
    gene: str,
) -> Diplotype:
    """Compute diplotype directly from two allele names."""
    as1 = _get_activity(gene, allele1)
    as2 = _get_activity(gene, allele2)
    return Diplotype(
        gene=gene,
        allele1=allele1,
        allele2=allele2,
        activity_score=as1 + as2,
    )
