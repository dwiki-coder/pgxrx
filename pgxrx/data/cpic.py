"""CPIC guideline data loader."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

_BUNDLED_PATH = Path(__file__).parent.parent.parent / "data" / "guidelines" / "cpic_guidelines.json"


def load_cpic_data(path: Optional[str | Path] = None) -> dict:
    """Load CPIC guideline data.

    Returns
    -------
    dict mapping (drug, gene) -> {phenotype: (recommendation, evidence)}
    """
    if path:
        with open(path) as f:
            raw = json.load(f)
        return _deserialize_guidelines(raw)

    if _BUNDLED_PATH.exists():
        with open(_BUNDLED_PATH) as f:
            raw = json.load(f)
        return _deserialize_guidelines(raw)

    # Return built-in data from dosing module
    from pgxrx.core.dosing import _DRUG_GENE_GUIDELINES
    return _DRUG_GENE_GUIDELINES


def save_cpic_data(data: dict, path: str | Path):
    """Save CPIC guideline data to JSON."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    serialized = _serialize_guidelines(data)
    with open(path, "w") as f:
        json.dump(serialized, f, indent=2)
    logger.info("Saved CPIC data to %s", path)


def _serialize_guidelines(data: dict) -> dict:
    """Serialize tuple keys to string format for JSON."""
    result = {}
    for (drug, gene), phenos in data.items():
        key = f"{drug}__{gene}"
        result[key] = phenos
    return result


def _deserialize_guidelines(data: dict) -> dict:
    """Deserialize string keys back to tuple format."""
    result = {}
    for key, phenos in data.items():
        parts = key.split("__")
        if len(parts) == 2:
            result[(parts[0], parts[1])] = phenos
    return result
