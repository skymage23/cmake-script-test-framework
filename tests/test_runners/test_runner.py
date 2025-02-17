#!/usr/bin/env python3

import copy
import importlib
import os
import pathlib
import subprocess
import sys


tests_dir = pathlib.Path(__file__).parent.parent
test_files_dir = tests_dir / "test_files"
test_runners_dir = tests_dir / "test_runners"
correct_dir = tests_dir.parent
scripts_dir = correct_dir / "python"
sys.path.append(scripts_dir.__str__())
gentestfile = importlib.import_module("generate-test-file")



def pretty_print(input):
    print("""*
*
* {}
*
**************************\n""".format(input))
    
def initialize():
    generated_tests_dir = correct_dir/"python"/"tests"
    os.chdir(correct_dir)
    return correct_dir, generated_tests_dir

def run_cmake_script(filename):
    try:
        cmake_process = subprocess.run(
            ["cmake", "-P", filename],
            stderr=sys.stderr,
            stdout=sys.stdout,
            shell=False
        )
        return cmake_process.returncode
    except Exception as e:
        print(
            "Failed to run CMake on \"{}\".".format(filename),
            file=sys.stderr
        )
        return 1

def run_test_file_generation_test(input, args_temp, test_file_output_dir):
    if input is None:
        raise ValueError("\"input\" cannot be None.")
    
    if args_temp is None:
        raise ValueError("\"args_temp\" cannot be None.")

    if test_file_output_dir is None:
        raise ValueError("\"test_file_output_dir\" cannot be None.")

    pretty_print("Testing using \"{}\".".format(input)) 
    args = copy.deepcopy(args_temp)
    args.append(input)
    if gentestfile.main(args) != 0:
        return 1
    if run_cmake_script(test_file_output_dir / "test-file.cmake"):
        return 1
    
    return 0

def run_cmake_framework_invocation_test(input):
    if input is None:
        raise ValueError("\"input\" cannot be None.")
    pretty_print("Running \"{}\".".format(input))

    if run_cmake_script(input):
        return 1
    return 0

def main():
    curr_dir, generated_tests_dir = initialize()
    cmake_p_source_dir = curr_dir
    cmake_p_binary_dir = cmake_p_source_dir
    cmake_p_project_source_dir = cmake_p_source_dir
    args_temp = [
        "-b",
        cmake_p_binary_dir.__str__(),
        "-c",
        cmake_p_source_dir.__str__(),
        "-p",
        cmake_p_project_source_dir.__str__()
    ]

    #Missing test-env-var-in-path.cmake: special case.
    run_test_file_list = [
        "test-file.cmake",
        "test-file-dot-backreference-in-filepath.cmake",
        "test-file-dot-reference-in-filepath.cmake",
        "test-file-just-a-comment.cmake",
        "test-file-no-setup-no-teardown.cmake",
        "test-file-no-setup.cmake",
        "test-file-no-teardown.cmake",
        "test-file-no-test-no-setup-no-teardown.cmake",
        "test-file-no-test-no-setup.cmake",
        "test-file-no-test-no-teardown.cmake",
        "test-file-no-test.cmake",
        "test-file-quotes-around-important-names.cmake",
        "test-file-var-in-include-path.cmake"
    ]

    cmake_script_test_framework_invocation_tests = [
        "test-run-test-proj-src-dir-arg.cmake",
        "test-run-test-skip-gen-file-proj-src-dir-arg.cmake",
        "test-run-test-skip-gen-file.cmake",
        "test-run-test.cmake"
    ]    

    for var in run_test_file_list:
        if run_test_file_generation_test(
            (test_files_dir / var).__str__(),
            args_temp,
            generated_tests_dir
        ) != 0:
            print("Test failed: {}".format(var), file=sys.stderr) 
            return 1
    
    #This one is a special case since it requires that we set an environment
    #variable first.
    file = "test-file-env-var-in-path.cmake"
    os.environ["CMAKE_TEST_DIR"] = curr_dir.__str__()
    os.environ["OUR_PATH"] = test_files_dir.__str__()
    if run_test_file_generation_test(
        (test_files_dir / file).__str__(),
        args_temp,
        generated_tests_dir
    ) != 0:
        print("Test failed: {}".format(file), file=sys.stderr) 
        return 1
    file = None
    del os.environ["CMAKE_TEST_DIR"]
    del os.environ["OUR_PATH"]


    for var in cmake_script_test_framework_invocation_tests:
        var = (test_runners_dir / var).__str__()
        if run_cmake_framework_invocation_test(var) != 0:
            print("Test failed: {}".format(var))
            return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())

