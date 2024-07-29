import re
import codecs

####
#### Global definitions
####

version = "2024.07.29.00-BETA"

is3116_filename = 'ISO3116/ISO3116'

###
### Read in all ISO3116 information and put into a dictonary based on country
### name.
###
        
country_file = open(is3116_filename, encoding='latin-1')

countries = {}
while (True):
    #
    # Read the English name of the country
    #
    long_english = country_file.readline().strip()
    #
    #If this if the end-of file, exit the while loop. Only checking here will
    #cause an error if we don't have exactly five entries per country, and
    #an error message in such a case is something we want.
    #
    if not long_english:
        break

    #
    #Strip off any parenthetical endings off the English name
    #
    short_english = re.sub(r'\s*\(.*$', '', long_english)

    #
    # Read the French name of the country
    #
    long_french = country_file.readline().strip()

    #
    #Strip off any parenthetical endings off the French name
    #
    short_french = re.sub(r'\s*\(.*$', '', long_french)

    #
    #Get two letter country abbreviation
    #
    two_letter = country_file.readline().strip()

    #
    #Get three letter country abbreviation
    #
    three_letter = country_file.readline().strip()

    #
    #Get numeric country
    #
    number = int(country_file.readline().strip())

    #
    #Create country entry based on two letter abbreviation. Don't need to store
    #the two letter designation since that's the key.
    #
    countries[two_letter] = (long_english, short_english, long_french,
        short_french, three_letter, number)

country_file.close()
