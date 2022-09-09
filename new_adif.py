import calendar
import re
import k0rlo

def TBS(test):
    #
    #To be supplied checking. Placeholder, always return valid (False)
    #
    return(False)

def Boolean(test):
    if rf.fullmatch(r'[NnYy]', test):
        return(False)

    return("""
Error: ADIF boolean is not "Y" or "N" (or "y" or "n")
""")

def Digit(test):
    if rf.fullmatch(r'[0-9]', test):
        return(False)

    return("""
Error: ADIF digit is outside the "0" to "9" (ASCII 48-57) range.
""")

def Integer(test):
    if rf.fullmatch(r'-?\d+', test):
        return(False)

    return("""
Error: ADIF integer "{}" does not have integer format:
       A sequence of one or more Digits representing a decimal integer,
       optionally preceded by a minus sign.  Leading zeroes are allowed.
""")


def PositiveInteger(test):
    if not rf.fullmatch(r'\d+', test):
        #
        #Incorrect format
        #
        return("""
Error: ADIF positive integer "{}" does not have integer format:
       An unsigned sequence of one or more Digits representing a decimal
       integer that has a value greater than 0.  Leading zeroes are allowed.
""")

    if int(test) < 1:
        #
        #Incorrect format
        #
        return("""
Error: ADIF positive integer "{}" must be greater than zero.
""")    

    #
    #It's correct
    #
    return(False)

def Number(test):
    if rf.fullmatch(r'-?(\.\d+)|(\d+\.?\d*)', test):
        return(False)

    return("""
Error: ADIF number "{}" does not have number format:
       A sequence of one or more Digits representing a decimal number,
       optionally preceded by a minus sign and optionally including a single
       decimal point.
""")

def Character(test):
    if rf.fullmatch(r'[\ -~]', test):
        return(False)

    return("""
Error: ADIF character is outside the " " to "~" (ASCII 36-126) range.
""")

def String(test):
    if rf.fullmatch(r'[\ -~]+', test):
        return(False)

    return("""
Error: ADIF string contains a character outside the " " to "~" (ASCII 36-126)
       range.
""")

def MultilineString(test):
    #
    #Make copy of multiline string to be checked
    #
    test_copy = str(test)

    while(test_copy):
        #
        #Match to string followed by CR-LF or end of line
        if re.match(r'[\ -~]+(\r\n|$)', test_copy):
            #
            #Remove the matched line
            #
            test_copy = re.sub(r'^[\ -~]+(\r\n|$)', "", test_copy)
        else:
            #
            #Not a correct multiline format
            #
            return("""
Error: The following is not a valid MultilineString which must follow this
       standard: A sequence of Characters and line-breaks, where a line break
       is an ASCII CR (code 13) followed immediately by an ASCII LF (code 10).
       Invalid MultilineString:
{}
""".format(test))

    #
    #Valid multiline string
    #
    return(False)

def Date(test):

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
        if month > 12:
            errors += """
Error: ADIF date's month is greater than 12: "{}"
""".format(month)

        #
        #Make sure day is in range
        #
        max_day = calendar.monthrange(year, month)
        if day > maxday:
            errors += """
Error: ADIF date's day is greater than the days in the month.
       {}/{} has {} days, {} was specified.
""".format(month, year, max_day, day)

    else:
        errors += """
Error: ADIF date "{}" not in correct format. Should be "YYYYMMDD"
""".format(test)

    #
    #Report all errors found
    #
    if errors:
        return(errors)

    #
    #Date valid, return false
    #
    return(False)

def Time(test):

    errors = ""

    hms = re.findall(r'(\d{2})(\d{2})(\d\d)?$', test)
    if hms:
        #
        #Get hour, minute and [maybe] seond and validate
        #
        (hour, minute, second) = ymd[0]

        #
        #Make sure month is in range
        #
        if int(hour) > 23:
            errors += """
Error: ADIF time's hour is greater than 23: "{}"
""".format(hour)

        #
        #Make sure minute is in range
        #
        max_day = calendar.monthrange(year, month)
        if int(minute) > 59:
            errors += """
Error: ADIF time's minutes is greater than 59: "{}"
""".format(minute)

        if second and (int(second) > 59):
            errors += """
Error: ADIF time's seconds is greater than 59: "{}"
""".format(second)

    else:
        errors += """
Error: ADIF time "{}" not in correct format. Should be "HHMM" or "HHMMSS"
""".format(test)

    #
    #Report all errors found
    #
    if errors:
        return(errors)

    #
    #Time valid, return false
    #
    return(False)

header_fields = {
    "ADIF_VER" : (String),
    "CREATED_TIMESTAMP" : (String), 
    "PROGRAMID" : (String),
    "PROGRAMVERSION" : (String),
    "USERDEF" : (String)
    }

QSO_fields = {
    "ADDRESS" : (MultilineString),
    "ADDRESS_INTL" : (TBS),
    "AGE" : (Integer),
    "ANT_AZ" : (Number),
    "ANT_EL" : (Number),
    "ANT_PATH" : (TBS),
    "ARRL_SECT" : (TBS),
    "AWARD_GRANTED" : (TBS),
    "AWARD_SUBMITTED" : (TBS),
    "A_INDEX" : (Number),
    "BAND" : (TBS),
    "BAND_RX" : (TBS),
    "CALL" : (String),
    "CHECK" : (String),
    "CLASS" : (String),
    "CLUBLOG_QSO_UPLOAD_DATE" : Date,
    "CLUBLOG_QSO_UPLOAD_STATUS" : (TBS),
    "CNTY" : (TBS),
    "COMMENT" : (String),
    "COMMENT_INTL" : (TBS),
    "CONT" : (TBS),
    "CONTACTED_OP" : (String),
    "CONTEST_ID" : (String),
    "COUNTRY" : (String),
    "COUNTRY_INTL" : (TBS),
    "CQZ" : (PositiveInteger),
    "CREDIT_GRANTED" : (TBS),
    "CREDIT_SUBMITTED" : (TBS),
    "DARC_DOK" : (TBS),
    "DISTANCE" : (Number),
    "DXCC" : (TBS),
    "EMAIL" : (String),
    "EQSL_QSLRDATE" : (Date),
    "EQSL_QSLSDATE" : (Date),
    "EQSL_QSL_RCVD" : (TBS),
    "EQSL_QSL_SENT" : (TBS),
    "EQ_CALL" : (String),
    "FISTS" : (PositiveInteger),
    "FISTS_CC" : (PositiveInteger),
    "FORCE_INIT" : (Boolean),
    "FREQ" : (Number),
    "FREQ_RX" : (Number),
    "GRIDSQUARE" : (TBS),
    "GUEST_OP" : (String),
    "HRDLOG_QSO_UPLOAD_DATE" : (Date),
    "HRDLOG_QSO_UPLOAD_STATUS" : (TBS),
    "IOTA" : (TBS),
    "IOTA_ISLAND_ID" : (PositiveInteger),
    "ITUZ" : (PositiveInteger),
    "K_INDEX" : (Integer),
    "LAT" : (TBS),
    "LON" : (TBS),
    "LOTW_QSLRDATE" : (Date),
    "LOTW_QSLSDATE" : (Date),
    "LOTW_QSL_RCVD" : (TBS),
    "LOTW_QSL_SENT" : (TBS),
    "MAX_BURSTS" : (Number),
    "MODE" : (TBS),
    "MS_SHOWER" : (String),
    "MY_ANTENNA" : (String),
    "MY_ANTENNA_INTL" : (TBS),
    "MY_ARRL_SECT" : (TBS),
    "MY_CITY" : (String),
    "MY_CITY_INTL" : (TBS),
    "MY_CNTY" : (TBS),
    "MY_COUNTRY" : (String),
    "MY_COUNTRY_INTL" : (TBS),
    "MY_CQ_ZONE" : (PositiveInteger),
    "MY_DXCC" : (TBS),
    "MY_FISTS" : (PositiveInteger),
    "MY_GRIDSQUARE" : (TBS),
    "MY_IOTA" : (TBS),
    "MY_IOTA_ISLAND_ID" : (TBS),
    "MY_ITU_ZONE" : (PositiveInteger),
    "MY_LAT" : (TBS),
    "MY_LON" : (TBS),
    "MY_NAME" : (String),
    "MY_NAME_INTL" : (TBS),
    "MY_POSTAL_CODE" : (String),
    "MY_POSTAL_CODE_INTL" : (TBS),
    "MY_RIG" : (String),
    "MY_RIG_INTL" : (TBS),
    "MY_SIG" : (String),
    "MY_SIG_INFO" : (String),
    "MY_SIG_INFO_INTL" : (TBS),
    "MY_SIG_INTL" : (TBS),
    "MY_SOTA_REF" : (TBS),
    "MY_STATE" : (TBS),
    "MY_STREET" : (String),
    "MY_STREET_INTL" : (TBS),
    "MY_USACA_COUNTIES" : (TBS),
    "MY_VUCC_GRIDS" : (TBS),
    "MY_WWFF_REF" : (TBS),
    "NAME" : (String),
    "NAME_INTL" : (TBS),
    "NOTES" : (MultilineString),
    "NOTES_INTL" : (TBS),
    "NR_BURSTS" : (Integer),
    "NR_PINGS" : (Integer),
    "OPERATOR" : (String),
    "OWNER_CALLSIGN" : (String),
    "PFX" : (String),
    "PRECEDENCE" : (String),
    "PROP_MODE" : (TBS),
    "PUBLIC_KEY" : (String),
    "QRZCOM_QSO_UPLOAD_DATE" : (Date),
    "QRZCOM_QSO_UPLOAD_STATUS" : (TBS),
    "QSLMSG" : (MultilineString),
    "QSLMSG_INTL" : (TBS),
    "QSLRDATE" : (Date),
    "QSLSDATE" : (Date),
    "QSL_RCVD" : (TBS),
    "QSL_RCVD_VIA" : (TBS),
    "QSL_SENT" : (TBS),
    "QSL_SENT_VIA" : (TBS),
    "QSL_VIA" : (String),
    "QSO_COMPLETE" : (TBS),
    "QSO_DATE" : (TBS),
    "QSO_DATE_OFF" : (TBS),
    "QSO_RANDOM" : (Boolean),
    "QTH" : (String),
    "QTH_INTL" : (TBS),
    "REGION" : (TBS),
    "RIG" : (MultilineString),
    "RIG_INTL" : (TBS),
    "RST_RCVD" : (String),
    "RST_SENT" : (String),
    "RX_PWR" : (PositiveInteger),
    "SAT_MODE" : (String),
    "SAT_NAME" : (String),
    "SFI" : (Integer),
    "SIG" : (String),
    "SIG_INFO" : (String),
    "SIG_INFO_INTL" : (TBS),
    "SIG_INTL" : (TBS),
    "SILENT_KEY" : (Boolean),
    "SKCC" : (String),
    "SOTA_REF" : (TBS),
    "SRX" : (Integer),
    "SRX_STRING" : (String),
    "STATE" : (TBS),
    "STATION_CALLSIGN" : (String),
    "STX" : (Integer),
    "STX_STRING" : (String),
    "SUBMODE" : (String),
    "SWL" : (Boolean),
    "TEN_TEN" : (PositiveInteger),
    "TIME_OFF" : (Time),
    "TIME_ON" : (Time),
    "TX_PWR" : (PositiveInteger),
    "UKSMG" : (PositiveInteger),
    "USACA_COUNTIES" : (TBS),
    "VE_PROV" : (String),
    "VUCC_GRIDS" : (TBS),
    "WEB" : (String),
    "WWFF_REF" : (TBS)
    }

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
Error: ADIF USERDEF number "{}" invalid, it must be greater than 0:
       Specifies the name and optional enumeration or range of the nth
       user-defined field, where n is a positive integer.
""")
    else:
        return("""
Error: ADIF USERDEF "{}" format invalid, it must be "USERDEFn" where "n" is a
       number greater than 0.
