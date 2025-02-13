#!/usr/bin/env python3

import copy
import importlib
import os
import pathlib
import subprocess
import sys

scripts_dir = pathlib.Path(__file__).parent
correct_dir = scripts_dir.parent
sys.path.append(scripts_dir.__str__())
gentestfile = importlib.import_module("generate-test-file")



def pretty_print(input):
    print("""*
*
* {}
*
**************************\n""".format(input))
    
def initialize():
    tests_dir = correct_dir/"python"/"tests"
    os.chdir(correct_dir)
    return correct_dir, tests_dir

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


def main():
    curr_dir, tests_dir = initialize()
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
    
    pretty_print("Testing using \"test-file.cmake\".")
    #build arg
    args = copy.deepcopy(args_temp)
    args.append("test-file.cmake")
    if gentestfile.main(args) != 0:
        return 1
    if run_cmake_script(tests_dir/"test-file.cmake"):
        return 1

    pretty_print("Testing using \"test-file-var-in-include-path.cmake\".")
    #build args 
    args = copy.deepcopy(args_temp)
    args.append("test-file-var-in-include-path.cmake")
    if gentestfile.main(args) != 0:
        return 1
    if run_cmake_script(
        tests_dir/"test-file-var-in-include-path.cmake"
    ):
        return 1

    pretty_print("Testing using \"test-file-relative-path.cmake\".")
    #build args
    args = copy.deepcopy(args_temp)
    args.append("test-file-relative-path.cmake")
    if gentestfile.main(args) != 0:
        return 1 
    if run_cmake_script(
        tests_dir/"test-file-relative-path.cmake"
    ):
        return 1

    pretty_print("Testing \"test-file-quotes-around-important-names.cmake\".")
    #build args
    args = copy.deepcopy(args_temp)
    args.append("test-file-quotes-around-important-names.cmake")
    if gentestfile.main(args) != 0:
        return 1
    if run_cmake_script(
        tests_dir/"test-file-quotes-around-important-names.cmake"
    ):
        return 1


    pretty_print("Testing \"test-file-env-var-in-path.cmake\".")
    #build args
    args = copy.deepcopy(args_temp)
    args.append("test-file-env-var-in-path.cmake")
    os.environ["OUR_PATH"] = curr_dir.__str__()
    if gentestfile.main(args) != 0:
        return 1
    if run_cmake_script(
        tests_dir/"test-file-env-var-in-path.cmake"
    ):
        return 1
    
    pretty_print("Running \"test-run-test.cmake\"")
    if run_cmake_script("test-run-test.cmake"):
        return 1
    
    pretty_print("Running \"test-run-test-proj-src-dir-arg.cmake\"")
    if run_cmake_script("test-run-test-proj-src-dir-arg.cmake"):
        return 1
 
    pretty_print("Running \"test-run-test-skip-gen-file.cmake\"")
    if run_cmake_script("test-run-test-skip-gen-file.cmake"):
        return 1

    pretty_print("Running \"test-run-test-skip-gen-file-proj-src-dir-arg.cmake\"")
    if run_cmake_script("test-run-test-skip-gen-file-proj-src-dir-arg.cmake"):
        return 1


    return 0

if __name__ == "__main__":
    sys.exit(main())

