#!/usr/local/bin/perl
use strict;

=head1 NAME

assessment_recs.cgi - create the users assessment records page

=head1 DESCRIPTION

Use this script as the redirect after the login process is complete.
As part of the login, you should have set a cookie named 'hs_ident' on
the users browser with a temporary file name as the parameter.  This
script will grab the initial user information from the temporary file
look up the assessments the user has taken and present a page where
they can review the results from the previous assessments, take a new
assessment or anything else we throw in the assessment_recs template.

=head1 INPUT

This script depends on certain control parameters to tell it what to
do.

'hs_ident'	- a cookie or hidden form field containing the
		file name of a temporary file to use for authentication
		and to collect initial user information in a more
		secure manner than passing hidden form fields. This
		file holds points to another configuration file
		or overrides values in the default configuration
		file.  Config data is collected by
		C<HealthStatus::Config>


We use the C<HealthStatus::Database> object to collect the
users previously taken assessments.  C<HealthStatus::Authenticate>
is called to determine if the user is valid or if their session
has expired.

=head2 OUTPUT

The script loads a template file with C<Text::Template> and fills in
the template.  The contents of C<max_assessments> configuration variable
determine the number of assessments that will be returned.  Depending
on the assessment records template the user can then click on a previous
assessment and review the results of that assessment, or click a link
to start a new assessment.

=head1 ERRORS

This script will issue an error if it cannot read the temporary,
configuration, template files, or if the user cannot be authenticated.
A short, vague message is sent to the browser and a more detailed message
should show up in the error log.

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

use HealthStatus qw ( error html_error fill_and_send assessment_expired);
use HealthStatus::Constants;
use Date::Calc;
use CGI::Carp;

my $input = CGI->new();
my $config = getConfig($input->param('extracfg'));
my $session = new CGI::Session(undef, undef, {Directory=>'../../sessions'}) or die CGI::Session->errstr;
carp "Session id in assessment_recs is: ".$session->id();
$session->save_param();

my %hash = map { $_, $input->param($_) } $input->param();

my %config = map { $_, $config->$_ } $config->directives;

$hash{config} = \%config;

my %input = $input->Vars();

$cook = $session->param('hs_ident') || $input->param('hs_ident') || $input->cookie('hs_ident');

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
	print "HealthStatus::Config - $HealthStatus::Config::VERSION\nHealthStatus::User - $HealthStatus::User::VERSION\n\n";
	foreach my $key ( sort keys %input )
		{
		print "\t$key\t\t$input{$key}\n";
		}
	print "my cookie = $cook\ncookie - " . $input->cookie('hs_ident') . "\nparam - " . $input->param('hs_ident') . "\n";
	$config->pretty_print;
	}

delete($hash{'Submit.x'}) if (exists($hash{'Submit.x'}));
delete($hash{'Submit.y'}) if (exists($hash{'Submit.y'}));
delete($hash{'action'}) if (exists($hash{'action'}));

# authenticate_user redirects the user if they not allowed to
# view this page
my $user = authenticateUser('all', $input, $config) or exit();
my $site_id = $user->siteid;
$site_id =~ s/\///;
my @assessments = @{$$config{common_assessments}};
my $db = HealthStatus::Database->new( $config );
my ($assess_status,$expired_status,$goto_input_page,$goto_report_page,$asess_status);			
if($config->expired_check){		
	foreach my $assess(@assessments){				
		$assess_status = $db->get_users_last_assessment($user, $config, $assess);	
	}
	$goto_input_page = $config->html_home.'/cgi-bin/hs/collector.cgi?assessment=GHA&page=0';
	$goto_report_page = $config->html_home.'/cgi-bin/hs/review_any.cgi?assessment=DRC&xnum=3&user_hs_ident=hsadmin_8228';
	
	if(assessment_expired($config, $user) && $assess_status){
		print $input->redirect( -uri=> $goto_input_page );
	}else{
		print $input->redirect( -uri=> $goto_report_page );
	}	
} 

my $query_results;
my %grp_vars;

my %grps_table = %{$db->get_db_tables($config)};
my %tables = %{$db->all_table_names};
if($site_id){	
	my $stipulations = "Where groupID = '".$site_id."'";			
    $query_results = $db->select_one_row('*', $tables{GRP}, $stipulations, 1);
	 %grp_vars = %{$query_results} if($query_results);
}

$db->debug_on( \*STDERR ) if $Debug;

my @BIO = ("BIO");

my $status1  =  $db->get_users_bio_taken( $user, $config, \@BIO, "where client7='".$session->param('case')."'" ) if($config{biometric_file_pre});

if($status1){
	my @user_to_save = $user->attributes();

	foreach (@user_to_save){
		$session->param( $_, $user->$_ ) if($_ ne 'config' && $user->$_ ne '');
		}
	}
$db->debug_off();

my @returned_recs  =  $db->get_users_assessments_taken( $user, $config, \@assessments );

my @sorted_results = map { $_->[2] }
	     sort { $b->[1] cmp $a->[1] || $a->[0] cmp $b->[0] }
	     map { [$_->{adate}, $_->{assessment}, $_] } @returned_recs;

if ($Debug){ foreach (@returned_recs) { print "$_\n"; } }

my @import_recs  = $db->get_pending_import ( $user) if ($grps_table{'hs_import'});

$db->disconnect;

my %config_stuff = ();

foreach my $key ( $config->directives )
	{
	$config_stuff{$key} = $config->$key;
	print "$key - $config_stuff{$key}\n" if $Debug;
	}

my %vars = ( 'config' => \%config_stuff,
	     'records' => \@returned_recs,
             'imports' => \@import_recs,
             'biometric_status' => $status1);

if( $input->cookie('hs_ident') < 0 ){
	$vars{cookie}=$input->cookie(-name=>'hs_ident', -value=> $user->db_number , -domain=>$ENV{HTTP_HOST});
	}

$vars{view_all} = $input->param('view_all');
$vars{site_id}= \%grp_vars;
foreach my $key ( $user->attributes ) { $vars{$key} = $user->get($key);
					print "$key - $vars{$key}\n" if $Debug;
					}
					
my $domain = $ENV{SERVER_NAME};
my @domain_parts = split /\./,$domain;
my $subdomain = $domain_parts[0];



my $form_to_get = '';
$form_to_get = $config->assessment_recs_page_admin if ($user->hs_administration eq 'admin');
$form_to_get = $config->assessment_recs_page_coach if ($user->hs_administration eq 'coach');
$form_to_get = $config->assessment_recs_page_clerk if ($user->hs_administration eq 'clerk');
$form_to_get = $config->assessment_recs_page if ($form_to_get eq '');
$form_to_get = $config->reliance_assessment_recs_page if ($subdomain eq 'reliance1');

fill_and_send( $config->template_directory . $form_to_get, $user, \%vars, $config->html_use_ssi );

=head1 BUGS

* none that i've found so far.

=head1 TO DO

* none at this time

=head1 AUTHOR

Greg White <gwhite@healthstatus.com>

=head1 COPYRIGHT

Copyright 2002-2008, HealthStatus.com

=cut

1;
