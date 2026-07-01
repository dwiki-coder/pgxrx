"""Variant data model using Pydantic v2."""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field


class Variant(BaseModel):
    """A single genomic variant parsed from VCF."""

    chrom: str = Field(description="Chromosome, e.g. '10' or 'chr10'")
    pos: int = Field(description="1-based position")
    ref: str = Field(description="Reference allele")
    alt: str = Field(description="Alternate allele")
    sample_id: str = Field(default="UNKNOWN", description="Sample / patient ID")
    gene: Optional[str] = Field(default=None, description="Associated PGx gene")
    rs_id: Optional[str] = Field(default=None, description="dbSNP rsID")
    genotype: Optional[str] = Field(
        default=None, description="GT field, e.g. '0/1'"
    )
    quality: Optional[float] = Field(default=None)
    filter_status: Optional[str] = Field(default="PASS")
    extra_info: dict = Field(default_factory=dict)

    @property
    def allele_symbol(self) -> str:
        return f"{self.chrom}:{self.pos}{self.ref}>{self.alt}"

    def __hash__(self) -> int:
        return hash((self.chrom, self.pos, self.ref, self.alt))


class AlleleCall(BaseModel):
    """A PharmVar allele call for one chromosome."""

    gene: str
    allele_name: str  # e.g. "*2"
    rs_ids: list[str] = Field(default_factory=list)
    activity_score: Optional[float] = None
    chrom_source: str = Field(default="chr1", description="Which haplotype (1 or 2)")


class Diplotype(BaseModel):
    """A pair of alleles on two chromosomes."""

    gene: str
    allele1: str  # e.g. "*1"
    allele2: str  # e.g. "*2"
    activity_score: Optional[float] = None
    phenotype: Optional[str] = None

    def __str__(self) -> str:
        return f"{self.allele1}/{self.allele2}"


class PhenotypeResult(BaseModel):
    """CPIC phenotype for a gene-diplotype."""

    gene: str
    diplotype: str
    activity_score: Optional[float]
    phenotype: str  # e.g. "Intermediate Metabolizer"
    confidence: str = Field(default="High", description="Evidence confidence")


class DosingRecommendation(BaseModel):
    """CPIC dosing recommendation for a drug-gene-phenotype triple."""

    gene: str
    drug: str
    phenotype: str
    recommendation: str
    evidence_level: str = Field(default="A1")  # A1, A2, B, C
    guideline_version: str = Field(default="CPIC 2024")


class InterpretationReport(BaseModel):
    """Full interpretation for one sample, gene, optional drug."""

    sample_id: str
    gene: str
    variants: list[Variant] = Field(default_factory=list)
    allele_calls: list[AlleleCall] = Field(default_factory=list)
    diplotype: Optional[Diplotype] = None
    phenotype: Optional[PhenotypeResult] = None
    dosing: list[DosingRecommendation] = Field(default_factory=list)
    timestamp: str = ""
