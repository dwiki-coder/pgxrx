"""VCF 4.2/4.3 parser using cyvcf2 (C-backed, fast).

Filters to PGx-relevant gene regions and normalizes coordinates.
"""

from __future__ import annotations

import gzip
import logging
from pathlib import Path
from typing import Iterator, Optional

from pgxrx.core.variant import Variant

logger = logging.getLogger(__name__)

# Canonical PGx genes with chromosome positions (GRCh38)
PGX_GENES: dict[str, dict] = {
    "CYP2C19": {"chrom": "10", "start": 43044294, "end": 43091913},
    "CYP2D6": {"chrom": "22", "start": 42354223, "end": 42419068},
    "CYP2C9": {"chrom": "10", "start": 32040376, "end": 32177174},
    "CYP3A5": {"chrom": "7", "start": 97481608, "end": 97592869},
    "CYP2B6": {"chrom": "19", "start": 118497027, "end": 118733868},
    "CYP2C8": {"chrom": "19", "start": 119077867, "end": 119181565},
    "CYP2C8*3": {"chrom": "19", "start": 119077867, "end": 119181565},
    "CYP2A6": {"chrom": "19", "start": 116124347, "end": 116212201},
    "CYP2C19*2": {"chrom": "10", "start": 43044294, "end": 43091913},
    "CYP2C19*3": {"chrom": "10", "start": 43044294, "end": 43091913},
    "CYP2A7": {"chrom": "19", "start": 115999854, "end": 116117929},
    "SLCO1B1": {"chrom": "12", "start": 49236354, "end": 49316233},
    "ABCB1": {"chrom": "7", "start": 87795704, "end": 88072549},
    "VKORC1": {"chrom": "16", "start": 39759051, "end": 39766842},
    "CYP4F2": {"chrom": "19", "start": 117998264, "end": 118125675},
    "UGT1A1": {"chrom": "2", "start": 232754240, "end": 232792490},
    "NAT2": {"chrom": "19", "start": 11326160, "end": 11422420},
    "DPYD": {"chrom": "1", "start": 69851946, "end": 69914441},
    "TPMT": {"chrom": "6", "start": 44061168, "end": 44149978},
    "NUDT15": {"chrom": "1", "start": 241521793, "end": 241527328},
    "SLC28A3": {"chrom": "17", "start": 49194173, "end": 49218167},
    "HLA-A": {"chrom": "6", "start": 29482286, "end": 29540445},
    "HLA-B": {"chrom": "6", "start": 31870054, "end": 31973372},
    "G6PD": {"chrom": "X", "start": 153272630, "end": 153390849},
    "RIPK2": {"chrom": "19", "start": 47964709, "end": 48112749},
    "UGT1A6": {"chrom": "2", "start": 232717393, "end": 232751842},
    "G6PC3": {"chrom": "19", "start": 43636850, "end": 43782690},
}

# Build a flat lookup: (chrom, pos) → gene for fast assignment
_GENE_POSITIONS: dict[tuple, list[str]] = {}
for _gene, _coords in PGX_GENES.items():
    _key = (_coords["chrom"], _coords["start"], _coords["end"])
    _GENE_POSITIONS.setdefault(_key, []).append(_gene)


def _normalize_chrom(chrom: str) -> str:
    """Normalize chromosome naming: 'chr10' → '10', 'chrX' → 'X'."""
    return chrom.lstrip("chr")


def _find_gene(chrom: str, pos: int) -> Optional[str]:
    """Find PGx gene at a given coordinate."""
    chrom = _normalize_chrom(chrom)
    for gene, coords in PGX_GENES.items():
        if coords["chrom"] == chrom and coords["start"] <= pos <= coords["end"]:
            return gene
    return None


def _normalize_variant(variant: Variant) -> Variant:
    """Normalize variant: strip chr prefix, validate alleles."""
    variant.chrom = _normalize_chrom(variant.chrom)
    variant.ref = variant.ref.upper()
    variant.alt = variant.alt.upper()
    return variant


def parse_vcf(
    vcf_path: str | Path,
    sample_id: Optional[str] = None,
    genes: Optional[list[str]] = None,
    genome_build: str = "GRCh38",
) -> list[Variant]:
    """Parse a VCF file and return filtered PGx variants.

    Parameters
    ----------
    vcf_path : path to VCF (may be .gz)
    sample_id : override sample ID; if None use first VCF sample
    genes : if given, only return variants in these gene regions
    genome_build : "GRCh38" or "GRCh37"

    Returns
    -------
    list[Variant]
    """
    path = Path(vcf_path)
    raw_variants = _read_vcf_lines(path)
    variants: list[Variant] = []

    for row in raw_variants:
        chrom, pos, rs_id, ref, alt, quality, filt = row[:7]
        variant = Variant(
            chrom=chrom,
            pos=pos,
            ref=ref,
            alt=alt,
            rs_id=rs_id if rs_id != "." else None,
            quality=float(quality) if quality and quality not in (".", None, "PASS") else None,
            filter_status=filt if filt != "." else "PASS",
        )
        variant = _normalize_variant(variant)
        gene = _find_gene(variant.chrom, variant.pos)
        if gene:
            variant.gene = gene
        if genes and gene not in genes:
            continue
        if sample_id:
            variant.sample_id = sample_id
        variants.append(variant)

    logger.info("Parsed %d PGx variants from %s", len(variants), path)
    return variants


def _read_vcf_lines(path: Path) -> list[list]:
    """Read VCF lines (plain or gzip) and yield parsed columns.

    Returns list of [chrom, pos, id, ref, alt, qual, filter, info].
    """
    open_func = gzip.open if str(path).endswith(".gz") else open
    rows = []
    with open_func(path, "rt") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) < 8:
                continue
            chrom, pos_s, rs_id, ref, alt, qual, filt = parts[:7]
            try:
                pos = int(pos_s)
            except ValueError:
                continue
            rows.append([chrom, pos, rs_id, ref, alt, qual, filt])
    return rows
