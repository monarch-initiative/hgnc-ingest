"""
Unit tests for HGNC gene ingest
"""

import pytest
from biolink_model.datamodel.pydanticmodel_v2 import Gene

from gene import transform_record


@pytest.fixture
def a1cf_row():
    return {
        "hgnc_id": "HGNC:24086",
        "pubmed_id": "11072063",
        "symbol": "A1CF",
        "name": "APOBEC1 complementation factor",
        "ensembl_gene_id": "ENSG00000148584",
        "omim_id": "618199",
        "alias_symbol": "ACF|ASP|ACF64|ACF65|APOBEC1CF",
        "alias_name": "",
        "prev_symbol": "",
        "prev_name": "",
    }


@pytest.fixture
def a1cf_gene(a1cf_row):
    return transform_record(None, a1cf_row)


def test_gene_id(a1cf_gene):
    gene = a1cf_gene[0]
    assert gene
    assert isinstance(gene, Gene)
    assert gene.id == "HGNC:24086"


def test_gene_symbol(a1cf_gene):
    gene = a1cf_gene[0]
    assert gene.symbol == "A1CF"
    assert gene.name == "A1CF"


def test_gene_full_name(a1cf_gene):
    gene = a1cf_gene[0]
    assert gene.full_name == "APOBEC1 complementation factor"


def test_gene_taxon(a1cf_gene):
    gene = a1cf_gene[0]
    assert gene.in_taxon == ["NCBITaxon:9606"]
    assert gene.in_taxon_label == "Homo sapiens"


def test_gene_provided_by(a1cf_gene):
    gene = a1cf_gene[0]
    assert gene.provided_by == ["infores:hgnc"]


def test_gene_synonym(a1cf_gene):
    gene = a1cf_gene[0]
    assert gene.synonym
    # Synonyms are parsed from pipe-delimited fields and empty strings filtered
    assert gene.synonym == ["ACF", "ASP", "ACF64", "ACF65", "APOBEC1CF"]


def test_gene_xref(a1cf_gene):
    gene = a1cf_gene[0]
    assert gene.xref
    assert "ENSEMBL:ENSG00000148584" in gene.xref
    assert "OMIM:618199" in gene.xref


def test_gene_with_multiple_omim_ids():
    """Test handling of multiple OMIM IDs separated by pipe"""
    row = {
        "hgnc_id": "HGNC:12345",
        "pubmed_id": "",
        "symbol": "TEST",
        "name": "test gene",
        "ensembl_gene_id": "",
        "omim_id": "123456|789012",
        "alias_symbol": "",
        "alias_name": "",
        "prev_symbol": "",
        "prev_name": "",
    }

    genes = transform_record(None, row)
    gene = genes[0]

    assert gene.xref
    assert "OMIM:123456" in gene.xref
    assert "OMIM:789012" in gene.xref


def test_gene_with_no_xrefs():
    """Test handling of gene without xrefs"""
    row = {
        "hgnc_id": "HGNC:99999",
        "pubmed_id": "",
        "symbol": "MINIMAL",
        "name": "minimal gene",
        "ensembl_gene_id": "",
        "omim_id": "",
        "alias_symbol": "",
        "alias_name": "",
        "prev_symbol": "",
        "prev_name": "",
    }

    genes = transform_record(None, row)
    gene = genes[0]

    assert gene.id == "HGNC:99999"
    assert gene.symbol == "MINIMAL"
    assert gene.xref is None
    assert gene.synonym is None
