#!/usr/local/bin/perl
# This file contains simple Perl subroutines that are shared amongst
# the HealthStatus code.  As of this writing (Jan 22, 2005), it is being
# used by a single file.  Eventually all scripts that use these (or similar)
# functions should use this file instead.
#

use File::Basename        qw( dirname );
use File::Spec::Functions qw( rel2abs );

use lib dirname(rel2abs($0)),'.','/usr/local/www/vhosts/managed2/modules/pdf', '/usr/local/www/vhosts/managed2/modules';

use vars qw( $Debug $production $cook $config_file $nph);

############################################################################
### Change the following line before going into production      ############
$production = 0;
#### 1 = production server, 0 = setup/test server               ############
#### this changes if error messages are sent to the browser or not #########
############################################################################

############################################################################
### Set debug for all scripts here, use the debug in the individual ########
### script for finer control                                        ########
$Debug = 0;
#### only uncomment if you need to debug the input scripts      ############
############################################################################

use HealthStatus qw( fill_and_send );
use HealthStatus::Authenticate;
use HealthStatus::Config;
use HealthStatus::Constants;
use HealthStatus::Database;
use HealthStatus::User;
use HealthStatus::Messenger;
use Data::Dumper;
use CGI qw(-no_xhtml -debug);
if (!$production) {
	use CGI::Carp qw(fatalsToBrowser);
	}
else {
	use CGI::Carp;
	}
$CGI::POST_MAX=1024 * 100;  # max 100K posts
$CGI::DISABLE_UPLOADS = 0;  # can uploads
use CGI::Session;

# build the path to find the config file. store in $work_path
my @wpath = File::Spec->splitdir(dirname(rel2abs($0)));
my $tcnt = scalar @wpath;
my $work_path;
my $j=0;
while ($j < $tcnt-2){ $work_path .= '/'.$wpath[$j]; ++$j; }
$work_path = File::Spec->canonpath( $work_path ) ;

my $operating_system = $^O;
if ($operating_system eq 'MSWin32'){
    $work_path =~ s|^\\||;
	$nph=1;
	CGI->nph($nph);
	#print $work_path;
	open(STDERR, ">> $work_path/conf/healthstatus.log") or die "Can't redirect stderr: $!";
	}
elsif ($operating_system eq 'solaris' || $operating_system eq 'sunos' ){
	open(STDOUT, "> $work_path/conf/healthstatus.log") or die "Can't redirect stdout: $!";
	open(STDERR, ">&STDOUT")  or die "Can't redirect stderr: $!";
	$nph=0;
	}
else	{
	$nph=0;
	}

$config_file = $work_path."/conf/healthstatus.conf";
$config_file = $work_path."/conf/healthstatus.local" if($ENV{SERVER_ADDR} eq '192.168.9.25');

#my $operating_system = $^O;

#if ($operating_system eq 'MSWin32'){

#	$nph=1;
#	CGI->nph($nph);
#	}
# else	{
#	$nph=0;
#	}

# if ($operating_system eq 'solaris' || $operating_system eq 'sunos' ){
#	open(STDOUT, "> $work_path/conf/healthstatus.log") or die "Can't redirect stdout: $!";
#	open(STDERR, ">&STDOUT")  or die "Can't redirect stderr: $!";
#	}

#my $operating_system = $^O;

#if ($operating_system eq 'MSWin32'){
#	$nph=1;
#	CGI->nph($nph);
#	}
#else	{
#	$nph=0;
#	}

#if ($operating_system eq 'solaris' || $operating_system eq 'sunos' ){
#	open(STDOUT, "> /usr/local/www/vhosts/managed2/base/conf/healthstatus.log") or die "Can't redirect stdout: $!";
#	open(STDERR, ">&STDOUT")  or die "Can't redirect stderr: $!";
#	}

sub assessment_name
	{
	my( $code ) = @_;

	my %assessment_names = ( HRA	=> 'General Health assesments ',
				 GHA	=> 'Health Risk assesments',
				 CRC	=> 'Cardiac Risk assesments',
				 DRC	=> 'Diabetes Risk assesments',
				 FIT	=> 'Fitness assesments',
				 GWB	=> 'General Well Being assesments',
				 MRF	=> 'Major Risk Factors assessments',
				 RRA	=> 'Robust Health assessments',
				 );

	return $assessment_names{$code} || 'Invalid assessment code';
	}

