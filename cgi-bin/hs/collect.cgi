#!/usr/bin/perl
use strict;

=head1 NAME

collect.cgi - post a user login

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

use vars qw( $Debug $production $cook $config_file $nph);

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
use Data::Dumper;

use HealthStatus qw( fill_and_send error check_digit );
use HealthStatus::Authenticate;
use HealthStatus::Config;
use HealthStatus::Constants;
use HealthStatus::Database;
use HealthStatus::User;
use File::Basename        qw( dirname );
use File::Spec::Functions qw( rel2abs );
use lib dirname(rel2abs($0));

my  $stat ;

carp "=================================== in collect.cgi ====================================";

CGI->nph($nph) if $nph;
my $input = new CGI();
my $config = getConfig($input->param('extracfg'));
my $session = new CGI::Session(undef, undef, {Directory=>'../../sessions'}) or die CGI::Session->errstr;
carp "Session id in collect is: ".$session->id();
$session->clear();
$session->flush();
$session->save_param();

$cook = $session->param('hs_ident') || $input->param('hs_ident') || $input->cookie('hs_ident');

$session->save_param();
$session->clear(['page', 'prev.x', 'prev.y', 'next.x', 'next.y', 'next', 'prev', 'status']);
$session->load_param($input);

#carp "Session id in collector #2 is: ".$session->id();

my %hash = map { $_, $input->param($_) } $input->param();

my %config = map { $_, $config->$_ } $config->directives;

$hash{config} = \%config;

my %input = $input->Vars();

# authenticate_user redirects the user if they not allowed to
# view this page
#my $user = authenticateUser('all', $input, $config) or die "You should never see this message.";

$hash{cookie} = $input->cookie( -name   => $session->name,
                              -value  => $session->id );
foreach (sort keys %hash){ carp "$hash{$_} - $_ \n"; }
$session->flush();

my $session_cookie = $input->cookie( -name   => $session->name, -value  => $session->id );
my $cook = $input->param('hs_ident') || $input->cookie('hs_ident');

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
	$config->pretty_print;
	}

$cook = $input->param('hs_ident') || $input->cookie('hs_ident');
my $temp_file_name = $config->authenticate_dir;
my $temp_file = $input->param('hs_ident') || $input->cookie('hs_ident');
$temp_file = '0';

# redirection pages
my $beg_site = $input->param("siteid");
my $member = $config->member_page;
my $login  = $config->login_page;
my $timeout = $config->timeout_page;
my $failed = $config->login_failed;
my $template_dir = $config->template_directory;

$hash{db_id} = $input->param('user_id') || $input->param('db_id');
$hash{db_email} = $input->param('email');
$hash{db_fullname} = $input->param('db_fullname')  || $input->param('first_name') . " " . $input->param('last_name');
if(uc($hash{sex}) eq 'M' || uc($hash{sex}) eq 'MALE'){ $hash{Personal_Sex} = MALE; $hash{sex} = MALE; $input->param('sex', MALE); } else { $hash{Personal_Sex} = FEMALE; $hash{sex} = FEMALE;  $input->param('sex', FEMALE); }
$hash{auth_password_entry} = $hash{auth_password} if $hash{auth_password};
$hash{biometric_key} = $input->param('biometric_key') ||$input->param('biokey') || $input->param('case') || $input->param('uniqueid');
$hash{birth_month} = sprintf("%02d",$input->param('birth_month')) if ($input->param('birth_month'));


$hash{config} = \%config;

delete($hash{'Submit.x'}) if (exists($hash{'Submit.x'}));
delete($hash{'Submit.y'}) if (exists($hash{'Submit.y'}));
delete($hash{'action'}) if (exists($hash{'action'}));

my $db = HealthStatus::Database->new( $config );

if(!$hash{db_number}) { $hash{db_number} = $temp_file }

$db->debug_on( \*STDERR ) if $Debug;

my $user = HealthStatus::User->new( \%hash );
my $user_change = HealthStatus::User->new( \%hash );

$user->pretty_print if $Debug;

my $auth_m_times = $config->auth_m_times || 1366;
my $auth_m_plus = $config->auth_m_plus || 150889;
my $auth_m_modulo = $config->auth_m_modulo || 714025;
my $magic_number = $input->param('mnum');
my $m_base = $magic_number;
my $m_length = substr($m_base,0,1);
my $m_seed = substr($m_base,0,$m_length+1);
my $m_compare = substr($m_base, $m_length+1);
my $m_computed = ($auth_m_times * $m_seed + $auth_m_plus) % $auth_m_modulo;
carp "magic input = $magic_number\nmagic parts: length = $m_length  seed = $m_seed  compare to = $m_compare\nFormula =  ($auth_m_times * $m_seed + $auth_m_plus) % $auth_m_modulo\nResult = $m_computed\n\n";
if ($m_compare != $m_computed && $config->Magic_required){
	print "magic input = $magic_number\nmagic parts: length = $m_length  seed = $m_seed  compare to = $m_compare\nFormula =  ($auth_m_times * $m_seed + $auth_m_plus) % $auth_m_modulo\nResult = $m_computed\n\n" if $Debug;
	carp "magic input = $magic_number\nmagic parts: length = $m_length  seed = $m_seed  compare to = $m_compare\nFormula =  ($auth_m_times * $m_seed + $auth_m_plus) % $auth_m_modulo\nResult = $m_computed\n\n";
	$hash{error_msg} = "Login calculation factor does not match - $magic_number.";
	my $form = $config->template_directory . $config->login_failed;
	$form = $config->login_failed if $config->SSO;
	fill_and_send( $form, $user, \%hash, $config->html_use_ssi );
	exit;
	}
