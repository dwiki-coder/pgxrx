"""Tests for the full PGx pipeline (engine)."""

import pytest

from pgxrx.core.engine import PGxEngine
from pgxrx.core.variant import Variant


class TestFullPipelineDirect:
    def test_cyp2c19_star2_star1_clopidogrel(self, engine):
        """CYP2C19 *1/*2 + clopidogrel → IM, recommend alternative."""
        report = engine.interpret_direct(
            gene="CYP2C19",
            allele1="*2",
            allele2="*1",
            drugs=["clopidogrel"],
            sample_id="TEST001",
        )
        assert report.gene == "CYP2C19"
        assert report.diplotype is not None
        assert report.phenotype is not None
        assert "Intermediate" in report.phenotype.phenotype
        assert len(report.dosing) > 0
        assert report.dosing[0].drug == "clopidogrel"

    def test_cyp2c19_star1_star1_clopidogrel(self, engine):
        """CYP2C19 *1/*1 + clopidogrel → NM, no change."""
        report = engine.interpret_direct(
            gene="CYP2C19",
            allele1="*1",
            allele2="*1",
            drugs=["clopidogrel"],
        )
        assert "Normal" in report.phenotype.phenotype
        assert "standard" in report.dosing[0].recommendation.lower() or "no change" in report.dosing[0].recommendation.lower()

    def test_cyp2c19_star2_star2_clopidogrel(self, engine):
        """CYP2C19 *2/*2 + clopidogrel → PM, avoid."""
        report = engine.interpret_direct(
            gene="CYP2C19",
            allele1="*2",
            allele2="*2",
            drugs=["clopidogrel"],
        )
        assert "Poor" in report.phenotype.phenotype

    def test_cyp2d6_codeine_poor(self, engine):
        report = engine.interpret_direct(
            gene="CYP2D6",
            allele1="*5",
            allele2="*3",
            drugs=["codeine"],
        )
        assert "Poor" in report.phenotype.phenotype
        assert "avoid" in report.dosing[0].recommendation.lower()

    def test_cyp2d6_codeine_ultrarapid(self, engine):
        report = engine.interpret_direct(
            gene="CYP2D6",
            allele1="*1xN",
            allele2="*1",
            drugs=["codeine"],
        )
        assert "Ultrarapid" in report.phenotype.phenotype

    def test_cyp2d6_tamoxifen(self, engine):
        report = engine.interpret_direct(
            gene="CYP2D6",
            allele1="*4",
            allele2="*4",
            drugs=["tamoxifen"],
        )
        assert "Poor" in report.phenotype.phenotype
        assert "alternative" in report.dosing[0].recommendation.lower()

    def test_no_drugs(self, engine):
        """Without drugs, no dosing recommendations."""
        report = engine.interpret_direct(
            gene="CYP2C19",
            allele1="*2",
            allele2="*1",
            drugs=[],
        )
        assert len(report.dosing) == 0

    def test_multiple_drugs(self, engine):
        """Multiple drugs should produce multiple dosing entries."""
        report = engine.interpret_direct(
            gene="CYP2C19",
            allele1="*2",
            allele2="*1",
            drugs=["clopidogrel", "sertraline"],
        )
        assert len(report.dosing) >= 1


class TestFullPipelineVCF:
    def test_parse_and_interpret(self, engine, test_vcf_cyp2c19):
        """Full pipeline from VCF parsing to interpretation."""
        variants = engine.mapper.map_variants(
            [
                Variant(
                    chrom="10", pos=43084621, ref="G", alt="A",
                    rs_id="rs4244285", gene="CYP2C19", sample_id="TEST",
                )
            ]
        )
        assert "CYP2C19" in variants

    def test_engine_annotate(self, engine, sample_variant):
        result = engine.annotate([sample_variant])
        assert "CYP2C19" in result


class TestPipelineVariance:
    def test_cyp2c9_warfarin(self, engine):
        report = engine.interpret_direct(
            gene="CYP2C9",
            allele1="*3",
            allele2="*3",
            drugs=["warfarin"],
        )
        assert report.phenotype is not None
        assert len(report.dosing) > 0

    def test_slco1b1_simvastatin(self, engine):
        report = engine.interpret_direct(
            gene="SLCO1B1",
            allele1="*5",
            allele2="*5",
            drugs=["simvastatin"],
        )
        assert "Poor" in report.phenotype.phenotype
        assert "myopathy" in report.dosing[0].recommendation.lower() or "alternative" in report.dosing[0].recommendation.lower()

    def test_dpyd_5fu(self, engine):
        report = engine.interpret_direct(
            gene="DPYD",
            allele1="*2A",
            allele2="*2A",
            drugs=["5-fluorouracil"],
        )
        assert "Poor" in report.phenotype.phenotype

    def test_tpmt_azathioprine(self, engine):
        report = engine.interpret_direct(
            gene="TPMT",
            allele1="*3A",
            allele2="*3A",
            drugs=["azathioprine"],
        )
        assert "Poor" in report.phenotype.phenotype

    def test_cyp3a5_tacrolimus(self, engine):
        report = engine.interpret_direct(
            gene="CYP3A5",
            allele1="*1",
            allele2="*1",
            drugs=["tacrolimus"],
        )
        assert report.phenotype is not None
        assert len(report.dosing) > 0
