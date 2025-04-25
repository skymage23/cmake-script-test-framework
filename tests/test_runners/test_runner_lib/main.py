#!/usr/bin/env python3
from unittest import TestCase, TestSuite, TestLoader, TextTestRunner
import argparse
import importlib
import inspect
import pathlib
import sys

import common
import development_shell_helpers
import development

class TestCaseRequest:
    def __init__(self, testcase, module = None):
        self.testcase = testcase
        self.module = module
        if module is None:
            self.mod_set = False
        else:
            self.mod_set = True

    def __str__(self):
        return f"""Specified module: {self.module}, Testcase: {self.testcase}"""

class TestRequest:
    def __init__(self,
        test_name = None,
        test_module = None,
        test_case = None    
    ):
        self.test_name = test_name
        self.test_module = test_module
        self.test_case = test_case

class ApplicationSingleton:
    def __init__(self,
        args = None,
        module_dir = None,
        module_list = None,
        requested_test_cases = None,
        registered_modules = None,
        registered_test_cases = None,
        registered_tests = None
    ):
        self.args = args
        self.requested_test_cases = requested_test_cases
        self.module_dir = module_dir
        self.module_list = module_list
        self.registered_modules = registered_modules
        self.registered_test_cases = registered_test_cases
        self.registered_tests = registered_tests

def parse_requested_test_cases(input_list):
    retval = []
    temp_arr = None
    for elem in input_list:
        temp_arr = elem.split('.')
        if len(temp_arr) > 2:
            common.die(f"Malformed test case request: {elem}. Too many Python scope specifications.")
        elif len(temp_arr) == 1:
            retval.append(TestCaseRequest(testcase = temp_arr[0]))
        elif len(temp_arr) == 2:
            retval.append(TestCaseRequest(testcase = temp_arr[1], module = temp_arr[0]))
    return retval

#def parse_requested_tests(input_list):
#    pass        


def validate_and_initialize():
    parser = argparse.ArgumentParser(description='Run unit tests with breakpoint control')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--breakpoint-all', '-ba', action='store_true', 
                      help='Enable breakpoints for all tests')
    group.add_argument('--breakpoint', '-b', nargs='+', 
                      help='Enable breakpoints for specific test names. Ignored if "--breakpoint-all" is specified.')
    
    parser.add_argument('--test-modules', '-m', nargs="+",
                       help = """Import specific test modules. Unless you specify either
\"--testcases\" or \"--run-specific-tests\" all tests for all test cases
in the listed modules are executed. If this argument is absent, all modules
in the \"test_modules\" directory are evaluated.""")

    parser.add_argument('--testcases', '-c', nargs='+',
                       help = "Run specific test cases. Form: [<test_module_name>.]<test_case_name>") 
    
    parser.add_argument('--run-specific-tests', '-t', nargs='+',
                        help="Run specific tests. Only these will be executed."),
    
    parser.add_argument('--print-test-output','-p', nargs='+',
                      help="Enable output printing for specific test names.")
    args = parser.parse_args()

    if args.run_specific_tests and not args.testcases:
        parser.error("--run-specific-tests (-t) requires --testcases (-c).")

    requested_test_cases = None
    dir_path = pathlib.Path(__file__).parent
    module_dir = dir_path / "test_modules"
    if not module_dir.exists():
        raise development.errors.DevelopmentError(
            development_shell_helpers.Universal.repo_utils.Get_RepoCorruptMessage()
        )
    sys.path.append(module_dir)

    if args.testcases:
        requested_test_cases = parse_requested_test_cases(args.testcases) 
    return ApplicationSingleton(args = args, requested_test_cases = requested_test_cases, module_dir = module_dir)


def get_module_list(app_singleton: ApplicationSingleton):
    requested_modules = app_singleton.args.test_modules
    print(f"Requested modules: {requested_modules}")
    retval = [entry.stem for entry in app_singleton.module_dir.iterdir()
              if entry.is_file() and entry.suffix == ".py"] 
    print(f"Found modules: {retval}")
    if len(retval) == 0:
        common.die("No test modules found in the \"test_modules\" directory.")
    
    if not requested_modules is None:
        retval = [entry for entry in retval if entry in requested_modules]
        print(f"After module filtering: {retval}")
        if len(retval) == 0:
            common.die("None of the requested modules were found in the \"test_modules\" directory.")
    app_singleton.module_list = retval

def load_modules(app_singleton: ApplicationSingleton):
    dict_temp = {}
    for module in app_singleton.module_list:
        dict_temp[module] = importlib.import_module(module)
    
    app_singleton.registered_modules = dict_temp


