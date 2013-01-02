# this script will open a file with email addresses in it, then extract
# those address and write them to a new file

import os
import re
import getopt
import sys
import string
import codecs

def isEmailAddress(string):
    return email_prog.match(string)

def writeFile(filename, separator='\n', encoding=None):
    separator_replace = {
            'space': ' ',
            'newline': '\n',
    }
    if not os.path.isfile(filename):
        raise IOError("%s is not a file." % filename)
    results = set()
    with codecs.open(filename, 'rb', encoding) as f:
        for line in f:
            results.update(email_prog.findall(line))
    for k, v in separator_replace.iteritems():
        separator = separator.replace(k, v)
    #print(separator.join(results))
    f = open(newfilename, 'w')
    f.write(separator.join(results))
    f.close()
    print "File written."

try:
    opts, args = getopt.getopt(sys.argv[1:], "", ["readfile=", "writefile="])
except getopt.error, msg:
    print 'python sendMail.py --readfile [filename] --writefile [filename] '
    sys.exit(2)

# process sender and receiver
readfile = ''
writefile = ''

for o, a in opts:
    if o == "--readfile":
        readfile = a
    elif o == "--writefile":
        writefile = a

if readfile == '' or writefile == '':
    print 'python sendMail.py --readfile [filename] --writefile [filename] '
    sys.exit(2)

# vars for filenames
filename = readfile
newfilename = writefile

# Regular expression matching according to RFC 2822 (http://tools.ietf.org/html/rfc2822)
rfc2822_re = r"""(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])"""
email_prog = re.compile(rfc2822_re, re.IGNORECASE)

# read file
if os.path.exists(filename):
  data = open(filename,'r')
  bulkemails = data.read()
else:
  print "File not found."
  raise SystemExit

# question
def overwrite_ok():
  response = raw_input("Are you sure you want to overwrite "+str(newfilename)+"? Yes or No\n")
  if response == "Yes":
    writeFile(filename)
  elif response == "No":
    print "Aborted."
  else:
    print "Please enter Yes or No."
    overwrite_ok()

# write/overwrite
if os.path.exists(newfilename):
  overwrite_ok()
else:
  writeFile(filename)
