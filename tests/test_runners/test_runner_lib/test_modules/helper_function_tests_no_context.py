import unittest

import common
import importlib
import sys

sys.path.append(common.scripts_dir.__str__())

gentestfile = importlib.import_module("generate-test-file")

class TestFileGenerationHelperNoContextTests(common.TestCaseWrapper):
    #Hello
    def test_strip_quotation_marks(self):
        input="\"Stranglewood\""
        output = gentestfile.strip_quotation_marks(input)
        self.assertEqual(output, "Stranglewood")

    def test_remove_cmake_escape_sequences(self):
        input = R"\MyFilePath\ DumbPathWithPreceedingSpace"
        output = gentestfile.remove_cmake_escape_sequences(input)
        self.assertEqual(output, R"\\MyFilePath\\\ DumbPathWithPreceedingSpace")

