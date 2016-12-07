import unittest
import os, sys, glob
lib_path = os.path.abspath(os.path.join('..', 'clearwater-infrastructure', 'usr', 'share', 'clearwater', 'bin'))
sys.path.append(lib_path)
from subscriber_cache_utils import explain_user_profile_xml
import xml.etree.ElementTree as ET

class TestIFCParser(unittest.TestCase):

    def test_ifc_parsing(self):
        for xml_filename in glob.iglob('./ifc_test_files/*.xml'):
            txt_filename = xml_filename.replace("xml", "txt")
            subscription_tree = ET.parse(xml_filename)
            subscription_root = subscription_tree.getroot()
            output = explain_user_profile_xml(subscription_root)
            if os.path.isfile(txt_filename):
                with open(txt_filename) as txt_file:
                    expected_output = txt_file.read()
                    self.assertEqual(output, expected_output)
            else:
                with open(txt_filename, "w") as txt_file:
                    txt_file.write(output)
                    self.assertTrue(False, msg="Output file does not exist: " +
                            txt_filename)

if __name__ == '__main__':
        unittest.main()
