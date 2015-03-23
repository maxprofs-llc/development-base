#!/usr/local/bin/perl
use strict;

=head1 NAME

review.cgi - grab a previously taken assessment and display in the
selected format

=head1 DESCRIPTION

Use this script as the ACTION target for each previously taken assessment
or as a link to a different output format.

=head1 INPUT

This script depends on certain control parameters to tell it what to
do.

	assessment	- the type of assessment (FIT, CRC, etc.)
	xnum            - the record number from the database to display
	output_format   - the type of output you want (HTML, PDF, etc.)
	xnum1		- optional second assessment for a comparitive report

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

use vars qw( $Debug $production %Tables $cook $config_file $nph);
if (!do('common.inc')) {
   my $error = $@ ? $@
             : $! ? $!
             : 'did not return a true value';
   die("Unable to load common stuff: $error\n");
}

use HealthStatus qw ( error html_error fill_and_send  send_pdf_email);
use HealthStatus::Constants;
use Date::Calc;
use HealthStatus::CalcRisk;
use HealthStatus::Authenticate;
use HealthStatus::Config;
use HealthStatus::Database;
use CGI::Carp;
use Data::Dumper;
# Removing warnings in log while module is being used with CGI version 4 or above
$CGI::LIST_CONTEXT_WARN = 0;

my $input = new CGI();
my $config = getConfig($input->param('extracfg'));
my $session = new CGI::Session(undef, undef, {Directory=>'../../sessions'}) or die CGI::Session->errstr;
$cook = $session->param('hs_ident') || $input->param('hs_ident') || $input->cookie('hs_ident');
carp "Session id in review is: ".$session->id()." cook is: ".$cook;
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

if (!do($config->conf_config_dir.'/db_hs.conf')) {
   my $error = $@ ? $@
             : $! ? $!
             : 'did not return a true value';
   die("Unable to load ".$config->conf_config_dir."/db_hs.conf: $error\n");
}
############################################################################
$Debug = $input->param("HS_Debug") || $ENV{HS_DEBUG} || $Debug if !$production;
#### only uncomment if you need to debug the input scripts      ############
############################################################################

if ($Debug) {
	print "Content-type: text/plain\n\n";
	print "$ENV{SCRIPT_NAME} - $ENV{QUERY_STRING}\n";
	print "Modules Versions:\nHealthStatus - $HealthStatus::VERSION\nHealthStatus::Authenticate - $HealthStatus::Authenticate::VERSION\nHealthStatus::Database - $HealthStatus::Database::VERSION\n";
	print "HealthStatus::Config - $HealthStatus::Config::VERSION\nHealthStatus::User - $HealthStatus::User::VERSION\n\nText::Template - $Text::Template::VERSION\nHTML::FillInForm - $HTML::FillInForm::VERSION\n\n";
	foreach my $key ( sort keys %input )
		{
		print "\t$key\t\t$input{$key}\n";
		}
	print "Cookie hs_ident = " .$input->cookie('hs_ident') ."\n";
	print "Xnum values xnum = " .$input->param('xnum') . "   xnum1 = " .$input->param('xnum1') ."\n";
	}

$ENV{TMPDIR} = $config->authenticate_dir;
$ENV{TEMP} = $config->authenticate_dir;

