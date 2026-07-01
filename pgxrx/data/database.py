"""SQLite database manager for bundled knowledge base."""

from __future__ import annotations

import json
import logging
import sqlite3
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

_DEFAULT_DB_PATH = Path(__file__).parent.parent.parent / "data" / "pgxrx.db"


class PGxDatabase:
    """SQLite-backed knowledge base for PGx data."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or _DEFAULT_DB_PATH
        self._conn: Optional[sqlite3.Connection] = None

    def connect(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(str(self.db_path))
            self._conn.row_factory = sqlite3.Row
            self._create_tables()
        return self._conn

    def _create_tables(self):
        conn = self._conn
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS alleles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                gene TEXT NOT NULL,
                allele_name TEXT NOT NULL,
                rs_id TEXT,
                chrom TEXT,
                pos INTEGER,
                ref TEXT,
                alt TEXT,
                activity_score REAL,
                description TEXT
            );
            CREATE TABLE IF NOT EXISTS guidelines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                drug_name TEXT NOT NULL,
                gene TEXT NOT NULL,
                phenotype TEXT NOT NULL,
                activity_score_min REAL,
                activity_score_max REAL,
                dosing_text TEXT,
                evidence_level TEXT,
                guideline_version TEXT
            );
            CREATE TABLE IF NOT EXISTS drugs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                drug_name TEXT NOT NULL,
                generic_name TEXT,
                brand_names TEXT,
                drug_class TEXT
            );
            CREATE INDEX IF NOT EXISTS idx_alleles_gene ON alleles(gene);
            CREATE INDEX IF NOT EXISTS idx_alleles_rs ON alleles(rs_id);
            CREATE INDEX IF NOT EXISTS idx_guidelines_drug_gene ON guidelines(drug_name, gene);
        """)
        conn.commit()

    def close(self):
        if self._conn:
            self._conn.close()
            self._conn = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, *args):
        self.close()

    def load_alleles_from_json(self, data: dict):
        """Load allele definitions from PharmVar-style JSON dict."""
        conn = self.connect()
        for gene, alleles in data.items():
            for allele_name, info in alleles.items():
                for rs in info.get("variants", []):
                    conn.execute(
                        "INSERT OR IGNORE INTO alleles (gene, allele_name, rs_id, activity_score, description) "
                        "VALUES (?, ?, ?, ?, ?)",
                        (gene, allele_name, rs, info.get("activity_score"), info.get("description", "")),
                    )
        conn.commit()
        logger.info("Loaded %d alleles from JSON data", sum(len(v) for v in data.values()))

    def get_alleles_for_gene(self, gene: str) -> list[dict]:
        conn = self.connect()
        rows = conn.execute("SELECT * FROM alleles WHERE gene = ?", (gene,)).fetchall()
        return [dict(r) for r in rows]

    def get_alleles_by_rs(self, rs_id: str) -> list[dict]:
        conn = self.connect()
        rows = conn.execute("SELECT * FROM alleles WHERE rs_id = ?", (rs_id,)).fetchall()
        return [dict(r) for r in rows]

    def get_guidelines(self, drug: str, gene: str) -> list[dict]:
        conn = self.connect()
        rows = conn.execute(
            "SELECT * FROM guidelines WHERE drug_name = ? AND gene = ?",
            (drug, gene),
        ).fetchall()
        return [dict(r) for r in rows]

    def get_all_genes(self) -> list[str]:
        conn = self.connect()
        rows = conn.execute("SELECT DISTINCT gene FROM alleles").fetchall()
        return [r["gene"] for r in rows]

    def get_all_drugs(self) -> list[str]:
        conn = self.connect()
        rows = conn.execute("SELECT DISTINCT drug_name FROM guidelines").fetchall()
        return [r["drug_name"] for r in rows]


def build_database(
    alleles_data: dict,
    guidelines_data: Optional[dict] = None,
    db_path: Optional[Path] = None,
) -> PGxDatabase:
    """Build SQLite database from in-memory data dicts."""
    db = PGxDatabase(db_path)
    db.connect()
    db.load_alleles_from_json(alleles_data)

    if guidelines_data:
        conn = db._conn
        for (drug, gene), phenos in guidelines_data.items():
            for phenotype, (rec, evidence) in phenos.items():
                conn.execute(
                    "INSERT OR IGNORE INTO guidelines (drug_name, gene, phenotype, dosing_text, evidence_level) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (drug, gene, phenotype, rec, evidence),
                )
        conn.commit()

    return db
