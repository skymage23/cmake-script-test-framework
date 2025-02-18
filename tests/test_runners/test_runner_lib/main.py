#!/usr/bin/env python3
import unittest

from helper_function_tests_no_context import TestFileGenerationHelperNoContextTests
from helper_function_tests_with_context import TestHelperFunctionsRequiringContext
from test_file_generation_tests import TestFileGenerationTests

def main():
    unittest.main()

if __name__ == "__main__":
    main()