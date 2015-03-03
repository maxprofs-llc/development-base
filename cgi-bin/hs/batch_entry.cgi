#!/usr/local/bin/perl
use strict;

use File::Basename        qw( dirname );
use File::Spec::Functions qw( rel2abs );

use lib dirname(rel2abs($0)),'.','/usr/local/www/vhosts/managed2/modules/pdf', '/usr/local/www/vhosts/managed2/modules';

use vars qw( $Debug $production $cook $config_file $nph);

############################################################################
### Change the following line before going into production      ############
$production = 0;
#### 1 = production server, 0 = setup/test server               ############
############################################################################

if (!do('common.inc')) {
   my $error = $@ ? $@
             : $! ? $!
             : 'did not return a true value';
   die("Unable to load common stuff: $error\n");
}

use CGI::Carp;
use Date::Calc;
use HealthStatus qw ( error html_error fill_and_send );
use HealthStatus::Constants;
use HealthStatus::CalcRisk;

my $input = CGI->new();
my $config = getConfig($input->param('extracfg'));

my $session = new CGI::Session(undef, undef, {Directory=>'../../sessions'}) or die CGI::Session->errstr;
$session->save_param();

my %hash = map { $_, $input->param($_) } $input->param();

my %config = map { $_, $config->$_ } $config->directives;

$hash{config} = \%config;

my %input = $input->Vars();

$cook = $session->param('hs_ident') || $input->param('hs_ident') || $input->cookie('hs_ident');
$session->param('hs_ident',$cook);
$session->load_param($input);

my %hash1 = $input->Vars();
my %hash;
my %vars;
my $batch_user;
my @ignore;

#$Debug = 1;
# we do this step because we basically have two users, the person doing the input
# and the person that filled out the assessment form.  So if we have a legitimate batch
# then we need to keep the information for the data entry person slightly separate
if($input->param('db_batch_number')){
	$hash{db_id} = $input->param('db_batch_entered_by');
	my @keep_these = qw( db_batch_number db_batch_entered_by db_batch_printdate db_batch_count db_batch_count_crc
			     db_batch_count_drc db_batch_count_fit db_batch_count_gha db_batch_count_gwb db_batch_count_hra
			     db_batch_count_mr db_batch_count_pt assessment page hs_ident );
	foreach (@keep_these){
		$hash{$_} = $input->param($_);
		}
	}
# otherwise, this is the first time through and nothing has been entered
else	{
	%hash = %hash1;
	}

my( $year, $month, $day, $hour, $min, $sec ) = (localtime)[5,4,3,2,1,0];
$year  += 1900;
$month += 1;

my $date = sprintf("As of %02d/%02d/%04d", $month, $day, $year);
my $date_stamp = sprintf("%02d-%02d-%04d-%02d-%02d-%02d", $month, $day, $year, $hour, $min, $sec);
my $tight_date = sprintf("%04d%02d%02d%02d%02d%02d", $year, $month, $day, $hour, $min, $sec);

if ($Debug) {
	print "Content-type: text/plain\n\n";
	print "$ENV{SCRIPT_NAME} - $ENV{QUERY_STRING}\n";
	print "Modules Versions:\nHealthStatus - $HealthStatus::VERSION\nHealthStatus::Authenticate - $HealthStatus::Authenticate::VERSION\nHealthStatus::Database - $HealthStatus::Database::VERSION\n";
	print "HealthStatus::Config - $HealthStatus::Config::VERSION\nHealthStatus::User - $HealthStatus::User::VERSION\n\n";
	foreach my $key ( sort keys %hash )
		{
		print "\t$key\t\t$hash{$key}\n";
		}
	$config->pretty_print;
	print " *********  HS_IDENT Cookies or param ************************\n";
	print "This is what I see in the cookie hs_ident - ". $input->cookie('hs_ident')  . "\n" ;
	print "This is what I see in the parameter hs_ident - ". $input->param('hs_ident')  . "\n" ;
	print " **************************************************************\n";
	}
carp "at top ". $hash{db_batch_number}." - ".$hash{db_id}."\n";

my %config = map { $_, $config->$_ } $config->directives;

