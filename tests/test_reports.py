"""Tests for report generation."""

import pytest

from pgxrx.core.engine import PGxEngine
from pgxrx.reports.json_report import to_json
from pgxrx.reports.csv_report import to_csv
from pgxrx.reports.html_report import to_html


@pytest.fixture
def sample_report(engine):
    return engine.interpret_direct(
        gene="CYP2C19",
        allele1="*2",
        allele2="*1",
        drugs=["clopidogrel"],
        sample_id="TEST001",
    )


class TestJSONReport:
    def test_produces_valid_json(self, sample_report):
        json_str = to_json([sample_report])
        import json
        data = json.loads(json_str)
        assert len(data) == 1
        assert data[0]["gene"] == "CYP2C19"

    def test_json_has_phenotype(self, sample_report):
        import json
        data = json.loads(to_json([sample_report]))
        assert data[0]["phenotype"] is not None

    def test_json_has_dosing(self, sample_report):
        import json
        data = json.loads(to_json([sample_report]))
        assert len(data[0]["dosing"]) > 0

    def test_json_has_sample_id(self, sample_report):
        import json
        data = json.loads(to_json([sample_report]))
        assert data[0]["sample_id"] == "TEST001"


class TestCSVReport:
    def test_produces_csv(self, sample_report):
        csv_str = to_csv([sample_report])
        lines = csv_str.strip().split("\n")
        assert len(lines) >= 2  # header + at least 1 data row

    def test_csv_has_header(self, sample_report):
        csv_str = to_csv([sample_report])
        first_line = csv_str.split("\n")[0]
        assert "sample_id" in first_line
        assert "gene" in first_line

    def test_csv_has_data(self, sample_report):
        csv_str = to_csv([sample_report])
        assert "CYP2C19" in csv_str


class TestHTMLReport:
    def test_produces_html(self, sample_report):
        html = to_html([sample_report])
        assert "<html" in html or "<!DOCTYPE" in html
        assert "CYP2C19" in html

    def test_html_has_phenotype(self, sample_report):
        html = to_html([sample_report])
        assert "Intermediate" in html

    def test_html_has_recommendation(self, sample_report):
        html = to_html([sample_report])
        assert "clopidogrel" in html.lower()

    def test_html_patient_name(self, sample_report):
        html = to_html([sample_report], patient_name="John Doe")
        assert "John Doe" in html

    def test_html_has_disclaimer(self, sample_report):
        html = to_html([sample_report])
        assert "clinical" in html.lower() or "disclaimer" in html.lower()


class TestMultipleReports:
    def test_multiple_genes_json(self, engine):
        reports = [
            engine.interpret_direct("CYP2C19", "*2", "*1", drugs=["clopidogrel"]),
            engine.interpret_direct("CYP2D6", "*1", "*1", drugs=["codeine"]),
        ]
        import json
        data = json.loads(to_json(reports))
        assert len(data) == 2

    def test_multiple_genes_csv(self, engine):
        reports = [
            engine.interpret_direct("CYP2C19", "*2", "*1"),
            engine.interpret_direct("CYP2D6", "*1", "*1"),
        ]
        csv_str = to_csv(reports)
        assert "CYP2C19" in csv_str
        assert "CYP2D6" in csv_str
