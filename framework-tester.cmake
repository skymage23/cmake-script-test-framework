include(cmake-test-runner.cmake)

function(pretty_print INPUT)
    message(STATUS "")
    message(STATUS "")
    message(STATUS "*")
    message(STATUS "* ${INPUT}")
    message(STATUS "***************************")
    message(STATUS "")
endfunction()

pretty_print("Running \"run_test\" on test-file.cmake")
run_test(TEST_SCRIPT_FILE "test-file.cmake")

pretty_print("Running \"run_test\" on test-file.cmake and with the SKIP_GENERATE_FILE flag.")
run_test(TEST_SCRIPT_FILE "test-file.cmake" SKIP_GENERATE_FILE)

pretty_print("Running \"run_test\" on test-file-var-in-include.cmake")
run_test(TEST_SCRIPT_FILE "test-file-var-in-include-path.cmake")

pretty_print("Running \"run_test\" on test-file-relative-path.cmake")
run_test(TEST_SCRIPT_FILE "test-file-relative-path.cmake")

pretty_print("Running \"run_test\" on test-file-quotes-around-important-names.cmake")
run_test(TEST_SCRIPT_FILE "test-file-quotes-around-important-names.cmake")


