find_package(Python)

set(TEMP "${CMAKE_CURRENT_LIST_DIR}")
file(REAL_PATH "${TEMP}" CURRENT_SCRIPT_DIR)

set(PYTHON_SCRIPT_DIR_PATH "${TEMP}/python")
set(PYTHON_TEST_GENERATOR_SCRIPT_PATH "${PYTHON_SCRIPT_DIR_PATH}/generate-test-file.py")
set(GENERATED_TEST_DIR_PATH "${PYTHON_SCRIPT_DIR_PATH}/tests")



set(TEST_SUCCESS FALSE)

#
# SKIP_GENERATE_FILE is ignored if the generated test file does not exist.
#
function(run_test)
    if(${ARGC} LESS 2)
        message(SEND_ERROR "\"run_test\": Too few arguments.")
        return()
    endif()

    if(${ARGC} GREATER 3)
        message(SEND_ERROR "\"run_test\": Too many arguments.")
        return()
    endif()

    set(options "SKIP_GENERATE_FILE")
    set(oneValueArgs "TEST_SCRIPT_FILE")
    cmake_parse_arguments(run_test ${options} ${oneValueArgs} "" ${ARGN})

    get_filename_component(TEST_SCRIPT_FILENAME "${run_test_TEST_SCRIPT_FILE}" NAME)

    set(TEST_FILE "${GENERATED_TEST_DIR_PATH}/${TEST_SCRIPT_FILENAME}")
    
    if((NOT run_test_SKIP_GENERATE_FILE) OR (NOT EXISTS "${TEST_FILE}"))
        #generate test file
        message(STATUS "Generating test file for \"${run_test_TEST_SCRIPT_FILE}\".")
        execute_process(
            COMMAND "${Python_EXECUTABLE}" "${PYTHON_TEST_GENERATOR_SCRIPT_PATH}" "${run_test_TEST_SCRIPT_FILE}"
            WORKING_DIRECTORY "${CMAKE_CURRENT_LIST_DIR}"
            COMMAND_ERROR_IS_FATAL ANY
        )
    endif()

    #run generated test file
    message(STATUS "Executing test file for \"${run_test_TEST_SCRIPT_FILE}\".")
    execute_process(
        COMMAND "${CMAKE_COMMAND}" -P "${TEST_FILE}"
	    WORKING_DIRECTORY "${CMAKE_CURRENT_LIST_DIR}"
	    COMMAND_ERROR_IS_FATAL ANY
    )

    #If we get to this point, the tests have passed.
    set(TEST_SUCCESS TRUE PARENT_SCOPE)
endfunction()
