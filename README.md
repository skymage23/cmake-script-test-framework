# cmake-script-test-framework
A simple framework for testing CMake scripts. Supports test fixtures and test groups.

To use, write a test descriptor file using by including "cmake-test.cmake" in your script
and then using the included macros to define the test fixture setup and teardown, and the 
tests themselves.

To actually run the tests, include "cmake-test-runner.cmake" and call "run_test",
passing in the filepath to your test descriptor file.

For now, we don't have any CI.  Tests will have to run manually by invoking

cmake -P framework-tester.cmake

.

A word of warning: If you are running this script on macOS, the default Python
install included with the OS may be too old to run the test generation script.
You may have to install a newer Python versio and have it put on the system
PATH so that the new version will be found before (or in place of)
the default macOS install.
