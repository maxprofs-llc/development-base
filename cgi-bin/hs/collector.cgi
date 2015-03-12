#!/usr/local/bin/perl
# $Id: collector.cgi.PL,v 1.2 2010/04/27 09:53:08 code4hs Exp $
use strict;

=head1 NAME

collecter.cgi - collect data along a CGI template input chain

=head1 DESCRIPTION

Use this script as the ACTION target for each HTML form, except
for the last one, in a multi-page input chain.  The last ACTION
target should be a routine to process all of the data.

=head1 INPUT

This script depends on certain control parameters to tell it what to
do.

	assessment	- the type of assessment (FIT, CRC, etc.)
	page        - the current position in the chain, starting at 1

The script uses these parameters to load certain configuration
directives. The configuration files stores the required fields
in directives named after the assessment in page in the form

	<assessment>_required_fields_<page>

so that if C<assessment> is C<hra> and C<page> is C<2> then the
configuration directive that hold the required fields is

	hra_required_fields_2

Additionally, some fields are checked to ensure that they contain
integer values.  These fields are stored in the configuration
directive C<integer_fields> no matter the assessment.  If any
of the fields specified in C<integer_fields> show up in the
input, the script will remove all non-numeric characters from
their values.

The script expects the values of these configuration directives
to be a whitespace separated list of field names, such as

	integer_fields	height weight

so that the script checks C<height> and C<weight> for integer values.

The image submit buttons specify the template that the
script loads with one of two possible values.  If the name
of the image submit input type is C<next>, then the script
increments the value of C<page> , while if the value of the
submit input is C<prev>, the script decrements the value of
C<page>. The script uses the new value of C<page> to select
the next template in these cases.  If a third possible name
of the submit button, C<assess>, the script takes all of the
input and creates a C<HealthStatus::User> object from it.  That
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
C<assessment>, or the control parameter C<name>, it outputs
an error page.

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

use HealthStatus qw ( error html_error fill_and_send );
use HealthStatus::Constants;
use Date::Calc;
use HealthStatus::CalcRisk;
use CGI::Carp;
use JSON;
use LWP::UserAgent;
use LWP::Authen::OAuth;
use Data::Dumper;

# Removing warnings in log while module is being used with CGI version 4 or above
$CGI::LIST_CONTEXT_WARN = 0;

#my $input = new CGI();
my $input = CGI -> new;
my $config = getConfig($input->param('extracfg'));
my $session = CGI::Session->new(undef, undef, {Directory=>'../../sessions'}) or die CGI::Session->errstr;
#my $session = new CGI::Session(undef, undef, {Directory=>'../../sessions'}) or die CGI::Session->errstr;
carp "Session id in collector is: ".$session->id() if($ENV{REMOTE_ADDR} eq '173.165.73.118');
$cook = $session->param('hs_ident') || $input->param('hs_ident') || $input->cookie('hs_ident');
$session->param('hs_client',$config->client);
$session->flush();# unless ($ENV{REMOTE_ADDR} eq '173.165.73.118');

if($input->param('page') == 0 && !$config->prepopulate) {
	carp "collector: session clear" if($ENV{REMOTE_ADDR} eq '173.165.73.118');
	$session->clear();	
	$session->param('hs_ident',$cook);
} else {
	$session->param('hs_ident',$cook);
	$session->save_param();
	$session->clear(['page', 'prev.x', 'prev.y', 'next.x', 'next.y', 'next', 'prev', 'status']);
	my @image_submits = map { lc } grep { m/\.[xy]$/i } $session->param;
	$session->clear(\@image_submits);
	$session->load_param($input);
}
$session->flush();# unless ($ENV{REMOTE_ADDR} eq '173.165.73.118');
carp "Session id in collector #2 is: ".$session->id(). " dump\n".$session->dump() if($ENV{REMOTE_ADDR} eq '173.165.73.118');

my %hash = map { $_, $input->param($_) } $input->param();	

my %config = map { $_, $config->$_ } $config->directives;

$hash{config} = \%config;

my %input = $input->Vars();
if($ENV{REMOTE_ADDR} eq '173.165.73.118'){ carp "Hash dump\n"; foreach (sort keys %input){ carp $_." - ".$input{$_}; }}

# authenticate_user redirects the user if they not allowed to
# view this page
my $user = authenticateUser('all', $input, $config) or die "You should never see this message.";

$hash{cookie} = $input->cookie( -name   => $session->name,
                              -value  => $session->id );
$session->flush();# unless ($ENV{REMOTE_ADDR} eq '173.165.73.118');
carp "Session id in collector #3 is: ".$session->id(). " dump\n".$session->errstr() if($ENV{REMOTE_ADDR} eq '173.165.73.118');
my $first_pass = 1;
############################################################################
### Comment out the following line before going into production ############
$Debug = $input->param("HS_Debug") || $ENV{HS_DEBUG} || $Debug if (!$production && $ENV{REMOTE_ADDR} eq '173.165.73.118');
#### only uncomment if you need to debug the input scripts      ############
############################################################################

