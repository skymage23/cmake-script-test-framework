import importlib
import sys
import os
import unittest


import common

sys.path.append(common.scripts_dir.__str__())
cmake_helper = importlib.import_module("cmake.cmake_helper")
var_parsing = importlib.import_module("cmake.language_parsing.var_expansion_parsing")

class AugmentedCmakeScriptContext(cmake_helper.CMakeScriptContext):
    def __init__(self):
        super().__init__()
        self.var_dict = {}

    def setVariable(self, varname: str, value: str, is_env_var = False):
        if not is_env_var:
            self.var_dict[varname] = value
        else:
            os.environ[varname] = value

    def resolve_var(self, varname, is_env_var)

class TestVarExpansionParsing(unittest.TestCase):
    def setUp(self):
        super().__init__(self)
        context = AugmentedCmakeScriptContext()
        self.parser = var_parsing.VarParser(context = context)
    
    def test_char_string_passthrough(self):
        input = "The quick brown fox jumps over the lazy dog"
        output = self.parser.resolve_all_vars(input)
        self.assertEqual(input, output)

    def test_line_encompassing_basic_var_expansion(self):
        pass

    def test_multiple_var_expansion(self):
        pass

    def test_environ_var_expansion(self):
        pass

    def test_mixed_cmake_and_environ_var_expansion(self):
        pass

    def test_nested_var_expansion(self):
        pass

    def test_triple_depth_nested_var_expansion(self):
        pass

    def test_consecutive_nested_var_expansions(self):
        pass

    def test_nested_mixed_cmake_and_environ_var_expansion_outer_is_cmake_var(self):
        pass

    def test_nested_mixed_cmake_and_environ_var_expansion_outer_is_environ_var(self):
        pass