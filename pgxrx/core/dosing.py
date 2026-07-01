"""CPIC dosing recommendation engine.

Maps (drug, gene, phenotype) → dosing recommendation text
based on published CPIC guidelines.
"""

from __future__ import annotations

import logging
from typing import Optional

from pgxrx.core.variant import DosingRecommendation, PhenotypeResult

logger = logging.getLogger(__name__)

# ── CPIC drug-gene guideline tables ────────────────────────────────
# Format: { (drug, gene): { phenotype: (recommendation, evidence_level) } }

_DRUG_GENE_GUIDELINES: dict[tuple[str, str], dict[str, tuple[str, str]]] = {
    # ── CYP2C19 ───────────────────────────────────────────────
    ("clopidogrel", "CYP2C19"): {
        "Poor Metabolizer": (
            "Consider use of an alternative antiplatelet agent (prasugrel or ticagrelor) "
            "that does not depend on CYP2C19 for activation.",
            "A1",
        ),
        "Intermediate Metabolizer": (
            "Consider use of an alternative antiplatelet agent (prasugrel or ticagrelor) "
            "that does not depend on CYP2C19 for activation.",
            "A1",
        ),
        "Normal Metabolizer": (
            "No change in dosing. Standard clopidogrel dosing is appropriate.",
            "A1",
        ),
        "Ultrarapid Metabolizer": (
            "No change in dosing. Standard clopidogrel dosing is appropriate.",
            "A1",
        ),
    },
    ("dexlansoprazole", "CYP2C19"): {
        "Poor Metabolizer": (
            "Consider dose reduction to 30 mg daily.",
            "B",
        ),
        "Intermediate Metabolizer": (
            "Consider dose reduction to 30 mg daily.",
            "B",
        ),
        "Normal Metabolizer": (
            "No change in dosing. Standard dosing is appropriate.",
            "B",
        ),
        "Ultrarapid Metabolizer": (
            "No change in dosing.",
            "B",
        ),
    },
    ("omeprazole", "CYP2C19"): {
        "Poor Metabolizer": (
            "Consider dose reduction or alternative PPI.",
            "C",
        ),
        "Intermediate Metabolizer": (
            "Consider dose reduction or alternative PPI.",
            "C",
        ),
        "Normal Metabolizer": (
            "No change in dosing.",
            "C",
        ),
        "Ultrarapid Metabolizer": (
            "No change in dosing.",
            "C",
        ),
    },
    ("pantoprazole", "CYP2C19"): {
        "Poor Metabolizer": ("Consider dose reduction.", "C"),
        "Intermediate Metabolizer": ("Consider dose reduction.", "C"),
        "Normal Metabolizer": ("No change in dosing.", "C"),
        "Ultrarapid Metabolizer": ("No change in dosing.", "C"),
    },
    ("sertraline", "CYP2C19"): {
        "Poor Metabolizer": (
            "Consider alternative antidepressant with less CYP2C19 metabolism.",
            "A2",
        ),
        "Intermediate Metabolizer": (
            "Consider dose reduction or alternative antidepressant.",
            "A2",
        ),
        "Normal Metabolizer": ("No change in dosing.", "A2"),
        "Ultrarapid Metabolizer": ("No change in dosing.", "A2"),
    },
    ("citalopram", "CYP2C19"): {
        "Poor Metabolizer": (
            "Consider dose reduction or alternative antidepressant.",
            "A2",
        ),
        "Intermediate Metabolizer": (
            "Consider dose reduction or alternative antidepressant.",
            "A2",
        ),
        "Normal Metabolizer": ("No change in dosing.", "A2"),
        "Ultrarapid Metabolizer": ("No change in dosing.", "A2"),
    },
    ("escitalopram", "CYP2C19"): {
        "Poor Metabolizer": ("Consider dose reduction.", "A2"),
        "Intermediate Metabolizer": ("Consider dose reduction.", "A2"),
        "Normal Metabolizer": ("No change in dosing.", "A2"),
        "Ultrarapid Metabolizer": ("No change in dosing.", "A2"),
    },
    ("voriconazole", "CYP2C19"): {
        "Poor Metabolizer": (
            "Consider dose reduction and monitoring for toxicity.",
            "A2",
        ),
        "Intermediate Metabolizer": (
            "Consider dose reduction and monitoring for toxicity.",
            "A2",
        ),
        "Normal Metabolizer": ("No change in dosing.", "A2"),
        "Ultrarapid Metabolizer": (
            "Consider alternative antifungal agent.",
            "A2",
        ),
    },
    ("aprepitant", "CYP2C19"): {
        "Poor Metabolizer": ("Consider dose reduction.", "B"),
        "Intermediate Metabolizer": ("Consider dose reduction.", "B"),
        "Normal Metabolizer": ("No change in dosing.", "B"),
        "Ultrarapid Metabolizer": ("No change in dosing.", "B"),
    },
    ("duloxetine", "CYP2C19"): {
        "Poor Metabolizer": ("Consider dose reduction or alternative.", "C"),
        "Intermediate Metabolizer": ("Consider dose reduction.", "C"),
        "Normal Metabolizer": ("No change in dosing.", "C"),
        "Ultrarapid Metabolizer": ("No change in dosing.", "C"),
    },
    ("mirtazapine", "CYP2C19"): {
        "Poor Metabolizer": ("Consider dose reduction.", "C"),
        "Intermediate Metabolizer": ("Consider dose reduction.", "C"),
        "Normal Metabolizer": ("No change in dosing.", "C"),
        "Ultrarapid Metabolizer": ("No change in dosing.", "C"),
    },
    ("riluzole", "CYP2C19"): {
        "Poor Metabolizer": ("Consider dose reduction.", "B"),
        "Intermediate Metabolizer": ("Consider dose reduction.", "B"),
        "Normal Metabolizer": ("No change in dosing.", "B"),
        "Ultrarapid Metabolizer": ("No change in dosing.", "B"),
    },
    ("diazepam", "CYP2C19"): {
        "Poor Metabolizer": ("Consider dose reduction.", "B"),
        "Intermediate Metabolizer": ("Consider dose reduction.", "B"),
        "Normal Metabolizer": ("No change in dosing.", "B"),
        "Ultrarapid Metabolizer": ("No change in dosing.", "B"),
    },
    ("losartan", "CYP2C19"): {
        "Poor Metabolizer": (
            "Consider alternative antihypertensive agent.",
            "C",
        ),
        "Intermediate Metabolizer": (
            "Consider alternative antihypertensive agent.",
            "C",
        ),
        "Normal Metabolizer": ("No change in dosing.", "C"),
        "Ultrarapid Metabolizer": ("No change in dosing.", "C"),
    },

    # ── CYP2D6 ────────────────────────────────────────────────
    ("codeine", "CYP2D6"): {
        "Poor Metabolizer": (
            "Avoid codeine. Use alternative analgesic (e.g., ibuprofen, acetaminophen). "
            "Codeine requires CYP2D6 activation; PMs derive no analgesic benefit.",
            "A1",
        ),
        "Intermediate Metabolizer": (
            "Consider alternative analgesic. If codeine is used, reduce dose and monitor closely.",
            "A1",
        ),
        "Normal Metabolizer": (
            "No change in dosing. Standard codeine dosing is appropriate.",
            "A1",
        ),
        "Ultrarapid Metabolizer": (
            "Avoid codeine. Consider alternative analgesic due to risk of "
            "toxicity from excessive morphine formation.",
            "A1",
        ),
    },
    ("tramadol", "CYP2D6"): {
        "Poor Metabolizer": (
            "Consider alternative analgesic. Tramadol efficacy is reduced in PMs.",
            "A1",
        ),
        "Intermediate Metabolizer": (
            "Consider alternative analgesic or reduced dose with close monitoring.",
            "A1",
        ),
        "Normal Metabolizer": (
            "No change in dosing. Standard tramadol dosing is appropriate.",
            "A1",
        ),
        "Ultrarapid Metabolizer": (
            "Consider alternative analgesic. Risk of toxicity from excessive O-desmethyltramadol.",
            "A1",
        ),
    },
    ("tamoxifen", "CYP2D6"): {
        "Poor Metabolizer": (
            "Consider alternative breast cancer therapy (e.g., anastrozole, letrozole). "
            "Tamoxifen requires CYP2D6 activation to endoxifen.",
            "A1",
        ),
        "Intermediate Metabolizer": (
            "Consider alternative breast cancer therapy. If tamoxifen used, monitor closely.",
            "A1",
        ),
        "Normal Metabolizer": (
            "No change in dosing. Standard tamoxifen dosing is appropriate.",
            "A1",
        ),
        "Ultrarapid Metabolizer": (
            "No change in dosing. Standard tamoxifen dosing is appropriate.",
            "A1",
        ),
    },
    ("oxycodone", "CYP2D6"): {
        "Poor Metabolizer": (
            "Consider alternative analgesic. Reduced efficacy expected.",
            "A2",
        ),
        "Intermediate Metabolizer": (
            "Consider alternative analgesic or reduced dose with close monitoring.",
            "A2",
        ),
        "Normal Metabolizer": (
            "No change in dosing. Standard oxycodone dosing is appropriate.",
            "A2",
        ),
        "Ultrarapid Metabolizer": (
            "Consider alternative analgesic. Risk of excessive effect from active metabolites.",
            "A2",
        ),
    },
    ("atomoxetine", "CYP2D6"): {
        "Poor Metabolizer": (
            "Consider dose reduction to 0.3 mg/kg (max 18 mg daily).",
            "A1",
        ),
        "Intermediate Metabolizer": (
            "Consider dose reduction. Monitor for adverse effects.",
            "A2",
        ),
        "Normal Metabolizer": (
            "No change in dosing. Standard dosing is appropriate.",
            "A1",
        ),
        "Ultrarapid Metabolizer": (
            "No change in dosing. Standard dosing is appropriate.",
            "A1",
        ),
    },
    ("sertraline", "CYP2D6"): {
        "Poor Metabolizer": (
            "Consider dose reduction or alternative antidepressant.",
            "A2",
        ),
        "Intermediate Metabolizer": (
            "Consider dose reduction or alternative antidepressant.",
            "A2",
        ),
        "Normal Metabolizer": ("No change in dosing.", "A2"),
        "Ultrarapid Metabolizer": ("No change in dosing.", "A2"),
    },
    ("desipramine", "CYP2D6"): {
        "Poor Metabolizer": (
            "Consider dose reduction to 25% of standard dose.",
            "A1",
        ),
        "Intermediate Metabolizer": (
            "Consider dose reduction to 50% of standard dose.",
            "A1",
        ),
        "Normal Metabolizer": ("No change in dosing.", "A1"),
        "Ultrarapid Metabolizer": ("No change in dosing.", "A1"),
    },
    ("metoprolol", "CYP2D6"): {
        "Poor Metabolizer": ("Consider dose reduction.", "B"),
        "Intermediate Metabolizer": ("Consider dose reduction.", "B"),
        "Normal Metabolizer": ("No change in dosing.", "B"),
        "Ultrarapid Metabolizer": ("No change in dosing.", "B"),
    },
    ("carbamazepine", "HLA-A"): {
        "Positive": (
            "Avoid carbamazepine. Use alternative anticonvulsant due to high risk "
            "of Stevens-Johnson syndrome / toxic epidermal necrolysis.",
            "A1",
        ),
        "Negative": (
            "No change in dosing based on HLA genotype.",
            "A1",
        ),
    },
    ("carbamazepine", "HLA-B"): {
        "Positive": (
            "Avoid carbamazepine. Risk of severe cutaneous adverse reactions.",
            "A1",
        ),
        "Negative": (
            "No change in dosing based on HLA-B genotype.",
            "A1",
        ),
    },
    ("abacavir", "HLA-B"): {
        "Positive": (
            "Avoid abacavir. HLA-B*57:01 positive individuals are at high risk "
            "for abacavir hypersensitivity reaction.",
            "A1",
        ),
        "Negative": (
            "No change in dosing based on HLA-B*57:01 genotype.",
            "A1",
        ),
    },
    ("allopurinol", "HLA-B"): {
        "Positive": (
            "Avoid allopurinol. Use alternative gout therapy due to risk of SJS/TEN.",
            "A1",
        ),
        "Negative": (
            "No change in dosing based on HLA-B genotype.",
            "A1",
        ),
    },
    ("carbamazepine", "HLA-A"): {
        "Positive": (
            "Avoid carbamazepine due to risk of SJS/TEN.",
            "A1",
        ),
        "Negative": (
            "No change in dosing based on HLA-A genotype.",
            "A1",
        ),
    },

    # ── CYP2C9 / VKORC1 / warfarin ─────────────────────────────
    ("warfarin", "CYP2C9"): {
        "Poor Metabolizer": (
            "Consider reduced initial dose (e.g., 2-3 mg/day) and frequent INR monitoring.",
            "A1",
        ),
        "Intermediate Metabolizer": (
            "Consider reduced initial dose (e.g., 5 mg/day) and frequent INR monitoring.",
            "A1",
        ),
        "Normal Metabolizer": (
            "No genotype-based dose adjustment. Use standard dosing and INR monitoring.",
            "A1",
        ),
    },
    ("warfarin", "VKORC1"): {
        "Low expresser": (
            "Consider reduced initial dose (e.g., 2-5 mg/day).",
            "A1",
        ),
        "Intermediate expresser": (
            "Consider moderate dose reduction.",
            "A1",
        ),
        "Normal expresser": (
            "No genotype-based dose adjustment.",
            "A1",
        ),
    },
    ("phenytoin", "CYP2C9"): {
        "Poor Metabolizer": (
            "Consider reduced dose and frequent level monitoring.",
            "A2",
        ),
        "Intermediate Metabolizer": (
            "Consider reduced dose and frequent level monitoring.",
            "A2",
        ),
        "Normal Metabolizer": (
            "No change in dosing.",
            "A2",
        ),
    },
    ("losartan", "CYP2C9"): {
        "Poor Metabolizer": (
            "Consider alternative antihypertensive.",
            "C",
        ),
        "Intermediate Metabolizer": (
            "Consider alternative antihypertensive or monitor BP closely.",
            "C",
        ),
        "Normal Metabolizer": (
            "No change in dosing.",
            "C",
        ),
    },
    ("celecoxib", "CYP2C9"): {
        "Poor Metabolizer": (
            "Consider dose reduction or alternative NSAID.",
            "C",
        ),
        "Intermediate Metabolizer": (
            "Consider dose reduction or alternative NSAID.",
            "C",
        ),
        "Normal Metabolizer": (
            "No change in dosing.",
            "C",
        ),
    },
    ("diclofenac", "CYP2C9"): {
        "Poor Metabolizer": ("Consider alternative NSAID.", "C"),
        "Intermediate Metabolizer": ("Consider alternative NSAID.", "C"),
        "Normal Metabolizer": ("No change in dosing.", "C"),
    },
    ("tolbutamide", "CYP2C9"): {
        "Poor Metabolizer": (
            "Consider alternative sulfonylurea (e.g., glipizide).",
            "B",
        ),
        "Intermediate Metabolizer": (
            "Consider dose reduction.",
            "B",
        ),
        "Normal Metabolizer": (
            "No change in dosing.",
            "B",
        ),
    },

    # ── SLCO1B1 / simvastatin ──────────────────────────────────
    ("simvastatin", "SLCO1B1"): {
        "Poor Metabolizer": (
            "Avoid simvastatin doses > 40 mg. Consider alternative statin (e.g., pravastatin, "
            "fluvastatin) due to increased risk of myopathy.",
            "A1",
        ),
        "Intermediate Metabolizer": (
            "Consider dose limit of 40 mg daily. Monitor for myopathy.",
            "A1",
        ),
        "Normal Metabolizer": (
            "No change in dosing. Standard simvastatin dosing is appropriate.",
            "A1",
        ),
    },

    # ── DPYD / 5-FU / irinotecan ────────────────────────────────
    ("irinotecan", "DPYD"): {
        "Poor Metabolizer": (
            "Avoid irinotecan or consider 50% dose reduction with close monitoring "
            "for severe myelosuppression.",
            "A2",
        ),
        "Intermediate Metabolizer": (
            "Consider 25% dose reduction. Monitor for myelosuppression.",
            "A2",
        ),
        "Normal Metabolizer": (
            "No genotype-based dose adjustment.",
            "A2",
        ),
    },
    ("5-fluorouracil", "DPYD"): {
        "Poor Metabolizer": (
            "Avoid 5-FU or consider 50% dose reduction due to risk of severe toxicity.",
            "A1",
        ),
        "Intermediate Metabolizer": (
            "Consider 25% dose reduction with close monitoring.",
            "A1",
        ),
        "Normal Metabolizer": (
            "No genotype-based dose adjustment.",
            "A1",
        ),
    },
    ("capecitabine", "DPYD"): {
        "Poor Metabolizer": (
            "Avoid capecitabine or consider 50% dose reduction.",
            "A2",
        ),
        "Intermediate Metabolizer": (
            "Consider 25% dose reduction.",
            "A2",
        ),
        "Normal Metabolizer": (
            "No genotype-based dose adjustment.",
            "A2",
        ),
    },

    # ── TPMT / thiopurines ──────────────────────────────────────
    ("mercaptopurine", "TPMT"): {
        "Poor Metabolizer": (
            "Consider alternative agent (e.g., azathioprine not recommended) or "
            "reduce dose to 10% of standard with frequent CBC monitoring.",
            "A1",
        ),
        "Intermediate Metabolizer": (
            "Consider dose reduction to 30-70% of standard dose with frequent CBC monitoring.",
            "A1",
        ),
        "Normal Metabolizer": (
            "No change in dosing. Standard dosing is appropriate.",
            "A1",
        ),
    },
    ("azathioprine", "TPMT"): {
        "Poor Metabolizer": (
            "Consider alternative agent or reduce dose to 10% of standard "
            "with frequent CBC monitoring.",
            "A1",
        ),
        "Intermediate Metabolizer": (
            "Consider dose reduction to 30-70% of standard dose with frequent CBC monitoring.",
            "A1",
        ),
        "Normal Metabolizer": (
            "No change in dosing. Standard dosing is appropriate.",
            "A1",
        ),
    },
    ("6-thioguanine", "TPMT"): {
        "Poor Metabolizer": (
            "Consider dose reduction to 10% of standard with frequent CBC monitoring.",
            "A2",
        ),
        "Intermediate Metabolizer": (
            "Consider dose reduction with frequent CBC monitoring.",
            "A2",
        ),
        "Normal Metabolizer": (
            "No change in dosing.",
            "A2",
        ),
    },
    ("6-mercaptopurine", "NUDT15"): {
        "Poor Metabolizer": (
            "Consider alternative agent or reduce dose to 10% of standard.",
            "A1",
        ),
        "Intermediate Metabolizer": (
            "Consider dose reduction with close monitoring.",
            "A1",
        ),
        "Normal Metabolizer": (
            "No change in dosing.",
            "A1",
        ),
    },
    ("azathioprine", "NUDT15"): {
        "Poor Metabolizer": (
            "Consider alternative agent or reduce dose to 10% of standard.",
            "A1",
        ),
        "Intermediate Metabolizer": (
            "Consider dose reduction with close monitoring.",
            "A1",
        ),
        "Normal Metabolizer": (
            "No change in dosing.",
            "A1",
        ),
    },

    # ── UGT1A1 / irinotecan ─────────────────────────────────────
    ("irinotecan", "UGT1A1"): {
        "Poor Metabolizer": (
            "Consider dose reduction of irinotecan to 70% of standard dose.",
            "A1",
        ),
        "Intermediate Metabolizer": (
            "Monitor for neutropenia. Consider dose reduction if toxicity occurs.",
            "A2",
        ),
        "Normal Metabolizer": (
            "No genotype-based dose adjustment.",
            "A1",
        ),
    },
    ("atazanavir", "UGT1A1"): {
        "Poor Metabolizer": (
            "Monitor for jaundice. Consider dose reduction if hyperbilirubinemia occurs.",
            "C",
        ),
        "Intermediate Metabolizer": (
            "Monitor for jaundice.",
            "C",
        ),
        "Normal Metabolizer": (
            "No change in dosing.",
            "C",
        ),
    },
    ("irbesartan", "UGT1A1"): {
        "Poor Metabolizer": (
            "No clinically significant change expected.",
            "C",
        ),
        "Intermediate Metabolizer": (
            "No clinically significant change expected.",
            "C",
        ),
        "Normal Metabolizer": (
            "No change in dosing.",
            "C",
        ),
    },

    # ── CYP3A5 / tacrolimus ─────────────────────────────────────
    ("tacrolimus", "CYP3A5"): {
        "Non-expresser": (
            "Standard dosing is appropriate. Monitor trough levels.",
            "A2",
        ),
        "Reduced expresser": (
            "Consider increased dose. Monitor trough levels closely.",
            "A2",
        ),
        "Normal expresser": (
            "Consider increased dose (up to 2-3x standard). Monitor trough levels closely.",
            "A2",
        ),
    },
    ("cyclosporine", "CYP3A5"): {
        "Non-expresser": (
            "Standard dosing is appropriate.",
            "B",
        ),
        "Reduced expresser": (
            "Consider increased dose.",
            "B",
        ),
        "Normal expresser": (
            "Consider increased dose.",
            "B",
        ),
    },

    # ── CYP2B6 / efavirenz ──────────────────────────────────────
    ("efavirenz", "CYP2B6"): {
        "Poor Metabolizer": (
            "Consider dose reduction or alternative antiretroviral due to toxicity risk.",
            "B",
        ),
        "Intermediate Metabolizer": (
            "Monitor for CNS adverse effects.",
            "B",
        ),
        "Normal Metabolizer": (
            "No change in dosing.",
            "B",
        ),
    },

    # ── CYP2A6 / varenicline ────────────────────────────────────
    ("varenicline", "CYP2A6"): {
        "Poor Metabolizer": (
            "Consider dose reduction to 0.25 mg daily.",
            "A2",
        ),
        "Intermediate Metabolizer": (
            "Consider dose reduction. Monitor for adverse effects.",
            "A2",
        ),
        "Normal Metabolizer": (
            "No change in dosing.",
            "A2",
        ),
    },

    # ── CYP2C8 / repaglinide ────────────────────────────────────
    ("repaglinide", "CYP2C8"): {
        "Poor Metabolizer": (
            "Consider dose reduction or alternative antidiabetic.",
            "B",
        ),
        "Intermediate Metabolizer": (
            "Consider dose reduction.",
            "B",
        ),
        "Normal Metabolizer": (
            "No change in dosing.",
            "B",
        ),
    },
    ("paclitaxel", "CYP2C8"): {
        "Poor Metabolizer": (
            "Consider dose reduction or alternative chemotherapy.",
            "C",
        ),
        "Intermediate Metabolizer": (
            "Monitor closely for toxicity.",
            "C",
        ),
        "Normal Metabolizer": (
            "No change in dosing.",
            "C",
        ),
    },

    # ── NAT2 / procainamide ──────────────────────────────────────
    ("procainamide", "NAT2"): {
        "Poor acetylator": (
            "Consider dose reduction. Monitor for toxicity.",
            "B",
        ),
        "Intermediate acetylator": (
            "Monitor for adverse effects.",
            "B",
        ),
        "Rapid acetylator": (
            "No change in dosing.",
            "B",
        ),
    },
    ("isoniazid", "NAT2"): {
        "Poor acetylator": (
            "Consider dose reduction or extended dosing interval due to toxicity risk.",
            "B",
        ),
        "Intermediate acetylator": (
            "Monitor for peripheral neuropathy.",
            "B",
        ),
        "Rapid acetylator": (
            "No change in dosing.",
            "B",
        ),
    },
    ("sulfasalazine", "NAT2"): {
        "Poor acetylator": (
            "Monitor for toxicity. Consider dose reduction.",
            "C",
        ),
        "Intermediate acetylator": (
            "Monitor for adverse effects.",
            "C",
        ),
        "Rapid acetylator": (
            "No change in dosing.",
            "C",
        ),
    },
    ("hydralazine", "NAT2"): {
        "Poor acetylator": (
            "Monitor for drug-induced lupus. Consider alternative antihypertensive.",
            "C",
        ),
        "Intermediate acetylator": (
            "Monitor for adverse effects.",
            "C",
        ),
        "Rapid acetylator": (
            "No change in dosing.",
            "C",
        ),
    },

    # ── G6PD / dapsone / primaquine ─────────────────────────────
    ("dapsone", "G6PD"): {
        "Normal": (
            "No change in dosing.",
            "B",
        ),
    },
    ("primaquine", "G6PD"): {
        "Normal": (
            "No change in dosing.",
            "B",
        ),
    },
}

