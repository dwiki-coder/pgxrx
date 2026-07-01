"""PGxRx - Pharmacogenomics Prescription Decision Tool.

A command-line tool that takes VCF genotype data and produces
CPIC-guideline-based dosing recommendations.

Pipeline: VCF → Variant Normalization → PharmVar Alleles →
          CPIC Phenotype → Dosing Recommendation → Report
"""

__version__ = "0.1.0"
