#Given a test description file, itself valid CMake, generates
#another CMake file that is capable of running the tests.
import pdb
import enum
import re
import subprocess
import sys

class TestDescriptorFileParseError(RuntimeError):
    def __init__(self, msg, *args, line = '- ',  **kwargs):
        message = str.format("Line: {0}: {1}", line, msg)
        super().__init__(message, *args, **kwargs)


class ApplicationSingleton:
    def __init__(self):
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
        self.current_index = 0
        self.lines = []
        self.ranges_to_cut = []
        self.includes = []
        self.test_groups = []
        self.setup_macro = None
        self.teardown_macro = None
        self.command_definitions = []

    def __str__(self):
        str_arr = []
        str_arr.append("*******************************************\n")
        str_arr.append("Line read-in recall begin:\n")
        str_arr.append("*******************************************\n")

        for line in self.lines:
            str_arr.append(str.format("{0}", line))

        str_arr.append("*******************************************\n")
        str_arr.append("Line read-in recall end\n")
        str_arr.append("*******************************************\n")

        str_arr.append(str.format("Current index: {0}\n", self.current_index))
        str_arr.append(str.format("ranges_to_cut: {0}\n", self.ranges_to_cut))
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

#
# There is no need to account for syntax errors here as that
# was already handled during the linting step.
#

def scan_for_include(parse_status, app_singleton):
    #We ignore "include(*/cmake-test.cmake)"
    if not app_singleton.re_include.search(parse_status.lines[parse_status.current_index]) is None:
        parse_status.includes.append(parse_status.current_index)
        parse_status.current_index += 1

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
        raise TestDescriptorFileParseError(index_temp1, "You cannot define more than one setup macro.")

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
        raise TestDescriptorFileParseError(index_temp1, "You cannot define more than one teardown macro.")

    index_temp1 = str_temp.index('(')
    str_temp = (str_temp[index_temp1 + 1:-2]).strip()
    str_temp = (str_temp.split()[1])
    parse_status.teardown_macro = str_temp
    parse_status.current_index += 1

    return True

##Accepts: tuple: lines, current_index, and ranges_to_cut
##Returns None if not a \"add_test\" pseudo-macro
##Else, returns updated curr_status.
#def scan_for_add_test_macro(parse_status, app_singleton):
#    re_macro_start = re.compile("^\s?(.*?)add_test_macro\(")
#    if not re.match(curr_status[0][0]):
#        return curr_status
#    raise NotImplemented()

#Accepts: tuple: lines, and ranges_to_cut
#def scan_lines_for_macro_match(lines, app_singleton):
#    raise NotImplemented()

def parse_file(filename, app_singleton):
    #Shoud these checks pass, they advance "parse_status.current_index"
    #by point to the line after that indicating the end of the
    #structures they are looking for.
    checks = [
        scan_for_include,
        scan_for_macro_definition,
        scan_for_function_definition,
        scan_for_add_setup_macro,
        scan_for_add_teardown_macro
    ]

    if filename is None:
        raise TypeError("\"filename\" cannot be None.")

    checks_index = 0
    check_passed = False
    parse_status = ParseStatus()
    with open(filename, 'r') as file:
        parse_status.lines = file.readlines()

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

def run_cmake_as_linter(filename):
    try:
        cmake_process = subprocess.run(
            ["cmake", "-P", filename],
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


if __name__ == "__main__":
    #Hello
    argc = len(sys.argv)
    if argc > 2:
        print("Too many arguments", file=sys.stderr)
        sys.exit(1)
    if argc < 2:
        print("Too few arguments", file=sys.stderr)
        sys.exit(1)

    file_to_parse=sys.argv[1]
    if not run_cmake_as_linter(file_to_parse):
        print("Input file is not a valid CMake file", file=sys.stderr)
        sys.exit(1)
    
    app_singleton = ApplicationSingleton()
    parse_status = parse_file(file_to_parse, app_singleton)

    print(parse_status)
    preamble_template=""
    conclusion_template=""



