"""Tests for data layer (database, loaders, RxNorm)."""

import pytest

from pgxrx.data.database import PGxDatabase
from pgxrx.data.rxnorm import normalize_drug_name, resolve_drug
from pgxrx.data.pharm_var import load_pharmvar_data
from pgxrx.data.cpic import load_cpic_data
from pgxrx.data.phargkb import load_phargkb_data
from pgxrx.data.update import update_knowledge_base
from pathlib import Path


class TestRxNorm:
    def test_normalize_plavix(self):
        assert normalize_drug_name("Plavix") == "clopidogrel"

    def test_normalize_nolvadex(self):
        assert normalize_drug_name("Nolvadex") == "tamoxifen"

    def test_normalize_coumadin(self):
        assert normalize_drug_name("Coumadin") == "warfarin"

    def test_normalize_unknown(self):
        assert normalize_drug_name("xyzdrug") == "xyzdrug"

    def test_resolve_drug(self):
        assert resolve_drug("Zoloft") == "sertraline"

    def test_normalize_zocor(self):
        assert normalize_drug_name("Zocor") == "simvastatin"


class TestDatabase:
    def test_create_tables(self, tmp_path):
        db = PGxDatabase(tmp_path / "test.db")
        db.connect()
        db.close()
        assert (tmp_path / "test.db").exists()

    def test_load_alleles(self, tmp_path):
        from pgxrx.core.allele_mapper import _PHARMVAR_ALLELES
        db = PGxDatabase(tmp_path / "test.db")
        db.load_alleles_from_json(_PHARMVAR_ALLELES)
        alleles = db.get_alleles_for_gene("CYP2C19")
        assert len(alleles) > 0

    def test_get_genes(self, tmp_path):
        from pgxrx.core.allele_mapper import _PHARMVAR_ALLELES
        db = PGxDatabase(tmp_path / "test.db")
        db.load_alleles_from_json(_PHARMVAR_ALLELES)
        genes = db.get_all_genes()
        assert "CYP2C19" in genes
        assert "CYP2D6" in genes

    def test_context_manager(self, tmp_path):
        with PGxDatabase(tmp_path / "ctx.db") as db:
            assert db._conn is not None


class TestDataLoaders:
    def test_load_pharmvar(self):
        data = load_pharmvar_data()
        assert "CYP2C19" in data
        assert "CYP2D6" in data

    def test_load_cpic(self):
        data = load_cpic_data()
        assert len(data) >= 30

    def test_load_phargkb(self):
        data = load_phargkb_data()
        assert "clopidogrel" in data


class TestUpdate:
    def test_update_returns_status(self):
        data_dir = Path(__file__).parent.parent.parent / "data"
        status = update_knowledge_base(data_dir)
        assert "timestamp" in status
        assert "alleles" in status
        assert "guidelines" in status
