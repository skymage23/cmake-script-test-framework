include_guard(GLOBAL)
find_package(Python)
if(${CMAKE_HOST_SYSTEM_NAME} STREQUAL "Darwin")
  message(WARNING "You appear to be trying to run this script on a mac.
Please be advised that the version of Python shipped with macOS by
default may be too old to run the test file generation script. You
may have to install a newer version of Python (say, using Homebrew)
and alter your PATH environment variable so that this new version
of Python will be found before (or in place of) the default version.
")
endif()


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

    if(${ARGC} GREATER 5)
        message(SEND_ERROR "\"run_test\": Too many arguments.")
        return()
    endif()

    set(options "SKIP_GENERATE_FILE")
    set(oneValueArgs "TEST_SCRIPT_FILE" "PROJECT_SOURCE_DIR")
    cmake_parse_arguments(run_test ${options} ${oneValueArgs} "" ${ARGN})
 
    if(NOT run_test_TEST_SCRIPT_FILE)
        message(FATAL_ERROR "TEST_SCRIPT_FILE was not specified.")
    endif()

    if(NOT run_test_PROJECT_SOURCE_DIR)

    endif()

    get_filename_component(TEST_SCRIPT_FILENAME "${run_test_TEST_SCRIPT_FILE}" NAME)

    set(TEST_FILE "${GENERATED_TEST_DIR_PATH}/${TEST_SCRIPT_FILENAME}")
    
    if((NOT run_test_SKIP_GENERATE_FILE) OR (NOT EXISTS "${TEST_FILE}"))
        set(cmd_list "")
        list(APPEND cmd_list "${Python_EXECUTABLE}")
        list(APPEND cmd_list "${PYTHON_TEST_GENERATOR_SCRIPT_PATH}")
        list(APPEND cmd_list "-b" "${CMAKE_BINARY_DIR}")
        list(APPEND cmd_list "-c" "${CMAKE_SOURCE_DIR}")

        if(run_test_PROJECT_SOURCE_DIR)
            #Hello:
            list(APPEND cmd_list "-p" "${run_test_PROJECT_SOURCE_DIR}")
        endif()
        list(APPEND cmd_list "${run_test_TEST_SCRIPT_FILE}") 
        
        foreach(str  ${cmd_list})
            message(STATUS ${str})
        endforeach()

        #generate test file
        execute_process(
		    COMMAND ${cmd_list}
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
