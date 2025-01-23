import re
import sys

#def dereference_cmake_variable(lines, end_index=None):
#    if end_index is None:
#        end_index = len(lines) - 1



def scan_lines_for_macro_match(lines):



#returns tuple with setup,teardown,test_macros
#We may be able to do this parse in a single pass:

def extract_code_from_file(filename):
    if filename is None:
        raise TypeError("\"filename\" cannot be None.")
    
    #How do we add support for test groups?
    #Same as before:  macros with no associated test group
    #are treated as being the only member of a test group
    #with which they share a name.

    #all test groups are preceded by a preamble
    #and followed by a conclusion.

    #While we only care about the macros defined to be tests,
    #collecting all of them while we pass over the file makes
    #things easier:
    test_groups = {}
    add_test_call_indices=[]
    setup = None
    teardown = None

    #What do I do if the client includes other CMake files to be tested (
    #and they will)?
    #We need to capture and retain the include statements to include
    #in the generated file.

    #What if they invoke a function or macro that they created for their tests?

    #Maybe I need to rethink this and just spit out the same file put in,
    #but with the "add_setup", "setup_test", and "add_teardown" pseudo
    #-macros and the "run" function invocation removed, and in their place,
    #code that sets up and runs the tests.

    #Hello
    re_macro_start = re.compile("^\s?(.*?)add_test\(")
    re_cmake_command_end = re.compile(")\s?(.*?)(#)?$")
    lines = None

    with open(filename, 'r') as file:
        #Hello
        lines = file.readlines()

    for line in lines:



if __name__ == "__main__":
    #Hello
    argc = len(sys.argv)
    if argc > 1:
        print("Too many arguments", file=sys.stderr)

    if argc < 1:
        print("Too few arguments", file=sys.stderr)

    file_to_parse=sys.argv[0]
    preamble_template=""
    conclusion_template=""

