import sys
import urllib2
import xml.etree.cElementTree as et
import re

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
def ask_date(period):
    if period == 'range':
        print 'Please input date range with format YYYY-MM-DD'
        start  = raw_input('From: ')
        end = raw_input('End: ')
        if re.match(r"^[0-9]{4}-(1[0-2]|0[1-9])-(3[01]|[12][0-9]|0[1-9])$", start) and re.match(r"^[0-9]{4}-(1[0-2]|0[1-9])-(3[01]|[12][0-9]|0[1-9])$", end):
            return start + ',' + end
        else:
            return 'fail'
    else:
        date = raw_input('Please input the date with format YYYY-MM-DD: ')
        if date == 'today' or date == 'yesterday' or re.match(r"^[0-9]{4}-(1[0-2]|0[1-9])-(3[01]|[12][0-9]|0[1-9])$", date):
            return date
        else:
            return 'fail'

### Prepare the address and token auth string in order to fetch the data ###
def fetch_data(period, date):
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
    period_param = 'method=Actions.getPageTitles&idSite=7&period=' + period + '&date=' + date + '&format=xml&expanded=1'
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

    filename = write_pagetitles_xml(period, date, data)
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
op_list = {1 : 'day', 2 : 'month', 3 : 'year', 4 : 'range', 5 : 'exit'}

for k in op_list:
    print '%s. %s\n' % (k, op_list[k])

filename = None

while 1:
    period_ch = input('Choice the date range(1-4) or 5 to exit the program: ')

    if period_ch > 0 and period_ch < 5:
        date = ask_date(op_list[period_ch])
        if date != 'fail':
            filename = fetch_data(op_list[period_ch], date)
        else:
            print 'Please input a valid date with format YYYY-MM-DD!'
        break;
    elif period_ch == 5:
        sys.exit();
    else:
        print 'Please input the value!!'

tree = et.ElementTree(file=filename + '.xml')
tree.getroot()
root = tree.getroot()

### Started parsing xml ###
show_in_screen = False
show_op = raw_input('Ready parsing the xml data, would you like shows the data in the screen?[Y/N]')
if show_op[0] == 'Y' or show_op[0] == 'y':
    show_in_screen = True
print 'Start parsing the xml data and store the result to %s.csv ' % filename
pagetitles_file = open(filename + '.csv','w')
for child in root:
    parse_data(child, pagetitles_file, show_in_screen)
pagetitles_file.close()
print 'Parse the xml data done!'
