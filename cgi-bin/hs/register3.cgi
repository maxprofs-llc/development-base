#!/usr/bin/perl
use strict;

=head1 NAME

register.cgi - register a user

=head1 DESCRIPTION

Use this script as the program to submit registration information
to, it will check for duplicates, and proper formatting.  It can
add a new user, look up an old user, change user data, login a user
or log them out.

=head1 INPUT

This script depends on certain control parameters to tell it what to
do.

	action	- add change check confirm delete login logout
	          lookup remove subscribe update

The script uses these parameters to load certain configuration
directives. The configuration files stores the required fields
in directives named after the assessment in page in the form

	reg_required_fields_<action>

so that if the registration step is C<add> then the
configuration directive that hold the required fields is

	reg_required_fields_add

Additionally, some fields are checked to ensure that they contain
integer values.  These fields are stored in the configuration
directive C<reg_integer_fields> no matter the action.  If any
of the fields specified in C<reg_integer_fields> show up in the
input, the script will remove all non-numeric characters from
their values.

The script expects the values of these configuration directives
to be a whitespace separated list of field names, such as

	reg_integer_fields	height weight

so that the script checks C<height> and C<weight> for integer values.


=head2 OUTPUT

The script loads a template file with C<Text::Template> and fills in
the template.  The script passes the filled-in result of the template
to C<HTML::FillInForm> along with the C<CGI> object so that the form
values are passed along.

If the value of the image submit button is either C<next> or C<prev>
then the appropriate template, replaces the HTML form values, and
outputs the template.  However, if the script finds the C<assess>
image submit button name, it performs the health assessment and gives
output according to what it sees in the parameter C<output_format>, which
can be C<html>, C<pdf>, or C<xml>, although it can depend on the
particular assessment.

=head1 ERRORS

This script will issue an error if it cannot read the
configuration or template file.  A short, vague message
is sent to the browser and a more detailed message should
show up in the error log.

If the script cannot recognize the value of the control parameter
C<action> it outputs
an error page.

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
use Digest::MD5 qw(md5 md5_hex md5_base64);
use Data::Dumper;
use LWP::UserAgent;
use LWP::Authen::OAuth;
use JSON;
use HTTP::Request::Common;
use Net::OAuth;
use Digest::HMAC_SHA1;
use MIME::Base64;
use URI::URL;

my  $stat;

CGI->nph($nph) if $nph;
my $input = CGI->new();
my $config = getConfig($input->param('extracfg'));

my $session = new CGI::Session(undef, undef, {Directory=>'../../sessions'}) or die CGI::Session->errstr;
carp "Session id in register is: ".$session->id();
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

# %Allowed_assessments not only tells us which assessments we
# can do, but how many pages of input to expect
%Allowed_assessments = map
	{
	my $assessment = lc $_;
	my $method     = lc $_."_max_pages";
	my $max_pages  = $config->$method;

	( $assessment, $max_pages )
	} @{$$config{common_assessments}};

my %Allowed_actions = map { ( $_, 1 ) }
	 qw( add change change_pass confirm newcode delete login logout lookup update update_pass enroll newone add_many bootstrap log activate resend adv_lookup oauth_signup oauth_signup1 oauth_signup2 oauth_signup3 oauth_add oauth_cnt );
#	 qw( add change check confirm delete fix_email login logout lookup remove subscribe update update_pass );

my $action = lc $input->param('action');

#$action = 'oauth_signup1';
print "Action = $action\n" if $Debug;
my %oauth_data;
 my $varifier = $input->param('oauth_verifier');
if($varifier){
    carp "varifier===$varifier";
	$action = 'oauth_signup';
}       
carp "action=====$action";

my $temp_file_name = $config->authenticate_dir;
my $temp_file = $input->param('hs_ident') || $input->cookie('hs_ident') ;
$temp_file = '0' if ($action eq 'login' || $action eq 'lookup' || $action eq 'add' || $action eq 'delete' || $action eq 'add_many' || $action eq 'log');

print "Temp file = $temp_file\n$temp_file_name\n" if $Debug;

# redirection pages
my $beg_site = $input->param("siteid");
my $member = $config->member_page;
my $login  = $config->login_page;
my $timeout = $config->timeout_page;
my $failed = $config->login_failed;
my $template_dir = $config->template_directory;

my $db = HealthStatus::Database->new( $config );

if(!$hash{db_number}) { $hash{db_number} = $temp_file || '' }

$db->debug_on( \*STDERR ) if $Debug;

my $user = HealthStatus::User->new( \%hash );

$user->pretty_print if $Debug;

unless (exists $Allowed_actions{$action}){
	my $form = $config->template_directory . $config->login_register_retry;
	$hash{error_msg} = "That action is not permitted, please login again.";
	fill_and_send( $form, $user, \%hash, $config->html_use_ssi );
	exit;
	}

if($action eq 'enroll'){
	my $form = $config->template_directory . $config->login_register_retry;
	fill_and_send( $form, $user, \%hash, $config->html_use_ssi );
	exit;
	}
elsif($action eq 'log'){
	my $form = $config->template_directory . $config->login_failed;
	if($input->param('activation'))
	{
		$user->{activation} = $config->email_activation_message;
	}
	else
	{
		$user->{activation} = $config->general_login_message;
	}
	fill_and_send( $form, $user, \%hash, $config->html_use_ssi );
	exit;
	}
elsif(	$action eq 'bootstrap' )
	{
	$db->init_seq();
	my $form = $config->template_directory . $config->login_register_retry;
	fill_and_send( $form, $user, \%hash, $config->html_use_ssi );
	exit;
	}
elsif(	$action eq 'lookup' && $hash{render} == 1)
	{
	my $form = $config->template_directory . $config->lost_password;
	fill_and_send( $form, $user, \%hash, $config->html_use_ssi );
	exit;
	}
elsif(	$action eq 'lookup' && (!$input->param('db_id') && !$input->param('db_email') ) )
	{
	my $form = $config->template_directory . $config->lost_password;
	fill_and_send( $form, $user, \%hash, $config->html_use_ssi );
	exit;
	}


# check for required fields
my $method = "reg_required_fields_${action}";
print "Method is $method\n" if $Debug;
my @required_fields = split /\s+/, $config->$method;
print "Required are @required_fields\n" if $Debug;

my @missing_required_fields =
	map
	{
	my $value = $input->param($_);
	print "$_ - $value\n" if $Debug;
	( defined $value and $value ne "" ) ? () : "$_, "
	} @required_fields;
print "Missing is @missing_required_fields\n" if $Debug;

# only error if we are moving forward so that users can
# go back to correct things
if( @missing_required_fields )
	{
	my $form = $config->template_directory . $config->login_register_retry;
	$hash{error_msg} = ("Some needed information was not included - " . "@missing_required_fields" );
	fill_and_send( $form, $user, \%hash, $config->html_use_ssi );
	exit;
	}

# make sure integer fields only have integers in them
my @integer_fields = split /\s+/, $config->reg_integer_fields;
print "Integer fields are  @integer_fields<br>\n" if $Debug;

foreach my $field ( @integer_fields )
	{
	next unless $input->param($field);

	my $value = $input->param($field);
	print "My integer field [$field] has value [ $value ]<br>\n" if $Debug;
	next unless $value =~ /\D/;

	$value =~ s/\D//g;

	$input->param($field, $value);
	}

my $approved = HealthStatus::Authenticate->new( $config, $temp_file_name, $temp_file );

$approved->debug_on( \*STDERR ) if $Debug;

my $status = '';
my %flags = {};

