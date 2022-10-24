########################################################################
########################################################################
####
#### Test harness for testing functions in other routines
####
########################################################################
########################################################################

####
#### Import support modules
####

import re
import sys
import traceback

####
#### Global definitions
####

#
#Simple exception to be used if error and halt
#
class TestHarnessError(Exception):
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
    #If an error while trying to get a type name, throw and exception
    #
    try:
        return xlate.__name__
    except:
        raise TestHarnessError("Argument passed to type_to_text was not a type")

def format_argument(module_name, argument):
    #
    #Make the argument [somewhat] pretty
    #

    #
    #If the argument has a name, translate it. This causes
    #functions to display their names rather than their
    #classes.
    #
    try:
        arg = argument.__name__
        #
        #Special check for "NoneType" to change it back to
        #type(None)
        #
        if isinstance(argument, type):
            if arg == "NoneType":
                return("type(None)")

        return module_name + "." + arg

    except:
        #
        #Continue processing argument
        #
        pass

    #
    #If it's a string, put ', " or """s around it so it can
    #be cut and pasted as a legitimate string.
    #
    if isinstance(argument, str):
        single = re.search(r"'", argument)
        double = re.search(r'"', argument)
        if re.search(r'\n', argument) or (single and double):
            quotes = '"""'
        elif double:
            quotes = "'"
        else:
            quotes = '"'
        return quotes + argument + quotes

    #
    #If it's a tuple or list, list it out
    #
    if isinstance(argument, (tuple, list)):
        args = ""
        fstring = "{}"
        if isinstance(argument, (tuple, list)):
            for arg in argument:
                args += fstring.format(format_argument(module_name, arg))
                fstring = ",{}"
            if isinstance(argument, list):
                return "[" + args + "]"
            else:
                if len(argument) == 1:
                    return "(" + args + ",)"
                else:
                    return "(" + args + ")"

    #
    #If it's a dictonary, sort and list it out
    #
    if isinstance(argument, dict):
        args = ""
        fstring = "{}:{}"
        for key, value in argument.items():
            args += fstring.format(format_argument(module_name, key), format_argument(module_name, value))
            fstring = ",{}:{}"
        return "{" + args + "}"
    #
    #Nothing special, just return the argument as a string
    #
    return "{}".format(argument)

####
#### Test functions
####

def execute_function(function2test, args):

    try:
        return(None, function2test(*args))

    except Exception as ex:
        #
        #Exception, return exception string and the last line of the
        #exception, which contains the actual exception.
        #
        ex_text = traceback.format_exc()
        return (ex_text, ex_text.split("\n")[-2])

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

    if re.match(exception_text, data):
        #
        #Correct exeception returned, return True
        #
        print(exception)
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

def display(function2test, args, notes):

    (exception, data) = noexception(function2test, args)

    if exception:
        #
        #Not expecting an exception
        #
        return(False)

    print(data)
    if notes:
        print("\n### Display note-> {}".format(notes))
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

validation_mapping = (compare, display, exception)

def TestHarness(module_name, validation_tests):
    total = 0
    test_number = 0
    total_errors = []
    for function_and_tests in validation_tests:
        test_number += 1
        #
        #Build the name of the function to test in the calling module.
        #
        function = function_and_tests[0]
        try:
            function_name = function.__name__
        except:
            raise TestHarnessError("Function.__name__ does not exist.")

        if not callable(function):
            #
            #The function is not callable, throw exception
            #
            msg = 'Function "{}" is not callable, cannot test.'.format(function_name)
            raise TestHarnessError(msg)

        subtest_number = 0
        for test_function, arguments, data_expected in function_and_tests[1:]:
            #
            #Build test number in case we need to report any errors
            #
            subtest_number += 1
            test_string = "{} - {}".format(test_number, subtest_number)

            #
            #Make sure a valid test function was specified
            #
            if test_function not in validation_mapping:
                msg = """Test {}, not a valid test function""".format(test_string)
                raise TestHarnessError(msg)

            #
            #Make the arguments [somewhat] pretty
            #
            fstring = "\n    {}"
            args = ""
            for arg in arguments:
                args += fstring.format(format_argument(module_name, arg))
                fstring = ",\n    {}"

            #
            #Print the test call (without expected data) for logging purposes
            #
            print("""Test {} : {}

{}({}
    )""".format(test_string, test_function.__name__, function_name, args))

            #
            #Execute the test function which will call the function under
            #test. 
            #
            if test_function(function, arguments, data_expected):
                print(80 * "." + "\n")
            else:
                print(80 * "X" + "\n")
                total_errors.append(test_string)

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

def test_test(what_to_do):
    if what_to_do:
        return eval(what_to_do)
    else:
        raise TestHarnessError("Expected to do something")

validation_tests = (
    (
    type_to_text,
        (
        exception,
            ("TEST",),
            "TestHarness.TestHarnessError"
        ), #Not a type
        (
        compare,
            (type(None),),
            "NoneType"
        ),
        (
        compare,
            (dict,),
            "dict"
        ),
    ),

    (
    format_argument,
        (
        compare,
            (__name__, 7),
            "7"
        ),

        (
        compare,
            (__name__, "Foo"),
            '"Foo"'
        ),

        (
        compare,
            (__name__, (1,2)),
            "(1,2)"
        ),

        (
        compare,
            (__name__, [2,3]),
            "[2,3]"
        ),

        (
        compare,
            (__name__, test_test),
            "TestHarness.test_test"
        ),

        (
        compare,
            (__name__, {test_test:format_argument, format_argument:test_test}),
            "{TestHarness.test_test:TestHarness.format_argument,TestHarness.format_argument:TestHarness.test_test}"
        ),

        (
        compare,
            (__name__, {7:7, "foo":"bar", format_argument:test_test, (1,2):[10,20]}),
            '{7:7,"foo":"bar",TestHarness.format_argument:TestHarness.test_test,(1,2):[10,20]}'
        ),
    ),

    (
    execute_function,
        (
        display,
            (test_test, (None,)),
            "Should be a traceback"
        ),
        (
        display,
            (test_test, ("4 * 2",)),
            "Should be (None, 8)"
        ),
        (
        compare,
            (test_test, ("4 * 2",)),
            (None, 8)
        ),
    ),

    (
    test_test,
        (
        exception,
            (None,),
            "TestHarness.TestHarnessError"
        ), #Expected exception

        (
        compare,
            ("(1,2,3)",),
            (1,2,3)
        ),

        (
        display,
            ('"This should be printed"',),
            '"This should be printed" should be printed'
        ),
    ),

    (
    noexception,
        (
        compare,
            (type_to_text, (dict,)),
            (False, "dict")
        ),
    )
)

def run_tests():
    #
    #Run all validation tests
    #
    TestHarness(__name__, validation_tests)
