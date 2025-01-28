
#*******************************************************
# This is a generated file that is usually destroyed
# after it is used. Any changes to this file will be
# discarded. Instead, make your changes to the descriptor
# file used to generate this file.
#*******************************************************
#*****************
# Includes:
#*****************

#************************
# Command Definitions:
#************************
function(check_macro_exists MACRO_NAME)
    if (NOT COMMAND ${MACRO_NAME})
        message(FATAL_ERROR "Macro ${MACRO_NAME} does not exist")
    endif()
endfunction()

function(add_test_macro)
    if(${ARGC} LESS 2)
        message(FATAL_ERROR "add_setup_macro:  Too few arguments.")
    endif()

    message(STATUS ${ARGN})
    message(STATUS ${ARGC})
    if(${ARGC} GREATER 4)
        message(FATAL_ERROR "add_setup_macro:  Too many arguments.")
    endif()

    if(${ARGC} EQUAL 3)
        message(FATAL_ERROR "add_setup_macro:  TEST_GROUP declared, but none provided.")
    endif()

    set(oneValueArgs MACRO_NAME TEST_GROUP)
    cmake_parse_arguments(
        arg_test_macro
        ""
        "${oneValueArgs}"
        ""
        ${ARGN}
    )

    if(NOT arg_test_macro_MACRO_NAME)
        message(FATAL_ERROR "MACRO_NAME argument not specified.")
    endif()

    if(NOT TEST_GROUP)
        set(TEST_GROUP "${arg_test_macro_MACRO_NAME}")
    endif()

    message(STATUS "CMake lint test: add_test_macro: ${arg_test_macro_MACRO_NAME} ${TEST_GROUP}")

    check_macro_exists(${arg_test_macro_MACRO_NAME})
endfunction()

function(add_setup_macro)
    if(${ARGC} LESS 2)
        message(FATAL_ERROR "add_setup_macro:  Too few arguments.")
    endif()

    if(${ARGC} GREATER 2)
        message(FATAL_ERROR "add_setup_macro:  Too many arguments.")
    endif()

    set(options "")
    set(oneValueArgs "MACRO_NAME")
    set(multiValueArgs "")

    cmake_parse_arguments(arg_setup
        "${options}"
        "${oneValueArgs}"
        "${multiValueArgs}"
        ${ARGN}
    )

    if(NOT arg_setup_MACRO_NAME)
        message(FATAL_ERROR "MACRO_NAME argument not specified.")
    endif()

    message(STATUS "CMake lint test: add_setup_macro: ${arg_setup_MACRO_NAME}")
    check_macro_exists(${arg_setup_MACRO_NAME})
endfunction()

function(add_teardown_macro)
    if(${ARGC} LESS 2)
        message(FATAL_ERROR "add_setup_macro:  Too few arguments.")
    endif()

    if(${ARGC} GREATER 2)
        message(FATAL_ERROR "add_setup_macro:  Too many arguments.")
    endif()

    set(oneValueArgs MACRO_NAME)
    cmake_parse_arguments(
        arg_teardown
        ""
        "${oneValueArgs}"
        ""
        ${ARGN}
    )

    if(NOT arg_teardown_MACRO_NAME)
        message(FATAL_ERROR "MACRO_NAME argument not specified.")
    endif()

    message(STATUS "CMake lint test: add_teardown_macro: ${arg_teardown_MACRO_NAME}")
    check_macro_exists(${arg_teardown_MACRO_NAME})
endfunction()

#************************
# Tests: 
#************************