if(	$action eq 'add' || $action eq 'add_many' )
	{
		if ($config->authenticate_site){
		my $string = $user->db_employer;
		for ($string) {
			s/^\s+//;
			s/\s+$//;
			}
		$user->db_employer( $string );
		print STDERR "\ndb employer nu===".$user->db_employer;
		my ($check_OK, $check_error); 
		if($config->authenticate_site_file eq 'group_databases'){
			my $stipulation = 'Where groupID = '. "'".$user->db_employer."'";
			print STDERR "\nstipulatin====$stipulation";
			$check_OK = $db->get_group($stipulation);
			}
		else	{
			($check_OK, $check_error) = check_employer_number($user->db_employer, $config->authenticate_site_file);
			}
		if (!$check_OK){
			$user->siteid( $beg_site );
			my $form = $config->template_directory . $config->login_register_retry;
			$hash{error_msg} = "The registration number is not valid, please check it or contact" . ' '. $config->client. ".";
			fill_and_send( $form, $user, \%hash, $config->html_use_ssi );
			exit;
			}
		}
		$user->siteid ( $user->siteid . "/" . $user->db_employer );
		$status = $approved->add( $config, $user, \%flags );
		print "add - $status\n$config->member_page\n$member\n" if $Debug;
		if ($status eq TRUE || $status eq CONFIRM)
			{
			my $from = $config->email_from;
			my $smtp = $config->email_smtp;
			my $to = $config->email_admin;
			my %mail;
			if($config->authenticate_confirm)
                        	{
				my $health = HealthStatus->new(
					{
					assessment => 'HRA',
					user       => $user,
					config     => $config_file,
					}
					);
                                my %vars = ( link => $config->html_base . $config->cgi_dir . '/register.cgi?action=activate&id=' . $user->db_id );
                                unless($health->send_email( $user , 'CONFIRM', \%vars )) { carp "send_email to ". $user->db_id . ", ". $user->db_email . " did not work.";}
                        	}
			if($config->authenticate_notify)
                        	{
                                my %mail;

				%mail = (       To      => $to,
                                                From    => $from,
                                                Subject => 'New Registration',
                                                Message => $user->db_fullname."\n".$user->db_email."\n".$user->db_id."\njust registered to take an assessment.",
                                                smtp   => $smtp
                                         );
                                sendmail(%mail);
                                carp("Couldn't send email: $Mail::Sendmail::error")
                                	if $MAIL::Sendmail::error;
                             	}

			if($action eq 'add_many'){
				my $form = $config->template_directory . $config->login_register_retry;
				fill_and_send( $form, $user, \%hash, $config->html_use_ssi );
				exit;
				}
			else	{
				my $tnum = $user->db_number;
				$hash{hs_ident}=$tnum;
				$hash{full_name} = $user->db_fullname;
				$hash{email} = $user->db_email;
				my $expire_time = $config->session_timeout;
				my $cookie=$input->cookie(-name=>'hs_ident', -value=>"$tnum", -expires=> "+{$expire_time}m");
				$hash{'cookie'} = $cookie;
				my $goto_page;
				if($config->newuser_interstitial){
					my @ignore = split /\s+/, $config->newuser_inter_ignore;
					$goto_page = $config->newuser_inter_template;
					my $form = $config->template_directory . $goto_page;
					fill_and_send( $form, $user, \%hash, $config->html_use_ssi, \@ignore );
					}
				else	{
					$goto_page = "$member?hs_ident=$tnum&CGISESSID=".$session->id;
					print $input->redirect( -cookie=>$cookie, -uri=> $goto_page ) if ($^O ne 'MSWin32');
					print $input->redirect( -cookie=>$cookie, -uri=> $config->html_home.$goto_page ) if ($^O eq 'MSWin32');
					}
				}
			}
		elsif ($status eq DUPLICATE)
			{
			$user->siteid( $beg_site );
			my $form = $config->template_directory . $config->login_register_retry;
			$hash{error_msg} = "That user name is already taken, please try a different one.";
			fill_and_send( $form, $user, \%hash, $config->html_use_ssi );
			}
		else	{
			$user->siteid( $beg_site );
			my $form = $config->error_user ;
			$hash{error_msg} = "The system returned a status of $status during registration.";
			fill_and_send( $form, $user, \%hash, $config->html_use_ssi );
			}
	}
elsif(	$action eq 'change' || $action eq 'change_pass' )
	{
		$status = $approved->check( $config, $user );
		print "change(check) - $status\n$user->db_number\n$member\n" if $Debug;

		if ($status ne APPROVED) {
				$user->siteid( $beg_site );
				my $form = $config->error_user ;
				$hash{error_msg} = "You must login before changing your account.";
				fill_and_send( $form, $user, \%hash, $config->html_use_ssi );
				exit;
				}
		my $user_change = HealthStatus::User->new( \%hash );

		$user_change->auth_password( $hash{'new1_password_entry'} ) if ( $action eq 'change_pass' );

 		print "User_Change hash\n" if $Debug;
 		$user_change->pretty_print if $Debug;        
		
		$status = $approved->change( $config, $user_change );
		if ($status eq TRUE)
			{
			print "change - $status\n$user->db_number\n$member\n" if $Debug;
			$user->pretty_print if $Debug;
			my $form;
 		    $form = $config->template_directory . $config->update_pass_page if($action eq 'change_pass');
 		    $form = $config->template_directory . $config->update_page if($action eq 'change');
			$hash{update_acc} = "Your account details have been updated successfully.";
			$hash{update_pass} = "Your password has been changed successfully and would be apply while you login again.";
			fill_and_send( $form, $user, \%hash, $config->html_use_ssi );
			#print $input->redirect (-uri=> $member );
			}
		else	{
			$user->siteid( $beg_site );
			my $form = $config->error_user ;
			$hash{error_msg} = "The system returned a status of $status during attempted information change.";
			fill_and_send( $form, $user, \%hash, $config->html_use_ssi );
		}
	}
elsif(	$action eq 'confirm' )
	{
		my $input_number = $input->param('confirm');
		my $first_check = substr($input_number, 1, 15);
		my $first_digit = substr($input_number, 0, 1);
		my $second_check = substr($input_number, 2, 14);
		my $second_digit = substr($input_number, 1, 1);
		print "Status not approved, checking $input_number for validity.\n" if $Debug;
		if( length $input_number != 16 || check_digit($first_check) != $first_digit || check_digit($second_check) != $second_digit ) {
			print "$input_number not valid, $first_digit, $second_digit\n" if $Debug;
			$user->siteid( $beg_site );
			my $form = $config->error_user ;
			$hash{error_msg} = "You must login before changing your account.";
			fill_and_send( $form, $user, \%hash, $config->html_use_ssi );
			exit;
			}
		$status = $approved->confirm( $config, $user, $second_check );
		print "My timestamp field is [$second_check] since  [ ${user->db_id} ]<br>This returned a status of [ $status ]<br>\n" if $Debug;
		if ($status eq TRUE)
			{
			my $form = $config->template_directory . $config->unsubscribe_confirmation;
			$hash{error_msg} = "";
			fill_and_send( $form, $user, \%hash, $config->html_use_ssi );
			}
		else	{
			my $form = $config->error_user ;
			$hash{error_msg} = "The system returned a status of $status during your request.";
			fill_and_send( $form, $user, \%hash, $config->html_use_ssi );
		}
	}
elsif(	$action eq 'delete' )
	{
		$status = $approved->check( $config, $user );
		print "delete - $status\n$user->db_number\n$member\n" if $Debug;

		if ($status ne APPROVED) {
			my $input_number = $input->param('unsub');
			my $first_check = substr($input_number, 1, 15);
			my $first_digit = substr($input_number, 0, 1);
			my $second_check = substr($input_number, 2, 14);
			my $second_digit = substr($input_number, 1, 1);
			print "Status not approved, checking $input_number for validity.\n" if $Debug;
			if( length $input_number != 16 || check_digit($first_check) != $first_digit || check_digit($second_check) != $second_digit ) {
				print "$input_number not valid, $first_digit, $second_digit\n" if $Debug;
				$user->siteid( $beg_site );
				my $form = $config->error_user;
				$hash{error_msg} = "You must login before changing your account.";
				fill_and_send( $form, $user, \%hash, $config->html_use_ssi );
				exit;
				}
			}

		my $tables = backup_user($user->db_number);

		if ($tables) {
			foreach(@$tables) {$db->delete($_, " WHERE unum=".$user->db_number);}
			$status = TRUE;
		}

		if ($status eq TRUE)
			{
			    $hash{confirm_delete}= 1;
				my $form = $config->template_directory . $config->unsubscribe_confirmation;
				$hash{error_msg} = "";
				fill_and_send( $form, $user, \%hash, $config->html_use_ssi );
			}
		else	{
			my $form = $config->error_user;
			$hash{error_msg} = "The system returned a status of $status during your request.";
			fill_and_send( $form, $user, \%hash, $config->html_use_ssi );
		}
	}
