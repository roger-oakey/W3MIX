


import calendar
import os
import re
import sys
import time
import traceback

#
#Global variables
#

ADIF_VERSION = "3.1.3"
ADIF_VERSION_FIELD = "ADIF_VER"

default_split = r'[,:;\s\t]+'
helpfile_extension = ".help"
adiffile_extension = ".adif"
tuple_or_list = (tuple, list)

cr = "\r"
lf = "\n"
crlf = cr + lf
crlf_re = r'\r\n'
cr_or_lf_re = r'[\r\n]'
onlycr_re = r'\r[^\n]'
onlylf_re = r'[^\r]\n'

end_of_header = "<EOH>"
end_of_record = "<EOR>"

#
#XML information for ADX support
#
adx_first_line = '<?xml version="1.0" encoding="UTF-8"?>'
adx_adx     = "<ADX>"
adx_header  = "    <HEADER>"
adx_records = "    <RECORDS>"
adx_record  = "        <RECORD>"

#
#Simple hamlib.py exception to be used if error and halt
#
class HamlibError(Exception):
    """
    Exception for hamlib.py so we generate a stack trace
    """
    pass

########################################################################
########################################################################
#
# If a .help file exists for this Python script, read it in so it can be
# printed if the user types "help".
#
########################################################################
########################################################################

#
#Script help file must be in the same directory as the script, and have
#the same name of the script with ".help" added to the end of it.
#
script_path = os.path.abspath(sys.argv[0])
script_help = script_path + helpfile_extension

#
#See if a help file exists
#
if os.path.exists(script_help):
    #
    #If the help file exists, read it in
    #
    f = open(script_help, "r")
    script_help = f.read()
    f.close()
else:
    #
    #No help file report no help
    #
    script_help = """
No script help file.
"""

def generate_stack_trace(skip_depth:int=1) -> str:
    """
    Generate a stack trace to display so the point of failure for
    critical errors that can cause crashes can be found quickly.

    Arguments:
        skip_depth:
            Number of deepest functions to skip. Typically 1 to avoid
            this function from showing up in the stack dump (make the
            top of the displayed stack show where the error was, not
            this function).

    Returns:
        String containing stack trace
    """

    #
    #Generate stack trace and remove specified number of entries from end.
    #Add tiemstamp and lines around it to make it look pretty.
    #
    stack = list(traceback.format_stack())
    stack =  """
========================================================================

{}
========================================================================



""".format(
           #
           #Remove top entries on stack to eliminate the reporting
           #function(s). In other words, "declutter" the stack so it
           #ends with the function that actually caused the error, not
           #the functions printing the stack.
           #
           ''.join(stack[:-abs(skip_depth)]))

    return stack

def validate_arg_type(args_to_check) -> None:
    """
    Check arguments against valid type(s).

    Note: ALWAYS dumps trace and exits if an error detected. The
          assumption here is that argument type problems are a
          programming error and things should halt immediately with a
          good diagnostic.

          Problems with the argument valididity tuples (or lists) cause
          an immediate error and stack trace.

          Problems with the function variables themselves (wrong type)
          are gathered and ONE error is with all the arguments that have
          invalid types is printed.

    Arguments:
        args_to_check:  A table of arguments and valid types for each
            argument. The table is a tuple (preferred) or list,
            containing tuples (preferred) or a list that contains the
            argument and the type(s) that are valid for the argument.
            Ideally, these valid-argument-type tuples have the same
            order as the arguments in the function definition for
            readibility, consisting of:

            (
             (arg0,),                       # No type checking
             (arg1, typeA),                 # arg1 must be typeA
             (arg2, typeA, typeB, typeC),   # arg2 must be typeA, typeB
                                              or typeC
             .
             .
             .
             (argN, ...)                    # Any number of arguments or
                                              types may be specified
            )

            Each entry in args_to_check is also a tuple (preferred) or
            list which consists of the argument to check followed by one
            or more valid types of that argument.

            typeA, typeB, ... One or more valid types that "argN" can
                be, such as "str" or "tuple", "list" or "set",not in
                quotes and separated by commas. If no types are
                specified, anytype is allowed.

            Examples:
               (
                (anything,),               # anything can be any type
                (pi, float),               # pi must be type float
                (days, int),               # days must be type int
                (cars, tuple, list),       # cars may be a tuple or a
               )                             list

    Returns:
        All arg types valid and table correctly formatted:
            Returns None.
        Any arg types invalid or table malformed:
            Prints the error(s), the stack trace and exits.
    """

    def type_xlate(xlate) -> str:  
        """
        Translate a data type to a printable string. Special check for
        the NoneType to return "None". If error, report, dump stack and
        halt.

        Arguments:
            xlate:
                The type to translate to a printable string.

        Returns:
            Can translate the type to a printable string:
                A text string of the type.
            nable to translate the type to a printable string:
                Print the error, the stack and exit.
        """ 

        #
        #Special check to return "None" for "NoneType"
        #
        if xlate is type(None):
            return "None"

        #
        #Try and translate type to string
        #
        try:
            return xlate.__name__
        except:
            sys.stderr.write("""
ArgError: Unable to translate type "{}" to string.""".format(xlate))

        #
        #Don't return, throw exception to generate trace
        #
        raise HamlibError("validate_arg_type type translation error")

    def process_type(arg_off:int,
                     type_off:int,
                     one_type) -> type:
        """
        Make sure the agrument passed in "one_type" is of type "type" or
        None. If None, return type(None) - this allows "None" to be
        specified in the argument's type list rather than "NoneType"
        which can only be generated by "type(None)" - making it a bit
        clunky. So we allow "None" to be specified as a type and fix it
        up here.

        Arguments:
            arg_off:
                Offset into argument list for error reporting.
            type_off:
                Offset into type list for error reporting.
            one_type:
                The type to verify that it is in fact a type.

            See "validate_arg_type" for a more detailed description of
            the type options.

        Returns:
            one_type is of type "type":
                The type. In the case of None, NoneType
            one_type is not of type "type":
                Print the error that the type is NOT a valid type, dump
                the stack and exit.
        """

        #
        #Special check for None, return NoneType (this is because
        #there's no easy way to specify "NoneType" as a type as there is
        #for "str" or "int". So for argument type checking allow "None"
        #to be specified as a "type" and do a special check for it here
        #and chenage it to "NoneType".
        #
        if one_type is None:
            return type(None)

        #
        #If it's a type, return the type
        #
        if isinstance(one_type, type):
            return one_type

        #
        #Type given is not a valid type, report error
        #
        sys.stderr.write("""
ArgError: Element at offset {}, type offset {} is not a type or None.
""".format(arg_off, type_off))

        #
        #Don't return, throw exception to generate trace
        #
        raise HamlibError("validate_arg_type parameter error")

    def process_var_types(arg_off:int, var_and_valid_types) -> None:
        """
        Make sure the argument table is correctly formed, then validate
        that the argument is one of the valid listed types.

        Arguments:
            arg_off:
                Offset into argumetn list for error reporting.
            var_and_valid_types:
                The argument to test, followed by the valid types it
                may be. For example:

            (arg,)
            (arg, typeA)
            (arg, typeA, typeB, typeC, ...)

            See "validate_arg_type" for a more detailed description of
            the type options.

        Returns:
            Table valid and argument is a one of the valid types:
                Null string ("")
            Table malformed:
                 Print an error and immediately exit.
            Argument not a type found in the valid list:
                Return the text of the error found.
        """

        #
        #Check to assure var_and_valid_types is a valid ordered type
        #
        if not isinstance(var_and_valid_types, tuple_or_list):
            sys.stderr.write("""
ArgError: Element at offset {} is not a tuple or list. Should be an
          tuple or list starting with the function argument followed by
          a list of zero or more valid types.
""".format(arg_off)
    + generate_stack_trace())

            #
            #Don't return, throw exception to generate trace
            #
            raise HamlibError("Function argument error")

        #
        #If tuple or list has no entries, error
        #
        if not var_and_valid_types:
            sys.stderr.write("""
ArgError: Element at offset {} is an empty tuple or list. Should be an
          tuple or list starting with the function argument followed by
          a list of zero of more valid types for that argument.
""".format(arg_off))

            #
            #Don't return, throw exception to generate trace
            #
            raise HamlibError("validate_arg_type parameter error")

        #
        # (arg,)
        #
        #If the argument is the only thing in the tuple or list, so any
        #type is valid - we're done checking.
        #
        #
        if len(var_and_valid_types) == 1:
            #
            #Argument can be of ANY type, so no error. Return null
            #string.
            #
            return ""

        #
        # (arg, type0)
        # (arg, type0, type1)
        # (arg, type0 ... ,typeN)
        #
        #Now iterate through the types and validate that they're
        #legitimate data types and they're not duplicated. Do this by
        #skipping the first element of the tuple (or list) - which is
        #the variable itself - by slicing off the first element via a
        #[1:]. To report a correct offset within the tuple (or list)
        #start the offset counting at 1 via enumerate's start=1 option.
        #
        valid_types = {}
        for index, typ in enumerate(var_and_valid_types[1:], start=1):
            #
            #Determine type, validate and store options specified
            #
            hold_type = process_type(arg_off, index, typ)

            #
            #Check to see if type previously specified
            #
            if hold_type in valid_types:
                #
                #Report duplicate type
                #
                sys.stderr.write("""
ArgError: Element at offset {} has duplicate definitions of type
          "{}" at offsets {} and {}"
""".format(arg_off,
        type_xlate(hold_type),
        valid_types[hold_type],
        index)
    + generate_stack_trace())

                #
                #Don't return, throw exception to generate trace
                #
                raise HamlibError("validate_arg_type parameter error")

            #
            #Save new type
            #
            valid_types[hold_type] = index

        #
        #Validation tuplet (or list) is correctly formatted, now
        #validate the argument
        #
        this_arg_type = type(var_and_valid_types[0])
        if this_arg_type not in valid_types:
            #
            #The argument specified is not a valid type. Create string
            #of printable valid types
            #
            printable_types = []
            for index in valid_types:
                printable_types.append(type_xlate(index))

            #
            #Return the error specifying the valid types for this
            #argument.
            #
            return("""
ArgError: Detected invalid type "{}" at argument offset {}.
          Must be one of: "{}"
""".format(type_xlate(this_arg_type),
           arg_off,
           '", "'.join(sorted(printable_types))))
 
        #
        #Argument has a valid type, return null string.
        #
        return ""

    ####################################################################
    ####################################################################
    #
    #validate_arg_type starts here
    #
    ####################################################################
    ####################################################################

    #
    #Explicitly check args_to_check table list passed to this function
    #to assure that its format is correct.
    #
    if not isinstance(args_to_check, tuple_or_list):
        sys.stderr.write("""
ArgError: validate_arg_type must be called with a tuple or list
          argument.""")
        #
        #Don't return, throw exception to generate trace
        #
        raise HamlibError("validate_arg_type parameter error")

    if not args_to_check:
        sys.stderr.write("""
ArgError: validate_arg_type called with empty tuple or list."""
    + generate_stack_trace())
        #
        #Don't return, throw exception to generate trace
        #
        raise HamlibError("validate_arg_type parameter error")

    #
    #Go through the tuple (or list) and assure each tuple consists of an
    #argument and zero or more types that the argument can be. Then
    #check to assure that the argument type is one of the valid types
    #specified as the remaining elements in the tupe (or list).
    #
    #What we're iterating through:
    #       (
    #        (arg0,),
    #        (arg1, typeA),
    #        (arg2, typeA, typeB, typeC, ...),
    #        .
    #        .
    #        .
    #       )
    #
    #Start with no argument type errors
    #
    errors = ""
    for index, tup in enumerate(args_to_check):
        #
        #Process the argument and valid type lists one at a time.
        #
        #index is the argument offset: 0, 1, 2, etc. for reporting
        #purposes
        #
        #tup is the tuple (or list) that contains the variable its
        #valid types.
        #
        errors += process_var_types(index, tup)

    #
    #Report all errors accumulated in the errors string, if any.
    #Bump the stack trace skip to two so the "top" of the trace is the
    #function with the error, not this function that detected it!
    #
    if errors:
        #
        #Report all wrong type argument errors that were detected.
        #
        sys.stderr.write(errors)
        #
        #Exit immediately to make this a hard error since we're not
        #going to try and recover from a bad argument passed to a
        #function. That's a programming error that needs to be fixed!
        #

        #
        #Don't return, throw exception to generate trace
        #
        raise HamlibError("Bad argument type passed to function")

    #
    #All arguments are valid, return
    #
    return None

########################################################################
########################################################################
#
# ADIF and ADX support functions
#
########################################################################
########################################################################

Ant_Path_Enumeration = {
    "G" : "grayline",
    "O" : "other",
    "S" : "short path",
    "L" : "long path"
    }

ARRL_Section_Enumeration = {
    "AL" : ("Alabama", ("291",)),
    "AK" : ("Alaska", ("6",)),
    "AB" : ("Alberta", ("1",)),
    "AR" : ("Arkansas", ("291",)),
    "AZ" : ("Arizona", ("291",)),
    "BC" : ("British Columbia", ("1",)),
    "CO" : ("Colorado", ("291",)),
    "CT" : ("Connecticut", ("291",)),
    "DE" : ("Delaware", ("291",)),
    "EB" : ("East Bay", ("291",)),
    "EMA" : ("Eastern Massachusetts", ("291",)),
    "ENY" : ("Eastern New York", ("291",)),
    "EPA" : ("Eastern Pennsylvania", ("291",)),
    "EWA" : ("Eastern Washington", ("291",)),
    "GA" : ("Georgia", ("291",)),
    "GTA" : ("Greater Toronto Area", ("1",)),
    "ID" : ("Idaho", ("291",)),
    "IL" : ("Illinois", ("291",)),
    "IN" : ("Indiana", ("291",)),
    "IA" : ("Iowa", ("291",)),
    "KS" : ("Kansas", ("291",)),
    "KY" : ("Kentucky", ("291",)),
    "LAX" : ("Los Angeles", ("291",)),
    "LA" : ("Louisiana", ("291",)),
    "ME" : ("Maine", ("291",)),
    "MB" : ("Manitoba", ("1",)),
    "MAR" : ("Maritime", ("1",)),
    "MDC" : ("Maryland-DC", ("291",)),
    "MI" : ("Michigan", ("291",)),
    "MN" : ("Minnesota", ("291",)),
    "MS" : ("Mississippi", ("291",)),
    "MO" : ("Missouri", ("291",)),
    "MT" : ("Montana", ("291",)),
    "NE" : ("Nebraska", ("291",)),
    "NV" : ("Nevada", ("291",)),
    "NH" : ("New Hampshire", ("291",)),
    "NM" : ("New Mexico", ("291",)),
    "NLI" : ("New York City-Long Island", ("291",)),
    "NL" : ("Newfoundland/Labrador", ("1",)),
    "NC" : ("North Carolina", ("291",)),
    "ND" : ("North Dakota", ("291",)),
    "NTX" : ("North Texas", ("291",)),
    "NFL" : ("Northern Florida", ("291",)),
    "NNJ" : ("Northern New Jersey", ("291",)),
    "NNY" : ("Northern New York", ("291",)),
    "NT" : ("Northwest Territories/Yukon/Nunavut", ("1",)),
    "OH" : ("Ohio", ("291",)),
    "OK" : ("Oklahoma", ("291",)),
    "ONE" : ("Ontario East", ("1",)),
    "ONN" : ("Ontario North", ("1",)),
    "ONS" : ("Ontario South", ("1",)),
    "ORG" : ("Orange", ("291",)),
    "OR" : ("Oregon", ("291",)),
    "PAC" : ("Pacific", ("9", "20", "103", "110", "123", "134", "138", "166", "174", "197", "297", "515")),
    "PR" : ("Puerto Rico", ("43", "202",)),
    "QC" : ("Quebec", ("1",)),
    "RI" : ("Rhode Island", ("291",)),
    "SV" : ("Sacramento Valley", ("291",)),
    "SDG" : ("San Diego", ("291",)),
    "SF" : ("San Francisco", ("291",)),
    "SJV" : ("San Joaquin Valley", ("291",)),
    "SB" : ("Santa Barbara", ("291",)),
    "SCV" : ("Santa Clara Valley", ("291",)),
    "SK" : ("Saskatchewan", ("1",)),
    "SC" : ("South Carolina", ("291",)),
    "SD" : ("South Dakota", ("291",)),
    "STX" : ("South Texas", ("291",)),
    "SFL" : ("Southern Florida", ("291",)),
    "SNJ" : ("Southern New Jersey", ("291",)),
    "TN" : ("Tennessee", ("291",)),
    "VI" : ("US Virgin Islands", ("105", "182", "285")),
    "UT" : ("Utah", ("291",)),
    "VT" : ("Vermont", ("291",)),
    "VA" : ("Virginia", ("291",)),
    "WCF" : ("West Central Florida", ("291",)),
    "WTX" : ("West Texas", ("291",)),
    "WV" : ("West Virginia", ("291",)),
    "WMA" : ("Western Massachusetts", ("291",)),
    "WNY" : ("Western New York", ("291",)),
    "WPA" : ("Western Pennsylvania", ("291",)),
    "WWA" : ("Western Washington", ("291",)),
    "WI" : ("Wisconsin", ("291",)),
    "WY" : ("Wyoming", ("291",))

    }

Award_Ennumeration = (
    "AJA",
    "CQDX",
    "CQDXFIELD",
    "CQWAZ_MIXED",
    "CQWAZ_CW",
    "CQWAZ_PHONE",
    "CQWAZ_RTTY",
    "CQWAZ_160m",
    "CQWPX",
    "DARC_DOK",
    "DXCC",
    "DXCC_MIXED",
    "DXCC_CW",
    "DXCC_PHONE",
    "DXCC_RTTY",
    "IOTA",
    "JCC",
    "JCG",
    "MARATHON",
    "RDA",
    "WAB",
    "WAC",
    "WAE",
    "WAIP",
    "WAJA",
    "WAS",
    "WAZ",
    "USACA",
    "VUCC"
)

Band_Enumeration = {
    "2190M"  : (0.1357, 0.1378),
    "630M"   : (0.472, 0.479),
    "560M"   : (0.501, 0.504),
    "160M"   : (1.8, 2.0),
    "80M"    : (3.5, 4.0),
    "60M"    : (5.06, 5.45),
    "40M"    : (7.0, 7.3),
    "30M"    : (10.1, 10.15),
    "20M"    : (14.0, 14.35),
    "17M"    : (18.068, 18.168),
    "15M"    : (21.0, 21.45),
    "12M"    : (24.890, 24.99),
    "10M"    : (28.0, 29.7),
    "8M"     : (40, 45),
    "6M"     : (50, 54),
    "5M"     : (54.000001, 69.9),
    "4M"     : (70, 71),
    "2M"     : (144, 148),
    "1.25M"  : (222, 225),
    "70CM"   : (420, 450),
    "33CM"   : (902, 928),
    "23CM"   : (1240, 1300),
    "13CM"   : (2300, 2450),
    "9CM"    : (3300, 3500),
    "6CM"    : (5650, 5925),
    "3CM"    : (10000, 10500),
    "1.25CM" : (24000, 24250),
    "6MM"    : (47000, 47200),
    "4MM"    : (75500, 81000),
    "2.5MM"  : (119980, 123000),
    "2MM"    : (134000, 149000),
    "1MM"    : (241000, 250000)
    }

Contest_ID_Enumeration = {
    "070-160M-SPRINT" : "PODXS Great Pumpkin Sprint",
    "070-3-DAY" : "PODXS Three Day Weekend",
    "070-31-FLAVORS" : "PODXS 31 Flavors",
    "070-40M-SPRINT" : "PODXS 40m Firecracker Sprint",
    "070-80M-SPRINT" : "PODXS 80m Jay Hudak Memorial Sprint",
    "070-PSKFEST" : "PODXS PSKFest",
    "070-ST-PATS-DAY" : "PODXS St. Patricks Day",
    "070-VALENTINE-SPRINT" : "PODXS Valentine Sprint",
    "10-RTTY" : "Ten-Meter RTTY Contest (2011 onwards)",
    "1010-OPEN-SEASON" : "Open Season Ten Meter QSO Party",
    "7QP" : "7th-Area QSO Party",
    "AL-QSO-PARTY" : "Alabama QSO Party",
    "ALL-ASIAN-DX-CW" : "JARL All Asian DX Contest (CW)",
    "ALL-ASIAN-DX-PHONE" : "JARL All Asian DX Contest (PHONE)",
    "ANARTS-RTTY" : "ANARTS WW RTTY",
    "ANATOLIAN-RTTY" : "Anatolian WW RTTY",
    "AP-SPRINT" : "Asia - Pacific Sprint",
    "AR-QSO-PARTY" : "Arkansas QSO Party",
    "ARI-DX" : "ARI DX Contest",
    "ARRL-10" : "ARRL 10 Meter Contest",
    "ARRL-10-GHZ" : "ARRL 10 GHz and Up Contest",
    "ARRL-160" : "ARRL 160 Meter Contest",
    "ARRL-222" : "ARRL 222 MHz and Up Distance Contest",
    "ARRL-DX-CW" : "ARRL International DX Contest (CW)",
    "ARRL-DX-SSB" : "ARRL International DX Contest (Phone)",
    "ARRL-EME" : "ARRL EME contest",
    "ARRL-FIELD-DAY" : "ARRL Field Day",
    "ARRL-RR-CW" : "ARRL Rookie Roundup (CW)",
    "ARRL-RR-RTTY" : "ARRL Rookie Roundup (RTTY)",
    "ARRL-RR-SSB" : "ARRL Rookie Roundup (Phone)",
    "ARRL-RTTY" : "ARRL RTTY Round-Up",
    "ARRL-SCR" : "ARRL School Club Roundup",
    "ARRL-SS-CW" : "ARRL November Sweepstakes (CW)",
    "ARRL-SS-SSB" : "ARRL November Sweepstakes (Phone)",
    "ARRL-UHF-AUG" : "ARRL August UHF Contest",
    "ARRL-VHF-JAN" : "ARRL January VHF Sweepstakes",
    "ARRL-VHF-JUN" : "ARRL June VHF QSO Party",
    "ARRL-VHF-SEP" : "ARRL September VHF QSO Party",
    "AZ-QSO-PARTY" : "Arizona QSO Party",
    "BARTG-RTTY" : "BARTG Spring RTTY Contest",
    "BARTG-SPRINT" : "BARTG Sprint Contest",
    "BC-QSO-PARTY" : "British Columbia QSO Party",
    "CA-QSO-PARTY" : "California QSO Party",
    "CIS-DX" : "CIS DX Contest",
    "CO-QSO-PARTY" : "Colorado QSO Party",
    "CQ-160-CW" : "CQ WW 160 Meter DX Contest (CW)",
    "CQ-160-SSB" : "CQ WW 160 Meter DX Contest (SSB)",
    "CQ-M" : "CQ-M International DX Contest",
    "CQ-VHF" : "CQ World-Wide VHF Contest",
    "CQ-WPX-CW" : "CQ WW WPX Contest (CW)",
    "CQ-WPX-RTTY" : "CQ/RJ WW RTTY WPX Contest",
    "CQ-WPX-SSB" : "CQ WW WPX Contest (SSB)",
    "CQ-WW-CW" : "CQ WW DX Contest (CW)",
    "CQ-WW-RTTY" : "CQ/RJ WW RTTY DX Contest",
    "CQ-WW-SSB" : "CQ WW DX Contest (SSB)",
    "CT-QSO-PARTY" : "Connecticut QSO Party",
    "CVA-DX-CW" : "Concurso Verde e Amarelo DX CW Contest",
    "CVA-DX-SSB" : "Concurso Verde e Amarelo DX CW Contest",
    "CWOPS-CW-OPEN" : "CWops CW Open Competition",
    "CWOPS-CWT" : "CWops Mini-CWT Test",
    "DARC-WAEDC-CW" : "WAE DX Contest (CW)",
    "DARC-WAEDC-RTTY" : "WAE DX Contest (RTTY)",
    "DARC-WAEDC-SSB" : "WAE DX Contest (SSB)",
    "DARC-WAG" : "DARC Worked All Germany",
    "DE-QSO-PARTY" : "Delaware QSO Party",
    "DL-DX-RTTY" : "DL-DX RTTY Contest",
    "DMC-RTTY" : "DMC RTTY Contest",
    "EA-CNCW" : "Concurso Nacional de Telegrafía",
    "EA-DME" : "Municipios Españoles",
    "EA-PSK63" : "EA PSK63",
    "EA-RTTY (import-only)" : "Unión de Radioaficionados Españoles RTTY Contest",
    "EA-SMRE-CW" : "Su Majestad El Rey de España - CW",
    "EA-SMRE-SSB" : "Su Majestad El Rey de España - SSB",
    "EA-VHF-ATLANTIC" : "Atlántico V-UHF",
    "EA-VHF-COM" : "Combinado de V-UHF",
    "EA-VHF-COSTA-SOL" : "Costa del Sol V-UHF",
    "EA-VHF-EA" : "Nacional VHF",
    "EA-VHF-EA1RCS" : "Segovia EA1RCS V-UHF",
    "EA-VHF-QSL" : "QSL V-UHF & 50MHz",
    "EA-VHF-SADURNI" : "Sant Sadurni V-UHF",
    "EA-WW-RTTY" : "Unión de Radioaficionados Españoles RTTY Contest",
    "EPC-PSK63" : "PSK63 QSO Party",
    "EU Sprint" : "EU Sprint",
    "EU-HF" : "EU HF Championship",
    "EU-PSK-DX" : "EU PSK DX Contest",
    "EUCW160M" : "European CW Association 160m CW Party",
    "FALL SPRINT" : "FISTS Fall Sprint",
    "FL-QSO-PARTY" : "Florida QSO Party",
    "GA-QSO-PARTY" : "Georgia QSO Party",
    "HA-DX" : "Hungarian DX Contest",
    "HELVETIA" : "Helvetia Contest",
    "HI-QSO-PARTY" : "Hawaiian QSO Party",
    "HOLYLAND" : "IARC Holyland Contest",
    "IA-QSO-PARTY" : "Iowa QSO Party",
    "IARU-FIELD-DAY" : "DARC IARU Region 1 Field Day",
    "IARU-HF" : "IARU HF World Championship",
    "ID-QSO-PARTY" : "Idaho QSO Party",
    "IL QSO Party" : "Illinois QSO Party",
    "IN-QSO-PARTY" : "Indiana QSO Party",
    "JARTS-WW-RTTY" : "JARTS WW RTTY",
    "JIDX-CW" : "Japan International DX Contest (CW)",
    "JIDX-SSB" : "Japan International DX Contest (SSB)",
    "JT-DX-RTTY" : "Mongolian RTTY DX Contest",
    "K1USN-SST" : "K1USN Slow Speed Test",
    "KS-QSO-PARTY" : "Kansas QSO Party",
    "KY-QSO-PARTY" : "Kentucky QSO Party",
    "LA-QSO-PARTY" : "Louisiana QSO Party",
    "LDC-RTTY" : "DRCG Long Distance Contest (RTTY)",
    "LZ DX" : "LZ DX Contest",
    "MAR-QSO-PARTY" : "Maritimes QSO Party",
    "MD-QSO-PARTY" : "Maryland QSO Party",
    "ME-QSO-PARTY" : "Maine QSO Party",
    "MI-QSO-PARTY" : "Michigan QSO Party",
    "MIDATLANTIC-QSO-PARTY" : "Mid-Atlantic QSO Party",
    "MN-QSO-PARTY" : "Minnesota QSO Party",
    "MO-QSO-PARTY" : "Missouri QSO Party",
    "MS-QSO-PARTY" : "Mississippi QSO Party",
    "MT-QSO-PARTY" : "Montana QSO Party",
    "NA-SPRINT-CW" : "North America Sprint (CW)",
    "NA-SPRINT-RTTY" : "North America Sprint (RTTY)",
    "NA-SPRINT-SSB" : "North America Sprint (Phone)",
    "NAQP-CW" : "North America QSO Party (CW)",
    "NAQP-RTTY" : "North America QSO Party (RTTY)",
    "NAQP-SSB" : "North America QSO Party (Phone)",
    "NC-QSO-PARTY" : "North Carolina QSO Party",
    "ND-QSO-PARTY" : "North Dakota QSO Party",
    "NE-QSO-PARTY" : "Nebraska QSO Party",
    "NEQP" : "New England QSO Party",
    "NH-QSO-PARTY" : "New Hampshire QSO Party",
    "NJ-QSO-PARTY" : "New Jersey QSO Party",
    "NM-QSO-PARTY" : "New Mexico QSO Party",
    "NRAU-BALTIC-CW" : "NRAU-Baltic Contest (CW)",
    "NRAU-BALTIC-SSB" : "NRAU-Baltic Contest (SSB)",
    "NV-QSO-PARTY" : "Nevada QSO Party",
    "NY-QSO-PARTY" : "New York QSO Party",
    "OCEANIA-DX-CW" : "Oceania DX Contest (CW)",
    "OCEANIA-DX-SSB" : "Oceania DX Contest (SSB)",
    "OH-QSO-PARTY" : "Ohio QSO Party",
    "OK-DX-RTTY" : "Czech Radio Club OK DX Contest",
    "OK-OM-DX" : "Czech Radio Club OK-OM DX Contest",
    "OK-QSO-PARTY" : "Oklahoma QSO Party",
    "OMISS-QSO-PARTY" : "Old Man International Sideband Society QSO Party",
    "ON-QSO-PARTY" : "Ontario QSO Party",
    "OR-QSO-PARTY" : "Oregon QSO Party",
    "PA-QSO-PARTY" : "Pennsylvania QSO Party",
    "PACC" : "Dutch PACC Contest",
    "PSK-DEATHMATCH" : "MDXA PSK DeathMatch (2005-2010)",
    "QC-QSO-PARTY" : "Quebec QSO Party",
    "RAC (import-only)" : "Canadian Amateur Radio Society Contest",
    "RAC-CANADA-DAY" : "RAC Canada Day Contest",
    "RAC-CANADA-WINTER" : "RAC Canada Winter Contest",
    "RDAC" : "Russian District Award Contest",
    "RDXC" : "Russian DX Contest",
    "REF-160M" : "Reseau des Emetteurs Francais 160m Contest",
    "REF-CW" : "Reseau des Emetteurs Francais Contest (CW)",
    "REF-SSB" : "Reseau des Emetteurs Francais Contest (SSB)",
    "REP-PORTUGAL-DAY-HF" : "Rede dos Emissores Portugueses Portugal Day HF Contest",
    "RI-QSO-PARTY" : "Rhode Island QSO Party",
    "RSGB-160" : "1.8MHz Contest",
    "RSGB-21/28-CW" : "21/28 MHz Contest (CW)",
    "RSGB-21/28-SSB" : "21/28 MHz Contest (SSB)",
    "RSGB-80M-CC" : "80m Club Championships",
    "RSGB-AFS-CW" : "Affiliated Societies Team Contest (CW)",
    "RSGB-AFS-SSB" : "Affiliated Societies Team Contest (SSB)",
    "RSGB-CLUB-CALLS" : "Club Calls",
    "RSGB-COMMONWEALTH" : "Commonwealth Contest",
    "RSGB-IOTA" : "IOTA Contest",
    "RSGB-LOW-POWER" : "Low Power Field Day",
    "RSGB-NFD" : "National Field Day",
    "RSGB-ROPOCO" : "RoPoCo",
    "RSGB-SSB-FD" : "SSB Field Day",
    "RUSSIAN-RTTY" : "Russian Radio RTTY Worldwide Contest",
    "SAC-CW" : "Scandinavian Activity Contest (CW)",
    "SAC-SSB" : "Scandinavian Activity Contest (SSB)",
    "SARTG-RTTY" : "SARTG WW RTTY",
    "SC-QSO-PARTY" : "South Carolina QSO Party",
    "SCC-RTTY" : "SCC RTTY Championship",
    "SD-QSO-PARTY" : "South Dakota QSO Party",
    "SMP-AUG" : "SSA Portabeltest",
    "SMP-MAY" : "SSA Portabeltest",
    "SP-DX-RTTY" : "PRC SPDX Contest (RTTY)",
    "SPAR-WINTER-FD" : "SPAR Winter Field Day(2016 and earlier)",
    "SPDXContest" : "SP DX Contest",
    "SPRING SPRINT" : "FISTS Spring Sprint",
    "SR-MARATHON" : "Scottish-Russian Marathon",
    "STEW-PERRY" : "Stew Perry Topband Distance Challenge",
    "SUMMER SPRINT" : "FISTS Summer Sprint",
    "TARA-GRID-DIP" : "TARA Grid Dip PSK-RTTY Shindig",
    "TARA-RTTY" : "TARA RTTY Mêlée",
    "TARA-RUMBLE" : "TARA Rumble PSK Contest",
    "TARA-SKIRMISH" : "TARA Skirmish Digital Prefix Contest",
    "TEN-RTTY" : "Ten-Meter RTTY Contest (before 2011)",
    "TMC-RTTY" : "The Makrothen Contest",
    "TN-QSO-PARTY" : "Tennessee QSO Party",
    "TX-QSO-PARTY" : "Texas QSO Party",
    "UBA-DX-CW" : "UBA Contest (CW)",
    "UBA-DX-SSB" : "UBA Contest (SSB)",
    "UK-DX-BPSK63" : "European PSK Club BPSK63 Contest",
    "UK-DX-RTTY" : "UK DX RTTY Contest",
    "UKR-CHAMP-RTTY" : "Open Ukraine RTTY Championship",
    "UKRAINIAN DX" : "Ukrainian DX",
    "UKSMG-6M-MARATHON" : "UKSMG 6m Marathon",
    "UKSMG-SUMMER-ES" : "UKSMG Summer Es Contest",
    "URE-DX  (import-only)" : "Ukrainian DX Contest",
    "US-COUNTIES-QSO" : "Mobile Amateur Awards Club",
    "UT-QSO-PARTY" : "Utah QSO Party",
    "VA-QSO-PARTY" : "Virginia QSO Party",
    "VENEZ-IND-DAY" : "RCV Venezuelan Independence Day Contest",
    "VIRGINIA QSO PARTY (import-only)" : "Virginia QSO Party",
    "VOLTA-RTTY" : "Alessandro Volta RTTY DX Contest",
    "VT-QSO-PARTY" : "Vermont QSO Party",
    "WA-QSO-PARTY" : "Washington QSO Party",
    "WFD" : "Winter Field Day (2017 and later)",
    "WI-QSO-PARTY" : "Wisconsin QSO Party",
    "WIA-HARRY ANGEL" : "WIA Harry Angel Memorial 80m Sprint",
    "WIA-JMMFD" : "WIA John Moyle Memorial Field Day",
    "WIA-OCDX" : "WIA Oceania DX (OCDX) Contest",
    "WIA-REMEMBRANCE" : "WIA Remembrance Day",
    "WIA-ROSS HULL" : "WIA Ross Hull Memorial VHF/UHF Contest",
    "WIA-TRANS TASMAN" : "WIA Trans Tasman Low Bands Challenge",
    "WIA-VHF/UHF FD" : "WIA VHF UHF Field Days",
    "WIA-VK SHIRES" : "WIA VK Shires",
    "WINTER SPRINT" : "FISTS Winter Sprint",
    "WV-QSO-PARTY" : "West Virginia QSO Party",
    "WW-DIGI" : "World Wide Digi DX Contest",
    "WY-QSO-PARTY" : "Wyoming QSO Party",
    "XE-INTL-RTTY" : "Mexico International Contest (RTTY)",
    "YOHFDX" : "YODX HF contest",
    "YUDXC" : "YU DX Contest"
    }

