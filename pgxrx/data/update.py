"""Knowledge base update/downloader."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)


def update_knowledge_base(data_dir: str | Path) -> dict:
    """Check for and download updated knowledge base files.

    In production this would fetch from PharmVar, CPIC, PharmGKB.
    For now, validates local bundled data and reports version.

    Parameters
    ----------
    data_dir : path to data directory

    Returns
    -------
    dict with update status
    """
    data_dir = Path(data_dir)
    status = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "alleles": {"status": "bundled", "version": "2024.1", "path": str(data_dir / "alleles" / "pharmvar_alleles.json")},
        "guidelines": {"status": "bundled", "version": "CPIC 2024", "path": str(data_dir / "guidelines" / "cpic_guidelines.json")},
        "annotations": {"status": "bundled", "version": "2024.1", "path": str(data_dir / "drugs" / "phargkb_annotations.json")},
    }

    # Check local files exist
    alleles_file = data_dir / "alleles" / "pharmvar_alleles.json"
    guidelines_file = data_dir / "guidelines" / "cpic_guidelines.json"

    if alleles_file.exists():
        status["alleles"]["status"] = "available"
        status["alleles"]["size"] = alleles_file.stat().st_size
    else:
        status["alleles"]["status"] = "missing"

    if guidelines_file.exists():
        status["guidelines"]["status"] = "available"
        status["guidelines"]["size"] = guidelines_file.stat().st_size
    else:
        status["guidelines"]["status"] = "missing"

    return status