elsif(	$action eq 'login' )
	{
		$status = $approved->login( $config, $user );
		print "login - $status\n$user->db_number\n$member\n" if $Debug;
		if ($status eq APPROVED)
			{
			my $tnum = $user->db_number;
			$hash{hs_ident}=$tnum;
			my $cookie = $input->cookie(-name=>'hs_ident', -value=>"$tnum");
			
			my $session_cookie = $input->cookie( -name   => $session->name, -value  => $session->id );

			$hash{'cookie'} = $cookie;
			$hash{'tnum'} = $tnum;	
            $hash{'CGISESSID'} = $session->id;
			my $goto_page;
			if($config->login_interstitial){
				my @ignore = split /\s+/, $config->login_inter_ignore;
				$goto_page = $config->login_inter_template;
				my $form = $config->template_directory . $goto_page;
				fill_and_send( $form, $user, \%hash, $config->html_use_ssi, \@ignore );
			}
			else{
			        
                                my $referer=$ENV{HTTP_REFERER};
                                my $pos= rindex $referer, "/";
                                my $new_member = substr ($referer, $pos+1);
                                if ($new_member eq '' || $new_member eq 'register.cgi')
                                {
                                	$goto_page = "$member?hs_ident=$tnum&CGISESSID=".$session->id;
                                }
                                else
                                {
					               $goto_page = "$new_member";
                                }

				print $input->redirect( -cookie=>[$cookie,$session_cookie], -uri=> $goto_page ) if ($^O ne 'MSWin32');
				print $input->redirect( -cookie=>[$cookie,$session_cookie], -uri=> $config->html_home.$goto_page ) if ($^O eq 'MSWin32');
				}
			$stat = 0;
			}
		elsif ($status eq LOGIN_MAX)
			{
			my $form = $config->template_directory . $config->login_void;
			$hash{error_msg} = "You have exceeded the number of login attempts for this account, you must re-register.";
			$approved->delete( $config, $user, );
			fill_and_send( $form, $user, \%hash, $config->html_use_ssi );
			}
		else	{
			$user->siteid( $beg_site );
			$user->pretty_print if $Debug;
			$hash{error_msg} = "You have entered an incorrect username or password, please enter the same exact username or password you used for Health Assessment registration, or create a new username and password, thanks.";
			my $form = $config->template_directory . $config->login_failed;
			fill_and_send( $form, $user, \%hash, $config->html_use_ssi );
			$stat = 1;
			}
	}
elsif($action eq 'oauth_signup'){ 
		   use URI::Escape;
        	carp "action is oauth_signup";
		 my $callback = CGI::escape( $config->html_base . 'https://healthjibe.hra.net/cgi-bin/hs/register3.cgi');
		 my $ua = LWP::Authen::OAuth->new(
		                        oauth_consumer_key => "hra.net_NKHS7OR1",
								oauth_consumer_secret => "3c3798ca5c024f22a8f2474481a7e790"
				                
                        	);
							
							
        	carp "after Oauth->new";
                 my $oauth_nonce  = int( rand( 2**32 ) ) ;
                 my $timestamp    = time ;
				 my $enc_sig;
				 my $signature;
				 my $sig_url1 = "http://sandbox.healthjibe.net/access-token.ashx";
				 $sig_url1 = uri_escape_utf8($sig_url1);
				 my $sig_param = "oauth_consumer_key=hra.net_NKHS7OR1&oauth_nonce=".$oauth_nonce."&oauth_signature_method=HMAC-SHA1&oauth_timestamp=".$timestamp."&oauth_token=".$input->param('oauth_token')."&oauth_verifier=".$input->param('oauth_verifier')."&oauth_version=1.0";
				 $sig_param = uri_escape_utf8($sig_param);
				 my $sig_url = "GET&$sig_url1&$sig_param";										
        	carp "lwp useragent loads browser";
				my $browser = LWP::UserAgent->new();
				my $response = $browser->get($sig_url);
				 #carp "sign response===".Dumper $response;
				if( $response->is_success){ 							
					     my $content = $response->decoded_content;					
        	carp "lwp useragent response was success";
				}else{
        	carp "lwp useragent response failed";
				}
							
				if($varifier ne ''){
				
				my $token_url = "http://sandbox.healthjibe.net/access-token.ashx?oauth_consumer_key=hra.net_NKHS7OR1"."&oauth_nonce=".$oauth_nonce."&oauth_signature=".$signature."&oauth_signature_method=HMAC-SHA1&oauth_timestamp=".$timestamp."&oauth_token=".$input->param('oauth_token')."&oauth_version=1.0&oauth_verifier=".$input->param('oauth_verifier');
				        					 
						 
					  # my $token_url = "http://sandbox.healthjibe.net/access-token.ashx?"
					 # . "oauth_token=".$input->param('oauth_token')."&oauth_verifier=" . $input->param('oauth_verifier')."&oauth_signature_method=HMAC-SHA1"."&oauth_signature=".$oauth_params1->{oauth_signature}."&oauth_consumer_key=hra.net_NKHS7OR1&oauth_timestamp=".$timestamp."&oauth_nonce=".$oauth_nonce;
						carp "token url=====$token_url";
						use LWP::UserAgent;
						my $browser = LWP::UserAgent->new();
						my $response = $browser->get($token_url);
						#carp "respnseee==".Dumper $response;
					if( $response->is_success){ 
							
					my $content = $response->decoded_content;
					carp "contenttte==".Dumper $content;
					$content =~ /access_token=(.*?)(?:&expires=(.*))/;
					my $access_tocken = $1;           
					my $graph_url = "http://sandbox.healthjibe.net/api/v1/hra/phi?oauth_token=$access_tocken" ;
					my $user_res = $browser->get($graph_url);
					carp "register3 -- ".$user_res->decoded_content ;
					my $fb_user;
					#my $fb_user = decode_json ($user_res->decoded_content);
					#carp "user info".Dumper $fb_user;
					}
										# Request for an access_token 
						# my $uri = URI->new('http://sandbox.healthjibe.net/access-token.ashx'); 
						# my %params = ( 'oauth_token'     => $input->param('oauth_token'), 
									   # 'oauth_consumer_key'  => 'hra.net_NKHS7OR1', 
									   # 'oauth_consumer_secret'  => '3c3798ca5c024f22a8f2474481a7e790', 
									   # 'redirect_uri'         => $input->url(), 
									   # 'oauth_verifier' => $input->param('oauth_verifier'),
									   # 'oauth_signature_method' => "HMAC-SHA1",
									   # 'oauth_signature' =>  $oauth_params1->{oauth_signature},
									   # 'oauth_timestamp'  => $timestamp,
									   # 'oauth_nonce' => $oauth_nonce,
									   
									   # ); 
						# my $ua = new LWP::UserAgent; 
						# my $req = new HTTP::Request POST => $uri->as_string; 
						# $uri->query_form(%params); 
						# $req->content_type('application/x-www-form-urlencoded'); 
						# $req->content($uri->query); 
						# my $res = from_json($ua->request($req)->content); 
				 
						#The access token cannot be retrieved 
						# if (defined $res->{'error'}) { 
								# print $input->header . "An error occured : " . $res->{'error'}; 
				 
										#Ok now have the access token, let's request the API  
						# } else {
                                # my $url = 'http://google.com';						
								#my $url = "http://sandbox.healthjibe.net/api/v1/hra/phi?access_token=" . $res->{'access_token'};  
								 # print $input->redirect($url);  
						  
				     # my $varifier = $input->param('oauth_verifier'); 
				      # $r = $ua->post( 'http://sandbox.healthjibe.net/access-token.ashx', [
                     # oauth_consumer_key =>"hra.net_NKHS7OR1",
                     # oauth_token => $oauth_data{oauth_token},
                     # oauth_verifier => $varifier,					 
				 # ]);
                 # $ua->oauth_update_from_response( $r );
        
                # carp  'Token: '.$ua->oauth_token.'    Secret: '.$ua->oauth_token_secret;	
                }else{					
        	carp "ua post to request token";
				
				my $r = $ua->post( "http://sandbox.healthjibe.net/request-token.ashx",
				                [	
                        			oauth_callback => "https://healthjibe.hra.net/cgi-bin/hs/register3.cgi?action=oauth_signup",  		
																
								] );	
                              								
                carp 'OAuth request error: '. Dumper($r->{_request}{_headers}{authorization}); # if $r->is_error;
                # update the token secret from the HTTP response
		        $ua->oauth_update_from_response( $r );
		          
		        # data are returned as form-encoded
		        my $uri = URI->new( 'http:' );
		        $uri->query( $r->content );
		         %oauth_data = $uri->query_form;
		        carp 'OAuth data: '. Dumper %oauth_data;	 
			   
			   my $authorize_url = "http://sandbox.healthjibe.net/sso/v1/authorize?"
			   . "oauth_token=" . $oauth_data{oauth_token};
			   print $input->redirect($authorize_url);
               }		
	   
			 
    }
