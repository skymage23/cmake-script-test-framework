#!/usr/bin/env python3
from unittest import TestSuite, TestLoader, TextTestRunner
import argparse
import sys

from filepath_helper_tests import TestFilepathHelper
from helper_function_tests_no_context import TestFileGenerationHelperNoContextTests
from helper_function_tests_with_context import TestHelperFunctionsRequiringContext
from test_file_generation_tests import TestFileGenerationTests
from var_expansion_testing import TestVarExpansionParsing

def die(message):
    print(message, file=sys.stderr)
    exit(1)

def load_test_cases(args, registered_test_cases):
    suite = TestSuite()
    loader = TestLoader()
    if not args.testcases:
        for test_class in registered_test_cases.values():
            suite.addTests(TestLoader().loadTestsFromTestCase(test_class))
    else:
        valid_cases = [case.strip() for case in args.testcases if case.strip()]
        if not valid_cases:
            die("Error: No valid test cases provided. Use -c with a test group name.")
        for case in valid_cases:
            if case not in registered_test_cases:
                die(f"Error:  \"{case}\" isn't a valid test group. Use --list-tests to see available options.")
            test_class = registered_test_cases[case]
            if args.run_specific_tests:
                valid_tests = [test.strip() for test in args.run_specific_tests if test.strip()]
                if not valid_tests:
                    die("Error: No valid test names provided with -t. Use test method names.")
                invalid_tests = []
                for test in valid_tests[:]:  # Copy to allow removal
                    method = getattr(test_class, test, None)
                    if method:
                        test_name = f"{test_class.__name__}.{test}"
                        suite.addTest(loader.loadTestsFromName(test_name))
                        args.run_specific_tests.remove(test)
                    else:
                        invalid_tests.append(test)
                if invalid_tests:
                    die(f"Tests not found in {case}: {', '.join(invalid_tests)}")
            else:
                suite.addTests(TestLoader().loadTestsFromTestCase(test_class))
    return suite

def set_test_attribute(suite, attribute, value, test_names = None):
    for test in suite:
        if test_names is None or test.id().split('.')[-1] in test_names:
            setattr(test, attribute, value)

def main():
    parser = argparse.ArgumentParser(description='Run unit tests with breakpoint control')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--breakpoint-all', '-ba', action='store_true', 
                      help='Enable breakpoints for all tests')
    group.add_argument('--breakpoint', '-b', nargs='+', 
                      help='Enable breakpoints for specific test names. Ignored if "--breakpoint-all" is specified.')

    group.add_argument('--testcases', '-c', nargs='+',
                       help = "Run specific test cases.") 
    
    group.add_argument('--run-specific-tests', '-t', nargs='+',
                        help="Run specific tests. Only these will be executed."),
    
    group.add_argument('--print-test-output','-p', nargs='+',
                      help="Enable output printing for specific test names.")
    args = parser.parse_args()

    # Create a test suite
    suite = TestSuite()

    if args.run_specific_tests and not args.testcases:
        parser.error("--run-specific-tests (-t) requires --testcases (-c).")

 
    registered_test_cases  = {}
    registered_test_cases["TestFilepathHelper"] = TestFilepathHelper
    registered_test_cases["TestFileGenerationHelperNoContextTests"] = TestFileGenerationHelperNoContextTests
    registered_test_cases["TestHelperFunctionsRequiringContext"] = TestHelperFunctionsRequiringContext
    registered_test_cases["TestFileGenerationTests"] = TestFileGenerationTests
    registered_test_cases["TestVarExpansionParsing"] = TestVarExpansionParsing

    
    suite = load_test_cases(args, registered_test_cases)
    
    # Enable breakpoints based on arguments
    if args.breakpoint_all:
        # Enable breakpoints for all tests
        set_test_attribute(suite, "use_breakpoint", True)
    elif args.breakpoint:
        set_test_attribute(suite, "use_breakpoint", True, args.breakpoint)

    #Enable printing only for specified tests:
    if args.print_test_output:
        for test in suite:
            if test.id().split('.')[-1] in args.print_test_output:
                test.enable_output_printing = True
            
    # Run the tests
    runner = TextTestRunner()
    runner.run(suite)

if __name__ == "__main__":
    main()
