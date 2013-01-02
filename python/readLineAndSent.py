#!/usr/bin/env python

import sendMailFunc
import sys
import getopt
import time

try:
    opts, args = getopt.getopt(sys.argv[1:], "", ["file=", "dest="])
except getopt.error, msg:
    print 'python %s --file [filename] --dest [mail address]' % sys.argv[0]
    sys.exit(2)

# process sender and receiver
filename = ''
dest = ''

for o, a in opts:
    if o == "--file":
        filename = a
    elif o == "--dest":
        dest = a

if filename == '' or dest == '':
    print 'python %s --file [filename] --dest [mail address]' % sys.argv[0]
    sys.exit(2)

f = open(filename)

for address in iter(f):
    sendMailFunc.sendSubscribe(address, dest)
    time.sleep(5)
f.close()