elsif($action eq 'oauth_signupqq'){ 
		   use URI::Escape;
        	carp "action is oauth_signupqq";
		 my $callback = CGI::escape( $config->html_base . 'https://healthjibe.hra.net/cgi-bin/hs/register3.cgi');
		 my $ua = LWP::Authen::OAuth->new(
		                        oauth_consumer_key => "hra.net_NKHS7OR1",
								oauth_consumer_secret => "3c3798ca5c024f22a8f2474481a7e790"
				                
                        	);
							
							
        	carp "after Oauth->new";
                 my $oauth_nonce  = int( rand( 2**32 ) ) ;
                 my $timestamp    = time ;
				 my $enc_sig;
				 my $signature;
				 my $sig_url1 = "http://sandbox.healthjibe.net/access-token.ashx";
				 $sig_url1 = uri_escape_utf8($sig_url1);
				 my $sig_param = "oauth_consumer_key=hra.net_NKHS7OR1&oauth_nonce=".$oauth_nonce."&oauth_signature_method=HMAC-SHA1&oauth_timestamp=".$timestamp."&oauth_token=".$input->param('oauth_token')."&oauth_verifier=".$input->param('oauth_verifier')."&oauth_version=1.0";
				 $sig_param = uri_escape_utf8($sig_param);
				 my $sig_url = "GET&$sig_url1&$sig_param";										
        	carp "lwp useragent loads browser";
				my $browser = LWP::UserAgent->new();
				my $response = $browser->get($sig_url);
				 #carp "sign response===".Dumper $response;
				if( $response->is_success){ 							
					     my $content = $response->decoded_content;					
        	carp "lwp useragent response was success";
				}else{
        	carp "lwp useragent response failed";
				}
							
				if($varifier ne ''){
				
				my $token_url = "http://sandbox.healthjibe.net/access-token.ashx?oauth_consumer_key=hra.net_NKHS7OR1"."&oauth_nonce=".$oauth_nonce."&oauth_signature=".$signature."&oauth_signature_method=HMAC-SHA1&oauth_timestamp=".$timestamp."&oauth_token=".$input->param('oauth_token')."&oauth_version=1.0&oauth_verifier=".$input->param('oauth_verifier');
				        					 
						 
					  # my $token_url = "http://sandbox.healthjibe.net/access-token.ashx?"
					 # . "oauth_token=".$input->param('oauth_token')."&oauth_verifier=" . $input->param('oauth_verifier')."&oauth_signature_method=HMAC-SHA1"."&oauth_signature=".$oauth_params1->{oauth_signature}."&oauth_consumer_key=hra.net_NKHS7OR1&oauth_timestamp=".$timestamp."&oauth_nonce=".$oauth_nonce;
						carp "token url=====$token_url";
						use LWP::UserAgent;
						my $browser = LWP::UserAgent->new();
						my $response = $browser->get($token_url);
						#carp "respnseee==".Dumper $response;
					if( $response->is_success){ 
							
					my $content = $response->decoded_content;
					carp "contenttte==".Dumper $content;
					$content =~ /access_token=(.*?)(?:&expires=(.*))/;
					my $access_tocken = $1;           
					my $graph_url = "http://sandbox.healthjibe.net/api/v1/hra/phi?oauth_token=$access_tocken" ;
					my $user_res = $browser->get($graph_url);

					my $fb_user = decode_json ($user_res->decoded_content);
					#carp "user info".Dumper $fb_user;
					}
										# Request for an access_token 
						# my $uri = URI->new('http://sandbox.healthjibe.net/access-token.ashx'); 
						# my %params = ( 'oauth_token'     => $input->param('oauth_token'), 
									   # 'oauth_consumer_key'  => 'hra.net_NKHS7OR1', 
									   # 'oauth_consumer_secret'  => '3c3798ca5c024f22a8f2474481a7e790', 
									   # 'redirect_uri'         => $input->url(), 
									   # 'oauth_verifier' => $input->param('oauth_verifier'),
									   # 'oauth_signature_method' => "HMAC-SHA1",
									   # 'oauth_signature' =>  $oauth_params1->{oauth_signature},
									   # 'oauth_timestamp'  => $timestamp,
									   # 'oauth_nonce' => $oauth_nonce,
									   
									   # ); 
						# my $ua = new LWP::UserAgent; 
						# my $req = new HTTP::Request POST => $uri->as_string; 
						# $uri->query_form(%params); 
						# $req->content_type('application/x-www-form-urlencoded'); 
						# $req->content($uri->query); 
						# my $res = from_json($ua->request($req)->content); 
				 
						#The access token cannot be retrieved 
						# if (defined $res->{'error'}) { 
								# print $input->header . "An error occured : " . $res->{'error'}; 
				 
										#Ok now have the access token, let's request the API  
						# } else {
                                # my $url = 'http://google.com';						
								#my $url = "http://sandbox.healthjibe.net/api/v1/hra/phi?access_token=" . $res->{'access_token'};  
								 # print $input->redirect($url);  
						  
				     # my $varifier = $input->param('oauth_verifier'); 
				      # $r = $ua->post( 'http://sandbox.healthjibe.net/access-token.ashx', [
                     # oauth_consumer_key =>"hra.net_NKHS7OR1",
                     # oauth_token => $oauth_data{oauth_token},
                     # oauth_verifier => $varifier,					 
				 # ]);
                 # $ua->oauth_update_from_response( $r );
        
                # carp  'Token: '.$ua->oauth_token.'    Secret: '.$ua->oauth_token_secret;	
                }else{					
        	carp "ua post to request token";
				
				my $r = $ua->post( "http://sandbox.healthjibe.net/request-token.ashx",
				                [	
                        			oauth_callback => "https://healthjibe.hra.net/cgi-bin/hs/register3.cgi?action=oauth_signup",  		
																
								] );	
                              								
                carp 'OAuth request error: '. Dumper($r->{_request}{_headers}{authorization}); # if $r->is_error;
                # update the token secret from the HTTP response
		        $ua->oauth_update_from_response( $r );
		          
		        # data are returned as form-encoded
		        my $uri = URI->new( 'http:' );
		        $uri->query( $r->content );
		         %oauth_data = $uri->query_form;
		        carp 'OAuth data: '. Dumper %oauth_data;	 
			   
			   my $authorize_url = "http://sandbox.healthjibe.net/sso/v1/authorize?"
			   . "oauth_token=" . $oauth_data{oauth_token};
			   print $input->redirect($authorize_url);
               }		
	   
			 
    }
elsif($action eq 'oauth_add'){                      					  
				carp "Returned to oauth_add";
				exit;
					 
			          $user->{db_fullname} = $session->param('fb_first_name').' '.$session->param('fb_last_name') ; 
					  $user->{db_id} = $session->param('fb_db_id');
					  $user->{auth_password} = "fb_".$session->param('fb_db_id');
					  $user->{db_email} = $session->param('fb_db_email');                       					  
					  $user->siteid ( $user->siteid . "/" . $user->db_employer );					  
					  
					  $status = $approved->add( $config, $user, \%flags );
					 
			          if ($status eq TRUE || $status eq CONFIRM){
				          if($config->authenticate_confirm)
                        	{
								my $health = HealthStatus->new(
								{
									assessment => 'HRA',
									user       => $user,
									config     => $config_file,
								}
								);
											my %vars = ( link => $config->html_base . $config->cgi_dir . '/register.cgi?action=activate&id=' . $user->db_id );
											unless($health->send_email( $user , 'CONFIRM', \%vars )) { carp "send_email to ". $user->db_id . ", ". $user->db_email . " did not work.";}
							} 
			             my $tnum = $user->db_number;						
						 my $expire_time = $config->session_timeout;
						 my $cookie=$input->cookie(-name=>'hs_ident', -value=>"$tnum", -expires=> "+{$expire_time}m");
						 my $uri = $config->member_page . '?hs_ident='.$tnum.'&fb_id='.$session->param('fb_db_id');						
						 					 
                         print $input->redirect( -cookie=>$cookie, -uri=> $uri );
						 $session->clear(["fb_first_name", "fb_last_name","fb_db_id","fb_db_email","fb_count"]);
                    
					}elsif ($status eq DUPLICATE){
						$user->siteid( $beg_site );
						my $form = $config->template_directory . $config->login_register_retry;
						$hash{error_msg} = "<font style=color:red>That user name is already taken, please try a different one.</font>";
						fill_and_send( $form, $user, \%hash, $config->html_use_ssi );
			        }
    }	
