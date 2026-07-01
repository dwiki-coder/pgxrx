"""Orchestrator — full PGx pipeline.

VCF → Variants → Alleles → Diplotypes → Phenotypes → Dosing → Report
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Optional

from pgxrx.core.allele_mapper import AlleleMapper
from pgxrx.core.diplotype import compute_diplotype, compute_diplotype_from_alleles
from pgxrx.core.phenotype import determine_phenotype
from pgxrx.core.dosing import get_dosing_recommendation
from pgxrx.core.variant import (
    AlleleCall,
    Diplotype,
    InterpretationReport,
    PhenotypeResult,
    Variant,
    DosingRecommendation,
)

logger = logging.getLogger(__name__)


class PGxEngine:
    """Full PGx interpretation pipeline.

    Usage
    -----
    >>> engine = PGxEngine()
    >>> report = engine.interpret(vcf_path="patient.vcf", drugs=["clopidogrel"])
    """

    def __init__(self, alleles_data: Optional[dict] = None):
        self.mapper = AlleleMapper(alleles_data=alleles_data)

    def annotate(
        self,
        variants: list[Variant],
        genes: Optional[list[str]] = None,
    ) -> dict[str, list[AlleleCall]]:
        """Step 1: Map variants to allele calls, grouped by gene."""
        return self.mapper.map_variants(variants)

    def compute_diplotype(
        self,
        gene: str,
        allele_calls: Optional[list[AlleleCall]] = None,
        allele1: str = "*1",
        allele2: str = "*1",
    ) -> Diplotype:
        """Step 2: Compute diplotype for a gene."""
        if allele_calls:
            return compute_diplotype(allele_calls, gene)
        return compute_diplotype_from_alleles(allele1, allele2, gene)

    def determine_phenotype(self, diplotype: Diplotype) -> PhenotypeResult:
        """Step 3: Determine phenotype from diplotype."""
        return determine_phenotype(diplotype)

    def get_dosing(
        self,
        drug: str,
        gene: str,
        phenotype: str,
    ) -> Optional[DosingRecommendation]:
        """Step 4: Get dosing recommendation."""
        return get_dosing_recommendation(drug, gene, phenotype)

    def interpret(
        self,
        variants: list[Variant],
        drugs: Optional[list[str]] = None,
        genes: Optional[list[str]] = None,
        sample_id: str = "UNKNOWN",
    ) -> list[InterpretationReport]:
        """Run full pipeline: variants → alleles → diplotypes → phenotypes → dosing.

        Parameters
        ----------
        variants : list of Variant objects
        drugs : optional list of drugs to check dosing for
        genes : optional list of genes to focus on
        sample_id : patient/sample identifier

        Returns
        -------
        list of InterpretationReport (one per gene)
        """
        # Step 1: Allele mapping
        allele_map = self.annotate(variants, genes)
        logger.info("Mapped alleles for %d genes", len(allele_map))

        reports: list[InterpretationReport] = []

        for gene, calls in allele_map.items():
            report = InterpretationReport(
                sample_id=sample_id,
                gene=gene,
                variants=[v for v in variants if v.gene == gene],
                allele_calls=calls,
                timestamp=datetime.now(timezone.utc).isoformat(),
            )

            # Step 2: Diplotype
            diplotype = self.compute_diplotype(gene, calls)
            report.diplotype = diplotype

            # Step 3: Phenotype
            phenotype = self.determine_phenotype(diplotype)
            report.phenotype = phenotype

            # Step 4: Dosing
            if drugs:
                for drug in drugs:
                    rec = self.get_dosing(drug, gene, phenotype.phenotype)
                    if rec:
                        report.dosing.append(rec)

            reports.append(report)
            logger.info(
                "Gene %s: diplotype=%s, phenotype=%s",
                gene,
                diplotype,
                phenotype.phenotype,
            )

        return reports

    def interpret_direct(
        self,
        gene: str,
        allele1: str,
        allele2: str,
        drugs: Optional[list[str]] = None,
        sample_id: str = "UNKNOWN",
    ) -> InterpretationReport:
        """Interpret directly from known alleles (no VCF needed).

        Useful for manual entry or API calls with known genotypes.

        Parameters
        ----------
        gene : gene symbol
        allele1 : allele on chr1 (e.g. "*2")
        allele2 : allele on chr2 (e.g. "*1")
        drugs : optional drug list
        sample_id : sample ID

        Returns
        -------
        InterpretationReport
        """
        report = InterpretationReport(
            sample_id=sample_id,
            gene=gene,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

        # Diplotype
        diplotype = self.compute_diplotype(gene, allele1=allele1, allele2=allele2)
        report.diplotype = diplotype

        # Phenotype
        phenotype = self.determine_phenotype(diplotype)
        report.phenotype = phenotype

        # Dosing
        if drugs:
            for drug in drugs:
                rec = self.get_dosing(drug, gene, phenotype.phenotype)
                if rec:
                    report.dosing.append(rec)

        return report
