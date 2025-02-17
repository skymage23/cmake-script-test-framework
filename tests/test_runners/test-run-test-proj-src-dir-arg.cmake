include(${CMAKE_CURRENT_LIST_DIR}/../../cmake-test-runner.cmake)
run_test(TEST_SCRIPT_FILE "${CMAKE_CURRENT_LIST_DIR}/../test_files/test-file.cmake" PROJECT_SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}")