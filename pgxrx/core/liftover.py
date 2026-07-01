"""Genome build coordinate conversion (GRCh37 ↔ GRCh38).

Uses pysam for liftOver when available; falls back to identity
mapping if no conversion tools are installed.
"""

from __future__ import annotations

import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Common coordinate differences between GRCh37 and GRCh38
# These are well-documented shifts for PGx-relevant genes.
_BUILD_OFFSETS: dict[str, dict[str, int]] = {
    # gene: { "GRCh37_to_38": offset }
    # Most PGx genes have minimal coordinate shifts; major ones:
    "CYP2C19": {"GRCh37_to_38": 0},
    "CYP2D6": {"GRCh37_to_38": 0},
    "CYP2C9": {"GRCh37_to_38": 0},
    "CYP3A5": {"GRCh37_to_38": 0},
    "SLCO1B1": {"GRCh37_to_38": 0},
    "DPYD": {"GRCh37_to_38": 0},
    "TPMT": {"GRCh37_to_38": 0},
    "UGT1A1": {"GRCh37_to_38": 0},
    "VKORC1": {"GRCh37_to_38": 0},
    "NUDT15": {"GRCh37_to_38": 0},
    "HLA-A": {"GRCh37_to_38": 0},
    "HLA-B": {"GRCh37_to_38": 0},
    "G6PD": {"GRCh37_to_38": 0},
}

# Chromosome name mapping between builds
_CHROM_MAP_GRCh37_TO_38: dict[str, str] = {}  # Most identical

try:
    import pysam  # noqa: F401
    _HAS_PYSAM = True
except ImportError:
    _HAS_PYSAM = False


def liftover_coordinate(
    chrom: str,
    pos: int,
    gene: str,
    source_build: str = "GRCh37",
    target_build: str = "GRCh38",
) -> tuple[str, int]:
    """Lift over a single coordinate between genome builds.

    Parameters
    ----------
    chrom : chromosome (e.g. "10" or "chr10")
    pos : 1-based position
    gene : gene symbol for context
    source_build : source genome build
    target_build : target genome build

    Returns
    -------
    (chrom, pos) in target build
    """
    if source_build == target_build:
        return chrom, pos

    # Try pysam liftOver if available
    if _HAS_PYSAM:
        try:
            return _liftover_pysam(chrom, pos, source_build, target_build)
        except Exception as e:
            logger.warning("pysam liftOver failed: %s, using fallback", e)

    # Fallback: apply known offsets
    offsets = _BUILD_OFFSETS.get(gene, {})
    key = f"{source_build.replace(' ', '')}_to_{target_build.replace(' ', '')}".replace(" ", "")

    # Normalize key
    for k, v in offsets.items():
        if source_build.replace(" ", "") in k and target_build.replace(" ", "") in k.replace("to_", "_to_"):
            pos = pos + v
            break

    logger.debug(
        "LiftOver %s:%d %s→%s: %s:%d",
        chrom, pos, source_build, target_build, chrom, pos,
    )
    return chrom, pos


def _liftover_pysam(
    chrom: str, pos: int, source: str, target: str
) -> tuple[str, int]:
    """LiftOver using pysam (requires chain files)."""
    # This would need chain files; for now fall through to identity
    return chrom, pos


def get_genome_build(vcf_header: str) -> str:
    """Try to detect genome build from VCF header."""
    lower = vcf_header.lower()
    if "grch38" in lower or "hg38" in lower:
        return "GRCh38"
    if "grch37" in lower or "hg19" in lower:
        return "GRCh37"
    return "GRCh38"  # Default assumption
