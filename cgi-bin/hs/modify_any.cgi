#!/usr/local/bin/perl
use strict;

=head1 NAME

modify_any.cgi - grab a previously taken assessment and display in the
on an html form for editing

=head1 DESCRIPTION

Use this script to modify the data associated with a specific assessment.
Judicious use is preferred.

=head1 INPUT

This script depends on certain control parameters to tell it what to
do.

	assessment	- the type of assessment (FIT, CRC, etc.)
	xnum            - the record number from the database to display
	get_dumped      - will retrieve a dumped user hash and show the data
	modify		- if empty the program will load the record
			  if true the program will update the record in the database

The script uses these parameters to load certain configuration
directives. The script also retrieves this cookie from the user:

'hs_ident'	- a cookie or hidden form field containing the
		file name of a temporary file to use for authentication
		by C<HealthStatus::Authenticate> and to collect initial
		user information in a more secure manner than passing
		hidden form fields. This file points to another configuration
		file or overrides values in the default configuration
		file.  Config data is collected by
		C<HealthStatus::Config>

The script takes all of the parameters and creates a
C<HealthStatus::Database> object the information is retrieved
which creates a C<HealthStatus::User> object.  That
object is then written onto a form, once the form is edited, the
data is saved to the database.

=head1 ERRORS

This script will issue an error if it cannot read the
configuration or template file.  A short, vague message
is sent to the browser and a more detailed message should
show up in the error log.

If the script cannot recognize the value of the control parameter
C<assessment>, or the control parameter C<name>, it outputs
an error page.  The user is redirected to the login page or timeout
page if they cannot be authenticated.

=cut

use File::Basename        qw( dirname );
use File::Spec::Functions qw( rel2abs );

use lib 'dirname(rel2abs($0))','.','/usr/local/www/vhosts/managed1/modules/pdf', '/usr/local/www/vhosts/managed1/modules';

use vars qw( $Debug $production $cook $config_file $nph);

if (!do('common.inc')) {
   my $error = $@ ? $@
             : $! ? $!
             : 'did not return a true value';
   die("Unable to load common stuff: $error\n");
}

use HealthStatus qw( fill_and_send error html_error );
use HealthStatus::CalcRisk;
use HealthStatus::Config;
use HealthStatus::Constants;
use HealthStatus::Database;
use HealthStatus::User;
use HealthStatus::Authenticate;
use Data::Dumper;

my $input = CGI->new();
my $config = getConfig($input->param('extracfg'));

my @assessments_allowed = @{$$config{common_assessments}};

print "Content-type: text/plain\n\n" if $Debug;

# authenticate_user redirects the user if ey is not allowed to
# view this page
my $user = authenticateUser(["admin", 'coach'], $input, $config) or die "You should never see this message.";

my $assessment = lc $input->param('assessment');
print "Assessment = $assessment\n" if $Debug;

my %hash = map { $_, $input->param($_) } $input->param();

my %config = map { $_, $config->$_ } $config->directives;

$hash{config} = \%config;

delete($hash{'Submit.x'}) if (exists($hash{'Submit.x'}));
delete($hash{'Submit.y'}) if (exists($hash{'Submit.y'}));
delete($hash{'action'}) if (exists($hash{'action'}));

$user->pretty_print if $Debug;

my $temp_file_name = $config->authenticate_dir;
my $temp_file = $input->cookie('hs_ident') || $input->param('hs_ident') || '10001';

my $got_it = 0;
my $user1 = HealthStatus::User->new( \%hash );

$user1->db_id( $input->param('user_hs_ident') );

if($input->param('modify')){
	my $db = HealthStatus::Database->new( $config );

	$db->debug_on( \*STDERR );

	$got_it = $db->update_users_assessment( $user1, uc $input->param('assessment'), 'where xnum = ' . $input->param('xnum') );

	$db->finish;

	$db->disconnect;

	$hash{msg} = "Record has been updated, close this window";

	my $template = $config->template_directory . "admin_info_page.tmpl";
	print "template is $template<br>\n" if $Debug;

	fill_and_send( $template, $user1, \%hash, $config->html_use_ssi );

	exit;

	}

if( $input->param('get_dumped') ) {

	my $dumpfile = $config->authenticate_dir . "/" . uc($input->param('assessment')) . "_dump_of_" . $input->param('get_dumped') . ".user";

	$user1 = do $dumpfile;

	bless($user1, "HealthStatus::User");

	$user1->{config} = \%config;

	$user1->pretty_print if $Debug;

	++$got_it;
	}
else	{

	my $db = HealthStatus::Database->new( $config );

	$db->debug_on( \*STDERR ) if $Debug;

	$got_it = $db->get_users_assessment( $user1, $config, uc $input->param('assessment'), $input->param('xnum') );

	$user1->pretty_print if $Debug;

	$db->finish;

	$db->disconnect;
	}

if($user1->feet < 2 && $user1->height){
	my $height = $user1->height;
	$hash{feet} = int($height/12);
	$hash{inches} = $height%12;
	}

$hash{modify} = 1;

my $template = $config->template_directory . $assessment . "_qbatch.html";
print "template is $template<br>\n" if $Debug;

fill_and_send( $template, $user1, \%hash, $config->html_use_ssi );

=head1 BUGS

* none that i've found so far.

=head1 TO DO

* nothing yet

=head1 AUTHOR

Greg White <gwhite@healthstatus.com>

=head1 COPYRIGHT

Copyright 2001-2009, HealthStatus.com

=cut

1;
