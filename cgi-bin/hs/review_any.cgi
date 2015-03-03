#!/usr/local/bin/perl
use strict;

=head1 NAME

review_any.cgi - allows and admin or coach to grab a previously taken assessment and display in the
selected format

=head1 DESCRIPTION

Use this script as the ACTION target for each previously taken assessment
or as a link to a different output format.

=head1 INPUT

This script depends on certain control parameters to tell it what to
do.

	assessment	- the type of assessment (FIT, CRC, etc.)
	user_hs_ident   - the user id (hs_uid) of the record to be retrieved, so you need to
			  know the xnum and the user id
	xnum            - the record number from the database to display
	output_format   - the type of output you want (HTML, PDF, etc.)
	dump_it         - will dump the user hash to a file in the shared directory, the number
	                  you set dump it to will be part of the output file name.
	send_it         - will dump the user hash to a file in the shared directory
	                  and send it to HealthStatus for examination.
	get_dumped      - will retrieve a dumped user hash and show the report

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
object is given to a C<HealthStatus> object and the health
assessment is done. See the C<OUTPUT> section for more
details.

Three parameters together specify the birthday -- C<birth_date>,
C<birth_month>, and C<birth_year>.  The script checks the combination
of these values to enusre they represent a valid date, although not
necessarily a reasonable birthday for anyone presently taking the
test. The values of these fields are the numberic representations
of their context.  For example, January is represented as C<1>. Note
the the month representation is the common sense version rather than
the computer language start-from-zero version.

=head2 OUTPUT

When the script executes it performs the health assessment and gives
output according to what it sees in the parameter C<output_format>, which
can be C<html>, C<pdf>, or C<xml>, although it can depend on the
particular assessment.

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

use lib dirname(rel2abs($0)),'.','/usr/local/www/vhosts/managed2/modules/pdf', '/usr/local/www/vhosts/managed2/modules';

use vars qw( $Debug $production $cook $config_file $nph);

if (!do('common.inc')) {
   my $error = $@ ? $@
             : $! ? $!
             : 'did not return a true value';
   die("Unable to load common stuff: $error\n");
}
# Removing warnings in log while module is being used with CGI version 4 or above
$CGI::LIST_CONTEXT_WARN = 0;
use HealthStatus qw ( error html_error fill_and_send );
use Date::Calc;
use HealthStatus::Constants;
use HealthStatus::CalcRisk;
use CGI::Carp;

my $input = new CGI();
my $config = getConfig($input->param('extracfg'));

my $session = new CGI::Session(undef, undef, {Directory=>'../../sessions'}) or die CGI::Session->errstr;
$cook = $session->param('hs_ident') || $input->param('hs_ident') || $input->cookie('hs_ident');

$session->clear();
$session->save_param($input);
$session->param('hs_ident',$cook);
$session->clear(['page', 'prev.x', 'prev.y', 'next.x', 'next.y', 'next', 'prev']);
my @image_submits = map { lc } grep { m/\.[xy]$/i } $session->param;
$session->clear(\@image_submits);
$session->load_param($input);

$session->flush();

my %hash = map { $_, $input->param($_) } $input->param();

my %config = map { $_, $config->$_ } $config->directives;

$hash{config} = \%config;

my %input = $input->Vars();

############################################################################
### Comment out the following line before going into production ############
$Debug = $input->param("HS_Debug") || $ENV{HS_DEBUG} || $Debug if !$production;
#### only uncomment if you need to debug the input scripts      ############
############################################################################

if ($Debug) {
	print "Content-type: text/plain\n\n";
	print "Modules Versions:\nHealthStatus - $HealthStatus::VERSION\nHealthStatus::Authenticate - $HealthStatus::Authenticate::VERSION\nHealthStatus::Database - $HealthStatus::Database::VERSION\n";
	print "HealthStatus::Config - $HealthStatus::Config::VERSION\nHealthStatus::User - $HealthStatus::User::VERSION\n\n";
	$config->pretty_print;
}