Continent_Enumeration = {
    "NA" : "North America",
    "SA" : "South America",
    "EU" : "Europe",
    "AF" : "Africa",
    "OC" : "Oceana",
    "AS" : "Asia",
    "AN" : "Antarctica"
    }

Credit_Ennumeration = {
    "CQDX" : ("CQ Magazine", "DX", "Mixed"),
    "CQDX_BAND" : ("CQ Magazine", "DX", "Band"),
    "CQDX_MODE" : ("CQ Magazine", "DX", "Mode"),
    "CQDX_MOBILE" : ("CQ Magazine", "DX", "Mobile"),
    "CQDX_QRP" : ("CQ Magazine", "DX", "QRP"),
    "CQDX_SATELLITE" : ("CQ Magazine", "DX", "Satellite"),
    "CQDXFIELD" : ("CQ Magazine", "DX Field", "Mixed"),
    "CQDXFIELD_BAND" : ("CQ Magazine", "DX Field", "Band"),
    "CQDXFIELD_MODE" : ("CQ Magazine", "DX Field", "Mode"),
    "CQDXFIELD_MOBILE" : ("CQ Magazine", "DX Field", "Mobile"),
    "CQDXFIELD_QRP" : ("CQ Magazine", "DX Field", "QRP"),
    "CQDXFIELD_SATELLITE" : ("CQ Magazine", "DX Field", "Satellite"),
    "CQWAZ_MIXED" : ("CQ Magazine", "Worked All Zones (WAZ)", "Mixed"),
    "CQWAZ_BAND" : ("CQ Magazine", "Worked All Zones (WAZ)", "Band"),
    "CQWAZ_MODE" : ("CQ Magazine", "Worked All Zones (WAZ)", "Mode"),
    "CQWAZ_SATELLITE" : ("CQ Magazine", "Worked All Zones (WAZ)", "Satellite"),
    "CQWAZ_EME" : ("CQ Magazine", "Worked All Zones (WAZ)", "EME"),
    "CQWAZ_MOBILE" : ("CQ Magazine", "Worked All Zones (WAZ)", "Mobile"),
    "CQWAZ_QRP" : ("CQ Magazine", "Worked All Zones (WAZ)", "QRP"),
    "CQWPX" : ("CQ Magazine", "WPX", "Mixed"),
    "CQWPX_BAND" : ("CQ Magazine", "WPX", "Band"),
    "CQWPX_MODE" : ("CQ Magazine", "WPX", "Mode"),
    "DXCC" : ("ARRL", "DX Century Club (DXCC)", "Mixed"),
    "DXCC_BAND" : ("ARRL", "DX Century Club (DXCC)", "Band"),
    "DXCC_MODE" : ("ARRL", "DX Century Club (DXCC)", "Mode"),
    "DXCC_SATELLITE" : ("ARRL", "DX Century Club (DXCC)", "Satellite"),
    "EAUSTRALIA" : ("eQSL", "eAustralia", "Mixed"),
    "ECANADA" : ("eQSL", "eCanada", "Mixed"),
    "ECOUNTY_STATE" : ("eQSL", "eCounty", "State"),
    "EDX" : ("eQSL", "eDX", "Mixed"),
    "EDX100" : ("eQSL", "eDX100", "Mixed"),
    "EDX100_BAND" : ("eQSL", "eDX100", "Band"),
    "EDX100_MODE" : ("eQSL", "eDX100", "Mode"),
    "EECHOLINK50" : ("eQSL", "eEcholink50", "Echolink"),
    "EGRID_BAND" : ("eQSL", "eGrid", "Band"),
    "EGRID_SATELLITE" : ("eQSL", "eGrid", "Satellite"),
    "EPFX300" : ("eQSL", "ePfx300", "Mixed"),
    "EPFX300_MODE" : ("eQSL", "ePfx300", "Mode"),
    "EWAS" : ("eQSL", "eWAS", "Mixed"),
    "EWAS_BAND" : ("eQSL", "eWAS", "Band"),
    "EWAS_MODE" : ("eQSL", "eWAS", "Mode"),
    "EWAS_SATELLITE" : ("eQSL", "eWAS", "Satellite"),
    "EZ40" : ("eQSL", "eZ40", "Mixed"),
    "EZ40_MODE" : ("eQSL", "eZ40", "Mode"),
    "FFMA" : ("ARRL", "Fred Fish Memorial Award (FFMA)", "Mixed"),
    "IOTA" : ("RSGB", "Islands on the Air (IOTA)", "Mixed"),
    "IOTA_BASIC" : ("RSGB", "Islands on the Air (IOTA)", "Mixed"),
    "IOTA_CONT" : ("RSGB", "Islands on the Air (IOTA)", "Continent"),
    "IOTA_GROUP" : ("RSGB", "Islands on the Air (IOTA)", "Group"),
    "RDA" : ("TAG", "Russian Districts Award (RDA)", "Mixed"),
    "USACA" : ("CQ Magazine", "United States of America Counties (USA-CA)", "Mixed"),
    "VUCC_BAND" : ("ARRL", "VHF/UHF Century Club Program (VUCC)", "Band"),
    "VUCC_SATELLITE" : ("ARRL", "VHF/UHF Century Club Program (VUCC)", "Satellite"),
    "WAB" : ("WAB AG", "Worked All Britain (WAB)", "Mixed"),
    "WAC" : ("IARU", "Worked All Continents (WAC)", "Mixed"),
    "WAC_BAND" : ("IARU", "Worked All Continents (WAC)", "Band"),
    "WAE" : ("DARC", "Worked All Europe (WAE)", "Mixed"),
    "WAE_BAND" : ("DARC", "Worked All Europe (WAE)", "Band"),
    "WAE_MODE" : ("DARC", "Worked All Europe (WAE)", "Mode"),
    "WAIP" : ("ARI", "Worked All Italian Provinces (WAIP)", "Mixed"),
    "WAIP_BAND" : ("ARI", "Worked All Italian Provinces (WAIP)", "Band"),
    "WAIP_MODE" : ("ARI", "Worked All Italian Provinces (WAIP)", "Mode"),
    "WAS" : ("ARRL", "Worked All States (WAS)", "Mixed"),
    "WAS_BAND" : ("ARRL", "Worked All States (WAS)", "Band"),
    "WAS_EME" : ("ARRL", "Worked All States (WAS)", "EME"),
    "WAS_MODE" : ("ARRL", "Worked All States (WAS)", "Mode"),
    "WAS_NOVICE" : ("ARRL", "Worked All States (WAS)", "Novice"),
    "WAS_QRP" : ("ARRL", "Worked All States (WAS)", "QRP"),
    "WAS_SATELLITE" : ("ARRL", "Worked All States (WAS)", "Satellite"),
    "WITUZ" : ("RSGB", "Worked ITU Zones (WITUZ)", "Mixed"),
    "WITUZ_BAND" : ("RSGB", "Worked ITU Zones (WITUZ)", "Band")
    }

#
#Table of valid submodes for each mode, if any
#
Mode_Enumeration = {
    "AM" : (),
    "ARDOP" : (),
    "ATV" : (),
    "CHIP" : ("CHIP64", "CHIP128"),
    "CLO" : (),
    "CONTESTI" : (),
    "CW" : ("PCW",),
    "DIGITALVOICE" : ("C4FM", "DMR", "DSTAR"),
    "DOMINO" : ("DOM-M", "DOM4", "DOM5", "DOM8", "DOM11", "DOM16",
        "DOM22", "DOM44", "DOM88", "DOMINOEX", "DOMINOF"),
    "DYNAMIC" : ("VARA HF", "VARA SATELLITE", "VARA FM 1200",
        "VARA FM 9600"),
    "FAX" : (),
    "FM" : (),
    "FSK441" : (),
    "FT8" : (),
    "HELL" : ("FMHELL", "FSKHELL", "HELL80", "HELLX5", "HELLX9", "HFSK",
        "PSKHELL", "SLOWHELL"),
    "ISCAT" : ("ISCAT-A", "ISCAT-B"),
    "JT4" : ("JT4A", "JT4B", "JT4C", "JT4D", "JT4E", "JT4F", "JT4G"),
    "JT6M" : (),
    "JT9" : ("JT9-1", "JT9-2", "JT9-5", "JT9-10", "JT9-30", "JT9A",
        "JT9B", "JT9C", "JT9D", "JT9E", "JT9E FAST", "JT9F",
        "JT9F FAST", "JT9G", "JT9G FAST", "JT9H", "JT9H FAST"),
    "JT44" : (),
    "JT65" : ("JT65A", "JT65B", "JT65B2", "JT65C", "JT65C2"),
    "MFSK" : ("FSQCALL", "FST4", "FST4W", "FT4", "JS8", "JTMS", "MFSK4",
        "MFSK8", "MFSK11", "MFSK16", "MFSK22", "MFSK31", "MFSK32",
        "MFSK64", "MFSK64L", "MFSK128 MFSK128L", "Q65"),
    "MSK144" : (),
    "MT63" : (),
    "OLIVIA" : ("OLIVIA 4/125", "OLIVIA 4/250", "OLIVIA 8/250",
        "OLIVIA 8/500", "OLIVIA 16/500", "OLIVIA 16/1000",
        "OLIVIA 32/1000"),
    "OPERA" : ("OPERA-BEACON", "OPERA-QSO"),
    "PAC" : ("PAC2", "PAC3", "PAC4"),
    "PAX" : ("PAX2"),
    "PKT" : (),
    "PSK" : ("8PSK125", "8PSK125F", "8PSK125FL", "8PSK250", "8PSK250F",
        "8PSK250FL", "8PSK500", "8PSK500F", "8PSK1000", "8PSK1000F",
        "8PSK1200F", "FSK31", "PSK10", "PSK31", "PSK63", "PSK63F",
        "PSK63RC4", "PSK63RC5", "PSK63RC10", "PSK63RC20", "PSK63RC32",
        "PSK125", "PSK125C12", "PSK125R", "PSK125RC10", "PSK125RC12",
        "PSK125RC16", "PSK125RC4", "PSK125RC5", "PSK250", "PSK250C6",
        "PSK250R", "PSK250RC2", "PSK250RC3", "PSK250RC5", "PSK250RC6",
        "PSK250RC7", "PSK500", "PSK500C2", "PSK500C4", "PSK500R",
        "PSK500RC2", "PSK500RC3", "PSK500RC4", "PSK800C2", "PSK800RC2",
        "PSK1000", "PSK1000C2", "PSK1000R", "PSK1000RC2", "PSKAM10",
        "PSKAM31", "PSKAM50", "PSKFEC31", "QPSK31", "QPSK63", "QPSK125",
        "QPSK250", "QPSK500", "SIM31"),
    "PSK2K" : (),
    "Q15" : (),
    "QRA64" : ("QRA64A", "QRA64B", "QRA64C", "QRA64D", "QRA64E"),
    "ROS" : ("ROS-EME", "ROS-HF", "ROS-MF"),
    "RTTY" : ("ASCI",),
    "RTTYM" : (),
    "SSB" : ("LSB", "USB"),
    "SSTV" : (),
    "T10" : (),
    "THOR" : ("THOR-M", "THOR4", "THOR5", "THOR8", "THOR11", "THOR16",
        "THOR22", "THOR25X4", "THOR50X1", "THOR50X2", "THOR100"),
    "THRB" : ("THRBX", "THRBX1", "THRBX2", "THRBX4", "THROB1", "THROB2",
        "THROB4"),
    "TOR" : ("AMTORFEC", "GTOR", "NAVTEX", "SITORB"),
    "V4" : (),
    "VOI" : (),
    "WINMOR" : (),
    "WSPR" : ()
    }

#
#Table of valid modes for each submode. Created from the mode table.
#
Submode_Enumeration = {}
for mode in Mode_Enumeration:
    for submode in Mode_Enumeration[mode]:
        Submode_Enumeration[submode] = mode

Propgation_Mode_Enumeration = {
    "AS" : "Aircraft Scatter",
    "AUE" : "Aurora-E",
    "AUR" : "Aurora",
    "BS" : "Back scatter",
    "ECH" : "EchoLink",
    "EME" : "Earth-Moon-Earth",
    "ES" : "Sporadic E",
    "F2" : "F2 Reflection",
    "FAI" : "Field Aligned Irregularities",
    "GWAVE" : "Ground Wave",
    "INTERNET" : "Internet-assisted",
    "ION" : "Ionoscatter",
    "IRL" : "IRLP",
    "LOS" : "Line of Sight (includes transmission through obstacles such as walls)",
    "MS" : "Meteor scatter",
    "RPT" : "Terrestrial or atmospheric repeater or transponder",
    "RS" : "Rain scatter",
    "SAT" : "Satellite",
    "TEP" : "Trans-equatorial",
    "TR" : "Tropospheric ducting"
    }

Primary_Administrative_Subdivision_Enumeration_1 = {
    "NS" : ("Nova Scotia", None, ("05",), ("09",)),
    "QC" : ("Québec", None, ("02", "05",), ("04", "09",)),
    "ON" : ("Ontario", None, ("04",), ("03", "04",)),
    "MB" : ("Manitoba", None, ("04",), ("03", "04",)),
    "SK" : ("Saskatchewan", None, ("04",), ("03",)),
    "AB" : ("Alberta", None, ("04",), ("02",)),
    "BC" : ("British Columbia", None, ("03",), ("02",)),
    "NT" : ("Northwest Territories", None, ("01", "02", "04",), ("03", "04", "75",)),
    "NB" : ("New Brunswick", None, ("05",), ("09",)),
    "NL" : ("Newfoundland and Labrador", None, ("02", "05",), ("09",)),
    "YT" : ("Yukon", None, ("01",), ("02",)),
    "PE" : ("Prince Edward Island", None, ("05",), ("09",)),
    "NU" : ("Nunavut", None, ("02",), ("04", "09",))
    }

Primary_Administrative_Subdivision_Enumeration_5 = {
    "001" : ("Brändö", None, None, None),
    "002" : ("Eckerö", None, None, None),
    "003" : ("Finström", None, None, None),
    "004" : ("Föglö", None, None, None),
    "005" : ("Geta", None, None, None),
    "006" : ("Hammarland", None, None, None),
    "007" : ("Jomala", None, None, None),
    "008" : ("Kumlinge", None, None, None),
    "009" : ("Kökar", None, None, None),
    "010" : ("Lemland", None, None, None),
    "011" : ("Lumparland", None, None, None),
    "012" : ("Maarianhamina", None, None, None),
    "013" : ("Saltvik", None, None, None),
    "014" : ("Sottunga", None, None, None),
    "015" : ("Sund", None, None, None),
    "016" : ("Vårdö", None, None, None)
    }

Primary_Administrative_Subdivision_Enumeration_6 = {
    "AK" : ("Alaska", None, None, None)
    }

Primary_Administrative_Subdivision_Enumeration_15 = {
    "UO" : ("Ust’-Ordynsky Autonomous Okrug - for contacts made before 2008-01-01", "174", ("18",), ("32",)),
    "AB" : ("Aginsky Buryatsky Autonomous Okrug - for contacts made before 2008-03-01", "175", ("18",), ("33",)),
    "CB" : ("Chelyabinsk (Chelyabinskaya oblast)", "165", ("17",), ("30",)),
    "SV" : ("Sverdlovskaya oblast", "154", ("17",), ("30",)),
    "PM" : ("Perm` (Permskaya oblast) - for contacts made on or after 2005-12-01", "140", ("17",), ("30",)),
    "PM" : ("Permskaya Kraj - for contacts made before 2005-12-01", "140", ("17",), ("30",)),
    "KP" : ("Komi-Permyatsky Autonomous Okrug - for contacts made before 2005-12-01", "141", ("17",), ("30",)),
    "TO" : ("Tomsk (Tomskaya oblast)", "158", ("18",), ("30",)),
    "HM" : ("Khanty-Mansyisky Autonomous Okrug", "162", ("17",), ("21",)),
    "YN" : ("Yamalo-Nenetsky Autonomous Okrug", "163", ("17",), ("21",)),
    "TN" : ("Tyumen' (Tyumenskaya oblast)", "161", ("17",), ("30",)),
    "OM" : ("Omsk (Omskaya oblast)", "146", ("17",), ("30",)),
    "NS" : ("Novosibirsk (Novosibirskaya oblast)", "145", ("18",), ("31",)),
    "KN" : ("Kurgan (Kurganskaya oblast)", "134", ("17",), ("30",)),
    "OB" : ("Orenburg (Orenburgskaya oblast)", "167", ("16", "17"), ("30",)),
    "KE" : ("Kemerovo (Kemerovskaya oblast)", "130", ("18",), ("31",)),
    "BA" : ("Republic of Bashkortostan", "84", ("16",), ("30",)),
    "KO" : ("Republic of Komi", "90", ("17",), ("20",)),
    "AL" : ("Altaysky Kraj", "99", ("18",), ("31",)),
    "GA" : ("Republic Gorny Altay", "100", ("18",), ("31",)),
    "KK" : ("Krasnoyarsk (Krasnoyarsk Kraj)", "103", ("18",), ("32",)),
    "TM" : ("Taymyr Autonomous Okrug - for contacts made before 2007-01-01", "105", ("18",), ("32",)),
    "HK" : ("Khabarovsk (Khabarovsky Kraj)", "110", ("19",), ("34",)),
    "EA" : ("Yevreyskaya Autonomous Oblast", "111", ("19",), ("33",)),
    "SL" : ("Sakhalin (Sakhalinskaya oblast)", "153", ("19",), ("34",)),
    "EV" : ("Evenkiysky Autonomous Okrug - for contacts made before 2007-01-01", "106", ("18",), ("22",)),
    "MG" : ("Magadan (Magadanskaya oblast)", "138", ("19",), ("24",)),
    "AM" : ("Amurskaya oblast", "112", ("19",), ("33",)),
    "CK" : ("Chukotka Autonomous Okrug", "139", ("19",), ("26",)),
    "PK" : ("Primorsky Kraj", "107", ("19",), ("34",)),
    "BU" : ("Republic of Buryatia", "85", ("18",), ("32",)),
    "YA" : ("Sakha (Yakut) Republic", "98", ("19",), ("32",)),
    "IR" : ("Irkutsk (Irkutskaya oblast)", "124", ("18",), ("32",)),
    "CT" : ("Zabaykalsky Kraj - referred to as Chita (Chitinskaya oblast) before 2008-03-01", "166", ("18",), ("33",)),
    "HA" : ("Republic of Khakassia", "104", ("18",), ("32",)),
    "KY" : ("Koryaksky Autonomous Okrug - for contacts made before 2007-01-01", "129", ("19",), ("25",)),
    "TU" : ("Republic of Tuva", "159", ("23",), ("32",)),
    "KT" : ("Kamchatka (Kamchatskaya oblast)", "128", ("19",), ("35",))
    }

Primary_Administrative_Subdivision_Enumeration_21 = {
    "IB" : ("Baleares", None, None, None)
    }

Primary_Administrative_Subdivision_Enumeration_27 = {
    "MI" : ("Minsk (Minskaya voblasts')", None, None, None),
    "BR" : ("Brest (Brestskaya voblasts')", None, None, None),
    "HR" : ("Grodno (Hrodzenskaya voblasts')", None, None, None),
    "VI" : ("Vitebsk (Vitsyebskaya voblasts')", None, None, None),
    "MA" : ("Mogilev (Mahilyowskaya voblasts')", None, None, None),
    "HO" : ("Gomel (Homyel'skaya voblasts')", None, None, None),
    "HM" : ("Horad Minsk", None, None, None)
    }

Primary_Administrative_Subdivision_Enumeration_29 = {
    "GC" : ("Las Palmas", None, None, None),
    "TF" : ("Tenerife", None, None, None)
    }

Primary_Administrative_Subdivision_Enumeration_32 = {
    "CE" : ("Ceuta", None, None, None),
    "ML" : ("Melilla", None, None, None)
    }

Primary_Administrative_Subdivision_Enumeration_50 = {
    "COL" : ("Colima", None, None, None),
    "DF" : ("Distrito Federal", None, None, None),
    "EMX" : ("Estado de México", None, None, None),
    "GTO" : ("Guanajuato", None, None, None),
    "HGO" : ("Hidalgo", None, None, None),
    "JAL" : ("Jalisco", None, None, None),
    "MIC" : ("Michoacán de Ocampo", None, None, None),
    "MOR" : ("Morelos", None, None, None),
    "NAY" : ("Nayarit", None, None, None),
    "PUE" : ("Puebla", None, None, None),
    "QRO" : ("Querétaro de Arteaga", None, None, None),
    "TLX" : ("Tlaxcala", None, None, None),
    "VER" : ("Veracruz-Llave", None, None, None),
    "AGS" : ("Aguascalientes", None, None, None),
    "BC" : ("Baja California", None, None, None),
    "BCS" : ("Baja California Sur", None, None, None),
    "CHH" : ("Chihuahua", None, None, None),
    "COA" : ("Coahuila de Zaragoza", None, None, None),
    "DGO" : ("Durango", None, None, None),
    "NL" : ("Nuevo Leon", None, None, None),
    "SLP" : ("San Luis Potosí", None, None, None),
    "SIN" : ("Sinaloa", None, None, None),
    "SON" : ("Sonora", None, None, None),
    "TMS" : ("Tamaulipas", None, None, None),
    "ZAC" : ("Zacatecas", None, None, None),
    "CAM" : ("Campeche", None, None, None),
    "CHS" : ("Chiapas", None, None, None),
    "GRO" : ("Guerrero", None, None, None),
    "OAX" : ("Oaxaca", None, None, None),
    "QTR" : ("Quintana Roo", None, None, None),
    "TAB" : ("Tabasco", None, None, None),
    "YUC" : ("Yucatán", None, None, None)
    }