elsif($action eq 'oauth_signup1'){  
# concept with this is that the user has signed in at an OAuth website, we will take the token, verify they are logged in,
# add them to the database if needed
#
        	carp "action is oauth_signup1";
        	my $callback = CGI::escape( $config->html_base . '/cgi-bin/hs/register3.cgi?action=oauth_signup1');
        	
        	carp '1. '.$config->OAUTH_Consumer;
        	carp '2. '.$config->OAUTH_Consumer_Secret;
        	carp '3. '.$callback;
        	carp '4. '.$config->OAuth_app_title;
        	carp '5. '.$hash{oauth_token};
						
			use HealthJibe;
			# Get the tokens from the command line, a config file or wherever 
			my %tokens  = (
					consumer_key => $config->OAUTH_Consumer,
					consumer_secret => $config->OAUTH_Consumer_Secret,
					callback => $callback,
				); 
			my $app = HealthJibe->new(%tokens);
			# Check to see we have a consumer key and secret
			unless ($app->consumer_key && $app->consumer_secret) {
				die "You must go get a consumer key and secret from App\n";
			} 

			# If the app is authorized (i.e has an access token and secret)
			# Then look at a restricted resourse
			if ($app->authorized) {
				my $response = $app->view_restricted_resource;
				carp $response->content."\n";
				exit;
			}
			# Otherwise the user needs to go get an access token and secret
			 $app->get_authorization_url( callback => $callback.'&rand=' . rand() );
			carp "Then hit return after\n";

			my ($access_token, $access_token_secret) = $app->request_access_token($_);

			carp 'Tokens: '. $access_token, $access_token_secret;
			exit;

    }	
elsif($action eq 'oauth_signup2'){  
        	carp "action is oauth_signup2";
			
        	#my $callback = CGI::escape( $config->html_base . '/cgi-bin/hs/register3.cgi');

        	# carp '1. '.$config->OAUTH_Consumer;
        	# carp '2. '.$config->OAUTH_Consumer_Secret;
        	# carp '3. '.$callback;
        	# carp '4. '.$config->OAuth_app_title;      
           
        	
		         my $ua = LWP::Authen::OAuth->new(
								 oauth_consumer_secret => "3c3798ca5c024f22a8f2474481a7e790"
				                
                        	 );
                # my $r = $ua->post( "http://sandbox.healthjibe.net/request-token.ashx",
				                # [	oauth_consumer_key => "hra.net_NKHS7OR1",
                        			# oauth_callback => "https://healthjibe.hra.net//cgi-bin/hs/register3.cgi",
                        			# xoauth_displayname =>  $config->OAuth_app_title,
								# ] );
                 #carp 'OAuth request error: '. Dumper($r->as_string); # if $r->is_error;
                # update the token secret from the HTTP response
		       # $ua->oauth_update_from_response( $r );
		          
		        # data are returned as form-encoded
		        # my $uri = URI->new( 'http:' );
		        # $uri->query( $r->content );
		         # %oauth_data = $uri->query_form;
		        # carp 'OAuth data: '. Dumper %oauth_data;	 
			   
			   # my $authorize_url = "http://sandbox.healthjibe.net/sso/v1/authorize?"
			   # . "oauth_token=" . $oauth_data{oauth_token};
			   # print $input->redirect($authorize_url);		  
			    # carp "action is not varifier";
				# my $browser = LWP::UserAgent->new();
				# my $response = $browser->get($authorize_url);				
				 # if ($response->is_success) {			                  
					    # my $uaa       = LWP::UserAgent->new();
						# my $responses = $uaa->post( 'http://sandbox.healthjibe.net/Account/signin?', { UserName => 'greg@hra.net',Password=> 'danielle',Button=>'Sign in',Register=>'true' } );
						# my $content  = $responses->decoded_content();								 
					    # carp "responrrrrrrr=" . Dumper $content;  
				 # }
				 
				
		        # turn the 'request' token into an 'access' token with the verifier
		        # returned by google
		       
				my $r = $ua->post( 'http://sandbox.healthjibe.net/access-token.ashx', [
                     oauth_consumer_key =>"hra.net_NKHS7OR1",
                     oauth_token => $oauth_data{oauth_token},
                     oauth_verifier => $varifier,					 
				 ]);
                carp 'OAuth access error: '. Dumper $r->{_request}{_content}; # if $r->is_error;
				 # my $tnum = $user->db_number;						
						 # my $expire_time = $config->session_timeout;
						 # my $cookie=$input->cookie(-name=>'hs_ident', -value=>"$tnum", -expires=> "+{$expire_time}m");
						 # my $uri = $config->member_page . '?hs_ident='.$tnum;						
						 					 
                         # print $input->redirect( -cookie=>$cookie, -uri=> $uri );
		        	             			
		        #update the token secret from the HTTP response			   
		        # $ua->oauth_update_from_response( $r );
                # carp ' updated OAuth access: '. Dumper $ua;
                
				
				#print  'Token ->: '.$ua->oauth_token.'    Secret->: '.$ua->oauth_token_secret;
		        #$user->oauth_token($ua->oauth_token);
		        #$user->oauth_token_secret($ua->oauth_token_secret);
 
                # carp  'Token: '.$user->oauth_token.'    Secret: '.$user->oauth_token_secret;
               # my $tnum = $user->db_number;						
						 # my $expire_time = $config->session_timeout;
						 # my $cookie=$input->cookie(-name=>'hs_ident', -value=>"$tnum", -expires=> "+{$expire_time}m");
						 # my $uri = $config->member_page . '?hs_ident='.$tnum;						
						 					 
                         # print $input->redirect( -cookie=>$cookie, -uri=> $uri );
			 
    }
elsif($action eq 'varifier'){
                 carp "action is variifer===";
                 my $callback = CGI::escape( $config->html_base . 'https://healthjibe.hra.net/cgi-bin/hs/register3.cgi');
		         my $ua = LWP::Authen::OAuth->new(
		                        oauth_consumer_key => "hra.net_NKHS7OR1",
								oauth_consumer_secret => "3c3798ca5c024f22a8f2474481a7e790",
				                
                        	);
							
							
                 my $oauth_nonce  = int( rand( 2**32 ) ) ;
                 my $timestamp    = time ;
				 my $enc_sig;
				 my $signature;
				 my $sig_url1 = "http://sandbox.healthjibe.net/access-token.ashx";
				 $sig_url1 = uri_escape_utf8($sig_url1);
				 my $sig_param = "oauth_consumer_key=hra.net_NKHS7OR1&oauth_nonce=".$oauth_nonce."&oauth_signature_method=HMAC-SHA1&oauth_timestamp=".$timestamp."&oauth_token=".$input->param('oauth_token')."&oauth_verifier=".$input->param('oauth_verifier')."&oauth_version=1.0";
				 $sig_param = uri_escape_utf8($sig_param);
				 my $sig_url = "GET&$sig_url1&$sig_param";
                 my @values = $ua->sign_hmac_sha1($sig_url);
				 carp "values=====@values";
}	

elsif($action eq 'oauth_signup3'){
		use OAuth::Lite::Consumer;
        	carp "action is oauth_signup3";
        	my $callback = CGI::escape( $config->html_base . '/cgi-bin/hs/register3.cgi?action=oauth_signup3');

        	carp '1.===== '.$config->OAUTH_Consumer;
        	carp '2.===== '.$config->OAUTH_Consumer_Secret;
        	carp '3.===== '.$callback;
        	carp '4.===== '.$config->OAuth_app_title;
        	
		my $consumer = OAuth::Lite::Consumer->new(
				                    consumer_key => $config->OAUTH_Consumer,
				                    consumer_secret => $config->OAUTH_Consumer_Secret,
				                    site => 'http://sandbox.healthjibe.net',
				                    request_token_path => 'http://sandbox.healthjibe.net/request-token.ashx',
                        			access_token_path => 'http://sandbox.healthjibe.net/access-token.ashx',
                        			authorize_path => 'http://sandbox.healthjibe.net/sso/v1/authorize',
                        			signature_method =>  'HMAC-SHA1',
                        			http_method => 'GET',
                        			callback_url => $callback,
                        		);
        carp "request token url ".$consumer->request_token_url;
        my $request_token = $consumer->obtain_request_token();
		
        carp "request token=======".Dumper $request_token;
		    $session->param( 'request_token', $request_token );

		    $input->redirect( $consumer->url_to_authorize(
			         token        => $request_token,
		    ) );			
		
		   
#         my $verifier = $input->param('oauth_verifier');
#		 my $request_token = $session->param('request_token');
#		 carp "varifier=======$verifier";
		
		   
		 my $res = $consumer->obtain_access_token(
        		url    => $consumer->access_token_url,
        		);
        	my $access_token = $res->token;
    	carp  'Token: '.$access_token->token.'    Secret: '.$access_token->secret;
    	
		$res = $consumer->get( 'http://sandbox.healthjibe.net/api/v1/hra/phi' );
		    if ($res->is_success) {
		        carp 'Content: '. $res->decoded_content||$res->content;
    }
                exit;
			 
    }
