#!/usr/bin/perl


use Mail::IMAPClient;
use Term::ReadKey;
use Net::SMTP;

use strict;
use warnings;

sub send_mail {
    my ($from, $to_addr, $subject_input, $body_input);

    #########-- Enter the Details here --###################################

    my $sender             = shift;
    my $receiver           = shift;
    my $subject            = shift;
    my $body               = shift;
    my $mailhost           = 'smtp.novell.com';
    my $sender_name        = 'Max Lin';
    my $password           = 'xxx';


    my $smtp = new Net::SMTP(
        $mailhost,
        Port    =>      25,
        #Timeout =>      10
        Debug   =>      0
    );
    $smtp->auth ( $sender, $password ) or die "Could not authenticate $!";

    print "sending to $receiver\n";

#  -- Enter sender mail address. --
    $smtp->mail($sender);

#  -- Enter recipient mails address. --
    $smtp->recipient($receiver);

    $smtp->data();

# -- This part creates the SMTP headers you see. --
    $smtp->datasend("To: <$receiver> \n");
    $smtp->datasend("From: $sender_name <$sender> \n");
    $smtp->datasend("Content-Type: text/plain \n");
    $smtp->datasend("Subject: Re: $subject");

# -- line break to separate headers from message body. --
    $smtp->datasend("\n");

    $smtp->datasend($body);

    $smtp->datasend("\n");
    $smtp->dataend();

    $smtp->quit;

}

my $imap = Mail::IMAPClient->new(
    Server   => 'imap.googlemail.com',
    User     => 'xxx@xxx.xx',
    Password => 'xxx',
    Ssl      => 1,
    Uid      => 1,
    Port => 993
) or die "new failed: $@\n";;


$imap->select('promodvd') 
    or die "Could not select: $@\n";

my @unread = $imap->search('unseen') or warn "Could not find unseen msgs: $@\n";

foreach my $msg (@unread) {

    my $key;
    print "From: ", $imap->get_header($msg, 'From'), "\n";
    print "Subject: ", $imap->subject($msg), "\n";

# now ask what to do...

    ReadMode('cbreak');
    do {
        print "What to do? (I)gnore, (R)eject, (S)chedule, (O)ut of media, (F)ull message: \n";
        $key = ReadKey(0);
        if ($key =~ /[fF]/) {
            my $message = $imap->body_string ($msg);
            print "$message\n";
        }
    } until ($key =~ /[IiRrsSoO]/ );
    ReadMode('normal');

    &schedule_file ($msg) if (uc $key eq 'S');
    &reject ($msg) if (uc $key eq 'R');
    &ignore ($msg) if (uc $key eq 'I');
    &oom ($msg) if (uc $key eq 'O');

    #Just for testing!
    #$imap->unset_flag('\Seen',$msg)
    #or die "Could not unset_flag: $@\n";
   }

# Close the folder
$imap->close;

$imap->logout
    or die "Logout error: ", $imap->LastError, "\n";

print "Have a lot of fun!\n";

sub schedule_file {
    my ($msg) = @_;
    my ($message, $send_msg, $from, $subject, $text, $line);

    $imap->set_flag('\Seen',$msg);

    my $uidlist =$imap->copy('promodvd_review', $msg)
	or die ("could not copy message to DVD-Sending: $@\n"); 
    $imap->set_flag ("Answered", [$msg]);

    open my $pipe, "|grep --after-context=2 CSV |tail -n1 >> ~/New-PromoDVD-orders.csv"
	or die("Open pipe failed: $!");

    $imap->message_to_file($pipe, $msg);

     close $pipe
       or die("Close pipe error: $!");

    $message = $imap->message_string ($msg);
    $from= $imap->get_header($msg, 'From');
    $subject = $imap->get_header($msg, 'Subject');

    $text = "Thanks, your order has been scheduled and will be processed soon.\nWe will ship based on availabilty of what we have and thus might change your request.\n\nNote that the openSUSE project will only cover cost of material and transportation,\nyou have to take care of any customs or tax costs.\n\nNote. We decided decrease european quantities by 50%, therefore the numbers that you received is not as expected.\n\nCheers,\nMax\n\n-- \n";
    open SIGNATURE, "< $ENV{HOME}/.signature" 
      or die ("could not read $ENV{HOME}/.signature: $?");
    while ($line = <SIGNATURE>) {
	last if $line =~ /EOF/;
	$text .= $line;
    }
    close SIGNATURE;

    send_mail('xxx@xx.xx', $from, $subject, $text);
    printf "Scheduled...\n"
}