if ($Debug) {
        print "Content-type: text/plain\n\n";
	$config->pretty_print;
	print " *********  HS_IDENT Cookies or param ************************\n";
	print "This is what I see in the cookie hs_ident - ". $input->cookie('hs_ident')  . "\n" ;
	print "This is what I see in the parameter hs_ident - ". $input->param('hs_ident')  . "\n" ;
	print " **************************************************************\n";
	$user->pretty_print;
	}

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
my $sex = $input->param('sex');
print "Assessment = $assessment\n" if $Debug;
error( "The assessment [$assessment] is not allowed" )
	unless exists $Allowed_assessments{$assessment};

my $max_pages = $Allowed_assessments{$assessment};
print "Max pages = $max_pages\n" if $Debug;

# which page number are we on?
my $page = int $input->param('page');
my $language = $input->param('language');
print "Page is $page\n" if $Debug;
if( defined $page and $page == 0 ) # load the first page
	{
	$input->param('next.x', 'next.x');
	}
elsif( not( defined $page and $page <= $max_pages and $page > 0 ) )
	{
	error( "Bad page - $page" );
	}

# check for required fields
my $method = "${assessment}_required_fields_${page}";
print "Method is $method<br>\n" if $Debug;
my @required_fields = split /\s+/, $config->$method;
print "Required are @required_fields<br>\n" if $Debug;

my @missing_required_fields =
	map
	{
	my $value = $input->param($_);
	( defined $value and $value ne "" ) ? () : "$_, "
	} @required_fields;
print "Missing is @missing_required_fields<br>\n" if $Debug;

# only error if we are moving forward so that users can
# go back to correct things
if( @missing_required_fields and ( $input->param('next.x')
	or $input->param('assess.x') ) )
	{
	html_error($config, "Some needed information was not included - " .
		"@missing_required_fields" .
		"<br><br>Click your back button and make sure these " .
		"fields have valid data.",
		"Missing information", "assessment 03");
	}

# make sure integer fields only have integers in them

my @integer_fields = split /\s+/, $config->integer_fields;
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

# check the entered date if birthday fields exist
if( grep { /birth_(year|month|date)/ } $input->param )
	{
	my $year  = $input->param('birth_year');
	my $month = $input->param('birth_month');
	my $date  = $input->param('birth_date');

	unless( Date::Calc::check_date( $year, $month, $date ) )
		{
		html_error($config, "The values entered for date of birth are invalid. ".
			"$month/$date/$year<br><br>Click your back button and".
			" make sure these fields have valid data.",
			"Bad birthdate", "assessment 03a");
		}
	}
require HealthStatus::Database;

my $db = HealthStatus::Database->new( $config );
# set the next page
my @image_submits = map { lc } grep { m/\.[xy]$/i } $input->param;
my( $image_submit ) = $image_submits[0] =~ m/(.*)\.[xy]/;
$user->{pageno} = $page;
my $inserted_flag = '0' || $session->param('insert_flag');

if( ($image_submit eq 'next' || $input->param('next') || lc($input->param('hidButtonName')) eq 'next' ) &&
	$page < $max_pages)
	{
	
	# if($inserted_flag){
		# $db->save_users_assessment( $user, 'TEMP_GHA' );			
	# }	
	$input->param( 'page', ++$page );
	$session->param('insert_flag', 1);
	}
elsif( ($image_submit eq 'prev' || $input->param('back') || lc($input->param('hidButtonName')) eq 'back')  &&
	$page > 1)
	{
	$input->param( 'page', --$page );
	$first_pass = 0;
	$session->param('insert_flag', 0);
	}
