find_package(Python3)


set(TEMP "${CMAKE_CURRENT_LIST_DIR}")
file(REAL_PATH "${TEMP}" CURRENT_SCRIPT_DIR)

file(DIRECTORY "${TEMP}" TEMP)

set(PYTHON_TEST_GENERATOR_SCRIPT_PATH "")
set(TEMP "${PYTHON_TEST_GENERATOR_SCRIPT_PATH}/python/generate-test-file.py")

function(run_test)
   set(TEST_SCRIPT_FILENAME "${CMAKE_CURRENT_LIST_FILE}")
   file(NAME ${TEST_SCRIPT_FILENAME} TEST_SCRIPT_FILENAME)

    #generate test file
    execute_process(
	COMMAND "${Python::Interpreter}" ${CMAKE_CURRENT_LIST_FILE}
	WORKING_DIRECTORY "${CMAKE_CURRENT_LIST_DIR}"
	COMMAND_ERROR_IS_FATAL ANY
    )

    #run generated test file
    execute_process(
        COMMAND "${CMAKE_COMMAND}" -P "${TEST_SCRIPT_FILENAME}"
	WORKING_DIRECTORY "${CMAKE_CURRENT_LIST_DIR}"
	COMMAND_ERROR_IS_FATAL ANY
    )

endfunction()
