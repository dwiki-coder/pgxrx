"""FastAPI application for PGxRx REST API."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from pgxrx.core.engine import PGxEngine
from pgxrx.core.vcf_parser import parse_vcf
from pgxrx.core.diplotype import compute_diplotype_from_alleles
from pgxrx.core.phenotype import determine_phenotype
from pgxrx.core.dosing import get_dosing_recommendation, get_gene_drugs
from pgxrx.data.rxnorm import normalize_drug_name

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="PGxRx API",
    description="Pharmacogenomics prescription decision API. "
                "Map VCF variants → PharmVar alleles → CPIC phenotypes → dosing.",
    version="0.1.0",
)

# ── Static UI ──────────────────────────────────────────────────────────
_web_dir = Path(__file__).resolve().parent.parent / "web"
app.mount("/static", StaticFiles(directory=str(_web_dir)), name="static")

# ── Request/Response models ──────────────────────────────────────────


class AnnotateRequest(BaseModel):
    """Request model for /annotate endpoint."""
    gene: str
    allele1: str
    allele2: str
    drugs: list[str] = []
    sample_id: str = "UNKNOWN"


class AnnotateResponse(BaseModel):
    """Response model for /annotate endpoint."""
    sample_id: str
    gene: str
    diplotype: str
    activity_score: Optional[float] = None
    phenotype: str
    confidence: str
    dosing: list[dict] = []


class PhenotypeRequest(BaseModel):
    """Request model for /phenotype endpoint."""
    gene: str
    allele1: str
    allele2: str


class PhenotypeResponse(BaseModel):
    """Response model for /phenotype endpoint."""
    gene: str
    diplotype: str
    activity_score: Optional[float] = None
    phenotype: str
    confidence: str


class DoseRequest(BaseModel):
    """Request model for /dose endpoint."""
    drug: str
    gene: str
    phenotype: str


class DoseResponse(BaseModel):
    """Response model for /dose endpoint."""
    gene: str
    drug: str
    phenotype: str
    recommendation: str
    evidence_level: str
    guideline_version: str


class GeneInfo(BaseModel):
    """Gene information."""
    gene: str
    alleles: list[str]


class DrugInfo(BaseModel):
    """Drug information."""
    drug: str
    genes: list[str]


# ── Endpoints ─────────────────────────────────────────────────────────

engine = PGxEngine()


@app.get("/health")
async def health():
    """Health check."""
    return {
        "service": "PGxRx API",
        "version": "0.1.0",
        "status": "healthy",
    }


@app.get("/")
async def serve_ui():
    """Serve the web UI."""
    return FileResponse(str(_web_dir / "index.html"))


@app.post("/annotate", response_model=AnnotateResponse)
async def annotate(request: AnnotateRequest):
    """Full interpretation: alleles → diplotype → phenotype → dosing.

    Example request:
    ```json
    {
        "gene": "CYP2C19",
        "allele1": "*2",
        "allele2": "*1",
        "drugs": ["clopidogrel"],
        "sample_id": "PATIENT001"
    }
    ```
    """
    report = engine.interpret_direct(
        gene=request.gene,
        allele1=request.allele1,
        allele2=request.allele2,
        drugs=request.drugs,
        sample_id=request.sample_id,
    )

    dosing = []
    for d in report.dosing:
        dosing.append({
            "drug": d.drug,
            "phenotype": d.phenotype,
            "recommendation": d.recommendation,
            "evidence_level": d.evidence_level,
        })

    return AnnotateResponse(
        sample_id=report.sample_id,
        gene=report.gene,
        diplotype=str(report.diplotype) if report.diplotype else "",
        activity_score=report.diplotype.activity_score if report.diplotype else None,
        phenotype=report.phenotype.phenotype if report.phenotype else "",
        confidence=report.phenotype.confidence if report.phenotype else "",
        dosing=dosing,
    )


@app.post("/phenotype", response_model=PhenotypeResponse)
async def phenotype(request: PhenotypeRequest):
    """Determine CPIC phenotype from allele pair.

    Example request:
    ```json
    {
        "gene": "CYP2C19",
        "allele1": "*2",
        "allele2": "*1"
    }
    ```
    """
    diplotype = compute_diplotype_from_alleles(request.allele1, request.allele2, request.gene)
    result = determine_phenotype(diplotype)

    return PhenotypeResponse(
        gene=result.gene,
        diplotype=result.diplotype,
        activity_score=result.activity_score,
        phenotype=result.phenotype,
        confidence=result.confidence,
    )


@app.post("/dose", response_model=DoseResponse)
async def dose(request: DoseRequest):
    """Get dosing recommendation for drug-gene-phenotype.

    Example request:
    ```json
    {
        "drug": "clopidogrel",
        "gene": "CYP2C19",
        "phenotype": "Intermediate Metabolizer"
    }
    ```
    """
    rec = get_dosing_recommendation(request.drug, request.gene, request.phenotype)
    if rec is None:
        raise HTTPException(
            status_code=404,
            detail=f"No guideline found for drug={request.drug}, gene={request.gene}, phenotype={request.phenotype}",
        )

    return DoseResponse(
        gene=rec.gene,
        drug=rec.drug,
        phenotype=rec.phenotype,
        recommendation=rec.recommendation,
        evidence_level=rec.evidence_level,
        guideline_version=rec.guideline_version,
    )


@app.get("/genes", response_model=list[GeneInfo])
async def list_genes():
    """List all supported PGx genes with their known alleles."""
    genes_info = []
    for gene in sorted(engine.mapper.get_all_genes()):
        alleles = engine.mapper.get_alleles_for_gene(gene)
        genes_info.append(
            GeneInfo(gene=gene, alleles=list(alleles.keys()))
        )
    return genes_info


@app.get("/drugs", response_model=list[DrugInfo])
async def list_drugs():
    """List all supported drugs with their associated genes."""
    from pgxrx.core.dosing import _DRUG_GENE_GUIDELINES
    drug_genes = {}
    for (drug, gene) in _DRUG_GENE_GUIDELINES:
        drug_genes.setdefault(drug, []).append(gene)

    return [DrugInfo(drug=d, genes=sorted(g)) for d, g in sorted(drug_genes.items())]


@app.get("/genes/{gene}/drugs", response_model=list[str])
async def get_gene_drugs_endpoint(gene: str):
    """Get all drugs associated with a gene."""
    return get_gene_drugs(gene)


@app.get("/drugs/{drug}/genes", response_model=list[str])
async def get_drug_genes_endpoint(drug: str):
    """Get all genes associated with a drug."""
    from pgxrx.core.dosing import get_drug_genes
    return get_drug_genes(drug)