elsif( ($image_submit eq 'assess' || $input->param('submit') || lc($input->param('hidButtonName')) eq 'submit' ) ||
	$page >= $max_pages)
	{
	$first_pass = 0;
	$session->param('insert_flag', 0);
	$user->set_non_standard;

	my $health = HealthStatus->new(
		{
		assessment => uc($assessment),
		user       => $user,
		config     => $config_file,
		extraconfig => $input->param('extracfg'),
		}
		);

	$health->assess( $user );	

	$db->debug_on( \*STDERR ) if $Debug;
   
	$user->{batch_add1} = $user->{oauth_verifier};
	$user->{batch_add2} = $user->{oauth_token_update};
	$user->{batch_add3} = $user->{oauth_token_secret_update};
	#$db->save_users_assessment( $user, 'TEMP_GHA' );
	$db->save_users_assessment( $user, uc($assessment) );

	if( (!$db->email_sent($user) && $config->attaboy_first_only && $config->send_attaboy) ||
		( !$config->attaboy_first_only && $config->send_attaboy ))
			{
			$health->send_email( $user , 'ATTABOY' );
			$db->save_users_assessment( $user, 'EM' ) if $config->attaboy_first_only;
			}

	if( $config->db_extra_table )
			{
			### these are client specific values ####
			my $stipulations = "where memberId='" . $user->db_id . "' and moduleName='" . uc($assessment) . "'";
			my ($year_ex, $mon_ex, $mday_ex, $mhour_ex, $mmin_ex, $msec_ex) = Date::Calc::Today_and_Now();
			$user->client1( 'completed' );
			$user->client2( sprintf("%04d%02d%02d", $year_ex, $mon_ex, $mday_ex));
			my $table_to_change = 'LA';

			### end client specific values ####

			my $db1 = HealthStatus::Database->new_extra( $config->db_connect_extra, $config->db_user_extra, $config->db_pass_extra, $config->db_driver, $config );
			$db1->debug_on( \*STDERR ) if $Debug;
			$db1->update_users_assessment( $user, $table_to_change, $stipulations ) if ($config->db_extra_method == 'update');
			$db1->save_users_assessment( $user, $table_to_change ) if ($config->db_extra_method == 'add');
			$db1->finish( );
			$db1->disconnect( );
			}
	if( $config->JSON_Output )
			{
			my %json_data;
			my $export_list_name = 'JSON_'. lc($assessment).'_export';
			carp $export_list_name;
			my @export_list = split /\s+/, $config->$export_list_name;
			foreach (@export_list){
				$json_data{$_} = $user->{$_};
				}
			my $json_export = encode_json \%json_data;
			carp $json_export;
			if($config->JSON_post_type eq 'application'){
				my $ua = LWP::UserAgent->new;			
				my $req = HTTP::Request->new( POST => $config{JSON_post});
				$req->content_type('application/json');
				$req->content($json_export);			
				my $res = $ua->request($req);
				if ($res->is_success) {
					carp 'JSON post complete'; 
					}
				else 	{
					carp 'JSON Error Response = '. $res->status_line;
					}
				}
			elsif($config->JSON_post_type eq 'OAuth'){
				my $ua = LWP::Authen::OAuth->new(
				                oauth_consumer_key => $config->OAUTH_Consumer,
				                oauth_consumer_secret => $config->OAUTH_Consumer_Secret,
				        );				        
				 my $request_token = $session->param('oauth_token_update') ||  $input->param('oauth_token_update');
				 my $request_token_secret = $session->param('oauth_token_secret_update') || $input->param('oauth_token_secret_update');
				  carp "request token from collector.cgi====$request_token";
				  carp "request token secret from collector.cgi====$request_token_secret";
				 $ua->oauth_token_secret($request_token_secret); 
				 my $verifier = $session->param('oauth_verifier') ||  $input->param('oauth_verifier');
				 carp "verifier collector.cgi========$verifier";
				 my $res = $ua->post( $config{JSON_post},[					
						        oauth_token => $request_token,
                            	oauth_verifier => $verifier, 
                            	phi => $json_export,
						]);
				carp 'OAuth request error: '. Dumper($res->{_request}{_headers}{authorization}) if $res->is_error;					
				
				$ua->oauth_update_from_response( $res );
				if ($res->is_success) {
					carp 'JSON OAuth post complete'; 
					}
				else 	{
					carp 'JSON OAuth Error Response = '. $res->status_line;
					}
				}
			else{
				carp 'JSON Error - JSON_post_type is invalid set to: '. $config->JSON_post;
				}
			}

	if( $config->XML_Output )
			{
			my %xml_data;
			my $xml_export;
			if( $config->XML_Output_Report){
				$xml_export = $health->output('xml');
				}
			else	{
				my $export_list_name = 'XML_'. lc($assessment).'_export';
				carp $export_list_name;
				my @export_list = split /\s+/, $config->$export_list_name;
				foreach (@export_list){
					$xml_data{$_} = $user->{$_};
					}
				$xml_export = encode_json \%xml_data;
				}
			carp $xml_export;
			if($config->XML_post_type eq 'application'){
				my $ua = LWP::UserAgent->new;			
				my $req = HTTP::Request->new( POST => $config{XML_post});
				$req->content_type('application/xml');
				$req->content($xml_export);			
				my $res = $ua->request($req);
				if ($res->is_success) {
					carp 'XML post complete'; 
					}
				else 	{
					carp 'XML Error Response = '. $res->status_line;
					}
				}
			elsif($config->XML_post_type eq 'OAuth'){
				my $ua = LWP::Authen::OAuth->new(
				                oauth_consumer_key => $config->OAUTH_Consumer,
				                oauth_consumer_secret => $config->OAUTH_Consumer_Secret,
				        );				        
				 my $request_token = $session->param('oauth_token_update') ||  $input->param('oauth_token_update');
				 my $request_token_secret = $session->param('oauth_token_secret_update') || $input->param('oauth_token_secret_update');
				  carp "request token from collector.cgi====$request_token";
				  carp "request token secret from collector.cgi====$request_token_secret";
				 $ua->oauth_token_secret($request_token_secret); 
				 my $verifier = $session->param('oauth_verifier') ||  $input->param('oauth_verifier');
				 carp "verifier collector.cgi========$verifier";
				 my $res = $ua->post( $config{JSON_post},[					
						        oauth_token => $request_token,
                            	oauth_verifier => $verifier, 
                            	phi => $xml_export,
						]);
				carp 'OAuth request error: '. Dumper($res->{_request}{_headers}{authorization}) if $res->is_error;					
				
				$ua->oauth_update_from_response( $res );
				if ($res->is_success) {
					carp 'JSON OAuth post complete'; 
					}
				else 	{
					carp 'JSON OAuth Error Response = '. $res->status_line;
					}
				}
			else	{
				carp 'JSON Error - JSON_post_type is invalid set to: '. $config->JSON_post;
				}
			}
	$db->finish( );

	$db->disconnect( );
	print "Content-type: text/plain\n\n" if ($config->pdf_debug);
    my($data,$mime);
	my $m_format = lc $input->param('output_format') || DEFAULT_OUTPUT_FORMAT ;
	carp "collector: m_format = $m_format\n";
        $mime = $health->mime(   lc $input->param('output_format') );
        if($config->no_assessment_report){
        	my $tnum = $input->cookie('hs_ident') || $input->param('hs_ident');
		my $form = $config->no_assessment_report_redirect || $config->member_page . "?hs_ident=" . $tnum.'&CGISESSID='.$session->id;
		carp "collector no assessment redirect: ". $form;
		print $input->redirect( -uri=> $form, -domain=>$ENV{HTTP_HOST} );
		exit;
		}
        elsif(($user->auth_emailCheck != 9 && $config->authenticate_confirm) || !$config->authenticate_confirm)
        {
		my $template;

		if($user->db_template){
#			if($user->db_template eq '_espanol') { $user->language( 'espanol'); }
			my $template_lookup = lc $assessment . '_' . lc $m_format .  lc $user->db_template . '_template';
			$template = $config->$template_lookup;
			}
		$data = $health->output( lc $m_format, $template, $session );
		if ($data ne 'PDF') { print $input->header(-type => $mime ), $data; }

        }
        else
        {
		my $form = $config->template_directory.$config->email_confirm;
		fill_and_send( $form, $user, \%hash, $config->html_use_ssi );
		exit;
        }

	exit 1;
	}

