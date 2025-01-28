include(cmake-test-runner.cmake)
run_test(TEST_SCRIPT_FILE "test-file.cmake")
run_test(TEST_SCRIPT_FILE "test-file.cmake" SKIP_GENERATE_FILE)