""")

    return(False)

extension = ".adif"


ant_path_enumeration = {
    'G':'grayline',
    'O':'other',
    'S':'short path',
    'L':'long path'
    }

ARRL_Section_Enumeration = {
   "AL" : ("Alabama", (291,)),
    "AK" : ("Alaska", (6,)),
    "AB" : ("Alberta", (1,)),
    "AR" : ("Arkansas", (291,)),
    "AZ" : ("Arizona", (291,)),
    "BC" : ("British Columbia", (1,)),
    "CO" : ("Colorado", (291,)),
    "CT" : ("Connecticut", (291,)),
    "DE" : ("Delaware", (291,)),
    "EB" : ("East Bay", (291,)),
    "EMA" : ("Eastern Massachusetts", (291,)),
    "ENY" : ("Eastern New York", (291,)),
    "EPA" : ("Eastern Pennsylvania", (291,)),
    "EWA" : ("Eastern Washington", (291,)),
    "GA" : ("Georgia", (291,)),
    "GTA" : ("Greater Toronto Area", (1,)),
    "ID" : ("Idaho", (291,)),
    "IL" : ("Illinois", (291,)),
    "IN" : ("Indiana", (291,)),
    "IA" : ("Iowa", (291,)),
    "KS" : ("Kansas", (291,)),
    "KY" : ("Kentucky", (291,)),
    "LAX" : ("Los Angeles", (291,)),
    "LA" : ("Louisiana", (291,)),
    "ME" : ("Maine", (291,)),
    "MB" : ("Manitoba", (1,)),
    "MAR" : ("Maritime", (1,)),
    "MDC" : ("Maryland-DC", (291,)),
    "MI" : ("Michigan", (291,)),
    "MN" : ("Minnesota", (291,)),
    "MS" : ("Mississippi", (291,)),
    "MO" : ("Missouri", (291,)),
    "MT" : ("Montana", (291,)),
    "NE" : ("Nebraska", (291,)),
    "NV" : ("Nevada", (291,)),
    "NH" : ("New Hampshire", (291,)),
    "NM" : ("New Mexico", (291,)),
    "NLI" : ("New York City-Long Island", (291,)),
    "NL" : ("Newfoundland/Labrador", (1,)),
    "NC" : ("North Carolina", (291,)),
    "ND" : ("North Dakota", (291,)),
    "NTX" : ("North Texas", (291,)),
    "NFL" : ("Northern Florida", (291,)),
    "NNJ" : ("Northern New Jersey", (291,)),
    "NNY" : ("Northern New York", (291,)),
    "NT" : ("Northwest Territories/Yukon/Nunavut", (1,)),
    "OH" : ("Ohio", (291,)),
    "OK" : ("Oklahoma", (291,)),
    "ONE" : ("Ontario East", (1,)),
    "ONN" : ("Ontario North", (1,)),
    "ONS" : ("Ontario South", (1,)),
    "ORG" : ("Orange", (291,)),
    "OR" : ("Oregon", (291,)),
    "PAC" : ("Pacific", (9, 20, 103, 110, 123, 134, 138, 166, 174, 197, 297, 515)),
    "PR" : ("Puerto Rico", (43, 202,)),
    "QC" : ("Quebec", (1,)),
    "RI" : ("Rhode Island", (291,)),
    "SV" : ("Sacramento Valley", (291,)),
    "SDG" : ("San Diego", (291,)),
    "SF" : ("San Francisco", (291,)),
    "SJV" : ("San Joaquin Valley", (291,)),
    "SB" : ("Santa Barbara", (291,)),
    "SCV" : ("Santa Clara Valley", (291,)),
    "SK" : ("Saskatchewan", (1,)),
    "SC" : ("South Carolina", (291,)),
    "SD" : ("South Dakota", (291,)),
    "STX" : ("South Texas", (291,)),
    "SFL" : ("Southern Florida", (291,)),
    "SNJ" : ("Southern New Jersey", (291,)),
    "TN" : ("Tennessee", (291,)),
    "VI" : ("US Virgin Islands", (105, 182, 285)),
    "UT" : ("Utah", (291,)),
    "VT" : ("Vermont", (291,)),
    "VA" : ("Virginia", (291,)),
    "WCF" : ("West Central Florida", (291,)),
    "WTX" : ("West Texas", (291,)),
    "WV" : ("West Virginia", (291,)),
    "WMA" : ("Western Massachusetts", (291,)),
    "WNY" : ("Western New York", (291,)),
    "WPA" : ("Western Pennsylvania", (291,)),
    "WWA" : ("Western Washington", (291,)),
    "WI" : ("Wisconsin", (291,)),
    "WY" : ("Wyoming", (291,))
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

Mode_Enumeration = {
    "AM" : (),
    "ARDOP" : (),
    "ATV" : (),
    "CHIP" : ("CHIP64", "CHIP128"),
    "CLO" : (),
    "CONTESTI" : (),
    "CW" : ("PCW",),
    "DIGITALVOICE" : ("C4FM", "DMR", "DSTAR"),
    "DOMINO" : ("DOM-M", "DOM4", "DOM5", "DOM8", "DOM11", "DOM16", "DOM22", "DOM44", "DOM88", "DOMINOEX", "DOMINOF"),
    "DYNAMIC" : ("VARA HF", "VARA SATELLITE", "VARA FM 1200", "VARA FM 9600"),
    "FAX" : (),
    "FM" : (),
    "FSK441" : (),
    "FT8" : (),
    "HELL" : ("FMHELL", "FSKHELL", "HELL80", "HELLX5", "HELLX9", "HFSK", "PSKHELL", "SLOWHELL"),
    "ISCAT" : ("ISCAT-A", "ISCAT-B"),
    "JT4" : ("JT4A", "JT4B", "JT4C", "JT4D", "JT4E", "JT4F", "JT4G"),
    "JT6M" : (),
    "JT9" : ("JT9-1", "JT9-2", "JT9-5", "JT9-10", "JT9-30", "JT9A", "JT9B", "JT9C", "JT9D", "JT9E", "JT9E FAST", "JT9F", "JT9F FAST", "JT9G", "JT9G FAST", "JT9H", "JT9H FAST"),
    "JT44" : (),
    "JT65" : ("JT65A", "JT65B", "JT65B2", "JT65C", "JT65C2"),
    "MFSK" : ("FSQCALL", "FST4", "FST4W", "FT4", "JS8", "JTMS", "MFSK4", "MFSK8", "MFSK11", "MFSK16", "MFSK22", "MFSK31", "MFSK32", "MFSK64", "MFSK64L", "MFSK128 MFSK128L", "Q65"),
    "MSK144" : (),
    "MT63" : (),
    "OLIVIA" : ("OLIVIA 4/125", "OLIVIA 4/250", "OLIVIA 8/250", "OLIVIA 8/500", "OLIVIA 16/500", "OLIVIA 16/1000", "OLIVIA 32/1000"),
    "OPERA" : ("OPERA-BEACON", "OPERA-QSO"),
    "PAC" : ("PAC2", "PAC3", "PAC4"),
    "PAX" : ("PAX2"),
    "PKT" : (),
    "PSK" : ("8PSK125", "8PSK125F", "8PSK125FL", "8PSK250", "8PSK250F", "8PSK250FL", "8PSK500", "8PSK500F", "8PSK1000", "8PSK1000F", "8PSK1200F", "FSK31", "PSK10", "PSK31", "PSK63", "PSK63F", "PSK63RC4", "PSK63RC5", "PSK63RC10", "PSK63RC20", "PSK63RC32", "PSK125", "PSK125C12", "PSK125R", "PSK125RC10", "PSK125RC12", "PSK125RC16", "PSK125RC4", "PSK125RC5", "PSK250", "PSK250C6", "PSK250R", "PSK250RC2", "PSK250RC3", "PSK250RC5", "PSK250RC6", "PSK250RC7", "PSK500", "PSK500C2", "PSK500C4", "PSK500R", "PSK500RC2", "PSK500RC3", "PSK500RC4", "PSK800C2", "PSK800RC2", "PSK1000", "PSK1000C2", "PSK1000R", "PSK1000RC2", "PSKAM10", "PSKAM31", "PSKAM50", "PSKFEC31", "QPSK31", "QPSK63", "QPSK125", "QPSK250", "QPSK500", "SIM31"),
    "PSK2K" : (),
    "Q15" : (),
    "QRA64" : ("QRA64A", "QRA64B", "QRA64C", "QRA64D", "QRA64E"),
    "ROS" : ("ROS-EME", "ROS-HF", "ROS-MF"),
    "RTTY" : ("ASCI",),
    "RTTYM" : (),
    "SSB" : ("LSB", "USB"),
    "SSTV" : (),
    "T10" : (),
    "THOR" : ("THOR-M", "THOR4", "THOR5", "THOR8", "THOR11", "THOR16", "THOR22", "THOR25X4", "THOR50X1", "THOR50X2", "THOR100"),
    "THRB" : ("THRBX", "THRBX1", "THRBX2", "THRBX4", "THROB1", "THROB2", "THROB4"),
    "TOR" : ("AMTORFEC", "GTOR", "NAVTEX", "SITORB"),
    "V4" : (),
    "VOI" : (),
    "WINMOR" : (),
    "WSPR" : ()
    }

Subnode_Enumeration = {
    "8PSK125" : ("PSK", ""),
    "8PSK125F" : ("PSK", ""),
    "8PSK125FL" : ("PSK", ""),
    "8PSK250" : ("PSK", ""),
    "8PSK250F" : ("PSK", ""),
    "8PSK250FL" : ("PSK", ""),
    "8PSK500" : ("PSK", ""),
    "8PSK500F" : ("PSK", ""),
    "8PSK1000" : ("PSK", ""),
    "8PSK1000F" : ("PSK", ""),
    "8PSK1200F" : ("PSK", ""),
    "AMTORFEC" : ("TOR", ""),
    "ASCI" : ("RTTY", ""),
    "C4FM" : ("DIGITALVOICE", "C4FM 4-level FSK. See the Propagation_Mode enumeration section for examples of representing C4FM voice transmissions."),
    "CHIP64" : ("CHIP", ""),
    "CHIP128" : ("CHIP", ""),
    "DMR" : ("DIGITALVOICE", "Digital Mobile Radio. See the Propagation_Mode enumeration section for examples of representing DMR voice transmissions."),
    "DOM-M" : ("DOMINO", ""),
    "DOM4" : ("DOMINO", ""),
    "DOM5" : ("DOMINO", ""),
    "DOM8" : ("DOMINO", ""),
    "DOM11" : ("DOMINO", ""),
    "DOM16" : ("DOMINO", ""),
    "DOM22" : ("DOMINO", ""),
    "DOM44" : ("DOMINO", ""),
    "DOM88" : ("DOMINO", ""),
    "DOMINOEX" : ("DOMINO", ""),
    "DOMINOF" : ("DOMINO", ""),
    "DSTAR" : ("DIGITALVOICE", "Digital Smart Technologies for Amateur Radio. See the Propagation_Mode enumeration section for examples of representing DSTAR voice transmissions."),
    "FMHELL" : ("HELL", ""),
    "FSK31" : ("PSK", ""),
    "FSKHELL" : ("HELL", ""),
    "FSQCALL" : ("MFSK", "FSQCall protocol used with FSQ (Fast Simple QSO) transmission mode"),
    "FST4" : ("MFSK", "This is a digital mode supported by the WSJT-X software"),
    "FST4W" : ("MFSK", "This is a digital mode supported by the WSJT-X software that is for quasi-beacon transmissions of WSPR-style messages"),
    "FT4" : ("MFSK", "FT4 is a digital mode designed specifically for radio contesting"),
    "GTOR" : ("TOR", ""),
    "HELL80" : ("HELL", ""),
    "HELLX5" : ("HELL", ""),
    "HELLX9" : ("HELL", ""),
    "HFSK" : ("HELL", ""),
    "ISCAT-A" : ("ISCAT", ""),
    "ISCAT-B" : ("ISCAT", ""),
    "JS8" : ("MFSK", "Jordan Sherer designed 8-FSK modulation"),
    "JT4A" : ("JT4", ""),
    "JT4B" : ("JT4", ""),
    "JT4C" : ("JT4", ""),
    "JT4D" : ("JT4", ""),
    "JT4E" : ("JT4", ""),
    "JT4F" : ("JT4", ""),
    "JT4G" : ("JT4", ""),
    "JT9-1" : ("JT9", ""),
    "JT9-2" : ("JT9", ""),
    "JT9-5" : ("JT9", ""),
    "JT9-10" : ("JT9", ""),
    "JT9-30" : ("JT9", ""),
    "JT9A" : ("JT9", ""),
    "JT9B" : ("JT9", ""),
    "JT9C" : ("JT9", ""),
    "JT9D" : ("JT9", ""),
    "JT9E" : ("JT9", ""),
    "JT9E FAST" : ("JT9", ""),
    "JT9F" : ("JT9", ""),
    "JT9F FAST" : ("JT9", ""),
    "JT9G" : ("JT9", ""),
    "JT9G FAST" : ("JT9", ""),
    "JT9H" : ("JT9", ""),
    "JT9H FAST" : ("JT9", ""),
    "JT65A" : ("JT65", ""),
    "JT65B" : ("JT65", ""),
    "JT65B2" : ("JT65", ""),
    "JT65C" : ("JT65", ""),
    "JT65C2" : ("JT65", ""),
    "JTMS" : ("MFSK", ""),
    "LSB" : ("SSB", "Amplitude modulated voice telephony, lower-sideband, suppressed-carrier"),
    "MFSK4" : ("MFSK", ""),
    "MFSK8" : ("MFSK", ""),
    "MFSK11" : ("MFSK", ""),
    "MFSK16" : ("MFSK", ""),
    "MFSK22" : ("MFSK", ""),
    "MFSK31" : ("MFSK", ""),
    "MFSK32" : ("MFSK", ""),
    "MFSK64" : ("MFSK", ""),
    "MFSK64L" : ("MFSK", ""),
    "MFSK128" : ("MFSK", ""),
    "MFSK128L" : ("MFSK", ""),
    "NAVTEX" : ("TOR", ""),
    "OLIVIA 4/125" : ("OLIVIA", ""),
    "OLIVIA 4/250" : ("OLIVIA", ""),
    "OLIVIA 8/250" : ("OLIVIA", ""),
    "OLIVIA 8/500" : ("OLIVIA", ""),
    "OLIVIA 16/500" : ("OLIVIA", ""),
    "OLIVIA 16/1000" : ("OLIVIA", ""),
    "OLIVIA 32/1000" : ("OLIVIA", ""),
    "OPERA-BEACON" : ("OPERA", ""),
    "OPERA-QSO" : ("OPERA", ""),
    "PAC2" : ("PAC", ""),
    "PAC3" : ("PAC", ""),
    "PAC4" : ("PAC", ""),
    "PAX2" : ("PAX", ""),
    "PCW" : ("CW", "Coherent CW"),
    "PSK10" : ("PSK", ""),
    "PSK31" : ("PSK", ""),
    "PSK63" : ("PSK", ""),
    "PSK63F" : ("PSK", ""),
    "PSK63RC10" : ("PSK", ""),
    "PSK63RC20" : ("PSK", ""),
    "PSK63RC32" : ("PSK", ""),
    "PSK63RC4" : ("PSK", ""),
    "PSK63RC5" : ("PSK", ""),
    "PSK125" : ("PSK", ""),
    "PSK125RC10" : ("PSK", ""),
    "PSK125RC12" : ("PSK", ""),
    "PSK125RC16" : ("PSK", ""),
    "PSK125RC4" : ("PSK", ""),
    "PSK125RC5" : ("PSK", ""),
    "PSK250" : ("PSK", ""),
    "PSK250RC2" : ("PSK", ""),
    "PSK250RC3" : ("PSK", ""),
    "PSK250RC5" : ("PSK", ""),
    "PSK250RC6" : ("PSK", ""),
    "PSK250RC7" : ("PSK", ""),
    "PSK500" : ("PSK", ""),
    "PSK500RC2" : ("PSK", ""),
    "PSK500RC3" : ("PSK", ""),
    "PSK500RC4" : ("PSK", ""),
    "PSK800RC2" : ("PSK", ""),
    "PSK1000" : ("PSK", ""),
    "PSK1000RC2" : ("PSK", ""),
    "PSKAM10" : ("PSK", ""),
    "PSKAM31" : ("PSK", ""),
    "PSKAM50" : ("PSK", ""),
    "PSKFEC31" : ("PSK", ""),
    "PSKHELL" : ("HELL", ""),
    "QPSK31" : ("PSK", ""),
    "Q65" : ("MFSK", ""),
    "QPSK63" : ("PSK", ""),
    "QPSK125" : ("PSK", ""),
    "QPSK250" : ("PSK", ""),
    "QPSK500" : ("PSK", ""),
    "QRA64A" : ("QRA64", ""),
    "QRA64B" : ("QRA64", ""),
    "QRA64C" : ("QRA64", ""),
    "QRA64D" : ("QRA64", ""),
    "QRA64E" : ("QRA64", ""),
    "ROS-EME" : ("ROS", ""),
    "ROS-HF" : ("ROS", ""),
    "ROS-MF" : ("ROS", ""),
    "SIM31" : ("PSK", ""),
    "SITORB" : ("TOR", ""),
    "SLOWHELL" : ("HELL", ""),
    "THOR-M" : ("THOR", ""),
    "THOR4" : ("THOR", ""),
    "THOR5" : ("THOR", ""),
    "THOR8" : ("THOR", ""),
    "THOR11" : ("THOR", ""),
    "THOR16" : ("THOR", ""),
    "THOR22" : ("THOR", ""),
    "THOR25X4" : ("THOR", ""),
    "THOR50X1" : ("THOR", ""),
    "THOR50X2" : ("THOR", ""),
    "THOR100" : ("THOR", ""),
    "THRBX" : ("THRB", ""),
    "THRBX1" : ("THRB", ""),
    "THRBX2" : ("THRB", ""),
    "THRBX4" : ("THRB", ""),
    "THROB1" : ("THRB", ""),
    "THROB2" : ("THRB", ""),
    "THROB4" : ("THRB", ""),
    "USB" : ("SSB", "Amplitude modulated voice telephony, upper-sideband, suppressed-carrier"),
    "VARA HF" : ("DYNAMIC", "Channel adaptive high-speed modem for HF"),
    "VARA SATELLITE" : ("DYNAMIC", "Channel adaptive high-speed modem for satellite operations"),
    "VARA FM 1200" : ("DYNAMIC", "Channel adaptive high-speed modem for FM transceivers"),
    "VARA FM 9600" : ("DYNAMIC", "Channel adaptive high-speed modem for FM transceivers")
    }

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
    "NS" : ("Nova Scotia", 0, (5,), (9,)),
    "QC" : ("Québec", 0, (2, 5,), (4, 9,)),
    "ON" : ("Ontario", 0, (4,), (3, 4,)),
    "MB" : ("Manitoba", 0, (4,), (3, 4,)),
    "SK" : ("Saskatchewan", 0, (4,), (3,)),
    "AB" : ("Alberta", 0, (4,), (2,)),
    "BC" : ("British Columbia", 0, (3,), (2,)),
    "NT" : ("Northwest Territories", 0, (1, 2, 4,), (3, 4, 75,)),
    "NB" : ("New Brunswick", 0, (5,), (9,)),
    "NL" : ("Newfoundland and Labrador", 0, (2, 5,), (9,)),
    "YT" : ("Yukon", 0, (1,), (2,)),
    "PE" : ("Prince Edward Island", 0, (5,), (9,)),
    "NU" : ("Nunavut", 0, (2,), (4, 9,))
    }

Primary_Administrative_Subdivision_Enumeration_5 = {
    "001" : ("Brändö", 0, (), ()),
    "002" : ("Eckerö", 0, (), ()),
    "003" : ("Finström", 0, (), ()),
    "004" : ("Föglö", 0, (), ()),
    "005" : ("Geta", 0, (), ()),
    "006" : ("Hammarland", 0, (), ()),
    "007" : ("Jomala", 0, (), ()),
    "008" : ("Kumlinge", 0, (), ()),
    "009" : ("Kökar", 0, (), ()),
    "010" : ("Lemland", 0, (), ()),
    "011" : ("Lumparland", 0, (), ()),
    "012" : ("Maarianhamina", 0, (), ()),
    "013" : ("Saltvik", 0, (), ()),
    "014" : ("Sottunga", 0, (), ()),
    "015" : ("Sund", 0, (), ()),
    "016" : ("Vårdö", 0, (), ())
    }

Primary_Administrative_Subdivision_Enumeration_6 = {
    "AK" : ("Alaska", 0, (), ())
    }

Primary_Administrative_Subdivision_Enumeration_15 = {
    "UO" : ("Ust’-Ordynsky Autonomous Okrug - for contacts made before 2008-01-01", 174, (18,), (32,)),
    "AB" : ("Aginsky Buryatsky Autonomous Okrug - for contacts made before 2008-03-01", 175, (18,), (33,)),
    "CB" : ("Chelyabinsk (Chelyabinskaya oblast)", 165, (17,), (30,)),
    "SV" : ("Sverdlovskaya oblast", 154, (17,), (30,)),
    "PM" : ("Perm` (Permskaya oblast) - for contacts made on or after 2005-12-01", 140, (17,), (30,)),
    "PM" : ("Permskaya Kraj - for contacts made before 2005-12-01", 140, (17,), (30,)),
    "KP" : ("Komi-Permyatsky Autonomous Okrug - for contacts made before 2005-12-01", 141, (17,), (30,)),
    "TO" : ("Tomsk (Tomskaya oblast)", 158, (18,), (30,)),
    "HM" : ("Khanty-Mansyisky Autonomous Okrug", 162, (17,), (21,)),
    "YN" : ("Yamalo-Nenetsky Autonomous Okrug", 163, (17,), (21,)),
    "TN" : ("Tyumen' (Tyumenskaya oblast)", 161, (17,), (30,)),
    "OM" : ("Omsk (Omskaya oblast)", 146, (17,), (30,)),
    "NS" : ("Novosibirsk (Novosibirskaya oblast)", 145, (18,), (31,)),
    "KN" : ("Kurgan (Kurganskaya oblast)", 134, (17,), (30,)),
    "OB" : ("Orenburg (Orenburgskaya oblast)", 167, (16, 17), (30,)),
    "KE" : ("Kemerovo (Kemerovskaya oblast)", 130, (18,), (31,)),
    "BA" : ("Republic of Bashkortostan", 84, (16,), (30,)),
    "KO" : ("Republic of Komi", 90, (17,), (20,)),
    "AL" : ("Altaysky Kraj", 99, (18,), (31,)),
    "GA" : ("Republic Gorny Altay", 100, (18,), (31,)),
    "KK" : ("Krasnoyarsk (Krasnoyarsk Kraj)", 103, (18,), (32,)),
    "TM" : ("Taymyr Autonomous Okrug - for contacts made before 2007-01-01", 105, (18,), (32,)),
    "HK" : ("Khabarovsk (Khabarovsky Kraj)", 110, (19,), (34,)),
    "EA" : ("Yevreyskaya Autonomous Oblast", 111, (19,), (33,)),
    "SL" : ("Sakhalin (Sakhalinskaya oblast)", 153, (19,), (34,)),
    "EV" : ("Evenkiysky Autonomous Okrug - for contacts made before 2007-01-01", 106, (18,), (22,)),
    "MG" : ("Magadan (Magadanskaya oblast)", 138, (19,), (24,)),
    "AM" : ("Amurskaya oblast", 112, (19,), (33,)),
    "CK" : ("Chukotka Autonomous Okrug", 139, (19,), (26,)),
    "PK" : ("Primorsky Kraj", 107, (19,), (34,)),
    "BU" : ("Republic of Buryatia", 85, (18,), (32,)),
    "YA" : ("Sakha (Yakut) Republic", 98, (19,), (32,)),
    "IR" : ("Irkutsk (Irkutskaya oblast)", 124, (18,), (32,)),
    "CT" : ("Zabaykalsky Kraj - referred to as Chita (Chitinskaya oblast) before 2008-03-01", 166, (18,), (33,)),
    "HA" : ("Republic of Khakassia", 104, (18,), (32,)),
    "KY" : ("Koryaksky Autonomous Okrug - for contacts made before 2007-01-01", 129, (19,), (25,)),
    "TU" : ("Republic of Tuva", 159, (23,), (32,)),
    "KT" : ("Kamchatka (Kamchatskaya oblast)", 128, (19,), (35,))
    }

Primary_Administrative_Subdivision_Enumeration_21 = {
    "IB" : ("Baleares", 0, (), ())
    }

Primary_Administrative_Subdivision_Enumeration_27 = {
    "MI" : ("Minsk (Minskaya voblasts')", 0, (), ()),
    "BR" : ("Brest (Brestskaya voblasts')", 0, (), ()),
    "HR" : ("Grodno (Hrodzenskaya voblasts')", 0, (), ()),
    "VI" : ("Vitebsk (Vitsyebskaya voblasts')", 0, (), ()),
    "MA" : ("Mogilev (Mahilyowskaya voblasts')", 0, (), ()),
    "HO" : ("Gomel (Homyel'skaya voblasts')", 0, (), ()),
    "HM" : ("Horad Minsk", 0, (), ())
    }

Primary_Administrative_Subdivision_Enumeration_29 = {
    "GC" : ("Las Palmas", 0, (), ()),
    "TF" : ("Tenerife", 0, (), ())
    }

Primary_Administrative_Subdivision_Enumeration_32 = {
    "CE" : ("Ceuta", 0, (), ()),
    "ML" : ("Melilla", 0, (), ())
    }

Primary_Administrative_Subdivision_Enumeration_50 = {
    "COL" : ("Colima", 0, (), ()),
    "DF" : ("Distrito Federal", 0, (), ()),
    "EMX" : ("Estado de México", 0, (), ()),
    "GTO" : ("Guanajuato", 0, (), ()),
    "HGO" : ("Hidalgo", 0, (), ()),
    "JAL" : ("Jalisco", 0, (), ()),
    "MIC" : ("Michoacán de Ocampo", 0, (), ()),
    "MOR" : ("Morelos", 0, (), ()),
    "NAY" : ("Nayarit", 0, (), ()),
    "PUE" : ("Puebla", 0, (), ()),
    "QRO" : ("Querétaro de Arteaga", 0, (), ()),
    "TLX" : ("Tlaxcala", 0, (), ()),
    "VER" : ("Veracruz-Llave", 0, (), ()),
    "AGS" : ("Aguascalientes", 0, (), ()),
    "BC" : ("Baja California", 0, (), ()),
    "BCS" : ("Baja California Sur", 0, (), ()),
    "CHH" : ("Chihuahua", 0, (), ()),
    "COA" : ("Coahuila de Zaragoza", 0, (), ()),
    "DGO" : ("Durango", 0, (), ()),
    "NL" : ("Nuevo Leon", 0, (), ()),
    "SLP" : ("San Luis Potosí", 0, (), ()),
    "SIN" : ("Sinaloa", 0, (), ()),
    "SON" : ("Sonora", 0, (), ()),
    "TMS" : ("Tamaulipas", 0, (), ()),
    "ZAC" : ("Zacatecas", 0, (), ()),
    "CAM" : ("Campeche", 0, (), ()),
    "CHS" : ("Chiapas", 0, (), ()),
    "GRO" : ("Guerrero", 0, (), ()),
    "OAX" : ("Oaxaca", 0, (), ()),
    "QTR" : ("Quintana Roo", 0, (), ()),
    "TAB" : ("Tabasco", 0, (), ()),
    "YUC" : ("Yucatán", 0, (), ())
    }

Primary_Administrative_Subdivision_Enumeration_54 = {
    "SP" : ("City of St. Petersburg", 169, (16,), (29,)),
    "LO" : ("Leningradskaya oblast", 136, (16,), (29,)),
    "KL" : ("Republic of Karelia", 88, (16,), (19,)),
    "AR" : ("Arkhangelsk (Arkhangelskaya oblast)", 113, (16,), (19,)),
    "NO" : ("Nenetsky Autonomous Okrug", 114, (16,), (20,)),
    "VO" : ("Vologda (Vologodskaya oblast)", 120, (16,), (29,)),
    "NV" : ("Novgorodskaya oblast", 144, (16,), (29,)),
    "PS" : ("Pskov (Pskovskaya oblast)", 149, (16,), (29,)),
    "MU" : ("Murmansk (Murmanskaya oblast)", 143, (16,), (19,)),
    "MA" : ("City of Moscow", 170, (16,), (29,)),
    "MO" : ("Moscowskaya oblast", 142, (16,), (29,)),
    "OR" : ("Oryel (Orlovskaya oblast)", 147, (16,), (29,)),
    "LP" : ("Lipetsk (Lipetskaya oblast)", 137, (16,), (29,)),
    "TV" : ("Tver' (Tverskaya oblast)", 126, (16,), (29,)),
    "SM" : ("Smolensk (Smolenskaya oblast)", 155, (16,), (29,)),
    "YR" : ("Yaroslavl (Yaroslavskaya oblast)", 168, (16,), (29,)),
    "KS" : ("Kostroma (Kostromskaya oblast)", 132, (16,), (29,)),
    "TL" : ("Tula (Tul'skaya oblast)", 160, (16,), (29,)),
    "VR" : ("Voronezh (Voronezhskaya oblast)", 121, (16,), (29,)),
    "TB" : ("Tambov (Tambovskaya oblast)", 157, (16,), (29,)),
    "RA" : ("Ryazan' (Ryazanskaya oblast)", 151, (16,), (29,)),
    "NN" : ("Nizhni Novgorod (Nizhegorodskaya oblast)", 122, (16,), (29,)),
    "IV" : ("Ivanovo (Ivanovskaya oblast)", 123, (16,), (29,)),
    "VL" : ("Vladimir (Vladimirskaya oblast)", 119, (16,), (29,)),
    "KU" : ("Kursk (Kurskaya oblast)", 135, (16,), (29,)),
    "KG" : ("Kaluga (Kaluzhskaya oblast)", 127, (16,), (29,)),
    "BR" : ("Bryansk (Bryanskaya oblast)", 118, (16,), (29,)),
    "BO" : ("Belgorod (Belgorodskaya oblast)", 117, (16,), (29,)),
    "VG" : ("Volgograd (Volgogradskaya oblast)", 156, (16,), (29,)),
    "SA" : ("Saratov (Saratovskaya oblast)", 152, (16,), (29,)),
    "PE" : ("Penza (Penzenskaya oblast)", 148, (16,), (29,)),
    "SR" : ("Samara (Samarskaya oblast)", 133, (16,), (30,)),
    "UL" : ("Ulyanovsk (Ulyanovskaya oblast)", 164, (16,), (29,)),
    "KI" : ("Kirov (Kirovskaya oblast)", 131, (16,), (30,)),
    "TA" : ("Republic of Tataria", 94, (16,), (30,)),
    "MR" : ("Republic of Marij-El", 91, (16,), (29,)),
    "MD" : ("Republic of Mordovia", 92, (16,), (29,)),
    "UD" : ("Republic of Udmurtia", 95, (16,), (30,)),
    "CU" : ("Republic of Chuvashia", 97, (16,), (29,)),
    "KR" : ("Krasnodar (Krasnodarsky Kraj)", 101, (16,), (29,)),
    "KC" : ("Republic of Karachaevo-Cherkessia", 109, (16,), (29,)),
    "ST" : ("Stavropol' (Stavropolsky Kraj)", 108, (16,), (29,)),
    "KM" : ("Republic of Kalmykia", 89, (16,), (29,)),
    "SO" : ("Republic of Northern Ossetia", 93, (16,), (29,)),
    "RO" : ("Rostov-on-Don (Rostovskaya oblast)", 150, (16,), (29,)),
    "CN" : ("Republic Chechnya", 96, (16,), (29,)),
    "IN" : ("Republic of Ingushetia", 96, (16,), (29,)),
    "AO" : ("Astrakhan' (Astrakhanskaya oblast)", 115, (16,), (29,)),
    "DA" : ("Republic of Daghestan", 86, (16,), (29,)),
    "KB" : ("Republic of Kabardino-Balkaria", 87, (16,), (29,)),
    "AD" : ("Republic of Adygeya", 102, (16,), (29,))
    }

Primary_Administrative_Subdivision_Enumeration_61 = {
    "AR" : ("Arkhangelsk (Arkhangelskaya oblast)", 0, (), ()),
    "FJL" : ("Franz Josef Land (import-only)", 0, (), ())
    }

Primary_Administrative_Subdivision_Enumeration_100 = {
    "C" : ("Capital federal (Buenos Aires City)", 0, (), ()),
    "B" : ("Buenos Aires Province", 0, (), ()),
    "S" : ("Santa Fe", 0, (), ()),
    "H" : ("Chaco", 0, (), ()),
    "P" : ("Formosa", 0, (), ()),
    "X" : ("Cordoba", 0, (), ()),
    "N" : ("Misiones", 0, (), ()),
    "E" : ("Entre Rios", 0, (), ()),
    "T" : ("Tucumán", 0, (), ()),
    "W" : ("Corrientes", 0, (), ()),
    "M" : ("Mendoza", 0, (), ()),
    "G" : ("Santiago del Estero", 0, (), ()),
    "A" : ("Salta", 0, (), ()),
    "J" : ("San Juan", 0, (), ()),
    "D" : ("San Luis", 0, (), ()),
    "K" : ("Catamarca", 0, (), ()),
    "F" : ("La Rioja", 0, (), ()),
    "Y" : ("Jujuy", 0, (), ()),
    "L" : ("La Pampa", 0, (), ()),
    "R" : ("Rió Negro", 0, (), ()),
    "U" : ("Chubut", 0, (), ()),
    "Z" : ("Santa Cruz", 0, (), ()),
    "V" : ("Tierra del Fuego", 0, (), ()),
    "Q" : ("Neuquén", 0, (), ())
    }

Primary_Administrative_Subdivision_Enumeration_108 = {
    "ES" : ("Espírito Santo", 0, (), ()),
    "GO" : ("Goiás", 0, (), ()),
    "SC" : ("Santa Catarina", 0, (), ()),
    "SE" : ("Sergipe", 0, (), ()),
    "AL" : ("Alagoas", 0, (), ()),
    "AM" : ("Amazonas", 0, (), ()),
    "TO" : ("Tocantins", 0, (), ()),
    "AP" : ("Amapã", 0, (), ()),
    "PB" : ("Paraíba", 0, (), ()),
    "MA" : ("Maranhao", 0, (), ()),
    "RN" : ("Rio Grande do Norte", 0, (), ()),
    "PI" : ("Piaui", 0, (), ()),
    "DF" : ("Oietrito Federal (Brasila)", 0, (), ()),
    "CE" : ("Ceará", 0, (), ()),
    "AC" : ("Acre", 0, (), ()),
    "MS" : ("Mato Grosso do Sul", 0, (), ()),
    "RR" : ("Roraima", 0, (), ()),
    "RO" : ("Rondônia", 0, (), ()),
    "RJ" : ("Rio de Janeiro", 0, (), ()),
    "SP" : ("Sao Paulo", 0, (), ()),
    "RS" : ("Rio Grande do Sul", 0, (), ()),
    "MG" : ("Minas Gerais", 0, (), ()),
    "PR" : ("Paranã", 0, (), ()),
    "BA" : ("Bahia", 0, (), ()),
    "PE" : ("Pernambuco", 0, (), ()),
    "PA" : ("Parã", 0, (), ()),
    "MT" : ("Mato Grosso", 0, (), ())
    }

Primary_Administrative_Subdivision_Enumeration_110 = {
    "HI" : ("Hawaii", 0, (), ())
    }

Primary_Administrative_Subdivision_Enumeration_112 = {
    "II" : ("Antofagasta", 0, (), ()),
    "III" : ("Atacama", 0, (), ()),
    "I" : ("Tarapacá", 0, (), ()),
    "XV" : ("Arica y Parinacota", 0, (), ()),
    "IV" : ("Coquimbo", 0, (), ()),
    "V" : ("Valparaíso", 0, (), ()),
    "RM" : ("Region Metropolitana de Santiago", 0, (), ()),
    "VI" : ("Libertador General Bernardo O'Higgins", 0, (), ()),
    "VII" : ("Maule", 0, (), ()),
    "VIII" : ("Bío-Bío", 0, (), ()),
    "IX" : ("La Araucanía", 0, (), ()),
    "XIV" : ("Los Ríos", 0, (), ()),
    "X" : ("Los Lagos", 0, (), ()),
    "XI" : ("Aisén del General Carlos Ibáñez del Campo", 0, (), ()),
    "XII" : ("Magallanes", 0, (), ())
    }

Primary_Administrative_Subdivision_Enumeration_126 = {
    "KA" : ("Kalingrad (Kaliningradskaya oblast)", 125, (15,), (29,))
    }

Primary_Administrative_Subdivision_Enumeration_132 = {
    "16" : ("Alto Paraguay", 0, (), ()),
    "19" : ("Boquerón", 0, (), ()),
    "15" : ("Presidente Hayes", 0, (), ()),
    "13" : ("Amambay", 0, (), ()),
    "01" : ("Concepción", 0, (), ()),
    "14" : ("Canindeyú", 0, (), ()),
    "02" : ("San Pedro", 0, (), ()),
    "ASU" : ("Asunción", 0, (), ()),
    "11" : ("Central", 0, (), ()),
    "03" : ("Cordillera", 0, (), ()),
    "09" : ("Paraguarí", 0, (), ()),
    "06" : ("Caazapl", 0, (), ()),
    "05" : ("Caeguazú", 0, (), ()),
    "04" : ("Guairá", 0, (), ()),
    "08" : ("Miaiones", 0, (), ()),
    "12" : ("Ñeembucu", 0, (), ()),
    "10" : ("Alto Paraná", 0, (), ()),
    "07" : ("Itapua", 0, (), ())
    }

Primary_Administrative_Subdivision_Enumeration_137 = {
    "A" : ("Seoul (Seoul Teugbyeolsi)", 0, (), ()),
    "N" : ("Inchon (Incheon Gwang'yeogsi)", 0, (), ()),
    "D" : ("Kangwon-do (Gang 'weondo)", 0, (), ()),
    "C" : ("Kyunggi-do (Gyeonggido)", 0, (), ()),
    "E" : ("Choongchungbuk-do (Chungcheongbugdo)", 0, (), ()),
    "F" : ("Choongchungnam-do (Chungcheongnamdo)", 0, (), ()),
    "R" : ("Taejon (Daejeon Gwang'yeogsi)", 0, (), ()),
    "M" : ("Cheju-do (Jejudo)", 0, (), ()),
    "G" : ("Chollabuk-do (Jeonrabugdo)", 0, (), ()),
    "H" : ("Chollanam-do (Jeonranamdo)", 0, (), ()),
    "Q" : ("Kwangju (Gwangju Gwang'yeogsi)", 0, (), ()),
    "K" : ("Kyungsangbuk-do (Gyeongsangbugdo)", 0, (), ()),
    "L" : ("Kyungsangnam-do (Gyeongsangnamdo)", 0, (), ()),
    "B" : ("Pusan (Busan Gwang'yeogsi)", 0, (), ()),
    "P" : ("Taegu (Daegu Gwang'yeogsi)", 0, (), ()),
    "S" : ("Ulsan (Ulsan Gwanq'yeogsi)", 0, (), ()),
    "T" : ("Sejong", 0, (), ()),
    "IS" : ("Special Island", 0, (), ())
    }

Primary_Administrative_Subdivision_Enumeration_138 = {
    "KI" : ("Kure Island", 0, (), ())
    }

Primary_Administrative_Subdivision_Enumeration_144 = {
    "MO" : ("Montevideo", 0, (), ()),
    "CA" : ("Canelones", 0, (), ()),
    "SJ" : ("San José", 0, (), ()),
    "CO" : ("Colonia", 0, (), ()),
    "SO" : ("Soriano", 0, (), ()),
    "RN" : ("Rio Negro", 0, (), ()),
    "PA" : ("Paysandu", 0, (), ()),
    "SA" : ("Salto", 0, (), ()),
    "AR" : ("Artigsa", 0, (), ()),
    "FD" : ("Florida", 0, (), ()),
    "FS" : ("Flores", 0, (), ()),
    "DU" : ("Durazno", 0, (), ()),
    "TA" : ("Tacuarembo", 0, (), ()),
    "RV" : ("Rivera", 0, (), ()),
    "MA" : ("Maldonado", 0, (), ()),
    "LA" : ("Lavalleja", 0, (), ()),
    "RO" : ("Rocha", 0, (), ()),
    "TT" : ("Treinta y Tres", 0, (), ()),
    "CL" : ("Cerro Largo", 0, (), ())
    }

Primary_Administrative_Subdivision_Enumeration_147 = {
    "LH" : ("Lord Howe Is", 0, (), ())
    }

Primary_Administrative_Subdivision_Enumeration_148 = {
    "AM" : ("Amazonas", 0, (), ()),
    "AN" : ("Anzoátegui", 0, (), ()),
    "AP" : ("Apure", 0, (), ()),
    "AR" : ("Aragua", 0, (), ()),
    "BA" : ("Barinas", 0, (), ()),
    "BO" : ("Bolívar", 0, (), ()),
    "CA" : ("Carabobo", 0, (), ()),
    "CO" : ("Cojedes", 0, (), ()),
    "DA" : ("Delta Amacuro", 0, (), ()),
    "DC" : ("Distrito Capital", 0, (), ()),
    "FA" : ("Falcón", 0, (), ()),
    "GU" : ("Guárico", 0, (), ()),
    "LA" : ("Lara", 0, (), ()),
    "ME" : ("Mérida", 0, (), ()),
    "MI" : ("Miranda", 0, (), ()),
    "MO" : ("Monagas", 0, (), ()),
    "NE" : ("Nueva Esparta", 0, (), ()),
    "PO" : ("Portuguesa", 0, (), ()),
    "SU" : ("Sucre", 0, (), ()),
    "TA" : ("Táchira", 0, (), ()),
    "TR" : ("Trujillo", 0, (), ()),
    "VA" : ("Vargas", 0, (), ()),
    "YA" : ("Yaracuy", 0, (), ()),
    "ZU" : ("Zulia", 0, (), ())
    }

Primary_Administrative_Subdivision_Enumeration_149 = {
    "AC" : ("Açores", 0, (), ())
    }

Primary_Administrative_Subdivision_Enumeration_150 = {
    "ACT" : ("Australian Capital Territory", 0, (), ()),
    "NSW" : ("New South Wales", 0, (), ()),
    "VIC" : ("Victoria", 0, (), ()),
    "QLD" : ("Queensland", 0, (), ()),
    "SA" : ("South Australia", 0, (), ()),
    "WA" : ("Western Australia", 0, (), ()),
    "TAS" : ("Tasmania", 0, (), ()),
    "NT" : ("Northern Territory", 0, (), ())
    }

Primary_Administrative_Subdivision_Enumeration_151 = {
    "LO" : ("Leningradskaya Oblast", 0, (), ()),
    "MV" : ("Malyj Vysotskij (import-only)", 0, (), ())
    }

Primary_Administrative_Subdivision_Enumeration_153 = {
    "MA" : ("Macquarie Is", 0, (), ())
    }

Primary_Administrative_Subdivision_Enumeration_163 = {
    "NCD" : ("National Capital District (Port Moresby)", 0, (), ()),
    "CPM" : ("Central", 0, (), ()),
    "CPK" : ("Chimbu", 0, (), ()),
    "EHG" : ("Eastern Highlands", 0, (), ()),
    "EBR" : ("East New Britain", 0, (), ()),
    "ESW" : ("East Sepik", 0, (), ()),
    "EPW" : ("Enga", 0, (), ()),
    "GPK" : ("Gulf", 0, (), ()),
    "MPM" : ("Madang", 0, (), ()),
    "MRL" : ("Manus", 0, (), ()),
    "MBA" : ("Milne Bay", 0, (), ()),
    "MPL" : ("Morobe", 0, (), ()),
    "NIK" : ("New Ireland", 0, (), ()),
    "NPP" : ("Northern", 0, (), ()),
    "NSA" : ("North Solomons", 0, (), ()),
    "SAN" : ("Santaun", 0, (), ()),
    "SHM" : ("Southern Highlands", 0, (), ()),
    "WPD" : ("Western", 0, (), ()),
    "WHM" : ("Western Highlands", 0, (), ()),
    "WBR" : ("West New Britain", 0, (), ())
    }

Primary_Administrative_Subdivision_Enumeration_170 = {
    "AUK" : ("Auckland", 0, (), ()),
    "BOP" : ("Bay of Plenty", 0, (), ()),
    "NTL" : ("Northland", 0, (), ()),
    "WKO" : ("Waikato", 0, (), ()),
    "GIS" : ("Gisborne", 0, (), ()),
    "HKB" : ("Hawkes Bay", 0, (), ()),
    "MWT" : ("Manawatu-Wanganui", 0, (), ()),
    "TKI" : ("Taranaki", 0, (), ()),
    "WGN" : ("Wellington", 0, (), ()),
    "CAN" : ("Canterbury", 0, (), ()),
    "MBH" : ("Marlborough", 0, (), ()),
    "NSN" : ("Nelson", 0, (), ()),
    "TAS" : ("Tasman", 0, (), ()),
    "WTC" : ("West Coast", 0, (), ()),
    "OTA" : ("Otago", 0, (), ()),
    "STL" : ("Southland", 0, (), ())
    }

Primary_Administrative_Subdivision_Enumeration_177 = {
    "MT" : ("Minami Torishima", 0, (), ())
    }

Primary_Administrative_Subdivision_Enumeration_192 = {
    "O" : ("Ogasawara", 0, (), ())
    }

Primary_Administrative_Subdivision_Enumeration_206 = {
    "WC" : ("Wien", 0, (), ()),
    "HA" : ("Hallein", 0, (), ()),
    "JO" : ("St. Johann", 0, (), ()),
    "SC" : ("Salzburg", 0, (), ()),
    "SL" : ("Salzburg-Land", 0, (), ()),
    "TA" : ("Tamsweg", 0, (), ()),
    "ZE" : ("Zell Am See", 0, (), ()),
    "AM" : ("Amstetten", 0, (), ()),
    "BL" : ("Bruck/Leitha", 0, (), ()),
    "BN" : ("Baden", 0, (), ()),
    "GD" : ("Gmünd", 0, (), ()),
    "GF" : ("Gänserndorf", 0, (), ()),
    "HL" : ("Hollabrunn", 0, (), ()),
    "HO" : ("Horn", 0, (), ()),
    "KO" : ("Korneuburg", 0, (), ()),
    "KR" : ("Krems-Region", 0, (), ()),
    "KS" : ("Krems", 0, (), ()),
    "LF" : ("Lilienfeld", 0, (), ()),
    "MD" : ("Mödling", 0, (), ()),
    "ME" : ("Melk", 0, (), ()),
    "MI" : ("Mistelbach", 0, (), ()),
    "NK" : ("Neunkirchen", 0, (), ()),
    "PC" : ("St. Pölten", 0, (), ()),
    "PL" : ("St. Pölten-Land", 0, (), ()),
    "SB" : ("Scheibbs", 0, (), ()),
    "SW" : ("Schwechat", 0, (), ()),
    "TU" : ("Tulln", 0, (), ()),
    "WB" : ("Wr.Neustadt-Bezirk", 0, (), ()),
    "WN" : ("Wr.Neustadt", 0, (), ()),
    "WT" : ("Waidhofen/Thaya", 0, (), ()),
    "WU" : ("Wien-Umgebung", 0, (), ()),
    "WY" : ("Waidhofen/Ybbs", 0, (), ()),
    "ZT" : ("Zwettl", 0, (), ()),
    "EC" : ("Eisenstadt", 0, (), ()),
    "EU" : ("Eisenstadt-Umgebung", 0, (), ()),
    "GS" : ("Güssing", 0, (), ()),
    "JE" : ("Jennersdorf", 0, (), ()),
    "MA" : ("Mattersburg", 0, (), ()),
    "ND" : ("Neusiedl/See", 0, (), ()),
    "OP" : ("Oberpullendorf", 0, (), ()),
    "OW" : ("Oberwart", 0, (), ()),
    "BR" : ("Braunau/Inn", 0, (), ()),
    "EF" : ("Eferding", 0, (), ()),
    "FR" : ("Freistadt", 0, (), ()),
    "GM" : ("Gmunden", 0, (), ()),
    "GR" : ("Grieskirchen", 0, (), ()),
    "KI" : ("Kirchdorf", 0, (), ()),
    "LC" : ("Linz", 0, (), ()),
    "LL" : ("Linz-Land", 0, (), ()),
    "PE" : ("Perg", 0, (), ()),
    "RI" : ("Ried/Innkreis", 0, (), ()),
    "RO" : ("Rohrbach", 0, (), ()),
    "SD" : ("Schärding", 0, (), ()),
    "SE" : ("Steyr-Land", 0, (), ()),
    "SR" : ("Steyr", 0, (), ()),
    "UU" : ("Urfahr", 0, (), ()),
    "VB" : ("Vöcklabruck", 0, (), ()),
    "WE" : ("Wels", 0, (), ()),
    "WL" : ("Wels-Land", 0, (), ()),
    "BA" : ("Bad Aussee - for contacts made before 2012/01/01", 0, (), ()),
    "BM" : ("Bruck/Mur - for contacts made before 2013/01/01", 0, (), ()),
    "BM" : ("Bruck-Mürzzuschlag - for contacts made on or after 2013/01/01", 0, (), ()),
    "DL" : ("Deutschlandsberg", 0, (), ()),
    "FB" : ("Feldbach - for contacts made before 2013/01/01", 0, (), ()),
    "FF" : ("Fürstenfeld - for contacts made before 2013/01/01", 0, (), ()),
    "GB" : ("Gröbming", 0, (), ()),
    "GC" : ("Graz", 0, (), ()),
    "GU" : ("Graz-Umgebung", 0, (), ()),
    "HB" : ("Hartberg - for contacts made before 2013/01/01", 0, (), ()),
    "HF" : ("Hartberg-Fürstenfeld - for contacts made on or after 2013/01/01", 0, (), ()),
    "JU" : ("Judenburg - for contacts made before 2012/01/01", 0, (), ()),
    "KF" : ("Knittelfeld - for contacts made before 2012/01/01", 0, (), ()),
    "LB" : ("Leibnitz", 0, (), ()),
    "LE" : ("Leoben", 0, (), ()),
    "LI" : ("Liezen", 0, (), ()),
    "LN" : ("Leoben-Land", 0, (), ()),
    "MT" : ("Murtal - for contacts made on or after 2012/01/01", 0, (), ()),
    "MU" : ("Murau", 0, (), ()),
    "MZ" : ("Mürzzuschlag - for contacts made before 2013/01/01", 0, (), ()),
    "RA" : ("Radkersburg - for contacts made before 2013/01/01", 0, (), ()),
    "SO" : ("Südoststeiermark - for contacts made on or after 2013/01/01", 0, (), ()),
    "VO" : ("Voitsberg", 0, (), ()),
    "WZ" : ("Weiz", 0, (), ()),
    "IC" : ("Innsbruck", 0, (), ()),
    "IL" : ("Innsbruck-Land", 0, (), ()),
    "IM" : ("Imst", 0, (), ()),
    "KB" : ("Kitzbühel", 0, (), ()),
    "KU" : ("Kufstein", 0, (), ()),
    "LA" : ("Landeck", 0, (), ()),
    "LZ" : ("Lienz", 0, (), ()),
    "RE" : ("Reutte", 0, (), ()),
    "SZ" : ("Schwaz", 0, (), ()),
    "FE" : ("Feldkirchen", 0, (), ()),
    "HE" : ("Hermagor", 0, (), ()),
    "KC" : ("Klagenfurt", 0, (), ()),
    "KL" : ("Klagenfurt-Land", 0, (), ()),
    "SP" : ("Spittal/Drau", 0, (), ()),
    "SV" : ("St.Veit/Glan", 0, (), ()),
    "VI" : ("Villach", 0, (), ()),
    "VK" : ("Völkermarkt", 0, (), ()),
    "VL" : ("Villach-Land", 0, (), ()),
    "WO" : ("Wolfsberg", 0, (), ()),
    "BC" : ("Bregenz", 0, (), ()),
    "BZ" : ("Bludenz", 0, (), ()),
    "DO" : ("Dornbirn", 0, (), ()),
    "FK" : ("Feldkirch", 0, (), ())
    }

Primary_Administrative_Subdivision_Enumeration_209 = {
    "AN" : ("Antwerpen", 0, (), ()),
    "BR" : ("Brussels", 0, (), ()),
    "BW" : ("Brabant Wallon", 0, (), ()),
    "HT" : ("Hainaut", 0, (), ()),
    "LB" : ("Limburg", 0, (), ()),
    "LG" : ("Liêge", 0, (), ()),
    "NM" : ("Namur", 0, (), ()),
    "LU" : ("Luxembourg", 0, (), ()),
    "OV" : ("Oost-Vlaanderen", 0, (), ()),
    "VB" : ("Vlaams Brabant", 0, (), ()),
    "WV" : ("West-Vlaanderen", 0, (), ())
    }

Primary_Administrative_Subdivision_Enumeration_212 = {
    "BU" : ("Burgas", 0, (), ()),
    "SL" : ("Sliven", 0, (), ()),
    "YA" : ("Yambol (Jambol)", 0, (), ()),
    "SO" : ("Sofija Grad", 0, (), ()),
    "HA" : ("Haskovo", 0, (), ()),
    "KA" : ("Kărdžali", 0, (), ()),
    "SZ" : ("Stara Zagora", 0, (), ()),
    "PA" : ("Pazardžik", 0, (), ()),
    "PD" : ("Plovdiv", 0, (), ()),
    "SM" : ("Smoljan", 0, (), ()),
    "BL" : ("Blagoevgrad", 0, (), ()),
    "KD" : ("Kjustendil", 0, (), ()),
    "PK" : ("Pernik", 0, (), ()),
    "SF" : ("Sofija (Sofia)", 0, (), ()),
    "GA" : ("Gabrovo", 0, (), ()),
    "LV" : ("Loveč (Lovech)", 0, (), ()),
    "PL" : ("Pleven", 0, (), ()),
    "VT" : ("Veliko Tărnovo", 0, (), ()),
    "MN" : ("Montana", 0, (), ()),
    "VD" : ("Vidin", 0, (), ()),
    "VR" : ("Vraca", 0, (), ()),
    "RZ" : ("Razgrad", 0, (), ()),
    "RS" : ("Ruse", 0, (), ()),
    "SS" : ("Silistra", 0, (), ()),
    "TA" : ("Tărgovište", 0, (), ()),
    "DO" : ("Dobrič", 0, (), ()),
    "SN" : ("Šumen", 0, (), ()),
    "VN" : ("Varna", 0, (), ())
    }

Primary_Administrative_Subdivision_Enumeration_214 = {
    "2A" : ("Corse-du-Sud", 0, (), ()),
    "2B" : ("Haute-Corse", 0, (), ())
    }

Primary_Administrative_Subdivision_Enumeration_221 = {
    "015" : ("Koebenhavns amt", 0, (), ()),
    "020" : ("Frederiksborg amt", 0, (), ()),
    "025" : ("Roskilde amt", 0, (), ()),
    "030" : ("Vestsjaellands amt", 0, (), ()),
    "035" : ("Storstrøm amt (Storstroems)", 0, (), ()),
    "040" : ("Bornholms amt", 0, (), ()),
    "042" : ("Fyns amt", 0, (), ()),
    "050" : ("Sínderjylland amt (Sydjyllands)", 0, (), ()),
    "055" : ("Ribe amt", 0, (), ()),
    "060" : ("Vejle amt", 0, (), ()),
    "065" : ("Ringkøbing amt (Ringkoebing)", 0, (), ()),
    "070" : ("Århus amt (Aarhus)", 0, (), ()),
    "076" : ("Viborg amt", 0, (), ()),
    "080" : ("Nordjyllands amt", 0, (), ()),
    "101" : ("Copenhagen City", 0, (), ()),
    "147" : ("Frederiksberg", 0, (), ())
    }

Primary_Administrative_Subdivision_Enumeration_224 = {
    "100" : ("Somero", 0, (), ()),
    "102" : ("Alastaro", 0, (), ()),
    "103" : ("Askainen", 0, (), ()),
    "104" : ("Aura", 0, (), ()),
    "105" : ("Dragsfjärd", 0, (), ()),
    "106" : ("Eura", 0, (), ()),
    "107" : ("Eurajoki", 0, (), ()),
    "108" : ("Halikko", 0, (), ()),
    "109" : ("Harjavalta", 0, (), ()),
    "110" : ("Honkajoki", 0, (), ()),
    "111" : ("Houtskari", 0, (), ()),
    "112" : ("Huittinen", 0, (), ()),
    "115" : ("Iniö", 0, (), ()),
    "116" : ("Jämijärvi", 0, (), ()),
    "117" : ("Kaarina", 0, (), ()),
    "119" : ("Kankaanpää", 0, (), ()),
    "120" : ("Karinainen", 0, (), ()),
    "122" : ("Karvia", 0, (), ()),
    "123" : ("Äetsä", 0, (), ()),
    "124" : ("Kemiö", 0, (), ()),
    "126" : ("Kiikala", 0, (), ()),
    "128" : ("Kiikoinen", 0, (), ()),
    "129" : ("Kisko", 0, (), ()),
    "130" : ("Kiukainen", 0, (), ()),
    "131" : ("Kodisjoki", 0, (), ()),
    "132" : ("Kokemäki", 0, (), ()),
    "133" : ("Korppoo", 0, (), ()),
    "134" : ("Koski tl", 0, (), ()),
    "135" : ("Kullaa", 0, (), ()),
    "136" : ("Kustavi", 0, (), ()),
    "137" : ("Kuusjoki", 0, (), ()),
    "138" : ("Köyliö", 0, (), ()),
    "139" : ("Laitila", 0, (), ()),
    "140" : ("Lappi", 0, (), ()),
    "141" : ("Lavia", 0, (), ()),
    "142" : ("Lemu", 0, (), ()),
    "143" : ("Lieto", 0, (), ()),
    "144" : ("Loimaa", 0, (), ()),
    "145" : ("Loimaan kunta", 0, (), ()),
    "147" : ("Luvia", 0, (), ()),
    "148" : ("Marttila", 0, (), ()),
    "149" : ("Masku", 0, (), ()),
    "150" : ("Mellilä", 0, (), ()),
    "151" : ("Merikarvia", 0, (), ()),
    "152" : ("Merimasku", 0, (), ()),
    "154" : ("Mietoinen", 0, (), ()),
    "156" : ("Muurla", 0, (), ()),
    "157" : ("Mynämäki", 0, (), ()),
    "158" : ("Naantali", 0, (), ()),
    "159" : ("Nakkila", 0, (), ()),
    "160" : ("Nauvo", 0, (), ()),
    "161" : ("Noormarkku", 0, (), ()),
    "162" : ("Nousiainen", 0, (), ()),
    "163" : ("Oripää", 0, (), ()),
    "164" : ("Paimio", 0, (), ()),
    "165" : ("Parainen", 0, (), ()),
    "167" : ("Perniö", 0, (), ()),
    "168" : ("Pertteli", 0, (), ()),
    "169" : ("Piikkiö", 0, (), ()),
    "170" : ("Pomarkku", 0, (), ()),
    "171" : ("Pori", 0, (), ()),
    "172" : ("Punkalaidun", 0, (), ()),
    "173" : ("Pyhäranta", 0, (), ()),
    "174" : ("Pöytyä", 0, (), ()),
    "175" : ("Raisio", 0, (), ()),
    "176" : ("Rauma", 0, (), ()),
    "178" : ("Rusko", 0, (), ()),
    "179" : ("Rymättylä", 0, (), ()),
    "180" : ("Salo", 0, (), ()),
    "181" : ("Sauvo", 0, (), ()),
    "182" : ("Siikainen", 0, (), ()),
    "183" : ("Suodenniemi", 0, (), ()),
    "184" : ("Suomusjärvi", 0, (), ()),
    "185" : ("Säkylä", 0, (), ()),
    "186" : ("Särkisalo", 0, (), ()),
    "187" : ("Taivassalo", 0, (), ()),
    "188" : ("Tarvasjoki", 0, (), ()),
    "189" : ("Turku", 0, (), ()),
    "190" : ("Ulvila", 0, (), ()),
    "191" : ("Uusikaupunki", 0, (), ()),
    "192" : ("Vahto", 0, (), ()),
    "193" : ("Vammala", 0, (), ()),
    "194" : ("Vampula", 0, (), ()),
    "195" : ("Vehmaa", 0, (), ()),
    "196" : ("Velkua", 0, (), ()),
    "198" : ("Västanfjärd", 0, (), ()),
    "199" : ("Yläne", 0, (), ()),
    "201" : ("Artjärvi", 0, (), ()),
    "202" : ("Askola", 0, (), ()),
    "204" : ("Espoo", 0, (), ()),
    "205" : ("Hanko", 0, (), ()),
    "206" : ("Helsinki", 0, (), ()),
    "207" : ("Hyvinkää", 0, (), ()),
    "208" : ("Inkoo", 0, (), ()),
    "209" : ("Järvenpää", 0, (), ()),
    "210" : ("Karjaa", 0, (), ()),
    "211" : ("Karjalohja", 0, (), ()),
    "212" : ("Karkkila", 0, (), ()),
    "213" : ("Kauniainen", 0, (), ()),
    "214" : ("Kerava", 0, (), ()),
    "215" : ("Kirkkonummi", 0, (), ()),
    "216" : ("Lapinjärvi", 0, (), ()),
    "217" : ("Liljendal", 0, (), ()),
    "218" : ("Lohjan kaupunki", 0, (), ()),
    "220" : ("Loviisa", 0, (), ()),
    "221" : ("Myrskylä", 0, (), ()),
    "222" : ("Mäntsälä", 0, (), ()),
    "223" : ("Nummi-Pusula", 0, (), ()),
    "224" : ("Nurmijärvi", 0, (), ()),
    "225" : ("Orimattila", 0, (), ()),
    "226" : ("Pernaja", 0, (), ()),
    "227" : ("Pohja", 0, (), ()),
    "228" : ("Pornainen", 0, (), ()),
    "229" : ("Porvoo", 0, (), ()),
    "231" : ("Pukkila", 0, (), ()),
    "233" : ("Ruotsinpyhtää", 0, (), ()),
    "234" : ("Sammatti", 0, (), ()),
    "235" : ("Sipoo", 0, (), ()),
    "236" : ("Siuntio", 0, (), ()),
    "238" : ("Tammisaari", 0, (), ()),
    "241" : ("Tuusula", 0, (), ()),
    "242" : ("Vantaa", 0, (), ()),
    "243" : ("Vihti", 0, (), ()),
    "301" : ("Asikkala", 0, (), ()),
    "303" : ("Forssa", 0, (), ()),
    "304" : ("Hattula", 0, (), ()),
    "305" : ("Hauho", 0, (), ()),
    "306" : ("Hausjärvi", 0, (), ()),
    "307" : ("Hollola", 0, (), ()),
    "308" : ("Humppila", 0, (), ()),
    "309" : ("Hämeenlinna", 0, (), ()),
    "310" : ("Janakkala", 0, (), ()),
    "311" : ("Jokioinen", 0, (), ()),
    "312" : ("Juupajoki", 0, (), ()),
    "313" : ("Kalvola", 0, (), ()),
    "314" : ("Kangasala", 0, (), ()),
    "315" : ("Hämeenkoski", 0, (), ()),
    "316" : ("Kuhmalahti", 0, (), ()),
    "318" : ("Kuru", 0, (), ()),
    "319" : ("Kylmäkoski", 0, (), ()),
    "320" : ("Kärkölä", 0, (), ()),
    "321" : ("Lahti", 0, (), ()),
    "322" : ("Lammi", 0, (), ()),
    "323" : ("Lempäälä", 0, (), ()),
    "324" : ("Loppi", 0, (), ()),
    "325" : ("Luopioinen", 0, (), ()),
    "326" : ("Längelmäki", 0, (), ()),
    "327" : ("Mänttä", 0, (), ()),
    "328" : ("Nastola", 0, (), ()),
    "329" : ("Nokia", 0, (), ()),
    "330" : ("Orivesi", 0, (), ()),
    "331" : ("Padasjoki", 0, (), ()),
    "332" : ("Pirkkala", 0, (), ()),
    "333" : ("Pälkäne", 0, (), ()),
    "334" : ("Renko", 0, (), ()),
    "335" : ("Riihimäki", 0, (), ()),
    "336" : ("Ruovesi", 0, (), ()),
    "337" : ("Sahalahti", 0, (), ()),
    "340" : ("Tammela", 0, (), ()),
    "341" : ("Tampere", 0, (), ()),
    "342" : ("Toijala", 0, (), ()),
    "344" : ("Tuulos", 0, (), ()),
    "345" : ("Urjala", 0, (), ()),
    "346" : ("Valkeakoski", 0, (), ()),
    "347" : ("Vesilahti", 0, (), ()),
    "348" : ("Viiala", 0, (), ()),
    "349" : ("Vilppula", 0, (), ()),
    "350" : ("Virrat", 0, (), ()),
    "351" : ("Ylöjärvi", 0, (), ()),
    "352" : ("Ypäjä", 0, (), ()),
    "353" : ("Hämeenkyrö", 0, (), ()),
    "354" : ("Ikaalinen", 0, (), ()),
    "355" : ("Kihniö", 0, (), ()),
    "356" : ("Mouhijärvi", 0, (), ()),
    "357" : ("Parkano", 0, (), ()),
    "358" : ("Viljakkala", 0, (), ()),
    "402" : ("Enonkoski", 0, (), ()),
    "403" : ("Hartola", 0, (), ()),
    "404" : ("Haukivuori", 0, (), ()),
    "405" : ("Heinola", 0, (), ()),
    "407" : ("Heinävesi", 0, (), ()),
    "408" : ("Hirvensalmi", 0, (), ()),
    "409" : ("Joroinen", 0, (), ()),
    "410" : ("Juva", 0, (), ()),
    "411" : ("Jäppilä", 0, (), ()),
    "412" : ("Kangaslampi", 0, (), ()),
    "413" : ("Kangasniemi", 0, (), ()),
    "414" : ("Kerimäki", 0, (), ()),
    "415" : ("Mikkeli", 0, (), ()),
    "417" : ("Mäntyharju", 0, (), ()),
    "418" : ("Pertunmaa", 0, (), ()),
    "419" : ("Pieksämäki", 0, (), ()),
    "420" : ("Pieksänmaa", 0, (), ()),
    "421" : ("Punkaharju", 0, (), ()),
    "422" : ("Puumala", 0, (), ()),
    "423" : ("Rantasalmi", 0, (), ()),
    "424" : ("Ristiina", 0, (), ()),
    "425" : ("Savonlinna", 0, (), ()),
    "426" : ("Savonranta", 0, (), ()),
    "427" : ("Sulkava", 0, (), ()),
    "428" : ("Sysmä", 0, (), ()),
    "502" : ("Elimäki", 0, (), ()),
    "503" : ("Hamina", 0, (), ()),
    "504" : ("Iitti", 0, (), ()),
    "505" : ("Imatra", 0, (), ()),
    "506" : ("Jaala", 0, (), ()),
    "507" : ("Joutseno", 0, (), ()),
    "509" : ("Kotka", 0, (), ()),
    "510" : ("Kouvola", 0, (), ()),
    "511" : ("Kuusankoski", 0, (), ()),
    "513" : ("Lappeenranta", 0, (), ()),
    "514" : ("Lemi", 0, (), ()),
    "515" : ("Luumäki", 0, (), ()),
    "516" : ("Miehikkälä", 0, (), ()),
    "518" : ("Parikkala", 0, (), ()),
    "519" : ("Pyhtää", 0, (), ()),
    "520" : ("Rautjärvi", 0, (), ()),
    "521" : ("Ruokolahti", 0, (), ()),
    "522" : ("Saari", 0, (), ()),
    "523" : ("Savitaipale", 0, (), ()),
    "525" : ("Suomenniemi", 0, (), ()),
    "526" : ("Taipalsaari", 0, (), ()),
    "527" : ("Uukuniemi", 0, (), ()),
    "528" : ("Valkeala", 0, (), ()),
    "530" : ("Virolahti", 0, (), ()),
    "531" : ("Ylämaa", 0, (), ()),
    "532" : ("Anjalankoski", 0, (), ()),
    "601" : ("Alahärmä", 0, (), ()),
    "602" : ("Alajärvi", 0, (), ()),
    "603" : ("Alavus", 0, (), ()),
    "604" : ("Evijärvi", 0, (), ()),
    "605" : ("Halsua", 0, (), ()),
    "606" : ("Hankasalmi", 0, (), ()),
    "607" : ("Himanka", 0, (), ()),
    "608" : ("Ilmajoki", 0, (), ()),
    "609" : ("Isojoki", 0, (), ()),
    "610" : ("Isokyrö", 0, (), ()),
    "611" : ("Jalasjärvi", 0, (), ()),
    "612" : ("Joutsa", 0, (), ()),
    "613" : ("Jurva", 0, (), ()),
    "614" : ("Jyväskylä", 0, (), ()),
    "615" : ("Jyväskylän mlk", 0, (), ()),
    "616" : ("Jämsä", 0, (), ()),
    "617" : ("Jämsänkoski", 0, (), ()),
    "619" : ("Kannonkoski", 0, (), ()),
    "620" : ("Kannus", 0, (), ()),
    "621" : ("Karijoki", 0, (), ()),
    "622" : ("Karstula", 0, (), ()),
    "623" : ("Kaskinen", 0, (), ()),
    "624" : ("Kauhajoki", 0, (), ()),
    "625" : ("Kauhava", 0, (), ()),
    "626" : ("Kaustinen", 0, (), ()),
    "627" : ("Keuruu", 0, (), ()),
    "628" : ("Kinnula", 0, (), ()),
    "629" : ("Kivijärvi", 0, (), ()),
    "630" : ("Kokkola", 0, (), ()),
    "632" : ("Konnevesi", 0, (), ()),
    "633" : ("Korpilahti", 0, (), ()),
    "634" : ("Korsnäs", 0, (), ()),
    "635" : ("Kortesjärvi", 0, (), ()),
    "636" : ("Kristiinankaupunki", 0, (), ()),
    "637" : ("Kruunupyy", 0, (), ()),
    "638" : ("Kuhmoinen", 0, (), ()),
    "639" : ("Kuortane", 0, (), ()),
    "640" : ("Kurikka", 0, (), ()),
    "641" : ("Kyyjärvi", 0, (), ()),
    "642" : ("Kälviä", 0, (), ()),
    "643" : ("Laihia", 0, (), ()),
    "644" : ("Lappajärvi", 0, (), ()),
    "645" : ("Lapua", 0, (), ()),
    "646" : ("Laukaa", 0, (), ()),
    "647" : ("Lehtimäki", 0, (), ()),
    "648" : ("Leivonmäki", 0, (), ()),
    "649" : ("Lestijärvi", 0, (), ()),
    "650" : ("Lohtaja", 0, (), ()),
    "651" : ("Luhanka", 0, (), ()),
    "652" : ("Luoto", 0, (), ()),
    "653" : ("Maalahti", 0, (), ()),
    "654" : ("Maksamaa", 0, (), ()),
    "655" : ("Multia", 0, (), ()),
    "656" : ("Mustasaari", 0, (), ()),
    "657" : ("Muurame", 0, (), ()),
    "658" : ("Nurmo", 0, (), ()),
    "659" : ("Närpiö", 0, (), ()),
    "660" : ("Oravainen", 0, (), ()),
    "661" : ("Perho", 0, (), ()),
    "662" : ("Peräseinäjoki", 0, (), ()),
    "663" : ("Petäjävesi", 0, (), ()),
    "664" : ("Pietarsaari", 0, (), ()),
    "665" : ("Pedersöre", 0, (), ()),
    "666" : ("Pihtipudas", 0, (), ()),
    "668" : ("Pylkönmäki", 0, (), ()),
    "669" : ("Saarijärvi", 0, (), ()),
    "670" : ("Seinäjoki", 0, (), ()),
    "671" : ("Soini", 0, (), ()),
    "672" : ("Sumiainen", 0, (), ()),
    "673" : ("Suolahti", 0, (), ()),
    "675" : ("Teuva", 0, (), ()),
    "676" : ("Toholampi", 0, (), ()),
    "677" : ("Toivakka", 0, (), ()),
    "678" : ("Töysä", 0, (), ()),
    "679" : ("Ullava", 0, (), ()),
    "680" : ("Uurainen", 0, (), ()),
    "681" : ("Uusikaarlepyy", 0, (), ()),
    "682" : ("Vaasa", 0, (), ()),
    "683" : ("Veteli", 0, (), ()),
    "684" : ("Viitasaari", 0, (), ()),
    "685" : ("Vimpeli", 0, (), ()),
    "686" : ("Vähäkyrö", 0, (), ()),
    "687" : ("Vöyri", 0, (), ()),
    "688" : ("Ylihärmä", 0, (), ()),
    "689" : ("Ylistaro", 0, (), ()),
    "690" : ("Ähtäri", 0, (), ()),
    "692" : ("Äänekoski", 0, (), ()),
    "701" : ("Eno", 0, (), ()),
    "702" : ("Iisalmi", 0, (), ()),
    "703" : ("Ilomantsi", 0, (), ()),
    "704" : ("Joensuu", 0, (), ()),
    "705" : ("Juankoski", 0, (), ()),
    "706" : ("Juuka", 0, (), ()),
    "707" : ("Kaavi", 0, (), ()),
    "708" : ("Karttula", 0, (), ()),
    "709" : ("Keitele", 0, (), ()),
    "710" : ("Kesälahti", 0, (), ()),
    "711" : ("Kiihtelysvaara", 0, (), ()),
    "712" : ("Kitee", 0, (), ()),
    "713" : ("Kiuruvesi", 0, (), ()),
    "714" : ("Kontiolahti", 0, (), ()),
    "715" : ("Kuopio", 0, (), ()),
    "716" : ("Lapinlahti", 0, (), ()),
    "717" : ("Leppävirta", 0, (), ()),
    "718" : ("Lieksa", 0, (), ()),
    "719" : ("Liperi", 0, (), ()),
    "720" : ("Maaninka", 0, (), ()),
    "721" : ("Nilsiä", 0, (), ()),
    "722" : ("Nurmes", 0, (), ()),
    "723" : ("Outokumpu", 0, (), ()),
    "724" : ("Pielavesi", 0, (), ()),
    "725" : ("Polvijärvi", 0, (), ()),
    "726" : ("Pyhäselkä", 0, (), ()),
    "727" : ("Rautalampi", 0, (), ()),
    "728" : ("Rautavaara", 0, (), ()),
    "729" : ("Rääkkylä", 0, (), ()),
    "730" : ("Siilinjärvi", 0, (), ()),
    "731" : ("Sonkajärvi", 0, (), ()),
    "732" : ("Suonenjoki", 0, (), ()),
    "733" : ("Tervo", 0, (), ()),
    "734" : ("Tohmajärvi", 0, (), ()),
    "735" : ("Tuupovaara", 0, (), ()),
    "736" : ("Tuusniemi", 0, (), ()),
    "737" : ("Valtimo", 0, (), ()),
    "738" : ("Varkaus", 0, (), ()),
    "739" : ("Varpaisjärvi", 0, (), ()),
    "740" : ("Vehmersalmi", 0, (), ()),
    "741" : ("Vesanto", 0, (), ()),
    "742" : ("Vieremä", 0, (), ()),
    "743" : ("Värtsilä", 0, (), ()),
    "801" : ("Alavieska", 0, (), ()),
    "802" : ("Haapajärvi", 0, (), ()),
    "803" : ("Haapavesi", 0, (), ()),
    "804" : ("Hailuoto", 0, (), ()),
    "805" : ("Haukipudas", 0, (), ()),
    "806" : ("Hyrynsalmi", 0, (), ()),
    "807" : ("Ii", 0, (), ()),
    "808" : ("Kajaani", 0, (), ()),
    "810" : ("Kalajoki", 0, (), ()),
    "811" : ("Kempele", 0, (), ()),
    "812" : ("Kestilä", 0, (), ()),
    "813" : ("Kiiminki", 0, (), ()),
    "814" : ("Kuhmo", 0, (), ()),
    "815" : ("Kuivaniemi", 0, (), ()),
    "816" : ("Kuusamo", 0, (), ()),
    "817" : ("Kärsämäki", 0, (), ()),
    "818" : ("Liminka", 0, (), ()),
    "819" : ("Lumijoki", 0, (), ()),
    "820" : ("Merijärvi", 0, (), ()),
    "821" : ("Muhos", 0, (), ()),
    "822" : ("Nivala", 0, (), ()),
    "823" : ("Oulainen", 0, (), ()),
    "824" : ("Oulu", 0, (), ()),
    "825" : ("Oulunsalo", 0, (), ()),
    "826" : ("Paltamo", 0, (), ()),
    "827" : ("Pattijoki", 0, (), ()),
    "828" : ("Piippola", 0, (), ()),
    "829" : ("Pudasjärvi", 0, (), ()),
    "830" : ("Pulkkila", 0, (), ()),
    "831" : ("Puolanka", 0, (), ()),
    "832" : ("Pyhäjoki", 0, (), ()),
    "833" : ("Pyhäjärvi", 0, (), ()),
    "834" : ("Pyhäntä", 0, (), ()),
    "835" : ("Raahe", 0, (), ()),
    "836" : ("Rantsila", 0, (), ()),
    "837" : ("Reisjärvi", 0, (), ()),
    "838" : ("Ristijärvi", 0, (), ()),
    "839" : ("Ruukki", 0, (), ()),
    "840" : ("Sievi", 0, (), ()),
    "841" : ("Siikajoki", 0, (), ()),
    "842" : ("Sotkamo", 0, (), ()),
    "843" : ("Suomussalmi", 0, (), ()),
    "844" : ("Taivalkoski", 0, (), ()),
    "846" : ("Tyrnävä", 0, (), ()),
    "847" : ("Utajärvi", 0, (), ()),
    "848" : ("Vaala", 0, (), ()),
    "849" : ("Vihanti", 0, (), ()),
    "850" : ("Vuolijoki", 0, (), ()),
    "851" : ("Yli-Ii", 0, (), ()),
    "852" : ("Ylikiiminki", 0, (), ()),
    "853" : ("Ylivieska", 0, (), ()),
    "901" : ("Enontekiö", 0, (), ()),
    "902" : ("Inari", 0, (), ()),
    "903" : ("Kemi", 0, (), ()),
    "904" : ("Keminmaa", 0, (), ()),
    "905" : ("Kemijärvi", 0, (), ()),
    "907" : ("Kittilä", 0, (), ()),
    "908" : ("Kolari", 0, (), ()),
    "909" : ("Muonio", 0, (), ()),
    "910" : ("Pelkosenniemi", 0, (), ()),
    "911" : ("Pello", 0, (), ()),
    "912" : ("Posio", 0, (), ()),
    "913" : ("Ranua", 0, (), ()),
    "914" : ("Rovaniemi", 0, (), ()),
    "915" : ("Rovaniemen mlk", 0, (), ()),
    "916" : ("Salla", 0, (), ()),
    "917" : ("Savukoski", 0, (), ()),
    "918" : ("Simo", 0, (), ()),
    "919" : ("Sodankylä", 0, (), ()),
    "920" : ("Tervola", 0, (), ()),
    "921" : ("Tornio", 0, (), ()),
    "922" : ("Utsjoki", 0, (), ()),
    "923" : ("Ylitornio", 0, (), ())
    }

Primary_Administrative_Subdivision_Enumeration_225 = {
    "CA" : ("Cagliari", 0, (), ()),
    "CI" : ("Carbonia-Iglesias", 0, (), ()),
    "MD" : ("Medio Campidano (import-only)", 0, (), ()),
    "NU" : ("Nuoro", 0, (), ()),
    "OG" : ("Ogliastra", 0, (), ()),
    "OR" : ("Oristano", 0, (), ()),
    "OT" : ("Olbia-Tempio", 0, (), ()),
    "SS" : ("Sassari", 0, (), ()),
    "VS" : ("MedioCampidano", 0, (), ())
    }

Primary_Administrative_Subdivision_Enumeration_227 = {
    "01" : ("Ain", 0, (), ()),
    "02" : ("Aisne", 0, (), ()),
    "03" : ("Allier", 0, (), ()),
    "04" : ("Alpes-de-Haute-Provence", 0, (), ()),
    "05" : ("Hautes-Alpes", 0, (), ()),
    "06" : ("Alpes-Maritimes", 0, (), ()),
    "07" : ("Ardèche", 0, (), ()),
    "08" : ("Ardennes", 0, (), ()),
    "09" : ("Ariège", 0, (), ()),
    "10" : ("Aube", 0, (), ()),
    "11" : ("Aude", 0, (), ()),
    "12" : ("Aveyron", 0, (), ()),
    "13" : ("Bouches-du-Rhone", 0, (), ()),
    "14" : ("Calvados", 0, (), ()),
    "15" : ("Cantal", 0, (), ()),
    "16" : ("Charente", 0, (), ()),
    "17" : ("Charente-Maritime", 0, (), ()),
    "18" : ("Cher", 0, (), ()),
    "19" : ("Corrèze", 0, (), ()),
    "21" : ("Cote-d'Or", 0, (), ()),
    "22" : ("Cotes-d'Armor", 0, (), ()),
    "23" : ("Creuse", 0, (), ()),
    "24" : ("Dordogne", 0, (), ()),
    "25" : ("Doubs", 0, (), ()),
    "26" : ("Drôme", 0, (), ()),
    "27" : ("Eure", 0, (), ()),
    "28" : ("Eure-et-Loir", 0, (), ()),
    "29" : ("Finistère", 0, (), ()),
    "30" : ("Gard", 0, (), ()),
    "31" : ("Haute-Garonne", 0, (), ()),
    "32" : ("Gere", 0, (), ()),
    "33" : ("Gironde", 0, (), ()),
    "34" : ("Hérault", 0, (), ()),
    "35" : ("Ille-et-Vilaine", 0, (), ()),
    "36" : ("Indre", 0, (), ()),
    "37" : ("Indre-et-Loire", 0, (), ()),
    "38" : ("Isère", 0, (), ()),
    "39" : ("Jura", 0, (), ()),
    "40" : ("Landes", 0, (), ()),
    "41" : ("Loir-et-Cher", 0, (), ()),
    "42" : ("Loire", 0, (), ()),
    "43" : ("Haute-Loire", 0, (), ()),
    "44" : ("Loire-Atlantique", 0, (), ()),
    "45" : ("Loiret", 0, (), ()),
    "46" : ("Lot", 0, (), ()),
    "47" : ("Lot-et-Garonne", 0, (), ()),
    "48" : ("Lozère", 0, (), ()),
    "49" : ("Maine-et-Loire", 0, (), ()),
    "50" : ("Manche", 0, (), ()),
    "51" : ("Marne", 0, (), ()),
    "52" : ("Haute-Marne", 0, (), ()),
    "53" : ("Mayenne", 0, (), ()),
    "54" : ("Meurthe-et-Moselle", 0, (), ()),
    "55" : ("Meuse", 0, (), ()),
    "56" : ("Morbihan", 0, (), ()),
    "57" : ("Moselle", 0, (), ()),
    "58" : ("Niëvre", 0, (), ()),
    "59" : ("Nord", 0, (), ()),
    "60" : ("Oise", 0, (), ()),
    "61" : ("Orne", 0, (), ()),
    "62" : ("Pas-de-Calais", 0, (), ()),
    "63" : ("Puy-de-Dôme", 0, (), ()),
    "64" : ("Pyrénées-Atlantiques", 0, (), ()),
    "65" : ("Hautea-Pyrénées", 0, (), ()),
    "66" : ("Pyrénées-Orientales", 0, (), ()),
    "67" : ("Bas-Rhin", 0, (), ()),
    "68" : ("Haut-Rhin", 0, (), ()),
    "69" : ("Rhône", 0, (), ()),
    "70" : ("Haute-Saône", 0, (), ()),
    "71" : ("Saône-et-Loire", 0, (), ()),
    "72" : ("Sarthe", 0, (), ()),
    "73" : ("Savoie", 0, (), ()),
    "74" : ("Haute-Savoie", 0, (), ()),
    "75" : ("Paris", 0, (), ()),
    "76" : ("Seine-Maritime", 0, (), ()),
    "77" : ("Seine-et-Marne", 0, (), ()),
    "78" : ("Yvelines", 0, (), ()),
    "79" : ("Deux-Sèvres", 0, (), ()),
    "80" : ("Somme", 0, (), ()),
    "81" : ("Tarn", 0, (), ()),
    "82" : ("Tarn-et-Garonne", 0, (), ()),
    "83" : ("Var", 0, (), ()),
    "84" : ("Vaucluse", 0, (), ()),
    "85" : ("Vendée", 0, (), ()),
    "86" : ("Vienne", 0, (), ()),
    "87" : ("Haute-Vienne", 0, (), ()),
    "88" : ("Vosges", 0, (), ()),
    "89" : ("Yonne", 0, (), ()),
    "90" : ("Territoire de Belfort", 0, (), ()),
    "91" : ("Essonne", 0, (), ()),
    "92" : ("Hauts-de-Selne", 0, (), ()),
    "93" : ("Seine-Saint-Denis", 0, (), ()),
    "94" : ("Val-de-Marne", 0, (), ()),
    "95" : ("Val-d'Oise", 0, (), ())
    }

Primary_Administrative_Subdivision_Enumeration_230 = {
    "BB" : ("Brandenburg", 0, (), ()),
    "BE" : ("Berlin", 0, (), ()),
    "BW" : ("Baden-Württemberg", 0, (), ()),
    "BY" : ("Freistaat Bayern", 0, (), ()),
    "HB" : ("Freie Hansestadt Bremen", 0, (), ()),
    "HE" : ("Hessen", 0, (), ()),
    "HH" : ("Freie und Hansestadt Hamburg", 0, (), ()),
    "MV" : ("Mecklenburg-Vorpommern", 0, (), ()),
    "NI" : ("Niedersachsen", 0, (), ()),
    "NW" : ("Nordrhein-Westfalen", 0, (), ()),
    "RP" : ("Rheinland-Pfalz", 0, (), ()),
    "SL" : ("Saarland", 0, (), ()),
    "SH" : ("Schleswig-Holstein", 0, (), ()),
    "SN" : ("Freistaat Sachsen", 0, (), ()),
    "ST" : ("Sachsen-Anhalt", 0, (), ()),
    "TH" : ("Freistaat Thüringen", 0, (), ())
    }

Primary_Administrative_Subdivision_Enumeration_239 = {
    "GY" : ("Gyõr (Gyõr-Moson-Sopron)", 0, (), ()),
    "VA" : ("Vas", 0, (), ()),
    "ZA" : ("Zala", 0, (), ()),
    "KO" : ("Komárom (Komárom-Esztergom)", 0, (), ()),
    "VE" : ("Veszprém", 0, (), ()),
    "BA" : ("Baranya", 0, (), ()),
    "SO" : ("Somogy", 0, (), ()),
    "TO" : ("Tolna", 0, (), ()),
    "FE" : ("Fejér", 0, (), ()),
    "BP" : ("Budapest", 0, (), ()),
    "HE" : ("Heves", 0, (), ()),
    "NG" : ("Nógrád", 0, (), ()),
    "PE" : ("Pest", 0, (), ()),
    "SZ" : ("Szolnok (Jász-Nagykun-Szolnok)", 0, (), ()),
    "BE" : ("Békés", 0, (), ()),
    "BN" : ("Bács-Kiskun", 0, (), ()),
    "CS" : ("Csongrád", 0, (), ()),
    "BO" : ("Borsod (Borsod-Abaúj-Zemplén)", 0, (), ()),
    "HB" : ("Hajdú-Bihar", 0, (), ()),
    "SA" : ("Szabolcs (Szabolcs-Szatmár-Bereg)", 0, (), ())
    }

Primary_Administrative_Subdivision_Enumeration_245 = {
    "CW" : ("Carlow (Ceatharlach)", 0, (), ()),
    "CN" : ("Cavan (An Cabhán)", 0, (), ()),
    "CE" : ("Clare (An Clár)", 0, (), ()),
    "C" : ("Cork (Corcaigh)", 0, (), ()),
    "DL" : ("Donegal (Dún na nGall)", 0, (), ()),
    "D" : ("Dublin (Baile Áth Cliath)", 0, (), ()),
    "G" : ("Galway (Gaillimh)", 0, (), ()),
    "KY" : ("Kerry (Ciarraí)", 0, (), ()),
    "KE" : ("Kildare (Cill Dara)", 0, (), ()),
    "KK" : ("Kilkenny (Cill Chainnigh)", 0, (), ()),
    "LS" : ("Laois (Laois)", 0, (), ()),
    "LM" : ("Leitrim (Liatroim)", 0, (), ()),
    "LK" : ("Limerick (Luimneach)", 0, (), ()),
    "LD" : ("Longford (An Longfort)", 0, (), ()),
    "LH" : ("Louth (Lú)", 0, (), ()),
    "MO" : ("Mayo (Maigh Eo)", 0, (), ()),
    "MH" : ("Meath (An Mhí)", 0, (), ()),
    "MN" : ("Monaghan (Muineachán)", 0, (), ()),
    "OY" : ("Offaly (Uíbh Fhailí)", 0, (), ()),
    "RN" : ("Roscommon (Ros Comáin)", 0, (), ()),
    "SO" : ("Sligo (Sligeach)", 0, (), ()),
    "TA" : ("Tipperary (Tiobraid Árann)", 0, (), ()),
    "WD" : ("Waterford (Port Láirge)", 0, (), ()),
    "WH" : ("Westmeath (An Iarmhí)", 0, (), ()),
    "WX" : ("Wexford (Loch Garman)", 0, (), ()),
    "WW" : ("Wicklow (Cill Mhantáin)", 0, (), ())
    }

Primary_Administrative_Subdivision_Enumeration_248 = {
    "GE" : ("Genova", 0, (), ()),
    "IM" : ("Imperia", 0, (), ()),
    "SP" : ("La Spezia", 0, (), ()),
    "SV" : ("Savona", 0, (), ()),
    "AL" : ("Alessandria", 0, (), ()),
    "AT" : ("Asti", 0, (), ()),
    "BI" : ("Biella", 0, (), ()),
    "CN" : ("Cuneo", 0, (), ()),
    "NO" : ("Novara", 0, (), ()),
    "TO" : ("Torino", 0, (), ()),
    "VB" : ("Verbano Cusio Ossola", 0, (), ()),
    "VC" : ("Vercelli", 0, (), ()),
    "AO" : ("Aosta", 0, (), ()),
    "BG" : ("Bergamo", 0, (), ()),
    "BS" : ("Brescia", 0, (), ()),
    "CO" : ("Como", 0, (), ()),
    "CR" : ("Cremona", 0, (), ()),
    "LC" : ("Lecco", 0, (), ()),
    "LO" : ("Lodi", 0, (), ()),
    "MB" : ("Monza e Brianza", 0, (), ()),
    "MN" : ("Mantova", 0, (), ()),
    "MI" : ("Milano", 0, (), ()),
    "PV" : ("Pavia", 0, (), ()),
    "SO" : ("Sondrio", 0, (), ()),
    "VA" : ("Varese", 0, (), ()),
    "BL" : ("Belluno", 0, (), ()),
    "PD" : ("Padova", 0, (), ()),
    "RO" : ("Rovigo", 0, (), ()),
    "TV" : ("Treviso", 0, (), ()),
    "VE" : ("Venezia", 0, (), ()),
    "VR" : ("Verona", 0, (), ()),
    "VI" : ("Vicenza", 0, (), ()),
    "BZ" : ("Bolzano", 0, (), ()),
    "TN" : ("Trento", 0, (), ()),
    "GO" : ("Gorizia", 0, (), ()),
    "PN" : ("Pordenone", 0, (), ()),
    "TS" : ("Trieste", 0, (), ()),
    "UD" : ("Udine", 0, (), ()),
    "BO" : ("Bologna", 0, (), ()),
    "FE" : ("Ferrara", 0, (), ()),
    "FO" : ("Forlì (import-only)", 0, (), ()),
    "FC" : ("Forlì-Cesena", 0, (), ()),
    "MO" : ("Modena", 0, (), ()),
    "PR" : ("Parma", 0, (), ()),
    "PC" : ("Piacenza", 0, (), ()),
    "RA" : ("Ravenna", 0, (), ()),
    "RE" : ("Reggio Emilia", 0, (), ()),
    "RN" : ("Rimini", 0, (), ()),
    "AR" : ("Arezzo", 0, (), ()),
    "FI" : ("Firenze", 0, (), ()),
    "GR" : ("Grosseto", 0, (), ()),
    "LI" : ("Livorno", 0, (), ()),
    "LU" : ("Lucca", 0, (), ()),
    "MS" : ("Massa Carrara", 0, (), ()),
    "PT" : ("Pistoia", 0, (), ()),
    "PI" : ("Pisa", 0, (), ()),
    "PO" : ("Prato", 0, (), ()),
    "SI" : ("Siena", 0, (), ()),
    "CH" : ("Chieti", 0, (), ()),
    "AQ" : ("L'Aquila", 0, (), ()),
    "PE" : ("Pescara", 0, (), ()),
    "TE" : ("Teramo", 0, (), ()),
    "AN" : ("Ancona", 0, (), ()),
    "AP" : ("Ascoli Piceno", 0, (), ()),
    "FM" : ("Fermo", 0, (), ()),
    "MC" : ("Macerata", 0, (), ()),
    "PS" : ("Pesaro e Urbino (import-only)", 0, (), ()),
    "PU" : ("Pesaro e Urbino", 0, (), ()),
    "MT" : ("Matera", 0, (), ()),
    "PZ" : ("Potenza", 0, (), ()),
    "BA" : ("Bari", 0, (), ()),
    "BT" : ("Barletta-Andria-Trani", 0, (), ()),
    "BR" : ("Brindisi", 0, (), ()),
    "FG" : ("Foggia", 0, (), ()),
    "LE" : ("Lecce", 0, (), ()),
    "TA" : ("Taranto", 0, (), ()),
    "CZ" : ("Catanzaro", 0, (), ()),
    "CS" : ("Cosenza", 0, (), ()),
    "KR" : ("Crotone", 0, (), ()),
    "RC" : ("Reggio Calabria", 0, (), ()),
    "VV" : ("Vibo Valentia", 0, (), ()),
    "AV" : ("Avellino", 0, (), ()),
    "BN" : ("Benevento", 0, (), ()),
    "CE" : ("Caserta", 0, (), ()),
    "NA" : ("Napoli", 0, (), ()),
    "SA" : ("Salerno", 0, (), ()),
    "IS" : ("Isernia", 0, (), ()),
    "CB" : ("Campobasso", 0, (), ()),
    "FR" : ("Frosinone", 0, (), ()),
    "LT" : ("Latina", 0, (), ()),
    "RI" : ("Rieti", 0, (), ()),
    "RM" : ("Roma", 0, (), ()),
    "VT" : ("Viterbo", 0, (), ()),
    "PG" : ("Perugia", 0, (), ()),
    "TR" : ("Terni", 0, (), ()),
    "AG" : ("Agrigento", 0, (), ()),
    "CL" : ("Caltanissetta", 0, (), ()),
    "CT" : ("Catania", 0, (), ()),
    "EN" : ("Enna", 0, (), ()),
    "ME" : ("Messina", 0, (), ()),
    "PA" : ("Palermo", 0, (), ()),
    "RG" : ("Ragusa", 0, (), ()),
    "SR" : ("Siracusa", 0, (), ()),
    "TP" : ("Trapani", 0, (), ())
    }

Primary_Administrative_Subdivision_Enumeration_256 = {
    "MD" : ("Madeira", 0, (), ())
    }

Primary_Administrative_Subdivision_Enumeration_263 = {
    "DR" : ("Drenthe", 0, (), ()),
    "FR" : ("Friesland", 0, (), ()),
    "GR" : ("Groningen", 0, (), ()),
    "NB" : ("Noord-Brabant", 0, (), ()),
    "OV" : ("Overijssel", 0, (), ()),
    "ZH" : ("Zuid-Holland", 0, (), ()),
    "FL" : ("Flevoland", 0, (), ()),
    "GD" : ("Gelderland", 0, (), ()),
    "LB" : ("Limburg", 0, (), ()),
    "NH" : ("Noord-Holland", 0, (), ()),
    "UT" : ("Utrecht", 0, (), ()),
    "ZL" : ("Zeeland", 0, (), ())
    }

Primary_Administrative_Subdivision_Enumeration_269 = {
    "Z" : ("Zachodnio-Pomorskie", 0, (), ()),
    "F" : ("Pomorskie", 0, (), ()),
    "P" : ("Kujawsko-Pomorskie", 0, (), ()),
    "B" : ("Lubuskie", 0, (), ()),
    "W" : ("Wielkopolskie", 0, (), ()),
    "J" : ("Warminsko-Mazurskie", 0, (), ()),
    "O" : ("Podlaskie", 0, (), ()),
    "R" : ("Mazowieckie", 0, (), ()),
    "D" : ("Dolnoslaskie", 0, (), ()),
    "U" : ("Opolskie", 0, (), ()),
    "C" : ("Lodzkie", 0, (), ()),
    "S" : ("Swietokrzyskie", 0, (), ()),
    "K" : ("Podkarpackie", 0, (), ()),
    "L" : ("Lubelskie", 0, (), ()),
    "G" : ("Slaskie", 0, (), ()),
    "M" : ("Malopolskie", 0, (), ())
    }

Primary_Administrative_Subdivision_Enumeration_272 = {
    "AV" : ("Aveiro", 0, (), ()),
    "BJ" : ("Beja", 0, (), ()),
    "BR" : ("Braga", 0, (), ()),
    "BG" : ("Bragança", 0, (), ()),
    "CB" : ("Castelo Branco", 0, (), ()),
    "CO" : ("Coimbra", 0, (), ()),
    "EV" : ("Evora", 0, (), ()),
    "FR" : ("Faro", 0, (), ()),
    "GD" : ("Guarda", 0, (), ()),
    "LR" : ("Leiria", 0, (), ()),
    "LX" : ("Lisboa", 0, (), ()),
    "PG" : ("Portalegre", 0, (), ()),
    "PT" : ("Porto", 0, (), ()),
    "SR" : ("Santarem", 0, (), ()),
    "ST" : ("Setubal", 0, (), ()),
    "VC" : ("Viana do Castelo", 0, (), ()),
    "VR" : ("Vila Real", 0, (), ()),
    "VS" : ("Viseu", 0, (), ())
    }

Primary_Administrative_Subdivision_Enumeration_275 = {
    "AR" : ("Arad", 0, (), ()),
    "CS" : ("Cara'-Severin", 0, (), ()),
    "HD" : ("Hunedoara", 0, (), ()),
    "TM" : ("Timiş (Timis)", 0, (), ()),
    "BU" : ("Bucureşti (Bucure'ti)", 0, (), ()),
    "IF" : ("Ilfov", 0, (), ()),
    "BR" : ("Brăila (Braila)", 0, (), ()),
    "CT" : ("Conatarta", 0, (), ()),
    "GL" : ("Galati", 0, (), ()),
    "TL" : ("Tulcea", 0, (), ()),
    "VN" : ("Vrancea", 0, (), ()),
    "AB" : ("Alba", 0, (), ()),
    "BH" : ("Bihor", 0, (), ()),
    "BN" : ("Bistrita-Nasaud", 0, (), ()),
    "CJ" : ("Cluj", 0, (), ()),
    "MM" : ("Maramureş (Maramures)", 0, (), ()),
    "SJ" : ("Sălaj (Salaj)", 0, (), ()),
    "SM" : ("Satu Mare", 0, (), ()),
    "BV" : ("Braşov (Bra'ov)", 0, (), ()),
    "CV" : ("Covasna", 0, (), ()),
    "HR" : ("Harghita", 0, (), ()),
    "MS" : ("Mureş (Mures)", 0, (), ()),
    "SB" : ("Sibiu", 0, (), ()),
    "AG" : ("Arge'", 0, (), ()),
    "DJ" : ("Dolj", 0, (), ()),
    "GJ" : ("Gorj", 0, (), ()),
    "MH" : ("Mehedinţi (Mehedinti)", 0, (), ()),
    "OT" : ("Olt", 0, (), ()),
    "VL" : ("Vâlcea", 0, (), ()),
    "BC" : ("Bacau", 0, (), ()),
    "BT" : ("Boto'ani", 0, (), ()),
    "IS" : ("Iaşi (Iasi)", 0, (), ()),
    "NT" : ("Neamţ (Neamt)", 0, (), ()),
    "SV" : ("Suceava", 0, (), ()),
    "VS" : ("Vaslui", 0, (), ()),
    "BZ" : ("Buzău (Buzau)", 0, (), ()),
    "CL" : ("Călăraşi (Calarasi)", 0, (), ()),
    "DB" : ("Dâmboviţa (Dambovita)", 0, (), ()),
    "GR" : ("Giurqiu", 0, (), ()),
    "IL" : ("Ialomita", 0, (), ()),
    "PH" : ("Prahova", 0, (), ()),
    "TR" : ("Teleorman", 0, (), ())
    }

Primary_Administrative_Subdivision_Enumeration_281 = {
    "AV" : ("Avila", 0, (), ()),
    "BU" : ("Burgos", 0, (), ()),
    "C" : ("A Coruña", 0, (), ()),
    "LE" : ("Leon", 0, (), ()),
    "LO" : ("La Rioja", 0, (), ()),
    "LU" : ("Lugo", 0, (), ()),
    "O" : ("Asturias", 0, (), ()),
    "OU" : ("Ourense", 0, (), ()),
    "P" : ("Palencia", 0, (), ()),
    "PO" : ("Pontevedra", 0, (), ()),
    "S" : ("Cantabria", 0, (), ()),
    "SA" : ("Salamanca", 0, (), ()),
    "SG" : ("Segovia", 0, (), ()),
    "SO" : ("Soria", 0, (), ()),
    "VA" : ("Valladolid", 0, (), ()),
    "ZA" : ("Zamora", 0, (), ()),
    "BI" : ("Vizcaya", 0, (), ()),
    "HU" : ("Huesca", 0, (), ()),
    "NA" : ("Navarra", 0, (), ()),
    "SS" : ("Guipuzcoa", 0, (), ()),
    "TE" : ("Teruel", 0, (), ()),
    "VI" : ("Alava", 0, (), ()),
    "Z" : ("Zaragoza", 0, (), ()),
    "B" : ("Barcelona", 0, (), ()),
    "GI" : ("Girona", 0, (), ()),
    "L" : ("Lleida", 0, (), ()),
    "T" : ("Tarragona", 0, (), ()),
    "BA" : ("Badajoz", 0, (), ()),
    "CC" : ("Caceres", 0, (), ()),
    "CR" : ("Ciudad Real", 0, (), ()),
    "CU" : ("Cuenca", 0, (), ()),
    "GU" : ("Guadalajara", 0, (), ()),
    "M" : ("Madrid", 0, (), ()),
    "TO" : ("Toledo", 0, (), ()),
    "A" : ("Alicante", 0, (), ()),
    "AB" : ("Albacete", 0, (), ()),
    "CS" : ("Castellon", 0, (), ()),
    "MU" : ("Murcia", 0, (), ()),
    "V" : ("Valencia", 0, (), ()),
    "AL" : ("Almeria", 0, (), ()),
    "CA" : ("Cadiz", 0, (), ()),
    "CO" : ("Cordoba", 0, (), ()),
    "GR" : ("Granada", 0, (), ()),
    "H" : ("Huelva", 0, (), ()),
    "J" : ("Jaen", 0, (), ()),
    "MA" : ("Malaga", 0, (), ()),
    "SE" : ("Sevilla", 0, (), ())
    }

Primary_Administrative_Subdivision_Enumeration_284 = {
    "AB" : ("Stockholm län", 0, (), ()),
    "I" : ("Gotlands län", 0, (), ()),
    "BD" : ("Norrbottens län", 0, (), ()),
    "AC" : ("Västerbottens län", 0, (), ()),
    "X" : ("Gävleborgs län", 0, (), ()),
    "Z" : ("Jämtlands län", 0, (), ()),
    "Y" : ("Västernorrlands län", 0, (), ()),
    "W" : ("Dalarna län", 0, (), ()),
    "S" : ("Värmlands län", 0, (), ()),
    "O" : ("Västra Götalands län", 0, (), ()),
    "T" : ("Örebro län", 0, (), ()),
    "E" : ("Östergötlands län", 0, (), ()),
    "D" : ("Södermanlands län", 0, (), ()),
    "C" : ("Uppsala län", 0, (), ()),
    "U" : ("Västmanlands län", 0, (), ()),
    "N" : ("Hallands län", 0, (), ()),
    "K" : ("Blekinge län", 0, (), ()),
    "F" : ("Jönköpings län", 0, (), ()),
    "H" : ("Kalmar län", 0, (), ()),
    "G" : ("Kronobergs län", 0, (), ()),
    "M" : ("Skåne län", 0, (), ())
    }

Primary_Administrative_Subdivision_Enumeration_287 = {
    "AG" : ("Aargau", 0, (), ()),
    "AR" : ("Appenzell Ausserrhoden", 0, (), ()),
    "AI" : ("Appenzell Innerrhoden", 0, (), ()),
    "BL" : ("Basel Landschaft", 0, (), ()),
    "BS" : ("Basel Stadt", 0, (), ()),
    "BE" : ("Bern", 0, (), ()),
    "FR" : ("Freiburg / Fribourg", 0, (), ()),
    "GE" : ("Genf / Genève", 0, (), ()),
    "GL" : ("Glarus", 0, (), ()),
    "GR" : ("Graubuenden / Grisons", 0, (), ()),
    "JU" : ("Jura", 0, (), ()),
    "LU" : ("Luzern", 0, (), ()),
    "NE" : ("Neuenburg / Neuchâtel", 0, (), ()),
    "NW" : ("Nidwalden", 0, (), ()),
    "OW" : ("Obwalden", 0, (), ()),
    "SH" : ("Schaffhausen", 0, (), ()),
    "SZ" : ("Schwyz", 0, (), ()),
    "SO" : ("Solothurn", 0, (), ()),
    "SG" : ("St. Gallen", 0, (), ()),
    "TI" : ("Tessin / Ticino", 0, (), ()),
    "TG" : ("Thurgau", 0, (), ()),
    "UR" : ("Uri", 0, (), ()),
    "VD" : ("Waadt / Vaud", 0, (), ()),
    "VS" : ("Wallis / Valais", 0, (), ()),
    "ZH" : ("Zuerich", 0, (), ()),
    "ZG" : ("Zug", 0, (), ())
    }

Primary_Administrative_Subdivision_Enumeration_288 = {
    "SU" : ("Sums'ka Oblast'", 0, (), ()),
    "TE" : ("Ternopil's'ka Oblast'", 0, (), ()),
    "CH" : ("Cherkas'ka Oblast'", 0, (), ()),
    "ZA" : ("Zakarpats'ka Oblast'", 0, (), ()),
    "DN" : ("Dnipropetrovs'ka Oblast'", 0, (), ()),
    "OD" : ("Odes'ka Oblast'", 0, (), ()),
    "HE" : ("Khersons'ka Oblast'", 0, (), ()),
    "PO" : ("Poltavs'ka Oblast'", 0, (), ()),
    "DO" : ("Donets'ka Oblast'", 0, (), ()),
    "RI" : ("Rivnens'ka Oblast'", 0, (), ()),
    "HA" : ("Kharkivs'ka Oblast'", 0, (), ()),
    "LU" : ("Luhans'ka Oblast'", 0, (), ()),
    "VI" : ("Vinnyts'ka Oblast'", 0, (), ()),
    "VO" : ("Volyos'ka Oblast'", 0, (), ()),
    "ZP" : ("Zaporiz'ka Oblast'", 0, (), ()),
    "CR" : ("Chernihivs'ka Oblast'", 0, (), ()),
    "IF" : ("Ivano-Frankivs'ka Oblast'", 0, (), ()),
    "HM" : ("Khmel'nyts'ka Oblast'", 0, (), ()),
    "KV" : ("Kyïv", 0, (), ()),
    "KO" : ("Kyivs'ka Oblast'", 0, (), ()),
    "KI" : ("Kirovohrads'ka Oblast'", 0, (), ()),
    "LV" : ("L'vivs'ka Oblast'", 0, (), ()),
    "ZH" : ("Zhytomyrs'ka Oblast'", 0, (), ()),
    "CN" : ("Chernivets'ka Oblast'", 0, (), ()),
    "NI" : ("Mykolaivs'ka Oblast'", 0, (), ()),
    "KR" : ("Respublika Krym", 0, (), ()),
    "SL" : ("Sevastopol'", 0, (), ())
    }

Primary_Administrative_Subdivision_Enumeration_291 = {
    "CT" : ("Connecticut", 0, (5,), (8,)),
    "ME" : ("Maine", 0, (5,), (8,)),
    "MA" : ("Massachusetts", 0, (5,), (8,)),
    "NH" : ("New Hampshire", 0, (5,), (8,)),
    "RI" : ("Rhode Island", 0, (5,), (8,)),
    "VT" : ("Vermont", 0, (5,), (8,)),
    "NJ" : ("New Jersey", 0, (5,), (8,)),
    "NY" : ("New York", 0, (5,), (8,)),
    "DE" : ("Delaware", 0, (5,), (8,)),
    "DC" : ("District of Columbia", 0, (5,), (8,)),
    "MD" : ("Maryland", 0, (5,), (8,)),
    "PA" : ("Pennsylvania", 0, (5,), (8,)),
    "AL" : ("Alabama", 0, (4,), (8,)),
    "FL" : ("Florida", 0, (5,), (8,)),
    "GA" : ("Georgia", 0, (5,), (8,)),
    "KY" : ("Kentucky", 0, (4,), (8,)),
    "NC" : ("North Carolina", 0, (4,), (8,)),
    "SC" : ("South Carolina", 0, (5,), (8,)),
    "TN" : ("Tennessee", 0, (4,), (7, 8,)),
    "VA" : ("Virginia", 0, (5,), (8,)),
    "AR" : ("Arkansas", 0, (4,), (7, 8,)),
    "LA" : ("Louisiana", 0, (4,), (7, 8,)),
    "MS" : ("Mississippi", 0, (4,), (7, 8,)),
    "NM" : ("New Mexico", 0, (4,), (7,)),
    "OK" : ("Oklahoma", 0, (4,), (7,)),
    "TX" : ("Texas", 0, (4,), (7,)),
    "CA" : ("California", 0, (3,), (6,)),
    "AZ" : ("Arizona", 0, (3,), (6, 7,)),
    "ID" : ("Idaho", 0, (3,), (6,)),
    "MT" : ("Montana", 0, (4,), (6, 7,)),
    "NV" : ("Nevada", 0, (3,), (6,)),
    "OR" : ("Oregon", 0, (3,), (6,)),
    "UT" : ("Utah", 0, (3,), (6, 7,)),
    "WA" : ("Washington", 0, (3,), (6,)),
    "WY" : ("Wyoming", 0, (4,), (7,)),
    "MI" : ("Michigan", 0, (4,), (7, 8,)),
    "OH" : ("Ohio", 0, (4,), (8,)),
    "WV" : ("West Virginia", 0, (5,), (8,)),
    "IL" : ("Illinois", 0, (4,), (7, 8,)),
    "IN" : ("Indiana", 0, (4,), (8,)),
    "WI" : ("Wisconsin", 0, (4,), (7, 8,)),
    "CO" : ("Colorado", 0, (4,), (7,)),
    "IA" : ("Iowa", 0, (4,), (7,)),
    "KS" : ("Kansas", 0, (4,), (7,)),
    "MN" : ("Minnesota", 0, (4,), (7, 8,)),
    "MO" : ("Missouri", 0, (4,), (7, 8,)),
    "NE" : ("Nebraska", 0, (4,), (7,)),
    "ND" : ("North Dakota", 0, (4,), (7,)),
    "SD" : ("South Dakota", 0, (4,), (7,))
    }

Primary_Administrative_Subdivision_Enumeration_318 = {
    "AH" : ("Anhui", 0, (), ()),
    "BJ" : ("Beijing", 0, (), ()),
    "CQ" : ("Chongqing", 0, (), ()),
    "FJ" : ("Fujian", 0, (), ()),
    "GD" : ("Guangdong", 0, (), ()),
    "GS" : ("Gansu", 0, (), ()),
    "GX" : ("Guangxi Zhuangzu", 0, (), ()),
    "GZ" : ("Guizhou", 0, (), ()),
    "HA" : ("Henan", 0, (), ()),
    "HB" : ("Hubei", 0, (), ()),
    "HE" : ("Hebei", 0, (), ()),
    "HI" : ("Hainan", 0, (), ()),
    "HL" : ("Heilongjiang", 0, (), ()),
    "HN" : ("Hunan", 0, (), ()),
    "JL" : ("Jilin", 0, (), ()),
    "JS" : ("Jiangsu", 0, (), ()),
    "JX" : ("Jiangxi", 0, (), ()),
    "LN" : ("Liaoning", 0, (), ()),
    "NM" : ("Nei Mongol", 0, (), ()),
    "NX" : ("Ningxia Huizu", 0, (), ()),
    "QH" : ("Qinghai", 0, (), ()),
    "SC" : ("Sichuan", 0, (), ()),
    "SD" : ("Shandong", 0, (), ()),
    "SH" : ("Shanghai", 0, (), ()),
    "SN" : ("Shaanxi", 0, (), ()),
    "SX" : ("Shanxi", 0, (), ()),
    "TJ" : ("Tianjin", 0, (), ()),
    "XJ" : ("Xinjiang Uygur", 0, (), ()),
    "XZ" : ("Xizang", 0, (), ()),
    "YN" : ("Yunnan", 0, (), ()),
    "ZJ" : ("Zhejiang", 0, (), ()),
    }

Primary_Administrative_Subdivision_Enumeration_339 = {
    "12" : ("Chiba", 0, (), ()),
    "16" : ("Gunma", 0, (), ()),
    "14" : ("Ibaraki", 0, (), ()),
    "11" : ("Kanagawa", 0, (), ()),
    "13" : ("Saitama", 0, (), ()),
    "15" : ("Tochigi", 0, (), ()),
    "10" : ("Tokyo", 0, (), ()),
    "17" : ("Yamanashi", 0, (), ()),
    "20" : ("Aichi", 0, (), ()),
    "19" : ("Gifu", 0, (), ()),
    "21" : ("Mie", 0, (), ()),
    "18" : ("Shizuoka", 0, (), ()),
    "27" : ("Hyogo", 0, (), ()),
    "22" : ("Kyoto", 0, (), ()),
    "24" : ("Nara", 0, (), ()),
    "25" : ("Osaka", 0, (), ()),
    "23" : ("Shiga", 0, (), ()),
    "26" : ("Wakayama", 0, (), ()),
    "35" : ("Hiroshima", 0, (), ()),
    "31" : ("Okayama", 0, (), ()),
    "32" : ("Shimane", 0, (), ()),
    "34" : ("Tottori", 0, (), ()),
    "33" : ("Yamaguchi", 0, (), ()),
    "38" : ("Ehime", 0, (), ()),
    "36" : ("Kagawa", 0, (), ()),
    "39" : ("Kochi", 0, (), ()),
    "37" : ("Tokushima", 0, (), ()),
    "40" : ("Fukuoka", 0, (), ()),
    "46" : ("Kagoshima", 0, (), ()),
    "43" : ("Kumamoto", 0, (), ()),
    "45" : ("Miyazaki", 0, (), ()),
    "42" : ("Nagasaki", 0, (), ()),
    "44" : ("Oita", 0, (), ()),
    "47" : ("Okinawa", 0, (), ()),
    "41" : ("Saga", 0, (), ()),
    "04" : ("Akita", 0, (), ()),
    "02" : ("Aomori", 0, (), ()),
    "07" : ("Fukushima", 0, (), ()),
    "03" : ("Iwate", 0, (), ()),
    "06" : ("Miyagi", 0, (), ()),
    "05" : ("Yamagata", 0, (), ()),
    "01" : ("Hokkaido", 0, (), ()),
    "29" : ("Fukui", 0, (), ()),
    "30" : ("Ishikawa", 0, (), ()),
    "28" : ("Toyama", 0, (), ()),
    "09" : ("Nagano", 0, (), ()),
    "08" : ("Niigata", 0, (), ())
    }

Primary_Administrative_Subdivision_Enumeration_375 = {
    "AUR" : ("Aurora", 0, (), ()),
    "BTG" : ("Batangas", 0, (), ()),
    "CAV" : ("Cavite", 0, (), ()),
    "LAG" : ("Laguna", 0, (), ()),
    "MAD" : ("Marinduque", 0, (), ()),
    "MDC" : ("Mindoro Occidental", 0, (), ()),
    "MDR" : ("Mindoro Oriental", 0, (), ()),
    "PLW" : ("Palawan", 0, (), ()),
    "QUE" : ("Quezon", 0, (), ()),
    "RIZ" : ("Rizal", 0, (), ()),
    "ROM" : ("Romblon", 0, (), ()),
    "ILN" : ("Ilocos Norte", 0, (), ()),
    "ILS" : ("Ilocos Sur", 0, (), ()),
    "LUN" : ("La Union", 0, (), ()),
    "PAN" : ("Pangasinan", 0, (), ()),
    "BTN" : ("Batanes", 0, (), ()),
    "CAG" : ("Cagayan", 0, (), ()),
    "ISA" : ("Isabela", 0, (), ()),
    "NUV" : ("Nueva Vizcaya", 0, (), ()),
    "QUI" : ("Quirino", 0, (), ()),
    "ABR" : ("Abra", 0, (), ()),
    "APA" : ("Apayao", 0, (), ()),
    "BEN" : ("Benguet", 0, (), ()),
    "IFU" : ("Ifugao", 0, (), ()),
    "KAL" : ("Kalinga-Apayso", 0, (), ()),
    "MOU" : ("Mountain Province", 0, (), ()),
    "BAN" : ("Batasn", 0, (), ()),
    "BUL" : ("Bulacan", 0, (), ()),
    "NUE" : ("Nueva Ecija", 0, (), ()),
    "PAM" : ("Pampanga", 0, (), ()),
    "TAR" : ("Tarlac", 0, (), ()),
    "ZMB" : ("Zambales", 0, (), ()),
    "ALB" : ("Albay", 0, (), ()),
    "CAN" : ("Camarines Norte", 0, (), ()),
    "CAS" : ("Camarines Sur", 0, (), ()),
    "CAT" : ("Catanduanes", 0, (), ()),
    "MAS" : ("Masbate", 0, (), ()),
    "SOR" : ("Sorsogon", 0, (), ()),
    "BIL" : ("Biliran", 0, (), ()),
    "EAS" : ("Eastern Samar", 0, (), ()),
    "LEY" : ("Leyte", 0, (), ()),
    "NSA" : ("Northern Samar", 0, (), ()),
    "SLE" : ("Southern Leyte", 0, (), ()),
    "WSA" : ("Western Samar", 0, (), ()),
    "AKL" : ("Aklan", 0, (), ()),
    "ANT" : ("Antique", 0, (), ()),
    "CAP" : ("Capiz", 0, (), ()),
    "GUI" : ("Guimaras", 0, (), ()),
    "ILI" : ("Iloilo", 0, (), ()),
    "NEC" : ("Negroe Occidental", 0, (), ()),
    "BOH" : ("Bohol", 0, (), ()),
    "CEB" : ("Cebu", 0, (), ()),
    "NER" : ("Negros Oriental", 0, (), ()),
    "SIG" : ("Siquijor", 0, (), ()),
    "ZAN" : ("Zamboanga del Norte", 0, (), ()),
    "ZAS" : ("Zamboanga del Sur", 0, (), ()),
    "ZSI" : ("Zamboanga Sibugay", 0, (), ()),
    "NCO" : ("North Cotabato", 0, (), ()),
    "SUK" : ("Sultan Kudarat", 0, (), ()),
    "SAR" : ("Sarangani", 0, (), ()),
    "SCO" : ("South Cotabato", 0, (), ()),
    "BAS" : ("Basilan", 0, (), ()),
    "LAS" : ("Lanao del Sur", 0, (), ()),
    "MAG" : ("Maguindanao", 0, (), ()),
    "SLU" : ("Sulu", 0, (), ()),
    "TAW" : ("Tawi-Tawi", 0, (), ()),
    "LAN" : ("Lanao del Norte", 0, (), ()),
    "BUK" : ("Bukidnon", 0, (), ()),
    "CAM" : ("Camiguin", 0, (), ()),
    "MSC" : ("Misamis Occidental", 0, (), ()),
    "MSR" : ("Misamis Oriental", 0, (), ()),
    "COM" : ("Compostela Valley", 0, (), ()),
    "DAV" : ("Davao del Norte", 0, (), ()),
    "DAS" : ("Davao del Sur", 0, (), ()),
    "DAO" : ("Davao Oriental", 0, (), ()),
    "AGN" : ("Agusan del Norte", 0, (), ()),
    "AGS" : ("Agusan del Sur", 0, (), ()),
    "SUN" : ("Surigao del Norte", 0, (), ()),
    "SUR" : ("Surigao del Sur", 0, (), ())
    }

Primary_Administrative_Subdivision_Enumeration_497 = {
    "01" : ("Zagrebačka županija", 0, (), ()),
    "02" : ("Krapinsko-Zagorska županija", 0, (), ()),
    "03" : ("Sisačko-Moslavačka županija", 0, (), ()),
    "04" : ("Karlovačka županija", 0, (), ()),
    "05" : ("Varaždinska županija", 0, (), ()),
    "06" : ("Koprivničko-Križevačka županija", 0, (), ()),
    "07" : ("Bjelovarsko-Bilogorska županija", 0, (), ()),
    "08" : ("Primorsko-Goranska županija", 0, (), ()),
    "09" : ("Ličko-Senjska županija", 0, (), ()),
    "10" : ("Virovitičko-Podravska županija", 0, (), ()),
    "11" : ("Požeško-Slavonska županija", 0, (), ()),
    "12" : ("Brodsko-Posavska županija", 0, (), ()),
    "13" : ("Zadarska županija", 0, (), ()),
    "14" : ("Osječko-Baranjska županija", 0, (), ()),
    "15" : ("Šibensko-Kninska županija", 0, (), ()),
    "16" : ("Vukovarsko-Srijemska županija", 0, (), ()),
    "17" : ("Splitsko-Dalmatinska županija", 0, (), ()),
    "18" : ("Istarska županija", 0, (), ()),
    "19" : ("Dubrovačko-Neretvanska županija", 0, (), ()),
    "20" : ("Međimurska županija", 0, (), ()),
    "21" : ("Grad Zagreb", 0, (), ())
    }

Primary_Administrative_Subdivision_Enumeration_503 = {
    "APA" : ("Praha 1", 0, (), ()),
    "APB" : ("Praha 2", 0, (), ()),
    "APC" : ("Praha 3", 0, (), ()),
    "APD" : ("Praha 4", 0, (), ()),
    "APE" : ("Praha 5", 0, (), ()),
    "APF" : ("Praha 6", 0, (), ()),
    "APG" : ("Praha 7", 0, (), ()),
    "APH" : ("Praha 8", 0, (), ()),
    "API" : ("Praha 9", 0, (), ()),
    "APJ" : ("Praha 10", 0, (), ()),
    "BBN" : ("Benesov", 0, (), ()),
    "BBE" : ("Beroun", 0, (), ()),
    "BKD" : ("Kladno", 0, (), ()),
    "BKO" : ("Kolin", 0, (), ()),
    "BKH" : ("Kutna Hora", 0, (), ()),
    "BME" : ("Melnik", 0, (), ()),
    "BMB" : ("Mlada Boleslav", 0, (), ()),
    "BNY" : ("Nymburk", 0, (), ()),
    "BPZ" : ("Praha zapad", 0, (), ()),
    "BPV" : ("Praha vychod", 0, (), ()),
    "BPB" : ("Pribram", 0, (), ()),
    "BRA" : ("Rakovnik", 0, (), ()),
    "CBU" : ("Ceske Budejovice", 0, (), ()),
    "CCK" : ("Cesky Krumlov", 0, (), ()),
    "CJH" : ("Jindrichuv Hradec", 0, (), ()),
    "CPE" : ("Pelhrimov", 0, (), ()),
    "CPI" : ("Pisek", 0, (), ()),
    "CPR" : ("Prachatice", 0, (), ()),
    "CST" : ("Strakonice", 0, (), ()),
    "CTA" : ("Tabor", 0, (), ()),
    "DDO" : ("Domazlice", 0, (), ()),
    "DCH" : ("Cheb", 0, (), ()),
    "DKV" : ("Karlovy Vary", 0, (), ()),
    "DKL" : ("Klatovy", 0, (), ()),
    "DPM" : ("Plzen mesto", 0, (), ()),
    "DPJ" : ("Plzen jih", 0, (), ()),
    "DPS" : ("Plzen sever", 0, (), ()),
    "DRO" : ("Rokycany", 0, (), ()),
    "DSO" : ("Sokolov", 0, (), ()),
    "DTA" : ("Tachov", 0, (), ()),
    "ECL" : ("Ceska Lipa", 0, (), ()),
    "EDE" : ("Decin", 0, (), ()),
    "ECH" : ("Chomutov", 0, (), ()),
    "EJA" : ("Jablonec n. Nisou", 0, (), ()),
    "ELI" : ("Liberec", 0, (), ()),
    "ELT" : ("Litomerice", 0, (), ()),
    "ELO" : ("Louny", 0, (), ()),
    "EMO" : ("Most", 0, (), ()),
    "ETE" : ("Teplice", 0, (), ()),
    "EUL" : ("Usti nad Labem", 0, (), ()),
    "FHB" : ("Havlickuv Brod", 0, (), ()),
    "FHK" : ("Hradec Kralove", 0, (), ()),
    "FCR" : ("Chrudim", 0, (), ()),
    "FJI" : ("Jicin", 0, (), ()),
    "FNA" : ("Nachod", 0, (), ()),
    "FPA" : ("Pardubice", 0, (), ()),
    "FRK" : ("Rychn n. Kneznou", 0, (), ()),
    "FSE" : ("Semily", 0, (), ()),
    "FSV" : ("Svitavy", 0, (), ()),
    "FTR" : ("Trutnov", 0, (), ()),
    "FUO" : ("Usti nad Orlici", 0, (), ()),
    "GBL" : ("Blansko", 0, (), ()),
    "GBM" : ("Brno mesto", 0, (), ()),
    "GBV" : ("Brno venkov", 0, (), ()),
    "GBR" : ("Breclav", 0, (), ()),
    "GHO" : ("Hodonin", 0, (), ()),
    "GJI" : ("Jihlava", 0, (), ()),
    "GKR" : ("Kromeriz", 0, (), ()),
    "GPR" : ("Prostejov", 0, (), ()),
    "GTR" : ("Trebic", 0, (), ()),
    "GUH" : ("Uherske Hradiste", 0, (), ()),
    "GVY" : ("Vyskov", 0, (), ()),
    "GZL" : ("Zlin", 0, (), ()),
    "GZN" : ("Znojmo", 0, (), ()),
    "GZS" : ("Zdar nad Sazavou", 0, (), ()),
    "HBR" : ("Bruntal", 0, (), ()),
    "HFM" : ("Frydek-Mistek", 0, (), ()),
    "HJE" : ("Jesenik", 0, (), ()),
    "HKA" : ("Karvina", 0, (), ()),
    "HNJ" : ("Novy Jicin", 0, (), ()),
    "HOL" : ("Olomouc", 0, (), ()),
    "HOP" : ("Opava", 0, (), ()),
    "HOS" : ("Ostrava", 0, (), ()),
    "HPR" : ("Prerov", 0, (), ()),
    "HSU" : ("Sumperk", 0, (), ()),
    "HVS" : ("Vsetin", 0, (), ())
    }

Primary_Administrative_Subdivision_Enumeration_504 = {
    "BAA" : ("Bratislava 1", 0, (), ()),
    "BAB" : ("Bratislava 2", 0, (), ()),
    "BAC" : ("Bratislava 3", 0, (), ()),
    "BAD" : ("Bratislava 4", 0, (), ()),
    "BAE" : ("Bratislava 5", 0, (), ()),
    "MAL" : ("Malacky", 0, (), ()),
    "PEZ" : ("Pezinok", 0, (), ()),
    "SEN" : ("Senec", 0, (), ()),
    "DST" : ("Dunajska Streda", 0, (), ()),
    "GAL" : ("Galanta", 0, (), ()),
    "HLO" : ("Hlohovec", 0, (), ()),
    "PIE" : ("Piestany", 0, (), ()),
    "SEA" : ("Senica", 0, (), ()),
    "SKA" : ("Skalica", 0, (), ()),
    "TRN" : ("Trnava", 0, (), ()),
    "BAN" : ("Banovce n. Bebr.", 0, (), ()),
    "ILA" : ("Ilava", 0, (), ()),
    "MYJ" : ("Myjava", 0, (), ()),
    "NMV" : ("Nove Mesto n. Vah", 0, (), ()),
    "PAR" : ("Partizanske", 0, (), ()),
    "PBY" : ("Povazska Bystrica", 0, (), ()),
    "PRI" : ("Prievidza", 0, (), ()),
    "PUC" : ("Puchov", 0, (), ()),
    "TNC" : ("Trencin", 0, (), ()),
    "KOM" : ("Komarno", 0, (), ()),
    "LVC" : ("Levice", 0, (), ()),
    "NIT" : ("Nitra", 0, (), ()),
    "NZA" : ("Nove Zamky", 0, (), ()),
    "SAL" : ("Sala", 0, (), ()),
    "TOP" : ("Topolcany", 0, (), ()),
    "ZMO" : ("Zlate Moravce", 0, (), ()),
    "BYT" : ("Bytca", 0, (), ()),
    "CAD" : ("Cadca", 0, (), ()),
    "DKU" : ("Dolny Kubin", 0, (), ()),
    "KNM" : ("Kysucke N. Mesto", 0, (), ()),
    "LMI" : ("Liptovsky Mikulas", 0, (), ()),
    "MAR" : ("Martin", 0, (), ()),
    "NAM" : ("Namestovo", 0, (), ()),
    "RUZ" : ("Ruzomberok", 0, (), ()),
    "TTE" : ("Turcianske Teplice", 0, (), ()),
    "TVR" : ("Tvrdosin", 0, (), ()),
    "ZIL" : ("Zilina", 0, (), ()),
    "BBY" : ("Banska Bystrica", 0, (), ()),
    "BST" : ("Banska Stiavnica", 0, (), ()),
    "BRE" : ("Brezno", 0, (), ()),
    "DET" : ("Detva", 0, (), ()),
    "KRU" : ("Krupina", 0, (), ()),
    "LUC" : ("Lucenec", 0, (), ()),
    "POL" : ("Poltar", 0, (), ()),
    "REV" : ("Revuca", 0, (), ()),
    "RSO" : ("Rimavska Sobota", 0, (), ()),
    "VKR" : ("Velky Krtis", 0, (), ()),
    "ZAR" : ("Zarnovica", 0, (), ()),
    "ZIH" : ("Ziar nad Hronom", 0, (), ()),
    "ZVO" : ("Zvolen", 0, (), ()),
    "GEL" : ("Gelnica", 0, (), ()),
    "KEA" : ("Kosice 1", 0, (), ()),
    "KEB" : ("Kosice 2", 0, (), ()),
    "KEC" : ("Kosice 3", 0, (), ()),
    "KED" : ("Kosice 4", 0, (), ()),
    "KEO" : ("Kosice-okolie", 0, (), ()),
    "MIC" : ("Michalovce", 0, (), ()),
    "ROZ" : ("Roznava", 0, (), ()),
    "SOB" : ("Sobrance", 0, (), ()),
    "SNV" : ("Spisska Nova Ves", 0, (), ()),
    "TRE" : ("Trebisov", 0, (), ()),
    "BAR" : ("Bardejov", 0, (), ()),
    "HUM" : ("Humenne", 0, (), ()),
    "KEZ" : ("Kezmarok", 0, (), ()),
    "LEV" : ("Levoca", 0, (), ()),
    "MED" : ("Medzilaborce", 0, (), ()),
    "POP" : ("Poprad", 0, (), ()),
    "PRE" : ("Presov", 0, (), ()),
    "SAB" : ("Sabinov", 0, (), ()),
    "SNI" : ("Snina", 0, (), ()),
    "SLU" : ("Stara Lubovna", 0, (), ()),
    "STR" : ("Stropkov", 0, (), ()),
    "SVI" : ("Svidnik", 0, (), ()),
    "VRT" : ("Vranov nad Toplou", 0, (), ())
    }

DXCC_Entity_Code_Enumeration = {
    0 : ["None (the contacted station is known to not be within a DXCC entity)"],
    1 : ["CANADA"],
    3 : ["AFGHANISTAN"],
    4 : ["AGALEGA & ST. BRANDON IS."],
    5 : ["ALAND IS."],
    6 : ["ALASKA"],
    7 : ["ALBANIA"],
    9 : ["AMERICAN SAMOA"],
    10 : ["AMSTERDAM & ST. PAUL IS."],
    11 : ["ANDAMAN & NICOBAR IS."],
    12 : ["ANGUILLA"],
    13 : ["ANTARCTICA"],
    14 : ["ARMENIA"],
    15 : ["ASIATIC RUSSIA"],
    16 : ["NEW ZEALAND SUBANTARCTIC ISLANDS"],
    17 : ["AVES I."],
    18 : ["AZERBAIJAN"],
    20 : ["BAKER & HOWLAND IS."],
    21 : ["BALEARIC IS."],
    22 : ["PALAU"],
    24 : ["BOUVET"],
    27 : ["BELARUS"],
    29 : ["CANARY IS."],
    31 : ["C. KIRIBATI (BRITISH PHOENIX IS.)"],
    32 : ["CEUTA & MELILLA"],
    33 : ["CHAGOS IS."],
    34 : ["CHATHAM IS."],
    35 : ["CHRISTMAS I."],
    36 : ["CLIPPERTON I."],
    37 : ["COCOS I."],
    38 : ["COCOS (KEELING) IS."],
    40 : ["CRETE"],
    41 : ["CROZET I."],
    43 : ["DESECHEO I."],
    45 : ["DODECANESE"],
    46 : ["EAST MALAYSIA"],
    47 : ["EASTER I."],
    48 : ["E. KIRIBATI (LINE IS.)"],
    49 : ["EQUATORIAL GUINEA"],
    50 : ["MEXICO"],
    51 : ["ERITREA"],
    52 : ["ESTONIA"],
    53 : ["ETHIOPIA"],
    54 : ["EUROPEAN RUSSIA"],
    56 : ["FERNANDO DE NORONHA"],
    60 : ["BAHAMAS"],
    61 : ["FRANZ JOSEF LAND"],
    62 : ["BARBADOS"],
    63 : ["FRENCH GUIANA"],
    64 : ["BERMUDA"],
    65 : ["BRITISH VIRGIN IS."],
    66 : ["BELIZE"],
    69 : ["CAYMAN IS."],
    70 : ["CUBA"],
    71 : ["GALAPAGOS IS."],
    72 : ["DOMINICAN REPUBLIC"],
    74 : ["EL SALVADOR"],
    75 : ["GEORGIA"],
    76 : ["GUATEMALA"],
    77 : ["GRENADA"],
    78 : ["HAITI"],
    79 : ["GUADELOUPE"],
    80 : ["HONDURAS"],
    82 : ["JAMAICA"],
    84 : ["MARTINIQUE"],
    86 : ["NICARAGUA"],
    88 : ["PANAMA"],
    89 : ["TURKS & CAICOS IS."],
    90 : ["TRINIDAD & TOBAGO"],
    91 : ["ARUBA"],
    94 : ["ANTIGUA & BARBUDA"],
    95 : ["DOMINICA"],
    96 : ["MONTSERRAT"],
    97 : ["ST. LUCIA"],
    98 : ["ST. VINCENT"],
    99 : ["GLORIOSO IS."],
    100 : ["ARGENTINA"],
    103 : ["GUAM"],
    104 : ["BOLIVIA"],
    105 : ["GUANTANAMO BAY"],
    106 : ["GUERNSEY"],
    107 : ["GUINEA"],
    108 : ["BRAZIL"],
    109 : ["GUINEA-BISSAU"],
    110 : ["HAWAII"],
    111 : ["HEARD I."],
    112 : ["CHILE"],
    114 : ["ISLE OF MAN"],
    116 : ["COLOMBIA"],
    117 : ["ITU HQ"],
    118 : ["JAN MAYEN"],
    120 : ["ECUADOR"],
    122 : ["JERSEY"],
    123 : ["JOHNSTON I."],
    124 : ["JUAN DE NOVA, EUROPA"],
    125 : ["JUAN FERNANDEZ IS."],
    126 : ["KALININGRAD"],
    129 : ["GUYANA"],
    130 : ["KAZAKHSTAN"],
    131 : ["KERGUELEN IS."],
    132 : ["PARAGUAY"],
    133 : ["KERMADEC IS."],
    135 : ["KYRGYZSTAN"],
    136 : ["PERU"],
    137 : ["REPUBLIC OF KOREA"],
    138 : ["KURE I."],
    140 : ["SURINAME"],
    141 : ["FALKLAND IS."],
    142 : ["LAKSHADWEEP IS."],
    143 : ["LAOS"],
    144 : ["URUGUAY"],
    145 : ["LATVIA"],
    146 : ["LITHUANIA"],
    147 : ["LORD HOWE I."],
    148 : ["VENEZUELA"],
    149 : ["AZORES"],
    150 : ["AUSTRALIA"],
    152 : ["MACAO"],
    153 : ["MACQUARIE I."],
    157 : ["NAURU"],
    158 : ["VANUATU"],
    159 : ["MALDIVES"],
    160 : ["TONGA"],
    161 : ["MALPELO I."],
    162 : ["NEW CALEDONIA"],
    163 : ["PAPUA NEW GUINEA"],
    165 : ["MAURITIUS"],
    166 : ["MARIANA IS."],
    167 : ["MARKET REEF"],
    168 : ["MARSHALL IS."],
    169 : ["MAYOTTE"],
    170 : ["NEW ZEALAND"],
    171 : ["MELLISH REEF"],
    172 : ["PITCAIRN I."],
    173 : ["MICRONESIA"],
    174 : ["MIDWAY I."],
    175 : ["FRENCH POLYNESIA"],
    176 : ["FIJI"],
    177 : ["MINAMI TORISHIMA"],
    179 : ["MOLDOVA"],
    180 : ["MOUNT ATHOS"],
    181 : ["MOZAMBIQUE"],
    182 : ["NAVASSA I."],
    185 : ["SOLOMON IS."],
    187 : ["NIGER"],
    188 : ["NIUE"],
    189 : ["NORFOLK I."],
    190 : ["SAMOA"],
    191 : ["NORTH COOK IS."],
    192 : ["OGASAWARA"],
    195 : ["ANNOBON I."],
    197 : ["PALMYRA & JARVIS IS."],
    199 : ["PETER 1 I."],
    201 : ["PRINCE EDWARD & MARION IS."],
    202 : ["PUERTO RICO"],
    203 : ["ANDORRA"],
    204 : ["REVILLAGIGEDO"],
    205 : ["ASCENSION I."],
    206 : ["AUSTRIA"],
    207 : ["RODRIGUEZ I."],
    209 : ["BELGIUM"],
    211 : ["SABLE I."],
    212 : ["BULGARIA"],
    213 : ["SAINT MARTIN"],
    214 : ["CORSICA"],
    215 : ["CYPRUS"],
    216 : ["SAN ANDRES & PROVIDENCIA"],
    217 : ["SAN FELIX & SAN AMBROSIO"],
    219 : ["SAO TOME & PRINCIPE"],
    221 : ["DENMARK"],
    222 : ["FAROE IS."],
    223 : ["ENGLAND"],
    224 : ["FINLAND"],
    225 : ["SARDINIA"],
    227 : ["FRANCE"],
    230 : ["FEDERAL REPUBLIC OF GERMANY"],
    232 : ["SOMALIA"],
    233 : ["GIBRALTAR"],
    234 : ["SOUTH COOK IS."],
    235 : ["SOUTH GEORGIA I."],
    236 : ["GREECE"],
    237 : ["GREENLAND"],
    238 : ["SOUTH ORKNEY IS."],
    239 : ["HUNGARY"],
    240 : ["SOUTH SANDWICH IS."],
    241 : ["SOUTH SHETLAND IS."],
    242 : ["ICELAND"],
    245 : ["IRELAND"],
    246 : ["SOVEREIGN MILITARY ORDER OF MALTA"],
    247 : ["SPRATLY IS."],
    248 : ["ITALY"],
    249 : ["ST. KITTS & NEVIS"],
    250 : ["ST. HELENA"],
    251 : ["LIECHTENSTEIN"],
    252 : ["ST. PAUL I."],
    253 : ["ST. PETER & ST. PAUL ROCKS"],
    254 : ["LUXEMBOURG"],
    256 : ["MADEIRA IS."],
    257 : ["MALTA"],
    259 : ["SVALBARD"],
    260 : ["MONACO"],
    262 : ["TAJIKISTAN"],
    263 : ["NETHERLANDS"],
    265 : ["NORTHERN IRELAND"],
    266 : ["NORWAY"],
    269 : ["POLAND"],
    270 : ["TOKELAU IS."],
    272 : ["PORTUGAL"],
    273 : ["TRINDADE & MARTIM VAZ IS."],
    274 : ["TRISTAN DA CUNHA & GOUGH I."],
    275 : ["ROMANIA"],
    276 : ["TROMELIN I."],
    277 : ["ST. PIERRE & MIQUELON"],
    278 : ["SAN MARINO"],
    279 : ["SCOTLAND"],
    280 : ["TURKMENISTAN"],
    281 : ["SPAIN"],
    282 : ["TUVALU"],
    283 : ["UK SOVEREIGN BASE AREAS ON CYPRUS"],
    284 : ["SWEDEN"],
    285 : ["VIRGIN IS."],
    286 : ["UGANDA"],
    287 : ["SWITZERLAND"],
    288 : ["UKRAINE"],
    289 : ["UNITED NATIONS HQ"],
    291 : ["UNITED STATES OF AMERICA"],
    292 : ["UZBEKISTAN"],
    293 : ["VIET NAM"],
    294 : ["WALES"],
    295 : ["VATICAN"],
    296 : ["SERBIA"],
    297 : ["WAKE I."],
    298 : ["WALLIS & FUTUNA IS."],
    299 : ["WEST MALAYSIA"],
    301 : ["W. KIRIBATI (GILBERT IS. )"],
    302 : ["WESTERN SAHARA"],
    303 : ["WILLIS I."],
    304 : ["BAHRAIN"],
    305 : ["BANGLADESH"],
    306 : ["BHUTAN"],
    308 : ["COSTA RICA"],
    309 : ["MYANMAR"],
    312 : ["CAMBODIA"],
    315 : ["SRI LANKA"],
    318 : ["CHINA"],
    321 : ["HONG KONG"],
    324 : ["INDIA"],
    327 : ["INDONESIA"],
    330 : ["IRAN"],
    333 : ["IRAQ"],
    336 : ["ISRAEL"],
    339 : ["JAPAN"],
    342 : ["JORDAN"],
    344 : ["DEMOCRATIC PEOPLE'S REP. OF KOREA"],
    345 : ["BRUNEI DARUSSALAM"],
    348 : ["KUWAIT"],
    354 : ["LEBANON"],
    363 : ["MONGOLIA"],
    369 : ["NEPAL"],
    370 : ["OMAN"],
    372 : ["PAKISTAN"],
    375 : ["PHILIPPINES"],
    376 : ["QATAR"],
    378 : ["SAUDI ARABIA"],
    379 : ["SEYCHELLES"],
    381 : ["SINGAPORE"],
    382 : ["DJIBOUTI"],
    384 : ["SYRIA"],
    386 : ["TAIWAN"],
    387 : ["THAILAND"],
    390 : ["TURKEY"],
    391 : ["UNITED ARAB EMIRATES"],
    400 : ["ALGERIA"],
    401 : ["ANGOLA"],
    402 : ["BOTSWANA"],
    404 : ["BURUNDI"],
    406 : ["CAMEROON"],
    408 : ["CENTRAL AFRICA"],
    409 : ["CAPE VERDE"],
    410 : ["CHAD"],
    411 : ["COMOROS"],
    412 : ["REPUBLIC OF THE CONGO"],
    414 : ["DEMOCRATIC REPUBLIC OF THE CONGO"],
    416 : ["BENIN"],
    420 : ["GABON"],
    422 : ["THE GAMBIA"],
    424 : ["GHANA"],
    428 : ["COTE D'IVOIRE"],
    430 : ["KENYA"],
    432 : ["LESOTHO"],
    434 : ["LIBERIA"],
    436 : ["LIBYA"],
    438 : ["MADAGASCAR"],
    440 : ["MALAWI"],
    442 : ["MALI"],
    444 : ["MAURITANIA"],
    446 : ["MOROCCO"],
    450 : ["NIGERIA"],
    452 : ["ZIMBABWE"],
    453 : ["REUNION I."],
    454 : ["RWANDA"],
    456 : ["SENEGAL"],
    458 : ["SIERRA LEONE"],
    460 : ["ROTUMA I."],
    462 : ["SOUTH AFRICA"],
    464 : ["NAMIBIA"],
    466 : ["SUDAN"],
    468 : ["SWAZILAND"],
    470 : ["TANZANIA"],
    474 : ["TUNISIA"],
    478 : ["EGYPT"],
    480 : ["BURKINA FASO"],
    482 : ["ZAMBIA"],
    483 : ["TOGO"],
    489 : ["CONWAY REEF"],
    490 : ["BANABA I. (OCEAN I.)"],
    492 : ["YEMEN"],
    497 : ["CROATIA"],
    499 : ["SLOVENIA"],
    501 : ["BOSNIA-HERZEGOVINA"],
    502 : ["MACEDONIA"],
    503 : ["CZECH REPUBLIC"],
    504 : ["SLOVAK REPUBLIC"],
    505 : ["PRATAS I."],
    506 : ["SCARBOROUGH REEF"],
    507 : ["TEMOTU PROVINCE"],
    508 : ["AUSTRAL I."],
    509 : ["MARQUESAS IS."],
    510 : ["PALESTINE"],
    511 : ["TIMOR-LESTE"],
    512 : ["CHESTERFIELD IS."],
    513 : ["DUCIE I."],
    514 : ["MONTENEGRO"],
    515 : ["SWAINS I."],
    516 : ["SAINT BARTHELEMY"],
    517 : ["CURACAO"],
    518 : ["ST MAARTEN"],
    519 : ["SABA & ST. EUSTATIUS"],
    520 : ["BONAIRE"],
    521 : ["SOUTH SUDAN (REPUBLIC OF)"],
    522 : ["REPUBLIC OF KOSOVO"],
    }

#
#Rather than maintaining a table of DXCC_Entity_Code_Enumeration to
#Primary_Administrative_Subdivision_Enumeration_NNN links, allow the
#Primary_Administrative_Subdivision_Enumeration tables to be added to the
#DXCC_Entity_Code_Enumeration table on-the-fly by merely defining a
#Primary_Administrative_Subdivision_Enumeration_NNN table.
#
#This code will add a None - if no further information on a region - to the
#end of the list for the country, or a link to the country's
#Primary_Administrative_Subdivision_Enumeration_NNN table.
#
for i in DXCC_Entity_Code_Enumeration.keys():
    #
    #Figure out the name of the table (text) for that country
    #
    Primary_Administrative_Subdivision_Enumeration_number = (
        "Primary_Administrative_Subdivision_Enumeration_" +  str(i))

    #
    #See if the table exists
    #
    exec('table_exists = "' + Primary_Administrative_Subdivision_Enumeration_number + '" in locals()')

    #
    #If the table exists, add it to the end of the DXCC entry. If not, add None
    #to the end of the entry.
    #
    if table_exists:
        exec("DXCC_Entity_Code_Enumeration[i].append(" + Primary_Administrative_Subdivision_Enumeration_number + ")")
    else:
        DXCC_Entity_Code_Enumeration[i].append(None)

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
    "NONE" : (0, "Not within a WAE or CQ region that is within a DXCC entity", "", ()),
    "IV" : (206, "ITU Vienna", "4U1V", ("CQ", "WAE",)),
    "AI" : (248, "African Italy", "IG9", ("WAE",)),
    "SY" : (248, "Sicily", "IT9", ("CQ", "WAE",)),
    "BI" : (259, "Bear Island", "JW/B", ("CQ", "WAE",)),
    "SI" : (279, "Shetland Islands", "GM/S", ("CQ", "WAE",)),
    "KO" : (296, "Kosovo", "Z6", ("CQ", "WAE",)),
    "ET" : (390, "European Turkey", "TA1", ("CQ",))
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
    "US" : ("AK", "AL", "AR", "AS", "AZ", "CA", "CO", "CT", "DC", "DE", "FL",
        "FM", "GA", "GU", "HI", "IA", "ID", "IL", "IN", "KS", "KY", "LA", "MA",
        "MD", "ME", "MH", "MI", "MN", "MO", "MP", "MS", "MT", "NC", "ND", "NE",
        "NH", "NJ", "NM", "NV", "NY", "OH", "OK", "OR", "PA", "PR", "PW", "RI",
        "SC", "SD", "TN", "TX", "UT", "VA", "VI", "VT", "WA", "WI", "WV", "WY")
    }

re_power = r'\d+W'
re_band = r'\d+\.?\d*[M|CM|MM]'
re_frequency = r'(\.\d+)|(\d+\.?\d*)'

#
#Convert modes and submodes into regular expressions that can be used for
#searching.
#
re_mode_enumeration = {}
for mode in Mode_Enumeration:
    #
    #Make sure modes do not have blanks in their names
    #
    if re.search('\s', mode):
        print("""