elsif($action eq 'oauth_addxx'){                      					  
				carp "Returned to oauth_add";
				exit;
			          $user->{db_fullname} = $session->param('fb_first_name').' '.$session->param('fb_last_name') ; 
					  $user->{db_id} = $session->param('fb_db_id');
					  $user->{auth_password} = "fb_".$session->param('fb_db_id');
					  $user->{db_email} = $session->param('fb_db_email');                       					  
					  $user->siteid ( $user->siteid . "/" . $user->db_employer );					  
					  
					  $status = $approved->add( $config, $user, \%flags );
					 
			          if ($status eq TRUE || $status eq CONFIRM){
				          if($config->authenticate_confirm)
                        	{
								my $health = HealthStatus->new(
								{
									assessment => 'HRA',
									user       => $user,
									config     => $config_file,
								}
								);
											my %vars = ( link => $config->html_base . $config->cgi_dir . '/register.cgi?action=activate&id=' . $user->db_id );
											unless($health->send_email( $user , 'CONFIRM', \%vars )) { carp "send_email to ". $user->db_id . ", ". $user->db_email . " did not work.";}
							} 
			             my $tnum = $user->db_number;						
						 my $expire_time = $config->session_timeout;
						 my $cookie=$input->cookie(-name=>'hs_ident', -value=>"$tnum", -expires=> "+{$expire_time}m");
						 my $uri = $config->member_page . '?hs_ident='.$tnum.'&fb_id='.$session->param('fb_db_id');						
						 					 
                         print $input->redirect( -cookie=>$cookie, -uri=> $uri );
						 $session->clear(["fb_first_name", "fb_last_name","fb_db_id","fb_db_email","fb_count"]);
                    
					}elsif ($status eq DUPLICATE){
						$user->siteid( $beg_site );
						my $form = $config->template_directory . $config->login_register_retry;
						$hash{error_msg} = "<font style=color:red>That user name is already taken, please try a different one.</font>";
						fill_and_send( $form, $user, \%hash, $config->html_use_ssi );
			        }
    }

elsif($action eq 'newone'){
					use Net::OAuth::Request;
					use Net::OAuth::RequestTokenRequest;
					use Net::OAuth::AccessTokenRequest;
					use Net::OAuth::ProtectedResourceRequest;
				
			my $CONSUMER_KEY = 'hra.net_NKHS7OR1';
            my $CONSUMER_SECRET = '3c3798ca5c024f22a8f2474481a7e790';
			  
			my $REQUEST_TOKEN_URL = 'http://sandbox.healthjibe.net/request-token.ashxn';
			my $AUTHORIZATION_URL = 'http://sandbox.healthjibe.net/sso/v1/authorize';
			my $ACCESS_TOKEN_URL = 'http://sandbox.healthjibe.net/access-token.ashx';
			my $QUERY_API_URL = 'http://sandbox.healthjibe.net/api/v1/hra/phi';
            my $ua = LWP::Authen::OAuth->new(
								oauth_consumer_secret => "3c3798ca5c024f22a8f2474481a7e790"
				                
                        	);
				  my $oauth_params1;			
                  my $oauth_nonce  = int( rand( 2**32 ) ) ;
                  my $timestamp    = time ;			
			  
			my $r = $ua->post( "http://sandbox.healthjibe.net/request-token.ashx",
				                [	oauth_consumer_key => "hra.net_NKHS7OR1",
                        			oauth_callback => "https://healthjibe.hra.net//cgi-bin/hs/register3.cgi",                        												
                                    oauth_signature => $oauth_params1->{oauth_signature},							
									timestamp => $timestamp,
                                    nonce => $oauth_nonce,
									
								] );
				carp "carpppp===".Dumper $r;				
			  my $uri = URI->new( 'http:' );
		        $uri->query( $r->content );
		       my  %oauth_data = $uri->query_form;					 
			#$request_token_request->sign;
			# my $request_token_request_url = $REQUEST_TOKEN_URL . '?' . $request_token_request->to_post_body;
			 my $browser = LWP::UserAgent->new;
			# my $request_token_response = $browser->post( $request_token_request_url );
			# carp "respones===".Dumper $request_token_response;
			# my $request_token_response_query = new CGI($request_token_response->content);
			 my $oauth_token = $oauth_data{oauth_token};
             my $oauth_token_secret = $oauth_data{oauth_token_secret};
			carp "OAUTH_TOKEN : $oauth_data{oauth_token}";
            carp "OAUTH_TOKEN_SECRET : $oauth_data{oauth_token_secret}";
			my $authorization_url = $AUTHORIZATION_URL . '?oauth_token=' . $oauth_data{oauth_token};
			print $input->redirect($authorization_url);
			my $access_token_request = Net::OAuth::AccessTokenRequest->new(
				consumer_key => $CONSUMER_KEY,
				consumer_secret => $CONSUMER_SECRET,
				request_url => $ACCESS_TOKEN_URL,
				request_method => 'GET',
				signature_method => 'HMAC-SHA1',
				timestamp => time,
				nonce => int(rand(2 ** 32)),
				token => $oauth_token,
				token_secret => $oauth_token_secret,
            );
           $access_token_request->sign;
		   my $access_token_request_url = $ACCESS_TOKEN_URL . '?' . $access_token_request->to_post_body;
		   my $access_token_response = $browser->post( $access_token_request_url );
		   my $access_token_response_query = new CGI($access_token_response->content);
		   my $oauth_access_token = $access_token_response_query->param('oauth_token');
           my $oauth_access_token_secret = $access_token_response_query->param('oauth_token_secret');

		   carp "OAUTH_ACCESS_TOKEN : $oauth_access_token";
           carp "OAUTH_ACCESS_TOKEN_SECRET : $oauth_access_token_secret";
		   
		   my $image_gallery_request = Net::OAuth::ProtectedResourceRequest->new(
					consumer_key => $CONSUMER_KEY,
					consumer_secret => $CONSUMER_SECRET,
					request_url => $QUERY_API_URL,
					request_method => 'GET',
					signature_method => 'HMAC-SHA1',
					timestamp => time,
					nonce => int(rand(2 ** 32)),
					token => $oauth_access_token,
					token_secret => $oauth_access_token_secret,
				);
		  $image_gallery_request->sign;
		  my $image_gallery_request_url = $QUERY_API_URL . '?' . $image_gallery_request->to_post_body;
		  my $image_gallery_response = $browser->get( $image_gallery_request_url );
		  my $image_gallery_response_query = new CGI($image_gallery_response->content);
		  carp $image_gallery_response->content;		
			
}	
elsif($action eq 'fb_signup'){       
        
		   my $app_id           = "279195995425730";
		   my $app_secret       = "b45c261a393d9ffbb379b91fb20d87f5";
		   my $my_url           = "http://www.healthstatus.com/cgi-bin/hs/register.cgi?action=fb_signup";
     		   my $fb_user;
		
		  ## If user denied access to your site, let him take to return original page	   
		  if($input->param("error") eq 'access_denied' || $input->param("error_reason") eq 'user_denied'){
				
				$hash{win_close_tag} = 1; 		
				$hash{win_close} =  "window.close();";      		
				my $form = "/usr/local/www/vhosts/healthstatus.com/htdocs/fb_temp.html";
				fill_and_send( $form, $user, \%hash ,$config->html_use_ssi);		
				exit;
		  }
	 
	    my $code = $input->param('code');          
        if($code ne '') {				
				my $token_url = "https://graph.facebook.com/oauth/access_token?"
			   . "client_id=" . $app_id . "&redirect_uri=" . $my_url
			   . "&client_secret=" . $app_secret. "&code=" . $code;
				use LWP::UserAgent;
				my $browser = LWP::UserAgent->new();
				my $response = $browser->get($token_url);
		
				if( $response->is_success){ 
							
					my $content = $response->decoded_content;
					$content =~ /access_token=(.*?)(?:&expires=(.*))/;
					my $access_tocken = $1;           
					my $graph_url = "https://graph.facebook.com/me?access_token=$access_tocken" ;
					my $user_res = $browser->get($graph_url);

					$fb_user = decode_json ($user_res->decoded_content);			                
					
					print $session->header();
					$session->param('fb_first_name', $fb_user->{first_name});
					$session->param('fb_last_name', $fb_user->{last_name});
					$session->param('fb_db_id', $fb_user->{id});
					$session->param('fb_db_email', $fb_user->{email});
					$session->param('fb_count', '1');
				
					my %tables = %{$db->all_table_names};
					my $desired_field_unum = 'unum';
					my $desired_field = $config->db_id;				
					my $desired_table = $tables{'REG'};
					my $stipul = "WHERE $desired_field = " . "'". $fb_user->{id}."'";					
					my $db_hs_uid  =  $db->select_one_value( $desired_field, $desired_table, $stipul );
					my $user_unum  =  $db->select_one_value( $desired_field_unum, $desired_table, $stipul );
				
				    if($db_hs_uid eq $fb_user->{id}){ 
				        
								$user->{first_name} = $fb_user->{first_name};
								$user->{last_name}  = $fb_user->{last_name};									
								$user->{db_number} = $user_unum;			
								my $tnum = $user->db_number;
								
								my $expire_time = $config->session_timeout;
								my $cookie=$input->cookie(-name=>'hs_ident', -value=>"$tnum", -expires=> "+{$expire_time}m"); 					
								print $input->header( -cookie  => $cookie );
								my $uri = $config->member_page . '?hs_ident='.$tnum.'&fb_id='.$fb_user->{id};
								$hash{win_redirect} = "window.opener.location.href='$uri'; window.close();";               
								my $form = "/usr/local/www/vhosts/healthstatus.com/htdocs/fb_temp.html";				
								fill_and_send( $form, $user, \%hash ,$config->html_use_ssi);
									
                    }else{						 
								 my $uri = '/cgi-bin/hs/register.cgi' . '?action=fb_cnt';						
								 $hash{win_redirect} = "window.opener.location.href='$uri';window.close();";         
								 my $form = "/usr/local/www/vhosts/healthstatus.com/htdocs/fb_temp.html";				
								 fill_and_send( $form, $user, \%hash ,$config->html_use_ssi);						
			              }                         
                }else{
								 $hash{win_close} =  "window.close();";
								 my $form = "/usr/local/www/vhosts/healthstatus.com/htdocs/fb_temp.html";				
								 fill_and_send( $form, $user, \%hash ,$config->html_use_ssi);
					}	      
	    }else{          
								$hash{win_close} =  "window.close();";	  
								my $form = "/usr/local/www/vhosts/healthstatus.com/htdocs/fb_temp.html";	        
								fill_and_send( $form, $user, \%hash ,$config->html_use_ssi);		
	    }
			 
    }
