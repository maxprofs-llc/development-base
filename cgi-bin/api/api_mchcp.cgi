#!/usr/local/bin/perl
use strict;

=head1 NAME

api_mchcp.cgi - Provides API Interface 

=head1 INPUT

This script depends on certain control parameters to tell it what to do.

	admin - admin username
	
	pwd - admin password

	hs_uid - ID of user that will be processed

	assessment - For which processing has to be done

=head2 OUTPUT

	json response

=cut

use CGI::Carp;
use File::Basename        qw( dirname );
use File::Spec::Functions qw( rel2abs );

use lib dirname(rel2abs($0)),'.','/usr/local/www/vhosts/managed2/modules/pdf', '/usr/local/www/vhosts/managed2/modules';

use vars qw( $Debug $production $cook $config_file $nph);

if (!do('/usr/local/www/vhosts/managed2/base/cgi-bin/hs/common.inc')) {
   my $error = $@ ? $@
             : $! ? $!
             : 'did not return a true value';
   die("Unable to load common stuff: $error\n");
}

use HealthStatus qw ( error html_error fill_and_send );
use CGI::Carp;
use JSON;
use LWP::UserAgent;
use HTTP::Request::Common qw(GET);
use HealthStatus::Authenticate;
use HealthStatus::Config;
use HealthStatus::Constants;
use HealthStatus::Database;
use HealthStatus::User; 
use Data::Dumper;

my $input = new CGI();
my $config = getConfig($input->param('extracfg'));

my $session = new CGI::Session(undef, undef, {Directory=>'../../sessions'}) or die CGI::Session->errstr;
$session->save_param();
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

$cook = $session->param('hs_ident') || $input->param('hs_ident') || $input->cookie('hs_ident');

$session->flush();

my $admin = $input->param('admin');
my $pwd = $input->param('pwd');
my $hs_uid = $input->param('hs_uid');
my $assessment = uc $input->param('assessment');
my $xnum =  $input->param('xnum');
my $output_format = uc $input->param('output_format');
my $user_hs_ident = $input->param('user_hs_ident');
my $site_id = $input->param("siteid");
my $date_range = $input->param("date_range");
my $auth_password_entry = $input->param("auth_password_entry");

my $db = HealthStatus::Database->new( $config );

# check the admin username and password in the database
my $check_userID  =  $db->select_one_value( 'hs_uid', 'hs_pass', "WHERE hs_uid='$admin' and pass='$pwd'" );

if( $config->authenticate_admin == 1 && !$check_userID ) {	
		print $input->header(-type => "application/json", -charset => "utf-8");
		print "You are not authorized to run this program.";
		exit 1;		
}

if($input->param("db_id")&& $input->param("xnum") && $input->param("user_hs_ident") && $auth_password_entry){	
	&print_html_report();
}elsif ($xnum && $output_format && $assessment){	
	&view_report_pdf() ;
}elsif($hs_uid && $assessment){
	&last_assessment_taken_date();
}elsif($site_id && $date_range){
	&count_site_users();
}elsif($hs_uid){	
	&assessment_taken();
}elsif($user_hs_ident){
	&view_report_html();
}

#######################################################
## Data Processing
#######################################################

# Get last assessment date user has attempted
sub last_assessment_taken_date()
{
    	
	my $stipulation = " WHERE hs_uid='$hs_uid' ORDER BY adate DESC LIMIT 1";	
    my @result =$db->select(['hs_uid','xnum', 'adate'], [$HealthStatus::Database::Tables{$assessment}],$stipulation, 1);
	
	# return JSON string
	my $json = to_json(\@result);	
	print $input->header(-type => "application/json", -charset => "utf-8");
	print $json;
	
	exit;	
}
# Get all assessment user has attempted so far
sub assessment_taken()
{   
	
	my @assessments = @{$$config{common_assessments}};
    my @returned_assessments  =  $db->get_users_assessments_api( $hs_uid, $config, \@assessments);
	
	foreach (@returned_assessments){		
		$$_{assessment_fullname} = &assessment_name($$_{assessment});				
	}	

	# return JSON string
	my $json;
	$json->[0]{hs_uid} = $hs_uid;
	$json->[1] =  \@returned_assessments;
	my $json_text = to_json($json);
	print $input->header(-type => "application/json", -charset => "utf-8");
	print $json_text;
	
	exit;	
}

