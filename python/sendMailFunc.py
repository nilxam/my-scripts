#!/usr/bin/python

import smtplib
import sys
import string


def sendSubscribe(senderAddress, receiverAddress):
    # process sender and receiver
    sender = str(senderAddress)
    receiver = str(receiverAddress)

    if sender == '' or receiver == '':
        print 'Lost sender or receiver address'
        sys.exit(2)

    # scheduled the content
    sender_str = "From:%s" % sender
    receiver_str = "To:%s" % receiver

    #message = sender_str + '\n'
    message = receiver_str + '\n'
    #message += 'Subject: subscribe request\n\nSubscribe for registered people of osc12\n'
    message += """Subject: subscribe request

    Subscribe for registered people of osc12
    """

    # managed to send mail
    try:
        smtpObj = smtplib.SMTP('localhost')
        smtpObj.sendmail(sender, receiver, message)
        print "Successfully sent email by %s" % sender
    except SMTPException:
        print "Error: unable to send email"