Primary_Administrative_Subdivision_Enumeration_54 = {
    "SP" : ("City of St. Petersburg", "169", ("16",), ("29",)),
    "LO" : ("Leningradskaya oblast", "136", ("16",), ("29",)),
    "KL" : ("Republic of Karelia", "88", ("16",), ("19",)),
    "AR" : ("Arkhangelsk (Arkhangelskaya oblast)", "113", ("16",), ("19",)),
    "NO" : ("Nenetsky Autonomous Okrug", "114", ("16",), ("20",)),
    "VO" : ("Vologda (Vologodskaya oblast)", "120", ("16",), ("29",)),
    "NV" : ("Novgorodskaya oblast", "144", ("16",), ("29",)),
    "PS" : ("Pskov (Pskovskaya oblast)", "149", ("16",), ("29",)),
    "MU" : ("Murmansk (Murmanskaya oblast)", "143", ("16",), ("19",)),
    "MA" : ("City of Moscow", "170", ("16",), ("29",)),
    "MO" : ("Moscowskaya oblast", "142", ("16",), ("29",)),
    "OR" : ("Oryel (Orlovskaya oblast)", "147", ("16",), ("29",)),
    "LP" : ("Lipetsk (Lipetskaya oblast)", "137", ("16",), ("29",)),
    "TV" : ("Tver' (Tverskaya oblast)", "126", ("16",), ("29",)),
    "SM" : ("Smolensk (Smolenskaya oblast)", "155", ("16",), ("29",)),
    "YR" : ("Yaroslavl (Yaroslavskaya oblast)", "168", ("16",), ("29",)),
    "KS" : ("Kostroma (Kostromskaya oblast)", "132", ("16",), ("29",)),
    "TL" : ("Tula (Tul'skaya oblast)", "160", ("16",), ("29",)),
    "VR" : ("Voronezh (Voronezhskaya oblast)", "121", ("16",), ("29",)),
    "TB" : ("Tambov (Tambovskaya oblast)", "157", ("16",), ("29",)),
    "RA" : ("Ryazan' (Ryazanskaya oblast)", "151", ("16",), ("29",)),
    "NN" : ("Nizhni Novgorod (Nizhegorodskaya oblast)", "122", ("16",), ("29",)),
    "IV" : ("Ivanovo (Ivanovskaya oblast)", "123", ("16",), ("29",)),
    "VL" : ("Vladimir (Vladimirskaya oblast)", "119", ("16",), ("29",)),
    "KU" : ("Kursk (Kurskaya oblast)", "135", ("16",), ("29",)),
    "KG" : ("Kaluga (Kaluzhskaya oblast)", "127", ("16",), ("29",)),
    "BR" : ("Bryansk (Bryanskaya oblast)", "118", ("16",), ("29",)),
    "BO" : ("Belgorod (Belgorodskaya oblast)", "117", ("16",), ("29",)),
    "VG" : ("Volgograd (Volgogradskaya oblast)", "156", ("16",), ("29",)),
    "SA" : ("Saratov (Saratovskaya oblast)", "152", ("16",), ("29",)),
    "PE" : ("Penza (Penzenskaya oblast)", "148", ("16",), ("29",)),
    "SR" : ("Samara (Samarskaya oblast)", "133", ("16",), ("30",)),
    "UL" : ("Ulyanovsk (Ulyanovskaya oblast)", "164", ("16",), ("29",)),
    "KI" : ("Kirov (Kirovskaya oblast)", "131", ("16",), ("30",)),
    "TA" : ("Republic of Tataria", "94", ("16",), ("30",)),
    "MR" : ("Republic of Marij-El", "91", ("16",), ("29",)),
    "MD" : ("Republic of Mordovia", "92", ("16",), ("29",)),
    "UD" : ("Republic of Udmurtia", "95", ("16",), ("30",)),
    "CU" : ("Republic of Chuvashia", "97", ("16",), ("29",)),
    "KR" : ("Krasnodar (Krasnodarsky Kraj)", "101", ("16",), ("29",)),
    "KC" : ("Republic of Karachaevo-Cherkessia", "109", ("16",), ("29",)),
    "ST" : ("Stavropol' (Stavropolsky Kraj)", "108", ("16",), ("29",)),
    "KM" : ("Republic of Kalmykia", "89", ("16",), ("29",)),
    "SO" : ("Republic of Northern Ossetia", "93", ("16",), ("29",)),
    "RO" : ("Rostov-on-Don (Rostovskaya oblast)", "150", ("16",), ("29",)),
    "CN" : ("Republic Chechnya", "96", ("16",), ("29",)),
    "IN" : ("Republic of Ingushetia", "96", ("16",), ("29",)),
    "AO" : ("Astrakhan' (Astrakhanskaya oblast)", "115", ("16",), ("29",)),
    "DA" : ("Republic of Daghestan", "86", ("16",), ("29",)),
    "KB" : ("Republic of Kabardino-Balkaria", "87", ("16",), ("29",)),
    "AD" : ("Republic of Adygeya", "102", ("16",), ("29",))
    }

Primary_Administrative_Subdivision_Enumeration_61 = {
    "AR" : ("Arkhangelsk (Arkhangelskaya oblast)", None, None, None),
    "FJL" : ("Franz Josef Land (import-only)", None, None, None)
    }

Primary_Administrative_Subdivision_Enumeration_100 = {
    "C" : ("Capital federal (Buenos Aires City)", None, None, None),
    "B" : ("Buenos Aires Province", None, None, None),
    "S" : ("Santa Fe", None, None, None),
    "H" : ("Chaco", None, None, None),
    "P" : ("Formosa", None, None, None),
    "X" : ("Cordoba", None, None, None),
    "N" : ("Misiones", None, None, None),
    "E" : ("Entre Rios", None, None, None),
    "T" : ("Tucumán", None, None, None),
    "W" : ("Corrientes", None, None, None),
    "M" : ("Mendoza", None, None, None),
    "G" : ("Santiago del Estero", None, None, None),
    "A" : ("Salta", None, None, None),
    "J" : ("San Juan", None, None, None),
    "D" : ("San Luis", None, None, None),
    "K" : ("Catamarca", None, None, None),
    "F" : ("La Rioja", None, None, None),
    "Y" : ("Jujuy", None, None, None),
    "L" : ("La Pampa", None, None, None),
    "R" : ("Rió Negro", None, None, None),
    "U" : ("Chubut", None, None, None),
    "Z" : ("Santa Cruz", None, None, None),
    "V" : ("Tierra del Fuego", None, None, None),
    "Q" : ("Neuquén", None, None, None)
    }

Primary_Administrative_Subdivision_Enumeration_108 = {
    "ES" : ("Espírito Santo", None, None, None),
    "GO" : ("Goiás", None, None, None),
    "SC" : ("Santa Catarina", None, None, None),
    "SE" : ("Sergipe", None, None, None),
    "AL" : ("Alagoas", None, None, None),
    "AM" : ("Amazonas", None, None, None),
    "TO" : ("Tocantins", None, None, None),
    "AP" : ("Amapã", None, None, None),
    "PB" : ("Paraíba", None, None, None),
    "MA" : ("Maranhao", None, None, None),
    "RN" : ("Rio Grande do Norte", None, None, None),
    "PI" : ("Piaui", None, None, None),
    "DF" : ("Oietrito Federal (Brasila)", None, None, None),
    "CE" : ("Ceará", None, None, None),
    "AC" : ("Acre", None, None, None),
    "MS" : ("Mato Grosso do Sul", None, None, None),
    "RR" : ("Roraima", None, None, None),
    "RO" : ("Rondônia", None, None, None),
    "RJ" : ("Rio de Janeiro", None, None, None),
    "SP" : ("Sao Paulo", None, None, None),
    "RS" : ("Rio Grande do Sul", None, None, None),
    "MG" : ("Minas Gerais", None, None, None),
    "PR" : ("Paranã", None, None, None),
    "BA" : ("Bahia", None, None, None),
    "PE" : ("Pernambuco", None, None, None),
    "PA" : ("Parã", None, None, None),
    "MT" : ("Mato Grosso", None, None, None)
    }

Primary_Administrative_Subdivision_Enumeration_110 = {
    "HI" : ("Hawaii", None, None, None)
    }

Primary_Administrative_Subdivision_Enumeration_112 = {
    "II" : ("Antofagasta", None, None, None),
    "III" : ("Atacama", None, None, None),
    "I" : ("Tarapacá", None, None, None),
    "XV" : ("Arica y Parinacota", None, None, None),
    "IV" : ("Coquimbo", None, None, None),
    "V" : ("Valparaíso", None, None, None),
    "RM" : ("Region Metropolitana de Santiago", None, None, None),
    "VI" : ("Libertador General Bernardo O'Higgins", None, None, None),
    "VII" : ("Maule", None, None, None),
    "VIII" : ("Bío-Bío", None, None, None),
    "IX" : ("La Araucanía", None, None, None),
    "XIV" : ("Los Ríos", None, None, None),
    "X" : ("Los Lagos", None, None, None),
    "XI" : ("Aisén del General Carlos Ibáñez del Campo", None, None, None),
    "XII" : ("Magallanes", None, None, None)
    }

Primary_Administrative_Subdivision_Enumeration_126 = {
    "KA" : ("Kalingrad (Kaliningradskaya oblast)", "125", ("15",), ("29",))
    }

Primary_Administrative_Subdivision_Enumeration_132 = {
    "16" : ("Alto Paraguay", None, None, None),
    "19" : ("Boquerón", None, None, None),
    "15" : ("Presidente Hayes", None, None, None),
    "13" : ("Amambay", None, None, None),
    "01" : ("Concepción", None, None, None),
    "14" : ("Canindeyú", None, None, None),
    "02" : ("San Pedro", None, None, None),
    "ASU" : ("Asunción", None, None, None),
    "11" : ("Central", None, None, None),
    "03" : ("Cordillera", None, None, None),
    "09" : ("Paraguarí", None, None, None),
    "06" : ("Caazapl", None, None, None),
    "05" : ("Caeguazú", None, None, None),
    "04" : ("Guairá", None, None, None),
    "08" : ("Miaiones", None, None, None),
    "12" : ("Ñeembucu", None, None, None),
    "10" : ("Alto Paraná", None, None, None),
    "07" : ("Itapua", None, None, None)
    }

Primary_Administrative_Subdivision_Enumeration_137 = {
    "A" : ("Seoul (Seoul Teugbyeolsi)", None, None, None),
    "N" : ("Inchon (Incheon Gwang'yeogsi)", None, None, None),
    "D" : ("Kangwon-do (Gang 'weondo)", None, None, None),
    "C" : ("Kyunggi-do (Gyeonggido)", None, None, None),
    "E" : ("Choongchungbuk-do (Chungcheongbugdo)", None, None, None),
    "F" : ("Choongchungnam-do (Chungcheongnamdo)", None, None, None),
    "R" : ("Taejon (Daejeon Gwang'yeogsi)", None, None, None),
    "M" : ("Cheju-do (Jejudo)", None, None, None),
    "G" : ("Chollabuk-do (Jeonrabugdo)", None, None, None),
    "H" : ("Chollanam-do (Jeonranamdo)", None, None, None),
    "Q" : ("Kwangju (Gwangju Gwang'yeogsi)", None, None, None),
    "K" : ("Kyungsangbuk-do (Gyeongsangbugdo)", None, None, None),
    "L" : ("Kyungsangnam-do (Gyeongsangnamdo)", None, None, None),
    "B" : ("Pusan (Busan Gwang'yeogsi)", None, None, None),
    "P" : ("Taegu (Daegu Gwang'yeogsi)", None, None, None),
    "S" : ("Ulsan (Ulsan Gwanq'yeogsi)", None, None, None),
    "T" : ("Sejong", None, None, None),
    "IS" : ("Special Island", None, None, None)
    }

Primary_Administrative_Subdivision_Enumeration_138 = {
    "KI" : ("Kure Island", None, None, None)
    }

Primary_Administrative_Subdivision_Enumeration_144 = {
    "MO" : ("Montevideo", None, None, None),
    "CA" : ("Canelones", None, None, None),
    "SJ" : ("San José", None, None, None),
    "CO" : ("Colonia", None, None, None),
    "SO" : ("Soriano", None, None, None),
    "RN" : ("Rio Negro", None, None, None),
    "PA" : ("Paysandu", None, None, None),
    "SA" : ("Salto", None, None, None),
    "AR" : ("Artigsa", None, None, None),
    "FD" : ("Florida", None, None, None),
    "FS" : ("Flores", None, None, None),
    "DU" : ("Durazno", None, None, None),
    "TA" : ("Tacuarembo", None, None, None),
    "RV" : ("Rivera", None, None, None),
    "MA" : ("Maldonado", None, None, None),
    "LA" : ("Lavalleja", None, None, None),
    "RO" : ("Rocha", None, None, None),
    "TT" : ("Treinta y Tres", None, None, None),
    "CL" : ("Cerro Largo", None, None, None)
    }

Primary_Administrative_Subdivision_Enumeration_147 = {
    "LH" : ("Lord Howe Is", None, None, None)
    }

Primary_Administrative_Subdivision_Enumeration_148 = {
    "AM" : ("Amazonas", None, None, None),
    "AN" : ("Anzoátegui", None, None, None),
    "AP" : ("Apure", None, None, None),
    "AR" : ("Aragua", None, None, None),
    "BA" : ("Barinas", None, None, None),
    "BO" : ("Bolívar", None, None, None),
    "CA" : ("Carabobo", None, None, None),
    "CO" : ("Cojedes", None, None, None),
    "DA" : ("Delta Amacuro", None, None, None),
    "DC" : ("Distrito Capital", None, None, None),
    "FA" : ("Falcón", None, None, None),
    "GU" : ("Guárico", None, None, None),
    "LA" : ("Lara", None, None, None),
    "ME" : ("Mérida", None, None, None),
    "MI" : ("Miranda", None, None, None),
    "MO" : ("Monagas", None, None, None),
    "NE" : ("Nueva Esparta", None, None, None),
    "PO" : ("Portuguesa", None, None, None),
    "SU" : ("Sucre", None, None, None),
    "TA" : ("Táchira", None, None, None),
    "TR" : ("Trujillo", None, None, None),
    "VA" : ("Vargas", None, None, None),
    "YA" : ("Yaracuy", None, None, None),
    "ZU" : ("Zulia", None, None, None)
    }

Primary_Administrative_Subdivision_Enumeration_149 = {
    "AC" : ("Açores", None, None, None)
    }

Primary_Administrative_Subdivision_Enumeration_150 = {
    "ACT" : ("Australian Capital Territory", None, None, None),
    "NSW" : ("New South Wales", None, None, None),
    "VIC" : ("Victoria", None, None, None),
    "QLD" : ("Queensland", None, None, None),
    "SA" : ("South Australia", None, None, None),
    "WA" : ("Western Australia", None, None, None),
    "TAS" : ("Tasmania", None, None, None),
    "NT" : ("Northern Territory", None, None, None)
    }

Primary_Administrative_Subdivision_Enumeration_151 = {
    "LO" : ("Leningradskaya Oblast", None, None, None),
    "MV" : ("Malyj Vysotskij (import-only)", None, None, None)
    }

Primary_Administrative_Subdivision_Enumeration_153 = {
    "MA" : ("Macquarie Is", None, None, None)
    }

Primary_Administrative_Subdivision_Enumeration_163 = {
    "NCD" : ("National Capital District (Port Moresby)", None, None, None),
    "CPM" : ("Central", None, None, None),
    "CPK" : ("Chimbu", None, None, None),
    "EHG" : ("Eastern Highlands", None, None, None),
    "EBR" : ("East New Britain", None, None, None),
    "ESW" : ("East Sepik", None, None, None),
    "EPW" : ("Enga", None, None, None),
    "GPK" : ("Gulf", None, None, None),
    "MPM" : ("Madang", None, None, None),
    "MRL" : ("Manus", None, None, None),
    "MBA" : ("Milne Bay", None, None, None),
    "MPL" : ("Morobe", None, None, None),
    "NIK" : ("New Ireland", None, None, None),
    "NPP" : ("Northern", None, None, None),
    "NSA" : ("North Solomons", None, None, None),
    "SAN" : ("Santaun", None, None, None),
    "SHM" : ("Southern Highlands", None, None, None),
    "WPD" : ("Western", None, None, None),
    "WHM" : ("Western Highlands", None, None, None),
    "WBR" : ("West New Britain", None, None, None)
    }

Primary_Administrative_Subdivision_Enumeration_170 = {
    "AUK" : ("Auckland", None, None, None),
    "BOP" : ("Bay of Plenty", None, None, None),
    "NTL" : ("Northland", None, None, None),
    "WKO" : ("Waikato", None, None, None),
    "GIS" : ("Gisborne", None, None, None),
    "HKB" : ("Hawkes Bay", None, None, None),
    "MWT" : ("Manawatu-Wanganui", None, None, None),
    "TKI" : ("Taranaki", None, None, None),
    "WGN" : ("Wellington", None, None, None),
    "CAN" : ("Canterbury", None, None, None),
    "MBH" : ("Marlborough", None, None, None),
    "NSN" : ("Nelson", None, None, None),
    "TAS" : ("Tasman", None, None, None),
    "WTC" : ("West Coast", None, None, None),
    "OTA" : ("Otago", None, None, None),
    "STL" : ("Southland", None, None, None)
    }

Primary_Administrative_Subdivision_Enumeration_177 = {
    "MT" : ("Minami Torishima", None, None, None)
    }

Primary_Administrative_Subdivision_Enumeration_192 = {
    "O" : ("Ogasawara", None, None, None)
    }

Primary_Administrative_Subdivision_Enumeration_206 = {
    "WC" : ("Wien", None, None, None),
    "HA" : ("Hallein", None, None, None),
    "JO" : ("St. Johann", None, None, None),
    "SC" : ("Salzburg", None, None, None),
    "SL" : ("Salzburg-Land", None, None, None),
    "TA" : ("Tamsweg", None, None, None),
    "ZE" : ("Zell Am See", None, None, None),
    "AM" : ("Amstetten", None, None, None),
    "BL" : ("Bruck/Leitha", None, None, None),
    "BN" : ("Baden", None, None, None),
    "GD" : ("Gmünd", None, None, None),
    "GF" : ("Gänserndorf", None, None, None),
    "HL" : ("Hollabrunn", None, None, None),
    "HO" : ("Horn", None, None, None),
    "KO" : ("Korneuburg", None, None, None),
    "KR" : ("Krems-Region", None, None, None),
    "KS" : ("Krems", None, None, None),
    "LF" : ("Lilienfeld", None, None, None),
    "MD" : ("Mödling", None, None, None),
    "ME" : ("Melk", None, None, None),
    "MI" : ("Mistelbach", None, None, None),
    "NK" : ("Neunkirchen", None, None, None),
    "PC" : ("St. Pölten", None, None, None),
    "PL" : ("St. Pölten-Land", None, None, None),
    "SB" : ("Scheibbs", None, None, None),
    "SW" : ("Schwechat", None, None, None),
    "TU" : ("Tulln", None, None, None),
    "WB" : ("Wr.Neustadt-Bezirk", None, None, None),
    "WN" : ("Wr.Neustadt", None, None, None),
    "WT" : ("Waidhofen/Thaya", None, None, None),
    "WU" : ("Wien-Umgebung", None, None, None),
    "WY" : ("Waidhofen/Ybbs", None, None, None),
    "ZT" : ("Zwettl", None, None, None),
    "EC" : ("Eisenstadt", None, None, None),
    "EU" : ("Eisenstadt-Umgebung", None, None, None),
    "GS" : ("Güssing", None, None, None),
    "JE" : ("Jennersdorf", None, None, None),
    "MA" : ("Mattersburg", None, None, None),
    "ND" : ("Neusiedl/See", None, None, None),
    "OP" : ("Oberpullendorf", None, None, None),
    "OW" : ("Oberwart", None, None, None),
    "BR" : ("Braunau/Inn", None, None, None),
    "EF" : ("Eferding", None, None, None),
    "FR" : ("Freistadt", None, None, None),
    "GM" : ("Gmunden", None, None, None),
    "GR" : ("Grieskirchen", None, None, None),
    "KI" : ("Kirchdorf", None, None, None),
    "LC" : ("Linz", None, None, None),
    "LL" : ("Linz-Land", None, None, None),
    "PE" : ("Perg", None, None, None),
    "RI" : ("Ried/Innkreis", None, None, None),
    "RO" : ("Rohrbach", None, None, None),
    "SD" : ("Schärding", None, None, None),
    "SE" : ("Steyr-Land", None, None, None),
    "SR" : ("Steyr", None, None, None),
    "UU" : ("Urfahr", None, None, None),
    "VB" : ("Vöcklabruck", None, None, None),
    "WE" : ("Wels", None, None, None),
    "WL" : ("Wels-Land", None, None, None),
    "BA" : ("Bad Aussee - for contacts made before 2012/01/01", None, None, None),
    "BM" : ("Bruck/Mur - for contacts made before 2013/01/01", None, None, None),
    "BM" : ("Bruck-Mürzzuschlag - for contacts made on or after 2013/01/01", None, None, None),
    "DL" : ("Deutschlandsberg", None, None, None),
    "FB" : ("Feldbach - for contacts made before 2013/01/01", None, None, None),
    "FF" : ("Fürstenfeld - for contacts made before 2013/01/01", None, None, None),
    "GB" : ("Gröbming", None, None, None),
    "GC" : ("Graz", None, None, None),
    "GU" : ("Graz-Umgebung", None, None, None),
    "HB" : ("Hartberg - for contacts made before 2013/01/01", None, None, None),
    "HF" : ("Hartberg-Fürstenfeld - for contacts made on or after 2013/01/01", None, None, None),
    "JU" : ("Judenburg - for contacts made before 2012/01/01", None, None, None),
    "KF" : ("Knittelfeld - for contacts made before 2012/01/01", None, None, None),
    "LB" : ("Leibnitz", None, None, None),
    "LE" : ("Leoben", None, None, None),
    "LI" : ("Liezen", None, None, None),
    "LN" : ("Leoben-Land", None, None, None),
    "MT" : ("Murtal - for contacts made on or after 2012/01/01", None, None, None),
    "MU" : ("Murau", None, None, None),
    "MZ" : ("Mürzzuschlag - for contacts made before 2013/01/01", None, None, None),
    "RA" : ("Radkersburg - for contacts made before 2013/01/01", None, None, None),
    "SO" : ("Südoststeiermark - for contacts made on or after 2013/01/01", None, None, None),
    "VO" : ("Voitsberg", None, None, None),
    "WZ" : ("Weiz", None, None, None),
    "IC" : ("Innsbruck", None, None, None),
    "IL" : ("Innsbruck-Land", None, None, None),
    "IM" : ("Imst", None, None, None),
    "KB" : ("Kitzbühel", None, None, None),
    "KU" : ("Kufstein", None, None, None),
    "LA" : ("Landeck", None, None, None),
    "LZ" : ("Lienz", None, None, None),
    "RE" : ("Reutte", None, None, None),
    "SZ" : ("Schwaz", None, None, None),
    "FE" : ("Feldkirchen", None, None, None),
    "HE" : ("Hermagor", None, None, None),
    "KC" : ("Klagenfurt", None, None, None),
    "KL" : ("Klagenfurt-Land", None, None, None),
    "SP" : ("Spittal/Drau", None, None, None),
    "SV" : ("St.Veit/Glan", None, None, None),
    "VI" : ("Villach", None, None, None),
    "VK" : ("Völkermarkt", None, None, None),
    "VL" : ("Villach-Land", None, None, None),
    "WO" : ("Wolfsberg", None, None, None),
    "BC" : ("Bregenz", None, None, None),
    "BZ" : ("Bludenz", None, None, None),
    "DO" : ("Dornbirn", None, None, None),
    "FK" : ("Feldkirch", None, None, None)
    }

Primary_Administrative_Subdivision_Enumeration_209 = {
    "AN" : ("Antwerpen", None, None, None),
    "BR" : ("Brussels", None, None, None),
    "BW" : ("Brabant Wallon", None, None, None),
    "HT" : ("Hainaut", None, None, None),
    "LB" : ("Limburg", None, None, None),
    "LG" : ("Liêge", None, None, None),
    "NM" : ("Namur", None, None, None),
    "LU" : ("Luxembourg", None, None, None),
    "OV" : ("Oost-Vlaanderen", None, None, None),
    "VB" : ("Vlaams Brabant", None, None, None),
    "WV" : ("West-Vlaanderen", None, None, None)
    }

Primary_Administrative_Subdivision_Enumeration_212 = {
    "BU" : ("Burgas", None, None, None),
    "SL" : ("Sliven", None, None, None),
    "YA" : ("Yambol (Jambol)", None, None, None),
    "SO" : ("Sofija Grad", None, None, None),
    "HA" : ("Haskovo", None, None, None),
    "KA" : ("Kărdžali", None, None, None),
    "SZ" : ("Stara Zagora", None, None, None),
    "PA" : ("Pazardžik", None, None, None),
    "PD" : ("Plovdiv", None, None, None),
    "SM" : ("Smoljan", None, None, None),
    "BL" : ("Blagoevgrad", None, None, None),
    "KD" : ("Kjustendil", None, None, None),
    "PK" : ("Pernik", None, None, None),
    "SF" : ("Sofija (Sofia)", None, None, None),
    "GA" : ("Gabrovo", None, None, None),
    "LV" : ("Loveč (Lovech)", None, None, None),
    "PL" : ("Pleven", None, None, None),
    "VT" : ("Veliko Tărnovo", None, None, None),
    "MN" : ("Montana", None, None, None),
    "VD" : ("Vidin", None, None, None),
    "VR" : ("Vraca", None, None, None),
    "RZ" : ("Razgrad", None, None, None),
    "RS" : ("Ruse", None, None, None),
    "SS" : ("Silistra", None, None, None),
    "TA" : ("Tărgovište", None, None, None),
    "DO" : ("Dobrič", None, None, None),
    "SN" : ("Šumen", None, None, None),
    "VN" : ("Varna", None, None, None)
    }

Primary_Administrative_Subdivision_Enumeration_214 = {
    "2A" : ("Corse-du-Sud", None, None, None),
    "2B" : ("Haute-Corse", None, None, None)
    }

Primary_Administrative_Subdivision_Enumeration_221 = {
    "015" : ("Koebenhavns amt", None, None, None),
    "020" : ("Frederiksborg amt", None, None, None),
    "025" : ("Roskilde amt", None, None, None),
    "030" : ("Vestsjaellands amt", None, None, None),
    "035" : ("Storstrøm amt (Storstroems)", None, None, None),
    "040" : ("Bornholms amt", None, None, None),
    "042" : ("Fyns amt", None, None, None),
    "050" : ("Sínderjylland amt (Sydjyllands)", None, None, None),
    "055" : ("Ribe amt", None, None, None),
    "060" : ("Vejle amt", None, None, None),
    "065" : ("Ringkøbing amt (Ringkoebing)", None, None, None),
    "070" : ("Århus amt (Aarhus)", None, None, None),
    "076" : ("Viborg amt", None, None, None),
    "080" : ("Nordjyllands amt", None, None, None),
    "101" : ("Copenhagen City", None, None, None),
    "147" : ("Frederiksberg", None, None, None)
    }

