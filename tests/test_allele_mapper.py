"""Tests for allele mapper."""

import pytest

from pgxrx.core.allele_mapper import AlleleMapper
from pgxrx.core.variant import Variant


class TestAlleleMapper:
    def test_map_cyp2c19_rs4244285(self, mapper, sample_variant):
        """rs4244285 should map to CYP2C19*2."""
        call = mapper.map_variant(sample_variant)
        assert call is not None
        assert call.gene == "CYP2C19"
        assert call.allele_name == "*2"
        assert call.activity_score == 0.0

    def test_map_cyp2d6_rs16947(self, mapper, sample_cyp2d6_variant):
        """rs16947 should map to CYP2D6*2."""
        call = mapper.map_variant(sample_cyp2d6_variant)
        assert call is not None
        assert call.gene == "CYP2D6"
        assert call.allele_name == "*2"

    def test_map_unknown_variant(self):
        """Unknown rsID should return None."""
        mapper = AlleleMapper()
        v = Variant(chrom="1", pos=100, ref="A", alt="T", rs_id="rs99999999")
        assert mapper.map_variant(v) is None

    def test_map_variant_no_rs_id(self):
        """Variant without rsID should return None."""
        mapper = AlleleMapper()
        v = Variant(chrom="10", pos=100, ref="A", alt="T", rs_id=None)
        assert mapper.map_variant(v) is None

    def test_map_variants_grouping(self, mapper, sample_variant, sample_cyp2d6_variant):
        """Multiple variants should be grouped by gene."""
        calls = mapper.map_variants([sample_variant, sample_cyp2d6_variant])
        assert "CYP2C19" in calls
        assert "CYP2D6" in calls

    def test_get_allele_activity_cyp2c19_star2(self, mapper):
        assert mapper.get_allele_activity("CYP2C19", "*2") == 0.0

    def test_get_allele_activity_cyp2c19_star1(self, mapper):
        assert mapper.get_allele_activity("CYP2C19", "*1") == 1.0

    def test_get_allele_activity_cyp2d6_star1(self, mapper):
        assert mapper.get_allele_activity("CYP2D6", "*1") == 1.0

    def test_get_all_genes(self, mapper):
        genes = mapper.get_all_genes()
        assert "CYP2C19" in genes
        assert "CYP2D6" in genes
        assert "CYP2C9" in genes

    def test_get_alleles_for_gene(self, mapper):
        alleles = mapper.get_alleles_for_gene("CYP2C19")
        assert "*" in str(alleles) or "*2" in alleles
        assert len(alleles) > 0