$ENV{TMPDIR} = $config->authenticate_dir;
$ENV{TEMP} = $config->authenticate_dir;

# %Allowed_assessments not only tells us which assessments we
# can do, but how many pages of input to expect
my @assessments = @{$$config{common_assessments}};

my %Allowed_assessments = map
	{
	my $assessment = lc $_;
	my $method     = lc ${_}."_max_pages";
	my $max_pages  = $config->$method;

	( $assessment, $max_pages )
	} @{$$config{common_assessments}};

my $assessment = lc $input->param('assessment');
print "Assessment = $assessment\n" if $Debug;
error( "The assessment [$assessment] is not allowed" )
	unless exists $Allowed_assessments{$assessment};

delete($hash{'Submit.x'}) if (exists($hash{'Submit.x'}));
delete($hash{'Submit.y'}) if (exists($hash{'Submit.y'}));
delete($hash{'action'}) if (exists($hash{'action'}));

# authenticate_user redirects the user if they not allowed to
# view this page
my $user = authenticateUser(["admin"], $input, $config) or die "You should never see this message." if(!(lc $input->param('api_mchcp')));

my $got_it = 0;
my $user1 = HealthStatus::User->new( \%hash );

$user1->db_id( $input->param('user_hs_ident') );

if( $input->param('get_dumped') ) {

	my $dumpfile = $config->authenticate_dir . "/" . uc($input->param('assessment')) . "_dump_of_" . $input->param('get_dumped') . ".user";

	$user1 = do $dumpfile;

	bless($user1, "HealthStatus::User");

	$user1->{config} = \%config;

	$user1->pretty_print if $Debug;

	++$got_it;
}else{

	my $db = HealthStatus::Database->new( $config );

	$db->debug_on( \*STDERR ) if $Debug;

	$got_it = $db->get_users_assessment( $user1, $config, uc $input->param('assessment'), $input->param('xnum') );

	$user1->pretty_print if $Debug;

	$db->finish;

	$db->disconnect;
	}

if(!$got_it) { 	print $input->redirect( -uri=> $config->member_page ); exit;  }

my %mail_hash;

if( $input->param('dump_it') ){
	$Data::Dumper::Indent = 1;
	$Data::Dumper::Maxdepth = 1;

	my $dumpfile = $config->authenticate_dir . "/" . uc($input->param('assessment')) . "_dump_of_" . $input->param('dump_it') . ".user";

	open(DUMPFILE, ">$dumpfile" ) or die "Failed dump user - $dumpfile\n$!";
	print DUMPFILE Dumper($user1);
	close (DUMPFILE);

	if( $input->param('send_it') ){
		%mail_hash = ( body => 'Review_any dump',
				  attach => $dumpfile,
				  short_attach => uc($input->param('assessment')) . "_dump_of_" . $input->param('dump_it') . ".user",
				  );
		}
	}

my $health = HealthStatus->new(
	{
	assessment => uc($input->param('assessment')),
	user       => $user1,
	config     => $config_file,
	extraconfig => $input->param('extracfg'),
	}
	);

$health->send_email_to_HS( $user1, \%mail_hash ) if( $input->param('send_it') );

$user1->set_non_standard;

$health->assess( $user1 );

my $m_format = $input->param('output_format') || DEFAULT_OUTPUT_FORMAT ;

my $data = $health->output( lc $m_format, $hash{template},$session );

my $mime = $health->mime(  lc $m_format );

if ($data ne 'PDF' && $data ne 'PDFE') { print $input->header(), $data;	}

=head1 BUGS

* none that i've found so far.

=head1 TO DO

* nothing yet

=head1 AUTHOR

Greg White <gwhite@healthstatus.com>

=head1 COPYRIGHT

Copyright 2001-2008, HealthStatus.com

=cut

1;
