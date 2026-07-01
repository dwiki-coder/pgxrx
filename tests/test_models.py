"""Tests for Pydantic data models."""

import pytest

from pgxrx.core.variant import (
    Variant,
    AlleleCall,
    Diplotype,
    PhenotypeResult,
    DosingRecommendation,
    InterpretationReport,
)


class TestVariantModel:
    def test_create_variant(self):
        v = Variant(chrom="10", pos=100, ref="A", alt="T")
        assert v.chrom == "10"
        assert v.pos == 100

    def test_allele_symbol(self):
        v = Variant(chrom="10", pos=100, ref="A", alt="T")
        assert v.allele_symbol == "10:100A>T"

    def test_hashable(self):
        v = Variant(chrom="10", pos=100, ref="A", alt="T")
        assert hash(v) is not None

    def test_defaults(self):
        v = Variant(chrom="10", pos=100, ref="A", alt="T")
        assert v.sample_id == "UNKNOWN"
        assert v.filter_status == "PASS"
        assert v.gene is None

    def test_full_variant(self):
        v = Variant(
            chrom="10", pos=100, ref="A", alt="T",
            rs_id="rs123", gene="CYP2C19", sample_id="PAT",
            genotype="0/1", quality=99.5,
        )
        assert v.rs_id == "rs123"
        assert v.gene == "CYP2C19"
        assert v.genotype == "0/1"


class TestAlleleCallModel:
    def test_create(self):
        ac = AlleleCall(gene="CYP2C19", allele_name="*2", activity_score=0.0)
        assert ac.gene == "CYP2C19"
        assert ac.allele_name == "*2"

    def test_defaults(self):
        ac = AlleleCall(gene="CYP2C19", allele_name="*2")
        assert ac.rs_ids == []
        assert ac.chrom_source == "chr1"


class TestDiplotypeModel:
    def test_create(self):
        d = Diplotype(gene="CYP2C19", allele1="*1", allele2="*2")
        assert str(d) == "*1/*2"

    def test_with_activity_score(self):
        d = Diplotype(gene="CYP2C19", allele1="*1", allele2="*2", activity_score=1.0)
        assert d.activity_score == 1.0


class TestPhenotypeResultModel:
    def test_create(self):
        r = PhenotypeResult(
            gene="CYP2C19",
            diplotype="*1/*2",
            activity_score=1.0,
            phenotype="Intermediate Metabolizer",
        )
        assert r.phenotype == "Intermediate Metabolizer"
        assert r.confidence == "High"  # default

    def test_model_dump(self):
        r = PhenotypeResult(
            gene="CYP2C19",
            diplotype="*1/*2",
            activity_score=1.0,
            phenotype="Normal Metabolizer",
        )
        d = r.model_dump()
        assert "gene" in d
        assert "phenotype" in d


class TestDosingRecommendationModel:
    def test_create(self):
        d = DosingRecommendation(
            gene="CYP2C19", drug="clopidogrel", phenotype="IM",
            recommendation="Consider alternative",
        )
        assert d.evidence_level == "A1"  # default
        assert d.guideline_version == "CPIC 2024"


class TestInterpretationReportModel:
    def test_create(self):
        r = InterpretationReport(sample_id="TEST", gene="CYP2C19")
        assert r.sample_id == "TEST"
        assert r.variants == []
        assert r.dosing == []

    def test_full_report(self):
        r = InterpretationReport(
            sample_id="TEST",
            gene="CYP2C19",
            variants=[Variant(chrom="10", pos=100, ref="A", alt="T", rs_id="rs123")],
            allele_calls=[AlleleCall(gene="CYP2C19", allele_name="*2")],
            diplotype=Diplotype(gene="CYP2C19", allele1="*1", allele2="*2"),
            phenotype=PhenotypeResult(
                gene="CYP2C19", diplotype="*1/*2",
                activity_score=1.0, phenotype="Intermediate Metabolizer",
            ),
            dosing=[DosingRecommendation(
                gene="CYP2C19", drug="clopidogrel", phenotype="IM",
                recommendation="Test recommendation",
            )],
        )
        assert len(r.variants) == 1
        assert len(r.allele_calls) == 1
        assert r.diplotype is not None
        assert r.phenotype is not None
        assert len(r.dosing) == 1
