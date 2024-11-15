import xml.etree.ElementTree as ET
from pathlib import Path
from unittest import TestCase

from metadata.element_adapter import ElementAdapter
from metadata.exceptions import DataNotFoundError

class ElementAdapterTest(TestCase):

    def setUp(self):
        self.namespaces = {
            "METS": "http://www.loc.gov/METS/v2",
            "PREMIS": "http://www.loc.gov/premis/v3"
        }

        fixtures_path = Path("tests/fixtures")
        test_submission_package_path = fixtures_path / "test_submission_package"
        bag_path = test_submission_package_path / "xyzzy-01929af3-dd86-7579-8c1b-6a5b6e1cd6b9-v1"
        content_path = bag_path / "data" / "xyzzy:01JADF7QC6TS22WA9AJ1SPSD0P"
        self.item_metadata_path = content_path / "descriptor"  / "xyzzy:01JADF7QC6TS22WA9AJ1SPSD0P.root.mets2.xml"
        self.item_metadata_tree = ET.fromstring(self.item_metadata_path.read_text())

        self.elem = ElementAdapter(self.item_metadata_tree, self.namespaces)

    def test_element_can_be_setup_using_text(self):
        ElementAdapter.from_string(self.item_metadata_path.read_text(), self.namespaces)

    def test_element_can_be_setup_using_element(self):
        ElementAdapter(self.item_metadata_tree, self.namespaces)

    def test_element_can_find(self):
        result = self.elem.find(".//PREMIS:eventIdentifier")
        self.assertTrue(isinstance(result, ElementAdapter))

    def test_element_raises_when_no_element_is_found(self):
        with self.assertRaises(DataNotFoundError):
            self.elem.find("NoSuchTag")

    def test_element_returns_text(self):
        elem = ElementAdapter(self.item_metadata_tree, self.namespaces)
        result = elem.find(".//PREMIS:significantPropertiesType")
        self.assertEqual("scans count", result.text)

    def test_element_raises_when_no_text_is_found(self):
        mptr_elems = self.elem.findall(".//METS:mptr")
        mptr_elem = mptr_elems[0]
        with self.assertRaises(DataNotFoundError):
            mptr_elem.text

    def test_element_can_get_attribute_value(self):
        mets_agent_elem = self.elem.find(".//METS:agent")
        role = mets_agent_elem.get("ROLE")
        self.assertEqual("CREATOR", role)

    def test_element_raises_when_no_attribute_value_is_found(self):
        mets_xml_elem = self.elem.find(".//METS:xmlData")
        with self.assertRaises(DataNotFoundError):
            mets_xml_elem.get("NOSUCHATTRIBUTE")

    def test_element_can_find_all_elements_with_tag(self):
        mptr_elems = self.elem.findall(".//METS:mptr")
        self.assertEqual(5, len(mptr_elems))
        self.assertTrue(all(isinstance(mptr_elem, ElementAdapter) for mptr_elem in mptr_elems))

    def test_element_can_provide_tag(self):
        md_sec_elem = self.elem.find("METS:mdSec")
        self.assertEqual("{http://www.loc.gov/METS/v2}mdSec", md_sec_elem.tag)

    def test_element_can_list_children(self):
        mets_header_elem = self.elem.find("METS:metsHdr")
        children = mets_header_elem.get_children()
        self.assertEqual(1, len(children))
        child = children[0]
        self.assertTrue("agent" in child.tag)