# %Allowed_assessments not only tells us which assessments we
# can do, but how many pages of input to expect
my %Allowed_assessments = map
	{
	my $assessment = lc $_;
	my $method     = lc $_."_max_pages";
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
my $user = authenticateUser('all', $input, $config) or die "You should never see this message.";

my $temp_file_name = $config->authenticate_dir;
my $temp_file = $input->param('hs_ident') || $input->cookie('hs_ident') || '10001';

$user->db_number ( $temp_file );

my $approved = HealthStatus::Authenticate->new( $config, $temp_file_name, $temp_file );

my $status = $approved->check( $config, $user );

my $user1; # just in case this is a comparitive;

my $db = HealthStatus::Database->new( $config );
my $language = $input->param('language');

$db->debug_on( \*STDERR ) if $Debug;
my $domain = $ENV{SERVER_NAME};
my @domain_parts = split /\./,$domain;
my $subdomain = $domain_parts[0];
if($subdomain eq 'base1' && ($language eq 'select' || ($language eq 'select' && $input->param('output_format') eq 'PDF'))){
	 $hash{status}='retake';
	 $hash{assessment}= $input->param('assessment');
	 $hash{xnum}= $input->param('xnum');
	 $hash{output_format}= $input->param('output_format');
	 $hash{pretty_date}= $input->param('pretty_date');	
	 my $form = $config->template_directory . 'select_language_lightwindow.tmpl';
	 fill_and_send( $form, $user, \%hash, $config->html_use_ssi );
	 exit;
	
}

if($input->param('xnum1') > 1){
	print "xnum1 found " . $input->param('xnum1') . "\n" if $Debug;
	$user1 = HealthStatus::User->new( \%hash );
	$user1->db_number ( $input->cookie('hs_ident') );
	my $status = $approved->check( $config, $user1 );
	$db->get_users_assessment( $user1, $config, uc $input->param('assessment'), $input->param('xnum1') );
	$user1->set_non_standard;
	print "xnum1 data before assessment\n" if $Debug;
	$user1->pretty_print if $Debug;
	$user->pretty_print if $Debug;
	my $health1 = HealthStatus->new(
		{
		assessment => uc($input->param('assessment')),
		user       => $user1,
		config     => $config_file,
		extraconfig => $input->param('extracfg'),
		}
		);

	$health1->assess( $user1 );
	print "xnum1 data after assessment\n" if $Debug;
	$user1->pretty_print if $Debug;
}

#####Check if data is good enough
my (%inches_hs_uids,$field,@existing_column_db);
my $table = $Tables{uc($assessment)};
if($table eq 'hs_fitdata'){
	$field = 'Height';
}else{
	$field = 'Inches';
}
my $data_xnum = $input->param('xnum');
my $return_val = $db->check_temp_data($table,$field,$data_xnum);

# my $dbh  =  DBI->connect('dbi:mysql:hs_mchcptest_data:local-db.healthstatus.com', 'As!an9books', 'hrX1hs0' );

# my $column_data = "SHOW COLUMNS FROM $table";
# my $fields_from_db = $dbh->prepare($column_data);
# $fields_from_db->execute();
 # while (my @row = $fields_from_db->fetchrow_array()) {
	# next if($row[0] eq 'hs_uid' || $row[0] eq 'unum' || $row[0] eq 'xnum' || $row[0] eq 'adate');
	# push(@existing_column_db, $row[0]); 
# }

#Get all fields having NULL values
# my $inches_str = "SELECT * FROM $table WHERE xnum=$data_xnum AND $field IS NULL";
# print STDERR "inches_str===$inches_str\n"; 
# my $hsuid_from_gha = $dbh->prepare($inches_str);
# $hsuid_from_gha->execute();
 # while (my $hs_uid = $hsuid_from_gha->fetchrow_hashref()) {
	# my @column_ref ;
	# foreach(@existing_column_db){
		# if(!$hs_uid->{$_}){
			# push(@column_ref,$_);
		# }
	# }
	# $inches_hs_uids{$hs_uid->{hs_uid}}= \@column_ref; 
# }
# print STDERR Dumper(%inches_hs_uids);

#update all fields having NULL values from temp data
# if(%inches_hs_uids){
	# foreach my $hsuid( keys %inches_hs_uids) {		
		# my $select_temp_str = "SELECT * FROM hs_tmp_ghadata WHERE hs_uid = '$hsuid'";
		# print STDERR "select_temp_str===$select_temp_str\n";
		# my $column_from_tempgha = $dbh->prepare($select_temp_str);
		# $column_from_tempgha->execute();
		# my $update_qry;		
		# while (my $hs_uid = $column_from_tempgha->fetchrow_hashref()) {		
			# foreach(@{$inches_hs_uids{$hsuid}}){			
				# if($hs_uid->{$_}){
				# $update_qry .= "$_='$hs_uid->{$_}',";
				# }
			# }
		# }
		# if($update_qry){
			 # chop($update_qry);
			 # my $update_str = "UPDATE $table SET $update_qry WHERE hs_uid='$hsuid' AND xnum=$data_xnum";			
			 #my $update_db = $dbh->prepare($update_str);
			 #$update_db->execute();
			 # print STDERR "Updated record for hs_uid : $update_str\n";			
			# }
	# }

# }
#####End Check of data

$db->get_users_assessment( $user, $config, uc $input->param('assessment'), $input->param('xnum') );

$db->finish;

$db->disconnect;



$user->set_non_standard;

print "have xnum data before assessment\n" if $Debug;
$user->pretty_print if $Debug;

my $health = HealthStatus->new(
	{
	assessment => uc($input->param('assessment')),
	user       => $user,
	config     => $config_file,
	extraconfig => $input->param('extracfg'),
	}
	);

$health->assess( $user );

print "xnum data after assessment\n" if $Debug;
$user->pretty_print if $Debug;

my $m_format = $input->param('output_format') || DEFAULT_OUTPUT_FORMAT ;
my $mime = $health->mime(  lc $m_format );

my $data;

if(($user->auth_emailCheck != 9 && $config->authenticate_confirm) || !$config->authenticate_confirm)
	{
	if($input->param('xnum1') > 1){
		my $tempfile =  'compare_' . lc $assessment . '_1.tmpl';
		print "going to compare - $tempfile \n" if $Debug;
		$data = $health->compare( $user1, lc $m_format, $tempfile );
		print "back from compare\n" if $Debug;
		}
	else	{		
		$data = $health->output( lc $m_format, $hash{template}, $session );
		}
	}
else
	{
	 $hash{status}='retake';
	 my $form = $config->template_directory . $config->email_confirm;
	 fill_and_send( $form, $user, \%hash, $config->html_use_ssi );
	 exit;
	}

if (($data ne 'PDF' && $data ne 'PDFE') && $config->pdf_debug) {
	print "Content-type: text/plain\n\n";
	print $data;
	exit;
	}
if (($data ne 'PDF' && $data ne 'PDFE')) {
	print $input->header($mime), $data;
	}
#send_pdf_email( $config, $user ,uc($hash{assessment}));
if ($data eq 'PDFE') {
		my $form;
		if(send_pdf_email( $config, $user ,uc($hash{assessment}))){
			$form = $config->template_directory . 'report_sent.tmpl';}
		else	{
			$form = $config->template_directory . 'report_not_sent.tmpl';}

		fill_and_send( $form, $user, \%hash, $config->html_use_ssi );
		exit;
		}


=head1 BUGS

* none that i've found so far.

=head1 TO DO

* nothing yet

=head1 AUTHOR

Greg White <gwhite@healthstatus.com>

=head1 COPYRIGHT

Copyright 2001-2007, HealthStatus.com

=cut

1;