# set the variable for the next template
my $qset = "_" . $input->param('qset') if ($input->param('qset')  && lc($input->param('qset')) ne 'imperial');
my $template = $config->template_directory . $assessment . $qset . "_qset.html";
# stay compatible with old template retrieval method (1 file per page)
unless (-e $template) {
	$template = $config->template_directory . $assessment . "_q$page.html";
	}

print "template is $template<br>\n" if $Debug;
print STDERR "template is $template\n"; 
# if( $config->prepopulate && $page == 1 && $first_pass ){ 
	# my @name_parts = split / /,$user->db_fullname;
	# $user->first_name(@name_parts[0]);
	# $user->last_name(@name_parts[1].' '.@name_parts[2]);
	# }

my $health = HealthStatus->new(
	{
	assessment => uc($assessment),
	user       => $user,
	config     => $config_file,
	extraconfig => $input->param('extracfg'),
	}
	);

$health->assess( $user );

# pass along all of the data in hidden fields
$hash{curr_page} = $page;
$hash{page} = $page;
$hash{sex} = $sex;
$hash{language} = $language;
foreach my $key ( $user->attributes ) { $hash{$key} = $user->get($key);  }
if($ENV{REMOTE_ADDR} eq '173.165.73.118'){ carp "Hash dump\n"; foreach (sort keys %hash){ carp $_." - ".$hash{$_}; }}
$session->flush();

fill_and_send( $template, $user, \%hash, $config->html_use_ssi );

=head1 BUGS

* none that i've found so far.

=head1 TO DO

* it would be nice if the templates names in the HTML forms
were not the same as the actual file names.  that way, we could
allow only certain template names and never tell the user what
the file names are.

* the same issue exists for configuration files.

* the error routine is simple, but you can't do much when
you can't find the right files.

=head1 AUTHOR

brian d foy <bdfoy@cpan.org>
Greg White <gwhite@healthstatus.com>

=head1 COPYRIGHT

Copyright 2001-2009, HealthStatus.com

=cut

1;
