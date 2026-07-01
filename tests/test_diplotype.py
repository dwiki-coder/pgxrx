"""Tests for diplotype calculator."""

import pytest

from pgxrx.core.diplotype import compute_diplotype, compute_diplotype_from_alleles
from pgxrx.core.variant import AlleleCall, Diplotype


class TestDiplotypeComputation:
    def test_star1_star2_cyp2c19(self):
        d = compute_diplotype_from_alleles("*1", "*2", "CYP2C19")
        assert d.allele1 == "*1"
        assert d.allele2 == "*2"
        assert d.activity_score == 1.0  # 1.0 + 0.0

    def test_star2_star2_cyp2c19(self):
        d = compute_diplotype_from_alleles("*2", "*2", "CYP2C19")
        assert d.activity_score == 0.0

    def test_star1_star1_cyp2c19(self):
        d = compute_diplotype_from_alleles("*1", "*1", "CYP2C19")
        assert d.activity_score == 2.0

    def test_cyp2d6_star1_star5(self):
        d = compute_diplotype_from_alleles("*1", "*5", "CYP2D6")
        assert d.activity_score == 1.0  # 1.0 + 0.0

    def test_cyp2d6_star1xN_star1(self):
        d = compute_diplotype_from_alleles("*1xN", "*1", "CYP2D6")
        assert d.activity_score == 3.0  # 2.0 + 1.0

    def test_cyp2c9_star1_star3(self):
        d = compute_diplotype_from_alleles("*1", "*3", "CYP2C9")
        assert d.activity_score == 1.1  # 1.0 + 0.1

    def test_diplotype_str(self):
        d = Diplotype(gene="CYP2C19", allele1="*1", allele2="*2")
        assert str(d) == "*1/*2"

    def test_empty_allele_calls_defaults_to_ref(self):
        d = compute_diplotype([], "CYP2C19")
        assert d.allele1 == "*1"
        assert d.allele2 == "*1"

    def test_single_allele_call_with_default(self):
        calls = [AlleleCall(gene="CYP2C19", allele_name="*2", chrom_source="chr1")]
        d = compute_diplotype(calls, "CYP2C19")
        assert d.allele1 == "*2"
        assert d.allele2 == "*1"

    def test_slco1b1_star1_star5(self):
        d = compute_diplotype_from_alleles("*1", "*5", "SLCO1B1")
        assert d.activity_score == 1.0  # 1.0 + 0.0

    def test_dpyd_star1_star2A(self):
        d = compute_diplotype_from_alleles("*1", "*2A", "DPYD")
        assert d.activity_score == 1.0