# view report as PDF
sub view_report_pdf(){
	my $ua = LWP::UserAgent->new;	
    # Create Request Object
	my $url = "https://base1.hra.net/cgi-bin/hs/review_any.cgi?api_mchcp=1&assessment=".$assessment."&xnum=".$xnum."&user_hs_ident=".$hs_uid."&output_format=".$output_format;
   
	my $req = GET $url;
	
    # Make the request
    my $res = $ua->request($req);	
	print $input->header(-type => "application/pdf", -charset => "utf-8");
    # Check the response of the request
    if ($res->is_success) {
        print $res->content;		
    } else {
        print $res->status_line . "\n";
    }
    exit;
	
}

# view report as HTML
sub view_report_html(){
	
	# check password in the database
	my $auth_password_entry  =  $db->select_one_value( 'pass', 'hs_pass', "WHERE hs_uid='$user_hs_ident'" );
	# Redirect to approve user status
	if($auth_password_entry){ 		
		my $url = "https://base1.hra.net/cgi-bin/api/api_mchcp.cgi?admin=hsadmin_8228&pwd=hsadmin_8228&db_id=".$user_hs_ident."&auth_password_entry=".$auth_password_entry."&assessment=".$assessment."&xnum=".$xnum."&user_hs_ident=".$user_hs_ident;
   		#my $url = "https://base1.hra.net/cgi-bin/hs/register_api.cgi?db_id=".$user_hs_ident."&auth_password_entry=".$auth_password_entry."&assessment=".$assessment."&xnum=".$xnum."&user_hs_ident=".$user_hs_ident;
		print $input->redirect(-url => $url);
		exit;
	}	
}

#Get total number of users that taken assessments for specific site code within specified date range
sub count_site_users(){
	
	my ($stipulation,$count_users);	
	my @date_range_array = split /,/,$date_range;
	my @assessment_list = split /\s+/, $config->ggr_adv_tables;	
	$stipulation .= "WHERE site like '%".$site_id."'";
	$stipulation .= "AND adate>='" . $date_range_array[0] ." 00:00:00'";
	$stipulation .= " AND adate<'" . $date_range_array[1] . " 00:00:00'";
	foreach (@assessment_list){			
		$count_users  +=  $db->hs_count( $_, $stipulation );
	}
	my %json;
	$json{total_users} = $count_users;
	my $res_json = to_json( \%json);	
	print $input->header(-type => "application/json", -charset => "utf-8");
	print $res_json;
}

sub print_html_report(){ 
	
	my $temp_file_name = $config->authenticate_dir;
	my $temp_file = $input->param('hs_ident') || $input->cookie('hs_ident') || '0';
	if(!$hash{db_number}) { $hash{db_number} = $temp_file || '' }
	my $user = HealthStatus::User->new( \%hash );
	my $approved = HealthStatus::Authenticate->new( $config, $temp_file_name, $temp_file );
	my $status = $approved->login( $config, $user );
	
	if ($status eq APPROVED)
	{
		my $tnum = $user->db_number;
		$hash{hs_ident}=$tnum;
		my $cookie = $input->cookie(-name=>'hs_ident', -value=>"$tnum");	
		my $session_cookie = $input->cookie( -name   => $session->name, -value  => $session->id );
		#Create url and print report
		my $goto_page = "https://base1.hra.net/cgi-bin/hs/review_any.cgi?user_hs_ident=".$user_hs_ident."&assessment=".$assessment."&xnum=".$xnum;
		print $input->redirect( -cookie=>[$cookie,$session_cookie], -uri=>$goto_page );	
	}

}

