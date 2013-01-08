import argparse
import sys
import urllib2
import xml.etree.cElementTree as et
import re
from datetime import date

__author__ = 'Max Lin <mlin@suse.com>'

### Fetch completely xml file ###
def write_pagetitles_xml(period, date, data):
    date = date.replace(',','-')
    filename = 'pagetitles-' + period + '-' + date
    pagetitles_xml_file = open(filename + '.xml','w')
    pagetitles_xml_file.write(data)
    pagetitles_xml_file.close()

    print 'The data already stored in %s' % filename
    return filename

### Ask user to input the date ###
def validation_date(period, begin, end):
    if not begin:
        begin = str(date.today())
    if period == 'range':
        if re.match(r"^[0-9]{4}-(1[0-2]|0[1-9])-(3[01]|[12][0-9]|0[1-9])$", begin) and re.match(r"^[0-9]{4}-(1[0-2]|0[1-9])-(3[01]|[12][0-9]|0[1-9])$", end):
            return begin + ',' + end
        else:
            return 'fail'
    elif period == 'day' or period == 'month' or period == 'year':
        if begin == 'today' or begin == 'yesterday' or re.match(r"^[0-9]{4}-(1[0-2]|0[1-9])-(3[01]|[12][0-9]|0[1-9])$", begin):
            return begin
        else:
            return 'fail'
    else:
        return 'fail'

### Prepare the address and token auth string in order to fetch the data ###
def fetch_data(period, query_date):
    # Read string of token_auth
    try:
        tokenauth_file = open('piwik_tokenauth')
    except IOError as e:
        print "Cannot found piwik_tokenauth file\nI/O error({0}): {1}".format(e.errno, e.strerror)
        sys.exit(1)
    else:
        tokenauth_param = '&token_auth=' + tokenauth_file.read()
        tokenauth_file.close()
    # Debugging
    #print tokenauth_param

    # software.o.o idSite is 7 in openSUSE piwik
    period_param = 'method=Actions.getPageTitles&idSite=7&period=' + period + '&date=' + query_date + '&format=xml&expanded=1'
    # Assembeled post
    post_param = 'http://beans.opensuse.org/piwik/index.php?module=API&' + period_param + tokenauth_param
    # Debugging
    #print post_param

    # Fetch the xml data and stored it
    piwikurl = urllib2.urlopen(post_param)
    data = piwikurl.read()
    piwikurl.close()

    # Debugging
    #print data

    filename = write_pagetitles_xml(period, query_date, data)
    return filename

### Walk throught the xml file ###
def parse_data(data, pagetitles_file, show_in_screen):
    # The condition of print visit numbers
    print_visits = False
    for child in data:
        if child.tag == 'label':
            if re.search(r"\Wtorrent$", child.text.strip()) or re.search(r"\Wiso$", child.text.strip()):
                if show_in_screen == True:
                    print child.text.strip() + ':',
                pagetitles_file.write(child.text.strip() + ':')
                print_visits = True
        elif child.tag == 'row' or child.tag == 'subtable':
            parse_data(child, pagetitles_file, show_in_screen)
        elif child.tag == 'nb_hits' and print_visits == True:
            if show_in_screen == True:
                print child.text.strip()
            pagetitles_file.write(child.text.strip() + '\n')
            print_visits = False

### Main ###
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate download numbers from PIWIK')
    parser.add_argument('-p', '--period', dest='period', help='period of data request, by default is day, option: day, month, year, range')
    parser.add_argument('-b', '--begin', dest='begin', help='first date request, by default is today, format YYYY-MM-DD')
    parser.add_argument('-e', '--end', dest='end', help='last date request for period is range, format YYYY-MM-DD')

    args = parser.parse_args()

    if not args.period:
        period = 'day'
    else:
        period = args.period

    filename = None

    query_date = validation_date(period, args.begin, args.end)
    if query_date != 'fail':
        filename = fetch_data(period, query_date)
    else:
        print 'Please input a valid date with format YYYY-MM-DD!'
        sys.exit(1)

    tree = et.ElementTree(file=filename + '.xml')
    tree.getroot()
    root = tree.getroot()

    ### Started parsing xml ###
    show_in_screen = False
    #show_op = raw_input('Ready parsing the xml data, would you like shows the data in the screen?[Y/N]')
    #if show_op[0] == 'Y' or show_op[0] == 'y':
    #    show_in_screen = True
    print 'Start parsing the xml data and store the result to %s.csv ' % filename
    pagetitles_file = open(filename + '.csv', 'w')
    for child in root:
        parse_data(child, pagetitles_file, show_in_screen)
    pagetitles_file.close()
    print 'Parse the xml data done!'
