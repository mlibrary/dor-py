from behave import given, then, when

from dataclasses import dataclass
from typing import Any

@dataclass
class Bin:
    identifier: str
    alternate_identifiers: list[str] 
    common_metadata: dict[str, Any]


class Catalog:
    def __init__(self):
        self.bins = []
        
    def add(self, bin):
        self.bins.append(bin)
        
    def get(self, identifier):
        for bin in self.bins:
            if bin.identifier == identifier:
                return bin 
        return None
    
    def get_by_alternate_identifier(self, identifier):
        for bin in self.bins:
            if identifier in bin.alternate_identifiers:
                return bin 
        return None
        

@given(u'a preserved monograph with an alternate identifier of "{alt_id}"')
def step_impl(context, alt_id):
    bin = Bin(
        identifier="00000000-0000-0000-0000-000000000001", 
        alternate_identifiers=[alt_id], 
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
    context.catalog = Catalog()
    context.catalog.add(bin)

@when(u'the Collection Manager looks up the bin by "{alt_id}"')
def step_impl(context, alt_id):
    context.alt_id = alt_id
    context.bin = context.catalog.get_by_alternate_identifier(alt_id)

@then(u'the Collection Manager sees the summary of the bin')
def step_impl(context):
    assert context.bin == Bin(
        identifier="00000000-0000-0000-0000-000000000001", 
        alternate_identifiers=[context.alt_id], 
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

@when(u'the Collection Manager lists the contents of the bin')
def step_impl(context):
    raise NotImplementedError(u'STEP: When the Collection Manager lists the contents of the bin')


@then(u'the Collection Manager sees the file sets.')
def step_impl(context):
    raise NotImplementedError(u'STEP: Then the Collection Manager sees the file sets.')