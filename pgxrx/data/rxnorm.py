"""RxNorm drug name normalization."""

from __future__ import annotations

from typing import Optional

# Common drug name aliases → canonical name
_DRUG_ALIASES: dict[str, str] = {
    "plavix": "clopidogrel",
    "advice plavix": "clopidogrel",
    "tylenol with codeine": "codeine",
    "cod liver": "codeine",
    "nolvadex": "tamoxifen",
    "coumadin": "warfarin",
    "zocor": "simvastatin",
    "tegretol": "carbamazepine",
    "strattera": "atomoxetine",
    "zoloft": "sertraline",
    "oxycontin": "oxycodone",
    "ultram": "tramadol",
    "prograf": "tacrolimus",
    "sustiva": "efavirenz",
    "lopressor": "metoprolol",
    "toprol": "metoprolol",
    "norpramin": "desipramine",
    "cozaar": "losartan",
    "dilantin": "phenytoin",
    "celebrex": "celecoxib",
    "ziagen": "abacavir",
    "zyloprim": "allopurinol",
    "imuran": "azathioprine",
    "purinethol": "mercaptopurine",
    "chantix": "varenicline",
    "valium": "diazepam",
    "prilosec": "omeprazole",
    "protonix": "pantoprazole",
    "vfend": "voriconazole",
    "5-fu": "5-fluorouracil",
    "fluorouracil": "5-fluorouracil",
    "xeloda": "capecitabine",
}


def normalize_drug_name(name: str) -> str:
    """Normalize drug name to canonical form."""
    lower = name.strip().lower()
    return _DRUG_ALIASES.get(lower, lower)


def resolve_drug(name: str) -> Optional[str]:
    """Try to resolve a drug name to its canonical form.

    Returns the canonical name or None if unrecognized.
    """
    lower = name.strip().lower()
    return _DRUG_ALIASES.get(lower, name.lower())
