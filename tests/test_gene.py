"""
Unit tests for HGNC gene ingest
"""

from unittest.mock import MagicMock

import pytest
from biolink_model.datamodel.pydanticmodel_v2 import Gene
from koza.transform import KozaTransform

from gene import transform_record


@pytest.fixture
def hgnc_so_terms_mapping():
    return {
        "hgnc_so_terms": {
            "HGNC:24086": {
                "gene_id": "HGNC:24086",
                "so_term_id": "SO:0001217",
            },
        },
    }


@pytest.fixture
def koza_transform_with_mapping(hgnc_so_terms_mapping):
    return KozaTransform(
        extra_fields={},
        writer=MagicMock(),
        mappings=hgnc_so_terms_mapping,
    )


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
def a1cf_gene(a1cf_row, koza_transform_with_mapping):
    return transform_record(koza_transform_with_mapping, a1cf_row)


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


def test_gene_so_term(a1cf_gene):
    """Test that a gene with a mapping gets the correct SO term type"""
    gene = a1cf_gene[0]
    assert gene.type == ["SO:0001217"]


def test_gene_with_multiple_omim_ids(koza_transform_with_mapping):
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

    genes = transform_record(koza_transform_with_mapping, row)
    gene = genes[0]

    assert gene.xref
    assert "OMIM:123456" in gene.xref
    assert "OMIM:789012" in gene.xref


def test_gene_without_mapping():
    """Test that a gene without a mapping gets type=None"""
    row = {
        "hgnc_id": "HGNC:99999",
        "pubmed_id": "",
        "symbol": "UNMAPPED",
        "name": "unmapped gene",
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
    assert gene.type is None


def test_gene_with_no_xrefs(koza_transform_with_mapping):
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

    genes = transform_record(koza_transform_with_mapping, row)
    gene = genes[0]

    assert gene.id == "HGNC:99999"
    assert gene.symbol == "MINIMAL"
    assert gene.xref is None
    assert gene.synonym is None