sub authenticateUser {
	my ($required_types, $input, $config) = @_;
	$required_types = (ref $required_types eq 'ARRAY') ? $required_types : [$required_types];

#$Debug = 1 if ($ENV{REMOTE_ADDR} eq '173.165.73.118');
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
	my $temp_file_name = $config->authenticate_dir;
  # use the cgi param for the identifier or if that doesn't exist use the cookie
	my $uid = $cook || int($input->param('hs_ident')) || int($input->cookie('hs_ident'));

  # If the user is not logged in and this is a public
  # area, return an empty User.  Otherwise, redirect to login page.
#	if (($uid <= 0 ||!defined($uid))) {
#		if (grep(/guest/, @$required_types)) {return new HealthStatus::User({config => $config->as_hash()});}
#		else {print $input->redirect (-uri => $config->login_page ); exit;}
#	}

	my %hash = map { $_, $input->param($_) } $input->param();
	my %config = map { $_, $config->$_ } $config->directives;
	$hash{config} = \%config;
	my $temp_file = $uid || '10001';
	$temp_file = '0' if (!$temp_file);

	my $user = HealthStatus::User->new(\%hash);

	$user->db_number ( $temp_file );

	my $approved = HealthStatus::Authenticate->new( $config, $temp_file_name, $temp_file);

	my $status = $approved->check( $config, $user );
	print "login status - $status\n" if $Debug;
	$user->pretty_print if $Debug;
	my $user_rank = $user->hs_administration();

	if ($config->group_variables){
		get_group_config( $config, $HealthStatus::Database::Tables{GRP}, $user{'siteid'} );
		my %config = map { $_, $config->$_ } $config->directives;
		$hash{config} = \%config;
		}

  # check the user rank against the priviliges required for the calling program
	if ($status eq APPROVED && (!$config->authenticate_admin || (!defined($required_types[0]) || $required_types[0] eq 'all' || grep(/$user_rank/, @$required_types)))) {return $user;}
	elsif ($status eq APPROVED) {errorPageAndExit("You are not authorized to view this page.", $user, $config);}
	
	print "Got Here somehow...\n" if $Debug;

  # what we do based on the approval status and the login method
	if ($config->authenticate_method eq 'client'){
		if ( $status eq TIMEOUT )	{print $input->redirect (-uri => $config->timeout_page,  );}
		elsif ( $status eq NOT_LOGGED )	{print $input->redirect (-uri => $config->login_page );}
		elsif ( $status ne APPROVED) { error( "There is a problem with your login." );}

		exit();
	}
	else	{
		my $form;
		my %hash;

		if ( $status eq TIMEOUT )	{$form = $config->template_directory . $config->timeout_page;}
		elsif ( $status eq NOT_LOGGED ) {$form = $config->template_directory . $config->login_page;}
		elsif ( $status ne APPROVED) {
			error( "There is a problem with your login." );
			$hash{error_msg} = "There is a problem with your login.";
			$form = $config->template_directory . $config->login_failed;
			$form = $config->login_failed if ($config->SSO);
		}

		$hash{i_am_reg_page} = 1;
		$hash{config} = $config;
		$hash{cookie}=$input->cookie(-name=>'hs_ident', -value=>"", -expires=> '+1m');
		fill_and_send( $form, $user, \%hash, $config->html_use_ssi );
		exit();
	}

	# Deal with redirects here.
	return undef;
}

sub errorPageAndExit {
	my ($error, $user, $config) = @_;
	fill_and_send( $config->template_directory . "admin_error_page.tmpl",
			$user, {config=>$config->as_hash(), msg=>$error}, $config->html_use_ssi );
	exit();
}