# Build gene→drug and drug→gene indexes for quick lookup
_GENE_DRUGS: dict[str, list[str]] = {}
_DRUG_GENES: dict[str, list[str]] = {}
for (drug, gene) in _DRUG_GENE_GUIDELINES:
    _GENE_DRUGS.setdefault(gene, []).append(drug)
    _DRUG_GENES.setdefault(drug, []).append(gene)


def get_drug_genes(drug: str) -> list[str]:
    """Return genes associated with a drug."""
    return _DRUG_GENES.get(drug.lower(), [])


def get_gene_drugs(gene: str) -> list[str]:
    """Return drugs associated with a gene."""
    return _GENE_DRUGS.get(gene, [])


def get_dosing_recommendation(
    drug: str,
    gene: str,
    phenotype: str,
) -> Optional[DosingRecommendation]:
    """Look up CPIC dosing recommendation for a drug-gene-phenotype triple.

    Parameters
    ----------
    drug : drug name (case-insensitive)
    gene : gene symbol
    phenotype : phenotype string (e.g. "Poor Metabolizer")

    Returns
    -------
    DosingRecommendation or None
    """
    key = (drug.lower(), gene)
    table = _DRUG_GENE_GUIDELINES.get(key)
    if table is None:
        logger.warning("No guideline found for drug=%s, gene=%s", drug, gene)
        return None

    rec_text, evidence = table.get(phenotype, (
        "No specific recommendation found for this phenotype.",
        "C",
    ))

    return DosingRecommendation(
        gene=gene,
        drug=drug,
        phenotype=phenotype,
        recommendation=rec_text,
        evidence_level=evidence,
    )


def get_all_guidelines() -> dict[tuple[str, str], dict]:
    """Return all guideline tables."""
    return {k: dict(v) for k, v in _DRUG_GENE_GUIDELINES.items()}
