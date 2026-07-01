"""PharmVar allele data loader."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

_BUNDLED_PATH = Path(__file__).parent.parent.parent / "data" / "alleles" / "pharmvar_alleles.json"


def load_pharmvar_data(path: Optional[str | Path] = None) -> dict:
    """Load PharmVar allele data from JSON file or bundled data.

    Parameters
    ----------
    path : optional path to JSON file with allele definitions

    Returns
    -------
    dict mapping gene -> allele -> {activity_score, variants, description}
    """
    if path:
        with open(path) as f:
            return json.load(f)

    if _BUNDLED_PATH.exists():
        with open(_BUNDLED_PATH) as f:
            return json.load(f)

    # Return built-in data from allele_mapper
    from pgxrx.core.allele_mapper import _PHARMVAR_ALLELES
    return _PHARMVAR_ALLELES


def save_pharmvar_data(data: dict, path: str | Path):
    """Save PharmVar allele data to JSON file."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    logger.info("Saved PharmVar data to %s", path)
