#!/usr/bin/perl

use LWP::UserAgent;
use URI::URL;
use Mail::Sendmail;
use Date::Calc qw(:all);

use vars qw($checkme);
$checkme = 1;
## begin configure

my ($year,$month,$day) = Today();

my $base_dir = '/usr/local/www/vhosts/healthstatus.com/template/';
my %bad_list;
my $yes_bad = 0;

@CHECK =                        # list of links templates
  qw(crc_links.tmpl drc_links.tmpl hra_links.tmpl gha_links.tmpl gwb_links.tmpl fit_links.tmpl);

$ua = new LWP::UserAgent;
$ua->agent("good_link_verify/1.0");

$| = 1;

MAINLOOP:
  while ($these_templates = shift @CHECK) {
    my $tmp = $base_dir . $these_templates;
    my $tmp1 = '';
    open LINK, $tmp;
	while (<LINK>){
		$tmp1 .= $_;
		}
    close LINK;
    eval $tmp1;
    foreach my $tmp2 (@links){
      $thisurl = $$tmp2[1];
      warn "fetching $$tmp2[0]\n";
      $request = new HTTP::Request('GET',$thisurl);
      $response = $ua->request($request); # fetch!

      unless ($response->is_success) {
        ++$yes_bad;
        $tmp3 = "Cannot fetch $these_templates - $$tmp2[0] - $thisurl (status ".  $response->code. " ". $response->message.")\n";
      	$bad_list{$tmp}{$thisurl} = $tmp3;
        next;
      }
    next;
    }
  next;
  }
if($yes_bad) {
	$tmp4='';
	foreach my $t1 (sort keys %bad_list){
		foreach my $t2 (sort keys %{$bad_list{$t1}}){
			$tmp4 .= "$bad_list{$t1}{$t2}";
			}
		}
	my %mail = (   To      => 'gwhite@healthstatus.com',
		    From    => 'webmaster@healthstatus.com',
		    Subject => "Bad link count - $yes_bad",
		    Message => $tmp4,
		    smtp    =>  'mail.healthstatus.com'
		   );
	sendmail(%mail);
	}