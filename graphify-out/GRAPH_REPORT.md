# Graph Report - .  (2026-06-26)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 459 nodes · 827 edges · 24 communities (20 shown, 4 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 79 edges (avg confidence: 0.53)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 19|Community 19]]
- [[_COMMUNITY_Community 20|Community 20]]
- [[_COMMUNITY_Community 21|Community 21]]

## God Nodes (most connected - your core abstractions)
1. `Variant` - 50 edges
2. `PGxEngine` - 41 edges
3. `compute_diplotype_from_alleles()` - 40 edges
4. `determine_phenotype()` - 31 edges
5. `Diplotype` - 27 edges
6. `InterpretationReport` - 27 edges
7. `get_dosing_recommendation()` - 26 edges
8. `AlleleCall` - 26 edges
9. `AlleleMapper` - 19 edges
10. `PhenotypeResult` - 19 edges

## Surprising Connections (you probably didn't know these)
- `TestAlleleMapper` --uses--> `AlleleMapper`  [INFERRED]
  tests/test_allele_mapper.py → pgxrx/core/allele_mapper.py
- `TestFullPipelineDirect` --uses--> `PGxEngine`  [INFERRED]
  tests/test_full_pipeline.py → pgxrx/core/engine.py
- `TestFullPipelineVCF` --uses--> `PGxEngine`  [INFERRED]
  tests/test_full_pipeline.py → pgxrx/core/engine.py
- `TestPipelineVariance` --uses--> `PGxEngine`  [INFERRED]
  tests/test_full_pipeline.py → pgxrx/core/engine.py
- `TestCSVReport` --uses--> `PGxEngine`  [INFERRED]
  tests/test_reports.py → pgxrx/core/engine.py

## Import Cycles
- None detected.