sub getConfig {
	my $extraconfig = @_;
	my $config = new HealthStatus::Config($config_file);   
	my @common_assessments;

   # if an extraconfig file parameter is passed and the master config file allows it we read the extra config
   # the extra config will override any previously set configuration variables, this will allow you
   # set default values and then override them for co-branded sites or sites on a different domain
   
	if($config->extra_conf_on_subdomain){
	   
		my $domain = $ENV{SERVER_NAME};		
		my @domain_parts = split /\./,$domain;
		my $subdomain = $domain_parts[0];		
		$extraconfig = $subdomain . '_config.conf';
		}
		
	if($extraconfig && $config->extra_allowed) { 
		$config->add_config_file( $config->extra_conf_dir . $extraconfig );
		}
		
   # Fill config with ggr_adv config info as well.
	if ($config->ggr_adv_conf){
		$config->add_config_file( $config->ggr_adv_conf );
		@common_assessments = split /\s+/, $config->ggr_adv_tables;
		}
   # Fill config with pt config info as well.
	if ($config->pt_conf && ptracker_on){$config->add_config_file( $config->pt_conf ); }
   # open a database connection based on the configuration information
	$$config{db} = new HealthStatus::Database($config);
   # get configuration data from database
  
  if ( lc($config->db_driver) eq 'mssql' ){
	  
	  # For MSSQL 
	    my $table_flag = $$config{db}->execute_sql_return("select name from sysobjects where type='U' and name like 'hs_configuration'");
	}
	else
    {
        # Using MySQL
     my $table_flag = $$config{db}->execute_sql_return("show tables like 'hs_configuration'");
	 }

   	if($config->extra_from_db && $table_flag){
			
			my $hash_ref = $$config{db}->get_default_config_variables();
			$config->add_from_hash( $hash_ref );
   		}
	my @batch_assessments = split /\s+/, $config->batch_assessments;
	$$config{batch_assessments} = \@batch_assessments;
	$$config{common_assessments} = \@common_assessments;
	    
	return $config;
}

sub login {
	# System config, input params, cgi object
	my ($config, $hash_ref, $input) = @_;

	error( "The configuration object is bad after passing it to login." ) unless ref $config eq 'HealthStatus::Config';

	require HealthStatus::Authenticate;

	my %hash = %$hash_ref;
	my $user = HealthStatus::User->new( \%hash );
	my $temp_file_name = $config->authenticate_dir;
	my $temp_file = $input->param('hs_ident') || $input->cookie('hs_ident') || '10001';
	$user->db_number ( $temp_file );

	print "Temp file = $temp_file\n" if $Debug;

	my %config = map { $_, $config->$_ } $config->directives;

	$hash{config} = \%config;

	delete($hash{'Submit.x'}) if (exists($hash{'Submit.x'}));
	delete($hash{'Submit.y'}) if (exists($hash{'Submit.y'}));
	delete($hash{'action'}) if (exists($hash{'action'}));

	my $approved = HealthStatus::Authenticate->new( $config, $temp_file_name, $temp_file );

	my $status = $approved->check( $config, $user );

	print "Login status = $status\n" if $Debug;

	if ($config->authenticate_method eq 'client'){
		if ( $status eq TIMEOUT )
			{
			print $input->redirect (-uri => $config->timeout_page );
			exit;
			}
		elsif ( $status eq NOT_LOGGED )
			{
			print $input->redirect (-uri => $config->login_page );
			exit;
			}
		elsif ( $status ne APPROVED)
			{
			error( "There is a problem with your login." );
			exit;
			}
		}
	else	{
		if ( $status eq TIMEOUT )
			{
			$hash{cookie}=$input->cookie(-name=>'hs_ident',
			       -value=>"",
			       -expires=> '+1m');
			my $form = $config->template_directory . $config->timeout_page;
			fill_and_send( $form, $user, \%hash, $config->html_use_ssi );
			exit;
			}
		elsif ( $status eq NOT_LOGGED )
			{
			$hash{cookie}=$input->cookie(-name=>'hs_ident',
			       -value=>"",
			       -expires=> '+1m');
			my $form = $config->template_directory . $config->login_page;
			fill_and_send( $form, $user, \%hash, $config->html_use_ssi );
			exit;
			}
		elsif ( $status ne APPROVED)
			{
			error( "There is a problem with your login." );
			$hash{error_msg} = "There is a problem with your login.";
			my $form = $config->template_directory . $config->login_failed;
			fill_and_send( $form, $user, \%hash, $config->html_use_ssi );
			exit;
			}
		}
	return ($user);
}
sub get_group_config {
	my ($config, $table, $grp) = @_;
	$grp =~ s/'/\\'/;

	my $stipulation = " WHERE groupID=$grp";

	my $query_results = $db->select_one_row('*', $table, $stipulation, 1);

	$config->add_from_hash($query_results);

	return 1;
}

1;