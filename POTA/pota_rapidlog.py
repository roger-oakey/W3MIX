import re

band_mapping = {
    '2190M'  : [0.1357, 0.1378],
    '630M'   : [0.472, 0.479],
    '560M'   : [0.501, 0.504],
    '160M'   : [1.8, 2.0],
    '80M'    : [3.5, 4.0],
    '60M'    : [5.06, 5.45],
    '40M'    : [7.0, 7.3],
    '30M'    : [10.1, 10.15],
    '20M'    : [14.0, 14.35],
    '17M'    : [18.068, 18.168],
    '15M'    : [21.0, 21.45],
    '12M'    : [24.890, 24.99],
    '10M'    : [28.0, 29.7],
    '8M'     : [40, 45],
    '6M'     : [50, 54],
    '5M'     : [54.000001, 69.9],
    '4M'     : [70, 71],
    '2M'     : [144, 148],
    '1.25M'  : [222, 225],
    '70CM'   : [420, 450],
    '33CM'   : [902, 928],
    '23CM'   : [1240, 1300],
    '13CM'   : [2300, 2450],
    '9CM'    : [3300, 3500],
    '6CM'    : [5650, 5925],
    '3CM'    : [10000, 10500],
    '1.25CM' : [24000, 24250],
    '6MM'    : [47000, 47200],
    '4MM'    : [75500, 81000],
    '2.5MM'  : [119980, 123000],
    '2MM'    : [134000, 149000],
    '1MM'    : [241000, 250000]
    }

modes_and_submodes = {
    "AM" : [],	 	 
    "ARDOP" : [],
    "ATV" : [],
    "CHIP" : ["CHIP64", "CHIP128"],
    "CLO" : [],
    "CONTESTI" : [],
    "CW" : ["PCW"],
    "DIGITALVOICE" : ["C4FM", "DMR", "DSTAR"],
    "DOMINO" : ["DOM-M", "DOM4", "DOM5", "DOM8", "DOM11", "DOM16", "DOM22", "DOM44", "DOM88", "DOMINOEX", "DOMINOF"],
    "DYNAMIC" : ["VARA HF", "VARA SATELLITE", "VARA FM 1200", "VARA FM 9600"],
    "FAX" : [],
    "FM" : [],
    "FSK441" : [],
    "FT8" : [],
    "HELL" : ["FMHELL", "FSKHELL", "HELL80", "HELLX5", "HELLX9", "HFSK", "PSKHELL", "SLOWHELL"],
    "ISCAT" : ["ISCAT-A", "ISCAT-B"],	 
    "JT4" : ["JT4A", "JT4B", "JT4C", "JT4D", "JT4E", "JT4F", "JT4G"],
    "JT6M" : [],
    "JT9" : ["JT9-1", "JT9-2", "JT9-5", "JT9-10", "JT9-30", "JT9A", "JT9B", "JT9C", "JT9D", "JT9E", "JT9E FAST", "JT9F", "JT9F FAST", "JT9G", "JT9G FAST", "JT9H", "JT9H FAST"],
    "JT44" : [],
    "JT65" : ["JT65A", "JT65B", "JT65B2", "JT65C", "JT65C2"],
    "MFSK" : ["FSQCALL", "FST4", "FST4W", "FT4", "JS8", "JTMS", "MFSK4", "MFSK8", "MFSK11", "MFSK16", "MFSK22", "MFSK31", "MFSK32", "MFSK64", "MFSK64L", "MFSK128 MFSK128L", "Q65"],
    "MSK144" : [],
    "MT63" : [],
    "OLIVIA" : ["OLIVIA 4/125", "OLIVIA 4/250", "OLIVIA 8/250", "OLIVIA 8/500", "OLIVIA 16/500", "OLIVIA 16/1000", "OLIVIA 32/1000"],
    "OPERA" : ["OPERA-BEACON", "OPERA-QSO"],
    "PAC" : ["PAC2", "PAC3", "PAC4"],
    "PAX" : ["PAX2"],
    "PKT" : [],
    "PSK" : ["8PSK125", "8PSK125F", "8PSK125FL", "8PSK250", "8PSK250F", "8PSK250FL", "8PSK500", "8PSK500F", "8PSK1000", "8PSK1000F", "8PSK1200F", "FSK31", "PSK10", "PSK31", "PSK63", "PSK63F", "PSK63RC4", "PSK63RC5", "PSK63RC10", "PSK63RC20", "PSK63RC32", "PSK125", "PSK125C12", "PSK125R", "PSK125RC10", "PSK125RC12", "PSK125RC16", "PSK125RC4", "PSK125RC5", "PSK250", "PSK250C6", "PSK250R", "PSK250RC2", "PSK250RC3", "PSK250RC5", "PSK250RC6", "PSK250RC7", "PSK500", "PSK500C2", "PSK500C4", "PSK500R", "PSK500RC2", "PSK500RC3", "PSK500RC4", "PSK800C2", "PSK800RC2", "PSK1000", "PSK1000C2", "PSK1000R", "PSK1000RC2", "PSKAM10", "PSKAM31", "PSKAM50", "PSKFEC31", "QPSK31", "QPSK63", "QPSK125", "QPSK250", "QPSK500", "SIM31"],
    "PSK2K" : [],
    "Q15" : [],
    "QRA64" : ["QRA64A", "QRA64B", "QRA64C", "QRA64D", "QRA64E"],
    "ROS" : ["ROS-EME", "ROS-HF", "ROS-MF"],
    "RTTY" : ["ASCI"],
    "RTTYM" : [],
    "SSB" : ["LSB", "USB"],	 
    "SSTV" : [],
    "T10" : [],
    "THOR" : ["THOR-M", "THOR4", "THOR5", "THOR8", "THOR11", "THOR16", "THOR22", "THOR25X4", "THOR50X1", "THOR50X2", "THOR100"],
    "THRB" : ["THRBX", "THRBX1", "THRBX2", "THRBX4", "THROB1", "THROB2", "THROB4"],
    "TOR" : ["AMTORFEC", "GTOR", "NAVTEX", "SITORB"],
    "V4" : [],
    "VOI" : [],
    "WINMOR" : [],
    "WSPR" : []
    }

#
#Convert modes and submodes into regular expressions that can bve used for
#searching.
#
re_modes_and_submodes = {}
for mode in modes_and_submodes:
    #
    #Make sure modes do not have blanks in their names
    #
    if re.search('\s', mode):
        print("""
Severe error: "{}" mode not valid. QSO modes many not have blanks in their
              names. Please contact K0RLO@nankoweap" about this error and send
              the pota_rapidlog.py file.
""".format(mode))
        exit(1)

    re_modes_and_submodes[mode] = {}    
    #
    #Submodes can have blanks within them. Remove all blanks for matching but
    #keep the original format arond for readability.
    #
    for submode in modes_and_submodes[mode]:
        re_modes_and_submodes[mode][re.sub(r'\s+', "", submode)] = submode

#
#This is the order that the ADIF tags will be placed into the file for
#consistency
#
adif_tag_order = [
    "STATION_CALLSIGN",
    "OPERATOR",
    "CALL",
    "QSO_DATE",
    "TIME_ON",
    "BAND",
    "MODE",
    "SUBMODE",
    "MY_SIG",
    "MY_SIG_INFO",
    "MY_STATE",
    "SIG",
    "SIG_INFO",
    "RST_SENT",
    "RST_RCVD",
    "FREQ",
    "FREQ_RX",
    "TX_PWR",
    "RX_PWR"
    ]
    
