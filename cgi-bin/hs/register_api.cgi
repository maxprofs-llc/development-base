#!/usr/bin/perl
use strict;

=head1 NAME

register_api.cgi - authenticate api users to view html report.

=head1 DESCRIPTION

Use this script as the program to submit login information,create cookie and redirect to reporting page.

=cut

#  This includes the current directory in the list of places to check for
# modules and other files, mainly for NT systems.

use File::Basename        qw( dirname );
use File::Spec::Functions qw( rel2abs );

use lib dirname(rel2abs($0)),'.','/usr/local/www/vhosts/managed2/modules/pdf', '/usr/local/www/vhosts/managed2/modules';

use vars qw( $Debug $production $cook $config_file $nph %Allowed_assessments);

if (!do('common.inc')) {
   my $error = $@ ? $@
             : $! ? $!
             : 'did not return a true value';
   die("Unable to load common stuff: $error\n");
}

use CGI qw(-no_xhtml -debug);
if (!$production) {
	use CGI::Carp qw(fatalsToBrowser);
	}
else {
	use CGI::Carp;
	}
$CGI::POST_MAX=1024 * 100;  # max 100K posts
$CGI::DISABLE_UPLOADS = 1;  # no uploads
use Date::Calc;
use Text::Template;
use Mail::Sendmail;
use HTML::FillInForm;

use HealthStatus qw( fill_and_send error check_digit );
use HealthStatus::Authenticate;
use HealthStatus::Config;
use HealthStatus::Constants;
use HealthStatus::Database;
use HealthStatus::User;
use Data::Dumper;

CGI->nph($nph) if $nph;
my $input = CGI->new();
my $config = getConfig($input->param('extracfg'));

my $session = new CGI::Session(undef, undef, {Directory=>'../../sessions'}) or die CGI::Session->errstr;
$session->save_param();

my %hash = map { $_, $input->param($_) } $input->param();

my %config = map { $_, $config->$_ } $config->directives;

delete($hash{'Submit.x'}) if (exists($hash{'Submit.x'}));
delete($hash{'Submit.y'}) if (exists($hash{'Submit.y'}));
delete($hash{'action'}) if (exists($hash{'action'}));

$hash{config} = \%config;

my %input = $input->Vars();

$cook = $session->param('hs_ident') || $input->param('hs_ident') || $input->cookie('hs_ident');

$session->flush();

############################################################################
### Comment out the following line before going into production ############
$Debug = $input->param("HS_Debug") || $ENV{HS_DEBUG} || $Debug if !$production;
#### only uncomment if you need to debug the input scripts      ############
############################################################################

if( $Debug )
	{
	print "Content-type: text/plain\n\n";
	print "$ENV{SCRIPT_NAME} - $ENV{QUERY_STRING}\n";
	print "Modules Versions:\nHealthStatus - $HealthStatus::VERSION\nHealthStatus::Authenticate - $HealthStatus::Authenticate::VERSION\nHealthStatus::Database - $HealthStatus::Database::VERSION\n";
	print "HealthStatus::Config - $HealthStatus::Config::VERSION\nHealthStatus::User - $HealthStatus::User::VERSION\n\nText::Template - $Text::Template::VERSION\nHTML::FillInForm - $HTML::FillInForm::VERSION\n\n";
	foreach my $key ( sort keys %input )
		{
		print "\t$key\t\t$input{$key}\n";
		}
	print "Cookie hs_ident = " .$input->cookie('hs_ident') ."\n";
	$config->pretty_print if $Debug;

	}

my $temp_file_name = $config->authenticate_dir;
my $temp_file = $input->param('hs_ident') || $input->cookie('hs_ident') || '0';

print "Temp file = $temp_file\n$temp_file_name\n" if $Debug;

my $db = HealthStatus::Database->new( $config );

if(!$hash{db_number}) { $hash{db_number} = $temp_file || '' }

$db->debug_on( \*STDERR ) if $Debug;

my $user = HealthStatus::User->new( \%hash );

$user->pretty_print if $Debug;

my $approved = HealthStatus::Authenticate->new( $config, $temp_file_name, $temp_file );

$approved->debug_on( \*STDERR ) if $Debug;
my $status = '';
$status = $approved->login( $config, $user );

print "login - $status\n$user->db_number\n\n" if $Debug;
if ($status eq APPROVED)
{
	my $tnum = $user->db_number;
	$hash{hs_ident}=$tnum;
	my $cookie = $input->cookie(-name=>'hs_ident', -value=>"$tnum");	
	my $session_cookie = $input->cookie( -name   => $session->name, -value  => $session->id );
	my $xnum = $input->param('xnum');
	my $user_hs_ident = $input->param('user_hs_ident');
	my $assessment = uc $input->param('assessment');
	
	my $goto_page = "https://base1.hra.net/cgi-bin/hs/review_any.cgi?user_hs_ident=".$user_hs_ident."&assessment=".$assessment."&xnum=".$xnum;
			
	print $input->redirect( -cookie=>[$cookie,$session_cookie], -uri=>$goto_page );	
}


=head1 COPYRIGHT

Copyright 2001-2014, HealthStatus.com

=cut

1;
