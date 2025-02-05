#!/usr/bin/env python3

#Given a test description file, itself valid CMake, generates
#another CMake file that is capable of running the tests.
import argparse
import enum
import os
import pathlib
import re
import subprocess
import sys

import cmake_helper

class TestDescriptorFileParseError(RuntimeError):
    def __init__(self, msg, *args, line = '- ',  **kwargs):
        message = str.format("Line: {0}: {1}", line, msg)
        super().__init__(message, *args, **kwargs)


class ApplicationSingleton:
    def __init__(self, context):
        self.context = context
        self.re_add_setup_macro = re.compile(R"^\s?add_setup_macro\s?\(")
        self.re_add_teardown_macro = re.compile(R"^\s?add_teardown_macro\s?\(")
        self.re_add_test_macro = re.compile(R"^\s?add_test_macro\s?\(")
        self.re_macro_definition = re.compile(R"^\s?macro\s?\(")
        self.re_macro_end = re.compile(R"^\s?endmacro\s?\(\)\s?(.*?)(#.*)?$")
        self.re_function_definition = re.compile(R"^\s?function\s?\(")
        self.re_function_end = re.compile(R"^\s?endfunction\s?\(\)\s?(.*?)(#.*)?$")
        self.re_include = re.compile(R"^\s?include\s?\(")

class TestMacro:
    def __init__(self, name, args):
        self.name = name
        self.args = args

class ParseStatus:
    def __init__(self):
        self.input_filepath = None
        self.current_index = 0
        self.lines = []
        self.includes = []
        self.test_groups = {}
        self.setup_macro = None
        self.teardown_macro = None
        self.command_definitions = []

    def __str__(self):
        str_arr = []
        str_arr.append(str.format("Input filename: {}", self.input_filepath.__str__()))
        str_arr.append("*******************************************\n")
        str_arr.append("Line read-in recall begin:\n")
        str_arr.append("*******************************************\n")

        for line in self.lines:
            str_arr.append(str.format("{0}", line))

        str_arr.append("*******************************************\n")
        str_arr.append("Line read-in recall end\n")
        str_arr.append("*******************************************\n")

        str_arr.append(str.format("Current index: {0}\n", self.current_index))
        str_arr.append(str.format("includes: {0}\n", self.includes))
        str_arr.append(str.format("test_groups: {0}\n", self.test_groups))
        str_arr.append(str.format("setup_macro: {0}\n", self.setup_macro))
        str_arr.append(str.format("Teardown macro: {0}\n", self.teardown_macro))
        str_arr.append(str.format("Command definitions: {0}\n", self.command_definitions))
        str_arr.append("\n")
        return "".join(str_arr)


class CommandDefinitionTypes(enum.Enum):
    MACRO = enum.auto()
    FUNCTION = enum.auto()

def print_err(string: str):
    if string is None:
        string = "Unknown error. Message string was mistakenly set to None."

    print(string, file=sys.stderr)

def die(string: str):
    print_err(string)
    sys.exit(1)

##We need to able to resolve some common CMake variables ourselves:
##CMAKE_CURRENT_LIST_DIR
##CMAKE_BUILD_DIR
##CMAKE_SOURCE_DIR
#def resolve_certain_cmake_vars(parse_status):
#    raise NotImplemented()
#
#def resolve_environment_vars():
#    raise NotImplemented()
#

def resolve_vars_in_filepath(filepath, app_singleton):
    retval = []    
    separator = os.path.sep
    exploded_path = filepath.split(separator) 
    for var in exploded_path:
        #var = var.strip()
        #if self.re_cmake_var_dereference.search(var) is None:
        #    continue
        
        #ind_temp1 = var.index('$') + 1
        #ind_temp2 = var.index('}')
        #var = var[ind_temp1: -(len(var) - (ind_temp2))]

        ##OK. Are we an environment variable or not.
        #print(var)
        #if self.re_cmake_env_var_dereference.search(var) is None:
        #   retval = resolve_certain_cmake_vars(parse_status)            
        #else: 
        retval.append(app_singleton.context.resolve_vars(var))
    return separator.join(retval)