Primary_Administrative_Subdivision_Enumeration_224 = {
    "100" : ("Somero", None, None, None),
    "102" : ("Alastaro", None, None, None),
    "103" : ("Askainen", None, None, None),
    "104" : ("Aura", None, None, None),
    "105" : ("Dragsfjärd", None, None, None),
    "106" : ("Eura", None, None, None),
    "107" : ("Eurajoki", None, None, None),
    "108" : ("Halikko", None, None, None),
    "109" : ("Harjavalta", None, None, None),
    "110" : ("Honkajoki", None, None, None),
    "111" : ("Houtskari", None, None, None),
    "112" : ("Huittinen", None, None, None),
    "115" : ("Iniö", None, None, None),
    "116" : ("Jämijärvi", None, None, None),
    "117" : ("Kaarina", None, None, None),
    "119" : ("Kankaanpää", None, None, None),
    "120" : ("Karinainen", None, None, None),
    "122" : ("Karvia", None, None, None),
    "123" : ("Äetsä", None, None, None),
    "124" : ("Kemiö", None, None, None),
    "126" : ("Kiikala", None, None, None),
    "128" : ("Kiikoinen", None, None, None),
    "129" : ("Kisko", None, None, None),
    "130" : ("Kiukainen", None, None, None),
    "131" : ("Kodisjoki", None, None, None),
    "132" : ("Kokemäki", None, None, None),
    "133" : ("Korppoo", None, None, None),
    "134" : ("Koski tl", None, None, None),
    "135" : ("Kullaa", None, None, None),
    "136" : ("Kustavi", None, None, None),
    "137" : ("Kuusjoki", None, None, None),
    "138" : ("Köyliö", None, None, None),
    "139" : ("Laitila", None, None, None),
    "140" : ("Lappi", None, None, None),
    "141" : ("Lavia", None, None, None),
    "142" : ("Lemu", None, None, None),
    "143" : ("Lieto", None, None, None),
    "144" : ("Loimaa", None, None, None),
    "145" : ("Loimaan kunta", None, None, None),
    "147" : ("Luvia", None, None, None),
    "148" : ("Marttila", None, None, None),
    "149" : ("Masku", None, None, None),
    "150" : ("Mellilä", None, None, None),
    "151" : ("Merikarvia", None, None, None),
    "152" : ("Merimasku", None, None, None),
    "154" : ("Mietoinen", None, None, None),
    "156" : ("Muurla", None, None, None),
    "157" : ("Mynämäki", None, None, None),
    "158" : ("Naantali", None, None, None),
    "159" : ("Nakkila", None, None, None),
    "160" : ("Nauvo", None, None, None),
    "161" : ("Noormarkku", None, None, None),
    "162" : ("Nousiainen", None, None, None),
    "163" : ("Oripää", None, None, None),
    "164" : ("Paimio", None, None, None),
    "165" : ("Parainen", None, None, None),
    "167" : ("Perniö", None, None, None),
    "168" : ("Pertteli", None, None, None),
    "169" : ("Piikkiö", None, None, None),
    "170" : ("Pomarkku", None, None, None),
    "171" : ("Pori", None, None, None),
    "172" : ("Punkalaidun", None, None, None),
    "173" : ("Pyhäranta", None, None, None),
    "174" : ("Pöytyä", None, None, None),
    "175" : ("Raisio", None, None, None),
    "176" : ("Rauma", None, None, None),
    "178" : ("Rusko", None, None, None),
    "179" : ("Rymättylä", None, None, None),
    "180" : ("Salo", None, None, None),
    "181" : ("Sauvo", None, None, None),
    "182" : ("Siikainen", None, None, None),
    "183" : ("Suodenniemi", None, None, None),
    "184" : ("Suomusjärvi", None, None, None),
    "185" : ("Säkylä", None, None, None),
    "186" : ("Särkisalo", None, None, None),
    "187" : ("Taivassalo", None, None, None),
    "188" : ("Tarvasjoki", None, None, None),
    "189" : ("Turku", None, None, None),
    "190" : ("Ulvila", None, None, None),
    "191" : ("Uusikaupunki", None, None, None),
    "192" : ("Vahto", None, None, None),
    "193" : ("Vammala", None, None, None),
    "194" : ("Vampula", None, None, None),
    "195" : ("Vehmaa", None, None, None),
    "196" : ("Velkua", None, None, None),
    "198" : ("Västanfjärd", None, None, None),
    "199" : ("Yläne", None, None, None),
    "201" : ("Artjärvi", None, None, None),
    "202" : ("Askola", None, None, None),
    "204" : ("Espoo", None, None, None),
    "205" : ("Hanko", None, None, None),
    "206" : ("Helsinki", None, None, None),
    "207" : ("Hyvinkää", None, None, None),
    "208" : ("Inkoo", None, None, None),
    "209" : ("Järvenpää", None, None, None),
    "210" : ("Karjaa", None, None, None),
    "211" : ("Karjalohja", None, None, None),
    "212" : ("Karkkila", None, None, None),
    "213" : ("Kauniainen", None, None, None),
    "214" : ("Kerava", None, None, None),
    "215" : ("Kirkkonummi", None, None, None),
    "216" : ("Lapinjärvi", None, None, None),
    "217" : ("Liljendal", None, None, None),
    "218" : ("Lohjan kaupunki", None, None, None),
    "220" : ("Loviisa", None, None, None),
    "221" : ("Myrskylä", None, None, None),
    "222" : ("Mäntsälä", None, None, None),
    "223" : ("Nummi-Pusula", None, None, None),
    "224" : ("Nurmijärvi", None, None, None),
    "225" : ("Orimattila", None, None, None),
    "226" : ("Pernaja", None, None, None),
    "227" : ("Pohja", None, None, None),
    "228" : ("Pornainen", None, None, None),
    "229" : ("Porvoo", None, None, None),
    "231" : ("Pukkila", None, None, None),
    "233" : ("Ruotsinpyhtää", None, None, None),
    "234" : ("Sammatti", None, None, None),
    "235" : ("Sipoo", None, None, None),
    "236" : ("Siuntio", None, None, None),
    "238" : ("Tammisaari", None, None, None),
    "241" : ("Tuusula", None, None, None),
    "242" : ("Vantaa", None, None, None),
    "243" : ("Vihti", None, None, None),
    "301" : ("Asikkala", None, None, None),
    "303" : ("Forssa", None, None, None),
    "304" : ("Hattula", None, None, None),
    "305" : ("Hauho", None, None, None),
    "306" : ("Hausjärvi", None, None, None),
    "307" : ("Hollola", None, None, None),
    "308" : ("Humppila", None, None, None),
    "309" : ("Hämeenlinna", None, None, None),
    "310" : ("Janakkala", None, None, None),
    "311" : ("Jokioinen", None, None, None),
    "312" : ("Juupajoki", None, None, None),
    "313" : ("Kalvola", None, None, None),
    "314" : ("Kangasala", None, None, None),
    "315" : ("Hämeenkoski", None, None, None),
    "316" : ("Kuhmalahti", None, None, None),
    "318" : ("Kuru", None, None, None),
    "319" : ("Kylmäkoski", None, None, None),
    "320" : ("Kärkölä", None, None, None),
    "321" : ("Lahti", None, None, None),
    "322" : ("Lammi", None, None, None),
    "323" : ("Lempäälä", None, None, None),
    "324" : ("Loppi", None, None, None),
    "325" : ("Luopioinen", None, None, None),
    "326" : ("Längelmäki", None, None, None),
    "327" : ("Mänttä", None, None, None),
    "328" : ("Nastola", None, None, None),
    "329" : ("Nokia", None, None, None),
    "330" : ("Orivesi", None, None, None),
    "331" : ("Padasjoki", None, None, None),
    "332" : ("Pirkkala", None, None, None),
    "333" : ("Pälkäne", None, None, None),
    "334" : ("Renko", None, None, None),
    "335" : ("Riihimäki", None, None, None),
    "336" : ("Ruovesi", None, None, None),
    "337" : ("Sahalahti", None, None, None),
    "340" : ("Tammela", None, None, None),
    "341" : ("Tampere", None, None, None),
    "342" : ("Toijala", None, None, None),
    "344" : ("Tuulos", None, None, None),
    "345" : ("Urjala", None, None, None),
    "346" : ("Valkeakoski", None, None, None),
    "347" : ("Vesilahti", None, None, None),
    "348" : ("Viiala", None, None, None),
    "349" : ("Vilppula", None, None, None),
    "350" : ("Virrat", None, None, None),
    "351" : ("Ylöjärvi", None, None, None),
    "352" : ("Ypäjä", None, None, None),
    "353" : ("Hämeenkyrö", None, None, None),
    "354" : ("Ikaalinen", None, None, None),
    "355" : ("Kihniö", None, None, None),
    "356" : ("Mouhijärvi", None, None, None),
    "357" : ("Parkano", None, None, None),
    "358" : ("Viljakkala", None, None, None),
    "402" : ("Enonkoski", None, None, None),
    "403" : ("Hartola", None, None, None),
    "404" : ("Haukivuori", None, None, None),
    "405" : ("Heinola", None, None, None),
    "407" : ("Heinävesi", None, None, None),
    "408" : ("Hirvensalmi", None, None, None),
    "409" : ("Joroinen", None, None, None),
    "410" : ("Juva", None, None, None),
    "411" : ("Jäppilä", None, None, None),
    "412" : ("Kangaslampi", None, None, None),
    "413" : ("Kangasniemi", None, None, None),
    "414" : ("Kerimäki", None, None, None),
    "415" : ("Mikkeli", None, None, None),
    "417" : ("Mäntyharju", None, None, None),
    "418" : ("Pertunmaa", None, None, None),
    "419" : ("Pieksämäki", None, None, None),
    "420" : ("Pieksänmaa", None, None, None),
    "421" : ("Punkaharju", None, None, None),
    "422" : ("Puumala", None, None, None),
    "423" : ("Rantasalmi", None, None, None),
    "424" : ("Ristiina", None, None, None),
    "425" : ("Savonlinna", None, None, None),
    "426" : ("Savonranta", None, None, None),
    "427" : ("Sulkava", None, None, None),
    "428" : ("Sysmä", None, None, None),
    "502" : ("Elimäki", None, None, None),
    "503" : ("Hamina", None, None, None),
    "504" : ("Iitti", None, None, None),
    "505" : ("Imatra", None, None, None),
    "506" : ("Jaala", None, None, None),
    "507" : ("Joutseno", None, None, None),
    "509" : ("Kotka", None, None, None),
    "510" : ("Kouvola", None, None, None),
    "511" : ("Kuusankoski", None, None, None),
    "513" : ("Lappeenranta", None, None, None),
    "514" : ("Lemi", None, None, None),
    "515" : ("Luumäki", None, None, None),
    "516" : ("Miehikkälä", None, None, None),
    "518" : ("Parikkala", None, None, None),
    "519" : ("Pyhtää", None, None, None),
    "520" : ("Rautjärvi", None, None, None),
    "521" : ("Ruokolahti", None, None, None),
    "522" : ("Saari", None, None, None),
    "523" : ("Savitaipale", None, None, None),
    "525" : ("Suomenniemi", None, None, None),
    "526" : ("Taipalsaari", None, None, None),
    "527" : ("Uukuniemi", None, None, None),
    "528" : ("Valkeala", None, None, None),
    "530" : ("Virolahti", None, None, None),
    "531" : ("Ylämaa", None, None, None),
    "532" : ("Anjalankoski", None, None, None),
    "601" : ("Alahärmä", None, None, None),
    "602" : ("Alajärvi", None, None, None),
    "603" : ("Alavus", None, None, None),
    "604" : ("Evijärvi", None, None, None),
    "605" : ("Halsua", None, None, None),
    "606" : ("Hankasalmi", None, None, None),
    "607" : ("Himanka", None, None, None),
    "608" : ("Ilmajoki", None, None, None),
    "609" : ("Isojoki", None, None, None),
    "610" : ("Isokyrö", None, None, None),
    "611" : ("Jalasjärvi", None, None, None),
    "612" : ("Joutsa", None, None, None),
    "613" : ("Jurva", None, None, None),
    "614" : ("Jyväskylä", None, None, None),
    "615" : ("Jyväskylän mlk", None, None, None),
    "616" : ("Jämsä", None, None, None),
    "617" : ("Jämsänkoski", None, None, None),
    "619" : ("Kannonkoski", None, None, None),
    "620" : ("Kannus", None, None, None),
    "621" : ("Karijoki", None, None, None),
    "622" : ("Karstula", None, None, None),
    "623" : ("Kaskinen", None, None, None),
    "624" : ("Kauhajoki", None, None, None),
    "625" : ("Kauhava", None, None, None),
    "626" : ("Kaustinen", None, None, None),
    "627" : ("Keuruu", None, None, None),
    "628" : ("Kinnula", None, None, None),
    "629" : ("Kivijärvi", None, None, None),
    "630" : ("Kokkola", None, None, None),
    "632" : ("Konnevesi", None, None, None),
    "633" : ("Korpilahti", None, None, None),
    "634" : ("Korsnäs", None, None, None),
    "635" : ("Kortesjärvi", None, None, None),
    "636" : ("Kristiinankaupunki", None, None, None),
    "637" : ("Kruunupyy", None, None, None),
    "638" : ("Kuhmoinen", None, None, None),
    "639" : ("Kuortane", None, None, None),
    "640" : ("Kurikka", None, None, None),
    "641" : ("Kyyjärvi", None, None, None),
    "642" : ("Kälviä", None, None, None),
    "643" : ("Laihia", None, None, None),
    "644" : ("Lappajärvi", None, None, None),
    "645" : ("Lapua", None, None, None),
    "646" : ("Laukaa", None, None, None),
    "647" : ("Lehtimäki", None, None, None),
    "648" : ("Leivonmäki", None, None, None),
    "649" : ("Lestijärvi", None, None, None),
    "650" : ("Lohtaja", None, None, None),
    "651" : ("Luhanka", None, None, None),
    "652" : ("Luoto", None, None, None),
    "653" : ("Maalahti", None, None, None),
    "654" : ("Maksamaa", None, None, None),
    "655" : ("Multia", None, None, None),
    "656" : ("Mustasaari", None, None, None),
    "657" : ("Muurame", None, None, None),
    "658" : ("Nurmo", None, None, None),
    "659" : ("Närpiö", None, None, None),
    "660" : ("Oravainen", None, None, None),
    "661" : ("Perho", None, None, None),
    "662" : ("Peräseinäjoki", None, None, None),
    "663" : ("Petäjävesi", None, None, None),
    "664" : ("Pietarsaari", None, None, None),
    "665" : ("Pedersöre", None, None, None),
    "666" : ("Pihtipudas", None, None, None),
    "668" : ("Pylkönmäki", None, None, None),
    "669" : ("Saarijärvi", None, None, None),
    "670" : ("Seinäjoki", None, None, None),
    "671" : ("Soini", None, None, None),
    "672" : ("Sumiainen", None, None, None),
    "673" : ("Suolahti", None, None, None),
    "675" : ("Teuva", None, None, None),
    "676" : ("Toholampi", None, None, None),
    "677" : ("Toivakka", None, None, None),
    "678" : ("Töysä", None, None, None),
    "679" : ("Ullava", None, None, None),
    "680" : ("Uurainen", None, None, None),
    "681" : ("Uusikaarlepyy", None, None, None),
    "682" : ("Vaasa", None, None, None),
    "683" : ("Veteli", None, None, None),
    "684" : ("Viitasaari", None, None, None),
    "685" : ("Vimpeli", None, None, None),
    "686" : ("Vähäkyrö", None, None, None),
    "687" : ("Vöyri", None, None, None),
    "688" : ("Ylihärmä", None, None, None),
    "689" : ("Ylistaro", None, None, None),
    "690" : ("Ähtäri", None, None, None),
    "692" : ("Äänekoski", None, None, None),
    "701" : ("Eno", None, None, None),
    "702" : ("Iisalmi", None, None, None),
    "703" : ("Ilomantsi", None, None, None),
    "704" : ("Joensuu", None, None, None),
    "705" : ("Juankoski", None, None, None),
    "706" : ("Juuka", None, None, None),
    "707" : ("Kaavi", None, None, None),
    "708" : ("Karttula", None, None, None),
    "709" : ("Keitele", None, None, None),
    "710" : ("Kesälahti", None, None, None),
    "711" : ("Kiihtelysvaara", None, None, None),
    "712" : ("Kitee", None, None, None),
    "713" : ("Kiuruvesi", None, None, None),
    "714" : ("Kontiolahti", None, None, None),
    "715" : ("Kuopio", None, None, None),
    "716" : ("Lapinlahti", None, None, None),
    "717" : ("Leppävirta", None, None, None),
    "718" : ("Lieksa", None, None, None),
    "719" : ("Liperi", None, None, None),
    "720" : ("Maaninka", None, None, None),
    "721" : ("Nilsiä", None, None, None),
    "722" : ("Nurmes", None, None, None),
    "723" : ("Outokumpu", None, None, None),
    "724" : ("Pielavesi", None, None, None),
    "725" : ("Polvijärvi", None, None, None),
    "726" : ("Pyhäselkä", None, None, None),
    "727" : ("Rautalampi", None, None, None),
    "728" : ("Rautavaara", None, None, None),
    "729" : ("Rääkkylä", None, None, None),
    "730" : ("Siilinjärvi", None, None, None),
    "731" : ("Sonkajärvi", None, None, None),
    "732" : ("Suonenjoki", None, None, None),
    "733" : ("Tervo", None, None, None),
    "734" : ("Tohmajärvi", None, None, None),
    "735" : ("Tuupovaara", None, None, None),
    "736" : ("Tuusniemi", None, None, None),
    "737" : ("Valtimo", None, None, None),
    "738" : ("Varkaus", None, None, None),
    "739" : ("Varpaisjärvi", None, None, None),
    "740" : ("Vehmersalmi", None, None, None),
    "741" : ("Vesanto", None, None, None),
    "742" : ("Vieremä", None, None, None),
    "743" : ("Värtsilä", None, None, None),
    "801" : ("Alavieska", None, None, None),
    "802" : ("Haapajärvi", None, None, None),
    "803" : ("Haapavesi", None, None, None),
    "804" : ("Hailuoto", None, None, None),
    "805" : ("Haukipudas", None, None, None),
    "806" : ("Hyrynsalmi", None, None, None),
    "807" : ("Ii", None, None, None),
    "808" : ("Kajaani", None, None, None),
    "810" : ("Kalajoki", None, None, None),
    "811" : ("Kempele", None, None, None),
    "812" : ("Kestilä", None, None, None),
    "813" : ("Kiiminki", None, None, None),
    "814" : ("Kuhmo", None, None, None),
    "815" : ("Kuivaniemi", None, None, None),
    "816" : ("Kuusamo", None, None, None),
    "817" : ("Kärsämäki", None, None, None),
    "818" : ("Liminka", None, None, None),
    "819" : ("Lumijoki", None, None, None),
    "820" : ("Merijärvi", None, None, None),
    "821" : ("Muhos", None, None, None),
    "822" : ("Nivala", None, None, None),
    "823" : ("Oulainen", None, None, None),
    "824" : ("Oulu", None, None, None),
    "825" : ("Oulunsalo", None, None, None),
    "826" : ("Paltamo", None, None, None),
    "827" : ("Pattijoki", None, None, None),
    "828" : ("Piippola", None, None, None),
    "829" : ("Pudasjärvi", None, None, None),
    "830" : ("Pulkkila", None, None, None),
    "831" : ("Puolanka", None, None, None),
    "832" : ("Pyhäjoki", None, None, None),
    "833" : ("Pyhäjärvi", None, None, None),
    "834" : ("Pyhäntä", None, None, None),
    "835" : ("Raahe", None, None, None),
    "836" : ("Rantsila", None, None, None),
    "837" : ("Reisjärvi", None, None, None),
    "838" : ("Ristijärvi", None, None, None),
    "839" : ("Ruukki", None, None, None),
    "840" : ("Sievi", None, None, None),
    "841" : ("Siikajoki", None, None, None),
    "842" : ("Sotkamo", None, None, None),
    "843" : ("Suomussalmi", None, None, None),
    "844" : ("Taivalkoski", None, None, None),
    "846" : ("Tyrnävä", None, None, None),
    "847" : ("Utajärvi", None, None, None),
    "848" : ("Vaala", None, None, None),
    "849" : ("Vihanti", None, None, None),
    "850" : ("Vuolijoki", None, None, None),
    "851" : ("Yli-Ii", None, None, None),
    "852" : ("Ylikiiminki", None, None, None),
    "853" : ("Ylivieska", None, None, None),
    "901" : ("Enontekiö", None, None, None),
    "902" : ("Inari", None, None, None),
    "903" : ("Kemi", None, None, None),
    "904" : ("Keminmaa", None, None, None),
    "905" : ("Kemijärvi", None, None, None),
    "907" : ("Kittilä", None, None, None),
    "908" : ("Kolari", None, None, None),
    "909" : ("Muonio", None, None, None),
    "910" : ("Pelkosenniemi", None, None, None),
    "911" : ("Pello", None, None, None),
    "912" : ("Posio", None, None, None),
    "913" : ("Ranua", None, None, None),
    "914" : ("Rovaniemi", None, None, None),
    "915" : ("Rovaniemen mlk", None, None, None),
    "916" : ("Salla", None, None, None),
    "917" : ("Savukoski", None, None, None),
    "918" : ("Simo", None, None, None),
    "919" : ("Sodankylä", None, None, None),
    "920" : ("Tervola", None, None, None),
    "921" : ("Tornio", None, None, None),
    "922" : ("Utsjoki", None, None, None),
    "923" : ("Ylitornio", None, None, None)
    }

Primary_Administrative_Subdivision_Enumeration_225 = {
    "CA" : ("Cagliari", None, None, None),
    "CI" : ("Carbonia-Iglesias", None, None, None),
    "MD" : ("Medio Campidano (import-only)", None, None, None),
    "NU" : ("Nuoro", None, None, None),
    "OG" : ("Ogliastra", None, None, None),
    "OR" : ("Oristano", None, None, None),
    "OT" : ("Olbia-Tempio", None, None, None),
    "SS" : ("Sassari", None, None, None),
    "VS" : ("MedioCampidano", None, None, None)
    }

Primary_Administrative_Subdivision_Enumeration_227 = {
    "01" : ("Ain", None, None, None),
    "02" : ("Aisne", None, None, None),
    "03" : ("Allier", None, None, None),
    "04" : ("Alpes-de-Haute-Provence", None, None, None),
    "05" : ("Hautes-Alpes", None, None, None),
    "06" : ("Alpes-Maritimes", None, None, None),
    "07" : ("Ardèche", None, None, None),
    "08" : ("Ardennes", None, None, None),
    "09" : ("Ariège", None, None, None),
    "10" : ("Aube", None, None, None),
    "11" : ("Aude", None, None, None),
    "12" : ("Aveyron", None, None, None),
    "13" : ("Bouches-du-Rhone", None, None, None),
    "14" : ("Calvados", None, None, None),
    "15" : ("Cantal", None, None, None),
    "16" : ("Charente", None, None, None),
    "17" : ("Charente-Maritime", None, None, None),
    "18" : ("Cher", None, None, None),
    "19" : ("Corrèze", None, None, None),
    "21" : ("Cote-d'Or", None, None, None),
    "22" : ("Cotes-d'Armor", None, None, None),
    "23" : ("Creuse", None, None, None),
    "24" : ("Dordogne", None, None, None),
    "25" : ("Doubs", None, None, None),
    "26" : ("Drôme", None, None, None),
    "27" : ("Eure", None, None, None),
    "28" : ("Eure-et-Loir", None, None, None),
    "29" : ("Finistère", None, None, None),
    "30" : ("Gard", None, None, None),
    "31" : ("Haute-Garonne", None, None, None),
    "32" : ("Gere", None, None, None),
    "33" : ("Gironde", None, None, None),
    "34" : ("Hérault", None, None, None),
    "35" : ("Ille-et-Vilaine", None, None, None),
    "36" : ("Indre", None, None, None),
    "37" : ("Indre-et-Loire", None, None, None),
    "38" : ("Isère", None, None, None),
    "39" : ("Jura", None, None, None),
    "40" : ("Landes", None, None, None),
    "41" : ("Loir-et-Cher", None, None, None),
    "42" : ("Loire", None, None, None),
    "43" : ("Haute-Loire", None, None, None),
    "44" : ("Loire-Atlantique", None, None, None),
    "45" : ("Loiret", None, None, None),
    "46" : ("Lot", None, None, None),
    "47" : ("Lot-et-Garonne", None, None, None),
    "48" : ("Lozère", None, None, None),
    "49" : ("Maine-et-Loire", None, None, None),
    "50" : ("Manche", None, None, None),
    "51" : ("Marne", None, None, None),
    "52" : ("Haute-Marne", None, None, None),
    "53" : ("Mayenne", None, None, None),
    "54" : ("Meurthe-et-Moselle", None, None, None),
    "55" : ("Meuse", None, None, None),
    "56" : ("Morbihan", None, None, None),
    "57" : ("Moselle", None, None, None),
    "58" : ("Niëvre", None, None, None),
    "59" : ("Nord", None, None, None),
    "60" : ("Oise", None, None, None),
    "61" : ("Orne", None, None, None),
    "62" : ("Pas-de-Calais", None, None, None),
    "63" : ("Puy-de-Dôme", None, None, None),
    "64" : ("Pyrénées-Atlantiques", None, None, None),
    "65" : ("Hautea-Pyrénées", None, None, None),
    "66" : ("Pyrénées-Orientales", None, None, None),
    "67" : ("Bas-Rhin", None, None, None),
    "68" : ("Haut-Rhin", None, None, None),
    "69" : ("Rhône", None, None, None),
    "70" : ("Haute-Saône", None, None, None),
    "71" : ("Saône-et-Loire", None, None, None),
    "72" : ("Sarthe", None, None, None),
    "73" : ("Savoie", None, None, None),
    "74" : ("Haute-Savoie", None, None, None),
    "75" : ("Paris", None, None, None),
    "76" : ("Seine-Maritime", None, None, None),
    "77" : ("Seine-et-Marne", None, None, None),
    "78" : ("Yvelines", None, None, None),
    "79" : ("Deux-Sèvres", None, None, None),
    "80" : ("Somme", None, None, None),
    "81" : ("Tarn", None, None, None),
    "82" : ("Tarn-et-Garonne", None, None, None),
    "83" : ("Var", None, None, None),
    "84" : ("Vaucluse", None, None, None),
    "85" : ("Vendée", None, None, None),
    "86" : ("Vienne", None, None, None),
    "87" : ("Haute-Vienne", None, None, None),
    "88" : ("Vosges", None, None, None),
    "89" : ("Yonne", None, None, None),
    "90" : ("Territoire de Belfort", None, None, None),
    "91" : ("Essonne", None, None, None),
    "92" : ("Hauts-de-Selne", None, None, None),
    "93" : ("Seine-Saint-Denis", None, None, None),
    "94" : ("Val-de-Marne", None, None, None),
    "95" : ("Val-d'Oise", None, None, None)
    }

Primary_Administrative_Subdivision_Enumeration_230 = {
    "BB" : ("Brandenburg", None, None, None),
    "BE" : ("Berlin", None, None, None),
    "BW" : ("Baden-Württemberg", None, None, None),
    "BY" : ("Freistaat Bayern", None, None, None),
    "HB" : ("Freie Hansestadt Bremen", None, None, None),
    "HE" : ("Hessen", None, None, None),
    "HH" : ("Freie und Hansestadt Hamburg", None, None, None),
    "MV" : ("Mecklenburg-Vorpommern", None, None, None),
    "NI" : ("Niedersachsen", None, None, None),
    "NW" : ("Nordrhein-Westfalen", None, None, None),
    "RP" : ("Rheinland-Pfalz", None, None, None),
    "SL" : ("Saarland", None, None, None),
    "SH" : ("Schleswig-Holstein", None, None, None),
    "SN" : ("Freistaat Sachsen", None, None, None),
    "ST" : ("Sachsen-Anhalt", None, None, None),
    "TH" : ("Freistaat Thüringen", None, None, None)
    }

Primary_Administrative_Subdivision_Enumeration_239 = {
    "GY" : ("Gyõr (Gyõr-Moson-Sopron)", None, None, None),
    "VA" : ("Vas", None, None, None),
    "ZA" : ("Zala", None, None, None),
    "KO" : ("Komárom (Komárom-Esztergom)", None, None, None),
    "VE" : ("Veszprém", None, None, None),
    "BA" : ("Baranya", None, None, None),
    "SO" : ("Somogy", None, None, None),
    "TO" : ("Tolna", None, None, None),
    "FE" : ("Fejér", None, None, None),
    "BP" : ("Budapest", None, None, None),
    "HE" : ("Heves", None, None, None),
    "NG" : ("Nógrád", None, None, None),
    "PE" : ("Pest", None, None, None),
    "SZ" : ("Szolnok (Jász-Nagykun-Szolnok)", None, None, None),
    "BE" : ("Békés", None, None, None),
    "BN" : ("Bács-Kiskun", None, None, None),
    "CS" : ("Csongrád", None, None, None),
    "BO" : ("Borsod (Borsod-Abaúj-Zemplén)", None, None, None),
    "HB" : ("Hajdú-Bihar", None, None, None),
    "SA" : ("Szabolcs (Szabolcs-Szatmár-Bereg)", None, None, None)
    }

Primary_Administrative_Subdivision_Enumeration_245 = {
    "CW" : ("Carlow (Ceatharlach)", None, None, None),
    "CN" : ("Cavan (An Cabhán)", None, None, None),
    "CE" : ("Clare (An Clár)", None, None, None),
    "C" : ("Cork (Corcaigh)", None, None, None),
    "DL" : ("Donegal (Dún na nGall)", None, None, None),
    "D" : ("Dublin (Baile Áth Cliath)", None, None, None),
    "G" : ("Galway (Gaillimh)", None, None, None),
    "KY" : ("Kerry (Ciarraí)", None, None, None),
    "KE" : ("Kildare (Cill Dara)", None, None, None),
    "KK" : ("Kilkenny (Cill Chainnigh)", None, None, None),
    "LS" : ("Laois (Laois)", None, None, None),
    "LM" : ("Leitrim (Liatroim)", None, None, None),
    "LK" : ("Limerick (Luimneach)", None, None, None),
    "LD" : ("Longford (An Longfort)", None, None, None),
    "LH" : ("Louth (Lú)", None, None, None),
    "MO" : ("Mayo (Maigh Eo)", None, None, None),
    "MH" : ("Meath (An Mhí)", None, None, None),
    "MN" : ("Monaghan (Muineachán)", None, None, None),
    "OY" : ("Offaly (Uíbh Fhailí)", None, None, None),
    "RN" : ("Roscommon (Ros Comáin)", None, None, None),
    "SO" : ("Sligo (Sligeach)", None, None, None),
    "TA" : ("Tipperary (Tiobraid Árann)", None, None, None),
    "WD" : ("Waterford (Port Láirge)", None, None, None),
    "WH" : ("Westmeath (An Iarmhí)", None, None, None),
    "WX" : ("Wexford (Loch Garman)", None, None, None),
    "WW" : ("Wicklow (Cill Mhantáin)", None, None, None)
    }

