"""Tests for VCF parser."""

import gzip
from pathlib import Path

import pytest

from pgxrx.core.vcf_parser import (
    PGX_GENES,
    _normalize_chrom,
    _find_gene,
    _normalize_variant,
    parse_vcf,
    _read_vcf_lines,
)
from pgxrx.core.variant import Variant


class TestChromosomeNormalization:
    def test_strip_chr_prefix(self):
        assert _normalize_chrom("chr10") == "10"

    def test_already_no_prefix(self):
        assert _normalize_chrom("10") == "10"

    def test_x_chromosome(self):
        assert _normalize_chrom("chrX") == "X"

    def test_y_chromosome(self):
        assert _normalize_chrom("chrY") == "Y"

    def test_chr1(self):
        assert _normalize_chrom("chr1") == "1"


class TestGeneLookup:
    def test_find_cyp2c19(self):
        gene = _find_gene("10", 43084621)
        assert gene == "CYP2C19"

    def test_find_cyp2d6(self):
        gene = _find_gene("22", 42413817)
        assert gene == "CYP2D6"

    def test_find_cyp2c9(self):
        gene = _find_gene("10", 32108072)
        assert gene == "CYP2C9"

    def test_find_sco1b1(self):
        gene = _find_gene("12", 49266278)
        assert gene == "SLCO1B1"

    def test_no_gene_found(self):
        gene = _find_gene("1", 100)
        assert gene is None

    def test_find_dpyd(self):
        gene = _find_gene("1", 69873953)
        assert gene == "DPYD"

    def test_find_tpmt(self):
        gene = _find_gene("6", 44144383)
        assert gene == "TPMT"


class TestVariantNormalization:
    def test_normalizes_lowercase(self):
        v = Variant(chrom="chr10", pos=100, ref="g", alt="a")
        result = _normalize_variant(v)
        assert result.chrom == "10"
        assert result.ref == "G"
        assert result.alt == "A"

    def test_normalizes_already_good(self):
        v = Variant(chrom="10", pos=100, ref="G", alt="A")
        result = _normalize_variant(v)
        assert result.chrom == "10"


class TestVCFParser:
    def test_parse_cyp2c19_vcf(self, test_vcf_cyp2c19):
        variants = parse_vcf(test_vcf_cyp2c19)
        assert len(variants) >= 1
        assert any(v.gene == "CYP2C19" for v in variants)

    def test_parse_cyp2d6_vcf(self, test_vcf_cyp2d6):
        variants = parse_vcf(test_vcf_cyp2d6)
        assert len(variants) >= 1
        assert any(v.gene == "CYP2D6" for v in variants)

    def test_parse_multi_gene_vcf(self, test_vcf_multi):
        variants = parse_vcf(test_vcf_multi)
        genes_found = set(v.gene for v in variants if v.gene)
        assert "CYP2C19" in genes_found
        assert "CYP2C9" in genes_found

    def test_parse_with_sample_id(self, test_vcf_cyp2c19):
        variants = parse_vcf(test_vcf_cyp2c19, sample_id="PATIENT123")
        assert all(v.sample_id == "PATIENT123" for v in variants)

    def test_parse_with_gene_filter(self, test_vcf_multi):
        variants = parse_vcf(test_vcf_multi, genes=["CYP2C19"])
        assert all(v.gene == "CYP2C19" or v.gene is None for v in variants)

    def test_parse_gzipped_vcf(self, test_vcf_cyp2c19, tmp_path):
        # Create a gzipped copy
        gz_path = tmp_path / "test.vcf.gz"
        with open(test_vcf_cyp2c19) as src:
            with gzip.open(gz_path, "wt") as dst:
                dst.write(src.read())
        variants = parse_vcf(str(gz_path))
        assert len(variants) >= 1


class TestPGXGenes:
    def test_genes_dict_not_empty(self):
        assert len(PGX_GENES) >= 20

    def test_cyp2c19_in_genes(self):
        assert "CYP2C19" in PGX_GENES

    def test_cyp2d6_in_genes(self):
        assert "CYP2D6" in PGX_GENES

    def test_genes_have_coordinates(self):
        for gene, coords in PGX_GENES.items():
            assert "chrom" in coords
            assert "start" in coords
            assert "end" in coords