def resolve_relative_include_path(parse_status, relative_path, app_singleton):
    #Hello:
    SELF_REFERENCE = '.'
    PARENT_REFERENCE = ".."
    separator = os.path.sep
    elem_temp = None
    exploded_path = None 
    exploded_input_origin_dir_path = app_singleton.context.project_source_dir.__str__().split(separator)
    dir_stack = []

    relative_path = resolve_vars_in_filepath(relative_path, app_singleton)

    exploded_path = relative_path.split(separator)
    #Handle the case of len(exploded_path) = 1:
    
    #What if it is of the form?:
    #../hello/my/fellow/programmer
    if exploded_path[0] != '':
        exploded_input_origin_dir_path.extend(exploded_path)
        exploded_path = exploded_input_origin_dir_path

    for i in range(0, len(exploded_path)):
        elem_temp = exploded_path[i]
        if(elem_temp == SELF_REFERENCE):
            continue
        elif(elem_temp == PARENT_REFERENCE):
            if(len(dir_stack) == 1):
                continue  #This mimics how filesystem backreferences work.
                          #The lowest level backreference always refers to the current
                          #directory itself.
            dir_stack.pop()
            continue
        else:
            dir_stack.append(elem_temp)

    return separator.join(dir_stack)
#
# There is no need to account for syntax errors here as that
# was already handled during the linting step.
#

def scan_for_include(parse_status, app_singleton):
    #We ignore "include(*/cmake-test.cmake)"
    CMAKE_TEST_FILENAME = "cmake-test.cmake"
    temp = None
    index_temp = parse_status.current_index
    str_temp = parse_status.lines[index_temp]
 
    if app_singleton.re_include.search(str_temp) is None:
        return False
    index_temp = str_temp.index('(')
    str_temp = (str_temp[index_temp + 1: -2]).strip()

    temp = resolve_relative_include_path(parse_status, str_temp, app_singleton)  #Resolve relative paths.
    str_temp = pathlib.Path(temp).name
    
    #Quietly ignore the include of the dummy definitions:        
    if not CMAKE_TEST_FILENAME in str_temp:
        parse_status.includes.append((parse_status.current_index, temp.__str__()))
    parse_status.current_index += 1
    return True

#Macros and functions are defined similarly and can be detected in the same way.
#returns tuple: (start, end). If not macro, returns None
def check_for_command_definition(command_type, parse_status, app_singleton):
    re_command_start = None
    re_command_end = None

    match command_type :
        case CommandDefinitionTypes.MACRO:
            re_command_start = app_singleton.re_macro_definition
            re_command_end = app_singleton.re_macro_end

        case CommandDefinitionTypes.FUNCTION:
            re_command_start = app_singleton.re_function_definition
            re_command_end = app_singleton.re_function_end

    if re_command_start.search(parse_status.lines[parse_status.current_index]) is None:
        return None

    temp = None        
    index = parse_status.current_index
    command_start_stack = [parse_status.current_index]
    command_end_stack = []

    #We break out of the loop programmatically
    while len(command_start_stack) != len(command_end_stack):
        index += 1 
        temp = parse_status.lines[index]
        if not re_command_end.search(temp) is None:
            command_end_stack.append(index)
            continue

        if not re_command_start.search(temp) is None:
            command_start_stack.append(index) 

    final_command_end = command_end_stack[len(command_end_stack) - 1]
    parse_status.current_index = final_command_end + 1
    return (command_start_stack[0], final_command_end)



def scan_for_macro_definition(parse_status, app_singleton):
    start_end_tuple = check_for_command_definition(CommandDefinitionTypes.MACRO, parse_status, app_singleton)
    if start_end_tuple is None:
        return False
    
    parse_status.command_definitions.append(start_end_tuple)
    return True


def scan_for_function_definition(parse_status, app_singleton):
    start_end_tuple = check_for_command_definition(CommandDefinitionTypes.FUNCTION, parse_status, app_singleton)
    if start_end_tuple is None:
        return False
    
    parse_status.command_definitions.append(start_end_tuple)
    return True

##Returns None if not a \"add_setup\" pseudo-macro
def scan_for_add_setup_macro(parse_status, app_singleton):
    index_temp1 = parse_status.current_index
    #index_temp2 = -1
    str_temp = None

    str_temp = parse_status.lines[index_temp1]
    if app_singleton.re_add_setup_macro.search(str_temp) is None:
        return False

    if not parse_status.setup_macro is None:
        raise TestDescriptorFileParseError(
            "You cannot define more than one setup macro.",
            line = index_temp1
        )

    index_temp1 = str_temp.index('(')
    str_temp = (str_temp[index_temp1 + 1:-2]).strip()
    str_temp = (str_temp.split()[1])
    parse_status.setup_macro = str_temp
    parse_status.current_index += 1

    return True

