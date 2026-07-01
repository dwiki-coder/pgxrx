"""Variant-to-allele mapper using PharmVar allele nomenclature.

Maps variant coordinates or rsIDs to PharmVar allele symbols (e.g. *2).
Uses bundled PharmVar allele definition data stored in SQLite.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Optional

from pgxrx.core.variant import AlleleCall, Variant

logger = logging.getLogger(__name__)

# ── Bundled PharmVar-style allele definitions ──────────────────────────
# Format: { gene: { allele_name: { "activity_score": float, "variants": [...] } } }
# Variants listed as rsIDs for portability; coordinates secondary.

_PHARMVAR_ALLELES: dict = {
    "CYP2C19": {
        "*1": {"activity_score": 1.0, "variants": [], "description": "Reference / normal function"},
        "*2": {"activity_score": 0.0, "variants": ["rs4244285"], "description": "Loss of function"},
        "*3": {"activity_score": 0.0, "variants": ["rs4986902"], "description": "Loss of function"},
        "*4": {"activity_score": 0.0, "variants": ["rs56337373", "rs56337374"], "description": "Loss of function"},
        "*5": {"activity_score": 0.0, "variants": ["rs17822135"], "description": "Loss of function"},
        "*6": {"activity_score": 0.0, "variants": ["rs4149056"], "description": "Loss of function"},
        "*7": {"activity_score": 0.5, "variants": ["rs12777823"], "description": "Reduced function"},
        "*8": {"activity_score": 0.0, "variants": ["rs12777824"], "description": "Loss of function"},
        "*10": {"activity_score": 0.3, "variants": ["rs5030653"], "description": "Reduced function"},
        "*11": {"activity_score": 1.5, "variants": ["rs7638510"], "description": "Increased function"},
        "*12": {"activity_score": 0.0, "variants": ["rs28398879", "rs28398880"], "description": "Loss of function"},
        "*13": {"activity_score": 1.3, "variants": ["rs2637155"], "description": "Increased function"},
        "*14": {"activity_score": 0.0, "variants": ["rs121908824"], "description": "Loss of function"},
        "*15": {"activity_score": 0.3, "variants": ["rs55036960"], "description": "Reduced function"},
        "*16": {"activity_score": 1.0, "variants": ["rs112861174"], "description": "Normal function"},
        "*17": {"activity_score": 1.3, "variants": ["rs12248560"], "description": "Increased function"},
        "*21": {"activity_score": 0.5, "variants": ["rs57383978"], "description": "Reduced function"},
        "*22": {"activity_score": 0.0, "variants": ["rs110472182"], "description": "Loss of function"},
        "*23": {"activity_score": 0.0, "variants": ["rs141768685"], "description": "Loss of function"},
        "*24": {"activity_score": 0.0, "variants": ["rs78412513"], "description": "Loss of function"},
        "*1L": {"activity_score": 1.3, "variants": ["rs12777824", "rs12777823"], "description": "Promoter variant"},
    },
    "CYP2D6": {
        "*1": {"activity_score": 1.0, "variants": [], "description": "Reference / normal function"},
        "*2": {"activity_score": 1.0, "variants": ["rs16947"], "description": "Normal function"},
        "*3": {"activity_score": 0.0, "variants": ["rs5030655"], "description": "Loss of function"},
        "*4": {"activity_score": 0.0, "variants": ["rs3894978"], "description": "Loss of function"},
        "*5": {"activity_score": 0.0, "variants": ["rs1801138"], "description": "Gene deletion / LoF"},
        "*6": {"activity_score": 0.0, "variants": ["rs5030654"], "description": "Loss of function"},
        "*7": {"activity_score": 0.3, "variants": ["rs2032582"], "description": "Reduced function"},
        "*10": {"activity_score": 0.3, "variants": ["rs1065852"], "description": "Reduced function"},
        "*17": {"activity_score": 0.3, "variants": ["rs7821509"], "description": "Reduced function"},
        "*29": {"activity_score": 0.3, "variants": ["rs5030651"], "description": "Reduced function"},
        "*36": {"activity_score": 0.3, "variants": ["rs5030650"], "description": "Reduced function"},
        "*41": {"activity_score": 0.0, "variants": ["rs16873729"], "description": "Loss of function"},
        "*46": {"activity_score": 0.3, "variants": ["rs5030652"], "description": "Reduced function"},
        "*1xN": {"activity_score": 2.0, "variants": [], "description": "Gene duplication / ultrarapid"},
    },
    "CYP2C9": {
        "*1": {"activity_score": 1.0, "variants": [], "description": "Reference"},
        "*2": {"activity_score": 0.3, "variants": ["rs1799853"], "description": "Reduced function"},
        "*3": {"activity_score": 0.1, "variants": ["rs1057910"], "description": "Reduced function"},
        "*5": {"activity_score": 0.0, "variants": ["rs7900194"], "description": "Loss of function"},
        "*6": {"activity_score": 0.0, "variants": ["rs9332131"], "description": "Loss of function"},
        "*8": {"activity_score": 0.3, "variants": ["rs12167206"], "description": "Reduced function"},
    },
    "CYP3A5": {
        "*1": {"activity_score": 1.0, "variants": [], "description": "Expressed"},
        "*1A": {"activity_score": 1.0, "variants": ["rs2242480"], "description": "Expressed"},
        "*1B": {"activity_score": 1.0, "variants": ["rs41473528"], "description": "Expressed"},
        "*1F": {"activity_score": 1.0, "variants": ["rs7767451"], "description": "Expressed"},
        "*2": {"activity_score": 0.0, "variants": ["rs7767460"], "description": "Non-expressed"},
        "*3": {"activity_score": 0.0, "variants": ["rs59495192"], "description": "Non-expressed"},
        "*4": {"activity_score": 0.0, "variants": ["rs2242481"], "description": "Non-expressed"},
    },
    "SLCO1B1": {
        "*1": {"activity_score": 1.0, "variants": [], "description": "Reference"},
        "*5": {"activity_score": 0.0, "variants": ["rs4149056"], "description": "Loss of function"},
        "*11": {"activity_score": 0.3, "variants": ["rs2306283"], "description": "Reduced function"},
        "*12": {"activity_score": 0.3, "variants": ["rs4147466"], "description": "Reduced function"},
        "*15": {"activity_score": 0.0, "variants": ["rs119714864"], "description": "Loss of function"},
    },
    "DPYD": {
        "*1": {"activity_score": 1.0, "variants": [], "description": "Normal function"},
        "*2A": {"activity_score": 0.0, "variants": ["rs3918290"], "description": "Loss of function"},
        "*4": {"activity_score": 0.0, "variants": ["rs3918291"], "description": "Loss of function"},
        "*6": {"activity_score": 0.0, "variants": ["rs5591"], "description": "Loss of function"},
        "*7": {"activity_score": 0.3, "variants": ["rs67376791"], "description": "Reduced function"},
        "*13": {"activity_score": 0.0, "variants": ["rs56041004"], "description": "Loss of function"},
        "c.1679T>G": {"activity_score": 0.3, "variants": ["rs56041001"], "description": "Reduced function"},
    },
    "TPMT": {
        "*1": {"activity_score": 1.0, "variants": [], "description": "Normal function"},
        "*2": {"activity_score": 0.0, "variants": ["rs1800469"], "description": "Loss of function"},
        "*3A": {"activity_score": 0.0, "variants": ["rs1142345", "rs1142341"], "description": "Loss of function"},
        "*3B": {"activity_score": 0.0, "variants": ["rs1142341"], "description": "Loss of function"},
        "*3C": {"activity_score": 0.0, "variants": ["rs1142345"], "description": "Loss of function"},
        "*3D": {"activity_score": 0.0, "variants": ["rs1142341"], "description": "Loss of function"},
        "*3F": {"activity_score": 0.3, "variants": ["rs1800462"], "description": "Reduced function"},
        "*3J": {"activity_score": 0.0, "variants": ["rs1142341"], "description": "Loss of function"},
        "*3L": {"activity_score": 0.0, "variants": ["rs1142341"], "description": "Loss of function"},
    },
    "NUDT15": {
        "*1": {"activity_score": 1.0, "variants": [], "description": "Normal function"},
        "*2": {"activity_score": 0.0, "variants": ["rs116855232"], "description": "Loss of function"},
        "*3": {"activity_score": 0.0, "variants": ["rs6415532"], "description": "Loss of function"},
    },
    "UGT1A1": {
        "*1": {"activity_score": 1.0, "variants": [], "description": "Normal function"},
        "*6": {"activity_score": 0.0, "variants": ["rs8175347"], "description": "Loss of function"},
        "*28": {"activity_score": 0.3, "variants": ["rs8175345"], "description": "Reduced function"},
        "*29": {"activity_score": 1.3, "variants": ["rs8175345"], "description": "Increased function"},
        "*37": {"activity_score": 0.3, "variants": ["rs887829"], "description": "Reduced function"},
        "*60": {"activity_score": 0.0, "variants": ["rs10434141"], "description": "Loss of function"},
    },
    "VKORC1": {
        "*1": {"activity_score": 1.0, "variants": [], "description": "Normal function"},
        "*2": {"activity_score": 0.3, "variants": ["rs9923231"], "description": "Reduced function"},
        "*3": {"activity_score": 0.5, "variants": ["rs8050894"], "description": "Reduced function"},
    },
    "CYP2B6": {
        "*1": {"activity_score": 1.0, "variants": [], "description": "Reference"},
        "*4": {"activity_score": 0.3, "variants": ["rs3894876"], "description": "Reduced function"},
        "*6": {"activity_score": 0.3, "variants": ["rs2278555"], "description": "Reduced function"},
    },
    "CYP2A6": {
        "*1": {"activity_score": 1.0, "variants": [], "description": "Reference"},
        "*2": {"activity_score": 0.3, "variants": ["rs1041983"], "description": "Reduced function"},
        "*4": {"activity_score": 0.0, "variants": ["rs1799969"], "description": "Loss of function"},
        "*9": {"activity_score": 0.0, "variants": ["rs3758269"], "description": "Loss of function"},
        "*10": {"activity_score": 0.3, "variants": ["rs1801274"], "description": "Reduced function"},
        "*12": {"activity_score": 0.0, "variants": ["rs1799968"], "description": "Loss of function"},
        "*13": {"activity_score": 0.0, "variants": ["rs1799967"], "description": "Loss of function"},
        "*14": {"activity_score": 0.0, "variants": ["rs4362011"], "description": "Loss of function"},
        "*17": {"activity_score": 0.3, "variants": ["rs4011168"], "description": "Reduced function"},
        "*19": {"activity_score": 0.3, "variants": ["rs2069062"], "description": "Reduced function"},
        "*22": {"activity_score": 0.0, "variants": ["rs1799966"], "description": "Loss of function"},
    },
    "CYP2C8": {
        "*1": {"activity_score": 1.0, "variants": [], "description": "Reference"},
        "*3": {"activity_score": 0.3, "variants": ["rs11572052"], "description": "Reduced function"},
        "*4": {"activity_score": 0.3, "variants": ["rs11572033"], "description": "Reduced function"},
    },
    "NAT2": {
        "*1": {"activity_score": 1.0, "variants": [], "description": "Normal acetylator"},
        "*5": {"activity_score": 0.3, "variants": ["rs4299376"], "description": "Slow acetylator"},
        "*6": {"activity_score": 0.3, "variants": ["rs4299377"], "description": "Slow acetylator"},
        "*7": {"activity_score": 0.3, "variants": ["rs4299369"], "description": "Slow acetylator"},
        "*10": {"activity_score": 0.3, "variants": ["rs4299368"], "description": "Slow acetylator"},
        "*11": {"activity_score": 0.3, "variants": ["rs1801280"], "description": "Slow acetylator"},
        "*12": {"activity_score": 0.3, "variants": ["rs4299365"], "description": "Slow acetylator"},
        "*14": {"activity_score": 0.3, "variants": ["rs4299364"], "description": "Slow acetylator"},
        "*17": {"activity_score": 0.3, "variants": ["rs4299367"], "description": "Slow acetylator"},
    },
    "HLA-B": {
        "*57:01": {"activity_score": None, "variants": ["rs2395029"], "description": "Risk allele for abacavir hypersensitivity"},
    },
    "HLA-A": {
        "*31:01": {"activity_score": None, "variants": [], "description": "Risk allele for carbamazepine SJS/TEN"},
        "*32:01": {"activity_score": None, "variants": [], "description": "Risk allele for carbamazepine SJS/TEN"},
        "*33:03": {"activity_score": None, "variants": [], "description": "Risk allele for carbamazepine SJS/TEN"},
    },
    "G6PD": {
        "Mediterranean": {"activity_score": 0.0, "variants": ["rs28926138"], "description": "Deficient variant"},
        "A-": {"activity_score": 0.3, "variants": ["rs1050828"], "description": "Deficient variant"},
        "Wild": {"activity_score": 1.0, "variants": [], "description": "Normal activity"},
    },
    "RIPK2": {
        "Q588X": {"activity_score": None, "variants": ["rs3764880"], "description": "Loss of function, may affect azathioprine"},
    },
    "ABCB1": {
        "*1": {"activity_score": 1.0, "variants": [], "description": "Reference"},
        "*2": {"activity_score": 0.7, "variants": ["rs4148738"], "description": "Altered transport"},
        "*4": {"activity_score": 0.7, "variants": ["rs2032582", "rs4148738"], "description": "Altered transport"},
        "*6": {"activity_score": 0.7, "variants": ["rs1128503"], "description": "Altered transport"},
        "*22": {"activity_score": 0.3, "variants": ["rs2917656"], "description": "Altered transport"},
        "*31": {"activity_score": 0.3, "variants": ["rs2917655"], "description": "Altered transport"},
    },
}


def _load_alleles_data() -> dict:
    """Load allele definitions from bundled JSON or return built-in data."""
    data_path = Path(__file__).parent.parent.parent / "data" / "alleles" / "pharmvar_alleles.json"
    if data_path.exists():
        with open(data_path) as f:
            return json.load(f)
    return _PHARMVAR_ALLELES


class AlleleMapper:
    """Map variants to PharmVar allele symbols."""

    def __init__(self, alleles_data: Optional[dict] = None):
        self.alleles = alleles_data or _load_alleles_data()
        # Build rsID → (gene, allele) lookup
        self._rs_lookup: dict[str, list[tuple[str, str]]] = {}
        for gene, alleles in self.alleles.items():
            for allele_name, info in alleles.items():
                for rs in info.get("variants", []):
                    self._rs_lookup.setdefault(rs, []).append((gene, allele_name))

    def map_variant(self, variant: Variant) -> Optional[AlleleCall]:
        """Map a single variant to an allele call.

        Returns None if the variant doesn't match any known allele-defining variant.
        """
        if not variant.rs_id:
            return None

        matches = self._rs_lookup.get(variant.rs_id, [])
        if not matches:
            return None

        # Pick first matching gene-allele pair
        gene, allele_name = matches[0]
        allele_info = self.alleles.get(gene, {}).get(allele_name, {})

        return AlleleCall(
            gene=gene,
            allele_name=allele_name,
            rs_ids=[variant.rs_id],
            activity_score=allele_info.get("activity_score"),
            chrom_source="chr1",
        )

    def map_variants(self, variants: list[Variant]) -> dict[str, list[AlleleCall]]:
        """Map a list of variants grouped by gene.

        Returns {gene: [AlleleCall, ...]}.
        """
        results: dict[str, list[AlleleCall]] = {}
        for v in variants:
            call = self.map_variant(v)
            if call:
                results.setdefault(call.gene, []).append(call)
        return results

    def get_allele_activity(self, gene: str, allele_name: str) -> Optional[float]:
        """Get activity score for a specific gene+allele."""
        info = self.alleles.get(gene, {}).get(allele_name, {})
        return info.get("activity_score")

    def get_all_genes(self) -> list[str]:
        """Return all genes with allele definitions."""
        return sorted(self.alleles.keys())

    def get_alleles_for_gene(self, gene: str) -> dict[str, dict]:
        """Return all alleles for a gene."""
        return self.alleles.get(gene, {})
