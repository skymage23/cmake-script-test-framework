
#*******************************************************
# This is a generated file that is usually destroyed
# after it is used. Any changes to this file will be
# discarded. Instead, make your changes to the descriptor
# file used to generate this file.
#*******************************************************
#*****************
# Includes:
#*****************
include("cmake-test.cmak")
include("${CMAKE_CURRENT_LIST_DIR}/test-include.cmak")

#************************
# Command Definitions:
#************************
function(am_i_a_bro)message(STATUS "Yes.")endfunction()
macro(setup)message(STATUS "I am the Setup macro.")endmacro()
macro(teardown)message(STATUS "I am the Teardown macro.")endmacro()
macro(test)message(STATUS "I am the Test macro.")am_i_a_bro()endmacro()
macro(grouptester_test1)message(STATUS "I am grouptester_test1.")endmacro()
macro(grouptester_test2)message(STATUS "I am grouptester_test2.")endmacro()
macro(grouptester2_test1)message(STATUS "I am grouptester2_test1.")endmacro()
macro(grouptester2_test2)message(STATUS "I am grouptester2_test2.")endmacro()
#************************
# Tests: 
#************************
#*
#* Test Group: test
#*
#*************************
setu()
test()
teardow()

#*
#* Test Group: grouptester
#*
#*************************
setu()
grouptester_test1()
grouptester_test2()
teardow()

#*
#* Test Group: grouptester2
#*
#*************************
setu()
grouptester2_test1()
grouptester2_test2()
teardow()

