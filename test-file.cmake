include (cmake-test.cmake)
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

add_setup_macro(MACRO_NAME setup)
add_teardown_macro(MACRO_NAME teardown)
add_test_macro(MACRO_NAME test)
