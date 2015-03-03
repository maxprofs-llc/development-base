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
# Removing warnings in log while module is being used with CGI version 4 or above
$CGI::LIST_CONTEXT_WARN = 0;	
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
	 qw( add change change_pass confirm delete login logout lookup update update_pass enroll add_many bootstrap log activate resend adv_lookup);
#	 qw( add change check confirm delete fix_email login logout lookup remove subscribe update update_pass );

my $action = lc $input->param('action');

print "Action = $action\n" if $Debug;

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
	if ($config->SSO){
		$form = $config->login_register_retry ;
		print $input->redirect( -uri=> $form );
		exit;
		}
	$hash{error_msg} = "That action is not permitted, please login again.";
	fill_and_send( $form, $user, \%hash, $config->html_use_ssi );
	exit;
	}

if($action eq 'enroll'){
	my $form = $config->template_directory . $config->login_register_retry;
	$form = $config->login_register_retry if $config->SSO;
	if ($config->SSO){
		$form = $config->login_register_retry ;
		print $input->redirect( -uri=> $form );
		exit;
		}
	fill_and_send( $form, $user, \%hash, $config->html_use_ssi );
	exit;
	}
elsif($action eq 'log'){
	my $form = $config->template_directory . $config->login_failed;
	$form = $config->login_failed if $config->SSO;
	if ($config->SSO){
		$form = $config->login_register_retry ;
		print $input->redirect( -uri=> $form );
		exit;
		}
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
	if ($config->SSO){
		$form = $config->login_register_retry ;
		print $input->redirect( -uri=> $form );
		exit;
		}
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
			my ($emptemp, $subtemp) = split(/\//, $user->db_employer);
			my $stipulation = 'Where groupID = '. "'".$emptemp."'";
			print STDERR "\nstipulatin====$stipulation=====$emptemp, $subtemp";
			$check_OK = $db->get_group($stipulation);
			if($subtemp && $check_OK){
				my %tmpgroups = %$check_OK;
				 $check_OK = index($tmpgroups{subgroupNames}, $subtemp);
				}				
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
		else{
			$user->siteid( $beg_site );
			$user->pretty_print if $Debug;
			$hash{error_msg} = "You have entered an incorrect username or password, please enter the same exact username or password you used for Health Assessment registration, or create a new username and password, thanks.";
			my $form = $config->template_directory . $config->login_failed;
			fill_and_send( $form, $user, \%hash, $config->html_use_ssi );
			$stat = 1;
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
