"""Pytest configuration and shared fixtures for PGxRx tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

# Test data directory
TEST_DATA_DIR = Path(__file__).parent / "data"


@pytest.fixture
def test_vcf_cyp2c19():
    """Path to test CYP2C19 VCF."""
    return str(TEST_DATA_DIR / "test_cyp2c19.vcf")


@pytest.fixture
def test_vcf_cyp2d6():
    """Path to test CYP2D6 VCF."""
    return str(TEST_DATA_DIR / "test_cyp2d6.vcf")


@pytest.fixture
def test_vcf_cyp2c9():
    """Path to test CYP2C9 VCF."""
    return str(TEST_DATA_DIR / "test_cyp2c9.vcf")


@pytest.fixture
def test_vcf_multi():
    """Path to multi-gene test VCF."""
    return str(TEST_DATA_DIR / "test_multi.vcf")


@pytest.fixture
def test_vcf_dpyd():
    """Path to DPYD test VCF."""
    return str(TEST_DATA_DIR / "test_dpyd.vcf")


@pytest.fixture
def engine():
    """PGxEngine instance."""
    from pgxrx.core.engine import PGxEngine
    return PGxEngine()


@pytest.fixture
def mapper():
    """AlleleMapper instance."""
    from pgxrx.core.allele_mapper import AlleleMapper
    return AlleleMapper()


@pytest.fixture
def sample_variant():
    """A CYP2C19 *2 variant (rs4244285)."""
    from pgxrx.core.variant import Variant
    return Variant(
        chrom="10",
        pos=43084621,
        ref="G",
        alt="A",
        rs_id="rs4244285",
        gene="CYP2C19",
        sample_id="SAMPLE001",
        genotype="0/1",
    )


@pytest.fixture
def sample_cyp2d6_variant():
    """A CYP2D6 *2 variant (rs16947)."""
    from pgxrx.core.variant import Variant
    return Variant(
        chrom="22",
        pos=42413817,
        ref="G",
        alt="T",
        rs_id="rs16947",
        gene="CYP2D6",
        sample_id="SAMPLE001",
        genotype="0/1",
    )


@pytest.fixture
def sample_cyp2c9_variant():
    """A CYP2C9 *2 variant (rs1799853)."""
    from pgxrx.core.variant import Variant
    return Variant(
        chrom="10",
        pos=32108072,
        ref="A",
        alt="C",
        rs_id="rs1799853",
        gene="CYP2C9",
        sample_id="SAMPLE001",
        genotype="0/1",
    )


@pytest.fixture
def tmp_report_dir(tmp_path):
    """Temporary directory for report outputs."""
    return tmp_path
