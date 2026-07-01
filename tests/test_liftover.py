"""Tests for genome build coordinate conversion."""

import pytest

from pgxrx.core.liftover import (
    liftover_coordinate,
    get_genome_build,
)


class TestLiftover:
    def test_same_build_identity(self):
        chrom, pos = liftover_coordinate("10", 43084621, "CYP2C19", "GRCh38", "GRCh38")
        assert chrom == "10"
        assert pos == 43084621

    def test_detect_grch38(self):
        assert get_genome_build("##contig=<ID=chr10,GRCh38>") == "GRCh38"

    def test_detect_grch37(self):
        assert get_genome_build("##contig=<ID=chr10,hg19>") == "GRCh37"

    def test_default_to_grch38(self):
        assert get_genome_build("random header text") == "GRCh38"

    def test_hg38_detection(self):
        assert get_genome_build("##contig=<ID=chr10,hg38>") == "GRCh38"


class TestCoordinateConversion:
    def test_cyp2c19_coordinate(self):
        chrom, pos = liftover_coordinate("10", 43084621, "CYP2C19", "GRCh37", "GRCh38")
        assert pos >= 43084000  # Should be close to original
