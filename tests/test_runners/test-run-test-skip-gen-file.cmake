include(${CMAKE_CURRENT_LIST_DIR}/../../cmake-test-runner.cmake)
run_test(TEST_SCRIPT_FILE "${CMAKE_CURRENT_LIST_DIR}/../test_files/test-file.cmake" SKIP_GENERATE_FILE)
