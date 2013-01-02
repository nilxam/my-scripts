#!/usr/bin/python

import smtplib
import getopt
import sys
import string

try:
    opts, args = getopt.getopt(sys.argv[1:], "", ["sender=", "receiver="])
except getopt.error, msg:
    print 'python sendMail.py --sender [sender address] --receiver [receiver address] '
    sys.exit(2)

# process sender and receiver
sender = ''
receiver = ''

for o, a in opts:
    if o == "--sender":
        sender = a
    elif o == "--receiver":
        receiver = a

if sender == '' or receiver == '':
    print 'python sendMail.py --sender [sender address] --receiver [receiver address] '
    sys.exit(2)

# scheduled the content
sender_str = 'From:'
receiver_str = 'To:'

sender_str += sender
receiver_str += receiver

message = sender_str + '\n' + receiver_str + '\n'
message += """Subject: subscribe request

Subscribe for registered people of osc12
"""

# managed to send mail
try:
  smtpObj = smtplib.SMTP('localhost')
  smtpObj.sendmail(sender, receiver, message)
  print "Successfully sent email"
except SMTPException:
  print "Error: unable to send email"