##Accepts: tuple: lines, and ranges_to_cut
##Returns None if not a \"add_teardown\" pseudo-macro
def scan_for_add_teardown_macro(parse_status, app_singleton):
    index_temp1 = parse_status.current_index
    #index_temp2 = -1
    str_temp = None

    str_temp = parse_status.lines[index_temp1]
    if app_singleton.re_add_teardown_macro.search(str_temp) is None:
        return False

    if not parse_status.teardown_macro is None:
        raise TestDescriptorFileParseError(
            "You cannot define more than one teardown macro.",
            line = index_temp1
        )

    index_temp1 = str_temp.index('(')
    str_temp = (str_temp[index_temp1 + 1:-2]).strip()
    str_temp = (str_temp.split()[1])
    parse_status.teardown_macro = str_temp
    parse_status.current_index += 1

    return True


def scan_for_add_test_macro(parse_status, app_singleton):
    TOTAL_POSSIBLE_ARGUMENTS = 4
    macro_name = None
    test_group = None
    index_temp = None
    arr_temp = None
    str_temp = parse_status.lines[parse_status.current_index]
    str_temp.strip()

    if app_singleton.re_add_test_macro.search(str_temp) is None:
        return False 
    index_temp = str_temp.index('(')
    str_temp = (str_temp[index_temp + 1: -(len(str_temp) - str_temp.index(')'))]).strip()
    arr_temp = str_temp.split()

    macro_name = arr_temp[1]
    if len(arr_temp) < TOTAL_POSSIBLE_ARGUMENTS:
        test_group = macro_name
    else:
        test_group = arr_temp[3]

    if not test_group in parse_status.test_groups:
        parse_status.test_groups[test_group] = {}

    if macro_name in parse_status.test_groups[test_group]:
        raise TestDescriptorFileParseError(
            "You cannot add the same test to the same test group more than once.",
            line = parse_status.current_index
        )

    parse_status.test_groups[test_group][macro_name] = True
    parse_status.current_index += 1
    return True

#Accepts: tuple: lines, and ranges_to_cut
#def scan_lines_for_macro_match(lines, app_singleton):
#    raise NotImplemented()

def parse_file(app_singleton):
    #Shoud these checks pass, they advance "parse_status.current_index"
    #by point to the line after that indicating the end of the
    #structures they are looking for.
    checks = [
        scan_for_include,
        scan_for_macro_definition,
        scan_for_function_definition,
        scan_for_add_setup_macro,
        scan_for_add_teardown_macro,
        scan_for_add_test_macro
    ]

    checks_index = 0
    check_passed = False
    parse_status = ParseStatus()
    try:
        with open(context.list_file.__str__(), 'r') as file:
            parse_status.lines = file.readlines()
    except FileNotFoundError:
        print("Test descriptor file \"{}\" does not exist.".format(app_singleton.context.list_file.__str__()), file=sys.stderr)
        return None

    while parse_status.current_index < len(parse_status.lines):
        checks_index = 0
        check_passed = False
        while checks_index < len(checks):
            check_passed = checks[checks_index](parse_status, app_singleton)
            if check_passed:
                break;
            checks_index += 1
        if not check_passed:
            parse_status.current_index += 1 
    return parse_status

def generate_file_contents(parse_status):
    test_keys = None;
    preamble = """
#*******************************************************
# This is a generated file that is usually destroyed
# after it is used. Any changes to this file will be
# discarded. Instead, make your changes to the descriptor
# file used to generate this file.
#*******************************************************\n"""
    indices_to_ignore=[]
    str_buffer = [preamble]

    #Add includes:
    str_buffer.append(
"""#*****************
# Includes:
#*****************\n""")
    for elem in parse_status.includes:
        str_buffer.append("".join(["include(", elem[1], ")\n"]))
        indices_to_ignore.append(elem[0])
    str_buffer.append("\n")

    #Add command definitions:
    str_buffer.append(
"""#************************
# Command Definitions:
#************************\n""")
    for elem in parse_status.command_definitions:
        #Hello:
        for index in range(elem[0], elem[1] + 1):
            str_buffer.append(parse_status.lines[index])
            indices_to_ignore.append(index)
        str_buffer.append("\n")

    #Add everything that is not a test definition:
    str_buffer.append(
"""#************************
# Tests: 
#************************\n""")
    for test_group in parse_status.test_groups.keys():
        str_buffer.append(
"""#*
#* Test Group: {}
#*
#*************************\n""".format(test_group)
)
        #Hello:
        str_buffer.append("{}()\n".format(parse_status.setup_macro))
        for test in parse_status.test_groups[test_group].keys():
            str_buffer.append("{}()\n".format(test))
        str_buffer.append("{}()".format(parse_status.teardown_macro))
        str_buffer.append("\n\n")
    return str_buffer

