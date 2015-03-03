#!/usr/local/bin/perl
use strict;

=head1 NAME

api_mchcp.cgi - Provides API Interface 

=head1 INPUT

This script depends on certain control parameters to tell it what to do.

	username - admin username
	
	password - admin password

	userid - ID of user that will be processed

	assessment - For which processing has to be done

=head2 OUTPUT

	json response

=cut

use CGI::Carp;
use File::Basename        qw( dirname );
use File::Spec::Functions qw( rel2abs );

use lib dirname(rel2abs($0)),'.','/usr/local/www/vhosts/managed2/modules/pdf', '/usr/local/www/vhosts/managed2/modules';

use vars qw( $Debug $production $cook $config_file $nph %Allowed_assessments %field_info);

if (!do('common.inc')) {
   my $error = $@ ? $@
             : $! ? $!
             : 'did not return a true value';
   die("Unable to load common stuff: $error\n");
}

use HealthStatus qw ( error html_error fill_and_send );
use CGI::Carp;
use LWP::UserAgent;
use JSON;

my $input = new CGI();
my $config = getConfig($input->param('extracfg'));
#Get subdomain name for respective config file 
my @subdomains = split(/\./,$ENV{'HTTP_HOST'});

if (!do($config->conf_config_dir.'/healthstatus_db.conf')) {
   my $error = $@ ? $@
             : $! ? $!
             : 'did not return a true value';
   die("Unable to load ".$config->conf_config_dir."/healthstatus_db.conf: $error\n");
}

if (!do($config->conf_config_dir.'/db_hs.conf')) {
   my $error = $@ ? $@
             : $! ? $!
             : 'did not return a true value';
   die("Unable to load ".$config->conf_config_dir."/db_hs.conf: $error\n");
}


my %hash = map { $_, $input->param($_) } $input->param();

my %config = map { $_, $config->$_ } $config->directives;

$hash{config} = \%config;


my $username = $input->param('username');
my $password = $input->param('password');
my $userid = $input->param('userid');
my $assessment = $input->param('assessment');
my $db = HealthStatus::Database->new( $config );
my %vars = ();

# check the username and password in the database
my $check_userID  =  $db->select_one_value( 'hs_uid', 'hs_pass', "WHERE hs_uid='$username' and pass='$password'" );

if( $config->authenticate_admin == 1 ) {
	if( !$check_userID  ){
		print $input->header(-type => "application/json", -charset => "utf-8");
		print "You are not authorized to run this program";
		exit 1;
	}	
}


&assessment_taken_date();
#######################################################
## Data Processing
#######################################################


sub assessment_taken_date()
{
    my $stipulation = '';	
	$stipulation .= "WHERE hs_uid='$userid' ORDER BY adate DESC LIMIT 1";
	
    my @result =$db->select(['hs_uid', 'adate'], [$HealthStatus::Database::Tables{$assessment}],$stipulation, 1);
	# return JSON string
	my $json = to_json(\@result);
	print $input->header(-type => "application/json", -charset => "utf-8");
	print $json;
	
}


