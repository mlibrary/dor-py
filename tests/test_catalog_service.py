import os
import uuid

import pytest

from dor.service_layer.catalog_service import summarize, BinSummary
from dor.domain.models import Bin

@pytest.fixture
def sample_bin() -> Bin:
    return Bin(
        identifier=uuid.UUID("00000000-0000-0000-0000-000000000001"), 
        alternate_identifiers=["xyzzy:00000001"], 
        common_metadata={
            "@schema": "urn:umich.edu:dor:schema:common",
            "title": "Discussion also Republican owner hot already itself.",
            "author": "Kimberly Garza",
            "publication_date": "1989-04-16",
            "subjects": [
                "Liechtenstein",
                "Vietnam",
                "San Bartolomeo",
                "Bangladesh",
                "Liberia",
                "Mus musculus",
                "Schizosaccharomyces pombe",
                "Caenorhabditis elegans",
                "Drosophila melanogaster",
                "Xenopus laevis"
            ]
        }
    ) 


def test_catalog_generates_summary(sample_bin) -> BinSummary:
    expected_summary = BinSummary(
        identifier=sample_bin.identifier,
        alternate_identifiers=sample_bin.alternate_identifiers,
        common_metadata=sample_bin.common_metadata,
    )
    summary = summarize(sample_bin)
    assert expected_summary == summary