def register_select_test_cases(current_test_cases, requested_test_cases):
    err_message = """
Unable to locate the following test cases in any loaded module.
Are you sure you specified the correct module?

"""
    mod = None
    retval = {}
    case = None
    for case in requested_test_cases[:]:
        arr_temp = [cls for cls in current_test_cases if cls.__name__ == case.testcase]
       #if 0, requested test case not found.
        temp = len(arr_temp)
        if temp == 0:
            common.die(f"Test case not found in loaded modules: \"{case}\".")

        #Multiple test cases of the same name but from different modules:
        if case.module is None and temp >= 2:
            common.die(f"""Multiple possible candidates for test case \"{case.testcase}\". 
You will need to specify which test case you want by specifying the test module when using \"--testcases\".
Form:  <test_module_name>.<test_case_name>                   
""")
        
        for cls in arr_temp:
            if not case.testcase in retval:
                if (not case.module is None) and (case.module != cls.__module__):
                      continue
                retval[case.testcase] = {cls.__module__: cls}
            else:
                if case.module in retval[case.testcase]:
                    continue
                retval[case.testcase][cls.__module__] = cls
        requested_test_cases.remove(case)

    
    if len(requested_test_cases) > 0:
       for case in requested_test_cases:
           mod = case.module if case.module is not None else "not specified"
           err_message += f"Case: {case.testcase}, Module: {mod}."
           common.die(err_message)
    return retval

def register_test_cases(app_singleton: ApplicationSingleton):
    retval = None
    current_test_cases = common.TestCaseWrapper.__subclasses__() 
    #Look for requested test cases:
    if not app_singleton.requested_test_cases is None:
        retval = register_select_test_cases(
            current_test_cases,
            app_singleton.requested_test_cases
        )        
    else:
        retval = {}
        for case in current_test_cases:
            retval[case.__name__] = {}
            retval[case.__name__][case.__module__] = case
    
    app_singleton.registered_test_cases = retval

def get_test_methods(test_case):
    return [method for method in dir(test_case) if method.startswith('test_')]

def load_select_tests(app_singleton: ApplicationSingleton, suite: TestSuite, loader: TestLoader):
    test_found = False
    requested_tests = app_singleton.args.run_specific_tests[:]

    for test in app_singleton.args.run_specific_tests:
        for test_case in app_singleton.registered_test_cases.keys():
            test_case_mods = app_singleton.registered_test_cases[test_case]
            
            for key, test_case in test_case_mods.items():
                if test in get_test_methods(test_case):
                    #accidentally nesting suites:
                    suite.addTest(loader.loadTestsFromName(f"{key}.{test_case.__name__}.{test}"))
                    test_found = True
                    break
            if test_found:
                requested_tests.remove(test)
                break
    if len(requested_tests) > 0:
        common.die(f"Tests not found: {', '.join(requested_tests)}")
                    

def load_tests(app_singleton: ApplicationSingleton):
    test_case = None
    suite = TestSuite()
    loader = TestLoader()

    if app_singleton.args.run_specific_tests:
        load_select_tests(app_singleton, suite, loader)
    else:
        #For all test case name, load all tests from all test
        #cases of that name from all modules that have one.
        for case in app_singleton.registered_test_cases.keys():
            test_case_mods = app_singleton.registered_test_cases[case]
            for module_name, test_case in test_case_mods.items():
                suite.addTests(loader.loadTestsFromTestCase(test_case))
    return suite

def set_test_attribute(suite, attribute, value, test_names = None):
    for test in suite:
        if type(test) == TestSuite:
            set_test_attribute(test, attribute, value, test_names)
        else:
            if test_names is None or test.id().split('.')[-1] in test_names:
                setattr(test, attribute, value)

def main():    
    # 1. Initialization
    app_singleton = validate_and_initialize()
    
    # 2. Module Discovery
    get_module_list(app_singleton)
    
    # 3. Add module directory to Python path
    sys.path.append(app_singleton.module_dir.__str__())
    
    # 4. Module Loading
    load_modules(app_singleton)
    
    # 5. Test Case Registration
    register_test_cases(app_singleton)
    
    # 6. Test Suite Creation
    suite = load_tests(app_singleton)
    
    # 7. Debug Configuration
    if app_singleton.args.breakpoint_all:
        # Enable breakpoints for all tests
        set_test_attribute(suite, "use_breakpoint", True)
    elif app_singleton.args.breakpoint:
        set_test_attribute(suite, "use_breakpoint", True, app_singleton.args.breakpoint)

    # 8. Output Configuration
    if app_singleton.args.print_test_output:
        set_test_attribute(suite, "enable_output_printing", True, app_singleton.args.print_test_output) 
    # 9. Test Execution
    runner = TextTestRunner()
    runner.run(suite)

if __name__ == "__main__":
    main()