Primary_Administrative_Subdivision_Enumeration_248 = {
    "GE" : ("Genova", None, None, None),
    "IM" : ("Imperia", None, None, None),
    "SP" : ("La Spezia", None, None, None),
    "SV" : ("Savona", None, None, None),
    "AL" : ("Alessandria", None, None, None),
    "AT" : ("Asti", None, None, None),
    "BI" : ("Biella", None, None, None),
    "CN" : ("Cuneo", None, None, None),
    "NO" : ("Novara", None, None, None),
    "TO" : ("Torino", None, None, None),
    "VB" : ("Verbano Cusio Ossola", None, None, None),
    "VC" : ("Vercelli", None, None, None),
    "AO" : ("Aosta", None, None, None),
    "BG" : ("Bergamo", None, None, None),
    "BS" : ("Brescia", None, None, None),
    "CO" : ("Como", None, None, None),
    "CR" : ("Cremona", None, None, None),
    "LC" : ("Lecco", None, None, None),
    "LO" : ("Lodi", None, None, None),
    "MB" : ("Monza e Brianza", None, None, None),
    "MN" : ("Mantova", None, None, None),
    "MI" : ("Milano", None, None, None),
    "PV" : ("Pavia", None, None, None),
    "SO" : ("Sondrio", None, None, None),
    "VA" : ("Varese", None, None, None),
    "BL" : ("Belluno", None, None, None),
    "PD" : ("Padova", None, None, None),
    "RO" : ("Rovigo", None, None, None),
    "TV" : ("Treviso", None, None, None),
    "VE" : ("Venezia", None, None, None),
    "VR" : ("Verona", None, None, None),
    "VI" : ("Vicenza", None, None, None),
    "BZ" : ("Bolzano", None, None, None),
    "TN" : ("Trento", None, None, None),
    "GO" : ("Gorizia", None, None, None),
    "PN" : ("Pordenone", None, None, None),
    "TS" : ("Trieste", None, None, None),
    "UD" : ("Udine", None, None, None),
    "BO" : ("Bologna", None, None, None),
    "FE" : ("Ferrara", None, None, None),
    "FO" : ("Forlì (import-only)", None, None, None),
    "FC" : ("Forlì-Cesena", None, None, None),
    "MO" : ("Modena", None, None, None),
    "PR" : ("Parma", None, None, None),
    "PC" : ("Piacenza", None, None, None),
    "RA" : ("Ravenna", None, None, None),
    "RE" : ("Reggio Emilia", None, None, None),
    "RN" : ("Rimini", None, None, None),
    "AR" : ("Arezzo", None, None, None),
    "FI" : ("Firenze", None, None, None),
    "GR" : ("Grosseto", None, None, None),
    "LI" : ("Livorno", None, None, None),
    "LU" : ("Lucca", None, None, None),
    "MS" : ("Massa Carrara", None, None, None),
    "PT" : ("Pistoia", None, None, None),
    "PI" : ("Pisa", None, None, None),
    "PO" : ("Prato", None, None, None),
    "SI" : ("Siena", None, None, None),
    "CH" : ("Chieti", None, None, None),
    "AQ" : ("L'Aquila", None, None, None),
    "PE" : ("Pescara", None, None, None),
    "TE" : ("Teramo", None, None, None),
    "AN" : ("Ancona", None, None, None),
    "AP" : ("Ascoli Piceno", None, None, None),
    "FM" : ("Fermo", None, None, None),
    "MC" : ("Macerata", None, None, None),
    "PS" : ("Pesaro e Urbino (import-only)", None, None, None),
    "PU" : ("Pesaro e Urbino", None, None, None),
    "MT" : ("Matera", None, None, None),
    "PZ" : ("Potenza", None, None, None),
    "BA" : ("Bari", None, None, None),
    "BT" : ("Barletta-Andria-Trani", None, None, None),
    "BR" : ("Brindisi", None, None, None),
    "FG" : ("Foggia", None, None, None),
    "LE" : ("Lecce", None, None, None),
    "TA" : ("Taranto", None, None, None),
    "CZ" : ("Catanzaro", None, None, None),
    "CS" : ("Cosenza", None, None, None),
    "KR" : ("Crotone", None, None, None),
    "RC" : ("Reggio Calabria", None, None, None),
    "VV" : ("Vibo Valentia", None, None, None),
    "AV" : ("Avellino", None, None, None),
    "BN" : ("Benevento", None, None, None),
    "CE" : ("Caserta", None, None, None),
    "NA" : ("Napoli", None, None, None),
    "SA" : ("Salerno", None, None, None),
    "IS" : ("Isernia", None, None, None),
    "CB" : ("Campobasso", None, None, None),
    "FR" : ("Frosinone", None, None, None),
    "LT" : ("Latina", None, None, None),
    "RI" : ("Rieti", None, None, None),
    "RM" : ("Roma", None, None, None),
    "VT" : ("Viterbo", None, None, None),
    "PG" : ("Perugia", None, None, None),
    "TR" : ("Terni", None, None, None),
    "AG" : ("Agrigento", None, None, None),
    "CL" : ("Caltanissetta", None, None, None),
    "CT" : ("Catania", None, None, None),
    "EN" : ("Enna", None, None, None),
    "ME" : ("Messina", None, None, None),
    "PA" : ("Palermo", None, None, None),
    "RG" : ("Ragusa", None, None, None),
    "SR" : ("Siracusa", None, None, None),
    "TP" : ("Trapani", None, None, None)
    }

Primary_Administrative_Subdivision_Enumeration_256 = {
    "MD" : ("Madeira", None, None, None)
    }

Primary_Administrative_Subdivision_Enumeration_263 = {
    "DR" : ("Drenthe", None, None, None),
    "FR" : ("Friesland", None, None, None),
    "GR" : ("Groningen", None, None, None),
    "NB" : ("Noord-Brabant", None, None, None),
    "OV" : ("Overijssel", None, None, None),
    "ZH" : ("Zuid-Holland", None, None, None),
    "FL" : ("Flevoland", None, None, None),
    "GD" : ("Gelderland", None, None, None),
    "LB" : ("Limburg", None, None, None),
    "NH" : ("Noord-Holland", None, None, None),
    "UT" : ("Utrecht", None, None, None),
    "ZL" : ("Zeeland", None, None, None)
    }

Primary_Administrative_Subdivision_Enumeration_269 = {
    "Z" : ("Zachodnio-Pomorskie", None, None, None),
    "F" : ("Pomorskie", None, None, None),
    "P" : ("Kujawsko-Pomorskie", None, None, None),
    "B" : ("Lubuskie", None, None, None),
    "W" : ("Wielkopolskie", None, None, None),
    "J" : ("Warminsko-Mazurskie", None, None, None),
    "O" : ("Podlaskie", None, None, None),
    "R" : ("Mazowieckie", None, None, None),
    "D" : ("Dolnoslaskie", None, None, None),
    "U" : ("Opolskie", None, None, None),
    "C" : ("Lodzkie", None, None, None),
    "S" : ("Swietokrzyskie", None, None, None),
    "K" : ("Podkarpackie", None, None, None),
    "L" : ("Lubelskie", None, None, None),
    "G" : ("Slaskie", None, None, None),
    "M" : ("Malopolskie", None, None, None)
    }

Primary_Administrative_Subdivision_Enumeration_272 = {
    "AV" : ("Aveiro", None, None, None),
    "BJ" : ("Beja", None, None, None),
    "BR" : ("Braga", None, None, None),
    "BG" : ("Bragança", None, None, None),
    "CB" : ("Castelo Branco", None, None, None),
    "CO" : ("Coimbra", None, None, None),
    "EV" : ("Evora", None, None, None),
    "FR" : ("Faro", None, None, None),
    "GD" : ("Guarda", None, None, None),
    "LR" : ("Leiria", None, None, None),
    "LX" : ("Lisboa", None, None, None),
    "PG" : ("Portalegre", None, None, None),
    "PT" : ("Porto", None, None, None),
    "SR" : ("Santarem", None, None, None),
    "ST" : ("Setubal", None, None, None),
    "VC" : ("Viana do Castelo", None, None, None),
    "VR" : ("Vila Real", None, None, None),
    "VS" : ("Viseu", None, None, None)
    }

Primary_Administrative_Subdivision_Enumeration_275 = {
    "AR" : ("Arad", None, None, None),
    "CS" : ("Cara'-Severin", None, None, None),
    "HD" : ("Hunedoara", None, None, None),
    "TM" : ("Timiş (Timis)", None, None, None),
    "BU" : ("Bucureşti (Bucure'ti)", None, None, None),
    "IF" : ("Ilfov", None, None, None),
    "BR" : ("Brăila (Braila)", None, None, None),
    "CT" : ("Conatarta", None, None, None),
    "GL" : ("Galati", None, None, None),
    "TL" : ("Tulcea", None, None, None),
    "VN" : ("Vrancea", None, None, None),
    "AB" : ("Alba", None, None, None),
    "BH" : ("Bihor", None, None, None),
    "BN" : ("Bistrita-Nasaud", None, None, None),
    "CJ" : ("Cluj", None, None, None),
    "MM" : ("Maramureş (Maramures)", None, None, None),
    "SJ" : ("Sălaj (Salaj)", None, None, None),
    "SM" : ("Satu Mare", None, None, None),
    "BV" : ("Braşov (Bra'ov)", None, None, None),
    "CV" : ("Covasna", None, None, None),
    "HR" : ("Harghita", None, None, None),
    "MS" : ("Mureş (Mures)", None, None, None),
    "SB" : ("Sibiu", None, None, None),
    "AG" : ("Arge'", None, None, None),
    "DJ" : ("Dolj", None, None, None),
    "GJ" : ("Gorj", None, None, None),
    "MH" : ("Mehedinţi (Mehedinti)", None, None, None),
    "OT" : ("Olt", None, None, None),
    "VL" : ("Vâlcea", None, None, None),
    "BC" : ("Bacau", None, None, None),
    "BT" : ("Boto'ani", None, None, None),
    "IS" : ("Iaşi (Iasi)", None, None, None),
    "NT" : ("Neamţ (Neamt)", None, None, None),
    "SV" : ("Suceava", None, None, None),
    "VS" : ("Vaslui", None, None, None),
    "BZ" : ("Buzău (Buzau)", None, None, None),
    "CL" : ("Călăraşi (Calarasi)", None, None, None),
    "DB" : ("Dâmboviţa (Dambovita)", None, None, None),
    "GR" : ("Giurqiu", None, None, None),
    "IL" : ("Ialomita", None, None, None),
    "PH" : ("Prahova", None, None, None),
    "TR" : ("Teleorman", None, None, None)
    }

Primary_Administrative_Subdivision_Enumeration_281 = {
    "AV" : ("Avila", None, None, None),
    "BU" : ("Burgos", None, None, None),
    "C" : ("A Coruña", None, None, None),
    "LE" : ("Leon", None, None, None),
    "LO" : ("La Rioja", None, None, None),
    "LU" : ("Lugo", None, None, None),
    "O" : ("Asturias", None, None, None),
    "OU" : ("Ourense", None, None, None),
    "P" : ("Palencia", None, None, None),
    "PO" : ("Pontevedra", None, None, None),
    "S" : ("Cantabria", None, None, None),
    "SA" : ("Salamanca", None, None, None),
    "SG" : ("Segovia", None, None, None),
    "SO" : ("Soria", None, None, None),
    "VA" : ("Valladolid", None, None, None),
    "ZA" : ("Zamora", None, None, None),
    "BI" : ("Vizcaya", None, None, None),
    "HU" : ("Huesca", None, None, None),
    "NA" : ("Navarra", None, None, None),
    "SS" : ("Guipuzcoa", None, None, None),
    "TE" : ("Teruel", None, None, None),
    "VI" : ("Alava", None, None, None),
    "Z" : ("Zaragoza", None, None, None),
    "B" : ("Barcelona", None, None, None),
    "GI" : ("Girona", None, None, None),
    "L" : ("Lleida", None, None, None),
    "T" : ("Tarragona", None, None, None),
    "BA" : ("Badajoz", None, None, None),
    "CC" : ("Caceres", None, None, None),
    "CR" : ("Ciudad Real", None, None, None),
    "CU" : ("Cuenca", None, None, None),
    "GU" : ("Guadalajara", None, None, None),
    "M" : ("Madrid", None, None, None),
    "TO" : ("Toledo", None, None, None),
    "A" : ("Alicante", None, None, None),
    "AB" : ("Albacete", None, None, None),
    "CS" : ("Castellon", None, None, None),
    "MU" : ("Murcia", None, None, None),
    "V" : ("Valencia", None, None, None),
    "AL" : ("Almeria", None, None, None),
    "CA" : ("Cadiz", None, None, None),
    "CO" : ("Cordoba", None, None, None),
    "GR" : ("Granada", None, None, None),
    "H" : ("Huelva", None, None, None),
    "J" : ("Jaen", None, None, None),
    "MA" : ("Malaga", None, None, None),
    "SE" : ("Sevilla", None, None, None)
    }

Primary_Administrative_Subdivision_Enumeration_284 = {
    "AB" : ("Stockholm län", None, None, None),
    "I" : ("Gotlands län", None, None, None),
    "BD" : ("Norrbottens län", None, None, None),
    "AC" : ("Västerbottens län", None, None, None),
    "X" : ("Gävleborgs län", None, None, None),
    "Z" : ("Jämtlands län", None, None, None),
    "Y" : ("Västernorrlands län", None, None, None),
    "W" : ("Dalarna län", None, None, None),
    "S" : ("Värmlands län", None, None, None),
    "O" : ("Västra Götalands län", None, None, None),
    "T" : ("Örebro län", None, None, None),
    "E" : ("Östergötlands län", None, None, None),
    "D" : ("Södermanlands län", None, None, None),
    "C" : ("Uppsala län", None, None, None),
    "U" : ("Västmanlands län", None, None, None),
    "N" : ("Hallands län", None, None, None),
    "K" : ("Blekinge län", None, None, None),
    "F" : ("Jönköpings län", None, None, None),
    "H" : ("Kalmar län", None, None, None),
    "G" : ("Kronobergs län", None, None, None),
    "M" : ("Skåne län", None, None, None)
    }

Primary_Administrative_Subdivision_Enumeration_287 = {
    "AG" : ("Aargau", None, None, None),
    "AR" : ("Appenzell Ausserrhoden", None, None, None),
    "AI" : ("Appenzell Innerrhoden", None, None, None),
    "BL" : ("Basel Landschaft", None, None, None),
    "BS" : ("Basel Stadt", None, None, None),
    "BE" : ("Bern", None, None, None),
    "FR" : ("Freiburg / Fribourg", None, None, None),
    "GE" : ("Genf / Genève", None, None, None),
    "GL" : ("Glarus", None, None, None),
    "GR" : ("Graubuenden / Grisons", None, None, None),
    "JU" : ("Jura", None, None, None),
    "LU" : ("Luzern", None, None, None),
    "NE" : ("Neuenburg / Neuchâtel", None, None, None),
    "NW" : ("Nidwalden", None, None, None),
    "OW" : ("Obwalden", None, None, None),
    "SH" : ("Schaffhausen", None, None, None),
    "SZ" : ("Schwyz", None, None, None),
    "SO" : ("Solothurn", None, None, None),
    "SG" : ("St. Gallen", None, None, None),
    "TI" : ("Tessin / Ticino", None, None, None),
    "TG" : ("Thurgau", None, None, None),
    "UR" : ("Uri", None, None, None),
    "VD" : ("Waadt / Vaud", None, None, None),
    "VS" : ("Wallis / Valais", None, None, None),
    "ZH" : ("Zuerich", None, None, None),
    "ZG" : ("Zug", None, None, None)
    }

Primary_Administrative_Subdivision_Enumeration_288 = {
    "SU" : ("Sums'ka Oblast'", None, None, None),
    "TE" : ("Ternopil's'ka Oblast'", None, None, None),
    "CH" : ("Cherkas'ka Oblast'", None, None, None),
    "ZA" : ("Zakarpats'ka Oblast'", None, None, None),
    "DN" : ("Dnipropetrovs'ka Oblast'", None, None, None),
    "OD" : ("Odes'ka Oblast'", None, None, None),
    "HE" : ("Khersons'ka Oblast'", None, None, None),
    "PO" : ("Poltavs'ka Oblast'", None, None, None),
    "DO" : ("Donets'ka Oblast'", None, None, None),
    "RI" : ("Rivnens'ka Oblast'", None, None, None),
    "HA" : ("Kharkivs'ka Oblast'", None, None, None),
    "LU" : ("Luhans'ka Oblast'", None, None, None),
    "VI" : ("Vinnyts'ka Oblast'", None, None, None),
    "VO" : ("Volyos'ka Oblast'", None, None, None),
    "ZP" : ("Zaporiz'ka Oblast'", None, None, None),
    "CR" : ("Chernihivs'ka Oblast'", None, None, None),
    "IF" : ("Ivano-Frankivs'ka Oblast'", None, None, None),
    "HM" : ("Khmel'nyts'ka Oblast'", None, None, None),
    "KV" : ("Kyïv", None, None, None),
    "KO" : ("Kyivs'ka Oblast'", None, None, None),
    "KI" : ("Kirovohrads'ka Oblast'", None, None, None),
    "LV" : ("L'vivs'ka Oblast'", None, None, None),
    "ZH" : ("Zhytomyrs'ka Oblast'", None, None, None),
    "CN" : ("Chernivets'ka Oblast'", None, None, None),
    "NI" : ("Mykolaivs'ka Oblast'", None, None, None),
    "KR" : ("Respublika Krym", None, None, None),
    "SL" : ("Sevastopol'", None, None, None)
    }

Primary_Administrative_Subdivision_Enumeration_291 = {
    "CT" : ("Connecticut", None, ("05",), ("08",)),
    "ME" : ("Maine", None, ("05",), ("08",)),
    "MA" : ("Massachusetts", None, ("05",), ("08",)),
    "NH" : ("New Hampshire", None, ("05",), ("08",)),
    "RI" : ("Rhode Island", None, ("05",), ("08",)),
    "VT" : ("Vermont", None, ("05",), ("08",)),
    "NJ" : ("New Jersey", None, ("05",), ("08",)),
    "NY" : ("New York", None, ("05",), ("08",)),
    "DE" : ("Delaware", None, ("05",), ("08",)),
    "DC" : ("District of Columbia", None, ("05",), ("08",)),
    "MD" : ("Maryland", None, ("05",), ("08",)),
    "PA" : ("Pennsylvania", None, ("05",), ("08",)),
    "AL" : ("Alabama", None, ("04",), ("08",)),
    "FL" : ("Florida", None, ("05",), ("08",)),
    "GA" : ("Georgia", None, ("05",), ("08",)),
    "KY" : ("Kentucky", None, ("04",), ("08",)),
    "NC" : ("North Carolina", None, ("04",), ("08",)),
    "SC" : ("South Carolina", None, ("05",), ("08",)),
    "TN" : ("Tennessee", None, ("04",), ("07", "08",)),
    "VA" : ("Virginia", None, ("05",), ("08",)),
    "AR" : ("Arkansas", None, ("04",), ("07", "08",)),
    "LA" : ("Louisiana", None, ("04",), ("07", "08",)),
    "MS" : ("Mississippi", None, ("04",), ("07", "08",)),
    "NM" : ("New Mexico", None, ("04",), ("07",)),
    "OK" : ("Oklahoma", None, ("04",), ("07",)),
    "TX" : ("Texas", None, ("04",), ("07",)),
    "CA" : ("California", None, ("03",), ("06",)),
    "AZ" : ("Arizona", None, ("03",), ("06", "07",)),
    "ID" : ("Idaho", None, ("03",), ("06",)),
    "MT" : ("Montana", None, ("04",), ("06", "07",)),
    "NV" : ("Nevada", None, ("03",), ("06",)),
    "OR" : ("Oregon", None, ("03",), ("06",)),
    "UT" : ("Utah", None, ("03",), ("06", "07",)),
    "WA" : ("Washington", None, ("03",), ("06",)),
    "WY" : ("Wyoming", None, ("04",), ("07",)),
    "MI" : ("Michigan", None, ("04",), ("07", "08",)),
    "OH" : ("Ohio", None, ("04",), ("08",)),
    "WV" : ("West Virginia", None, ("05",), ("08",)),
    "IL" : ("Illinois", None, ("04",), ("07", "08",)),
    "IN" : ("Indiana", None, ("04",), ("08",)),
    "WI" : ("Wisconsin", None, ("04",), ("07", "08",)),
    "CO" : ("Colorado", None, ("04",), ("07",)),
    "IA" : ("Iowa", None, ("04",), ("07",)),
    "KS" : ("Kansas", None, ("04",), ("07",)),
    "MN" : ("Minnesota", None, ("04",), ("07", "08",)),
    "MO" : ("Missouri", None, ("04",), ("07", "08",)),
    "NE" : ("Nebraska", None, ("04",), ("07",)),
    "ND" : ("North Dakota", None, ("04",), ("07",)),
    "SD" : ("South Dakota", None, ("04",), ("07",))
    }

Primary_Administrative_Subdivision_Enumeration_318 = {
    "AH" : ("Anhui", None, None, None),
    "BJ" : ("Beijing", None, None, None),
    "CQ" : ("Chongqing", None, None, None),
    "FJ" : ("Fujian", None, None, None),
    "GD" : ("Guangdong", None, None, None),
    "GS" : ("Gansu", None, None, None),
    "GX" : ("Guangxi Zhuangzu", None, None, None),
    "GZ" : ("Guizhou", None, None, None),
    "HA" : ("Henan", None, None, None),
    "HB" : ("Hubei", None, None, None),
    "HE" : ("Hebei", None, None, None),
    "HI" : ("Hainan", None, None, None),
    "HL" : ("Heilongjiang", None, None, None),
    "HN" : ("Hunan", None, None, None),
    "JL" : ("Jilin", None, None, None),
    "JS" : ("Jiangsu", None, None, None),
    "JX" : ("Jiangxi", None, None, None),
    "LN" : ("Liaoning", None, None, None),
    "NM" : ("Nei Mongol", None, None, None),
    "NX" : ("Ningxia Huizu", None, None, None),
    "QH" : ("Qinghai", None, None, None),
    "SC" : ("Sichuan", None, None, None),
    "SD" : ("Shandong", None, None, None),
    "SH" : ("Shanghai", None, None, None),
    "SN" : ("Shaanxi", None, None, None),
    "SX" : ("Shanxi", None, None, None),
    "TJ" : ("Tianjin", None, None, None),
    "XJ" : ("Xinjiang Uygur", None, None, None),
    "XZ" : ("Xizang", None, None, None),
    "YN" : ("Yunnan", None, None, None),
    "ZJ" : ("Zhejiang", None, None, None),
    }

Primary_Administrative_Subdivision_Enumeration_339 = {
    "12" : ("Chiba", None, None, None),
    "16" : ("Gunma", None, None, None),
    "14" : ("Ibaraki", None, None, None),
    "11" : ("Kanagawa", None, None, None),
    "13" : ("Saitama", None, None, None),
    "15" : ("Tochigi", None, None, None),
    "10" : ("Tokyo", None, None, None),
    "17" : ("Yamanashi", None, None, None),
    "20" : ("Aichi", None, None, None),
    "19" : ("Gifu", None, None, None),
    "21" : ("Mie", None, None, None),
    "18" : ("Shizuoka", None, None, None),
    "27" : ("Hyogo", None, None, None),
    "22" : ("Kyoto", None, None, None),
    "24" : ("Nara", None, None, None),
    "25" : ("Osaka", None, None, None),
    "23" : ("Shiga", None, None, None),
    "26" : ("Wakayama", None, None, None),
    "35" : ("Hiroshima", None, None, None),
    "31" : ("Okayama", None, None, None),
    "32" : ("Shimane", None, None, None),
    "34" : ("Tottori", None, None, None),
    "33" : ("Yamaguchi", None, None, None),
    "38" : ("Ehime", None, None, None),
    "36" : ("Kagawa", None, None, None),
    "39" : ("Kochi", None, None, None),
    "37" : ("Tokushima", None, None, None),
    "40" : ("Fukuoka", None, None, None),
    "46" : ("Kagoshima", None, None, None),
    "43" : ("Kumamoto", None, None, None),
    "45" : ("Miyazaki", None, None, None),
    "42" : ("Nagasaki", None, None, None),
    "44" : ("Oita", None, None, None),
    "47" : ("Okinawa", None, None, None),
    "41" : ("Saga", None, None, None),
    "04" : ("Akita", None, None, None),
    "02" : ("Aomori", None, None, None),
    "07" : ("Fukushima", None, None, None),
    "03" : ("Iwate", None, None, None),
    "06" : ("Miyagi", None, None, None),
    "05" : ("Yamagata", None, None, None),
    "01" : ("Hokkaido", None, None, None),
    "29" : ("Fukui", None, None, None),
    "30" : ("Ishikawa", None, None, None),
    "28" : ("Toyama", None, None, None),
    "09" : ("Nagano", None, None, None),
    "08" : ("Niigata", None, None, None)
    }

Primary_Administrative_Subdivision_Enumeration_375 = {
    "AUR" : ("Aurora", None, None, None),
    "BTG" : ("Batangas", None, None, None),
    "CAV" : ("Cavite", None, None, None),
    "LAG" : ("Laguna", None, None, None),
    "MAD" : ("Marinduque", None, None, None),
    "MDC" : ("Mindoro Occidental", None, None, None),
    "MDR" : ("Mindoro Oriental", None, None, None),
    "PLW" : ("Palawan", None, None, None),
    "QUE" : ("Quezon", None, None, None),
    "RIZ" : ("Rizal", None, None, None),
    "ROM" : ("Romblon", None, None, None),
    "ILN" : ("Ilocos Norte", None, None, None),
    "ILS" : ("Ilocos Sur", None, None, None),
    "LUN" : ("La Union", None, None, None),
    "PAN" : ("Pangasinan", None, None, None),
    "BTN" : ("Batanes", None, None, None),
    "CAG" : ("Cagayan", None, None, None),
    "ISA" : ("Isabela", None, None, None),
    "NUV" : ("Nueva Vizcaya", None, None, None),
    "QUI" : ("Quirino", None, None, None),
    "ABR" : ("Abra", None, None, None),
    "APA" : ("Apayao", None, None, None),
    "BEN" : ("Benguet", None, None, None),
    "IFU" : ("Ifugao", None, None, None),
    "KAL" : ("Kalinga-Apayso", None, None, None),
    "MOU" : ("Mountain Province", None, None, None),
    "BAN" : ("Batasn", None, None, None),
    "BUL" : ("Bulacan", None, None, None),
    "NUE" : ("Nueva Ecija", None, None, None),
    "PAM" : ("Pampanga", None, None, None),
    "TAR" : ("Tarlac", None, None, None),
    "ZMB" : ("Zambales", None, None, None),
    "ALB" : ("Albay", None, None, None),
    "CAN" : ("Camarines Norte", None, None, None),
    "CAS" : ("Camarines Sur", None, None, None),
    "CAT" : ("Catanduanes", None, None, None),
    "MAS" : ("Masbate", None, None, None),
    "SOR" : ("Sorsogon", None, None, None),
    "BIL" : ("Biliran", None, None, None),
    "EAS" : ("Eastern Samar", None, None, None),
    "LEY" : ("Leyte", None, None, None),
    "NSA" : ("Northern Samar", None, None, None),
    "SLE" : ("Southern Leyte", None, None, None),
    "WSA" : ("Western Samar", None, None, None),
    "AKL" : ("Aklan", None, None, None),
    "ANT" : ("Antique", None, None, None),
    "CAP" : ("Capiz", None, None, None),
    "GUI" : ("Guimaras", None, None, None),
    "ILI" : ("Iloilo", None, None, None),
    "NEC" : ("Negroe Occidental", None, None, None),
    "BOH" : ("Bohol", None, None, None),
    "CEB" : ("Cebu", None, None, None),
    "NER" : ("Negros Oriental", None, None, None),
    "SIG" : ("Siquijor", None, None, None),
    "ZAN" : ("Zamboanga del Norte", None, None, None),
    "ZAS" : ("Zamboanga del Sur", None, None, None),
    "ZSI" : ("Zamboanga Sibugay", None, None, None),
    "NCO" : ("North Cotabato", None, None, None),
    "SUK" : ("Sultan Kudarat", None, None, None),
    "SAR" : ("Sarangani", None, None, None),
    "SCO" : ("South Cotabato", None, None, None),
    "BAS" : ("Basilan", None, None, None),
    "LAS" : ("Lanao del Sur", None, None, None),
    "MAG" : ("Maguindanao", None, None, None),
    "SLU" : ("Sulu", None, None, None),
    "TAW" : ("Tawi-Tawi", None, None, None),
    "LAN" : ("Lanao del Norte", None, None, None),
    "BUK" : ("Bukidnon", None, None, None),
    "CAM" : ("Camiguin", None, None, None),
    "MSC" : ("Misamis Occidental", None, None, None),
    "MSR" : ("Misamis Oriental", None, None, None),
    "COM" : ("Compostela Valley", None, None, None),
    "DAV" : ("Davao del Norte", None, None, None),
    "DAS" : ("Davao del Sur", None, None, None),
    "DAO" : ("Davao Oriental", None, None, None),
    "AGN" : ("Agusan del Norte", None, None, None),
    "AGS" : ("Agusan del Sur", None, None, None),
    "SUN" : ("Surigao del Norte", None, None, None),
    "SUR" : ("Surigao del Sur", None, None, None)
    }

