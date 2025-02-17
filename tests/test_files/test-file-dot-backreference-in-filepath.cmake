include ("${CMAKE_CURRENT_LIST_DIR}/../../cmake-test.cmake")
include("${CMAKE_CURRENT_LIST_DIR}/test_helper_dir/../test-include.cmake")
function(am_i_a_bro)
    message(STATUS "Yes.")
endfunction()

macro(setup)
    message(STATUS "I am the Setup macro.")
endmacro()

macro(teardown)
    message(STATUS "I am the Teardown macro.")
endmacro()

macro(test)
    message(STATUS "I am the Test macro.")
    am_i_a_bro()
endmacro()

macro(grouptester_test1)
    message(STATUS "I am grouptester_test1.")
endmacro()

macro(grouptester_test2)
    message(STATUS "I am grouptester_test2.")
endmacro()

macro(grouptester2_test1)
    message(STATUS "I am grouptester2_test1.")
endmacro()

macro(grouptester2_test2)
    message(STATUS "I am grouptester2_test2.")
endmacro()

add_setup_macro(MACRO_NAME setup)
add_teardown_macro(MACRO_NAME teardown)
add_test_macro(MACRO_NAME test)
add_test_macro(MACRO_NAME grouptester_test1 TEST_GROUP grouptester)
add_test_macro(MACRO_NAME grouptester_test2 TEST_GROUP grouptester)
add_test_macro(MACRO_NAME grouptester2_test1 TEST_GROUP grouptester2)
add_test_macro(MACRO_NAME grouptester2_test2 TEST_GROUP grouptester2)
