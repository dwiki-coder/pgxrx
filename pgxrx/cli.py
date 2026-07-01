"""PGxRx CLI - Typer-based command-line interface.

Subcommands:
  annotate   - Map VCF variants to PharmVar alleles
  phenotype  - Determine CPIC phenotype from diplotypes
  dose       - Get dosing recommendations
  report     - Generate clinical reports (JSON, CSV, HTML, PDF)
  batch      - Process multiple VCF files
  update     - Update knowledge base
  serve      - Start FastAPI server
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Optional

import typer

from pgxrx import __version__
from pgxrx.core.engine import PGxEngine
from pgxrx.core.vcf_parser import parse_vcf
from pgxrx.core.diplotype import compute_diplotype_from_alleles
from pgxrx.core.phenotype import determine_phenotype
from pgxrx.core.dosing import get_dosing_recommendation, get_gene_drugs
from pgxrx.data.rxnorm import normalize_drug_name
from pgxrx.reports.json_report import to_json
from pgxrx.reports.csv_report import to_csv
from pgxrx.reports.html_report import to_html
from pgxrx.reports.pdf_report import to_pdf

cli = typer.Typer(
    name="pgxrx",
    add_completion=False,
)


def _version_callback(value: bool):
    if value:
        typer.echo(f"pgxrx {__version__}")
        raise typer.Exit()


@cli.callback()
def _common_callback(version: bool = typer.Option(False, "--version", callback=_version_callback)):
    """PGxRx - Pharmacogenomics Prescription Decision Tool.

    VCF → PharmVar → CPIC Phenotype → Dosing Recommendation
    """
    pass


# ── annotate subcommand group ─────────────────────────────────────────
annotate_cli = typer.Typer(
    add_help_option=True,
    help="Map VCF variants to PharmVar alleles and interpret",
)
cli.add_typer(annotate_cli, name="annotate")


@annotate_cli.command("vcf")
def annotate_vcf(
    vcf_file: str = typer.Argument(..., help="Path to VCF file"),
    drug: Optional[str] = typer.Option(None, "--drug", "-d", help="Drug to check dosing for"),
    drugs: Optional[str] = typer.Option(None, "--drugs", help="Comma-separated list of drugs"),
    gene: Optional[str] = typer.Option(None, "--gene", "-g", help="Specific gene to analyze"),
    sample_id: str = typer.Option("SAMPLE001", "--sample-id", "-s", help="Sample/patient ID"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path"),
    format: str = typer.Option("json", "--format", "-f", help="Output format (json, csv, html, pdf)"),
    genes: Optional[str] = typer.Option(None, "--genes", help="Comma-separated list of genes"),
):
    """Annotate VCF variants and produce full interpretation.

    Reads a VCF file, maps variants to PharmVar alleles, determines
    CPIC phenotypes, and outputs dosing recommendations.

    Example:
        pgxrx annotate vcf sample.vcf --drug clopidogrel --gene CYP2C19
    """
    drug_list = []
    if drug:
        drug_list.append(normalize_drug_name(drug))
    if drugs:
        drug_list.extend(normalize_drug_name(d.strip()) for d in drugs.split(","))

    gene_list = [g.strip() for g in genes.split(",")] if genes else None
    if gene:
        gene_list = [gene]

    variants = parse_vcf(vcf_file, sample_id=sample_id, genes=gene_list)
    if not variants:
        typer.echo(f"No PGx variants found in {vcf_file}", err=True)
        raise typer.Exit(1)

    engine = PGxEngine()
    reports = engine.interpret(variants, drugs=drug_list, genes=gene_list, sample_id=sample_id)

    if not output:
        # Default to stdout
        if format == "json":
            typer.echo(to_json(reports))
        elif format == "csv":
            typer.echo(to_csv(reports))
        elif format == "html":
            typer.echo(to_html(reports))
        elif format == "pdf":
            typer.echo(to_html(reports))  # PDF needs file output
        else:
            typer.echo(to_json(reports))
    else:
        out_path = Path(output)
        if format == "json":
            out_path.write_text(to_json(reports))
        elif format == "csv":
            out_path.write_text(to_csv(reports))
        elif format == "html":
            out_path.write_text(to_html(reports))
        elif format == "pdf":
            html_content = to_html(reports)
            to_pdf(html_content, output)
        typer.secho(f"Report written to {output}", fg="green")


@annotate_cli.command("direct")
def annotate_direct(
    gene: str = typer.Argument(..., help="Gene symbol"),
    allele1: str = typer.Argument(..., help="Allele on chromosome 1 (e.g. *2)"),
    allele2: str = typer.Argument(..., help="Allele on chromosome 2 (e.g. *1)"),
    drug: Optional[str] = typer.Option(None, "--drug", "-d", help="Drug to check dosing for"),
    drugs: Optional[str] = typer.Option(None, "--drugs", help="Comma-separated list of drugs"),
    sample_id: str = typer.Option("SAMPLE001", "--sample-id", "-s", help="Sample ID"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file"),
    format: str = typer.Option("json", "--format", "-f", help="Output format"),
):
    """Interpret known allele pair directly (no VCF needed).

    Example:
        pgxrx annotate direct CYP2C19 \\*2 \\*1 --drug clopidogrel
    """
    drug_list = []
    if drug:
        drug_list.append(normalize_drug_name(drug))
    if drugs:
        drug_list.extend(normalize_drug_name(d.strip()) for d in drugs.split(","))

    engine = PGxEngine()
    report = engine.interpret_direct(
        gene=gene, allele1=allele1, allele2=allele2,
        drugs=drug_list, sample_id=sample_id,
    )

    output_content = to_json([report], fmt=format)
    if output:
        Path(output).write_text(output_content)
        typer.secho(f"Report written to {output}", fg="green")
    else:
        typer.echo(output_content)


# ── phenotype subcommand group ────────────────────────────────────────
phenotype_cli = typer.Typer(
    add_help_option=True,
    help="Determine CPIC phenotype from diplotypes",
)
cli.add_typer(phenotype_cli, name="phenotype")


@phenotype_cli.command()
def phenotype_check(
    gene: str = typer.Argument(..., help="Gene symbol"),
    allele1: str = typer.Argument(..., help="First allele (e.g. *2)"),
    allele2: str = typer.Argument(..., help="Second allele (e.g. *1)"),
    format: str = typer.Option("text", "--format", "-f", help="Output format (text, json)"),
):
    """Determine CPIC phenotype from a diplotype.

    Example:
        pgxrx phenotype CYP2C19 \\*2 \\*1
    """
    diplotype = compute_diplotype_from_alleles(allele1, allele2, gene)
    phenotype = determine_phenotype(diplotype)

    if format == "json":
        typer.echo(phenotype.model_dump_json(indent=2))
    else:
        typer.echo(f"Gene:        {gene}")
        typer.echo(f"Diplotype:   {diplotype}")
        typer.echo(f"Activity:    {diplotype.activity_score}")
        typer.echo(f"Phenotype:   {phenotype.phenotype}")
        typer.echo(f"Confidence:  {phenotype.confidence}")


# ── dose subcommand group ─────────────────────────────────────────────
dose_cli = typer.Typer(
    add_help_option=True,
    help="Get dosing recommendations",
)
cli.add_typer(dose_cli, name="dose")


@dose_cli.command()
def dose_check(
    drug: str = typer.Argument(..., help="Drug name"),
    gene: str = typer.Argument(..., help="Gene symbol"),
    phenotype: str = typer.Argument(..., help="Phenotype (e.g. 'Poor Metabolizer')"),
    format: str = typer.Option("text", "--format", "-f", help="Output format (text, json)"),
):
    """Get CPIC dosing recommendation for drug-gene-phenotype.

    Example:
        pgxrx dose clopidogrel CYP2C19 "Intermediate Metabolizer"
    """
    rec = get_dosing_recommendation(drug, gene, phenotype)
    if rec is None:
        typer.echo(f"No guideline found for {drug} + {gene}", err=True)
        raise typer.Exit(1)

    if format == "json":
        typer.echo(rec.model_dump_json(indent=2))
    else:
        typer.echo(f"Drug:        {rec.drug}")
        typer.echo(f"Gene:        {rec.gene}")
        typer.echo(f"Phenotype:   {rec.phenotype}")
        typer.echo(f"Evidence:    {rec.evidence_level}")
        typer.echo(f"Guideline:   {rec.guideline_version}")
        typer.echo(f"Recommendation:")
        typer.echo(f"  {rec.recommendation}")


@dose_cli.command("list")
def list_drugs(
    gene: Optional[str] = typer.Option(None, "--gene", "-g", help="Filter by gene"),
):
    """List all supported drug-gene pairs.

    Example:
        pgxrx dose list --gene CYP2C19
    """
    from pgxrx.core.dosing import _DRUG_GENE_GUIDELINES

    pairs = list(_DRUG_GENE_GUIDELINES.keys())
    if gene:
        pairs = [(d, g) for d, g in pairs if g == gene]

    if not pairs:
        typer.echo("No drug-gene pairs found.", err=True)
        raise typer.Exit(1)

    typer.echo(f"{'Drug':<25} {'Gene':<15}")
    typer.echo("-" * 40)
    for drug, gene in sorted(pairs):
        typer.echo(f"{drug:<25} {gene:<15}")


# ── report subcommand group ───────────────────────────────────────────
report_cli = typer.Typer(
    add_help_option=True,
    help="Generate clinical reports",
)
cli.add_typer(report_cli, name="report")


@report_cli.command()
def generate_report(
    input_file: str = typer.Argument(..., help="Input JSON report file"),
    output: str = typer.Option("report.html", "--output", "-o", help="Output file"),
    format: str = typer.Option("html", "--format", "-f", help="Format (json, csv, html, pdf)"),
    patient_name: str = typer.Option("Unknown", "--patient", "-p", help="Patient name"),
):
    """Generate a clinical report from a JSON interpretation file.

    Example:
        pgxrx report results.json -o report.html -f html
        pgxrx report results.json -o report.pdf -f pdf
    """
    import json as _json

    with open(input_file) as f:
        data = _json.load(f)

    output_path = Path(output)
    if format == "json":
        output_path.write_text(json.dumps(data, indent=2))
    elif format == "csv":
        from pgxrx.core.variant import InterpretationReport
        reports = [InterpretationReport(**item) for item in data]
        output_path.write_text(to_csv(reports))
    elif format == "html":
        from pgxrx.core.variant import InterpretationReport
        reports = [InterpretationReport(**item) for item in data]
        output_path.write_text(to_html(reports, patient_name=patient_name))
    elif format == "pdf":
        from pgxrx.core.variant import InterpretationReport
        reports = [InterpretationReport(**item) for item in data]
        html = to_html(reports, patient_name=patient_name)
        to_pdf(html, output)
    else:
        typer.echo(f"Unknown format: {format}", err=True)
        raise typer.Exit(1)

    typer.secho(f"Report written to {output}", fg="green")


# ── batch ─────────────────────────────────────────────────────────────
@cli.command()
def batch(
    vcf_dir: str = typer.Argument(..., help="Directory with VCF files"),
    drug: Optional[str] = typer.Option(None, "--drug", "-d", help="Drug to check"),
    output_dir: str = typer.Option("batch_results", "--output-dir", "-o", help="Output directory"),
    format: str = typer.Option("json", "--format", "-f", help="Output format"),
):
    """Batch process multiple VCF files.

    Example:
        pgxrx batch ./samples --drug clopidogrel -o results
    """
    drug_list = [normalize_drug_name(drug)] if drug else []
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    vcf_files = list(Path(vcf_dir).glob("*.vcf")) + list(Path(vcf_dir).glob("*.vcf.gz"))
    if not vcf_files:
        typer.echo(f"No VCF files found in {vcf_dir}", err=True)
        raise typer.Exit(1)

    engine = PGxEngine()
    results = []
    for vcf_path in vcf_files:
        sid = vcf_path.stem
        variants = parse_vcf(vcf_path, sample_id=sid)
        reports = engine.interpret(variants, drugs=drug_list, sample_id=sid)
        results.append({"sample": sid, "file": str(vcf_path), "reports": reports})

        # Write individual report
        if format == "json":
            (out_dir / f"{sid}.json").write_text(to_json(reports))
        elif format == "csv":
            (out_dir / f"{sid}.csv").write_text(to_csv(reports))

    typer.secho(f"Processed {len(vcf_files)} files → {out_dir}", fg="green")


# ── update ────────────────────────────────────────────────────────────
@cli.command()
def update():
    """Check and update knowledge base data."""
    from pgxrx.data.update import update_knowledge_base
    data_dir = Path(__file__).parent.parent.parent / "data"
    status = update_knowledge_base(data_dir)
    typer.echo(json.dumps(status, indent=2))


# ── serve ─────────────────────────────────────────────────────────────
@cli.command()
def serve(
    host: str = typer.Option("127.0.0.1", "--host", help="Host to bind"),
    port: int = typer.Option(8000, "--port", help="Port to listen on"),
    reload: bool = typer.Option(True, "--reload", help="Auto-reload on file changes"),
):
    """Start the FastAPI web server.

    Example:
        pgxrx serve --host 0.0.0.0 --port 8000
    """
    try:
        import uvicorn
    except ImportError:
        typer.echo("FastAPI dependencies not installed. Run: pip install pgxrx[api]", err=True)
        raise typer.Exit(1)

    typer.secho(f"Starting PGxRx API server on {host}:{port}", fg="cyan")
    uvicorn.run("pgxrx.api.server:app", host=host, port=port, reload=reload)


# ── genes/drugs listing ───────────────────────────────────────────────
@cli.command()
def genes():
    """List all supported PGx genes."""
    engine = PGxEngine()
    all_genes = engine.mapper.get_all_genes()
    for g in sorted(all_genes):
        typer.echo(f"  {g}")


@cli.command()
def drugs():
    """List all supported drugs."""
    from pgxrx.core.dosing import _DRUG_GENE_GUIDELINES
    seen = set()
    for drug, gene in sorted(_DRUG_GENE_GUIDELINES.keys()):
        if drug not in seen:
            typer.echo(f"  {drug}")
            seen.add(drug)