Primary_Administrative_Subdivision_Enumeration_497 = {
    "01" : ("Zagrebačka županija", None, None, None),
    "02" : ("Krapinsko-Zagorska županija", None, None, None),
    "03" : ("Sisačko-Moslavačka županija", None, None, None),
    "04" : ("Karlovačka županija", None, None, None),
    "05" : ("Varaždinska županija", None, None, None),
    "06" : ("Koprivničko-Križevačka županija", None, None, None),
    "07" : ("Bjelovarsko-Bilogorska županija", None, None, None),
    "08" : ("Primorsko-Goranska županija", None, None, None),
    "09" : ("Ličko-Senjska županija", None, None, None),
    "10" : ("Virovitičko-Podravska županija", None, None, None),
    "11" : ("Požeško-Slavonska županija", None, None, None),
    "12" : ("Brodsko-Posavska županija", None, None, None),
    "13" : ("Zadarska županija", None, None, None),
    "14" : ("Osječko-Baranjska županija", None, None, None),
    "15" : ("Šibensko-Kninska županija", None, None, None),
    "16" : ("Vukovarsko-Srijemska županija", None, None, None),
    "17" : ("Splitsko-Dalmatinska županija", None, None, None),
    "18" : ("Istarska županija", None, None, None),
    "19" : ("Dubrovačko-Neretvanska županija", None, None, None),
    "20" : ("Međimurska županija", None, None, None),
    "21" : ("Grad Zagreb", None, None, None)
    }

Primary_Administrative_Subdivision_Enumeration_503 = {
    "APA" : ("Praha 1", None, None, None),
    "APB" : ("Praha 2", None, None, None),
    "APC" : ("Praha 3", None, None, None),
    "APD" : ("Praha 4", None, None, None),
    "APE" : ("Praha 5", None, None, None),
    "APF" : ("Praha 6", None, None, None),
    "APG" : ("Praha 7", None, None, None),
    "APH" : ("Praha 8", None, None, None),
    "API" : ("Praha 9", None, None, None),
    "APJ" : ("Praha 10", None, None, None),
    "BBN" : ("Benesov", None, None, None),
    "BBE" : ("Beroun", None, None, None),
    "BKD" : ("Kladno", None, None, None),
    "BKO" : ("Kolin", None, None, None),
    "BKH" : ("Kutna Hora", None, None, None),
    "BME" : ("Melnik", None, None, None),
    "BMB" : ("Mlada Boleslav", None, None, None),
    "BNY" : ("Nymburk", None, None, None),
    "BPZ" : ("Praha zapad", None, None, None),
    "BPV" : ("Praha vychod", None, None, None),
    "BPB" : ("Pribram", None, None, None),
    "BRA" : ("Rakovnik", None, None, None),
    "CBU" : ("Ceske Budejovice", None, None, None),
    "CCK" : ("Cesky Krumlov", None, None, None),
    "CJH" : ("Jindrichuv Hradec", None, None, None),
    "CPE" : ("Pelhrimov", None, None, None),
    "CPI" : ("Pisek", None, None, None),
    "CPR" : ("Prachatice", None, None, None),
    "CST" : ("Strakonice", None, None, None),
    "CTA" : ("Tabor", None, None, None),
    "DDO" : ("Domazlice", None, None, None),
    "DCH" : ("Cheb", None, None, None),
    "DKV" : ("Karlovy Vary", None, None, None),
    "DKL" : ("Klatovy", None, None, None),
    "DPM" : ("Plzen mesto", None, None, None),
    "DPJ" : ("Plzen jih", None, None, None),
    "DPS" : ("Plzen sever", None, None, None),
    "DRO" : ("Rokycany", None, None, None),
    "DSO" : ("Sokolov", None, None, None),
    "DTA" : ("Tachov", None, None, None),
    "ECL" : ("Ceska Lipa", None, None, None),
    "EDE" : ("Decin", None, None, None),
    "ECH" : ("Chomutov", None, None, None),
    "EJA" : ("Jablonec n. Nisou", None, None, None),
    "ELI" : ("Liberec", None, None, None),
    "ELT" : ("Litomerice", None, None, None),
    "ELO" : ("Louny", None, None, None),
    "EMO" : ("Most", None, None, None),
    "ETE" : ("Teplice", None, None, None),
    "EUL" : ("Usti nad Labem", None, None, None),
    "FHB" : ("Havlickuv Brod", None, None, None),
    "FHK" : ("Hradec Kralove", None, None, None),
    "FCR" : ("Chrudim", None, None, None),
    "FJI" : ("Jicin", None, None, None),
    "FNA" : ("Nachod", None, None, None),
    "FPA" : ("Pardubice", None, None, None),
    "FRK" : ("Rychn n. Kneznou", None, None, None),
    "FSE" : ("Semily", None, None, None),
    "FSV" : ("Svitavy", None, None, None),
    "FTR" : ("Trutnov", None, None, None),
    "FUO" : ("Usti nad Orlici", None, None, None),
    "GBL" : ("Blansko", None, None, None),
    "GBM" : ("Brno mesto", None, None, None),
    "GBV" : ("Brno venkov", None, None, None),
    "GBR" : ("Breclav", None, None, None),
    "GHO" : ("Hodonin", None, None, None),
    "GJI" : ("Jihlava", None, None, None),
    "GKR" : ("Kromeriz", None, None, None),
    "GPR" : ("Prostejov", None, None, None),
    "GTR" : ("Trebic", None, None, None),
    "GUH" : ("Uherske Hradiste", None, None, None),
    "GVY" : ("Vyskov", None, None, None),
    "GZL" : ("Zlin", None, None, None),
    "GZN" : ("Znojmo", None, None, None),
    "GZS" : ("Zdar nad Sazavou", None, None, None),
    "HBR" : ("Bruntal", None, None, None),
    "HFM" : ("Frydek-Mistek", None, None, None),
    "HJE" : ("Jesenik", None, None, None),
    "HKA" : ("Karvina", None, None, None),
    "HNJ" : ("Novy Jicin", None, None, None),
    "HOL" : ("Olomouc", None, None, None),
    "HOP" : ("Opava", None, None, None),
    "HOS" : ("Ostrava", None, None, None),
    "HPR" : ("Prerov", None, None, None),
    "HSU" : ("Sumperk", None, None, None),
    "HVS" : ("Vsetin", None, None, None)
    }

Primary_Administrative_Subdivision_Enumeration_504 = {
    "BAA" : ("Bratislava 1", None, None, None),
    "BAB" : ("Bratislava 2", None, None, None),
    "BAC" : ("Bratislava 3", None, None, None),
    "BAD" : ("Bratislava 4", None, None, None),
    "BAE" : ("Bratislava 5", None, None, None),
    "MAL" : ("Malacky", None, None, None),
    "PEZ" : ("Pezinok", None, None, None),
    "SEN" : ("Senec", None, None, None),
    "DST" : ("Dunajska Streda", None, None, None),
    "GAL" : ("Galanta", None, None, None),
    "HLO" : ("Hlohovec", None, None, None),
    "PIE" : ("Piestany", None, None, None),
    "SEA" : ("Senica", None, None, None),
    "SKA" : ("Skalica", None, None, None),
    "TRN" : ("Trnava", None, None, None),
    "BAN" : ("Banovce n. Bebr.", None, None, None),
    "ILA" : ("Ilava", None, None, None),
    "MYJ" : ("Myjava", None, None, None),
    "NMV" : ("Nove Mesto n. Vah", None, None, None),
    "PAR" : ("Partizanske", None, None, None),
    "PBY" : ("Povazska Bystrica", None, None, None),
    "PRI" : ("Prievidza", None, None, None),
    "PUC" : ("Puchov", None, None, None),
    "TNC" : ("Trencin", None, None, None),
    "KOM" : ("Komarno", None, None, None),
    "LVC" : ("Levice", None, None, None),
    "NIT" : ("Nitra", None, None, None),
    "NZA" : ("Nove Zamky", None, None, None),
    "SAL" : ("Sala", None, None, None),
    "TOP" : ("Topolcany", None, None, None),
    "ZMO" : ("Zlate Moravce", None, None, None),
    "BYT" : ("Bytca", None, None, None),
    "CAD" : ("Cadca", None, None, None),
    "DKU" : ("Dolny Kubin", None, None, None),
    "KNM" : ("Kysucke N. Mesto", None, None, None),
    "LMI" : ("Liptovsky Mikulas", None, None, None),
    "MAR" : ("Martin", None, None, None),
    "NAM" : ("Namestovo", None, None, None),
    "RUZ" : ("Ruzomberok", None, None, None),
    "TTE" : ("Turcianske Teplice", None, None, None),
    "TVR" : ("Tvrdosin", None, None, None),
    "ZIL" : ("Zilina", None, None, None),
    "BBY" : ("Banska Bystrica", None, None, None),
    "BST" : ("Banska Stiavnica", None, None, None),
    "BRE" : ("Brezno", None, None, None),
    "DET" : ("Detva", None, None, None),
    "KRU" : ("Krupina", None, None, None),
    "LUC" : ("Lucenec", None, None, None),
    "POL" : ("Poltar", None, None, None),
    "REV" : ("Revuca", None, None, None),
    "RSO" : ("Rimavska Sobota", None, None, None),
    "VKR" : ("Velky Krtis", None, None, None),
    "ZAR" : ("Zarnovica", None, None, None),
    "ZIH" : ("Ziar nad Hronom", None, None, None),
    "ZVO" : ("Zvolen", None, None, None),
    "GEL" : ("Gelnica", None, None, None),
    "KEA" : ("Kosice 1", None, None, None),
    "KEB" : ("Kosice 2", None, None, None),
    "KEC" : ("Kosice 3", None, None, None),
    "KED" : ("Kosice 4", None, None, None),
    "KEO" : ("Kosice-okolie", None, None, None),
    "MIC" : ("Michalovce", None, None, None),
    "ROZ" : ("Roznava", None, None, None),
    "SOB" : ("Sobrance", None, None, None),
    "SNV" : ("Spisska Nova Ves", None, None, None),
    "TRE" : ("Trebisov", None, None, None),
    "BAR" : ("Bardejov", None, None, None),
    "HUM" : ("Humenne", None, None, None),
    "KEZ" : ("Kezmarok", None, None, None),
    "LEV" : ("Levoca", None, None, None),
    "MED" : ("Medzilaborce", None, None, None),
    "POP" : ("Poprad", None, None, None),
    "PRE" : ("Presov", None, None, None),
    "SAB" : ("Sabinov", None, None, None),
    "SNI" : ("Snina", None, None, None),
    "SLU" : ("Stara Lubovna", None, None, None),
    "STR" : ("Stropkov", None, None, None),
    "SVI" : ("Svidnik", None, None, None),
    "VRT" : ("Vranov nad Toplou", None, None, None)
    }

DXCC_Entity_Code_Enumeration = {
    "0" : "None (the contacted station is known to not be within a DXCC entity)",
    "1" : "CANADA",
    "3" : "AFGHANISTAN",
    "4" : "AGALEGA & ST. BRANDON IS.",
    "5" : "ALAND IS.",
    "6" : "ALASKA",
    "7" : "ALBANIA",
    "9" : "AMERICAN SAMOA",
    "10" : "AMSTERDAM & ST. PAUL IS.",
    "11" : "ANDAMAN & NICOBAR IS.",
    "12" : "ANGUILLA",
    "13" : "ANTARCTICA",
    "14" : "ARMENIA",
    "15" : "ASIATIC RUSSIA",
    "16" : "NEW ZEALAND SUBANTARCTIC ISLANDS",
    "17" : "AVES I.",
    "18" : "AZERBAIJAN",
    "20" : "BAKER & HOWLAND IS.",
    "21" : "BALEARIC IS.",
    "22" : "PALAU",
    "24" : "BOUVET",
    "27" : "BELARUS",
    "29" : "CANARY IS.",
    "31" : "C. KIRIBATI (BRITISH PHOENIX IS.)",
    "32" : "CEUTA & MELILLA",
    "33" : "CHAGOS IS.",
    "34" : "CHATHAM IS.",
    "35" : "CHRISTMAS I.",
    "36" : "CLIPPERTON I.",
    "37" : "COCOS I.",
    "38" : "COCOS (KEELING) IS.",
    "40" : "CRETE",
    "41" : "CROZET I.",
    "43" : "DESECHEO I.",
    "45" : "DODECANESE",
    "46" : "EAST MALAYSIA",
    "47" : "EASTER I.",
    "48" : "E. KIRIBATI (LINE IS.)",
    "49" : "EQUATORIAL GUINEA",
    "50" : "MEXICO",
    "51" : "ERITREA",
    "52" : "ESTONIA",
    "53" : "ETHIOPIA",
    "54" : "EUROPEAN RUSSIA",
    "56" : "FERNANDO DE NORONHA",
    "60" : "BAHAMAS",
    "61" : "FRANZ JOSEF LAND",
    "62" : "BARBADOS",
    "63" : "FRENCH GUIANA",
    "64" : "BERMUDA",
    "65" : "BRITISH VIRGIN IS.",
    "66" : "BELIZE",
    "69" : "CAYMAN IS.",
    "70" : "CUBA",
    "71" : "GALAPAGOS IS.",
    "72" : "DOMINICAN REPUBLIC",
    "74" : "EL SALVADOR",
    "75" : "GEORGIA",
    "76" : "GUATEMALA",
    "77" : "GRENADA",
    "78" : "HAITI",
    "79" : "GUADELOUPE",
    "80" : "HONDURAS",
    "82" : "JAMAICA",
    "84" : "MARTINIQUE",
    "86" : "NICARAGUA",
    "88" : "PANAMA",
    "89" : "TURKS & CAICOS IS.",
    "90" : "TRINIDAD & TOBAGO",
    "91" : "ARUBA",
    "94" : "ANTIGUA & BARBUDA",
    "95" : "DOMINICA",
    "96" : "MONTSERRAT",
    "97" : "ST. LUCIA",
    "98" : "ST. VINCENT",
    "99" : "GLORIOSO IS.",
    "100" : "ARGENTINA",
    "103" : "GUAM",
    "104" : "BOLIVIA",
    "105" : "GUANTANAMO BAY",
    "106" : "GUERNSEY",
    "107" : "GUINEA",
    "108" : "BRAZIL",
    "109" : "GUINEA-BISSAU",
    "110" : "HAWAII",
    "111" : "HEARD I.",
    "112" : "CHILE",
    "114" : "ISLE OF MAN",
    "116" : "COLOMBIA",
    "117" : "ITU HQ",
    "118" : "JAN MAYEN",
    "120" : "ECUADOR",
    "122" : "JERSEY",
    "123" : "JOHNSTON I.",
    "124" : "JUAN DE NOVA, EUROPA",
    "125" : "JUAN FERNANDEZ IS.",
    "126" : "KALININGRAD",
    "129" : "GUYANA",
    "130" : "KAZAKHSTAN",
    "131" : "KERGUELEN IS.",
    "132" : "PARAGUAY",
    "133" : "KERMADEC IS.",
    "135" : "KYRGYZSTAN",
    "136" : "PERU",
    "137" : "REPUBLIC OF KOREA",
    "138" : "KURE I.",
    "140" : "SURINAME",
    "141" : "FALKLAND IS.",
    "142" : "LAKSHADWEEP IS.",
    "143" : "LAOS",
    "144" : "URUGUAY",
    "145" : "LATVIA",
    "146" : "LITHUANIA",
    "147" : "LORD HOWE I.",
    "148" : "VENEZUELA",
    "149" : "AZORES",
    "150" : "AUSTRALIA",
    "152" : "MACAO",
    "153" : "MACQUARIE I.",
    "157" : "NAURU",
    "158" : "VANUATU",
    "159" : "MALDIVES",
    "160" : "TONGA",
    "161" : "MALPELO I.",
    "162" : "NEW CALEDONIA",
    "163" : "PAPUA NEW GUINEA",
    "165" : "MAURITIUS",
    "166" : "MARIANA IS.",
    "167" : "MARKET REEF",
    "168" : "MARSHALL IS.",
    "169" : "MAYOTTE",
    "170" : "NEW ZEALAND",
    "171" : "MELLISH REEF",
    "172" : "PITCAIRN I.",
    "173" : "MICRONESIA",
    "174" : "MIDWAY I.",
    "175" : "FRENCH POLYNESIA",
    "176" : "FIJI",
    "177" : "MINAMI TORISHIMA",
    "179" : "MOLDOVA",
    "180" : "MOUNT ATHOS",
    "181" : "MOZAMBIQUE",
    "182" : "NAVASSA I.",
    "185" : "SOLOMON IS.",
    "187" : "NIGER",
    "188" : "NIUE",
    "189" : "NORFOLK I.",
    "190" : "SAMOA",
    "191" : "NORTH COOK IS.",
    "192" : "OGASAWARA",
    "195" : "ANNOBON I.",
    "197" : "PALMYRA & JARVIS IS.",
    "199" : "PETER 1 I.",
    "201" : "PRINCE EDWARD & MARION IS.",
    "202" : "PUERTO RICO",
    "203" : "ANDORRA",
    "204" : "REVILLAGIGEDO",
    "205" : "ASCENSION I.",
    "206" : "AUSTRIA",
    "207" : "RODRIGUEZ I.",
    "209" : "BELGIUM",
    "211" : "SABLE I.",
    "212" : "BULGARIA",
    "213" : "SAINT MARTIN",
    "214" : "CORSICA",
    "215" : "CYPRUS",
    "216" : "SAN ANDRES & PROVIDENCIA",
    "217" : "SAN FELIX & SAN AMBROSIO",
    "219" : "SAO TOME & PRINCIPE",
    "221" : "DENMARK",
    "222" : "FAROE IS.",
    "223" : "ENGLAND",
    "224" : "FINLAND",
    "225" : "SARDINIA",
    "227" : "FRANCE",
    "230" : "FEDERAL REPUBLIC OF GERMANY",
    "232" : "SOMALIA",
    "233" : "GIBRALTAR",
    "234" : "SOUTH COOK IS.",
    "235" : "SOUTH GEORGIA I.",
    "236" : "GREECE",
    "237" : "GREENLAND",
    "238" : "SOUTH ORKNEY IS.",
    "239" : "HUNGARY",
    "240" : "SOUTH SANDWICH IS.",
    "241" : "SOUTH SHETLAND IS.",
    "242" : "ICELAND",
    "245" : "IRELAND",
    "246" : "SOVEREIGN MILITARY ORDER OF MALTA",
    "247" : "SPRATLY IS.",
    "248" : "ITALY",
    "249" : "ST. KITTS & NEVIS",
    "250" : "ST. HELENA",
    "251" : "LIECHTENSTEIN",
    "252" : "ST. PAUL I.",
    "253" : "ST. PETER & ST. PAUL ROCKS",
    "254" : "LUXEMBOURG",
    "256" : "MADEIRA IS.",
    "257" : "MALTA",
    "259" : "SVALBARD",
    "260" : "MONACO",
    "262" : "TAJIKISTAN",
    "263" : "NETHERLANDS",
    "265" : "NORTHERN IRELAND",
    "266" : "NORWAY",
    "269" : "POLAND",
    "270" : "TOKELAU IS.",
    "272" : "PORTUGAL",
    "273" : "TRINDADE & MARTIM VAZ IS.",
    "274" : "TRISTAN DA CUNHA & GOUGH I.",
    "275" : "ROMANIA",
    "276" : "TROMELIN I.",
    "277" : "ST. PIERRE & MIQUELON",
    "278" : "SAN MARINO",
    "279" : "SCOTLAND",
    "280" : "TURKMENISTAN",
    "281" : "SPAIN",
    "282" : "TUVALU",
    "283" : "UK SOVEREIGN BASE AREAS ON CYPRUS",
    "284" : "SWEDEN",
    "285" : "VIRGIN IS.",
    "286" : "UGANDA",
    "287" : "SWITZERLAND",
    "288" : "UKRAINE",
    "289" : "UNITED NATIONS HQ",
    "291" : "UNITED STATES OF AMERICA",
    "292" : "UZBEKISTAN",
    "293" : "VIET NAM",
    "294" : "WALES",
    "295" : "VATICAN",
    "296" : "SERBIA",
    "297" : "WAKE I.",
    "298" : "WALLIS & FUTUNA IS.",
    "299" : "WEST MALAYSIA",
    "301" : "W. KIRIBATI (GILBERT IS. )",
    "302" : "WESTERN SAHARA",
    "303" : "WILLIS I.",
    "304" : "BAHRAIN",
    "305" : "BANGLADESH",
    "306" : "BHUTAN",
    "308" : "COSTA RICA",
    "309" : "MYANMAR",
    "312" : "CAMBODIA",
    "315" : "SRI LANKA",
    "318" : "CHINA",
    "321" : "HONG KONG",
    "324" : "INDIA",
    "327" : "INDONESIA",
    "330" : "IRAN",
    "333" : "IRAQ",
    "336" : "ISRAEL",
    "339" : "JAPAN",
    "342" : "JORDAN",
    "344" : "DEMOCRATIC PEOPLE'S REP. OF KOREA",
    "345" : "BRUNEI DARUSSALAM",
    "348" : "KUWAIT",
    "354" : "LEBANON",
    "363" : "MONGOLIA",
    "369" : "NEPAL",
    "370" : "OMAN",
    "372" : "PAKISTAN",
    "375" : "PHILIPPINES",
    "376" : "QATAR",
    "378" : "SAUDI ARABIA",
    "379" : "SEYCHELLES",
    "381" : "SINGAPORE",
    "382" : "DJIBOUTI",
    "384" : "SYRIA",
    "386" : "TAIWAN",
    "387" : "THAILAND",
    "390" : "TURKEY",
    "391" : "UNITED ARAB EMIRATES",
    "400" : "ALGERIA",
    "401" : "ANGOLA",
    "402" : "BOTSWANA",
    "404" : "BURUNDI",
    "406" : "CAMEROON",
    "408" : "CENTRAL AFRICA",
    "409" : "CAPE VERDE",
    "410" : "CHAD",
    "411" : "COMOROS",
    "412" : "REPUBLIC OF THE CONGO",
    "414" : "DEMOCRATIC REPUBLIC OF THE CONGO",
    "416" : "BENIN",
    "420" : "GABON",
    "422" : "THE GAMBIA",
    "424" : "GHANA",
    "428" : "COTE D'IVOIRE",
    "430" : "KENYA",
    "432" : "LESOTHO",
    "434" : "LIBERIA",
    "436" : "LIBYA",
    "438" : "MADAGASCAR",
    "440" : "MALAWI",
    "442" : "MALI",
    "444" : "MAURITANIA",
    "446" : "MOROCCO",
    "450" : "NIGERIA",
    "452" : "ZIMBABWE",
    "453" : "REUNION I.",
    "454" : "RWANDA",
    "456" : "SENEGAL",
    "458" : "SIERRA LEONE",
    "460" : "ROTUMA I.",
    "462" : "SOUTH AFRICA",
    "464" : "NAMIBIA",
    "466" : "SUDAN",
    "468" : "SWAZILAND",
    "470" : "TANZANIA",
    "474" : "TUNISIA",
    "478" : "EGYPT",
    "480" : "BURKINA FASO",
    "482" : "ZAMBIA",
    "483" : "TOGO",
    "489" : "CONWAY REEF",
    "490" : "BANABA I. (OCEAN I.)",
    "492" : "YEMEN",
    "497" : "CROATIA",
    "499" : "SLOVENIA",
    "501" : "BOSNIA-HERZEGOVINA",
    "502" : "MACEDONIA",
    "503" : "CZECH REPUBLIC",
    "504" : "SLOVAK REPUBLIC",
    "505" : "PRATAS I.",
    "506" : "SCARBOROUGH REEF",
    "507" : "TEMOTU PROVINCE",
    "508" : "AUSTRAL I.",
    "509" : "MARQUESAS IS.",
    "510" : "PALESTINE",
    "511" : "TIMOR-LESTE",
    "512" : "CHESTERFIELD IS.",
    "513" : "DUCIE I.",
    "514" : "MONTENEGRO",
    "515" : "SWAINS I.",
    "516" : "SAINT BARTHELEMY",
    "517" : "CURACAO",
    "518" : "ST MAARTEN",
    "519" : "SABA & ST. EUSTATIUS",
    "520" : "BONAIRE",
    "521" : "SOUTH SUDAN (REPUBLIC OF)",
    "522" : "REPUBLIC OF KOSOVO",
    }

#
#Rather than maintaining a table of DXCC_Entity_Code_Enumeration to
#Primary_Administrative_Subdivision_Enumeration_NNN links, allow the
#Primary_Administrative_Subdivision_Enumeration tables to be added to
#the DXCC_Entity_Code_Enumeration table on-the-fly by merely defining a
#Primary_Administrative_Subdivision_Enumeration_NNN table.
#
#This code will change the couuntry number to country name dictonary
#mapping to a (country name, None) tuple - if no further information on
#a country, or a (country name,
#Primary_Administrative_Subdivision_Enumeration_NNN) tuple if there is
#subdivision information on the country.
#
for i in DXCC_Entity_Code_Enumeration.keys():
    #
    #Figure out the name of the table (text) for that country
    #
    Primary_Administrative_Subdivision_Enumeration_number = (
        "Primary_Administrative_Subdivision_Enumeration_" +  str(i))

    #
    #If the subdivision table exists, create a country name and a
    #DXCC_Entity_Code_Enumeration tuple. If not, create a country name
    #and a None tuple.
    #
    if Primary_Administrative_Subdivision_Enumeration_number in locals():
        DXCC_Entity_Code_Enumeration[i] = (
            DXCC_Entity_Code_Enumeration[i],
            eval(Primary_Administrative_Subdivision_Enumeration_number)
            )
    else:
        DXCC_Entity_Code_Enumeration[i] = (
            DXCC_Entity_Code_Enumeration[i], None)

QSL_Medium_Enumeration = {
    "CARD" : "QSO confirmation via paper QSL card",
    "EQSL" : "QSO confirmation via eQSL.cc",
    "LOTW" : "QSO confirmation via ARRL Logbook of the World"
}

QSL_Rcvd_Enumeration = {
    "Y" : "yes (confirmed)",
    "N" : "no",
    "R" : "requested",
    "I" : "ignore or invalid",
    "V" : "verified"
}

QSL_Sent_Enumeration = {
    "Y" : "yes",
    "N" : "no",
    "R" : "requested",
    "Q" : "queued",
    "I" : "ignore or invalid"
}

QSL_Via_Enumeration = {
    "B" : "bureau",
    "D" : "direct",
    "E" : "electronic",
    "M" : "manager"
}

QSO_Complete_Enumeration = {
    "Y" : "yes",
    "N" : "no",
    "NIL" : "not heard",
    "?" : "uncertain"
}

QSO_Upload_Status_Enumeration = {
    "Y" : "the QSO has been uploaded to, and accepted by, the online service",
    "N" : "do not upload the QSO to the online service",
    "M" : "the QSO has been modified since being uploaded to the online service"
}

Enumeration_for_US_Counties_DXCC_Entity_Code_6 = {
    "AK,Aleutians East" : ("Aleutians East", "Alaska Third Judicial District"),
    "AK,Aleutians West" : ("Aleutians West", "Alaska Third Judicial District"),
    "AK,Anchorage" : ("Anchorage", "Alaska Third Judicial District"),
    "AK,Bethel" : ("Bethel", "Alaska Fourth Judicial District"),
    "AK,Bristol Bay" : ("Bristol Bay", "Alaska Third Judicial District"),
    "AK,Denali" : ("Denali", "Alaska Fourth Judicial District"),
    "AK,Dillingham" : ("Dillingham", "Alaska Third Judicial District"),
    "AK,Fairbanks" : ("Fairbanks", "Alaska Fourth Judicial District"),
    "AK,Fairbanks North Star" : ("Fairbanks North Star", "Alaska Fourth Judicial District"),
    "AK,Haines" : ("Haines", "Alaska First Judicial District"),
    "AK,Juneau" : ("Juneau", "Alaska First Judicial District"),
    "AK,Hoonah-Angoon" : ("Hoonah-Angoon", "Alaska First Judicial District"),
    "AK,Kenai Peninsula" : ("Kenai Peninsula", "Alaska Third Judicial District"),
    "AK,Ketchikan Gateway" : ("Ketchikan Gateway", "Alaska First Judicial District"),
    "AK,Kodiak Island" : ("Kodiak Island", "Alaska Third Judicial District"),
    "AK,Kusilvak" : ("Kusilvak", "Alaska Second Judicial District"),
    "AK,Lake and Peninsula" : ("Lake and Peninsula", "Alaska Third Judicial District"),
    "AK,Matanuska-Susitna" : ("Matanuska-Susitna", "Alaska Third Judicial District"),
    "AK,Nome" : ("Nome", "Alaska Second Judicial District"),
    "AK,North Slope" : ("North Slope", "Alaska Second Judicial District"),
    "AK,Northwest Arctic" : ("Northwest Arctic", "Alaska Second Judicial District"),
    "AK,Petersburg" : ("Petersburg", "Alaska First Judicial District"),
    "AK,Pribilof Islands" : ("Pribilof Islands", "Alaska Third Judicial District"),
    "AK,Prince of Wales-Hyder" : ("Prince of Wales-Hyder", "Alaska First Judicial District"),
    "AK,Saint Matthew Island" : ("Saint Matthew Island", "Alaska Fourth Judicial District"),
    "AK,Sitka" : ("Sitka", "Alaska First Judicial District"),
    "AK,Skagway" : ("Skagway", "Alaska First Judicial District"),
    "AK,Southeast Fairbanks" : ("Southeast Fairbanks", "Alaska Fourth Judicial District"),
    "AK,Valdez-Cordova" : ("Valdez-Cordova", "Alaska Third Judicial District"),
    "AK,Wales-Hyder" : ("Wales-Hyder", "Alaska First Judicial District"),
    "AK,Wrangell" : ("Wrangell", "Alaska First Judicial District"),
    "AK,Yakutat" : ("Yakutat", "Alaska First Judicial District")
}