# this logs in the data entry user
my ($user) = login_local ( $config, \%hash );

if($hash{db_batch_number}){ $user->db_batch_number( $hash{db_batch_number} ); }
$user->pretty_print if $Debug;
carp "after login ". $user->db_batch_number." - ".$user->db_id."\n";


# users aren't allowed to enter batch forms so just return them to the assessment recs page.
if($user->hs_administration eq 'user') {
	my $tnum = $user->db_number;
	my $expire_time = $config->session_timeout;
	my $cookie=$input->cookie(-name=>'hs_ident', -value=>"$tnum", -expires=> "+{$expire_time}m");
	print $input->redirect( -cookie=>$cookie, -uri=> $config->member_page );
	exit;
	}

if($input->param('close')){
   
       my $batch_content;
	   print "In close routine\n" if $Debug;
	   my $str='';
	   $str=$input->param('db_batch_number');
       my @db_batch_number=split(/,/,$str);
	   my $c=0;
	  
	   while($db_batch_number[$c] ne ''){	
	   if(!$input->param('db_id')){
	   print "No db_id routine\n" if $Debug;
	   # if there is not a db_id, then we closed from an admin screen
	   # (not actually during the batch process) so we have to lookup the details
		my @batch_pieces = $db_batch_number[$c];
		my @batch_pieces_1 = split(/-/,$batch_pieces[2]);
		
		$hash1{$db_batch_number[$c]} = $batch_pieces[2];
		$hash1{db_batch_entered_by} = $batch_pieces_1[0];		
		$batch_user = HealthStatus::User->new( \%hash1 );		
		print "In CLOSE - $hash1{db_batch_number}\n" if $Debug;
        
		# this gets the counts based on the batch number passed to us
		my $status = get_counts($db_batch_number[$c], $batch_user, $config);
		print STDERR "batch++++++  $db_batch_number[$c]\n";
		print "Cardiac "   .$batch_user->db_batch_count_crc ;
		print "$status\n" if $Debug;
		if(!$status){ error("batch not found - $hash1{db_batch_number} - can not restart");}

		$batch_user->pretty_print if $Debug;
		}
 else{
	    my $str1='';
		$str1=$db_batch_number[$c];
		print "Exisiting db_id routine\n" if $Debug;
	    # if you are here, you closed an active batch, so we don't need to look stuff up
		$hash1{db_number} = '';
		$hash1{db_email} = 'null@healthstatus.com';
		$hash1{db_emailOK} = '0';
		$hash1{hs_administration} = 'closed_batch';
		$hash1{db_employer} = '';
		$hash1{db_fullname} = 'batch - ' . $str1;
		$hash1{db_id} = $input->param('db_id');
       		
		$batch_user =HealthStatus::User->new( \%hash1 );	
	    
	   }
	   	   
	  
	  $batch_user->pretty_print if $Debug;
	  my $temp_file_dir = $config->authenticate_dir;
	  my $temp_file = '10001';
	  my $approved1 = HealthStatus::Authenticate->new( $config, $temp_file_dir, $temp_file );
	  $batch_user->hs_administration('closed_batch');
	  $hash1{hs_administration} = 'closed_batch';
	  my $status1 = $approved1->change( $config, $batch_user );
	  my $batch_collector = "$config{batch_collector}" || "$config{cgi_dir}/batch_entry.cgi";
      my $batch_printer	= "$config{batch_printer}" || "$config{cgi_dir}/batch_print.cgi";
	  my $batch_print = "$config{batch_printing}" || "$config{cgi_dir}/batch_print.cgi";
      my $print_batch = "$batch_printer?print=1&db_batch_number=batch - " .$batch_user->db_batch_number; 
	  
	  print "Login change status = $status1\n" if $Debug;
	 
	  %vars = map { my $x = $_; $x =~ tr/A-Za-z_//c; $x, $input->param($_) }
		$input->param;		    
		 
	   $vars{config} = \%config;
	    # print the values for multiple check box selection
	    $batch_content .= "<table border=0 cellspacing=0 cellpadding=0>";
		$batch_content .= "<tr>";
		$batch_content .= "<td></td>";
		$batch_content .= "<td align=left class=HStitle>";
		$batch_content .= "Closing Batch -" .$batch_user->db_batch_number. "<br>";
		$batch_content .= "</td></tr>";
		$batch_content .=  "<tr>";	
		$batch_content .=  "<td width=12>&nbsp;</td>";
		$batch_content .=  "<td align=center valign=top>";		
		$batch_content .=  "<table border=0 cellspacing=0 cellpadding=0 align=right>";
		$batch_content .=  "<tr><td class=HSbodytext colspan=3><br />&nbsp;<br />";
		$batch_content .=  "Entered by:" .$batch_user->db_batch_entered_by. "<br>";
		$batch_content .=  "Entered on:" .$date. " <br />&nbsp;<br />";
		$batch_content .=   "</td></tr>";
		$batch_content .=   "<tr><td align=right class=HSbodytext>";
		$batch_content .=   "Assessment &nbsp;&nbsp;&nbsp;  count<br /> ";
		$batch_content .=   "---------------------<br />";				
	    $batch_content .= "Cardiac &nbsp;&nbsp;&nbsp;"   .$batch_user->db_batch_count_crc . "<br>" ;
		$batch_content .= "Diabetes &nbsp;&nbsp;&nbsp;"   .$batch_user->db_batch_count_drc . "<br>" ;
		$batch_content .= "Fitness &nbsp;&nbsp;&nbsp;"   .$batch_user->db_batch_count_fit  . "<br>";
		$batch_content .= "General Health &nbsp;&nbsp;&nbsp;"   .$batch_user->db_batch_count_gha . "<br>" ;
		$batch_content .= "Well-being &nbsp;&nbsp;"  .$batch_user->db_batch_count_gwb . "<br>" ;
		$batch_content .= "Health Risk &nbsp;&nbsp;" .$batch_user->db_batch_count_hra . "<br>";
		$batch_content .= "---------------------<br />";
		$batch_content .= "Total &nbsp;&nbsp;&nbsp;"   .$batch_user->db_batch_count . "<br>";
		$batch_content .= "<br />&nbsp;<br /><br />&nbsp;<br />";
		$batch_content .= "Batch number - "   .$batch_user->db_batch_number . "<br>";
		$batch_content .= "Batch id - "   .$batch_user->db_id . "<br>";
		$batch_content .= "<br />&nbsp;<br />";
		$batch_content .=  "</td></tr>";
		$batch_content .=  "<tr><td></td></tr>";
		$batch_content .=  "<tr><td align=center class=HSbodytext colspan=3><a href='$print_batch'>Print assessments for this batch</a></td><tr>";
		$batch_content .=  "<tr><td>&nbsp;</td></tr><br>";
		$batch_content .=  "<tr><td align=center class=HSbodytext colspan=3><a href='$batch_print?list=1'>[ batch maintenance page ]</a></td></tr>";
		$batch_content .=  "</table></td></tr>";
		$batch_content .=  "<tr><td width=12 height=30>&nbsp;</td><td align=center valign=top height=30>&nbsp;</td></tr>";
		
					 
	    $c=$c+1;
		}
		$vars{batch_content} = $batch_content;
		my $template = $config->template_directory . "batch_content.tmpl";
	    print "template is $template<br>\n" if $Debug;
	    fill_and_send( $template, $batch_user, \%vars, $config->html_use_ssi );
	    exit;
     
	# print "In close routine\n" if $Debug;
	# if(!$input->param('db_id')){
		# print "No db_id routine\n" if $Debug;
	# if there is not a db_id, then we closed from an admin screen
	# (not actually during the batch process) so we have to lookup the details
		# my @batch_pieces = split(/ /, $input->param('db_batch_number'));
		# my @batch_pieces_1 = split(/-/,$batch_pieces[2]);		
		# $hash1{db_batch_number} = $batch_pieces[2];
		# $hash1{db_batch_entered_by} = $batch_pieces_1[0];
		# $batch_user = HealthStatus::User->new( \%hash1 );
		# print "In CLOSE - $hash1{db_batch_number}\n" if $Debug;

		# this gets the counts based on the batch number passed to us
		# my $status = get_counts($input->param('db_batch_number'), $batch_user, $config);
		# print "$status\n" if $Debug;
		# if(!$status){ error("batch not found - $hash1{db_batch_number} - can not restart");}

		# $batch_user->pretty_print if $Debug;
		# }
	# else	{
		# print "Exisiting db_id routine\n" if $Debug;
	#if you are here, you closed an active batch, so we don't need to look stuff up
		# $hash1{db_number} = '';
		# $hash1{db_email} = 'null@healthstatus.com';
		# $hash1{db_emailOK} = '0';
		# $hash1{hs_administration} = 'closed_batch';
		# $hash1{db_employer} = '';
		# $hash1{db_fullname} = 'batch - ' . $user->db_batch_number;
		# $hash1{db_id} = $input->param('db_id');

		# $batch_user = HealthStatus::User->new( \%hash1 );
		# }

	# $batch_user->pretty_print if $Debug;
	# my $temp_file_dir = $config->authenticate_dir;
	# my $temp_file = '10001';
	# my $approved1 = HealthStatus::Authenticate->new( $config, $temp_file_dir, $temp_file );
	# $batch_user->hs_administration('closed_batch');
	# $hash1{hs_administration} = 'closed_batch';
	# my $status1 = $approved1->change( $config, $batch_user );
	# print "Login change status = $status1\n" if $Debug;
	# my $template = $config->template_directory . "batch_report.tmpl";
	# print "template is $template<br>\n" if $Debug;
	# %vars = map { my $x = $_; $x =~ tr/A-Za-z_//c; $x, $input->param($_) }
		# $input->param;
	# $vars{config} = \%config;
	# fill_and_send( $template, $batch_user, \%vars, $config->html_use_ssi );
	# exit;
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
print "Assessment = $assessment\n" if $Debug;
error( "The assessment [$assessment] is not allowed" )
	unless exists $Allowed_assessments{$assessment};

my $max_pages = $Allowed_assessments{$assessment};
print "Max pages = $max_pages\n" if $Debug;

my $template = $config->template_directory . $assessment . "_qbatch.html";
print "template is $template<br>\n" if $Debug;

if($input->param('restart')){
print "in restart\n" if $Debug;
	# at this point all we have is the db_batch_number so we have to lookup
	# everything reset our counters then continue with the batch.
	my @batch_pieces = split(/ /, $input->param('restart'));
	my @batch_pieces_1 = split(/-/,$batch_pieces[2]);

	#
	$hash1{db_batch_number} = $batch_pieces[2];
	$hash1{db_batch_entered_by} = $batch_pieces_1[0];
	$batch_user = HealthStatus::User->new( \%hash1 );
        print "In RESTART - $hash1{db_batch_number}\n" if $Debug;

	# this gets the counts based on the batch number passed to us
	my $status = get_counts($input->param('restart'), $batch_user, $config);
	print "$status\n" if $Debug;
	if(!$status){ error("batch not found - $hash1{db_batch_number} - can not restart");}

	$batch_user->pretty_print if $Debug;
	# fill in the vars and show the template
	$vars{config} = \%config;
	$vars{page} = 1;

	foreach my $key ( $batch_user->attributes ) { $vars{$key} = $batch_user->get($key) }
}
elsif($user->db_batch_number lt $user->db_id){
carp "in elsif 1 ". $user->db_batch_number." - ".$user->db_id."\n";
# create a batch number if not already done, this users id, and a timestamp
# since this is the first time requesting the batch file, zero stuff out
	$user->db_batch_number( $user->db_id . "-" . $date_stamp);
	$user->db_batch_entered_by( $user->db_id );
	$user->db_batch_printdate( '');
	$user->db_batch_count( 0 );
	$user->db_batch_count_crc( 0 );
	$user->db_batch_count_drc( 0 );
	$user->db_batch_count_fit( 0 );
	$user->db_batch_count_gha( 0 );
	$user->db_batch_count_gwb( 0 );
	$user->db_batch_count_hra( 0 );
	$user->db_batch_count_mr( 0 );
	$user->db_batch_count_pt( 0 );

	foreach my $key ( $user->attributes ) { $hash1{$key} = $user->get($key) }

	$hash1{db_number} = '';
	$hash1{db_email} = 'null@healthstatus.com';
	$hash1{db_emailOK} = '0';
	$hash1{hs_administration} = 'batch';
	$hash1{db_employer} = '';
 	$hash1{db_fullname} = 'batch - ' . $user->db_batch_number;
 	$hash1{client2} = 'batch - ' . $user->db_batch_number;
	$hash1{db_id} = "b" . $tight_date;

	my $batch_user = HealthStatus::User->new( \%hash1 );

	my $temp_file_dir = $config->authenticate_dir;
	my $temp_file = '10001';
	my $approved1 = HealthStatus::Authenticate->new( $config, $temp_file_dir, $temp_file );
	my $status1 = $approved1->add( $config, $batch_user );

	print "\n** batch user **\n" if $Debug;
	$batch_user->pretty_print if $Debug;

	# set the variable for the next template
	# pass along all of the data in hidden fields
	%vars = map { my $x = $_; $x =~ tr/A-Za-z_//c; $x, $input->param($_) }
		$input->param;
	$vars{config} = \%config;
	$vars{page} = 1;
	$vars{db_number} = $batch_user->db_number;
	$vars{db_employer} = '';
	$vars{siteid} = '';
 	$vars{db_fullname} = 'batch - ' . $user->db_batch_number;
 	$vars{client2} = 'batch - ' . $user->db_batch_number;
	foreach my $key ( $batch_user->attributes ) { $vars{$key} = $batch_user->get($key) }
	}
else	{
#############################################################################################################
# if we make it to here, this is not the first time through
print "in else\n" if $Debug;

	my $page=1;

	# no field checking in batch entry mode.  Javascript is used to check data entry.

	# create the batch_user and fill with form elements
	$batch_user = HealthStatus::User->new( \%hash1 );

	if($input->param('switch') != 1){
		#we are not just switching templates so increment and write stuff out.
        print "in switch not 1\n" if $Debug;

		#increment counters, save the record
		my $inc = $batch_user->db_batch_count;
		++$inc;
		$batch_user->db_batch_count( $inc );
		my $assess_inc = 'db_batch_count_' . $assessment;
		$inc = $batch_user->$assess_inc;
		++$inc;
		$batch_user->$assess_inc( $inc );

		print "\n** batch user **\n" if $Debug;
		$batch_user->pretty_print if $Debug;

		# save the user record
		my $db = HealthStatus::Database->new( $config );

		$db->debug_on( \*STDERR ) if $Debug;

		$db->save_users_assessment( $batch_user, uc($assessment) );

		$db->finish( );

		$db->disconnect( );
		}

	# fill in the vars and show the template
	$vars{config} = \%config;
	$vars{page} = $page;
    $vars{completed_page} = 1;
	
	# change this up to only save needed inputs
	my @keep_these = qw(db_id siteid db_batch_number db_batch_entered_by db_batch_printdate db_batch_count db_batch_count_crc
			     db_batch_count_drc db_batch_count_fit db_batch_count_gha db_batch_count_gwb db_batch_count_hra
			     db_batch_count_mr db_batch_count_pt assessment hs_ident db_number db_employer db_merge_status);
	foreach (@keep_these){
		$vars{$_} = $batch_user->get($_) ;
	}
	my @ignore_tables = split /\s+/, $config->ignore_tables;
	my @user_elements;
	my $db = HealthStatus::Database->new( $config );
    foreach my $table (@ignore_tables){
      my @user_element = $db->get_user_elements(uc($table) );
	  push @user_elements,@user_element;
      
    }  
    $db->disconnect( );	
    my %maped_array = map {$_=>1} @keep_these;				 
    @ignore = grep { !$maped_array{$_} } @user_elements;

	# @ignore = qw( sex weight height race first_name last_name client1 smoke_status birth_month birth_date birth_year
			# frame_size diabetes bp_meds bp_sys bp_dias cholesterol hdl bp_check cholesterol_check cigars_day pipes_day
			# chews_day smoke_status cigarette_years_quit cigs_a_day miles_car miles_motorcycle travel_mode seat_belt
			# speed drink_and_drive drinks_week menarche_female birth_age_female mammogram_female fam_breast_cancer
			# pap_female hyst_female self_breast_exam clinic_breast_exam rectal_female rectal_male violence overall_health
			# exercise exercise_unable helmet fiber fat life_satisfaction loss grade job stressed stress_cope pregnant_female
			# mental_health family_heart_attack family_diabetes heart_attack general_exam days_missed depressed db_relation
			# gdm big_kid height feet inch parents_have_diabetes siblings_have_diabetes);
	}
	foreach (@ignore){
		$vars{$_}="";$batch_user->$_('');}


fill_and_send( $template, $batch_user, \%vars, $config->html_use_ssi, \@ignore );
exit;

# login
sub login_local
	{

	my ($config, $hash_ref) = @_;

        error( "The configuration object is bad after passing it to login." ) unless ref $config eq 'HealthStatus::Config';

	require HealthStatus::Authenticate;

	my %hash = %$hash_ref;

	my $user = HealthStatus::User->new( \%hash );

	my $temp_file_name = $config->authenticate_dir;
	my $temp_file = $input->cookie('hs_ident') || $input->param('hs_ident') || '10001';

	$user->db_number ( $input->cookie('hs_ident') );

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
# get the number of assessments in all the tables
sub get_counts
	{
	my ($db_batch_number, $batch_user, $config) = @_;
	if ($Debug) {
		print "** In get_counts\n$db_batch_number, $batch_user, $config\n";
		$batch_user->pretty_print;
		$config->pretty_print;
	}
	my $db = HealthStatus::Database->new( $config );
	$db->debug_on( \*STDERR ) if $Debug;

	return FALSE if(!$db_batch_number);

	my $found = $db->_lookup_user( $batch_user, $config, "where full_name='$db_batch_number'" );

	return FALSE if(!$found);

	my $temp_id = $batch_user->db_id;
	my @assessments = @{$$config{batch_assessments}};
	my %assessment_check;
	foreach (@assessments) {
		$assessment_check{uc $_} = 1;
		}
	if($assessment_check{CRC}){
		$batch_user->db_batch_count_crc($db->hs_count('CRC',"where hs_uid='$temp_id'"));
		$batch_user->db_batch_count( $batch_user->db_batch_count + $batch_user->db_batch_count_crc );
		}
	if($assessment_check{DRC}){
		$batch_user->db_batch_count_drc($db->hs_count('DRC',"where hs_uid='$temp_id'"));
		$batch_user->db_batch_count( $batch_user->db_batch_count + $batch_user->db_batch_count_drc);
		}
	if($assessment_check{FIT}){
		$batch_user->db_batch_count_fit($db->hs_count('FIT',"where hs_uid='$temp_id'"));
		$batch_user->db_batch_count( $batch_user->db_batch_count + $batch_user->db_batch_count_fit);
		}
	if($assessment_check{GHA}){
		$batch_user->db_batch_count_gha($db->hs_count('GHA',"where hs_uid='$temp_id'"));
		$batch_user->db_batch_count( $batch_user->db_batch_count + $batch_user->db_batch_count_gha);
		}
	if($assessment_check{GWB}){
		$batch_user->db_batch_count_gwb($db->hs_count('GWB',"where hs_uid='$temp_id'"));
		$batch_user->db_batch_count( $batch_user->db_batch_count +  $batch_user->db_batch_count_gwb);
		}
	if($assessment_check{HRA}){
		$batch_user->db_batch_count_hra($db->hs_count('HRA',"where hs_uid='$temp_id'"));
		$batch_user->db_batch_count( $batch_user->db_batch_count + $batch_user->db_batch_count_hra);
		}
	$batch_user->pretty_print if $Debug;
	$db->finish( );
	$db->disconnect( );
	return TRUE;
	}


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

Copyright 2001-2006, HealthStatus.com

=cut

1;