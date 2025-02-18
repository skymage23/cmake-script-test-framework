import unittest

import copy
import importlib
import pathlib
import subprocess
import sys

import common

sys.path.append(common.scripts_dir.__str__())
gentestfile = importlib.import_module("generate-test-file")

class TestFileGenerationTests(unittest.TestCase):
    def run_cmake_script(self, filename):
        retcode = 0
        try:
            cmake_process = subprocess.run(
                ["cmake", "-P", filename],
                stderr=sys.stderr,
                stdout=sys.stdout,
                shell=False
            )
            retcode = cmake_process.returncode
        except Exception as e:
            print(
                "Failed to run CMake on \"{}\".".format(filename),
                file=sys.stderr
            )
            retcode = 1
        return retcode

    def run_test_file_generation_test(self, input, args_temp, test_file_output_dir):
        if input is None:
            raise ValueError("\"input\" cannot be None.")
        
        if args_temp is None:
            raise ValueError("\"args_temp\" cannot be None.")
    
        if test_file_output_dir is None:
            raise ValueError("\"test_file_output_dir\" cannot be None.")
    
        args = copy.deepcopy(args_temp)
        args.append(input)
        self.assertEqual(gentestfile.main(args),0)
        self.assertEqual(self.run_cmake_script(test_file_output_dir / "test-file.cmake"),0)

    def run_cmake_framework_invocation_test(self, input):
        if input is None:
            raise ValueError("\"input\" cannot be None.")
    
        self.assertEqual(self.run_cmake_script(input), 0)


    def setUp(self):
        self.pretend_working_directory = common.project_base_dir
        self.pretend_source_directory = common.project_base_dir
        self.pretend_build_directory = common.project_base_dir / "build"
        self.args = [
            "-b",
            self.pretend_source_directory.__str__(),
            "-c",
            self.pretend_source_directory.__str__(),
            "-p",
            self.pretend_source_directory.__str__(),
        ]
        self.test_output_dir = (common.scripts_dir / "tests")
        return super().setUp()
    
    def test_test_file(self):
        input = (common.test_file_dir / "test-file.cmake").__str__()
        self.run_test_file_generation_test(input, self.args, self.test_output_dir)

    def test_test_file_dot_backreference_in_filepath(self):
       input = (common.test_file_dir / "test-file-dot-backreference-in-filepath.cmake").__str__()
       self.run_test_file_generation_test(input, self.args, self.test_output_dir)


    def test_test_file_dot_reference_in_filepath(self):
       input = (common.test_file_dir / "test-file-dot-reference-in-filepath.cmake").__str__()
       self.run_test_file_generation_test(input, self.args, self.test_output_dir) 


    def test_test_file_just_a_comment(self):
       input = (common.test_file_dir / "test-file-just-a-comment.cmake").__str__()
       self.run_test_file_generation_test(input, self.args, self.test_output_dir)

    def test_test_file_no_setup_no_teardown(self):
       input = (common.test_file_dir / "test-file-no-setup-no-teardown.cmake").__str__()
       self.run_test_file_generation_test(input, self.args, self.test_output_dir)

    def test_test_file_no_setup(self):
       input = (common.test_file_dir / "test-file-no-setup.cmake").__str__()
       self.run_test_file_generation_test(input, self.args, self.test_output_dir)

    def test_test_file_no_teardown(self):
       input = (common.test_file_dir / "test-file-no-teardown.cmake").__str__()
       self.run_test_file_generation_test(input, self.args, self.test_output_dir)
    
    def test_test_file_no_test_no_setup_no_teardown(self):
       input = (common.test_file_dir / "test-file-no-test-no-setup-no-teardown.cmake").__str__()
       self.run_test_file_generation_test(input, self.args, self.test_output_dir)

    def test_test_file_no_test_no_setup(self):
       input = (common.test_file_dir / "test-file-no-test-no-setup.cmake").__str__()
       self.run_test_file_generation_test(input, self.args, self.test_output_dir)

    def test_test_file_no_test_no_teardown(self):
       input = (common.test_file_dir / "test-file-no-test-no-teardown.cmake").__str__()
       self.run_test_file_generation_test(input, self.args, self.test_output_dir)

    def test_test_file_no_test(self):
       input = (common.test_file_dir / "test-file-no-test.cmake").__str__()
       self.run_test_file_generation_test(input, self.args, self.test_output_dir)

    def test_test_file_quotes_around_important_names(self):
       input = (common.test_file_dir / "test-file-quotes-around-important-names.cmake").__str__()
       self.run_test_file_generation_test(input, self.args, self.test_output_dir)

    def test_test_file_var_in_include_path(self):
       input = (common.test_file_dir / "test-file-var-in-include-path.cmake").__str__()
       self.run_test_file_generation_test(input, self.args, self.test_output_dir)

    def test_test_file(self):
       input = (common.test_file_dir / "test-file.cmake").__str__()
       self.run_test_file_generation_test(input, self.args, self.test_output_dir)