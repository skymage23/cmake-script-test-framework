import unittest

import copy
import importlib
import pathlib
import subprocess
import sys

import common

sys.path.append(common.scripts_dir.__str__())
gentestfile = importlib.import_module("generate-test-file")

class GenTestFileArgs:
    def __init__(self, build_dir = None, source_dir = None, project_dir = None):
        self.build_dir = build_dir
        self.source_dir = source_dir
        self.project_dir = project_dir

    def translate_to_array(self):
        #Hello:
        return ["-b", self.build_dir, "-c", self.source_dir, "-p", self.project_dir]


class TestFileGenerationTests(unittest.TestCase):
    use_breakpoint = False  # Class variable to control breakpoint behavior
    enable_output_printing = False

    def run_cmake_script(self, filename):
        retcode = 0
        stdout = None
        stderr = None
        try:
            cmake_process = subprocess.run(
                ["cmake", "-P", filename],
                capture_output = True,
                shell=False
            )
            retcode = cmake_process.returncode
            stdout = cmake_process.stdout
            stderr = cmake_process.stderr
        except Exception as e:
            print(
                "Failed to run CMake on \"{}\".".format(filename),
                file=sys.stderr
            )
            retcode = 1
        return retcode, stdout, stderr 
    
    def run_test_generation(self, args):
        if self.use_breakpoint:
            breakpoint()
        return gentestfile.main(args)

    def run_test_file_generation_test(self, input, args: GenTestFileArgs, test_file_output_dir):
        test_file = input.name
        if input is None:
            raise ValueError("\"input\" cannot be None.")
         
        if test_file_output_dir is None:
            raise ValueError("\"test_file_output_dir\" cannot be None.")
        
        prog_args = args.translate_to_array()
        prog_args.append(input.__str__())
        self.assertEqual(self.run_test_generation(prog_args),0)

        retcode, stdout, stderr = self.run_cmake_script(test_file_output_dir / test_file)

        if self.enable_output_printing:
            print(f"stdout: {stdout.decode()}")
            print(f"stderr: {stderr.decode()}")

        self.assertEqual(retcode,0)
        return retcode, stdout, stderr

    def run_cmake_framework_invocation_test(self, input):
        if input is None:
            raise ValueError("\"input\" cannot be None.")
    
        self.assertEqual(self.run_cmake_script(input), 0)

    def print_output_header_banner(self, test_name: str):
        print(f"""
**************************************
* {test_name}
**************************************""")

    def setUp(self):
        self.pretend_working_directory = common.project_base_dir
        self.pretend_source_directory = common.project_base_dir
        self.pretend_build_directory = common.test_helper_dir / "build"

        self.args = GenTestFileArgs(
           build_dir = self.pretend_build_directory.__str__(),
           source_dir = self.pretend_source_directory.__str__(),
           project_dir = self.pretend_working_directory.__str__()
        )
        self.test_output_dir = (common.scripts_dir / "tests")
        return super().setUp()
    
    def test_test_file(self):
        if self.enable_output_printing:
            self.print_output_header_banner("test_test_file")
        input = (common.test_file_dir / "test-file.cmake")
        self.run_test_file_generation_test(input, self.args, self.test_output_dir)

    def test_test_file_dot_backreference_in_filepath(self):
       if self.enable_output_printing:
           self.print_output_header_banner("test_test_file_dot_backreference_in_filepath")
       input = (common.test_file_dir / "test-file-dot-backreference-in-filepath.cmake")
       self.run_test_file_generation_test(input, self.args, self.test_output_dir)


    def test_test_file_dot_reference_in_filepath(self):
       if self.enable_output_printing:
           self.print_output_header_banner("test_test_file_dot_reference_in_filepath")
       input = (common.test_file_dir / "test-file-dot-reference-in-filepath.cmake")
       self.run_test_file_generation_test(input, self.args, self.test_output_dir) 

    def test_test_file_just_a_comment(self):
       if self.enable_output_printing:
           self.print_output_header_banner("test_test_file_just_a_comment")
       input = (common.test_file_dir / "test-file-just-a-comment.cmake")
       self.run_test_file_generation_test(input, self.args, self.test_output_dir)

    def test_test_file_no_setup_no_teardown(self):
       if self.enable_output_printing:
           self.print_output_header_banner("test_test_file_no_setup_no_teardown")
       input = (common.test_file_dir / "test-file-no-setup-no-teardown.cmake")
       self.run_test_file_generation_test(input, self.args, self.test_output_dir)

    def test_test_file_no_setup(self):
       if self.enable_output_printing:
           self.print_output_header_banner("test_test_file_no_setup")
       input = (common.test_file_dir / "test-file-no-setup.cmake")
       self.run_test_file_generation_test(input, self.args, self.test_output_dir)

    def test_test_file_no_teardown(self):
       if self.enable_output_printing:
           self.print_output_header_banner("test_test_file_no_teardown")
       input = (common.test_file_dir / "test-file-no-teardown.cmake")
       self.run_test_file_generation_test(input, self.args, self.test_output_dir)
    
    def test_test_file_no_test_no_setup_no_teardown(self):
       if self.enable_output_printing:
           self.print_output_header_banner("test_test_file_no_test_no_setup_no_teardown")
       input = (common.test_file_dir / "test-file-no-test-no-setup-no-teardown.cmake")
       self.run_test_file_generation_test(input, self.args, self.test_output_dir)

    def test_test_file_no_test_no_setup(self):
       if self.enable_output_printing:
           self.print_output_header_banner("test_test_file_no_test_no_setup")
       input = (common.test_file_dir / "test-file-no-test-no-setup.cmake")
       self.run_test_file_generation_test(input, self.args, self.test_output_dir)

    def test_test_file_no_test_no_teardown(self):
       if self.enable_output_printing:
           self.print_output_header_banner("test_test_file_no_test_no_teardown")
       input = (common.test_file_dir / "test-file-no-test-no-teardown.cmake")
       self.run_test_file_generation_test(input, self.args, self.test_output_dir)

    def test_test_file_no_test(self):
       if self.enable_output_printing:
           self.print_output_header_banner("test_test_file_no_test")
       input = (common.test_file_dir / "test-file-no-test.cmake")
       self.run_test_file_generation_test(input, self.args, self.test_output_dir)

    def test_test_file_quotes_around_important_names(self):
       if self.enable_output_printing:
           self.print_output_header_banner("test_test_file_quotes_around_important_names")
       input = (common.test_file_dir / "test-file-quotes-around-important-names.cmake")
       self.run_test_file_generation_test(input, self.args, self.test_output_dir)

    def test_test_expand_cmake_current_list_dir(self):
       if self.enable_output_printing:
           self.print_output_header_banner("test_test_expand_cmake_current_list_dir")
       input = (common.test_file_dir / "test-file-expand-cmake-current-list-dir.cmake")
       self.run_test_file_generation_test(input, self.args, self.test_output_dir)
    
    def test_test_expand_cmake_build_dir(self):
       if self.enable_output_printing:
           self.print_output_header_banner("test_test_expand_cmake_build_dir")
       input = (common.test_file_dir / "test-file-expand-cmake-build-dir.cmake")
       args = copy.deepcopy(self.args)
       args.source_dir = common.test_helper_dir.__str__()
       if self.use_breakpoint:
           breakpoint()
       _, stdout, _ = self.run_test_file_generation_test(input, self.args, self.test_output_dir)
       self.assertEqual(stdout.decode(), args.source_dir)

    def test_test_file(self):
       if self.enable_output_printing:
           self.print_output_header_banner("test_test_file")
       input = (common.test_file_dir / "test-file.cmake")
       self.run_test_file_generation_test(input, self.args, self.test_output_dir)