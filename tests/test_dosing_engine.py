"""Tests for dosing recommendation engine."""

import pytest

from pgxrx.core.dosing import (
    get_dosing_recommendation,
    get_gene_drugs,
    get_drug_genes,
    get_all_guidelines,
    _DRUG_GENE_GUIDELINES,
)


class TestClopidogrelCYP2C19:
    def test_poor_metabolizer(self):
        rec = get_dosing_recommendation("clopidogrel", "CYP2C19", "Poor Metabolizer")
        assert rec is not None
        assert "alternative" in rec.recommendation.lower()
        assert rec.evidence_level == "A1"

    def test_intermediate_metabolizer(self):
        rec = get_dosing_recommendation("clopidogrel", "CYP2C19", "Intermediate Metabolizer")
        assert rec is not None
        assert "alternative" in rec.recommendation.lower()

    def test_normal_metabolizer(self):
        rec = get_dosing_recommendation("clopidogrel", "CYP2C19", "Normal Metabolizer")
        assert rec is not None
        assert "standard" in rec.recommendation.lower() or "no change" in rec.recommendation.lower()


class TestCodeineCYP2D6:
    def test_poor_metabolizer(self):
        rec = get_dosing_recommendation("codeine", "CYP2D6", "Poor Metabolizer")
        assert rec is not None
        assert "avoid" in rec.recommendation.lower()
        assert rec.evidence_level == "A1"

    def test_ultrarapid_metabolizer(self):
        rec = get_dosing_recommendation("codeine", "CYP2D6", "Ultrarapid Metabolizer")
        assert rec is not None
        assert "avoid" in rec.recommendation.lower() or "toxicity" in rec.recommendation.lower()


class TestTamoxifenCYP2D6:
    def test_poor_metabolizer(self):
        rec = get_dosing_recommendation("tamoxifen", "CYP2D6", "Poor Metabolizer")
        assert rec is not None
        assert "alternative" in rec.recommendation.lower()


class TestSimvastatinSLCO1B1:
    def test_poor_metabolizer(self):
        rec = get_dosing_recommendation("simvastatin", "SLCO1B1", "Poor Metabolizer")
        assert rec is not None
        assert "myopathy" in rec.recommendation.lower() or "alternative" in rec.recommendation.lower()


class TestWarfarinCYP2C9:
    def test_poor_metabolizer(self):
        rec = get_dosing_recommendation("warfarin", "CYP2C9", "Poor Metabolizer")
        assert rec is not None
        assert rec.evidence_level == "A1"


class TestAbacavirHLA:
    def test_positive(self):
        rec = get_dosing_recommendation("abacavir", "HLA-B", "Positive")
        assert rec is not None
        assert "avoid" in rec.recommendation.lower()
        assert rec.evidence_level == "A1"


class TestThiopurinesTPMT:
    def test_mercaptopurine_poor(self):
        rec = get_dosing_recommendation("mercaptopurine", "TPMT", "Poor Metabolizer")
        assert rec is not None

    def test_azathioprine_intermediate(self):
        rec = get_dosing_recommendation("azathioprine", "TPMT", "Intermediate Metabolizer")
        assert rec is not None


class TestUnknownDrugGene:
    def test_no_guideline_returns_none(self):
        rec = get_dosing_recommendation("xyzdrug", "CYP2C19", "Normal Metabolizer")
        assert rec is None


class TestGuidelineCoverage:
    def test_minimum_guidelines(self):
        """We should have at least 30 drug-gene pairs."""
        pairs = list(_DRUG_GENE_GUIDELINES.keys())
        assert len(pairs) >= 30

    def test_has_cyp2c19_drugs(self):
        drugs = get_gene_drugs("CYP2C19")
        assert "clopidogrel" in drugs

    def test_has_cyp2d6_drugs(self):
        drugs = get_gene_drugs("CYP2D6")
        assert "codeine" in drugs

    def test_get_drug_genes_clopidogrel(self):
        genes = get_drug_genes("clopidogrel")
        assert "CYP2C19" in genes

    def test_get_all_guidelines(self):
        guidelines = get_all_guidelines()
        assert len(guidelines) >= 30

    def test_effavirenz_cyp2b6(self):
        rec = get_dosing_recommendation("efavirenz", "CYP2B6", "Poor Metabolizer")
        assert rec is not None

    def test_varenicline_cyp2a6(self):
        rec = get_dosing_recommendation("varenicline", "CYP2A6", "Poor Metabolizer")
        assert rec is not None

    def test_isoniazid_nat2(self):
        rec = get_dosing_recommendation("isoniazid", "NAT2", "Poor acetylator")
        assert rec is not None

    def test_irinotecan_dpyd(self):
        rec = get_dosing_recommendation("irinotecan", "DPYD", "Poor Metabolizer")
        assert rec is not None
        assert rec.evidence_level in ("A1", "A2")
