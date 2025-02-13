include(cmake-test-runner.cmake)
run_test(TEST_SCRIPT_FILE "test-file.cmake" SKIP_GENERATE_FILE PROJECT_SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}")