elsif($action eq 'add_fb'){                      					  
					 
			          $user->{db_fullname} = $session->param('fb_first_name').' '.$session->param('fb_last_name') ; 
					  $user->{db_id} = $session->param('fb_db_id');
					  $user->{auth_password} = "fb_".$session->param('fb_db_id');
					  $user->{db_email} = $session->param('fb_db_email');                       					  
					  $user->siteid ( $user->siteid . "/" . $user->db_employer );					  
					  
					  $status = $approved->add( $config, $user, \%flags );
					 
			          if ($status eq TRUE || $status eq CONFIRM){
				          if($config->authenticate_confirm)
                        	{
								my $health = HealthStatus->new(
								{
									assessment => 'HRA',
									user       => $user,
									config     => $config_file,
								}
								);
											my %vars = ( link => $config->html_base . $config->cgi_dir . '/register.cgi?action=activate&id=' . $user->db_id );
											unless($health->send_email( $user , 'CONFIRM', \%vars )) { carp "send_email to ". $user->db_id . ", ". $user->db_email . " did not work.";}
							} 
			             my $tnum = $user->db_number;						
						 my $expire_time = $config->session_timeout;
						 my $cookie=$input->cookie(-name=>'hs_ident', -value=>"$tnum", -expires=> "+{$expire_time}m");
						 my $uri = $config->member_page . '?hs_ident='.$tnum.'&fb_id='.$session->param('fb_db_id');						
						 					 
                         print $input->redirect( -cookie=>$cookie, -uri=> $uri );
						 $session->clear(["fb_first_name", "fb_last_name","fb_db_id","fb_db_email","fb_count"]);
                    
					}elsif ($status eq DUPLICATE){
						$user->siteid( $beg_site );
						my $form = $config->template_directory . $config->login_register_retry;
						$hash{error_msg} = "<font style=color:red>That user name is already taken, please try a different one.</font>";
						fill_and_send( $form, $user, \%hash, $config->html_use_ssi );
			        }
    }	
elsif(	$action eq 'logout' )
	{
		$status = $approved->logout( $config, $user );
		print "logout - $status\n$user->db_number\n$member\n" if $Debug;
		my $cookie=$input->cookie(-name=>'hs_ident',
		       -value=>"",
		       -expires=> '-1M');
		$hash{'cookie'} = $cookie;
		my $goto_page;
		if($config->logout_interstitial){
			my @ignore = split /\s+/, $config->logout_inter_ignore;
			$goto_page = $config->logout_inter_template;
			my $form = $config->template_directory . $goto_page;
			fill_and_send( $form, $user, \%hash, $config->html_use_ssi,\@ignore );
			}
		else	{
			$goto_page = $config->logout_page;
			print $input->redirect( -cookie=>$cookie, -uri=> $goto_page ) if ($^O ne 'MSWin32');
			print $input->redirect( -cookie=>$cookie, -uri=> $config->html_home.$goto_page ) if ($^O eq 'MSWin32');
			}
		$stat = 1;
	}
elsif(	$action eq 'lookup' )
	{
		my %user_list;
		my $user_list_ref;
		($status, $user_list_ref) = $approved->find( $config, $user, 0 );
		%user_list = %$user_list_ref if $status;
		if ($status)
			{
			my $idline='';
			foreach (keys %user_list){
				$idline .= "$_ - User name: $user_list{$_}{db_id} - pass: $user_list{$_}{auth_password}\n";
				}
			my $message = "You are currently a";
			$message .= " member of ". $config->client ."\n\nYour user id(s) follow:\n$idline \nOur login system is case sensitive for both password and user id.\nThanks for using ". $config->client . "!";
			$message .= "\n\nThe member login can be entered at:\n". $config->html_home;
			my $from = $config->email_from;
			my $smtp = $config->email_smtp;
			my %mail = ( 	To      => $user->{db_email},
					From    => $from,
					Subject => 'Information requested from ' . $config->client,
					Message => $message,
					smtp 	=> $smtp
				   );
			sendmail(%mail);
			carp("Couldn't send email: $Mail::Sendmail::error")
				if $MAIL::Sendmail::error;
			$stat = 0;
			my $form = $config->template_directory . $config->login_sent;
			fill_and_send( $form, $user, \%hash, $config->html_use_ssi );
			}
		else	{
			$stat = 1;
			my $form = $config->template_directory . $config->login_not_sent;
			fill_and_send( $form, $user, \%hash, $config->html_use_ssi );
			}
	}