Region_Enumeration = {
    "NONE" : (None, "Not within a WAE or CQ region that is within a DXCC entity", None, None),
    "IV" : ("206", "ITU Vienna", "4U1V", ("CQ", "WAE",)),
    "AI" : ("248", "African Italy", "IG9", ("WAE",)),
    "SY" : ("248", "Sicily", "IT9", ("CQ", "WAE",)),
    "BI" : ("259", "Bear Island", "JW/B", ("CQ", "WAE",)),
    "SI" : ("279", "Shetland Islands", "GM/S", ("CQ", "WAE",)),
    "KO" : ("296", "Kosovo", "Z6", ("CQ", "WAE",)),
    "ET" : ("390", "European Turkey", "TA1", ("CQ",))
}

Sponsored_Award_Enumeration = {
    "ADIF_" : "ADIF Development Group",
    "ARI_" : "ARI - l'Associazione Radioamatori Italiani",
    "ARRL_" : "ARRL - American Radio Relay League",
    "CQ_" : "CQ Magazine",
    "DARC_" : "DARC - Deutscher Amateur-Radio-Club e.V.",
    "EQSL_" : "eQSL",
    "IARU_" : "IARU - International Amateur Radio Union",
    "JARL_" : "JARL - Japan Amateur Radio League",
    "RSGB_" : "RSGB - Radio Society of Great Britain",
    "TAG_" : "TAG - Tambov award group",
    "WABAG_" : "WAB - Worked all Britain"
}

state_enumeration = {
    "US" : ("AK", "AL", "AR", "AS", "AZ", "CA", "CO", "CT", "DC", "DE",
        "FL", "FM", "GA", "GU", "HI", "IA", "ID", "IL", "IN", "KS",
        "KY", "LA", "MA", "MD", "ME", "MH", "MI", "MN", "MO", "MP",
        "MS", "MT", "NC", "ND", "NE", "NH", "NJ", "NM", "NV", "NY",
        "OH", "OK", "OR", "PA", "PR", "PW", "RI", "SC", "SD", "TN",
        "TX", "UT", "VA", "VI", "VT", "WA", "WI", "WV", "WY")
    }

#re_band = r'\d+\.?\d*[M|CM|MM]'   Get rid of this?
re_frequency = r'(\.\d+)|(\d+\.?\d*)'

def Boolean(test):
    """
    ADIF Boolean field must be a "Y", "N", "y" or "n", error otherwise.

    Arguments:
        test:
            String to test

    Returns:
        Boolean field valid:
            Null string ("")
        Boolean field invalid:
            Error string.
    """

    validate_arg_type((
        (test, str),
    ))

    if rf.fullmatch(r'[YN]', test, flags=re.I):
        return("")

    return("""
    ADIF boolean is "{}", but must be "Y" or "N".
""")

def Digit(test):
    """
    ADIF Digit field must be 0-9, error otherwise.

    Arguments:
        test:
            String to test

    Returns:
        Digit field valid:
            Null string ("")
        Digit field invalid:
            Error string.
    """

    validate_arg_type((
        (test, str),
    ))

    if rf.fullmatch(r'[0-9]', test):
        return("")

    return("""
    ADIF digit "{}" is outside the "0" to "9" (ASCII 48-57) range.
""".format(test))

def Integer(test):
    """
    ADIF Integer field must be a digits with an optional starting "-"
    sign, error otherwise.

    Arguments:
        test:
            String to test

    Returns:
        Integer field valid:
            Null string ("")
        Integer field invalid:
            Error string.
    """

    validate_arg_type((
        (test, str),
    ))

    if rf.fullmatch(r'-?\d+', test):
        return("")

    return("""
    Integer "{}" does not have integer format:
    A sequence of one or more Digits representing a decimal integer,
    optionally preceded by a minus sign.  Leading zeroes are allowed.
""")


def PositiveInteger(test):
    """
    ADIF PositiveInteger field must be a digits with no "-" sign,
    error otherwise. It also must be greater than zero.

    Arguments:
        test:
            String to test

    Returns:
        PositiveInteger field valid:
            Null string ("")
        PositiveInteger field invalid:
            Error string.
    """

    validate_arg_type((
        (test, str),
    ))

    if not rf.fullmatch(r'\d+', test):
        #
        #Incorrect format
        #
        return("""
    Positive integer "{}" does not have integer format:
    An unsigned sequence of one or more Digits representing a decimal
    integer that has a value greater than 0.  Leading zeroes are
    allowed.
""")

    if int(test) < 1:
        #
        #Incorrect format
        #
        return("""
    Positive integer "{}" must be greater than zero.
""")    

    #
    #It's correct
    #
    return("")

def Number(test):
    """
    ADIF Number field must be a digits with an optional decimal point,
    error otherwise.

    Arguments:
        test:
            String to test

    Returns:
        Number field valid:
            Null string ("")
        Number field invalid:
            Error string.
    """

    validate_arg_type((
        (test, str),
    ))

    if rf.fullmatch(r'-?(\.\d+)|(\d+\.?\d*)', test):
        return("")

    return("""
    Number "{}" does not have number format:
    A sequence of one or more Digits representing a decimal number,
    optionally preceded by a minus sign and optionally including a
    single decimal point.
""")

def Character(test):
    """
    ADIF boolean field must be a "Y", "N", "y" or "n", error otherwise.

    Arguments:
        test:
            String of length one to test

    Returns:
        Character field valid:
            Null string ("")
        Character field invalid:
            Error string.
    """

    validate_arg_type((
        (test, str),
    ))

    if rf.fullmatch(r'[\ -~]', test):
        return("")

    return("""
    Character "{}" is outside the " " to "~" (ASCII 36-126) range.
""".format(test))

def String(test):
    """
    ADIF string field may only contain the ascii characters "space"
    through "~", error otherwise.

    Arguments:
        test:
            String to test

    Returns:
        String field valid:
            Null string ("")
        String field invalid:
            Error string.
    """

    validate_arg_type((
        (test, str),
    ))

    if re.fullmatch(r'[\ -~]+', test):
        return("")

    return("""
    String contains a character outside the " " to "~" range
    (ASCII 36-126 decimal).
""")

def TBS(test):
    """
    "To be Supplied"
    For ADIF fields that don't have explicit checking yet, just return
    the null string (Success).

    Arguments:
        test:
            String to test

    Returns:
        Always ""
    """

    validate_arg_type((
        (test, str),
    ))

    #
    #To be supplied checking. Always return the null string (Success)
    #
    return("")

def Region(test):
    """
    ADIF Region field may only contain an explicit list of
    regions. Verify against the list.

    Arguments:
        test:
            String to test

    Returns:
        Region field valid:
            Null string ("")
        Region field invalid:
            Error string.
    """

    validate_arg_type((
        (test, str),
    ))

    if test.upper() in Region_Enumeration:
        return("")

    return("""
    "{}" is not a valid region. Region must be one of:
        "{}"
""".format(test, '"\n        "'.join(Region_Enumeration)))

def AwardList(test):
    """
    ADIF AwardList field may only contain an explicit list of awards.
    Verify against the list.

    Arguments:
        test:
            String to test

    Returns:
        AwardList field valid:
            Null string ("")
        AwardList field invalid:
            Error string.
    """

    validate_arg_type((
        (test, str),
    ))

    errors = ""
    for i in test.split(","):
        if i.upper() not in Award_Enumeration:
            errors += """
    "{}" not a valid award.
""".format(i)

    if errors:
        errors += """
    Awards must be one of:
        "{}"
""".format(test, '"\n        "'.join(sorted(Sponsored_Award_Enumeration)))

    return(errors)

def SponsoredAwardList(test):
    """
    ADIF SponsoredAwardList field may only contain an explicit list of
    awards. Verify against the list.

    Arguments:
        test:
            String to test

    Returns:
        SponsoredAwardList field valid:
            Null string ("")
        SponsoredAwardList field invalid:
            Error string.
    """

    validate_arg_type((
        (test, str),
    ))

    errors = ""
    for i in test.split(","):
        if i.upper() not in Sponsored_Award_Enumeration:
            errors += """
    "{}" not a valid sponsored award.
""".format(i)

    if errors:
        errors += """
    Sponsored awards must be one of:
        "{}"
""".format(test, '"\n        "'.join(sorted(Sponsored_Award_Enumeration)))

    return(errors)

def MultilineString(test):
    """
    ADIF MultilineString field may only contain the ascii characters
    "space" through "~" with "CR-LF" pairs, error otherwise.

    Arguments:
        test:
            String to test

    Returns:
        MultilineString field valid:
            Null string ("")
        MultilineString field invalid:
            Error string.
    """

    validate_arg_type((
        (test, str),
    ))

    errors = ""
    #
    #See if there are any carriage returns without line feeds or
    #vice-versa
    #
    if re.search(onlycr_re, test) or re.search(onlylf_re, test):
        errors = """
    Multiline strings must have carriage return-line feed pairs. Either
    a linefeed without a carriage return or a carriage return without a
    line feed was detected.
"""

    #
    #Now remove all the carriage returns and linefeeds and make sure all
    #the rest of the text is in-range
    #
    return(errors + String(re.sub(cr_or_lf_re, '', test)))

def Date(test):
    """
    ADIF Date field must contain the date in the YYYYMMDD format, error
    otherwise.

    Arguments:
        test:
            String to test

    Returns:
        Date field valid:
            Null string ("")
        Date field invalid:
            Error string.
    """

    validate_arg_type((
        (test, str),
    ))

    errors = ""

    ymd = re.findall(r'^(\d{4})(\d{2})(\d{2})$', test)
    if ymd:
        #
        #Get year, month and day and validate
        #
        (year, month, day) = ymd[0]

        #
        #Make sure month is in range
        #
        if (month < 1) or (month > 12):
            errors += """
    ADIF date's month is zero of greater than 12: "{}"
""".format(month)

        #
        #Make sure day is in range
        #
        max_day = calendar.monthrange(int(year), int(month))
        if (int(day) < 1) or (int(day) > maxday):
            errors += """
    ADIF date's day is zero or greater than the days in the month.
    {}/{} has {} days, {} was specified.
""".format(month, year, max_day, day)

    else:
        errors += """
    ADIF date "{}" not in correct format. Should be "YYYYMMDD"
""".format(test)

    #
    #Return errors or null string
    #
    return(errors)

def Time(test):
    """
    ADIF Time field must contain the date in the HHMM or HHMMSS format,
    error otherwise.

    Arguments:
        test:
            String to test

    Returns:
        Time field valid:
            Null string ("")
        Time field invalid:
            Error string.
    """

    validate_arg_type((
        (test, str),
    ))

    errors = ""

    hms = re.findall(r'(\d{2})(\d{2})(\d\d)?$', test)
    if hms:
        #
        #Get hour, minute and [maybe] seond and validate
        #
        (hour, minute, second) = ymd[0]

        #
        #Make sure hour is in range
        #
        if int(hour) > 23:
            errors += """
    ADIF time's hour is greater than 23: "{}"
""".format(hour)

        #
        #Make sure minute is in range
        #
        if int(minute) > 59:
            errors += """
    ADIF time's minutes is greater than 59: "{}"
""".format(minute)

        #
        #If seconds were specified (optional) make sure they're 59 or
        #less.
        #
        if second and (int(second) > 59):
            errors += """
    ADIF time's seconds is greater than 59: "{}"
""".format(second)

    else:
        errors += """
    ADIF time "{}" not in correct format. Should be "HHMM" or
    "HHMMSS"
""".format(test)

    #
    #Retrun errors or null string.
    #
    return(errors)

def Ant_Path(test):
    """
    ADIF Ant_Path field may only contain only one of an explicit list of
    paths. Verify against the list.

    Arguments:
        test:
            String to test

    Returns:
        Ant_Path field valid:
            Null string ("")
        Ant_Path field invalid:
            Error string.
    """

    validate_arg_type((
        (test, str),
    ))

    if test.upper() in Ant_Path_Enumeration:
        return("")

    return("""
    "{}" not a valid antenna path, must be one of:
        "{}"
""".format(test, '"\n        "'.join(sorted(Ant_Path_Enumeration.keys()))))

def Location(test):
    """
    ADIF Location field must contain a location format in the form of
    XDDD MM.MMM where X is one of "NSEW" and the rest is degrees,
    minutes and decimal minutes. Degrees must be 0 - 180.

    Arguments:
        test:
            String to test

    Returns:
        Location field valid:
            Null string ("")
        Location field invalid:
            Error string.
    """

    validate_arg_type((
        (test, str),
    ))

    loc = re.findall(r'^([NSEW])(\d{3}) (\d{2})\.(\d{3})$', test)
    if not loc:
        return("""
    "{}" does not have correct location format: XDDD MM.MMM
    where X is "N","S", "E" or "W" and DDD is 000-180 with leading
    zeroes, one space, then MM.MMM is 00.000-59.999 with leading and
    trailing zeroes.
""".format(test))

    #
    #Check ranges
    #
    (cardinal, degrees, minutes, decimal_minutes) = loc

    errors = ""

    if int(degrees) > 180:
        errors += """
    "{}" degrees in "{}" (DDD in XDDD MM.MMM), is greater than 180
""".format(degrees, test)

    if int(minutes) > 59:
        errors += """
    "{}" minutes in "{}" (MM in XDDD MM.MMM), is greater than 59
""".format(minutes, test)

    #
    #Instead of converting to float with possible rounding errors, if
    #degrees is exactly 180, make sure minutes and decimal minutes are
    #both zero.
    #
    if (degrees == "180") and bool(int(minutes + decimal_minutes)):
        errors += """
    "{}.{}" minutes in "{}" (MM.MMM in XDDD MM.MMM),
    are non-zero, but the degrees is 180, making it greater than 180,
    which is not allowed.
""".format(minutes, decimal_minutes, test)

    return(errors)

def Longitude(test):
    """
    Longitude is not specified in the ADIF spec, but this is just a
    tighter check to assure that a valid longitude is specified in the
    form of XDDD MM.MMM where X is one of "EW" and the rest is degrees,
    minutes and decimal minutes. Degrees must be 000 - 180.

    Arguments:
        test:
            String to test

    Returns:
        Longitude field valid:
            Null string ("")
        Longitude field invalid:
            Error string.
    """

    validate_arg_type((
        (test, str),
    ))

    errors = Location(test)
    if errors:
        return(errors)
    
    if not re.match(r'[EW]', test):
        return("""
    For longitude, "{}" must start with "E" or "W".
""".format(test))

    return("")

def Latitude(test):
    """
    Latitude is not specified in the ADIF spec, but this is just a
    tighter check to assure that a valid latitude is specified in the
    form of XDDD MM.MMM where X is one of "NS" and the rest is degrees,
    minutes and decimal minutes. Degrees must be 000 - 090.

    Arguments:
        test:
            String to test

    Returns:
        Latitude field valid:
            Null string ("")
        Latitude field invalid:
            Error string.
    """

    validate_arg_type((
        (test, str),
    ))

    errors = Location(test)
    if errors:
        return(errors)

    if not re.match(r'[NS]', test):
        return("""
    For latitude, "{}" must start with "N" or "S".
""".format(test))

    #
    #This will match because we already used this RE for the Location
    #check, and that passed if we're here.
    #
    (cardinal, degrees, minutes, decimal_minutes) = \
        re.findall(r'^([NSEW])(\d{3}) (\d{2})\.(\d{3})$', test)

    #
    #Instead of converting to float with possible rounding errors, if
    #degrees is exactly 090, make sure minutes and decimal minutes are
    #both zero.
    #
    if (degrees == "090") and bool(int(minutes + decimal_minutes)):
        return("""
    "{}.{}" minutes in "{}" (MM.MMM in XDDD MM.MMM),
    are non-zero, but the degrees is 090 latitude, making it greater
    than 090, which is not allowed.
""".format(minutes, decimal_minutes, test))

    return("")

def GridSquare(test):
    """
    ADIF GridSquare field must contain a Maidenhead locator in the form
    of FF[SS[UU[EE]]], where each "F" is "A"-"R", "SS" is "00"-"99",
    each "U" is "a"-"x" and "EE" is "00"-"99"

    Arguments:
        test:
            String to test

    Returns:
        GridSquare field valid:
            Null string ("")
        GridSquare field invalid:
            Error string.
    """

    validate_arg_type((
        (test, str),
    ))

    fields = re.findall(r'.{2}', test)

    if (not fields) or (len(fields) > 4):
        return("""
    "{}" is not a correctly formatted Maidenhead locator.
    FF[SS[UU[EE]]], where each "F" is "A"-"R", "SS" is "00"-"99",
    each "U" is "a"-"x" and "EE" is "00"-"99"
""".format(test))

    field_verify = (
        (r'[A-Ra-r]{2}', """
        "{}" is not a correctly formatted Maidenhead locator.
        The first two characters are the field encodes and each character
        must be "A"-"R".
"""),
        (r'\d{2}', """
        "{}" is not a correctly formatted Maidenhead locator.
        The second two characters are the square encodes and must be
        "00"-"99".
"""),
        (r'[A-Xa-x]{2}', """
        "{}" is not a correctly formatted Maidenhead locator.
        The third two characters are the subsquare encodes and each
        character must be "a"-"x".
"""),
        (r'\d{2}', """
        "{}" is not a correctly formatted Maidenhead locator.
        The fourth two characters are the extended square encodes and must
        be "00"-"99".
""")
        )

    #
    #Start with no errors
    #
    errors = ""

    #
    #For all fields present, assure their format is correct
    #
    for i in range(len(fields)):
        if not re.fullmatch(field_verify[i][0], fields[i]):
            errors += field_verify[i][1].format(test)

    return(errors)

def GridSquareList(test):
    """
    ADIF GridSquareList field must contain a list of GridSquares
    separated by commas and no spaces.

    Arguments:
        test:
            String to test

    Returns:
        GridSquareList field valid:
            Null string ("")
        GridSquareList field invalid:
            Error string.
    """

    validate_arg_type((
        (test, str),
    ))

    #
    #Start with no errros
    #
    errors = ""

    #
    #Splitup the list of grid squares and validate each one
    #
    for i in test.split(","):
        errors += GridSquare(i)

    #
    #Return errros, if any
    #
    return(errors)

def Arrl_Sect(test):
    """
    ADIF Arrl_Sect field may only contain only one of an explicit list
    of ARRL sections. Verify against the list.

    Arguments:
        test:
            String to test

    Returns:
        Arrl_Sect field valid:
            Null string ("")
        Arrl_Sect field invalid:
            Error string.
    """

    validate_arg_type((
        (test, str),
    ))

    if test.upper() in ARRL_Section_Enumeration:
        return("")

    return("""
    "{}" not a valid ARRL section, must be one of:
        "{}"
""".format(test, '"\n        "'.join(sorted(ARRL_Section_Enumeration.keys()))))

def Band(test):
    """
    ADIF Band field may only contain only one of an explicit list of ham
    radio bands. Verify against the list.

    Arguments:
        test:
            String to test

    Returns:
        Band field valid:
            Null string ("")
        Band field invalid:
            Error string.
    """

    validate_arg_type((
        (test, str),
    ))

    if test.upper() in Band_Enumeration:
        return("")

    return("""
    "{}" not a valid band, must be one of:
        "{}"
""".format(test, '"\n        "'.join(sorted(Band_Enumeration.keys()))))

def QSO_Upload_Status(test):
    """
    ADIF QSO_Upload_Status field may only contain only one of an
    explicit list of upload statuses. Verify against the list.

    Arguments:
        test:
            String to test

    Returns:
        QSO_Upload_Status field valid:
            Null string ("")
        QSO_Upload_Status field invalid:
            Error string.
    """

    validate_arg_type((
        (test, str),
    ))

    if test.upper() in QSO_Upload_Status_Enumeration:
        return("")

    return("""
    "{}" not a QSO upload status, must be one of:
        "{}"
""".format(test, '"\n        "'.join(sorted(QSO_Upload_Status_Enumeration.keys()))))

def Continent(test):
    """
    ADIF Continent field may only contain only one of an explicit list
    of continents. Verify against the list.

    Arguments:
        test:
            String to test

    Returns:
        Continent field valid:
            Null string ("")
        Continent field invalid:
            Error string.
    """

    validate_arg_type((
        (test, str),
    ))

    if test.upper() in Continent_Enumeration:
        return("")

    return("""
    "{}" not a valid continent, must be one of:
        "{}"
""".format(test, '"\n        "'.join(sorted(Continent_Enumeration.keys()))))

def Contest(test):
    """
    ADIF Contest field may only contain only one of an explicit list of
    contests. Verify against the list.

    Arguments:
        test:
            String to test

    Returns:
        Contest field valid:
            Null string ("")
        Contest field invalid:
            Error string.
    """

    validate_arg_type((
        (test, str),
    ))

    if test in Contest_ID_Enumeration:
        return("")

    return("""
    "{}" not a valid contest, must be one of:
        "{}"
""".format(test, '"\n        "'.join(sorted(Contest_ID_Enumeration.keys()))))

def CreditList(test):
    """
    ADIF Credit field may only contain only one of an explicit list of
    credits. Verify against the list.

    Arguments:
        test:
            String to test

    Returns:
        Credit field valid:
            Null string ("")
        Credit field invalid:
            Error string.
    """

    validate_arg_type((
        (test, str),
    ))

    if (test in Credit_Ennumeration) or (test in Award_Ennumeration):
        return("")

    full_list = sorted(Credit_Ennumeration.keys()) \
        + sorted(Award_Ennumeration.keys())

    return("""
    "{}" not a valid contest credit, must be one of:
        "{}"
""".format(test, '"\n        "'.join(full_list)))

def Dxcc(test):
    """
    ADIF Dxcc field may only contain only one of an explicit list of
    entities. Verify against the list.

    Arguments:
        test:
            String to test

    Returns:
        Dxcc field valid:
            Null string ("")
        Dxcc field invalid:
            Error string.
    """

    validate_arg_type((
        (test, str),
    ))
    if test.upper() in DXCC_Entity_Code_Enumeration:
        return("")

    return("""
    "{}" not a valid DXCC entity code, must be one of:
        "{}"
""".format(test, '"\n        "'.join(sorted(DXCC_Entity_Code_Enumeration.keys()))))

def QSL_Rcvd(test):
    """
    ADIF QSL_Rcvd field may only contain only one of an explicit list of
    received statuses. Verify against the list.

    Arguments:
        test:
            String to test

    Returns:
        QSL_Rcvd field valid:
            Null string ("")
        QSL_Rcvd field invalid:
            Error string.
    """

    validate_arg_type((
        (test, str),
    ))

    if test.upper() in QSL_Rcvd_Enumeration:
        return("")

    return("""
    "{}" not a valid EQSL rcvd code, must be one of:
        "{}"
""".format(test, '"\n        "'.join(sorted(QSL_Rcvd_Enumeration.keys()))))

def QSL_Sent(test):
    """
    ADIF QSL_Sent field may only contain only one of an explicit list of
    sent statuses. Verify against the list.

    Arguments:
        test:
            String to test

    Returns:
        QSL_Sent field valid:
            Null string ("")
        QSL_Sent field invalid:
            Error string.
    """

    validate_arg_type((
        (test, str),
    ))

    if test.upper() in QSL_Sent_Enumeration:
        return("")

    return("""
    "{}" not a valid QSL via code, must be one of:
        "{}"
""".format(test, '"\n        "'.join(sorted(QSL_Sent_Enumeration.keys()))))

def QSL_Via(test):
    """
    ADIF QSL_Via field may only contain only one of an explicit list of
    via statuses. Verify against the list.

    Arguments:
        test:
            String to test

    Returns:
        QSL_Via field valid:
            Null string ("")
        QSL_Via field invalid:
            Error string.
    """

    validate_arg_type((
        (test, str),
    ))

    if test.upper() in QSL_Via_Enumeration:
        return("")

    return("""
    "{}" not a valid EQSL sent code, must be one of:
        "{}"
""".format(test, '"\n        "'.join(sorted(QSL_Via_Enumeration.keys()))))

def Mode(test):
    """
    ADIF Mode field may only contain only one of an explicit list of
    nodes. Verify against the list.

    Arguments:
        test:
            String to test

    Returns:
        Mode field valid:
            Null string ("")
        Mode field invalid:
            Error string.
    """

    validate_arg_type((
        (test, str),
    ))

    if test.upper() in Mode_Enumeration:
        return("")

    return("""
    "{}" not a valid mode, must be one of:
        "{}"
""".format(test, '"\n        "'.join(sorted(Mode_Enumeration.keys()))))

def WWFFRef(test):
    """
    ADIF WWFFRef field must be in the format of xFF-nnnn where "x" is
    one to four alphanumeric characters and nnnn is "0000" - "9999".

    Arguments:
        test:
            String to test

    Returns:
        WWFFRef field valid:
            Null string ("")
        WWFFRef field invalid:
            Error string.
    """

    validate_arg_type((
        (test, str),
    ))

    if re.fullmatch(r'[A-Z0-9]{1,4}F{2}-\d{4}', test, flags=re.I):
        return("")

    return("""
    "{}" not a valid International WWFF reference, must be in
    the format of: xFF-nnnn where "x" is one to four alphanumeric
    characters (A-Z, 0-9) and nnnn is "0000" - "9999".
""".format(test))

########################################################################
########################################################################
#
# ADIF header and QSO field definitions. Contains the name of the field
# and the field data type.
#
########################################################################
########################################################################

#
#Valid data types which contain the function to verify the data
#types [0] and the data type indicator [1]. Data type indicator is None
#if no data type indicator.
#

data_types = {
    "AwardList" : ("", AwardList),
    "CreditList" : ("", CreditList),
    "SponsoredAwardList" : ("", SponsoredAwardList),
    "Boolean" : ("B", Boolean),
    "Digit" : ("", Digit),
    "Integer" : ("", Integer),
    "Number" : ("N", Number),
    "PositiveInteger" : ("", PositiveInteger),
    "Character" : ("", Character),
    "IntlCharacter" : ("", TBS),
    "Date" : ("D", Date),
    "Time" : ("T", Time),
    "IOTARefNo" : ("", TBS),
    "String" : ("S", String),
    "IntlString" : ("I", TBS),
    "MultilineString" : ("M", MultilineString),
    "IntlMultilineString" : ("G", TBS),
    "Enumeration" : ("E", None),
    "GridSquare" : ("", GridSquare),
    "GridSquareList" : ("", GridSquareList),
    "Location" : ("L", Location),
    "SecondarySubdivisionList" : ("", TBS),
    "SOTARef" : ("", TBS),
    "WWFFRef" : ("", WWFFRef)
    }

header_fields = {
    "ADIF_VER" : ("String",),
    "CREATED_TIMESTAMP" : ("String",),
    "PROGRAMID" : ("String",),
    "PROGRAMVERSION" : ("String",),
    "USERDEF" : ("String",),
    }

