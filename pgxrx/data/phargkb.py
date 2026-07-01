"""PharmGKB annotation data loader."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

_BUNDLED_PATH = Path(__file__).parent.parent.parent / "data" / "drugs" / "phargkb_annotations.json"

# Default drug metadata from PharmGKB
_DEFAULT_ANNOTATIONS: dict[str, dict] = {
    "clopidogrel": {"class": "Antiplatelet", "brand_names": ["Plavix"]},
    "codeine": {"class": "Opioid analgesic", "brand_names": ["Cod肝ne"]},
    "tramadol": {"class": "Opioid analgesic", "brand_names": ["Ultram"]},
    "tamoxifen": {"class": "Selective estrogen receptor modulator", "brand_names": ["Nolvadex"]},
    "warfarin": {"class": "Anticoagulant", "brand_names": ["Coumadin"]},
    "simvastatin": {"class": "HMG-CoA reductase inhibitor", "brand_names": ["Zocor"]},
    "carbamazepine": {"class": "Anticonvulsant", "brand_names": ["Tegretol", "Carbatrol"]},
    "atomoxetine": {"class": "Norepinephrine reuptake inhibitor", "brand_names": ["Strattera"]},
    "sertraline": {"class": "SSRI", "brand_names": ["Zoloft"]},
    "oxycodone": {"class": "Opioid analgesic", "brand_names": ["OxyContin", "Roxicodone"]},
    "irinoxotecan": {"class": "Topoisomerase I inhibitor", "brand_names": ["Camptosar"]},
    "tacrolimus": {"class": "Calcineurin inhibitor", "brand_names": ["Prograf", "Astagraf"]},
    "efavirenz": {"class": "NNRTI", "brand_names": ["Sustiva"]},
    "metoprolol": {"class": "Beta-blocker", "brand_names": ["Lopressor", "Toprol-XL"]},
    "desipramine": {"class": "Tricyclic antidepressant", "brand_names": ["Norpramin"]},
    "losartan": {"class": "ARB", "brand_names": ["Cozaar"]},
    "phenytoin": {"class": "Anticonvulsant", "brand_names": ["Dilantin"]},
    "celecoxib": {"class": "COX-2 inhibitor", "brand_names": ["Celebrex"]},
    "abacavir": {"class": "NRTI", "brand_names": ["Ziagen"]},
    "allopurinol": {"class": "Xanthine oxidase inhibitor", "brand_names": ["Zyloprim"]},
    "azathioprine": {"class": "Immunosuppressant", "brand_names": ["Imuran"]},
    "mercaptopurine": {"class": "Antimetabolite", "brand_names": ["Purinethol"]},
    "varenicline": {"class": "Nicotinic receptor partial agonist", "brand_names": ["Chantix"]},
    "isoniazid": {"class": "Antimycobacterial", "brand_names": ["Nydrazid"]},
    "diazepam": {"class": "Benzodiazepine", "brand_names": ["Valium"]},
    "omeprazole": {"class": "PPI", "brand_names": ["Prilosec"]},
    "pantoprazole": {"class": "PPI", "brand_names": ["Protonix"]},
    "voriconazole": {"class": "Triazole antifungal", "brand_names": ["Vfend"]},
}


def load_phargkb_data(path: Optional[str | Path] = None) -> dict:
    """Load PharmGKB drug annotations."""
    if path:
        with open(path) as f:
            return json.load(f)
    if _BUNDLED_PATH.exists():
        with open(_BUNDLED_PATH) as f:
            return json.load(f)
    return _DEFAULT_ANNOTATIONS