carp "collect - checking user";
my $approved = HealthStatus::Authenticate->new( $config, $temp_file_name, $temp_file );

$approved->debug_on( \*STDERR );# if $Debug;

my $status = '';
my %flags = {};

# We try to add the user, if they already exist, we just log them on.
$status = $approved->add( $config, $user, \%flags );
carp "collect: add - $status\n$config->member_page\n$member\n";# if $Debug;
if ($status eq DUPLICATE)
	{
	$status = $approved->change( $config, $user_change );
	$status = $approved->login( $config, $user );
	carp "login - $status\n".$user->db_number."\n".$member."\n";# if $Debug;
	}

# configure cookie stuff
my $tnum = $user->db_number;
my $expire_time = $config->session_timeout;
my $cookie=$input->cookie(-name=>'hs_ident', -value=>"$tnum", -domain=>$ENV{HTTP_HOST});
my $redirect = $config->logout_page ;

$session->param('db_id',$hash{db_id});
$session->param('biometric_key',$hash{biometric_key});
$session->param('birth_month',$hash{birth_month});
$session->flush();

#if they were successfully logged in or added either setup the redirect page
#directly to an assessment (if requested) or to the member page
#aparam can be set with values to be passed to the assessment to prepopulate
#if too many parameters get passed we could exceed the GET limit of Apache and IIS
#so it may be better to move to post
carp "collect: status = $status";
if ($status eq TRUE || $status eq APPROVED)
	{
	if($input->param('streamPDF') ) {
carp "collect: streamPDF\n".$input->param('db_rec')."\n$hash{db_id}\n";# if $Debug;
		$db->debug_on( \*STDERR ) if $Debug;
		my $got_it = $db->get_users_assessment( $user, $config, uc($input->param('atype')), $input->param('db_rec') );
		$user->hs_stream_file(1);
		my $health = HealthStatus->new(
			{
			assessment => uc($input->param('assessment')),
			user       => $user,
			config     => $config_file,
			extraconfig => $input->param('extracfg'),
			}
			);

		$user->set_non_standard;
		$health->assess( $user );
		my $data = $health->output( 'pdf', $hash{template} );

		}
	elsif ( $input->param('resend') ){
carp "collect: resend\n$config->member_page\n$member\n";# if $Debug;
		}
	else	{
		my $assess_type = uc($input->param('atype'));
		my $assess_params = $input->param('aparam');
		my $output_format = '&output_format=';
		$output_format .= $config->default_output_format || 'HMTL';
		if($assess_type eq 'CRC' || $assess_type eq 'DRC' || $assess_type eq 'GHA' || $assess_type eq 'GWB' || $assess_type eq 'HRA' )
			{
			$redirect = $config->html_collector . '?assessment=' . $assess_type . $output_format . '&page=0&CGISESSID='.$session->id. '&hs_ident=' . $tnum . $assess_params;
			}
		elsif($input->param('atype') eq 'FIT' )
			{
			$redirect = $config->cgi_dir . '/fitme.cgi?page=fit_pre.html&CGISESSID='.$session->id . $assess_params;
			}
		elsif($input->param('atype') eq 'CALC' )
			{
			$redirect = $config->cgi_dir . '/calc.cgi?calc=men&hs_ident=' . $tnum.'&CGISESSID='.$session->id . $assess_params;
			}
		else	{
			$redirect = $config->member_page . "?hs_ident=" . $tnum.'&CGISESSID='.$session->id;
			}
		}
	
	}
carp "collect is redirecting to - $redirect\n";# if $Debug;
print "collect is redirecting to - $redirect\n" if $Debug;
print $input->redirect(  -cookie=>[$cookie,$session_cookie], -uri=> $redirect, -domain=>$ENV{HTTP_HOST} );

exit;

=head1 BUGS

* none that i've found so far.

=head1 TO DO

* nothing at this point

=head1 AUTHOR

Greg White <gwhite@healthstatus.com>

=head1 COPYRIGHT

Copyright 1998-2004, HealthStatus.com

=cut

1;