def run_cmake_as_linter(filename, working_dir):
    try:
        cmake_process = subprocess.run(
            ["cmake", "-P", filename],
            cwd = working_dir,
            stderr = sys.stderr,
            stdout = sys.stdout,
            shell = False
        )

        if cmake_process.returncode != 0:
            print("CMake lint failed. Input is not a valid CMake file.", file=sys.stderr)
            print(cmake_process.stderr, file=sys.stderr)
            return False
    except Exception as e:
        print("Failed to run CMake as linter", file=sys.stderr)
        print(e, file=sys.stderr)
        return False
    return True

def parse_args_into_context():
    context = None
    build_dir = None
    source_dir = None
    proj_source_dir = None

    parser = argparse.ArgumentParser(
        prog = 'generate-test-file.py',
        description = 'Takes in a test descriptor file and generates a CMake unit test file.',
        usage='%(prog)s [options]'
    )
    parser.add_argument(
        '-b',
        '--build_dir',
        type=str,
        help='CMake build directory.',
        required = True
    )

    parser.add_argument(
        '-c',
        '--source_dir',
        type=str,
        help = "CMake source directory.",
        required = True
    )

    parser.add_argument(
        '-p',
        '--project_source_dir',
        type=str,
        help = 'Project source directory.',
        required = True
    )

    parser.add_argument(
        'list_file',
        type=str,
        nargs=1,
        help = 'Test descriptor file',
    )

    parse_results = parser.parse_args()
    list_file = parse_results.list_file[0]
    build_dir = parse_results.build_dir
    if build_dir is None or build_dir == '':
        die("\"-b/--build_dir\" cannot be the empty string.")

    source_dir = parse_results.source_dir
    if source_dir is None or source_dir == '':
        die("\"-c/--source_dir\" cannot be the empty string.")
    source_dir = parse_results.source_dir

    proj_source_dir = parse_results.project_source_dir
    if proj_source_dir is None or proj_source_dir == '':
        proj_source_dir = source_dir

    context = cmake_helper.CMakeScriptContext(
        build_dir=build_dir,
        source_dir=source_dir,
        project_source_dir=proj_source_dir,
        list_file=list_file
    )
    if not context.build_dir.exists():
        die("\"build_dir\" does not exist.")

    if not context.build_dir.is_dir():
        die("\"build_dir\" is not a directory.")
    
    if not context.source_dir.exists():
        die("\"source_dir\" does not exist.")

    if not context.source_dir.is_dir():
        die("\"source_dir\" is not a directory.")
 
    if not context.project_source_dir.exists():
        die("\"project_source_dir\" does not exist.")

    if not context.project_source_dir.is_dir():
        die("\"project_source_dir\" is not a directory.")
    
    if not context.list_file.exists():
        die("\"list_file\" does not exist.")

    if not context.list_file.is_file():
        die("\"list_file\" is not a file.")
    
    if not run_cmake_as_linter(list_file, context.current_list_dir.__str__() ):
        die("Input file is not a valid CMake file")

    return context

if __name__ == "__main__":
     test_directory = pathlib.Path(__file__).parent / "tests"
     # argc = len(sys.argv)
     # if argc > 2:
     #     print("Too many arguments", file=sys.stderr)
     #     sys.exit(1)
     # if argc < 2:
     #     print("Too few arguments", file=sys.stderr)
     #     sys.exit(1)

     # file_to_parse=pathlib.Path(sys.argv[1])
     
     context = parse_args_into_context() 
     app_singleton = ApplicationSingleton(context)
     parse_status = parse_file(app_singleton)

     if parse_status is None:
         print("An error occurred while parsing file \"{}\".".format(context.list_file), file=sys.stderr)
         sys.exit(1)

     output_buffer = generate_file_contents(parse_status)
     if test_directory.exists():
         if not test_directory.is_dir():
             print(
                 "There exists something at path \"tests\", but it is not a directory",
                 file=sys.stderr
             )
             sys.exit(1)
         if not os.access(test_directory, os.W_OK):
             print(
                 "While the \"tests\" directory exists, You do not have write access to it."
             )
             sys.exit(1)
     else:
         test_directory.mkdir() 

     test_file = test_directory / context.list_file.name
     with open(test_file, 'w') as file:
         file.writelines(output_buffer)