record_fields = {
    "ADDRESS" : ("MultilineString",),
    "AGE" : ("Integer",),
    "ANT_AZ" : ("Number",),
    "ANT_EL" : ("Number",),
    "ANT_PATH" : Ant_Path,
    "ARRL_SECT" : Arrl_Sect,
    "AWARD_SUBMITTED" : ("SponsoredAwardList",),
    "AWARD_GRANTED" : ("SponsoredAwardList",),
    "A_INDEX" : ("Number",),
    "BAND" : Band,
    "BAND_RX" : Band,
    "CALL" : ("String",),
    "CHECK" : ("String",),
    "CLASS" : ("String",),
    "CLUBLOG_QSO_UPLOAD_DATE" : ("Date",),
    "CLUBLOG_QSO_UPLOAD_STATUS" : QSO_Upload_Status,
    "CNTY" : TBS,
    "COMMENT" : ("String",),
    "CONT" : Continent,
    "CONTACTED_OP" : ("String",),
    "CONTEST_ID" : ("String",),
    "COUNTRY" : ("String",),
    "CQZ" : ("PositiveInteger",),
    "CREDIT_SUBMITTED" : ("CreditList", "AwardList"),
    "CREDIT_GRANTED" : ("CreditList", "AwardList"),
    "DARC_DOK" : TBS,
    "DISTANCE" : ("Number",),
    "DXCC" : Dxcc,
    "EMAIL" : ("String",),
    "EQSL_QSLRDATE" : ("Date",),
    "EQSL_QSLSDATE" : ("Date",),
    "EQSL_QSL_RCVD" : QSL_Rcvd,
    "EQSL_QSL_SENT" : QSL_Sent,
    "EQ_CALL" : ("String",),
    "FISTS" : ("PositiveInteger",),
    "FISTS_CC" : ("PositiveInteger",),
    "FORCE_INIT" : ("Boolean",),
    "FREQ" : ("Number",),
    "FREQ_RX" : ("Number",),
    "GRIDSQUARE" : ("GridSquare",),
    "GUEST_OP" : ("String",),
    "HRDLOG_QSO_UPLOAD_DATE" : ("Date",),
    "HRDLOG_QSO_UPLOAD_STATUS" : QSO_Upload_Status,
    "IOTA" : ("IOTARefNo",),
    "IOTA_ISLAND_ID" : ("PositiveInteger",),
    "ITUZ" : ("PositiveInteger",),
    "K_INDEX" : ("Integer",),
    "LAT" : ("Location",),
    "LON" : ("Location",),
    "LOTW_QSLRDATE" : ("Date",),
    "LOTW_QSLSDATE" : ("Date",),
    "LOTW_QSL_RCVD" : QSL_Rcvd,
    "LOTW_QSL_SENT" : QSL_Sent,
    "MAX_BURSTS" : ("Number",),
    "MODE" : Mode,
    "MS_SHOWER" : ("String",),
    "MY_ANTENNA" : ("String",),
    "MY_ARRL_SECT" : Arrl_Sect,
    "MY_CITY" : ("String",),
    "MY_CNTY" : TBS,
    "MY_COUNTRY" : ("String",),
    "MY_CQ_ZONE" : ("PositiveInteger",),
    "MY_DXCC" : Dxcc,
    "MY_FISTS" : ("PositiveInteger",),
    "MY_GRIDSQUARE" : ("GridSquare",),
    "MY_IOTA" : ("IOTARefNo",),
    "MY_IOTA_ISLAND_ID" : "PositiveInteger",
    "MY_ITU_ZONE" : ("PositiveInteger",),
    "MY_LAT" : ("Location",),
    "MY_LON" : ("Location",),
    "MY_NAME" : ("String",),
    "MY_POSTAL_CODE" : ("String",),
    "MY_RIG" : ("String",),
    "MY_SIG" : ("String",),
    "MY_SIG_INFO" : ("String",),
    "MY_SOTA_REF" : "SOTARef",
    "MY_STATE" : TBS,
    "MY_STREET" : ("String",),
    "MY_USACA_COUNTIES" : TBS,
    "MY_VUCC_GRIDS" : ("GridSquareList",),
    "MY_WWFF_REF" : ("WWFFRef",),
    "NAME" : ("String",),
    "NOTES" : ("MultilineString",),
    "NR_BURSTS" : ("Integer",),
    "NR_PINGS" : ("Integer",),
    "OPERATOR" : ("String",),
    "OWNER_CALLSIGN" : ("String",),
    "PFX" : ("String",),
    "PRECEDENCE" : ("String",),
    "PROP_MODE" : TBS,
    "PUBLIC_KEY" : ("String",),
    "QRZCOM_QSO_UPLOAD_DATE" : ("Date",),
    "QRZCOM_QSO_UPLOAD_STATUS" : QSO_Upload_Status,
    "QSLMSG" : ("MultilineString",),
    "QSLRDATE" : ("Date",),
    "QSLSDATE" : ("Date",),
    "QSL_RCVD" : QSL_Rcvd,
    "QSL_RCVD_VIA" : QSL_Via,
    "QSL_SENT" : QSL_Sent,
    "QSL_SENT_VIA" : QSL_Via,
    "QSL_VIA" : ("String",),
    "QSO_COMPLETE" : TBS,
    "QSO_DATE" : ("Date",),
    "QSO_DATE_OFF" : ("Date",),
    "QSO_RANDOM" : ("Boolean",),
    "QTH" : ("String",),
    "REGION" : Region,
    "RIG" : ("MultilineString",),
    "RST_RCVD" : ("String",),
    "RST_SENT" : ("String",),
    "RX_PWR" : ("PositiveInteger",),
    "SAT_MODE" : ("String",),
    "SAT_NAME" : ("String",),
    "SFI" : ("Integer",),
    "SIG" : ("String",),
    "SIG_INFO" : ("String",),
    "SILENT_KEY" : ("Boolean",),
    "SKCC" : ("String",),
    "SOTA_REF" : "SOTARef",
    "SRX" : ("Integer",),
    "SRX_STRING" : ("String",),
    "STATE" : TBS,
    "STATION_CALLSIGN" : ("String",),
    "STX" : ("Integer",),
    "STX_STRING" : ("String",),
    "SUBMODE" : ("String",),
    "SWL" : ("Boolean",),
    "TEN_TEN" : ("PositiveInteger",),
    "TIME_OFF" : ("Time",),
    "TIME_ON" : ("Time",),
    "TX_PWR" : ("PositiveInteger",),
    "UKSMG" : ("PositiveInteger",),
    "USACA_COUNTIES" : "SecondarySubdivisionList",
    "VE_PROV" : ("String",),
    "VUCC_GRIDS" : ("GridSquareList",),
    "WEB" : ("String",),
    "WWFF_REF" : ("WWFFRef",)
    }

#
#XML supports the internationalization fields (UTF-8)
#
xml_subset_record_fields = {
    "ADDRESS_INTL" : "IntlMultilineString",
    "COMMENT_INTL" : "IntlString",
    "COUNTRY_INTL" : "IntlString",
    "MY_ANTENNA_INTL" : "IntlString",
    "MY_CITY_INTL" : "IntlString",
    "MY_COUNTRY_INTL" : "IntlString",
    "MY_NAME_INTL" : "IntlString",
    "MY_POSTAL_CODE_INTL" : "IntlString",
    "MY_RIG_INTL" : "IntlString",
    "MY_SIG_INTL" : "IntlString",
    "MY_SIG_INFO_INTL" : "IntlString",
    "MY_STREET_INTL" : "IntlString",
    "NAME_INTL" : "IntlString",
    "NOTES_INTL" : "IntlMultilineString",
    "QSLMSG_INTL" : "IntlMultilineString",
    "QTH_INTL" : "IntlString",
    "RIG_INTL" : "IntlMultilineString",
    "SIG_INTL" : "IntlString",
    "SIG_INFO_INTL" : "IntlString",
    }

#
#The XML data types
#
xml_record_fields = {**record_fields, **xml_subset_record_fields}

#
#USERDEFn is a special case
#
re_userdef = r'USERDEF(\d+)'

def userdef(test):
    udnum = re.findall(r'USERDEF(\d+)', test)
    if udnum:
        udnum = udnum[0]
        if int(udnum) < 1:
            return("""
    ADIF USERDEF number "{}" invalid, it must be greater than 0:
    Specifies the name and optional enumeration or range of the nth
    user-defined field, where n is a positive integer.
""")
    else:
        return("""
    ADIF USERDEF "{}" format invalid, it must be "USERDEFn"
    where "n" is a number greater than 0.
""")

    return("")

def dictonary_duplicates(dictonary):
    """
    Verify that there are not any duplicate keys that differ only in
    character case.

    Arguments:
        dictonary:
            The dictonary of fields to validate

    Returns:
        "" if no conflicts found
        Error text if conflicts found.
    """

    validate_arg_type((
        (dictonary, dict),
    ))

    #
    #Make a dictonary of all uppercase keys with empty lists
    #
    upcase_dict = {}
    for i in dictonary:
        upcase_dict[i.upper()] = []

    #
    #Now store all keys cooresponding to that uppercse key in the
    #dictonary
    #
    for i in dictonary:
        upcase_dict[i.upper()].append(i)

    #
    #At this point every key should have one and only one entry in its
    #list. More than one means we have multiple keys that map to the
    #same uppercase key, for example: foo, foO, fOo, fOO, Foo, FoO, FOo
    #and FOO makes eight.
    #
    errors = ""
    for i in sorted(upcase_dict):
        #
        #See if more than one entry
        #
        if len(upcase_dict[i]) > 1:
            #
            #We've got an error
            #
            errors += """
    Field conflict due to character case. The following field names are
    duplicates, differing only by character case:
        "{}"
""".format('", "'.join(sorted(upcase_dict[i])))

    #
    #Returns errors if any found or null string if no errors.
    #
    return(errors)

def get_dti(dti):
    """
    Return character (or null string) that identifies the data type

    Arguments:
        dti:
            Contains the data type string if anything but an enumerated
            type, or a callable routine if an enumerated type.

    Returns:
        One character data type or null string if no data type
        cooresponds to this data type.
    """

    validate_arg_type((
        (dti, tuple, type(get_dti)),
    ))

    if callable(dti):
        return("E")
    else:
        return(data_types[dti[0]][0])
        
########################################################################
########################################################################
#
# Validation code that assures tables, etc. that can be checked are
# correctly structured
#
########################################################################
########################################################################

#
#Start with no library errors
#
lib_errors = ""

#
#All header and QSO fields' data types should be found in the data types
#table (or, in the case of the enumeration types, there should be a
#callable routine). Assure one or the other exists.
#
#We use the table's names (strings) for error reporting reasons, see the
#error message at the bottom of the loop which uses the string in the
#error message.
#
for table in ("header_fields",
        "record_fields", "xml_subset_record_fields"):
    for key, value in eval(table).items():
        #
        #The value should be a tuple of ADIF data types OR a callable
        #function if the data type is ennumerated.
        #
        if callable(value):
            #
            #It's a callable function (Enumeration), that's a valid
            #option, we're done checking
            #
            continue

        if isinstance(value, tuple):
            #
            #It's a tuple of one or more data types. Check that all data
            #types are valid
            #
            for dt in value:
                #
                #for each data type, make sure it exists
                #
                if dt not in data_types:
                    lib_errors += """
SevereError: In hamlib.py, {0} field "{1}" has
             a data type of "{2}" which is NOT in the
             data_types dictonary. Either correct the
             {0} "{1}" field datatype or add "{2}"
             to the data_types dictonary.
""".format(table, key, dt)

#
#If we found any errors, exit
#
if lib_errors:
    print(lib_errors)
    sys.exit(1)

########################################################################
########################################################################
#
# Callable user interface functions
#
########################################################################
########################################################################

def get_input(prompt_help, prompt, default=None, can_exit=True):
    """
    Get input string from console.

    If "HELP" is typed, print <script_name>.help file, if one exists.
    If "EXIT" is typed and "can_exit" is True, exit the program.
        Otherwise print message that the program cannot be exited and
        reprint the prompt.
    If "?" is typed, print specific help text for this question, if it
        was supplied (suggestion: supply it!)
    If nothing is typed (null string, "") and default is None, do the
        same thing as "?". Otherwide return the default string so the
        calling function can use it as if it was typed in.

    If none of the above, strip off leading and trailing blanks and
        pass the string back to the calling function.

    Arguments:
        prompt_help:
            Text to print if help on this prompt is requested.
        prompt:
            String to print as question prompt.
        default: Default None
            None:
                No default answer, print prompt help, then print prompt
                again if just <Enter> ("") is pressed.
            string:
                String to return if just <Enter> ("") is pressed.
        can_exit: Default True
            True:
                Exit the program if "EXIT" is typed.
            False:
                Print message that the program cannot be exited print
                the prompt again.
    Returns:
        Input string to calling function.
    """

    validate_arg_type((
        (prompt_help, str),
        (prompt, str),
        (default, str, None),
        (can_exit, bool),
    ))

    while(True):
        #
        #Get input, strip blanks
        #
        text = str(input(prompt)).strip()

        #
        #If a default is specified and nothing entered (""), return
        #default string.
        #
        if (default is not None) and (not text):
            return(default)

        #
        #If help is  requested, display entire program help
        #
        if text.upper() == "HELP":
            print(script_help)
            continue

        #
        #If we can exit at this point and "EXIT" entered, exit
        #
        if text.upper() == "EXIT":
            if can_exit:
                sys.exit(0)
            else:
                print("Cannot exit at this point.\n\n")
                continue

        #
        #If input is "?" or just <Enter> (null string - ""), print
        #prompt help text if itexists.
        #
        if (text == "?") or (not text):
            print("""
Type "EXIT" to exit logger.
Type "?" for this help.
""" + prompt_help + """
Type "HELP" for more information.
""")
            continue

        break

    #
    #Return the text from the console
    #
    return(text)


def get_yes_no(prompt_help, prompt, default="Y", can_exit=True):
    """
    Print prompt that requires a Y or N answer.

    Arguments:
        help:
            Text to print if help on this prompt is requested.
        prompt_help:
            String to print as question prompt NOT including Y/N portion
            of prompt.
        default: Default "Y"
            None:
                No default answer, the user MUST answer "Y" or "N".
            string:
                "Y":
                    Deafult answer to the question is "Yes".
                "N":
                    Deafult answer to the question is "No".
        can_exit: Default True
            True:
                Exit the program if "EXIT" is typed.
            False:
                Print message that the program cannot be exited print
                the prompt again.

    Returns:
        True if Yes
        False if No
    """

    validate_arg_type((
        (prompt_help, str),
        (prompt, str),
        (default, str, None),
        (can_exit, bool),
    ))

    #
    #Make the default for no default yes/no answer something the user
    #can't possibly type by accident!
    #
    no_default_yes_no_answer = "XX_NO_DEFAULT_YES_NO_ANSWER_XX"

    default_prompt = {
        "Y" : " [(Y), n]: ",
        "N" : " [(N), y]: ",
        no_default_yes_no_answer : " [y, n]: "
        }

    if default is None:
        default = no_default_yes_no_answer
    else:
        default = default[:1].upper()

    #
    #Runtime programming check: Make sure "Y", "N" or None was supplied
    #as a default. If this fails, the program immediately exits.
    #
    if default not in default_prompt:
        print("""
SeverError: Default supplied for get_yes_no was "{}".
            It must be "Y", "N" or None.
""".format(default)
    + generate_stack_trace(2))
        sys.exit(1)

    #
    #Keep trying until you get a "Y", "N" or
    #"XX_NO_DEFAULT_YES_NO_ANSWER_XX" (if no default and the user types
    #just <ENTER>).
    #
    while(True):
        #
        #Ask the question and get an upcased response.
        #
        answer = get_input(prompt_help,
            prompt.rstrip() + default_prompt[default],
            default=default,
            can_exit=can_exit).upper()

        #
        #At this point we have input. Let's hope it's a "Y" or "N" after
        #we reduce it to the first character. Note that if there's no
        #default, the string ("XX_NO_DEFAULT_YES_NO_ANSWER_XX"") starts
        #with an "X" and once reduced to one character it won't match
        #anything in the default_prompt dictonary, causing an error to
        #be printed and the prompt displayed again.
        #

        #
        #Reduce answer to first character
        #
        answer = answer[:1]

        #
        #If valid response, return True if "Y", False if "N".
        #
        if answer in default_prompt:
            return(answer == "Y")

        #
        #Invalid response, report error and ask again.
        #
        if default == no_default_yes_no_answer:
            print("""
Error: First character of answer must be 'Y' or 'N', there is no
       default.
""")
        else:
            print("""
Error: First character of answer must be 'Y' or 'N' or <Enter> to use
       the default of "{}".
""".format(default))

def valid_callsign(callsign, slash=False):
    """
    Validate the callsign against the expected format - at least the
    best we can given the lack of a hard standard... :)

    Arguments:
        callsign:
            String containing callsign.
        slash: Default False
            True:
                Slash is allowed in the callsign name.
            False:
                Slash will generate an "Invalid callsign" error.

    Returns:
        Valid callsign:
            Null string ("")
        Invalid callsign:
            Error string.
    """
    
    validate_arg_type((
        (callsign, str),
        (slash, bool)
    ))

    if slash:
        if not re.fullmatch(r'[A-Z0-9]{3,}(/[A-Z0-9]+|$)', callsign):
            #
            #If an error is found, report it
            #
            return("""
Error: "{}" is not a valid format for a callsign.
       It must be three or more letters and digits only. Callsign may be
       terminated by a "/" followed by one or more letters and digits.
       Examples: "K0RLO", "W1JU" or "K0RLO/R1", "W1JU/MOBILE"
""".format(callsign))
    else:
        if not re.fullmatch(r'[A-Z0-9]{3,}', callsign):
            #
            #If an error is found, report it
            #
            return("""
Error: "{}" is not a valid format for a callsign. It must be three or
       more letters and digits only. It may NOT contain a "/"!
       Examples: "K0RLO" or "W1JU"
""".format(callsign))

    #
    #It's a correctly formatted callsign, return false.
    #
    return("")

def field(field_name, field_contents, data_type_indicator=""):
    """
    Convert a field name and contents to a correctly formatted ADIF field
    format "<FIELD_NAME:LENGTH_OF_CONTENTS>CONTENTS"

    Arguments:
        field_name:
            Name of the field
        field_contents:
            Contents of field
        data_type_indicator:
            Character of data type if to be included in the field, None
            otherwise.

    Returns:
        Correctly formatted ADIF field
    """

    validate_arg_type((
        (field_name, str),
        (field_contents, str),
        (data_type_indicator, str),
    ))

    #
    #See if data type to be included in field
    #
    if data_type_indicator:
        data_type_indicator = ":" + data_type_indicator

    #
    #Return the correctly formatted field.
    #
    return("<{}:{}{}>{}".format(field_name,
                            len(field_contents),
                            data_type_indicator,
                            field_contents))

def validate_field(field_definitions, field_name, field_contents):
    """
    Make sure specified header field is a valid fiend and it's contents
    are valid.

    Arguments:
        field_definitions:
            Dictonary of valid field names.
        field_name:
            Name of the field
        field_contents:
            Contents of field

    Returns:
        Field and contents valid:
            Null string ("")
        Field or contents invalid:
            Error string
    """

    validate_arg_type((
        (field_definitions, dict),
        (field_name, str),
        (field_contents, str),
    ))

    #
    #Make sure field is a valid header field. If not, report error and
    #return
    #
    if field_name.upper() not in field_definitions:
        return("""
    field "{}" is not a valid field name.
""".format(field_name))

    #
    #Make sure field contents are valid by calling the field
    #verification function in the data_types dictonary.
    #
    #We're guaranteed that the validation routine exists becasue of the
    #up-front library checking that happens at the end of this module.
    #
    field_type = field_definitions[field_name.upper()]

    if callable(field_type):
        #
        #It's an enumeration type with a validation function. Call the
        #valididation function.
        #
        errors = field_type(field_contents)
    else:
        #
        #It's not an ennumeration type. Cjeck all types and if any one
        #comes back without errors, were good to go...
        #
        errors = ""
        for test_type in field_type:
            #
            #Validate against each data type possible.
            #
            hold_error = data_types[test_type][1](field_contents)
            if not hold_error:
                #
                #If this data type matches, we're good. Clear any errors
                #you may have found for other data types.
                #
                errors = ""
                #
                #Exit the loop
                #
                break

            #
            #We never found a valid data type, report errors.
            #
            errors += hold_errors

    #
    #Retrun errors or null string
    #
    return(errors)

def ADIF_record(fields, spaces=0, include_data_type=False):
    """
    Convert a dictonary of fields to an ADIF record and return the
    string.

    Arguments:
        fields:
            Dictonary of fields and their contents.
        spaces: Default: 0
            Number of spaces between fields.
        include_data_type: Default: False
            If True, include data type in data specifier.

    Returns:
        Correctly formatted ADIF record with <EOR>\n at end
    """

    validate_arg_type((
        (fields, dict),
        (spaces, int),
        (include_data_type, bool),
    ))

    #
    #Number of spaces between fields
    #
    spaces = spaces * " "

    #
    #Generate fields in requested order
    #
    adif_record = ""
    errors = ""
    for field_name,field_value in sorted(fields.items()):

        #
        #Validate field and contents
        #
        errors += validate_field(record_fields, field_name, field_value)

        #
        #If any errors, detected, just continue checking
        #
        if errors:
            continue

        #
        #Generate data type identifier if reqested
        #
        dti = get_dti(record_fields[field_name]) if include_data_type else ""

        #
        #Add field to record
        #
        adif_record += field(field_name, fields[field_name], dti) + spaces

    #
    #Validate dictonary and assure that no mixed-case field names cause
    #duplicates. Note errors is "" if no errors.
    #
    errors += dictonary_duplicates(fields)

    #
    #See if any errors
    #
    if errors:
        print("""
SevereError: Errors were found with the following ADIF record fields:
""" + errors)
        sys.exit(1)

    #
    #Return the correctly formatted record with an <EOR> and newline at
    #the end
    #
    return(adif_record + end_of_record + "\n")

def ADIF_header(fields, header_comment="", include_data_type=False):
    """
    Convert a dictonary of fields to an ADIF header and return the
    string.

    Arguments:
        fields:
            Dictonary of fields and their contents.
        include_data_type: Default: False
            If True, include data type in data specifier.

    Returns:
        Correctly formatted ADIF record with <EOR>\n at end
    """

    validate_arg_type((
        (fields, dict),
        (header_comment, str),
        (include_data_type, bool),
    ))

    #
    #Get the current Zulu for header timestamp and generate file comment
    #
    zulu = time.gmtime()
    zdate = time.strftime("%Y-%m-%d", zulu)
    ztime = time.strftime("%H:%M:%S Zulu", zulu)

    adif_header = "Generated on {} at {} ".format(zdate, ztime) \
        + header_comment.strip() + "\n\n"

    #
    #Set the ADIF version to the version supported by this file unless
    #the user has defined it.
    #
    for i in fields:
        if i.upper() == ADIF_VERSION_FIELD:
            break
    else:
        fields[ADIF_VERSION_FIELD] = ADIF_VERSION

    #
    #Generate fields in sorted order
    #
    errors = ""
    for field_name,field_value in sorted(fields.items()):

        #
        #Validate field and contents
        #
        errors += validate_field(header_fields, field_name, field_value)

        #
        #If any errors, detected, just continue checking
        #
        if errors:
            continue

        dti = get_dti(header_fields[field_name])  if include_data_type else ""

        #
        #Add field to header
        #
        adif_header += field(field_name, field_value, dti) + "\n"

    #
    #Validate dictonary and assure that no mixed-case field names cause
    #duplicates. Note errors is "" if no errors.
    #
    errors += dictonary_duplicates(fields)

    #
    #See if any errors
    #
    if errors:
        print("""
SevereError: Errors were found with the following ADIF header fields:
""" + errors)
        sys.exit(1)

    #
    #Return the correctly formatted record with an <EOH> and newline at
    #the end
    #
    return(adif_header + end_of_header + "\n")


def freq_to_band(freq):
    """
    Given a frequency, convert it to a band

    Arguments:
        freq:   Frequency to use to search for band

    Returns:
        Tuple of one member if frequency valid
        String containing error if frequency invalid
    """

    validate_arg_type((
        (freq, str),
    ))

    #
    #Convert string frequency to float (valid float format already
    #verified)
    #
    float_freq = float(freq)

    #
    #Go through bands and check to see if frequency in range
    #
    for band in band_enumeration:
        if ((float_freq >= band_enumeration[band][0]) and
            (float_freq <= band_enumeration[band][1])):
            #
            #Frequency in range, return band
            #
            return((band,))

    #
    #Frequency not found in any band range, return False
    #
    return("""
    Frequency "{}" is does not fall within a valid range.
""".format(freq))

def valid_band(band):
    """
    See if valid band specified. If so, return it. If not, return False

    Arguments:
        band:   String containing band(s) to be verified

    Returns:
        List of band(s) if band(s) valid.
        Error string if invalid
    """

    validate_arg_type((
        (band, str),
    ))

    #
    #Split into xmit and recieve bands, if both specified
    #
    bands = re.split(default_split, band)

    #
    #If more than two bands specified, it's an error
    #
    if len(bands) > 2:
        return("""
    More than two bands specified. Specify a single band for
    simplex operation, two bands - first transmit, then receive
    ONLY for split frequency operations on different bands.
    Examples: "20M" or "20M 40M".
""")

    #
    #No bands
    #
    band_list = []

    for index in range(len(bands)):
        #
        #If it's not a valid band, return false
        #
        if bands[index] not in band_enumeration:
            return("""
    "{}" does not fall within a known band.
""".format(bands[index]))

        #
        #It's a valid band, save it
        #
        band_list.append(bands[index])

    #
    #Retrun xmit and recv band(s)
    #
    return(band_list)

def valid_frequency(freq):
    """
    See if valid frequency specified. If so, return it. If not, return False

    Arguments:
        freq:
            String containing frequency/frequencies to be verified

    Returns:
        List of bands and frequencies if correctly formatted
        Error string if formatted incorrectly
    """

    validate_arg_type((
        (freq, str),
    ))

    #
    #Split into xmit and recieve ferquencies, if both specified
    #
    freq = re.split(default_split, freq)

    #
    #If more than two frequencies specified, it's an error
    #
    if len(freq) > 2:
        return("""
    More than two frequencies specified. Specify a single frequency for
    simplex operation, two frequencies - first transmit, then receive
    for split frequency operations.
    Examples: "14.200" or "14.200 14.300".
""")

    #
    #Initialize band and frequency pairs
    #
    bands = []
    freqs = []

    for index in range(len(freq)):
        #
        #Check frequency for a valid format
        #
        if not re.fullmatch(re_frequency, freq[index]):
            #
            #Not a correctly formatted frequency, return False
            #
            return("""
    "{}" is not a valid frequency format.
""".format(freq[index]))

        #
        #Determine band
        #
        band = freq_to_band(freq[index])
        if type(band) == str:
            #
            #Frequency not valid, return error text supplied.
            #
            return(band)

        #
        #Save lists of band (which came back asa  tuple with one entry) and
        #frequency
        #
        bands.append(band[0])
        freqs.append(freq[index])

    #
    #If transmit and receive frequencies are the same, just report one
    #frequency and band.
    #
    if (len(freqs) > 1) and (freqs[0] == freqs[1]):
        freqs.pop(0)
        bands.pop(0)

    #
    #Retrun xmit and rcv bands and frequencies
    #
    return((bands, freqs))

def valid_mode(mode_submode):
    """
    See if mode (and submode) specified. If so, return the mode and
    submode.

    Arguments:
        mode_submode:
            String containing mode (and submode) to be verified

    Returns:
        [mode, submode] is valid.
        False if mode or submode not valid
    """

    validate_arg_type((
        (mode_submode, str),
    ))

    #
    #Some submodes can have blanks in them (thanks a lot, folks). So I
    #strip the blanks out for comparing, but keep around the original
    #format for reporting
    #
    #OLIVIA
    #OLIVIA OLIVIA8/500
    #OLIVIA8/500
    #
    #So I need to generate all the possible permutations and
    #combinations of mode and submode and throw it at the code that
    #identifies it to see if I get a match somehow.
    #

    #
    #Breakup the mode and submode
    #
    mode_submode = re.split(default_split, mode_submode)
    
    #
    #Pull off mode and re-create the submode with single blanks for
    #when the submode has blanks in it - to assure we have a match.
    #
    mode_text = mode_submode.pop(0)
    submode_text = " ".join(mode_submode)

    if submode_text:
        #
        #We've specified both a mode and submode, assure that they are
        #valid and compatible
        #
        if mode_text.upper() in Mode_enumeration:
            if submode_text.upper() in Mode_enumeration[mode_text.upper()]:
                #
                #Mode and submode are consistent
                #
                return(mode_text, submode_text)
            else:
                #
                #Not a valid submode for this mode, report error
                #
                return("""
Error: Submode "{}" specified for mode "{}".
       that is an invalid submode. Submode must be one of the following:
       "{}"
""".format(mode_text, '", "'.join(Mode_enumeration[mode_text.upper()])))
        else:
            #
            #Not a valid mode, report error
            #
            return("""
Error: "{}" is an invalid mode. It must be one of the following:
       "{}"
""".format(mode_text, '", "'.join(Mode_enumeration)))

    #
    #Only a mode or submode specified, validate
    #
    if mode_text.upper() in Mode_enumeration:
        #
        #Only a mode was specified, just return a mode
        #
        return(mode_text,)

    #
    #See if a valid submode specified alone
    #
    if mode_text.upper() in Submode_enumeration:
        #
        #Only a submode was specified, return both a mode and submode.
        #
        return(Submode_enumeration[mode_text.upper()], mode_text.upper())

        #
        #Mode incorrect for submode specified
        #
        return("""
Error: "{}" is an invalid mode or submode.
   Examples: "CW", "LSB" "SSB USB" or "JT9 JT9H FAST".
""".format(mode_text))