Severe error: "{}" mode not valid. QSO modes many not have blanks in their
              names. Please contact K0RLO@nankoweap" about this error and send
              the adif.py file.
""".format(mode))
        exit(1)

    re_mode_enumeration[mode] = {}    
    #
    #Submodes can have blanks within them. Remove all blanks for matching but
    #keep the original format arond for readability.
    #
    for submode in Mode_Enumeration[mode]:
        re_mode_enumeration[mode][re.sub(r'\s+', "", submode)] = submode

def tag(tag_name, tag_contents):
    """
    Convert a tag name and contents to a correctly formatted ADIF tag format
    <TAG_NAME:LENGTH_OF_CONTENTS>CONTENTS<b>

    Arguments:
        tag_name:       Name of the tag
        tag_contents:   Contents of tag

    Returns:
        Correctly formatted ADIF tag wit a blank at the end
    """

    #
    #Assure no blanks on front or end of tag name or contents
    #
    tag_name.strip()
    tag_contents.strip()

    #
    #Return the correctly formatted tag with a blank at the end
    #
    return("<{}:{}>{} ".format(tag_name, len(tag_contents), tag_contents))

def record(tags, tag_order=None):
    """
    Convert a dictonary of tags to an ADIF record and return the string.
    If the list tag_order is given, generate the tags in that order, otherwise
    generate in sort order.

    Arguments:
        tags:       Dictonary of tags and their contents
        tag_order:  Order to generate tags in

    Returns:
        Correctly formatted ADIF record with <EOR>\n at end
    """

    #
    #Make copy of dictonary so we don't modify the original
    #
    tags = tags.copy()

    #
    #If tag order not supplied, generate keys in sorted order
    #
    if not tag_order:
        tag_order = sorted(tags.keys())

    #
    #Generate tags in requested order
    #
    adif_record = ""
    for tag_name in tag_order:
        if tag_name in tags:
            #
            #If the tag exists, generate it
            #
            adif_record += tag(tag_name, tags[tag_name])

            #
            #Remove the tag from the dictonary to see if we have any leftovers
            #when we're done, which would be a severe error
            #
            del tags[tag_name]

    #
    #See if any leftover tags
    #
    if tags:
        print("""