sub reject {

    my ($msg) = @_;
    my ($message, $send_msg, $from, $subject, $text, $line);

    $imap->set_flag ("Answered", [$msg]);

    $from= $imap->get_header($msg, 'From');
    $subject = $imap->get_header($msg, 'Subject');

    $text= <<'EOF';
Hi,

Sorry, we will not fullfill your request.  The costs and logistics for
sending out DVDs worldwide incl. the overhead of customs, is so great
that we concentrate on larger events and orders and cannot fullfill
every requests.

Please download the media from http://software.opensuse.org

If your connection is too slow, contact your local ambassador
(http://en.opensuse.org/openSUSE:Ambassadors_list) for an event in
your area where you can get a free copy.

Btw. you can also buy openSUSE as a box product for details read:
http://en.opensuse.org/Buy_openSUSE

There are also a number of shops that produce and ship single DVDs
including the following:

  http://www.osdisc.com/cgi-bin/view.cgi/products/linux/suse
  http://easylinuxcds.com/index.php?app=ccp0&ns=prodshow&ref=opensuse
  http://www.linuxiso.co.uk/index.php
  http://www.thelinuxcdstore.com/index.php?cPath=25&osCsid=60f8bbf19445ce5326bdd21b4b541864
  http://on-disk.com/index.php/cPath/28_168_408?osCsid=ff5cc02525db698843651b3533e7009b
EOF

    $text .= "-- \n";

    open SIGNATURE, "< $ENV{HOME}/.signature" 
      or die ("could not read $ENV{HOME}/.signature: $?");
    while ($line = <SIGNATURE>) {
	last if $line =~ /EOF/;
	$text .= $line;
    }
    close SIGNATURE;

    send_mail('xxx@xxx.xx', $from, $subject, $text);
    printf "Rejected...\n"
}

sub oom {

    my ($msg) = @_;
    my ($message, $send_msg, $from, $subject, $text, $line);

    $imap->set_flag ("Answered", [$msg]);

    $from= $imap->get_header($msg, 'From');
    $subject = $imap->get_header($msg, 'Subject');

    $text= <<'EOF';
Hi,

Sorry, we cannot not fullfill your request since we're out of 
openSUSE media for now. We will produce again media after the
next release.

If you really need media, please download the media from 
http://software.opensuse.org

There are also a number of shops that produce and ship single DVDs
including the following:

  http://www.osdisc.com/cgi-bin/view.cgi/products/linux/suse
  http://easylinuxcds.com/index.php?app=ccp0&ns=prodshow&ref=opensuse
  http://www.linuxiso.co.uk/index.php
  http://www.thelinuxcdstore.com/index.php?cPath=25&osCsid=60f8bbf19445ce5326bdd21b4b541864
  http://on-disk.com/index.php/cPath/28_168_408?osCsid=ff5cc02525db698843651b3533e7009b
EOF

    $text .= "-- \n";

    open SIGNATURE, "< $ENV{HOME}/.signature" 
      or die ("could not read $ENV{HOME}/.signature: $?");
    while ($line = <SIGNATURE>) {
	last if $line =~ /EOF/;
	$text .= $line;
    }
    close SIGNATURE;

    send_mail('xxx@xx.xx', $from, $subject, $text);
    printf "OOm...\n"
}

sub ignore {

    my ($msg) = @_;

    $imap->unset_flag('\Seen',$msg)
	or die "Could not unset_flag: $@\n";

    printf "Ignored...\n"
}
