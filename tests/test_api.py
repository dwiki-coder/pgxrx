"""Tests for FastAPI server."""

import pytest
from fastapi.testclient import TestClient

from pgxrx.api.server import app

client = TestClient(app)


class TestRootEndpoint:
    def test_health_check(self):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["service"] == "PGxRx API"
        assert data["status"] == "healthy"

    def test_serves_ui(self):
        resp = client.get("/")
        assert resp.status_code == 200
        assert "PGxRx" in resp.text
        assert "text/html" in resp.headers.get("content-type", "")


class TestAnnotateEndpoint:
    def test_annotate_cyp2c19(self):
        resp = client.post("/annotate", json={
            "gene": "CYP2C19",
            "allele1": "*2",
            "allele2": "*1",
            "drugs": ["clopidogrel"],
            "sample_id": "API001",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["gene"] == "CYP2C19"
        assert data["phenotype"] == "Intermediate Metabolizer"
        assert len(data["dosing"]) > 0

    def test_annotate_cyp2d6(self):
        resp = client.post("/annotate", json={
            "gene": "CYP2D6",
            "allele1": "*5",
            "allele2": "*5",
            "drugs": ["codeine"],
        })
        assert resp.status_code == 200
        assert resp.json()["phenotype"] == "Poor Metabolizer"


class TestPhenotypeEndpoint:
    def test_phenotype_normal(self):
        resp = client.post("/phenotype", json={
            "gene": "CYP2C19",
            "allele1": "*1",
            "allele2": "*1",
        })
        assert resp.status_code == 200
        assert resp.json()["phenotype"] == "Normal Metabolizer"

    def test_phenotype_poor(self):
        resp = client.post("/phenotype", json={
            "gene": "CYP2C19",
            "allele1": "*2",
            "allele2": "*2",
        })
        assert resp.status_code == 200
        assert resp.json()["phenotype"] == "Poor Metabolizer"


class TestDoseEndpoint:
    def test_dose_clopidogrel(self):
        resp = client.post("/dose", json={
            "drug": "clopidogrel",
            "gene": "CYP2C19",
            "phenotype": "Intermediate Metabolizer",
        })
        assert resp.status_code == 200
        assert resp.json()["drug"] == "clopidogrel"

    def test_dose_not_found(self):
        resp = client.post("/dose", json={
            "drug": "nonexistent",
            "gene": "CYP2C19",
            "phenotype": "Normal Metabolizer",
        })
        assert resp.status_code == 404


class TestListEndpoints:
    def test_list_genes(self):
        resp = client.get("/genes")
        assert resp.status_code == 200
        assert len(resp.json()) > 0

    def test_list_drugs(self):
        resp = client.get("/drugs")
        assert resp.status_code == 200
        assert len(resp.json()) > 0

    def test_gene_drugs(self):
        resp = client.get("/genes/CYP2C19/drugs")
        assert resp.status_code == 200
        assert "clopidogrel" in resp.json()

    def test_drug_genes(self):
        resp = client.get("/drugs/clopidogrel/genes")
        assert resp.status_code == 200
        assert "CYP2C19" in resp.json()