Severe error: The following tags were left over after creating the ADIF record:
              {}
""".format(", ".join(sorted(tags.keys()))))
        exit(1)

    #
    #Return the correctly formatted record with an <EOR> and newline at the end
    #
    return(adif_record + "<EOR>\n")

def freq_to_band(freq):
    """
    Given a frequency, convert it to a band

    Arguments:
        freq:   Frequency to use to search for band

    Returns:
        Tuple of one member if frequency valid
        String containing error if frequency invalid
    """

    #
    #Convert string frequency to float (valid float format already verified)
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
Error: Frequency "{}" is does not fall within a valid range.
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

    #
    #Split into xmit and recieve bands, if both specified
    #
    bands = re.split(k0rlo.default_split, band)

    #
    #If more than two bands specified, it's an error
    #
    if len(bands) > 2:
        return("""
Error: More than two bands specified. Specify a single band for
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
Error: "{}" does not fall within a known band.
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
        freq:   String containing frequency/frequencies to be verified

    Returns:
        List of bands and frequencies if correctly formatted
        Error string if formatted incorrectly
    """

    #
    #Split into xmit and recieve ferquencies, if both specified
    #
    freq = re.split(k0rlo.default_split, freq)

    #
    #If more than two frequencies specified, it's an error
    #
    if len(freq) > 2:
        return("""