elsif(	$action eq 'adv_lookup' )
	{
		my %user_list;
		my $user_list_ref;
		($status, $user_list_ref) = $approved->find( $config, $user, 0 );
		# they gave us the user id and email address and we found them so that is good enough
		if ($status && ($input->param('db_id') && $input->param('db_email')) )
			{
			carp $status;
			my $idline='';
			%user_list = %$user_list_ref;
			foreach (keys %user_list){
				$idline .= "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Logon name: $user_list{$_}{db_id} - pass: $user_list{$_}{auth_password}<br>";
				}
			my $message = "Your logon name(s) and password(s) follow:<br>$idline <br>Our login system is case sensitive for both password and user id.";
			$idline = "";
			foreach (keys %user_list){
				$idline .= "    Logon name: $user_list{$_}{db_id}\n";
				}
			my $messagex = "You are currently a";
			$messagex .= " member of ". $config->client ."\n\nYour user id(s) follow:\n$idline \nOur login system is case sensitive for both password and user id.\nThanks for using ". $config->client . "!";
			$messagex .= "\n\nThe member login can be entered at:\n". $config->html_home;
			$messagex .= "/".$input->param('siteid') if $input->param('siteid');
			$messagex .= "\n\nThis information was requested online, if you did not request the information, please contact Amanda.Greene".'@'."lvh.com immediately.\n";
			my $from = $config->email_from;
			my $smtp = $config->email_smtp;
			my %mail = ( 	To      => $user->{db_email},
					From    => $from,
					Subject => 'Information requested from ' . $config->client,
					Message => $messagex,
					smtp 	=> $smtp
				   );
			sendmail(%mail);
			carp("Couldn't send email: $Mail::Sendmail::error")
				if $MAIL::Sendmail::error;
			$stat = 0;
			$hash{message} = $message;
			my $form = $config->template_directory . $config->login_hint;
			fill_and_send( $form, $user, \%hash, $config->html_use_ssi );
			}
		elsif($status && $input->param('db_email'))
			{
			carp "email only - ".$status;
			my $idline='';
			%user_list = %$user_list_ref;
			foreach (keys %user_list){
				$idline .= "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Logon name: $user_list{$_}{db_id}<br>";
				}
			my $message = "For security reasons we cannot provide your password based on only the data you entered, as a hint I can give you your Logon name. Your logon name(s) follow:<br>$idline <br>Our login system is case sensitive for both password and user id.";
			$idline = "";
			foreach (keys %user_list){
				$idline .= "    Logon name: $user_list{$_}{db_id}\n";
				}
			my $messagex = "You are currently a";
			$messagex .= " member of ". $config->client ."\n\nYour user id(s) follow:\n$idline \nOur login system is case sensitive for both password and user id.\nThanks for using ". $config->client . "!";
			$messagex .= "\n\nThe member login can be entered at:\n". $config->html_home;
			$messagex .= "/".$input->param('siteid') if $input->param('siteid');
			$messagex .= "\n\nThis information was requested online, if you did not request the information, please contact Amanda.Greene".'@'."lvh.com immediately.\n";
			my $from = $config->email_from;
			my $smtp = $config->email_smtp;
			my %mail = ( 	To      => $user->{db_email},
					From    => $from,
					Subject => 'Information requested from ' . $config->client,
					Message => $messagex,
					smtp 	=> $smtp
				   );
			sendmail(%mail);
			carp("Couldn't send email: $Mail::Sendmail::error")
				if $MAIL::Sendmail::error;
			$stat = 0;
			$hash{message} = $message;
			my $form = $config->template_directory . $config->login_hint;
			fill_and_send( $form, $user, \%hash, $config->html_use_ssi );
			}
		else	{
			$stat = 1;
			my $form = $config->template_directory . $config->login_not_sent;
			fill_and_send( $form, $user, \%hash, $config->html_use_ssi );
			}
	}

elsif(	$action eq 'update' || $action eq 'update_pass' )
	{
		$status = $approved->check( $config, $user );
		print "update - $status\n$user->db_number\n$member\n" if $Debug;

		if ($status ne APPROVED) {
				$user->siteid( $beg_site );
				my $form = $config->error_user;
				$hash{error_msg} = "You must login before changing your account.";
				fill_and_send( $form, $user, \%hash, $config->html_use_ssi );
				exit;
				}
 		my $form;
 		$form = $config->template_directory . $config->update_pass_page if($action eq 'update_pass');
 		$form = $config->template_directory . $config->update_page if($action eq 'update');
 		if($user->auth_reminder_quiz) {
 			my @arq_list = split /\|\|/,$config->arq;
 			print "update - $action - $arq_list[$user->auth_reminder_quiz]\n" if $Debug;
 			$hash{select} = $arq_list[$user->auth_reminder_quiz];
 			}
 		else	{
 			print "update - $action - $config->arq_alt\n" if $Debug;
 			$hash{select} = $config->arq_alt;
 			}
		$session->param('db_employer', $user->db_employer);
		fill_and_send( $form, $user, \%hash, $config->html_use_ssi );
	}
elsif($action eq 'activate')
	{
	  my $login = $input->param('id');
	  my %user1;
	  my $value=1;
          $user1{'emailCheck'} = $value;
          my $stipulations = "Where hs_uid = '$login'";
	  $status = $db->update('hs_userdata',\%user1,$stipulations );
	  print $input->redirect(-uri=> $config->login_activate ) if ($^O ne 'MSWin32');
	  print $input->redirect(-uri=> $config->html_home.$config->login_activate ) if ($^O eq 'MSWin32');
	}
elsif($action eq 'resend')
	{
		$status = $approved->check( $config, $user );
		print "update - $status\n$user->db_number\n$member\n" if $Debug;

		if ($status ne APPROVED) {
				$user->siteid( $beg_site );
				my $form = $config->error_user ;
				$hash{error_msg} = "You must login before sending activation mail";
				fill_and_send( $form, $user, \%hash, $config->html_use_ssi );
				exit;
				}
		if($config->authenticate_confirm && $status eq APPROVED)
                        	{
				my $health = HealthStatus->new(
					{
					assessment => 'HRA',
					user       => $user,
					config     => $config_file,
					}
					);
                                my %vars = ( link => $config->html_base . $config->cgi_dir . '/register.cgi?action=activate&id=' . $user->db_id );
                                unless($health->send_email( $user , 'CONFIRM', \%vars )) { carp "send_email to ". $user->db_id . ", ". $user->db_email . " did not work.";}
				my $form = $config->template_directory . $config->email_sent;
				fill_and_send( $form, $user, \%hash, $config->html_use_ssi );
				exit;
                        	}

	}

exit;

sub checkdigit_parts
	{
	my $number = @_;

	my $check_error;
	my $check_OK;

	my $first_check = substr($number, 1, 15);
	my $first_digit = substr($number, 0, 1);
	my $second_check = substr($number, 2, 14);
	my $second_digit = substr($number, 1, 1);

	if(length($number) != 16 || check_digit($first_check) != $first_digit || check_digit($second_check) != $second_digit)
		{
		print "$number not valid, $first_digit, $second_digit\n" if $Debug;
		$check_OK = 0;
		$check_error = "Bad number";
		$check_error = "Length error" if(length($number) != 16)
		}
	return ($first_check, $first_digit, $second_check, $second_digit, $check_OK, $check_error);
	}
sub check_employer_number
	{
	my ($number, $file) = @_;

	my $check_error = "Site number not valid";
	my $check_OK = 0;

	if(length($number) != 7)
		{
		print "Site $number not valid\n" if $Debug;
		$check_OK = 0;
		$check_error = "Length error" if(length($number) != 7)
		}
	else 	{
		open(NUMBERS, $file) ||
			die "Site: Can't open number file: $!  " . $file;

		while (<NUMBERS>)
			{
			chomp;

			next if /^\s*$/;  # blank
			next if /^\s*#/;  # comment

			if($number == $_){ $check_OK = 1; $check_error = ""; last; }

			}
		close(NUMBERS);
		}
	return ($check_OK, $check_error);
	}

sub backup_user {
	my ($unum) = @_;
	my $backup_txt = '';
	my $tname;
	my @tables;

	foreach my $table_key (keys %HealthStatus::Database::Tables) {
		# If this is a table that is tied to a user...
		if (($table_key eq 'REG' || $table_key eq 'PASS') || (exists ($Allowed_assessments{$table_key}) && exists($HealthStatus::Database::Fields{$table_key}{unum})) ) {
			$tname = $HealthStatus::Database::Tables{$table_key};
			push @tables, $tname;
			my @backup = $db->select_all([$tname], " WHERE unum=$unum", 1);

			foreach(@backup) {
				$backup_txt .= "\nINSERT INTO $tname(" . join(",", keys %$_) . ") VALUES (";

				my $first = 1;
				foreach(values %$_) {
					$backup_txt .= "," if !$first;
					$first = 0;
					$backup_txt .= $db->{db}->quote($_);
				}

				$backup_txt .= ");";
			}
		}
	}

	open (FH, ">" . $config->backup_directory . "user_${unum}_backup.sql")
				or (carp "Could not open backup file" && return 0);
	print FH $backup_txt;
	close FH;
	return \@tables;
}
=head1 BUGS

* none that i've found so far.

=head1 TO DO

* the error routine is simple, but you can't do much when
you can't find the right files.

* need to add some specific login error pages, bad login, email sent, bad registration

=head1 AUTHOR

Greg White <gwhite@healthstatus.com>

=head1 COPYRIGHT

Copyright 2001-2009, HealthStatus.com

=cut

1;
