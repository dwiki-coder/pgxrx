"""Tests for phenotype determination engine."""

import pytest

from pgxrx.core.diplotype import compute_diplotype_from_alleles
from pgxrx.core.phenotype import determine_phenotype


class TestCYP2C19Phenotypes:
    def test_poor_metabolizer(self):
        d = compute_diplotype_from_alleles("*2", "*3", "CYP2C19")
        result = determine_phenotype(d)
        assert result.phenotype == "Poor Metabolizer"

    def test_intermediate_metabolizer(self):
        d = compute_diplotype_from_alleles("*1", "*2", "CYP2C19")
        result = determine_phenotype(d)
        assert result.phenotype == "Intermediate Metabolizer"

    def test_normal_metabolizer(self):
        d = compute_diplotype_from_alleles("*1", "*1", "CYP2C19")
        result = determine_phenotype(d)
        assert result.phenotype == "Normal Metabolizer"

    def test_ultrarapid_metabolizer(self):
        d = compute_diplotype_from_alleles("*17", "*11", "CYP2C19")
        result = determine_phenotype(d)
        assert result.phenotype == "Ultrarapid Metabolizer"


class TestCYP2D6Phenotypes:
    def test_poor_metabolizer(self):
        d = compute_diplotype_from_alleles("*5", "*3", "CYP2D6")
        result = determine_phenotype(d)
        assert result.phenotype == "Poor Metabolizer"

    def test_intermediate_metabolizer(self):
        d = compute_diplotype_from_alleles("*1", "*10", "CYP2D6")
        result = determine_phenotype(d)
        assert result.phenotype == "Intermediate Metabolizer"

    def test_normal_metabolizer(self):
        d = compute_diplotype_from_alleles("*1", "*1", "CYP2D6")
        result = determine_phenotype(d)
        assert result.phenotype == "Normal Metabolizer"

    def test_ultrarapid_metabolizer(self):
        d = compute_diplotype_from_alleles("*1xN", "*1", "CYP2D6")
        result = determine_phenotype(d)
        assert result.phenotype == "Ultrarapid Metabolizer"


class TestCYP2C9Phenotypes:
    def test_poor_metabolizer(self):
        d = compute_diplotype_from_alleles("*3", "*3", "CYP2C9")
        result = determine_phenotype(d)
        assert result.phenotype == "Poor Metabolizer"

    def test_intermediate_metabolizer(self):
        d = compute_diplotype_from_alleles("*1", "*3", "CYP2C9")
        result = determine_phenotype(d)
        assert result.phenotype == "Intermediate Metabolizer"

    def test_normal_metabolizer(self):
        d = compute_diplotype_from_alleles("*1", "*1", "CYP2C9")
        result = determine_phenotype(d)
        assert result.phenotype == "Normal Metabolizer"


class TestSLCO1B1Phenotypes:
    def test_poor_metabolizer(self):
        d = compute_diplotype_from_alleles("*5", "*5", "SLCO1B1")
        result = determine_phenotype(d)
        assert result.phenotype == "Poor Metabolizer"

    def test_intermediate_metabolizer(self):
        d = compute_diplotype_from_alleles("*1", "*5", "SLCO1B1")
        result = determine_phenotype(d)
        assert result.phenotype == "Intermediate Metabolizer"


class TestDPYDPhenotypes:
    def test_poor_metabolizer(self):
        d = compute_diplotype_from_alleles("*2A", "*2A", "DPYD")
        result = determine_phenotype(d)
        assert result.phenotype == "Poor Metabolizer"

    def test_intermediate_metabolizer(self):
        d = compute_diplotype_from_alleles("*1", "*2A", "DPYD")
        result = determine_phenotype(d)
        assert result.phenotype == "Intermediate Metabolizer"


class TestTPMTPhenotypes:
    def test_poor_metabolizer(self):
        d = compute_diplotype_from_alleles("*3A", "*3C", "TPMT")
        result = determine_phenotype(d)
        assert result.phenotype == "Poor Metabolizer"

    def test_intermediate_metabolizer(self):
        d = compute_diplotype_from_alleles("*1", "*3C", "TPMT")
        result = determine_phenotype(d)
        assert result.phenotype == "Intermediate Metabolizer"


class TestHLAPhenotypes:
    def test_hla_b_positive(self):
        d = compute_diplotype_from_alleles("*57:01", "*44", "HLA-B")
        result = determine_phenotype(d)
        assert result.phenotype == "Positive"

    def test_hla_b_negative(self):
        d = compute_diplotype_from_alleles("*07", "*44", "HLA-B")
        result = determine_phenotype(d)
        assert result.phenotype == "Negative"


class TestPhenotypeResult:
    def test_has_all_fields(self):
        d = compute_diplotype_from_alleles("*1", "*1", "CYP2C19")
        result = determine_phenotype(d)
        assert result.gene == "CYP2C19"
        assert result.phenotype is not None
        assert result.confidence is not None
        assert result.diplotype == "*1/*1"