Error: More than two frequencies specified. Specify a single frequency for
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
Error: "{}" is not a valid frequency format.
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

def valid_power(power):
    """
    See if valid power specified. If so, return it. If not, return False

    Arguments:
        band:   String containing power to be verified

    Returns:
        Power string if correct
        False if band string incorrectly formatted
    """

    #
    #If it's a power, return it.
    #
    if re.fullmatch(re_power, power):
        #
        #Pack it into a tuple to differentiate it from an error string and
        #remove the "W" from the end.
        #
        return((power[:-1],))

    return("""
Error: "{}" is not a valid power syntax. It should be a number followed
       by a "W".
       Example: "100W" or "5W".
""".format(power))

def valid_mode(mode_submode):
    """
    See if mode (and submode) specified. If so, return the mode and submode.

    Arguments:
        mode_submode:   String containing mode (and submode) to be verified

    Returns:
        [mode, submode] is valid.
        False if mode or submode not valid
    """

    #
    #Some submodes can have blanks in them (thanks a lot, folks). So I strip
    #the blanks out for comparing, but keep around the original format for
    #reporting
    #
    #OLIVIA
    #OLIVIA OLIVIA8/500
    #OLIVIA8/500
    #
    #So I need to generate all the possible permutations and combinations of
    #mode and submode and throw it at the code that identifies it to see if I
    #get a match somehow.
    #

    #
    #Breakup the mode and submode
    #
    mode_submode = re.split(k0rlo.default_split, mode_submode)
    
    #
    #Pull off mode and re-create submode in case they're blanks in it (like the
    #OLIVIA submodes have)
    #
    mode_text = mode_submode.pop(0)
    display_submode = " ".join(mode_submode)
    submode_text = "".join(mode_submode)

    #
    #Try identifying it as both a mode and submode and just a submode
    #
    for (mode, submode) in [[mode_text, submode_text], [mode_text + submode_text, ""]]:
        if submode:
            #
            #We have a mode AND submode specified. See if it's a valid combo
            #
            if mode in re_mode_enumeration:
                #
                #Mode looks good, see if this is a valid submode for that mode
                #
                if submode in re_mode_enumeration[mode]:
                    return((mode, re_mode_enumeration[mode][submode]))
        else:
            #
            #We only have a mode. It could also be only a submode. Do an
            #exaustive search of modes and submodes for the string
            #
            if mode in re_mode_enumeration:
                #
                #Only a valid mode is specified. Return it and no submode
                #
                return((mode,))
            #
            #Did not find a mode match, do an exhaustive search through all the
            #submodes for a match
            #
            for mode_index in re_mode_enumeration.keys():
                if mode in re_mode_enumeration[mode_index]:
                    return((mode_index, re_mode_enumeration[mode_index][mode]))

    #
    #Not a valid mode and submode
    #
    if display_submode:
        return("""
Error: "{}" "{}" is an invalid mode and/or submode.
       Examples: "SSB USB" or"JT9 JT9H FAST".
""".format(mode_text, display_submode))
    else:
        return("""
Error: "{}" is not recognized as a mode or submode.
       Examples: "SSB", "USB" or "JT9H FAST".
""".format(mode_text))