## Communities (24 total, 4 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.07
Nodes (32): Variant-to-allele mapper using PharmVar allele nomenclature.  Maps variant coord, Map a single variant to an allele call.          Returns None if the variant doe, Map a list of variants grouped by gene.          Returns {gene: [AlleleCall, ..., Interpret directly from known alleles (no VCF needed).          Useful for manua, Step 1: Map variants to allele calls, grouped by gene., Step 2: Compute diplotype for a gene., Step 3: Determine phenotype from diplotype., Step 4: Get dosing recommendation. (+24 more)

### Community 1 - "Community 1"
Cohesion: 0.07
Nodes (22): compute_diplotype(), compute_diplotype_from_alleles(), _get_activity(), Diplotype calculator.  Combines allele calls from two chromosomes into a diploty, Compute diplotype directly from two allele names., Look up activity score for a gene-allele pair., Compute diplotype from allele calls on two chromosomes.      Parameters     ----, determine_phenotype() (+14 more)

### Community 2 - "Community 2"
Cohesion: 0.07
Nodes (20): get_all_guidelines(), get_dosing_recommendation(), get_drug_genes(), get_gene_drugs(), CPIC dosing recommendation engine.  Maps (drug, gene, phenotype) → dosing recomm, Return genes associated with a drug., Return drugs associated with a gene., Look up CPIC dosing recommendation for a drug-gene-phenotype triple.      Parame (+12 more)

### Community 3 - "Community 3"
Cohesion: 0.08
Nodes (17): _find_gene(), _normalize_chrom(), _normalize_variant(), parse_vcf(), VCF 4.2/4.3 parser using cyvcf2 (C-backed, fast).  Filters to PGx-relevant gene, Read VCF lines (plain or gzip) and yield parsed columns.      Returns list of [c, Normalize chromosome naming: 'chr10' → '10', 'chrX' → 'X'., Find PGx gene at a given coordinate. (+9 more)

### Community 4 - "Community 4"
Cohesion: 0.09
Nodes (30): annotate(), AnnotateRequest, AnnotateResponse, dose(), DoseRequest, DoseResponse, DrugInfo, GeneInfo (+22 more)

### Community 5 - "Community 5"
Cohesion: 0.08
Nodes (10): Tests for the full PGx pipeline (engine)., CYP2C19 *1/*2 + clopidogrel → IM, recommend alternative., CYP2C19 *1/*1 + clopidogrel → NM, no change., CYP2C19 *2/*2 + clopidogrel → PM, avoid., Without drugs, no dosing recommendations., Multiple drugs should produce multiple dosing entries., Full pipeline from VCF parsing to interpretation., TestFullPipelineDirect (+2 more)

### Community 6 - "Community 6"
Cohesion: 0.10
Nodes (19): Pytest configuration and shared fixtures for PGxRx tests., Temporary directory for report outputs., Path to test CYP2C19 VCF., Path to test CYP2D6 VCF., Path to test CYP2C9 VCF., Path to multi-gene test VCF., Path to DPYD test VCF., A CYP2C19 *2 variant (rs4244285). (+11 more)

### Community 7 - "Community 7"
Cohesion: 0.10
Nodes (5): Tests for data layer (database, loaders, RxNorm)., TestDatabase, TestDataLoaders, TestRxNorm, TestUpdate

### Community 8 - "Community 8"
Cohesion: 0.16
Nodes (10): get_genome_build(), liftover_coordinate(), _liftover_pysam(), Genome build coordinate conversion (GRCh37 ↔ GRCh38).  Uses pysam for liftOver w, Try to detect genome build from VCF header., Lift over a single coordinate between genome builds.      Parameters     -------, LiftOver using pysam (requires chain files)., Tests for genome build coordinate conversion. (+2 more)

### Community 9 - "Community 9"
Cohesion: 0.11
Nodes (7): Tests for allele mapper., rs4244285 should map to CYP2C19*2., rs16947 should map to CYP2D6*2., Unknown rsID should return None., Variant without rsID should return None., Multiple variants should be grouped by gene., TestAlleleMapper

### Community 10 - "Community 10"
Cohesion: 0.11
Nodes (6): Tests for FastAPI server., TestAnnotateEndpoint, TestDoseEndpoint, TestListEndpoints, TestPhenotypeEndpoint, TestRootEndpoint

### Community 11 - "Community 11"
Cohesion: 0.12
Nodes (14): _common_callback(), dose_check(), drugs(), genes(), list_drugs(), PGxRx CLI - Typer-based command-line interface.  Subcommands:   annotate   - Map, Get CPIC dosing recommendation for drug-gene-phenotype.      Example:         pg, List all supported drug-gene pairs.      Example:         pgxrx dose list --gene (+6 more)

### Community 12 - "Community 12"
Cohesion: 0.14
Nodes (11): AlleleMapper, Map variants to PharmVar allele symbols., Get activity score for a specific gene+allele., Return all genes with allele definitions., Return all alleles for a gene., PGxEngine, Orchestrator — full PGx pipeline.  VCF → Variants → Alleles → Diplotypes → Pheno, Full PGx interpretation pipeline.      Usage     -----     >>> engine = PGxEngin (+3 more)

### Community 13 - "Community 13"
Cohesion: 0.17
Nodes (8): CSV report generation., Serialize interpretation reports to CSV string., Write CSV report to file., to_csv(), to_csv_file(), Tests for report generation., TestCSVReport, TestMultipleReports

### Community 14 - "Community 14"
Cohesion: 0.18
Nodes (10): _allele_desc(), _phenotype_class(), HTML report generation with Jinja2 templates., Generate HTML report from interpretation reports.      Parameters     ----------, Map phenotype to CSS class., Get allele description from bundled data., Write HTML report to file., to_html() (+2 more)

### Community 15 - "Community 15"
Cohesion: 0.25
Nodes (6): JSON report generation., Serialize interpretation reports to JSON string., Write JSON report to file., to_json(), to_json_file(), TestJSONReport

### Community 16 - "Community 16"
Cohesion: 0.20
Nodes (9): _load_alleles_data(), Load allele definitions from bundled JSON or return built-in data., Path, annotate_direct(), batch(), Interpret known allele pair directly (no VCF needed).      Example:         pgxr, Batch process multiple VCF files.      Example:         pgxrx batch ./samples --, Check and update knowledge base data. (+1 more)

### Community 17 - "Community 17"
Cohesion: 0.25
Nodes (7): annotate_vcf(), generate_report(), Generate a clinical report from a JSON interpretation file.      Example:, Annotate VCF variants and produce full interpretation.      Reads a VCF file, ma, PDF report generation using WeasyPrint., Generate PDF report from HTML content using WeasyPrint.      Parameters     ----, to_pdf()

## Knowledge Gaps
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `PGxEngine` connect `Community 12` to `Community 0`, `Community 4`, `Community 5`, `Community 6`, `Community 11`, `Community 13`, `Community 14`, `Community 15`, `Community 16`, `Community 17`?**
  _High betweenness centrality (0.220) - this node is a cross-community bridge._
- **Why does `Variant` connect `Community 0` to `Community 3`, `Community 4`, `Community 5`, `Community 6`, `Community 9`, `Community 12`?**
  _High betweenness centrality (0.208) - this node is a cross-community bridge._
- **Why does `get_dosing_recommendation()` connect `Community 2` to `Community 0`, `Community 11`, `Community 4`, `Community 12`?**
  _High betweenness centrality (0.108) - this node is a cross-community bridge._
- **Are the 17 inferred relationships involving `Variant` (e.g. with `AlleleMapper` and `PGxEngine`) actually correct?**
  _`Variant` has 17 INFERRED edges - model-reasoned connections that need verification._
- **Are the 22 inferred relationships involving `PGxEngine` (e.g. with `AnnotateRequest` and `AnnotateResponse`) actually correct?**
  _`PGxEngine` has 22 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `Diplotype` (e.g. with `PGxEngine` and `TestDiplotypeComputation`) actually correct?**
  _`Diplotype` has 8 INFERRED edges - model-reasoned connections that need verification._
- **What connects `PGxRx - Pharmacogenomics Prescription Decision Tool.  A command-line tool that t`, `Entry point for `python -m pgxrx`.`, `PGxRx REST API - FastAPI server.` to the rest of the system?**
  _124 weakly-connected nodes found - possible documentation gaps or missing edges._