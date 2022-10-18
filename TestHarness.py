#!/usr/bin/python3

########################################################################
########################################################################
####
#### Validate all functions and error detection in hamlibIO.py
####
########################################################################
########################################################################

####
#### Import support modules
####

import hamlibIO
import re
import sys

####
#### Global definitions
####

#
#Simple exception to be used if error and halt
#
class TestHarness(Exception):
    """
    Exception for TestHarness so we generate a stack trace and
    exit
    """
    pass

def type_to_text(xlate) -> str:  
    """
    Translate a data type to a printable string. 

    Arguments:
        xlate:
            The type to translate to a printable string.

    Returns:
        Can translate the type to a printable string:
            A text string of the type.
        Unable to translate the type to a printable string:
            Print the error, the stack and exit.
    """ 

    #
    #If an erro while trying to get a type name, throw and exception
    #
    try:
        return xlate.__name__
    except:
        raise TestHarness("Argument passed to type_to_text was not a type")

####
#### Test functions
####

def execute_function(function2test, args):

    test_call = "{}({})".format(function2test, args)
    try:
        return(None, eval(test_call))

    except Exception as ex:
        #
        #Exception, return exception string
        #
        return("{}{}".format(type(ex).__name__, ex.args), None)

def noexception(function2test, args):

    (exception, data) = execute_function(function2test, args)

    if exception:
        #
        #Unexpected exception
        #
        print("""
TestHarnessError: Unexpected exception raised.
    {}
""".format(exception))
        return(True, data)
    #
    #Return True and data
    #
    return(False, data)

def exception(function2test, args, exception_text):

    (exception, data) = execute_function(function2test, args)

    if not exception:
        #
        #If it was supposed to cause an exception, report
        #
        print("""
TestHarnessError: Exception should have been generated.
    """)
        return False

    if re.match(exception_text, exception):
        #
        #Correct exeception returned, return True
        #
        print("""
{}""".format(exception))
        return True

    #
    #Unexpected exception
    #
    print("""
TestHarnessError: Unexpected exception raised.
    {}
""".format(exception))
    #
    #Print error dividing line
    #
    return False

def display(function2test, args, bitbucket):

    (exception, data) = noexception(function2test, args)

    if exception:
        #
        #Not expecting an exception
        #
        return(False)

    print(data)
    return True


def compare(function2test, args, data_expected):

    (exception, data) = noexception(function2test, args)

    if exception:
        #
        #Not expecting an exception
        #
        return(False)

    expected_type = type(data_expected)

    #
    #Make sure we got back the expected data type and data value.
    #
    if isinstance(data, expected_type):
        if data == data_expected:
            #
            #Data returned is expected type and data
            #
            return True
        else:
            #
            #Data returned does not match expected data
            #
            print   ("""
TestHarnessError: Data returned does not match data expected.
""")
    else:
        #
        #Type returned does not match type expected
        #
        print("""
TestHarnessError: Expected type of data returned was "{}",
                 but type "{}" was returned instead.
""".format(type_to_text(expected_type),
    type_to_text(type(data))))

    #
    #Print expected and returned data
    #
    print("""
Expected data:
{}""".format(data_expected))

    print("""
Received data:
{}""".format(data))

    return False

validation_mapping = {
    compare : "compare",
    display : "display",
    exception : "exception"
    }
    


def run_tests(module_name, test_list):
    total = 0
    total_errors = []
    for (sort_num, function), arguments in sorted(test_list.items()):
        #
        #Build the name of the function to test in the calling module.
        #
        function_under_test = module_name + "." + function

        if not callable(eval(function_under_test)):
            #
            #The function name to test is not callable, throw exception
            #
            msg = """Function "{}" not callable, cannot test.""".format(function_under_test)
            raise TestHarness(msg)

        subtest = 0
        for test_args in arguments:
            #
            #Build test number in case we need to report any errors
            #
            subtest += 1
            test_number = "{}-{}".format(sort_num, subtest)
            #
            #Make sure we have the right number of arguments
            #
            if (len(test_args) < 2) or (len(test_args) > 3):
                #
                #Not enough arguments
                #
                msg = "Test {} must have 2-3 arguments".format(test_number)
                raise TestHarness(mgs)

            #
            #Splitup tuple and set data_expected to "None" if no data
            #expected.
            #
            if len(test_args) == 2:
                #
                #Splitup tuple and set 
                (test_function, arguments) = test_args
                data_expected = None
            else:
                (test_function, arguments, data_expected) = test_args

            #
            #Make sure a valid test function was specified
            #
            if test_function not in validation_mapping:
                msg = """Test {}, not a valid test function""".format(test_number)
                raise TestHarness(msg)

            #
            #Build the full call to the testing function except for the
            #data to compare against (if any) and leave off the closing )
            #for printing purposes (we don't want to print expected data in
            #case it's long and complex)
            #
            test_call = "{}( {}( {} )".format(
                validation_mapping[test_function],
                function_under_test,
                arguments)

            #
            #Print the test call (without expected data) for logging purposes
            #
            print("""
    Test {} - {}: {}( {} )
    """.format(test_number, validation_mapping[test_function], function_under_test, arguments))

            #
            #Execute the test function which will call the function under
            #test. 
            #
            if test_function(function_under_test, arguments, data_expected):
                print(80 * "." + "\n")
            else:
                print(80 * "X" + "\n")
                total_errors.append(test_number)

            #
            #Increment number of tests sucessfully performed (note that
            #this isn't the number of SUCCESSFUL tests!)
            #
            total += 1

    #
    #Print out failed tests, if any.
    #
    print("{} tests run".format(total))
    failed_tests = ", ".join(total_errors)
    if failed_tests:
        print("Failed test numbers: " + failed_tests)
    else:
        print("No failed tests")


