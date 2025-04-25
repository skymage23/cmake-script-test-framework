import importlib
import sys
import os
import unittest

import common
from cmake_local import cmake_helper
from cmake_local.language_parsing import cmake_var_expander

class AugmentedCmakeScriptContext(cmake_helper.CMakeScriptContext):
    def __init__(self):
        # Create temporary files/directories for testing
        super().__init__(
            list_file="tests/test.cmake",
            build_dir="build",
            source_dir="source",
            project_source_dir="project"
        )
        self.var_dict = {}

    def setVariable(self, varname: str, value: str, is_env_var = False):
        if not is_env_var:
            self.var_dict[varname] = value
        else:
            os.environ[varname] = value
    
    def unsetVariable(self, varname: str, is_env_var = False):
        if not is_env_var:
            self.var_dict.pop(varname, None)
        else:
            os.environ.pop(varname, None)

    def resolve_var(self, varname, is_env_var):
        retval = None
        if is_env_var:
            retval = os.environ.get(varname, "")
        
        if retval is None:
            retval = super().resolve_var(varname, is_env_var)

        if retval is None:
            try:
                retval = self.var_dict[varname]
            except:
                retval = ""
        return retval

#class TestVarExpansionParsing(common.TestCaseWrapper):
#    def setUp(self):
#        super().setUp()
#        self.context = AugmentedCmakeScriptContext()
#        self.var_expander = cmake_var_expander.CMakeVarExpander(context = self.context)
#    
#    def test_char_string_passthrough(self):
#        input = "The quick brown fox jumps over the lazy dog"
#        if self.use_breakpoint:
#            breakpoint()
#        output = self.var_expander.resolve_vars(input)
#        self.assertEqual(input, output)
#
#    def test_line_encompassing_basic_var_expansion(self):
#        input = "${CMAKE_CURRENT_LIST_DIR}"
#        if self.use_breakpoint:
#            breakpoint()
#        output = self.var_expander.resolve_vars(input)
#        self.assertEqual(output, "tests")
        
class TestVarExpansionResolution(common.TestCaseWrapper):
    def setUp(self):
        super().setUp()
        self.context = AugmentedCmakeScriptContext()
    
    def test_char_string_passthrough(self):
        input = "The quick brown fox jumps over the lazy dog"
        if self.use_breakpoint:
            breakpoint()
        output = cmake_var_expander.resolve_vars(input, self.context)
        self.assertEqual(input, output)

    def test_line_encompassing_basic_var_expansion(self):
        input = "${CMAKE_CURRENT_LIST_DIR}"
        if self.use_breakpoint:
            breakpoint()
        output = cmake_var_expander.resolve_vars(input, self.context)
        self.assertEqual(output, "tests")

    def test_multiple_var_expansion(self):
        input = "${CMAKE_CURRENT_LIST_DIR}/${CMAKE_CURRENT_LIST_FILE}"
        if self.use_breakpoint:
            breakpoint()
        output = cmake_var_expander.resolve_vars(input, self.context)
        self.assertEqual(output, "tests/tests/test.cmake")

    def test_environ_var_expansion(self):
        self.context.setVariable("TEST_ENV_VAR", "tests", is_env_var = True)
        input = "$ENV{TEST_ENV_VAR}"
        if self.use_breakpoint:
            breakpoint()
        output = cmake_var_expander.resolve_vars(input, self.context)
        self.context.unsetVariable("TEST_ENV_VAR", is_env_var = True)
        self.assertEqual(output, "tests")
        
        

    def test_mixed_cmake_and_environ_var_expansion(self):
        self.context.setVariable("TEST_ENV_VAR", "tests", is_env_var = True)
        input = "${CMAKE_CURRENT_LIST_DIR}/$ENV{TEST_ENV_VAR}"
        if self.use_breakpoint:
            breakpoint()
        output = cmake_var_expander.resolve_vars(input, self.context)
        self.context.unsetVariable("TEST_ENV_VAR", is_env_var = True)
        self.assertEqual(output, "tests/tests")

    def test_nested_var_expansion(self):
        self.context.setVariable("TEST_ENV_VAR", "DIR", is_env_var = True)
        input = "${CMAKE_CURRENT_LIST_$ENV{TEST_ENV_VAR}}"
        if self.use_breakpoint:
            breakpoint()
        output = cmake_var_expander.resolve_vars(input, self.context)
        self.context.unsetVariable("TEST_ENV_VAR", is_env_var = True)
        self.assertEqual(output, "tests")

    def test_triple_depth_nested_var_expansion(self):
        self.context.setVariable("TEST_ENV_VAR", "DIR", is_env_var = True)
        self.context.setVariable("TEST_ENV_VAR2", "VAR", is_env_var = True)
        input = "${CMAKE_CURRENT_LIST_$ENV{TEST_ENV_$ENV{TEST_ENV_VAR2}}}"
        if self.use_breakpoint:
            breakpoint()
        output = cmake_var_expander.resolve_vars(input, self.context)
        self.context.unsetVariable("TEST_ENV_VAR", is_env_var = True)
        self.context.unsetVariable("TEST_ENV_VAR2", is_env_var = True)
        self.assertEqual(output, "tests")

    def test_consecutive_nested_var_expansions(self):
        self.context.setVariable("TEST_ENV_VAR", "pudding", is_env_var = True)
        input = "${CMAKE_CURRENT_LIST_DIR}_$ENV{TEST_ENV_VAR}"
        if self.use_breakpoint:
            breakpoint()
        output = cmake_var_expander.resolve_vars(input, self.context)
        self.context.unsetVariable("TEST_ENV_VAR", is_env_var = True)
        self.assertEqual(output, "tests_pudding")

    def test_nonexistent_var_expansion(self):
        #We should expect an error here.
        pass

    def test_nonexistant_env_var_expansion(self):
        self.context.setVariable("TEST_ENV_VAR", "pudding", is_env_var = True)
        input = "${CMAKE_CURRENT_LIST_DIR}_$ENV{TEST_ENV_VAR}"
        if self.use_breakpoint:
            breakpoint()
        output = cmake_var_expander.resolve_vars(input, self.context)
        self.context.unsetVariable("TEST_ENV_VAR", is_env_var = True)
        self.assertEqual(output, "tests_pudding")
    def test_nested_mixed_cmake_and_environ_var_expansion_outer_is_cmake_var(self):
        pass

    def test_nested_mixed_cmake_and_environ_var_expansion_outer_is_environ_var(self):
        pass