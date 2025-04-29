#These helpers require a proper context to work
import unittest

import importlib
import os
import pathlib
import sys

import common

sys.path.append(common.scripts_dir.__str__())

gentestfile = importlib.import_module("generate-test-file")
filepath_helper = importlib.import_module("filepath_helper")

class TestHelperFunctionsRequiringContext(common.TestCaseWrapper):

    def setUp(self) -> None:
        self.pretend_working_directory = common.project_base_dir
        self.pretend_source_directory = common.project_base_dir
        self.pretend_build_directory = common.project_base_dir / "build"
        args = [
            "-b",
            self.pretend_source_directory.__str__(),
            "-c",
            self.pretend_source_directory.__str__(),
            "-p",
            self.pretend_source_directory.__str__(),
            (common.test_file_dir / "test-file.cmake").__str__()
        ]
        _ , context = gentestfile.parse_args_into_context(args)
        self.app_singleton =  gentestfile.ApplicationSingleton(context)
        super().setUp()

        if self.use_breakpoint:
            breakpoint()

    def test_var_in_include_filepath(self):
        if self.use_breakpoint:
            breakpoint()
        input = R"${CMAKE_CURRENT_LIST_DIR}/test-include.cmake"
        output = self.app_singleton.context.resolve_vars(input)
        self.assertEqual(
            output, 
            (common.test_file_dir / "test-include.cmake").__str__()
        )
    
    def test_backreference_in_include_filepath(self):
        input = "/grandparent_dir/parent_dir/../test-include.cmake"
        output = filepath_helper.resolve_abs_path(input)
        expected_output_path = pathlib.Path("/grandparent_dir/test-include.cmake").resolve()
        self.assertEqual(
            output, 
            expected_output_path.__str__()
        )

    def test_backreference_after_variable(self):
        input = R"${CMAKE_CURRENT_LIST_DIR}/../test-include.cmake"
        input = self.app_singleton.context.resolve_vars(input)
        output = filepath_helper.resolve_abs_path(input)
        if self.enable_output_printing:
            print(output)
        self.assertEqual(
            output, 
            (common.test_dir / "test-include.cmake").__str__()
        )

    #Ok. This part is not going to make sense in context
    #because CMAKE_CURRENT_LIST_DIR resolves to a full, absolute
    #path. That said, we are going to leave it in because, 
    #in the future, we may support other CMake built-in
    #variables that don't behave this way, and we
    #want to be sure that our path resolution code
    #continues to work correctly.

    @unittest.skipIf(os.name == 'nt', 'Windows uses UNC pathing and drive letters, neither of which are used in non-Windows/DOS OSs.')
    def test_backreference_before_variable_posix(self):
        input = R"/grandparent_dir/parent_dir/../${CMAKE_CURRENT_LIST_DIR}/test-include.cmake"
        input = self.app_singleton.context.resolve_vars(input)
        output = filepath_helper.resolve_abs_path(input)
        #output = gentestfile.resolve_relative_include_path(input, self.app_singleton)
        expected_output = "/".join([
            "",
            "grandparent_dir",
            common.test_file_dir.__str__(),
            "test-include.cmake"
        ])
        self.assertEqual(
            output, 
            expected_output
        )

    @unittest.skipIf(os.name != 'nt', 'Windows uses UNC pathing, and here that means expecting drive letters.')
    def test_backreference_before_variable_unc(self):
        input = R"/grandparent_dir/parent_dir/../${CMAKE_CURRENT_LIST_DIR}/test-include.cmake"
        input = self.app_singleton.context.resolve_vars(input)
        output = filepath_helper.resolve_abs_path(input)
        #output = gentestfile.resolve_relative_include_path(input, self.app_singleton)
        expected_output = "\\".join([
            "C:",
            "grandparent_dir",
            common.test_file_dir.__str__(),
            "test-include.cmake"
        ])
        self.assertEqual(
            output, 
            expected_output
        )

    def test_self_reference_in_include_filepath(self):
        input = f"{common.test_file_dir.__str__()}/./test-include.cmake"
        input = self.app_singleton.context.resolve_vars(input)
        output = filepath_helper.resolve_abs_path(input)
        #output = gentestfile.resolve_relative_include_path(input, self.app_singleton)
        self.assertEqual(
            output, 
            (common.test_file_dir / "test-include.cmake").__str__()
        )

    def test_self_reference_after_variable(self):
        input = R"${CMAKE_CURRENT_LIST_DIR}/./test-include.cmake"
        input = self.app_singleton.context.resolve_vars(input)
        output = filepath_helper.resolve_abs_path(input)
        #output = gentestfile.resolve_relative_include_path(input, self.app_singleton)
        self.assertEqual(
            output, 
            (common.test_file_dir / "test-include.cmake").__str__()
        )

    #Ok. This part is not going to make sense in context
    #because CMAKE_CURRENT_LIST_DIR resolves to a full, absolute
    #path. That said, we are going to leave it in because, 
    #in the future, we may support other CMake built-in
    #variables that don't behave this way, and we
    #want to be sure that our path resolution code
    #continues to work correctly.

    @unittest.skipIf(os.name == 'nt', 'Windows uses UNC pathing and drive letters, neither of which are used in non-Windows/DOS OSs.')
    def test_self_reference_before_variable_posix(self):
        input = R"/grandparent_dir/parent_dir/./${CMAKE_CURRENT_LIST_DIR}/test-include.cmake"
        input = self.app_singleton.context.resolve_vars(input)
        output = filepath_helper.resolve_abs_path(input)
        #output = gentestfile.resolve_relative_include_path(input, self.app_singleton)
        expected_output = "/".join([
            "",
            "grandparent_dir",
            "parent_dir",
            common.test_file_dir.__str__(), 
            "test-include.cmake"
        ])
        self.assertEqual(
            output, 
            expected_output
        )

    @unittest.skipIf(os.name != 'nt', 'Windows uses UNC pathing, and here that means expecting drive letters.')
    def test_self_reference_before_variable_unc(self):
        input = R"/grandparent_dir/parent_dir/./${CMAKE_CURRENT_LIST_DIR}/test-include.cmake"
        input = self.app_singleton.context.resolve_vars(input)
        output = filepath_helper.resolve_abs_path(input)
        #output = gentestfile.resolve_relative_include_path(input, self.app_singleton)
        expected_output = "\\".join([
            "C:",
            "grandparent_dir",
            "parent_dir",
            common.test_file_dir.__str__(),
            "test-include.cmake"
        ])
        self.assertEqual(
            output, 
            expected_output
        )