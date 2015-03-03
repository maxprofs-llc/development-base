#!/usr/local/bin/perl

#use strict;

=head1 NAME

new_ggr.cgi Report Setup

=cut

# Make sure the local path is in the include directory (mainly for NT installations)
use File::Basename        qw( dirname );
use File::Spec::Functions qw( rel2abs );

#use lib dirname(rel2abs($0)),'.','c:/strawberry/healthstatus/cgi-bin/hs/pdf', 'c:/strawberry/healthstatus/cgi-bin/hs';
use lib dirname(rel2abs($0)),'.', '/usr/local/www/vhosts/managed2/modules/pdf', '/usr/local/www/vhosts/managed2/modules';


use vars qw( $Debug $production  %ggr_global_group_lists $cook $config_file %Tables %Fields);

if (!do('common.inc')) {
   my $error = $@ ? $@
             : $! ? $!
             : 'did not return a true value';
   die("Unable to load common stuff: $error\n");
}

############################################################################
### Change the following line before going into production      ############
$production = 0;
#### 1 = production server, 0 = setup/test server               ############
############################################################################

use CGI qw(-no_xhtml -debug);
if (!$production) {
	use CGI::Carp qw(fatalsToBrowser);
	}

# Removing warnings in log while module is being used with CGI version 4 or above
$CGI::LIST_CONTEXT_WARN = 0;	
$CGI::POST_MAX=1024 * 100;  # max 100K posts
$CGI::DISABLE_UPLOADS = 1;  # no uploads
use IO::File;
use Date::Calc qw(:all);
use Text::Template;
use HTML::FillInForm;
use Time::localtime;
use perlchartdir;
use File::Copy;
use ConfigReader::Simple;
use PDF;
use Archive::Zip qw( :ERROR_CODES :CONSTANTS );

use HealthStatus qw( fill_and_send error html_error );
use HealthStatus::CalcRisk;
use HealthStatus::Config;
use HealthStatus::Constants;
use HealthStatus::Database;
use HealthStatus::Report;
use HealthStatus::User;
use HealthStatus::Authenticate;
use XML::Simple;

perlchartdir::setLicenseCode("VFQNX8F6MPBDJJCF68F9D2BE");

BEGIN { require "ggr_graph2.pl"; }

use vars qw(%vars %Defaults %assessment_names_short);

my ($db, $curr_day, $curr_year, $curr_month);
my ( %PARMS , %GROUP, %CONFIG,  %COMPPARMS);
my (@pgroup_list, @sgroup_list, @stip_conditions, $stipulation, $stipulations, $stipulations1, $pgroup_select_string, $sgroup_select_string, $html_string);
my (@user_id, $user_id_ref, $user_list_ref,  %user_list, @hidden_fields_array);
my ($to_be_done, $cnt, $hra_cnt, $ggr_adv_page_dir);

my $input = new CGI();
my $config = getConfig($input->param('extracfg'));

my $session = new CGI::Session(undef,$input,{Directory=>"../../sessions"}) or die CGI::Session->errstr;
$cook = $session->param('hs_ident') || $input->cookie('hs_ident') || $input->param('hs_ident');
if(!$input->param('rpt_type') && !$input->param('view')) {
	$session->clear();
	$session->param('hs_ident',$cook);
	}
else 	{
	$session->save_param();
	$session->clear(['page','prev.x','prev.y','next.x','next.y', 'next', 'prev', 'status']);
	$session->param('hs_ident',$cook);
	$session->load_param($input);
	}
#}elsif($input->param('Submit') eq 'Next step') {
#	@hidden_fields_array =("rpt_format","date","comp_date","s_month","s_day","s_year","e_month","e_day","e_year","s_month1","s_day1","s_year1","e_month1","e_day1","e_year1","date_range","all_assessment","records","max_records","max");
#}elsif($input->param('query') eq 'Submit_query_pdf' || $input->param('query') eq 'Submit_query_ind') {
#	@hidden_fields_array =("field_groups","pdf_template","daily","twelve_month","comp_s_month","comp_s_day","comp_s_year","comp_e_month","comp_e_day","comp_e_year","comp_date_range","breakout_sex","breakout_age","comparitive","pgraphs","print_totalassessments","print_agegroups","print_risklevels","print_achievable","print_preventable","print_riskfactors","print_cardiac","print_diabetes","print_fitness","print_wellbeing","print_alcohol","print_bloodpressure","print_cholesterol","print_exercise","print_mammogram","print_pap","print_prostate","print_seatbelts","print_smoking","print_wellbeing2","print_srdisease","print_breast_self","print_srfam","print_weight","user_footer","save_rpt_parameter","rpt_parameter","rpt_email","email","print_empty_graphs","print_page_numbers","print_glucose","print_triglycerides","print_ldl","print_days_missed","print_colon_exam","print_general_exam","print_hdl","comp_date");
#}

foreach my $name ( @hidden_fields_array )	{
	my $val = ($input->param($name)) ? $input->param($name) : '' ;
	$session->param($name, $val);
}

$session->flush();

my %hash = map { $_, $input->param($_) } $input->param();

$hash{cookie}= $input->cookie( -name => $session->name, -value => $session->id );
$hash{$session->name} = $session->id;

my %config = map { $_, $config->$_ } $config->directives;

$hash{config} = \%config;


my %input = $input->Vars();
##############################
#	foreach (sort keys %input){
#	carp  $_ .' - '. $input{$_}.'<br>';}
#	carp 'Session: '.$session->id().'<br>';
##################################

############################################################################
### Comment out the following line before going into production ############
$Debug = $input->param("HS_Debug") || $ENV{HS_DEBUG} || 0;
#### only uncomment if you need to debug the input scripts      ############
############################################################################



if ($input->param('report_config') || $config->ggr_adv_conf){
	my $report_cfg = $input->param('report_config') ;
	$config->add_config_file( $report_cfg );
	}

if ($Debug) {
	print "Content-type: text/plain\n\n";
	print "$ENV{SCRIPT_NAME} - $ENV{QUERY_STRING}\n";
	print "Modules Versions:\nHealthStatus - $HealthStatus::VERSION\nHealthStatus::Authenticate - $HealthStatus::Authenticate::VERSION\nHealthStatus::Database - $HealthStatus::Database::VERSION\n";
	print "HealthStatus::Config - $HealthStatus::Config::VERSION\nHealthStatus::User - $HealthStatus::User::VERSION\nHealthStatus::Constants - $HealthStatus::Constants::VERSION\nHealthStatus::HRA - $HealthStatus::HRA::VERSION\n\n";
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

my $user = authenticateUser(["admin"], $input, $config) or die "You should never see this message.";
my $user_rank = $user->hs_administration;

# this section checks to see if there are multiple admins for one database.  If there are we create values of
# which groups they can see based on the admins $user object values, a master value can be set to override everything.
if($config->ggr_adv_multi_admin){
	my @sname = split /\s+/, $config->ggr_adv_multi_admin_key;
	my @svalue = split /\s+/, $config->ggr_adv_multi_admin_value;
	my @smaster = split /\s+/, $config->ggr_adv_multi_admin_master;
	my $cnt=0;
	carp "$cnt\n@sname\n@svalue\n@smaster\n";
	while ($cnt <= scalar(@sname) && $smaster[$cnt] ne $user->{$svalue[$cnt]}){
		$input->param(-name=> $sname[$cnt] . '_selectgroup', -value=> $user->{$svalue[$cnt]});
#		$input->param(-name=> $sname[$cnt] . '_selection', -value=> 1);
		$cnt++;
		}
	}

my $format = lc($input->param('rpt_format')) || 'pdf';

print "$format\n" if $Debug;

my $wd_time = Date_to_Time(Today_and_Now());
my $shortfile_name = $input->param('file_name') || $wd_time . "_ggr_output";
$wd_time .=  '/';
my $no_ext_shortfile_name = $shortfile_name;
$shortfile_name .= '.' . $format ;
my $output_file_name = $config->ggr_adv_page_dir . $shortfile_name  ;

# View the different output files in the browser.
if ($input->param('view'))
	{
	my $bin_set = 0;
	my $type;
	if($format eq 'pdf')
		{
		$type='application/pdf';
		}
	if($format eq 'xls')
		{
		$type='application/vnd.ms-excel';
		}
	if($format eq 'zip')
		{
		$type='application/x-zip-compressed';
		}
	if($format eq 'xml')
		{
		$type='text/xml';
		}
	if($format eq 'csv')
		{
		$type='text/plain';
		}
	my $f = new IO::File "$output_file_name", "r" or die "$output_file_name: $!\n";
	my $file = do { local $/; binmode $f; <$f> };

	print $input->header(-type=>$type, -attachment =>$shortfile_name ), $file;
	exit;
	}
if ($input->param('save_rpt_parameter') && $input->param('process'))
	{
	my ($hour,$min,$sec) = Now();
	my $rpt_cfg = $config->ggr_adv_page_dir . 'saved_reports/report_' . $hour . $min . $sec . '.conf';
	my $rpt_config = ConfigReader::Simple->new($rpt_cfg);
	$rpt_config->set('human_desc', $input->param('rpt_parameter'));
        my %hash = $input->Vars;
        my $alist = $input->{'assessment_list'};
        $alist =~ s/\\0/ /g;
        foreach (keys %hash)
        	{
        	next if ($_ eq 'assessment_list');
        	$rpt_config->set($_, $input->param($_));
        	}
        $rpt_config->save( $rpt_cfg );
    }
if ($input->param('use_saved'))
	{
	my $rpt_cfg = $config->ggr_adv_page_dir . 'saved_reports/' . $input->param('use_saved') ;
	my $rpt_config = ConfigReader::Simple->new($rpt_cfg);
	error( "Could not find configuration file $rpt_cfg" ) unless ref $rpt_config;
	my @rpt_list = $rpt_config->directives();
	foreach (@rpt_list)
		{
        	next if ($_ eq 'assessment_list');
		$input->param(-name=>$_, -value=>$rpt_config->get($_));
		}
	# load the values from the config file so it looks like it came from the form
	my @alist = split /\s+/, $rpt_config->get('assessment_list');
	$input->param(-name=>'assessment_list', -values=> \@alist);
	$format = lc($input->param('rpt_format')) || 'pdf';
	}
my $GGR_PDF = $config->template_directory . $config->ggr_adv_pdf_template;
$ENV{TEMP} = $config->ggr_adv_page_dir;
$ggr_adv_page_dir = $config->ggr_adv_page_dir;
my $blank_data = $config->fixed_images . $config->ggr_adv_blank_image;

my %assessment_names = ( HRA	=> 'General Health assesments ',
			 OHA    => 'Health and Brain Trauma',
			 GHA	=> 'Health Risk assesments (original)',
			 CRC	=> 'Cardiac Risk assesments',
			 DRC	=> 'Diabetes Risk assesments',
			 FIT	=> 'Fitness assesments',
			 GWB	=> 'General Well Being assesments');
%assessment_names_short = ( HRA	=> 'General Health ',
			 OHA    => 'Health and Brain Trauma',
			 GHA	=> 'Health Risk',
			 CRC	=> 'Cardiac',
			 DRC	=> 'Diabetes',
			 FIT	=> 'Fitness',
			 GWB	=> 'Well-Being');

my @assessments_allowed = split /\s+/, $config->ggr_adv_tables;
my %assessments_allowed_hash;
my %assessments_used_hash;
foreach (@assessments_allowed){
	$assessments_allowed_hash{$_} = $assessment_names_short{$_};
	}

my @list_of_assessments =();
my @list_of_assessments_named = ();

if (uc($input->param('all_assessment')) eq 'ALL' || !$input->param('assessment_list')){
	@list_of_assessments = @assessments_allowed ;
	foreach (@list_of_assessments){ 
		push @list_of_assessments_named, $assessment_names_short{$_}; 
		$assessments_used_hash{uc($_)} = $assessment_names_short{uc($_)};
		}
	}
else	{
	my @list_values = $input->param('assessment_list');
	foreach (@list_values){
		push @list_of_assessments, uc($_) ;
		push @list_of_assessments_named, $assessment_names_short{uc($_)};
		$assessments_used_hash{uc($_)} = $assessment_names_short{uc($_)};
		}
	}

my $assessments_ref = \@list_of_assessments;

my %quarters_hash = (
		1 => {
			beg_mon => '01',
			beg_day => '01',
			end_mon => '03',
			end_day => 31,
			prev => 4,
			desc => "1st Quarter",
			},
		2 => {
			beg_mon => '04',
			beg_day => '01',
			end_mon => '06',
			end_day => 31,
			prev => 1,
			desc => "2nd Quarter",
			},
		3 => {
			beg_mon => '07',
			beg_day => '01',
			end_mon => '09',
			end_day => 31,
			prev => 2,
			desc => "3rd Quarter",
			},
		4 => {
			beg_mon => 10,
			beg_day => '01',
			end_mon => 12,
			end_day => 31,
			prev => 3,
			desc => "4th Quarter",
			}  );

my @parm_list = ( 'm_lt_19','f_lt_19','m_19_29','f_19_29','m_30_39','f_30_39','m_40_49','f_40_49','m_50_59','f_50_59','m_60','f_60',
'sm_still','sm_never','sm_quit','males','females','wt_under','wt_good','wt_over','wt_obese','sb_never','sb_seldom','sb_some','sb_usually','sb_always','sb_speed','sb_drinkdrive',
'chol_high','chol_med','chol_low','chol_unknown','bp_high','bp_med','bp_low','bp_unknown','bp_no_meds','bp_meds','alc_high','alc_medium','alc_low','alc_drinks','exer_none','exer_some','exer_good',
'pap_good','pap_med','pap_bad','self_breast_good','self_breast_med','self_breast_bad','high','high_cnt','medium','medium_cnt','low','ach_high_cnt','ach_high','ach_medium_cnt','ach_medium','ach_moderate',
'ach_moderate_cnt','ach_low','user_count','mammo_good',' mammo_bad','mammo_med', 'GLUCOSE_high', 'GLUCOSE_med', 'GLUCOSE_low', 'GLUCOSE_unknown', 'LDL_high', 'LDL_med', 'LDL_low',  'LDL_unknown', 'TRI_above500', 'TRI_200_499', 'TRI_150_199', 'TRI_below150', 'TRI_unknown', 'days_missed_none', 'days_missed_1to5', 'days_missed_6to10', 'days_missed_10plus', 'days_missed_not_apply', 'colonoscopy_good', 'colonoscopy_med', 'colonoscopy_bad', 'gen_exam_under2', 'gen_exam_2to5', 'gen_exam_5plus', 'gen_exam_never');

foreach (@parm_list){
	$PARMS{$_} = 0;
}

foreach my $tkeys(@list_of_assessments){
	$PARMS{'users_back'}{$_}=0;
	$PARMS{'assessment'}{$_}=0;
	$PARMS{$tkeys. "_cnt"}=0;
	$PARMS{"$tkeys"}=0;
}

%COMPPARMS = %PARMS if ($input->param('comparitive') == 1);
$PARMS{"comparative"}=2 if ($input->param('comparitive') == 1);


my $db = HealthStatus::Database->new( $config );

$db->debug_on( \*STDERR ) if ($Debug);

if( lc($config->db_driver) eq 'oracle' )
{
	my $APrev = "ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY-MM-DD HH24:MI:SS'";
	$db->execute_sql($APrev);
}

# process the records from the data passed.
if($input->param('process')){
	$| = 1;
	my @ggr_javas='';
	my @ggr_styles='';
	
	my @ggr_java_parts = split /\s+/, $config->ggr_adv_java;
	foreach (@ggr_java_parts){
		my %t = { -type=> "text/javascript", -src=> $config->ggr_adv_java_dir.$_ };
	    	push @ggr_javas, { -type=> "text/javascript", -src=> $config->ggr_adv_java_dir.$_ };
		}
	my @ggr_style_parts = split /\s+/, $config->ggr_adv_styles;
	foreach (@ggr_style_parts){
	    	push @ggr_styles, { -src=> $config->ggr_adv_styles_dir.$_ };
		}


	my $rpt = HealthStatus::Report->new( {output=> uc($format), debug=> 0, config=> $config_file } );
    my $rpt_logo = $config->html_base.$config->brand_logo || $config->html_base.$config->admin_logo ;
	my $view_logo = qq|<p class="maintext-n"><img src="$rpt_logo" border="0" align="center"><br /></p>|;
	carp "rpt logo:::::$rpt_logo";
	my $rpt_types = 'Participation' if $input->param('rpt_type') eq 'participation';
	$rpt_types = 'Individual' if $input->param('rpt_type') eq 'indv_data';
	$rpt_types = 'Aggregate' if $input->param('rpt_type') eq 'agrgt_data';
	my $mybatchlookup = 0;
	if ($config->does_batch) { $mybatchlookup = 1; }
	my $unique = 1;
	if ( lc($input->param('records')) eq 'all' )  { $unique = 0; }

	print $input->header(-type=>'text/html');
	print $input->start_html(-title=>'Advanced Graphic Group Report Processor',
		    -author=>'gwhite@healthstatus.com',
		    -script=> \@ggr_javas,
		    -style=> \@ggr_styles );
	print $view_logo;		
	print '<p class="maintext-n"><span  class="maintext-b">'.$rpt_types. ' report being generated as a ' . $format . ' file.</span></p>';
	print '<p class="maintext-n">Getting the user list and ' . lc($input->param('records')) . ' records<br>' if(lc($input->param('process')) ne 'accounting');
	print '<p class="maintext-n">Starting the counts<br>' if(lc($input->param('process')) eq 'accounting');

	my $max_to_process;
	if($input->param('max_records') eq 'max' && $input->param('max')) {
		$max_to_process = $input->param('max');
	}

	my $temp_id = $config->db_id;
	$temp_id = uc($temp_id) if( lc($config->db_driver) eq 'oracle' );

	my @month = qw{ x jan feb mar apr may jun jul aug sep oct nov dec };

	($curr_year, $curr_month, $curr_day) = Today();

	my ($date_stipulations, $participation_date)  = &date_queries($input,$order_key,$temp_id);
	my ($comp_date_stipulations, $comp_participation_date) = &date_queries($input,$order_key,$temp_id,'comp_') if ($input->param('comparitive') == 1);
	$input->param(-name=>"ggr_sql_date", -value=>"$date_stipulations");
	$input->param(-name=>"comp_ggr_sql_date", -value=>"$comp_date_stipulations") if ($input->param('comparitive') == 1);

# select users, and then get all their assessments that meet the input criteria
	if ($input->param('ggr_sql') || $input->param('ggr_sql_date') && lc($input->param('rpt_type')) ne 'accounting')
	{
		$stipulation = $input->param('ggr_sql');
		print "filtering";		
        print " - $stipulation ";
		print " - limit to first $max_to_process" if $max_to_process > 0;
		print "<br>";
		if( $config->authenticate_method eq 'hs' || $config->authenticate_method eq 'client'){
			@user_id  =  $db->reg_group_list( $temp_id, $stipulation );
			@comp_user_id  =  $db->reg_group_list( $temp_id, $stipulation );
			}
		else	{
			@user_id  =  $db->assessment_group_list( $temp_id, $assessments_ref, $stipulation );
			@comp_user_id  =  $db->assessment_group_list( $temp_id, $assessments_ref, $stipulation );
			}
		my $use_cnt = scalar(@user_id);
		my $comp_use_cnt = scalar(@comp_user_id);
		$use_cnt = 0 if $use_cnt < 1;
		print "<br>$use_cnt potential user records or batches were found in this group.<br>";
		print "$comp_use_cnt potential comparitive records or batches were found in this group.<br>" if($input->param('comparitive') == 1);
		print "Finding assessments that meet the restriction criteria for these users and batches.<br>";

		$user_id_ref = \@user_id;
		$comp_user_id_ref = \@comp_user_id;
		push @stip_array, $input->param('ggr_sql_date');
		push @stip_array, $input->param('ggr_sql');
		$stipulation1 = $input->param('ggr_sql_date');
		$comp_stipulation = $input->param('comp_ggr_sql_date');
#$db->debug_on( \*STDERR );
		$user_list_ref  =  $db->get_users_details( $config, \@list_of_assessments, $user_id_ref, $stipulation1, $unique, 0 );
#$db->debug_off();
		$comp_user_list_ref  =  $db->get_users_details( $config, \@list_of_assessments, $comp_user_id_ref, $comp_stipulation, $unique, 0 ) if ($input->param('comparitive') == 1);
		print "Details retrieved.<br>";
	}
	elsif ( lc($input->param('rpt_type')) ne 'accounting' )
	{
		print "using all groups";
		print " - limit to first $max_to_process" if $max_to_process > 0;
		print "<br>";

		@user_id = $db->reg_group_list($temp_id);

		my $use_cnt = scalar(@user_id);
		$use_cnt = 0 if $use_cnt < 1;
		print "<br>$use_cnt potential user records or batches were found in this group.<br>Finding assessments that meet the restriction criteria for these users and batches.<br>";

		$user_id_ref = \@user_id;
		$user_list_ref  =  $db->get_users_details( $config, \@list_of_assessments, $user_id_ref, '', $unique, $mybatchlookup );
		print "Details retrieved.<br>";
	}

	%user_list = %{$user_list_ref};
	my $ul_cnt=keys %user_list;
	print "UL count = $ul_cnt<br>";

#	print "Comparitive input = ".$input->param('comparitive');

	%comp_user_list = %{$comp_user_list_ref} if($input->param('comparitive') == 1);
	$to_be_done = $user_list{'count_results'};
	$comp_to_be_done = $comp_user_list{'count_results'};
	$to_be_done = $input->param('max') if ($input->param('max') && $input->param('max') < $to_be_done);
	$comp_to_be_done = $input->param('max') if ($input->param('max') && $input->param('max') < $comp_to_be_done);

	if($to_be_done < 1 && ($input->param('ggr_sql') || $input->param('ggr_sql_date')) && lc($input->param('rpt_type')) ne 'accounting'){
		print qq|<p class="maintext-err">I am sorry, but we do not have enough data to continue with this report. Only $to_be_done records were available.|;
		print "Change your selection for a larger group. " if $stipulation;
		print "</p>";
		print '<p class="maintext-b">[ <a href="' . $ggr1 . '">run another group report</a> ]';
		my $member = $config->member_page || $config->cgi_dir . '/assessment_recs.cgi';
		print '<p class="maintext-b">[ <a href="' . $member . '">assessment records page</a> ]';
		exit;
	}

	my $rt =  lc($input->param('rpt_type'));
	my $rn =  lc($input->param('field_groups')) || 'hs';
	my $dcs = $input->param('date_condition_str');
	my %settings=(
			max_to_process=> $to_be_done,
			report_type=> $rt,
			report_format => uc($format),
			report_name => $rn,
			file_name => $output_file_name,
			pdf_template => $input->param('pdf_template'),
			work_dir => $wd_time,
			date_restrict => $dcs,
			participation_date => $participation_date,
			comp_participation_date => $comp_participation_date,
			comp_date_restrict => $input->param('comp_ggr_sql_date'),
			daily =>  $input->param('daily'),
			twelve_month =>  $input->param('twelve_month'),
			all_records =>  $input->param('records'),
			stipulation => $input->param('ggr_sql'),
			anonymous => 0,
			);


	print 'Have the list, ' . $to_be_done . ' assessments that might qualify, processing begins. ';
	print $comp_to_be_done.' assessments that might qualify for comparison were found. ' if($input->param('comparitive') == 1);
	print '</p><p class="maintext-n">';
	if($input->param('ggr2_batch')){
		open (TT,">>".$config->conf_data_dir."/healthstatus.log");
		my $selection = $input->param('site_selection');
		$selection =~ s/\///;
		print TT $input->param('ggr2_batch').','.$settings{file_name};
		print TT "\n";
		close TT;
		open FILE, ">>".$config->conf_data_dir.'/saved_reports/'.$selection.'.log ' or die "cannot write into file";
		print FILE $settings{file_name};
		print FILE "\n";
		close FILE;
		}

	my %temp_user_list = %user_list;
	my %comp_temp_user_list = %comp_user_list;
	my %temp_parms = %PARMS;
	my %temp_group = %GROUP;
	my %temp_settings = %settings;
# go out and process the records, if individual data, we save the data in this routine
# if aggregate we set the counters, if accounting we just count all kinds of stuff
	if ( lc($input->param('rpt_type')) eq 'accounting' )
		{
		print 'Calling accounting functions<br> ';
		$rpt->accounting($config_file, \%user_list, \%PARMS, \%GROUP, $assessments_ref, \$cnt, \%settings, $Debug );
		$PARMS{'cnt'} = $cnt;
		$hra_cnt = $PARMS{HRA_cnt} + $PARMS{GHA_cnt};
		my @assessment_count;
		my $max_value = 0;        
		( lc($input->param('rpt_type')) eq 'indv_data' && $format eq 'pdf' )?(&ggr_report($wd_time)):(&ggr_report($no_ext_shortfile_name));
		}
	elsif ( lc($input->param('rpt_type')) eq 'participation' )
		{
		print 'Calling accounting functions<br> ';
		$rpt->participation($config_file, \%user_list, \%PARMS, \%GROUP, $assessments_ref, \$cnt, \%settings, $Debug );
		$PARMS{'cnt'} = $cnt;
		$hra_cnt = $PARMS{HRA_cnt} + $PARMS{GHA_cnt};
		my @assessment_count;
		my $max_value = 0;        
		( lc($input->param('rpt_type')) eq 'indv_data' && $format eq 'pdf' )?(&ggr_report($wd_time)):(&ggr_report($no_ext_shortfile_name));
		}
	else	{ 
		print '<br>Setting data counters <br> ';
		if($input->param('comparitive') == 1)
		{
			print 'This is a Comparitive Report<br>';
#			print $output_file_name."<BR> $stipulation1<br>$comp_stipulation<br>";
			$hash{participation_date} = $participation_date;
			$PARMS{file_name} = $output_file_name;
#			foreach (sort keys %input){ print $_." - ".$input{$_}."<BR>"; }
#			foreach (sort keys %settings){ print $_." - ".$settings{$_}."<BR>"; }
			$rpt->set_counters($config_file, \%user_list, \%PARMS, \%GROUP, $assessments_ref, \$cnt, \%settings, $Debug );
			print 'Current data compiled<br>Starting to work on comparitive data<br>';
#			foreach (sort keys %PARMS){ print $_." - ".$PARMS{$_}."<BR>"; }
			$PARMS{'cnt'} = $cnt;
			$hra_cnt = $PARMS{HRA_cnt} + $PARMS{GHA_cnt};
#			my $h_ref = prepare_hashes_arg_pdf(\%hash, $config->ggr_adv_page_dir, $assessments_ref, \@assessment_count, \%PARMS, \%GROUP, $hra_cnt );
#			%COMP_OUTPUT_DATA = %{$h_ref};
			my @assessment_count;
			my $max_value = 0;
			$settings{file_name} = 'comp_'.$output_file_name;
			$settings{max_to_process} = $comp_to_be_done;
			$settings{participation_date} = $comp_participation_date;
			$hash{comp_participation_date} = $comp_participation_date;
#			$settings{date_restrict} = $input->param('comp_ggr_sql_date');
			$settings{date_restrict} = $dcs;
			$rpt->set_counters($config_file, \%comp_user_list, \%COMPPARMS, \%COMPGROUP, $assessments_ref, \$compcnt, \%settings, $Debug );
			print 'Comparitive data compiled<br>';
			$COMPPARMS{'cnt'} = $compcnt;
			$PARMS{comparitive} = 2;
#			foreach (sort keys %COMPPARMS){ print $_." - ".$COMPPARMS{$_}."<BR>"; }
#			my $h_ref = prepare_hashes_arg_pdf(\%hash, $config->ggr_adv_page_dir, $assessments_ref, \@assessment_count, \%PARMS, \%GROUP, $hra_cnt );

			#%COMP_OUTPUT_DATA = %{$h_ref};
			$comp_hra_cnt = $COMPPARMS{HRA_cnt} + $COMPPARMS{GHA_cnt};
			my @assessment_count;
			my $max_value = 0;
#			print 'Comparitive Counters Set<br>';            
			( lc($input->param('rpt_type')) eq 'indv_data' && $format eq 'pdf' )?(&ggr_report($wd_time)):(&ggr_report($no_ext_shortfile_name));
			exit;
		}
		else
		{
			$rpt->set_counters($config_file, \%user_list, \%PARMS, \%GROUP, $assessments_ref, \$cnt, \%settings, $Debug );
			$PARMS{'cnt'} = $cnt;
			$hra_cnt = $PARMS{HRA_cnt} + $PARMS{GHA_cnt};
			my @assessment_count;
			my $max_value = 0;

            carp "line 594::$wd_time::::$no_ext_shortfile_name";
			( lc($input->param('rpt_type')) eq 'indv_data' && $format eq 'pdf' )?(&ggr_report($wd_time)):(&ggr_report($no_ext_shortfile_name));

		}
		print "<br><br>Data counters are set,<br>";
	}

# process the aggregate report, make graphs if that is what they want, make the other formats if they want that.
	( lc($input->param('rpt_type')) eq 'indv_data' )?(carp("$input->param('rpt_type')\n")):(carp("$input->param('rpt_type')\n"));

#	carp($input->param('ggr2_batch')."-".%user_list."\n");
	if(($input->param('breakout_sex') == 1))
	{
		$breakout_sex{Male}{sex_restriction} =  " Personal_Sex='Male'";
		$breakout_sex{Male}{sex} =  "male";
		$breakout_sex{Male}{file_name} = $config->ggr_adv_page_dir .$male_name;
		$breakout_sex{Female}{sex_restriction} =  " Personal_Sex='Female'";
		$breakout_sex{Female}{sex} =  "female";
		$breakout_sex{Female}{file_name} = $config->ggr_adv_page_dir .$female_name;

		my $random_time = Date_to_Time(Today_and_Now());
		foreach my $use_sex (keys %breakout_sex)
		{
			 %PARMS = ();
			%user_list = %temp_user_list;
			%PARMS = %temp_parms;
			%GROUP = %temp_group;
			%settings = %temp_settings;
			$cnt = 0;

			$output_file_name = $breakout_sex{$use_sex}{file_name};
			$settings{file_name}   = $breakout_sex{$use_sex}{file_name};
			$settings{sex_restriction} = $breakout_sex{$use_sex}{sex_restriction};
			print $use_sex.'-'.$settings{file_name}.'-'.$settings{file_name}."-visu \n";
			$rpt->set_counters($config_file, \%user_list, \%PARMS, \%GROUP, $assessments_ref, \$cnt, \%settings, $Debug );
			$PARMS{'cnt'} = $cnt;
			$hra_cnt = $PARMS{HRA_cnt} + $PARMS{GHA_cnt};
			@assessment_count=();
			$max_value = 0;
			( lc($input->param('rpt_type')) eq 'indv_data' && (($format eq 'pdf') || ($format eq 'xls' ) || ($format eq 'xml' ) ) )?(&ggr_report($wd_time,'_'.$breakout_sex{$use_sex}{sex})):(&ggr_report($breakout_sex{$use_sex}{sex}.'_'.$no_ext_shortfile_name));
		}
	}
	if($input->param('breakout_age') == 1)
	{
		my @sql = ("  ($year - bYear) <= 19 and ($month >= bmonth) ", "  (($year - bYear) >= 20)  and (($year - bYear) <= 29) and ($month >= bmonth) ","  (($year - bYear) >= 30) and (($year - bYear) <= 39) and ($month >= bmonth) ","  (($year - bYear) >= 40) and (($year - bYear) <= 49 ) and ($month >= bmonth)  ","  (($year - bYear) >= 50) and (($year - bYear) <= 59) and ($month >= bmonth) ","  (($year - bYear) >= 60) and ($month >= bmonth) ");
		my @age_filenames = ('19_','20_29_','30_39_','40_49_','50_59_','60_');
		for(my $i=0;$i <=($#sql);$i++)
		{
			%PARMS = ();
			%PARMS = %temp_parms;
			%GROUP = %temp_group;
			%settings = %temp_settings;
			$cnt = 0;
			$output_file_name = $config->ggr_adv_page_dir.$age_filenames[$i].$shortfile_name;
			$settings{file_name}   = $config->ggr_adv_page_dir.$age_filenames[$i].$shortfile_name;
			$settings{sex_restriction} = $sql[$i];

			$rpt->set_counters($config_file, \%user_list, \%PARMS, \%GROUP, $assessments_ref, \$cnt, \%settings, $Debug );
			$PARMS{'cnt'} = $cnt;
			$hra_cnt = $PARMS{HRA_cnt} + $PARMS{GHA_cnt};
			@assessment_count=();
			$max_value = 0;
			( lc($input->param('rpt_type')) eq 'indv_data' && (($format eq 'pdf') || ($format eq 'xls' )|| ($format eq 'xml' )))?(&ggr_report($wd_time,'_'.$age_filenames[$i])):(&ggr_report($age_filenames[$i].$no_ext_shortfile_name));

		}
	}
	# free up some memory
	#undef (%{$user_list_ref});
	#undef (%user_list);
	#print $input->end_html;
	exit;
}

# read the inputs from various forms to create the SQL
# we don't rely on a specific form for input, so you can change the look and feel of the front-end.
@stip_conditions = ('WHERE ');
my $debug_string;
my $accounting_ok = 1;
my ($pgroup_count, $sgroup_count);

# specified which userdata fields will be used to select the data out
my @group_db_list = split / /,$config->ggr_adv_group_list_db;
my @group_friendly_list = split /,/,$config->ggr_adv_group_list_friendly;

# list of outputs for which user data fields will be printed
my %defined_reports_list;
my @rpt_list;
my @rpt_friendly_list;

if(lc($input->param('rpt_type')) eq 'participation'){
	@rpt_list = split / /,$config->ggr_adv_rpt_participation_db;
	@rpt_friendly_list = split /,/,$config->ggr_adv_rpt_participation_friendly;
	}
else	{
	@rpt_list = split / /,$config->ggr_adv_rpt_list_db;
	@rpt_friendly_list = split /,/,$config->ggr_adv_rpt_list_friendly;
	}


# list of outputs for which user data fields will be printed
my %defined_ind_pdf_list;
my @pdf_temp_list = split / /,$config->ggr_adv_indv_pdf_temps;
my @pdf_temp_friendly_list = split /,/,$config->ggr_adv_indv_pdf_temps_friendly;
my $t_cnt=0;
foreach my $temp_group (@pdf_temp_list)
	{
	$defined_ind_pdf_list{$temp_group} = $pdf_temp_friendly_list[$t_cnt];
	++$t_cnt;
	}

my $hidden_inputs;
my @lv = $input->param('assessment_list');
foreach (@lv){
	$hidden_inputs .= qq|\n<input type=hidden name="assessment_list" value="$_">|;
	}

my $t_cnt=0;
my $restrict_cnt = 0;
foreach my $db_group (@group_db_list)
	{
	my $tname = $db_group . '_selection';
	my $pname = $input->param($tname);
	my $tgroup = $db_group . '_selectgroup';
	my $pgroup = $input->param($tgroup);
	carp 'ggr_adv  - ' . $tname . ' - ' . $pname . ' - ' . $tgroup . ' - ' . $pgroup;
	if ($pname  ne '')
		{ carp "if pname:::";
		$hidden_inputs .= qq|<input type=hidden name="$tname" value="$pname">|;
		$accounting_ok = 0;
		my $connector = '=';
		my $close = "'";
		$_ = $pname;
		my $temp_id = $db_group;
		$temp_id = uc ($db_group) if( lc($config->db_driver) eq 'oracle' );
		if(/\/$/){
			$connector = ' LIKE ';
			$close = q|%'|; # '
			}
		push (@stip_conditions, $temp_id . $connector . " '" . $pname . $close);
		carp "stip_conditions11:::@stip_conditions";
		}
	else
		{
		my $restrict_name = 'ggr_adv_group_' . $db_group . '_restriction';
		my $restriction;
		if($config->{$restrict_name}){
			$restriction = $config->$restrict_name; }
		elsif($pgroup) {
			$hidden_inputs .= qq|<input type=hidden name="$tgroup" value="$pgroup">|;
			$accounting_ok = 0;
			my $connector = '=';
			my $close = "'";
			$_ = $pgroup;
			my $temp_id = $db_group;
			$temp_id = uc ($db_group) if( lc($config->db_driver) eq 'oracle' );
#			if(/\/$/){
				$connector = ' LIKE ';
				$close = q|%'|; # '
#				}
			$restriction = 'where ' . $temp_id . $connector . " '" . $pgroup . $close;
			$restrict_cnt++;
			push (@stip_conditions, $temp_id . $connector . " '" . $pgroup . $close);
			}
		my @pgroup_list;
		if( $config->authenticate_method eq 'hs' || $config->authenticate_method eq 'client'){
			@pgroup_list  =  $db->reg_group_list( $db_group, $restriction . ' ORDER by ' . $db_group ) ;
			}
		else	{
			@pgroup_list  =  $db->assessment_group_list( $db_group, \@assessments_allowed, $restriction . ' ORDER by ' . $db_group ) ;
			}
        carp "stip_conditions:::@stip_conditions";
		$ggr_global_group_lists{$db_group}{list} = \@pgroup_list;

		$ggr_global_group_lists{$db_group}{count} = scalar(@pgroup_list);

		$ggr_global_group_lists{$db_group}{human} = $group_friendly_list[$t_cnt];
		++$t_cnt;

		my @parsed_list;

		foreach my $group ( @{$ggr_global_group_lists{$db_group}{list}} )
			{
			$_ = $group;
			if(!/\// || $restrict_cnt)
				{
				push @parsed_list, $group;
				}
			else 	{
				my @split_list = split /\//;
				my $split_count = @split_list;
				my $scnt=0;
				while ( $scnt < ($split_count - 1) ){	$split_list[$scnt] .= '/'; ++$scnt; }
				$scnt= 1 ;
				while ( $scnt < $split_count )
					{
					$split_list[$scnt] = $split_list[$scnt-1] . $split_list[$scnt];
					push @split_list , $split_list[$scnt]  if ($scnt < ($split_count - 1) );
					++$scnt;
					}
				my %in_list = ();
				foreach my $item ( @parsed_list ) { $in_list{$item}=1; }
				foreach my $split_item ( @split_list )
					{
					next if $split_item eq 'qualcare';
					#if($split_item !~ m/\/$/){ $split_item .= '/'; }
					unless ($in_list{$split_item}){
						push @parsed_list, $split_item;
						$in_list{$split_item}=1;
						}
					}
				}
			}

		$ggr_global_group_lists{$db_group}{select_string} = qq|<option value="" selected>All</option>|;
		if($config->exists(ggr_group_db_process) && $config->ggr_group_db_process){
			foreach my $val (@parsed_list) {
				next if(!$val);
				if (!do($config->db_config_file))
				{
					my $error = $@ ? $@ : $! ? $!: 'did not return a true value';
					die("Unable to load common stuff: $error\n");
				}
				#my $field = $config->group_name;
				#my $stipulations = 'where '.$config->group_index. "='".$val."'";
				my $val_modify = $val;
				$val_modify =~ s/^\///;
				my $field = 'groupName';
				my $stipulations = "where groupID='".$val_modify."'";
				#carp $stipulations;

				@query_results  =  $db->select_one_column_distinct ( $field, $Tables{GRP}, $stipulations);
				$ggr_global_group_lists{$db_group}{select_string} .= qq|<option value="$val">$query_results[0]</option>| if $val_modify ne '';
				}

			}

		else	{
			foreach (@parsed_list) { $ggr_global_group_lists{$db_group}{select_string} .= qq|<option value="$_">$_</option>| if $_ ne ''; }
			}

			$db->finish;
		}
	}

my $t_cnt=0;
foreach my $rpt_group (@rpt_list)
	{
	$defined_reports_list{$rpt_group} = $rpt_friendly_list[$t_cnt];
#	carp "rpt_group - $rpt_group\n";
	++$t_cnt;
	}

my $order_key;
if ( lc($input->param('records')) eq "oldest" ||  lc($input->param('records')) eq "all" )  { $order_key = 'DESC'; }	else { $order_key = 'ASC'; }

my $temp_id = $config->db_id;
$temp_id = uc ($temp_id) if( lc($config->db_driver) eq 'oracle' );

my %report_type = (
	agrgt_data => 'n Aggregate data',
	indv_data => 'n Individual data',
	participation => ' Participation ',
	accounting => 'n Accounting' );

$html_string = "Creating a" . $report_type{$input->param('rpt_type')} . ' report, with output in ' .  $input->param('rpt_format') . ' format. <br>';

if( scalar(@stip_conditions) > 1)
{
	my $j=0;
	foreach ( @stip_conditions )
	{
		++$j;
		$stipulations .= " AND " if $j > 2;
		$stipulations .= "$_";
	}

	$input->param(-name=>"ggr_sql", -value=>"$stipulations");

	$html_string .=  qq|<br>All users $stipulations will be processed. |;
	$hidden_inputs .= qq|\n<input type=hidden name="ggr_sql" value="$stipulations">|;
}
else
{
	$html_string .=  qq|<br>All users will be processed. |;
}

my $date_line;
my $comp_date_line;
my %vars1 = map { my $x = $_; $x =~ tr/A-Za-z_//c; $x, $input->param($_) }
		$input->param;

if ($input->param('date') eq 'date_range') {
	$date_line = $input->param('date_range');
	$date_line =~ s/_/ /g;
	}
elsif($input->param('date') eq 'specific1')
{
	my ($year,$month,$day) = Today();
	$vars1{'e_month'} = sprintf("%02d",$month);
	$input->param(-name=>'e_month',-value=> $vars1{'e_month'});
	$vars1{'e_day'} = sprintf("%02d",$day);
	$input->param(-name=>'e_day',-value=> $vars1{'e_day'});
	$vars1{'e_year'} = $year;
	$input->param(-name=>'e_year',-value=> $vars1{'e_year'});
	$vars1{'s_month'} = $input->param('s_month1');
	$input->param(-name=>'s_month',-value=> $vars1{'s_month'});
	$vars1{'s_day'} = $input->param('s_day1');
	$input->param(-name=>'s_day',-value=> $vars1{'s_day'});
	$vars1{'s_year'} = $input->param('s_year1');
	$input->param(-name=>'s_year',-value=> $vars1{'s_year'});
	$date_line = 'between ' . $input->param('s_month') . "-" . $input->param('s_day') . "-" . $input->param('s_year')  . ' and ' .$input->param('e_month').'-'.$input->param('e_day').'-'.$input->param('e_year') ;
	$vars1{'date'} = 'specific';
	$input->param(-name=>'date',-value=>'specific');

}
elsif($input->param('date') eq 'specific2'){
	$vars1{'s_month'} = '01';
	$vars1{'s_day'} = '01';
	$vars1{'s_year'} = '1998';
	$vars1{'e_month'} = $input->param('e_month1');
	$vars1{'e_day'} = $input->param('e_day1');
	$vars1{'e_year'} = $input->param('e_year1');
	$input->param(-name=>'s_month',-value=> $vars1{'s_month'});
	$input->param(-name=>'s_day',-value=> $vars1{'s_day'});
	$input->param(-name=>'s_year',-value=> $vars1{'s_year'});
	$input->param(-name=>'e_month',-value=> $vars1{'e_month'});
	$input->param(-name=>'e_day',-value=> $vars1{'e_day'});
	$input->param(-name=>'e_year',-value=> $vars1{'e_year'});
	$date_line = 'between ' . $input->param('s_month') . "-" . $input->param('s_day') . "-" . $input->param('s_year')  . ' and ' .$input->param('e_month').'-'.$input->param('e_day').'-'.$input->param('e_year') ;
	$vars1{'date'} = 'specific';
	}
elsif($input->param('date') eq 'specific'){
	$date_line = 'between ' . $input->param('s_month') . "-" . $input->param('s_day') . "-" . $input->param('s_year')  . ' and ' .$input->param('e_month') . "-" . $input->param('e_day') . "-" . $input->param('e_year') ;
	}
else	{
	$date_line = 'anytime' ;
	}
if($input->param('comparitive') == 1)
	{
	if ($input->param('comp_date') eq 'comp_date_range')
		{
		$comp_date_line = $input->param('comp_date_range');
		$comp_date_line =~ s/_/ /g;
		}
	elsif($input->param('comp_date') eq 'specific')
		{
		$comp_date_line = 'between ' . $input->param('comp_s_month') . "-" . $input->param('comp_s_day') . "-" . $input->param('comp_s_year')  . ' and ' .$input->param('comp_e_month') . "-" . $input->param('comp_e_day') . "-" . $input->param('comp_e_year') ;
		}
	else
		{
		$comp_date_line = 'anytime' ;
		}

	}
$html_string .=  "<br>Assessments for " . commify(@list_of_assessments_named) . " taken $date_line will be processed ";
$html_string .=  "<br>and compared to Assessments for " . commify(@list_of_assessments_named) . " taken $comp_date_line will be processed " if($input->param('comparitive') == 1);
$html_string .= "limited to " . $input->param('max') . " assessment records" if ($input->param('max'));

my $user_footer = $input->param('user_footer');

$html_string .=  qq|<p>Footer on each page will be: $user_footer<br>&nbsp;<br>| if ($user_footer gt '');
$html_string .=  "<\p>";

##############################
#	foreach (sort keys %input){
#	$html_string .=  $_ .' - '. $input{$_}.'<br>';}
#	$html_string .=  'Session: '.$session->name.' - '.$session->id().'<br>';
##################################
my %vars1 = map { my $x = $_; $x =~ tr/A-Za-z_//c; $x, $input->param($_) }
		$input->param;
$vars1{accounting_ok} = $accounting_ok;
$vars1{html_string} = $html_string;
$vars1{hidden_values} = $hidden_inputs;
$vars1{assessments_allowed} = \%assessments_allowed_hash;
$vars1{ggr_global_group_lists} = \%ggr_global_group_lists;
$vars1{defined_reports_list} = \%defined_reports_list;
$vars1{defined_templates_list} = \%defined_ind_pdf_list;
$vars1{ggr_no_accounting} = $config->ggr_no_accounting || 0;
$vars1{ggr_no_participation} = $config->ggr_no_participation || 0;
$vars1{ggr_hipaa} = $config->ggr_hipaa || 0;
$vars1{hs_administration} = $user_rank;

my @ignore_array = ('assessment_list');

# Find all the conf files in the ggr directory and list them as saved reports.
chdir ($config->ggr_adv_page_dir . 'saved_reports/');
my @saved_reports = glob ('*.conf');

my %saved_reports_list;
foreach my $rpt_cfg(@saved_reports){
	my $rpt_config = ConfigReader::Simple->new($rpt_cfg);
	error( "Could not find configuration file $rpt_cfg" ) unless ref $rpt_config;
	my $hd = $rpt_config->get( 'human_desc' );
	$saved_reports_list{$rpt_cfg} = $hd;
	}

my %config = map { $_, $config->$_ } $config->directives;
$vars1{config} = \%config;
$vars1{saved_reports_list} = \%saved_reports_list;
$vars1{saved_reports_array} = \@saved_reports;

$user->add(\%vars1);

if($input->param('query') eq 'Submit_query_pdf' || $input->param('query') eq 'Submit_query_ind') {
	fill_and_send( $config->template_directory . $config->ggr_adv_check_template , $user, \%vars1, $config->html_use_ssi, \@ignore_array );
	exit;
}
#my @query_results = $db->select_all('hs_category',' where 1 ',1);
#$vars1{category_list} = \@query_results;
if ( ($input->param('rpt_type') eq 'agrgt_data') && (($input->param('rpt_format') eq 'PDF') || ($input->param('rpt_format') eq 'XLS') || ($input->param('rpt_format') eq 'XML') ) ) {
	fill_and_send( $config->template_directory . $config->ggr_adv_query_pdf_template, $user, \%vars1, $config->html_use_ssi, \@ignore_array );
}elsif ( ($input->param('rpt_type') eq 'indv_data') && (($input->param('rpt_format') eq 'XLS') || ($input->param('rpt_format') eq 'XML') || ($input->param('rpt_format') eq 'CSV') || ($input->param('rpt_format') eq 'PDF') ) ) {
	fill_and_send( $config->template_directory . $config->ggr_adv_query_xml_xls_cvs_template, $user, \%vars1, $config->html_use_ssi, \@ignore_array );
}elsif ( ($input->param('rpt_type') eq 'participation') && (($input->param('rpt_format') eq 'XLS') || ($input->param('rpt_format') eq 'XML') || ($input->param('rpt_format') eq 'CSV') ) ) {
	fill_and_send( $config->template_directory . $config->ggr_adv_query_xml_xls_cvs_template, $user, \%vars1, $config->html_use_ssi, \@ignore_array );
}elsif ( ($input->param('rpt_type') eq 'accounting') && ($input->param('rpt_format') eq 'XLS')  ) {
	fill_and_send( $config->template_directory . $config->ggr_adv_query_accounting_template, $user, \%vars1, $config->html_use_ssi, \@ignore_array );
}else{
	$vars1{error} = 'Something is incorrect, make sure the report format is appropriate for the report type and the date type is selected.';
	fill_and_send( $config->template_directory . $config->ggr_adv_input_template, $user, \%vars1, $config->html_use_ssi, \@ignore_array);
	my $dir_path = $config->ggr_adv_page_dir;
	opendir(DELE, $dir_path) or die "Could not open directory $dir_path ";
	my @TODELETE = readdir(DELE);
	#PUT LOOP HERE
	foreach my $file (@TODELETE) {
		my $file_path = $dir_path.$file;
		if (-d $file) {next;}
		my ($file_name, $ext) = split('\.',$file);
		if ((-M $file_path) > 4 && $ext eq 'png') {
			unlink($file_path);
		}
	}
	#END LOOP HERE
	closedir(DELE);
}
exit;

#########
# commify and and a series
sub commify {
	my $sepchar = grep(/,/ => @_) ? ";" : ",";
	(@_ == 0) ? "":
	(@_ == 1) ? $_[0]:
	(@_ == 2) ? join (" and ", @_):
				join ("$sepchar ", @_[0 .. ($#_-1)], "and $_[-1]");
}

sub send_email_attachment
	{
        my $self = shift;
        my $config = shift;
        my $format = shift;
        my $email_to = shift;
        my $file = shift;

	use Mail::Sendmail;
        use MIME::QuotedPrint;
	use MIME::Base64;

        return unless ref $user eq 'HealthStatus::User';

	my($directory, $filename) = $file =~ m/(.*\/)(.*)$/;

	my $subject = "Your group health assessment results.";
	my $from = $config->email_from;
	my $smtp = $config->email_smtp;
	my %mail = ( 	To      => $email_to,
			From    => $from,
			Subject => $subject,
			smtp 	=> $smtp
		   );

	my $boundary = "====" . time() . "====";
	$mail{'content-type'} = "multipart/mixed; boundary=\"$boundary\"";

	my $message = encode_qp( "Your group health assessment results." );

	open (F, $file) or die "Cannot read $file: $!";
	binmode F; undef $/;
	$mail{body} = encode_base64(<F>);
	close F;

	$boundary = '--'.$boundary;
	$mail{body} = <<END_OF_BODY;
$boundary
Content-Type: text/plain; charset="iso-8859-1"
Content-Transfer-Encoding: quoted-printable

$message
$boundary
Content-Type: application/octet-stream; name="$filename"
Content-Transfer-Encoding: base64
Content-Disposition: attachment; filename="$filename"

$mail{body}
$boundary--
END_OF_BODY

	sendmail(%mail) || print "Error: $Mail::Sendmail::error\n";

	carp("Couldn't send email: $Mail::Sendmail::error")
		if $MAIL::Sendmail::error;

	return TRUE;
	}
sub hash_remove_key_space
{	my $in_hash = shift;
	my %work_hash = %$in_hash;
	my %output_hash;

	foreach my $ckey(keys %work_hash){
		my $value;
		if (ref($work_hash{$ckey}) eq "HASH")
			{
			$value = hash_remove_key_space($work_hash{$ckey});
			}
		else	{
			$value = $work_hash{$ckey};
			}
		my $temp = $ckey;
		$temp =~ s|\s||isg;
		$temp =~ s|%||isg;
		$temp =~ s|(120/80)|BP-good|isg;
		$temp =~ s|(140/90)|BP-high|isg;
		$temp =~ s|,|_|isg;
		$temp =~ s|(200to240)|CHOL_200to240|isg;
		$temp =~ s|(1-2/week)|exercise-OneorTwo|isg;
		$temp =~ s|(3\+/week)|exercise-3weeks|isg;
		$temp =~ s|(1-5days)|OnetoFiveDays|isg;
		$temp =~ s|(10daysormore)|TenDaysOrMore|isg;
		$temp =~ s|(6-10days)|SixToTenDays|isg;
		$temp =~ s|(2to5years)|TwoToFiveDays|isg;
		$temp =~ s|(2yearsorless)|TwoYearsOrLess|isg;		
		$temp =~ s|(1fifty-199)|Onefifty-199|isg;
		$temp =~ s|(1to3years)|OnetoThree|isg;
		$temp =~ s|(1yearorless)|Oneyearorless|isg;
		#$temp =~ s|(GroupMammogram\(females40andolder\))|GroupMammogram-females40andolder|isg;
		#$temp =~ s|(GroupMammogram\(females40andolder\))|GroupMammogram-females40andolder|isg;
		$temp =~ s|\(|-|;
		$temp =~ s|\)||;
		$temp =~ s|/|-|;
		$temp =~ s|(1-40)|one-forty|isg;
		$temp =~ s|(41-80)|fortyone-eighty|isg;
		$temp =~ s|(81-99)|eigtyone-ninetynine|isg;
		$temp =~ s|20|twenty|;
		$temp =~ s|30|thirty|;
		$temp =~ s|40|forty|;
		$temp =~ s|50|fifty|;
		$temp =~ s|60\+|sixtyplus|;
		$temp =~ s|(1thirty)|OneThirty|isg;
		$temp =~ s|(1fifty)|Onefifty|isg;
		$temp =~ s|(1sixty)|OneSixty|isg;
		$output_hash{$temp} = $value;
		}

	return \%output_hash;
}
sub ggr_report
{
	my $file_name = shift;
	if ( lc($input->param('rpt_type')) eq 'agrgt_data' ||  lc($input->param('rpt_type')) eq 'indv_data' )
		{
		@assessment_count=();
		foreach (@list_of_assessments)
			{
			my $t = $_ . '_cnt';
			#print "$assessment_names{$_} = $PARMS{$t}<br>";
			push (@assessment_count, $PARMS{$t});
			}
		print '<p class="maintext-n">preparing data for output<br>';
		my $graph_cnt = 0;
		print '<br>' . uc($format) . ' prep<br>';
		carp "line 1163::$wd_time::::$output_file_name";
		$PARMS{file_name} = $output_file_name;
		$PARMS{files_prefix} = $wd_time;

		if (( $format eq 'xls' )&&($input->param('comparitive') != 1))
			{
			my $h_ref = prepare_hashes_arg_pdf(\%hash, $config->ggr_adv_page_dir, $assessments_ref, \@assessment_count, \%PARMS, \%GROUP, $hra_cnt );
			my %OUTPUT_DATA = %{$h_ref};
			print '<br>' . uc($format) . ' processing<br>';
			}
		elsif(( $format eq 'xls' )&&($input->param('comparitive') == 1))
		{
				print '<br>' . uc($format) . ' processing<br>';
		}
		elsif ( $format eq 'xml' )
			{
				use XML::Simple;
				my $h_ref = prepare_hashes_arg_pdf(\%hash, $ggr_adv_page_dir, $assessments_ref, \@assessment_count, \%PARMS, \%GROUP, $hra_cnt );
	#			my %OUTPUT_DATA = %{$h_ref};
				my %temp_output_data = %{hash_remove_key_space($h_ref)};
	#			foreach my $key (keys(%OUTPUT_DATA))
	#			{
	#				if (ref($OUTPUT_DATA{$key}) eq "HASH")
	#					{
	# 						my %temphash = %{$OUTPUT_DATA{$key}};
	# 						print %{$temphash};
	# 					}
	#				my $temp = $key;
	#				$temp =~ s|\s||isg;
	#
	#				foreach my $key1 (keys(%{$OUTPUT_DATA{$key}}))
	#				{
	#					my $temp1 = $key1;
	#					$temp1 =~ s|\s||isg;
	#					$temp_output_data{$temp}{$temp1} = $OUTPUT_DATA{$key}{$key1};
	#					print $OUTPUT_DATA{$key}{$key1}."visu <BR>";
	#					if (ref($OUTPUT_DATA{$key}{$key1}) eq "HASH")
	#					{
	# 						my $temphash = %{$OUTPUT_DATA{$key}{$key1}};
	# 						print %{$temphash};
	# 					}
	#				}
	#				$temp_output_data{$temp} = $OUTPUT_DATA{$key};
	#
	#			}
				my %OUTPUT_DATA = ();
				%OUTPUT_DATA = %temp_output_data;
				my %temp_comp_output_data = %{hash_remove_key_space(\%COMP_OUTPUT_DATA)};
				%COMP_OUTPUT_DATA = {};
				%COMP_OUTPUT_DATA = %temp_comp_output_data;
				print '<br>XML format<br>';
				my $xml = XMLout(\%OUTPUT_DATA, RootName => 'hs_data', NoAttr => 1);
				my $comp_xml = XMLout(\%COMP_OUTPUT_DATA, RootName => 'comp_hs_data', NoAttr => 1);
				if($xml_work)	{
					open(XML, ">>$output_file_name" ) or die "Failed xml open - $output_file_name\n$!";}
				else	{
					open(XML, ">$output_file_name" ) or die "Failed xml user - $output_file_name\n$!";}
				print "<br>XML writing<br>";
				if($input->param('comparitive')==1)
				{
				($achievable_group) = $xml=~ m|<AchievableGroupRisk>(.*?)</AchievableGroupRisk>|isg;
				($cardiac_group) = $xml=~ m|<CardiacAssessmentResults>(.*?)</CardiacAssessmentResults>|isg;
				($drink_group) = $xml=~ m|<DrinksinaWeek>(.*?)</DrinksinaWeek>|isg;
				($family_group) = $xml=~ m|<FamilyHistoryConditions>(.*?)</FamilyHistoryConditions>|isg;
				($fitness_group) = $xml=~ m|<FitnessAssessmentResults>(.*?)</FitnessAssessmentResults>|isg;
				($bp_group) = $xml=~ m|<GroupBloodPressure>(.*?)</GroupBloodPressure>|isg;
				($chol_group) = $xml=~ m|<GroupCholesterol>(.*?)</GroupCholesterol>|isg;
				($gcrf_group) = $xml=~ m|<GroupContributingRiskFactors>(.*?)</GroupContributingRiskFactors>|isg;
				($geb_group) = $xml=~ m|<GroupExerciseHabits>(.*?)</GroupExerciseHabits>|isg;
				($gmf_group) = $xml=~ m|<GroupMammogram-femalesfortyandolder>(.*?)</GroupMammogram-femalesfortyandolder>|isg;
				($gps_group) = $xml=~ m|<GroupPapSmear-allfemales>(.*?)</GroupPapSmear-allfemales>|isg;
				($gpe_group) = $xml=~ m|<GroupProstateExams-malesfortyandolder>(.*?)</GroupProstateExams-malesfortyandolder>|isg;
				($gsu_group) = $xml=~ m|<GroupSeatbeltUse>(.*?)</GroupSeatbeltUse>|isg;
				($gsh_group) = $xml=~ m|<GroupSmokingHabits>(.*?)</GroupSmokingHabits>|isg;
				($gw_group) = $xml=~ m|<GroupWeight>(.*?)</GroupWeight>|isg;
				($nat_group) = $xml=~ m|<NumberofAssessmentsTaken>(.*?)</NumberofAssessmentsTaken>|isg;
				($pc_group) = $xml=~ m|<PersonalConditions>(.*?)</PersonalConditions>|isg;
				($pdd_group) = $xml=~ m|<PreventableDeathsbyDisease>(.*?)</PreventableDeathsbyDisease>|isg;
				($sbe_group) = $xml=~ m|<SelfBreastExam-allfemales>(.*?)</SelfBreastExam-allfemales>|isg;
				($sbg_group) = $xml=~ m|<SexbyAgeGroup>(.*?)</SexbyAgeGroup>|isg;
				($sdr_group) = $xml=~ m|<StressandDepressionResultsfromGeneralHealthAssessment>(.*?)</StressandDepressionResultsfromGeneralHealthAssessment>|isg;
				($comp_achievable_group) = $comp_xml=~ m|<AchievableGroupRisk>(.*?)</AchievableGroupRisk>|isg;
				($comp_cardiac_group) = $comp_xml=~ m|<CardiacAssessmentResults>(.*?)</CardiacAssessmentResults>|isg;
				($comp_drink_group) = $comp_xml=~ m|<DrinksinaWeek>(.*?)</DrinksinaWeek>|isg;
				($comp_family_group) = $comp_xml=~ m|<FamilyHistoryConditions>(.*?)</FamilyHistoryConditions>|isg;
				($comp_fitness_group) = $comp_xml=~ m|<FitnessAssessmentResults>(.*?)</FitnessAssessmentResults>|isg;
				($comp_bp_group) = $comp_xml=~ m|<GroupBloodPressure>(.*?)</GroupBloodPressure>|isg;
				($comp_chol_group) = $comp_xml=~ m|<GroupCholesterol>(.*?)</GroupCholesterol>|isg;
				($comp_gcrf_group) = $comp_xml=~ m|<GroupContributingRiskFactors>(.*?)</GroupContributingRiskFactors>|isg;
				($comp_geb_group) = $comp_xml=~ m|<GroupExerciseHabits>(.*?)</GroupExerciseHabits>|isg;
				($comp_gmf_group) = $comp_xml=~ m|<GroupMammogram-femalesfortyandolder>(.*?)</GroupMammogram-femalesfortyandolder>|isg;
				($comp_gps_group) = $comp_xml=~ m|<GroupPapSmear-allfemales>(.*?)</GroupPapSmear-allfemales>|isg;
				($comp_gpe_group) = $comp_xml=~ m|<GroupProstateExams-malesfortyandolder>(.*?)</GroupProstateExams-malesfortyandolder>|isg;
				($comp_gsu_group) = $comp_xml=~ m|<GroupSeatbeltUse>(.*?)</GroupSeatbeltUse>|isg;
				($comp_gsh_group) = $comp_xml=~ m|<GroupSmokingHabits>(.*?)</GroupSmokingHabits>|isg;
				($comp_gw_group) = $comp_xml=~ m|<GroupWeight>(.*?)</GroupWeight>|isg;
				($comp_nat_group) = $comp_xml=~ m|<NumberofAssessmentsTaken>(.*?)</NumberofAssessmentsTaken>|isg;
				($comp_pc_group) = $comp_xml=~ m|<PersonalConditions>(.*?)</PersonalConditions>|isg;
				($comp_pdd_group) = $comp_xml=~ m|<PreventableDeathsbyDisease>(.*?)</PreventableDeathsbyDisease>|isg;
				($comp_sbe_group) = $comp_xml=~ m|<SelfBreastExam-allfemales>(.*?)</SelfBreastExam-allfemales>|isg;
				($comp_sbg_group) = $comp_xml=~ m|<SexbyAgeGroup>(.*?)</SexbyAgeGroup>|isg;
				($comp_sdr_group) = $comp_xml=~ m|<StressandDepressionResultsfromGeneralHealthAssessment>(.*?)</StressandDepressionResultsfromGeneralHealthAssessment>|isg;
				my $final_xml = "<ComparitiveReport>";
				$final_xml .= "\t<AchievableGroupRisk>"."\n";
				$final_xml .= "\t"."<group1>";
				$final_xml .= "\t"."<daterange_begin>";
				$final_xml .=  $input->param('s_month')."-".$input->param('s_day')."-".$input->param('s_year') if($input->param('date_range') eq '');
				$final_xml .= $input->param('date_range') if($input->param('date_range') ne '');
				$final_xml .= "</daterange_begin>";
				$final_xml .= "\t"."<daterange_end>";
				$final_xml .=  $input->param('e_month')."-".$input->param('e_day')."-".$input->param('e_year') if($input->param('comp_date_range') eq '');
				$final_xml .= "</daterange_end>";
				$final_xml .= $achievable_group;
				$final_xml .= "\t"."</group1>";
				$final_xml .= "\t"."<group2>";
				$final_xml .= "\t"."<daterange_begin>";
				$final_xml .=  $input->param('comp_s_month')."-".$input->param('comp_s_day')."-".$input->param('comp_s_year') if($input->param('comp_date_range') eq '');
				$final_xml .= $input->param('comp_date_range') if($input->param('comp_date_range') ne '');
				$final_xml .= "</daterange_begin>";
				$final_xml .= "\t"."<daterange_end>";
				$final_xml .=  $input->param('comp_e_month')."-".$input->param('comp_e_day')."-".$input->param('comp_e_year') if($input->param('comp_date_range') eq '');
				$final_xml .= "</daterange_end>";
				$final_xml .= $comp_achievable_group;
				$final_xml .= "\t"."</group2>";
				$final_xml .= "\t</AchievableGroupRisk>"."\n";
				$final_xml .= "\t<CardiacAssessmentResults>"."\n";
				$final_xml .= "\t"."<group1>";
				$final_xml .= "\t"."<daterange_begin>";
				$final_xml .=  $input->param('s_month')."-".$input->param('s_day')."-".$input->param('s_year') if($input->param('date_range') eq '');
				$final_xml .= $input->param('date_range') if($input->param('date_range') ne '');
				$final_xml .= "</daterange_begin>";
				$final_xml .= "\t"."<daterange_end>";
				$final_xml .=  $input->param('e_month')."-".$input->param('e_day')."-".$input->param('e_year') if($input->param('comp_date_range') eq '');
				$final_xml .= "</daterange_end>";
				$final_xml .= $cardiac_group;
				$final_xml .= "\t"."</group1>";
				$final_xml .= "\t"."<group2>";
				$final_xml .= "\t"."<daterange_begin>";
				$final_xml .=  $input->param('comp_s_month')."-".$input->param('comp_s_day')."-".$input->param('comp_s_year') if($input->param('comp_date_range') eq '');
				$final_xml .= $input->param('comp_date_range') if($input->param('comp_date_range') ne '');
				$final_xml .= "</daterange_begin>";
				$final_xml .= "\t"."<daterange_end>";
				$final_xml .=  $input->param('comp_e_month')."-".$input->param('comp_e_day')."-".$input->param('comp_e_year') if($input->param('comp_date_range') eq '');
				$final_xml .= "</daterange_end>";
				$final_xml .= $drink_group;
				$final_xml .= "\t"."</group2>";
				$final_xml .= "\t</CardiacAssessmentResults>"."\n";
				$final_xml .= "\t<DrinksinaWeek>"."\n";
				$final_xml .= "\t"."<group1>";
				$final_xml .= "\t"."<daterange_begin>";
				$final_xml .=  $input->param('s_month')."-".$input->param('s_day')."-".$input->param('s_year') if($input->param('date_range') eq '');
				$final_xml .= $input->param('date_range') if($input->param('date_range') ne '');
				$final_xml .= "</daterange_begin>";
				$final_xml .= "\t"."<daterange_end>";
				$final_xml .=  $input->param('e_month')."-".$input->param('e_day')."-".$input->param('e_year') if($input->param('comp_date_range') eq '');
				$final_xml .= "</daterange_end>";
				$final_xml .= $cardiac_group;
				$final_xml .= "\t"."</group1>";
				$final_xml .= "\t"."<group2>";
				$final_xml .= "\t"."<daterange_begin>";
				$final_xml .=  $input->param('comp_s_month')."-".$input->param('comp_s_day')."-".$input->param('comp_s_year') if($input->param('comp_date_range') eq '');
				$final_xml .= $input->param('comp_date_range') if($input->param('comp_date_range') ne '');
				$final_xml .= "</daterange_begin>";
				$final_xml .= "\t"."<daterange_end>";
				$final_xml .=  $input->param('comp_e_month')."-".$input->param('comp_e_day')."-".$input->param('comp_e_year') if($input->param('comp_date_range') eq '');
				$final_xml .= "</daterange_end>";
				$final_xml .= $comp_drink_group;
				$final_xml .= "\t"."</group2>";
				$final_xml .= "</DrinksinaWeek>"."\n";
				$final_xml .= "<FamilyHistoryConditions>"."\n";
				$final_xml .= "\t"."<group1>";
				$final_xml .= "\t"."<daterange_begin>";
				$final_xml .=  $input->param('s_month')."-".$input->param('s_day')."-".$input->param('s_year') if($input->param('date_range') eq '');
				$final_xml .= $input->param('date_range') if($input->param('date_range') ne '');
				$final_xml .= "</daterange_begin>";
				$final_xml .= "\t"."<daterange_end>";
				$final_xml .=  $input->param('e_month')."-".$input->param('e_day')."-".$input->param('e_year') if($input->param('comp_date_range') eq '');
				$final_xml .= "</daterange_end>";
				$final_xml .= $family_group;
				$final_xml .= "\t"."</group1>";
				$final_xml .= "\t"."<group2>";
				$final_xml .= "\t"."<daterange_begin>";
				$final_xml .=  $input->param('comp_s_month')."-".$input->param('comp_s_day')."-".$input->param('comp_s_year') if($input->param('comp_date_range') eq '');
				$final_xml .= $input->param('comp_date_range') if($input->param('comp_date_range') ne '');
				$final_xml .= "</daterange_begin>";
				$final_xml .= "\t"."<daterange_end>";
				$final_xml .=  $input->param('comp_e_month')."-".$input->param('comp_e_day')."-".$input->param('comp_e_year') if($input->param('comp_date_range') eq '');
				$final_xml .= "</daterange_end>";
				$final_xml .= $comp_family_group;
				$final_xml .= "\t"."</group2>";
				$final_xml .= "\t</FamilyHistoryConditions>"."\n";
				$final_xml .= "\t<FitnessAssessmentResults>"."\n";
				$final_xml .= "\t"."<group1>";
				$final_xml .= "\t"."<daterange_begin>";
				$final_xml .=  $input->param('s_month')."-".$input->param('s_day')."-".$input->param('s_year') if($input->param('date_range') eq '');
				$final_xml .= $input->param('date_range') if($input->param('date_range') ne '');
				$final_xml .= "</daterange_begin>";
				$final_xml .= "\t"."<daterange_end>";
				$final_xml .=  $input->param('e_month')."-".$input->param('e_day')."-".$input->param('e_year') if($input->param('comp_date_range') eq '');
				$final_xml .= "</daterange_end>";
				$final_xml .= $fitness_group;
				$final_xml .= "\t"."</group1>";
				$final_xml .= "\t"."<group2>";
				$final_xml .= "\t"."<daterange_begin>";
				$final_xml .=  $input->param('comp_s_month')."-".$input->param('comp_s_day')."-".$input->param('comp_s_year') if($input->param('comp_date_range') eq '');
				$final_xml .= $input->param('comp_date_range') if($input->param('comp_date_range') ne '');
				$final_xml .= "</daterange_begin>";
				$final_xml .= "\t"."<daterange_end>";
				$final_xml .=  $input->param('comp_e_month')."-".$input->param('comp_e_day')."-".$input->param('comp_e_year') if($input->param('comp_date_range') eq '');
				$final_xml .= "</daterange_end>";
				$final_xml .= $comp_fitness_group;
				$final_xml .= "\t"."</group2>";
				$final_xml .= "\t</FitnessAssessmentResults>"."\n";
				$final_xml .= "\t<GroupBloodPressure>"."\n";
				$final_xml .= "\t"."<group1>";
				$final_xml .= "\t"."<daterange_begin>";
				$final_xml .=  $input->param('s_month')."-".$input->param('s_day')."-".$input->param('s_year') if($input->param('date_range') eq '');
				$final_xml .= $input->param('date_range') if($input->param('date_range') ne '');
				$final_xml .= "</daterange_begin>";
				$final_xml .= "\t"."<daterange_end>";
				$final_xml .=  $input->param('e_month')."-".$input->param('e_day')."-".$input->param('e_year') if($input->param('comp_date_range') eq '');
				$final_xml .= "</daterange_end>";
				$final_xml .= $fitness_group;
				$final_xml .= "\t"."</group1>";
				$final_xml .= "\t"."<group2>";
				$final_xml .= "\t"."<daterange_begin>";
				$final_xml .=  $input->param('comp_s_month')."-".$input->param('comp_s_day')."-".$input->param('comp_s_year') if($input->param('comp_date_range') eq '');
				$final_xml .= $input->param('comp_date_range') if($input->param('comp_date_range') ne '');
				$final_xml .= "</daterange_begin>";
				$final_xml .= "\t"."<daterange_end>";
				$final_xml .=  $input->param('comp_e_month')."-".$input->param('comp_e_day')."-".$input->param('comp_e_year') if($input->param('comp_date_range') eq '');
				$final_xml .= "</daterange_end>";
				$final_xml .= $comp_fitness_group;
				$final_xml .= "\t"."</group2>";
				$final_xml .= "\t</GroupBloodPressure>"."\n";
				$final_xml .= "\t<GroupCholesterol>"."\n";
				$final_xml .= "\t"."<group1>";
				$final_xml .= "\t"."<daterange_begin>";
				$final_xml .=  $input->param('s_month')."-".$input->param('s_day')."-".$input->param('s_year') if($input->param('date_range') eq '');
				$final_xml .= $input->param('date_range') if($input->param('date_range') ne '');
				$final_xml .= "</daterange_begin>";
				$final_xml .= "\t"."<daterange_end>";
				$final_xml .=  $input->param('e_month')."-".$input->param('e_day')."-".$input->param('e_year') if($input->param('date_range') eq '');
				$final_xml .= "</daterange_end>";
				$final_xml .= $fitness_group;
				$final_xml .= "\t"."</group1>";
				$final_xml .= "\t"."<group2>";
				$final_xml .= "\t"."<daterange_begin>";
				$final_xml .=  $input->param('comp_s_month')."-".$input->param('comp_s_day')."-".$input->param('comp_s_year') if($input->param('comp_date_range') eq '');
				$final_xml .= $input->param('comp_date_range') if($input->param('comp_date_range') ne '');
				$final_xml .= "</daterange_begin>";
				$final_xml .= "\t"."<daterange_end>";
				$final_xml .=  $input->param('comp_e_month')."-".$input->param('comp_e_day')."-".$input->param('comp_e_year') if($input->param('comp_date_range') eq '');
				$final_xml .= "</daterange_end>";
				$final_xml .= $comp_fitness_group;
				$final_xml .= "\t"."</group2>";
				$final_xml .= "\t</GroupCholesterol>"."\n";
				$final_xml .= "\t<GroupContributingRiskFactors>"."\n";
				$final_xml .= "\t"."<group1>";
				$final_xml .= "\t"."<daterange_begin>";
				$final_xml .=  $input->param('s_month')."-".$input->param('s_day')."-".$input->param('s_year') if($input->param('date_range') eq '');
				$final_xml .= $input->param('date_range') if($input->param('date_range') ne '');
				$final_xml .= "</daterange_begin>";
				$final_xml .= "\t"."<daterange_end>";
				$final_xml .=  $input->param('e_month')."-".$input->param('e_day')."-".$input->param('e_year') if($input->param('date_range') eq '');
				$final_xml .= "</daterange_end>";
				$final_xml .= $gcrf_group;
				$final_xml .= "\t"."</group1>";
				$final_xml .= "\t"."<group2>";
				$final_xml .= "\t"."<daterange_begin>";
				$final_xml .=  $input->param('comp_s_month')."-".$input->param('comp_s_day')."-".$input->param('comp_s_year') if($input->param('comp_date_range') eq '');
				$final_xml .= $input->param('comp_date_range') if($input->param('comp_date_range') ne '');
				$final_xml .= "</daterange_begin>";
				$final_xml .= "\t"."<daterange_end>";
				$final_xml .=  $input->param('comp_e_month')."-".$input->param('comp_e_day')."-".$input->param('comp_e_year') if($input->param('comp_date_range') eq '');
				$final_xml .= "</daterange_end>";
				$final_xml .= $comp_gcrf_group;
				$final_xml .= "\t"."</group2>";
				$final_xml .= "\t</GroupContributingRiskFactors>"."\n";
				$final_xml .= "\t<GroupExerciseHabits>"."\n";
				$final_xml .= "\t"."<group1>";
				$final_xml .= "\t"."<daterange_begin>";
				$final_xml .=  $input->param('s_month')."-".$input->param('s_day')."-".$input->param('s_year') if($input->param('date_range') eq '');
				$final_xml .= $input->param('date_range') if($input->param('date_range') ne '');
				$final_xml .= "</daterange_begin>";
				$final_xml .= "\t"."<daterange_end>";
				$final_xml .=  $input->param('e_month')."-".$input->param('e_day')."-".$input->param('e_year') if($input->param('date_range') eq '');
				$final_xml .= "</daterange_end>";
				$final_xml .= $geb_group;
				$final_xml .= "\t"."</group1>";
				$final_xml .= "\t"."<group2>";
				$final_xml .= "\t"."<daterange_begin>";
				$final_xml .=  $input->param('comp_s_month')."-".$input->param('comp_s_day')."-".$input->param('comp_s_year') if($input->param('comp_date_range') eq '');
				$final_xml .= $input->param('comp_date_range') if($input->param('comp_date_range') ne '');
				$final_xml .= "</daterange_begin>";
				$final_xml .= "\t"."<daterange_end>";
				$final_xml .=  $input->param('comp_e_month')."-".$input->param('comp_e_day')."-".$input->param('comp_e_year') if($input->param('comp_date_range') eq '');
				$final_xml .= "</daterange_end>";
				$final_xml .= $comp_geb_group;
				$final_xml .= "\t"."</group2>";
				$final_xml .= "\t</GroupExerciseHabits>"."\n";
				$final_xml .= "\t<GroupMammogram-femalesfortyandolder>"."\n";
				$final_xml .= "\t"."<group1>";
				$final_xml .= "\t"."<daterange_begin>";
				$final_xml .=  $input->param('s_month')."-".$input->param('s_day')."-".$input->param('s_year') if($input->param('date_range') eq '');
				$final_xml .= $input->param('date_range') if($input->param('date_range') ne '');
				$final_xml .= "</daterange_begin>";
				$final_xml .= "\t"."<daterange_end>";
				$final_xml .=  $input->param('e_month')."-".$input->param('e_day')."-".$input->param('e_year') if($input->param('date_range') eq '');
				$final_xml .= "</daterange_end>";
				$final_xml .= $gmf_group;
				$final_xml .= "\t"."</group1>";
				$final_xml .= "\t"."<group2>";
				$final_xml .= "\t"."<daterange_begin>";
				$final_xml .=  $input->param('comp_s_month')."-".$input->param('comp_s_day')."-".$input->param('comp_s_year') if($input->param('comp_date_range') eq '');
				$final_xml .= $input->param('comp_date_range') if($input->param('comp_date_range') ne '');
				$final_xml .= "</daterange_begin>";
				$final_xml .= "\t"."<daterange_end>";
				$final_xml .=  $input->param('comp_e_month')."-".$input->param('comp_e_day')."-".$input->param('comp_e_year') if($input->param('comp_date_range') eq '');
				$final_xml .= "</daterange_end>";
				$final_xml .= $comp_gmf_group;
				$final_xml .= "\t"."</group2>";
				$final_xml .= "\t</GroupMammogram-femalesfortyandolder>"."\n";
				$final_xml .= "\t<GroupPapSmear-allfemales>"."\n";
				$final_xml .= "\t"."<group1>";
				$final_xml .= "\t"."<daterange_begin>";
				$final_xml .=  $input->param('s_month')."-".$input->param('s_day')."-".$input->param('s_year') if($input->param('date_range') eq '');
				$final_xml .= $input->param('date_range') if($input->param('date_range') ne '');
				$final_xml .= "</daterange_begin>";
				$final_xml .= "\t"."<daterange_end>";
				$final_xml .=  $input->param('e_month')."-".$input->param('e_day')."-".$input->param('e_year') if($input->param('date_range') eq '');
				$final_xml .= "</daterange_end>";
				$final_xml .= $gps_group;
				$final_xml .= "\t"."</group1>";
				$final_xml .= "\t"."<group2>";
				$final_xml .= "\t"."<daterange_begin>";
				$final_xml .=  $input->param('comp_s_month')."-".$input->param('comp_s_day')."-".$input->param('comp_s_year') if($input->param('comp_date_range') eq '');
				$final_xml .= $input->param('comp_date_range') if($input->param('comp_date_range') ne '');
				$final_xml .= "</daterange_begin>";
				$final_xml .= "\t"."<daterange_end>";
				$final_xml .=  $input->param('comp_e_month')."-".$input->param('comp_e_day')."-".$input->param('comp_e_year') if($input->param('comp_date_range') eq '');
				$final_xml .= "</daterange_end>";
				$final_xml .= $comp_gps_group;
				$final_xml .= "\t"."</group2>";
				$final_xml .= "\t</GroupPapSmear-allfemales>"."\n";
				$final_xml .= "\t<GroupProstateExams-malesfortyandolder>"."\n";
				$final_xml .= "\t"."<group1>";
				$final_xml .= "\t"."<daterange_begin>";
				$final_xml .=  $input->param('s_month')."-".$input->param('s_day')."-".$input->param('s_year') if($input->param('date_range') eq '');
				$final_xml .= $input->param('date_range') if($input->param('date_range') ne '');
				$final_xml .= "</daterange_begin>";
				$final_xml .= "\t"."<daterange_end>";
				$final_xml .=  $input->param('e_month')."-".$input->param('e_day')."-".$input->param('e_year') if($input->param('date_range') eq '');
				$final_xml .= "</daterange_end>";
				$final_xml .= $gpe_group;
				$final_xml .= "\t"."</group1>";
				$final_xml .= "\t"."<group2>";
				$final_xml .= "\t"."<daterange_begin>";
				$final_xml .=  $input->param('comp_s_month')."-".$input->param('comp_s_day')."-".$input->param('comp_s_year') if($input->param('comp_date_range') eq '');
				$final_xml .= $input->param('comp_date_range') if($input->param('comp_date_range') ne '');
				$final_xml .= "</daterange_begin>";
				$final_xml .= "\t"."<daterange_end>";
				$final_xml .=  $input->param('comp_e_month')."-".$input->param('comp_e_day')."-".$input->param('comp_e_year') if($input->param('comp_date_range') eq '');
				$final_xml .= "</daterange_end>";
				$final_xml .= $comp_gpe_group;
				$final_xml .= "\t"."</group2>";
				$final_xml .= "\t</GroupProstateExams-malesfortyandolder>"."\n";
				$final_xml .= "\t<GroupSeatbeltUse>"."\n";
				$final_xml .= "\t"."<group1>";
				$final_xml .= "\t"."<daterange_begin>";
				$final_xml .=  $input->param('s_month')."-".$input->param('s_day')."-".$input->param('s_year') if($input->param('date_range') eq '');
				$final_xml .= $input->param('date_range') if($input->param('date_range') ne '');
				$final_xml .= "</daterange_begin>";
				$final_xml .= "\t"."<daterange_end>";
				$final_xml .=  $input->param('e_month')."-".$input->param('e_day')."-".$input->param('e_year') if($input->param('date_range') eq '');
				$final_xml .= "</daterange_end>";
				$final_xml .= $gsu_group;
				$final_xml .= "\t"."</group1>";
				$final_xml .= "\t"."<group2>";
				$final_xml .= "\t"."<daterange_begin>";
				$final_xml .=  $input->param('comp_s_month')."-".$input->param('comp_s_day')."-".$input->param('comp_s_year') if($input->param('comp_date_range') eq '');
				$final_xml .= $input->param('comp_date_range') if($input->param('comp_date_range') ne '');
				$final_xml .= "</daterange_begin>";
				$final_xml .= "\t"."<daterange_end>";
				$final_xml .=  $input->param('comp_e_month')."-".$input->param('comp_e_day')."-".$input->param('comp_e_year') if($input->param('comp_date_range') eq '');
				$final_xml .= "</daterange_end>";
				$final_xml .= $comp_gsu_group;
				$final_xml .= "\t"."</group2>";
				$final_xml .= "\t</GroupSeatbeltUse>"."\n";
				$final_xml .= "\t<GroupSmokingHabits>"."\n";
				$final_xml .= "\t"."<group1>";
				$final_xml .= "\t"."<daterange_begin>";
				$final_xml .=  $input->param('s_month')."-".$input->param('s_day')."-".$input->param('s_year') if($input->param('date_range') eq '');
				$final_xml .= $input->param('date_range') if($input->param('date_range') ne '');
				$final_xml .= "</daterange_begin>";
				$final_xml .= "\t"."<daterange_end>";
				$final_xml .=  $input->param('e_month')."-".$input->param('e_day')."-".$input->param('e_year') if($input->param('date_range') eq '');
				$final_xml .= "</daterange_end>";
				$final_xml .= $gsh_group;
				$final_xml .= "\t"."</group1>";
				$final_xml .= "\t"."<group2>";
				$final_xml .= "\t"."<daterange_begin>";
				$final_xml .=  $input->param('comp_s_month')."-".$input->param('comp_s_day')."-".$input->param('comp_s_year') if($input->param('comp_date_range') eq '');
				$final_xml .= $input->param('comp_date_range') if($input->param('comp_date_range') ne '');
				$final_xml .= "</daterange_begin>";
				$final_xml .= "\t"."<daterange_end>";
				$final_xml .=  $input->param('comp_e_month')."-".$input->param('comp_e_day')."-".$input->param('comp_e_year') if($input->param('comp_date_range') eq '');
				$final_xml .= "</daterange_end>";
				$final_xml .= $comp_gsh_group;
				$final_xml .= "\t"."</group2>";
				$final_xml .= "\t</GroupSmokingHabits>"."\n";
				$final_xml .= "\t<GroupWeight>"."\n";
				$final_xml .= "\t"."<group1>";
				$final_xml .= "\t"."<daterange_begin>";
				$final_xml .=  $input->param('s_month')."-".$input->param('s_day')."-".$input->param('s_year') if($input->param('date_range') eq '');
				$final_xml .= $input->param('date_range') if($input->param('date_range') ne '');
				$final_xml .= "</daterange_begin>";
				$final_xml .= "\t"."<daterange_end>";
				$final_xml .=  $input->param('e_month')."-".$input->param('e_day')."-".$input->param('e_year') if($input->param('date_range') eq '');
				$final_xml .= "</daterange_end>";
				$final_xml .= $gw_group;
				$final_xml .= "\t"."</group1>";
				$final_xml .= "\t"."<group2>";
				$final_xml .= "\t"."<daterange_begin>";
				$final_xml .=  $input->param('comp_s_month')."-".$input->param('comp_s_day')."-".$input->param('comp_s_year') if($input->param('comp_date_range') eq '');
				$final_xml .= $input->param('comp_date_range') if($input->param('comp_date_range') ne '');
				$final_xml .= "</daterange_begin>";
				$final_xml .= "\t"."<daterange_end>";
				$final_xml .=  $input->param('comp_e_month')."-".$input->param('comp_e_day')."-".$input->param('comp_e_year') if($input->param('comp_date_range') eq '');
				$final_xml .= "</daterange_end>";
				$final_xml .= $comp_gw_group;
				$final_xml .= "\t"."</group2>";
				$final_xml .= "\t</GroupWeight>"."\n";
				$final_xml .= "\t<NumberofAssessmentsTaken>"."\n";
				$final_xml .= "\t"."<group1>";
				$final_xml .= "\t"."<daterange_begin>";
				$final_xml .=  $input->param('s_month')."-".$input->param('s_day')."-".$input->param('s_year') if($input->param('date_range') eq '');
				$final_xml .= $input->param('date_range') if($input->param('date_range') ne '');
				$final_xml .= "</daterange_begin>";
				$final_xml .= "\t"."<daterange_end>";
				$final_xml .=  $input->param('e_month')."-".$input->param('e_day')."-".$input->param('e_year') if($input->param('date_range') eq '');
				$final_xml .= "</daterange_end>";
				$final_xml .= $nat_group;
				$final_xml .= "\t"."</group1>";
				$final_xml .= "\t"."<group2>";
				$final_xml .= "\t"."<daterange_begin>";
				$final_xml .=  $input->param('comp_s_month')."-".$input->param('comp_s_day')."-".$input->param('comp_s_year') if($input->param('comp_date_range') eq '');
				$final_xml .= $input->param('comp_date_range') if($input->param('comp_date_range') ne '');
				$final_xml .= "</daterange_begin>";
				$final_xml .= "\t"."<daterange_end>";
				$final_xml .=  $input->param('comp_e_month')."-".$input->param('comp_e_day')."-".$input->param('comp_e_year') if($input->param('comp_date_range') eq '');
				$final_xml .= "</daterange_end>";
				$final_xml .= $comp_nat_group;
				$final_xml .= "\t"."</group2>";
				$final_xml .= "\t</NumberofAssessmentsTaken>"."\n";
				$final_xml .= "\t<PersonalConditions>"."\n";
				$final_xml .= "\t"."<group1>";
				$final_xml .= "\t"."<daterange_begin>";
				$final_xml .=  $input->param('s_month')."-".$input->param('s_day')."-".$input->param('s_year') if($input->param('date_range') eq '');
				$final_xml .= $input->param('date_range') if($input->param('date_range') ne '');
				$final_xml .= "</daterange_begin>";
				$final_xml .= "\t"."<daterange_end>";
				$final_xml .=  $input->param('e_month')."-".$input->param('e_day')."-".$input->param('e_year') if($input->param('date_range') eq '');
				$final_xml .= "</daterange_end>";
				$final_xml .= $pc_group;
				$final_xml .= "\t"."</group1>";
				$final_xml .= "\t"."<group2>";
				$final_xml .= "\t"."<daterange_begin>";
				$final_xml .=  $input->param('comp_s_month')."-".$input->param('comp_s_day')."-".$input->param('comp_s_year') if($input->param('comp_date_range') eq '');
				$final_xml .= $input->param('comp_date_range') if($input->param('comp_date_range') ne '');
				$final_xml .= "</daterange_begin>";
				$final_xml .= "\t"."<daterange_end>";
				$final_xml .=  $input->param('comp_e_month')."-".$input->param('comp_e_day')."-".$input->param('comp_e_year') if($input->param('comp_date_range') eq '');
				$final_xml .= "</daterange_end>";
				$final_xml .= $comp_pc_group;
				$final_xml .= "\t"."</group2>";
				$final_xml .= "\t</PersonalConditions>"."\n";
				$final_xml .= "\t<PreventableDeathsbyDisease>"."\n";
				$final_xml .= "\t"."<group1>";
				$final_xml .= "\t"."<daterange_begin>";
				$final_xml .=  $input->param('s_month')."-".$input->param('s_day')."-".$input->param('s_year') if($input->param('date_range') eq '');
				$final_xml .= $input->param('date_range') if($input->param('date_range') ne '');
				$final_xml .= "</daterange_begin>";
				$final_xml .= "\t"."<daterange_end>";
				$final_xml .=  $input->param('e_month')."-".$input->param('e_day')."-".$input->param('e_year') if($input->param('date_range') eq '');
				$final_xml .= "</daterange_end>";
				$final_xml .= $pdd_group;
				$final_xml .= "\t"."</group1>";
				$final_xml .= "\t"."<group2>";
				$final_xml .= "\t"."<daterange_begin>";
				$final_xml .=  $input->param('comp_s_month')."-".$input->param('comp_s_day')."-".$input->param('comp_s_year') if($input->param('comp_date_range') eq '');
				$final_xml .= $input->param('comp_date_range') if($input->param('comp_date_range') ne '');
				$final_xml .= "</daterange_begin>";
				$final_xml .= "\t"."<daterange_end>";
				$final_xml .=  $input->param('comp_e_month')."-".$input->param('comp_e_day')."-".$input->param('comp_e_year') if($input->param('comp_date_range') eq '');
				$final_xml .= "</daterange_end>";
				$final_xml .= $comp_pdd_group;
				$final_xml .= "\t"."</group2>";
				$final_xml .= "\t</PreventableDeathsbyDisease>"."\n";
				$final_xml .= "\t<SelfBreastExam-allfemales>"."\n";
				$final_xml .= "\t"."<group1>";
				$final_xml .= "\t"."<daterange_begin>";
				$final_xml .=  $input->param('s_month')."-".$input->param('s_day')."-".$input->param('s_year') if($input->param('date_range') eq '');
				$final_xml .= $input->param('date_range') if($input->param('date_range') ne '');
				$final_xml .= "</daterange_begin>";
				$final_xml .= "\t"."<daterange_end>";
				$final_xml .=  $input->param('e_month')."-".$input->param('e_day')."-".$input->param('e_year') if($input->param('date_range') eq '');
				$final_xml .= "</daterange_end>";
				$final_xml .= $sbe_group;
				$final_xml .= "\t"."</group1>";
				$final_xml .= "\t"."<group2>";
				$final_xml .= "\t"."<daterange_begin>";
				$final_xml .=  $input->param('comp_s_month')."-".$input->param('comp_s_day')."-".$input->param('comp_s_year') if($input->param('comp_date_range') eq '');
				$final_xml .= $input->param('comp_date_range') if($input->param('comp_date_range') ne '');
				$final_xml .= "</daterange_begin>";
				$final_xml .= "\t"."<daterange_end>";
				$final_xml .=  $input->param('comp_e_month')."-".$input->param('comp_e_day')."-".$input->param('comp_e_year') if($input->param('comp_date_range') eq '');
				$final_xml .= "</daterange_end>";
				$final_xml .= $comp_sbe_group;
				$final_xml .= "\t"."</group2>";
				$final_xml .= "\t</SelfBreastExam-allfemales>"."\n";
				$final_xml .= "\t<SexbyAgeGroup>"."\n";
				$final_xml .= "\t"."<group1>";
				$final_xml .= "\t"."<daterange_begin>";
				$final_xml .=  $input->param('s_month')."-".$input->param('s_day')."-".$input->param('s_year') if($input->param('date_range') eq '');
				$final_xml .= $input->param('date_range') if($input->param('date_range') ne '');
				$final_xml .= "</daterange_begin>";
				$final_xml .= "\t"."<daterange_end>";
				$final_xml .=  $input->param('e_month')."-".$input->param('e_day')."-".$input->param('e_year') if($input->param('date_range') eq '');
				$final_xml .= "</daterange_end>";
				$final_xml .= $sbg_group;
				$final_xml .= "\t"."</group1>";
				$final_xml .= "\t"."<group2>";
				$final_xml .= "\t"."<daterange_begin>";
				$final_xml .=  $input->param('comp_s_month')."-".$input->param('comp_s_day')."-".$input->param('comp_s_year') if($input->param('comp_date_range') eq '');
				$final_xml .= $input->param('comp_date_range') if($input->param('comp_date_range') ne '');
				$final_xml .= "</daterange_begin>";
				$final_xml .= "\t"."<daterange_end>";
				$final_xml .=  $input->param('comp_e_month')."-".$input->param('comp_e_day')."-".$input->param('comp_e_year') if($input->param('comp_date_range') eq '');
				$final_xml .= "</daterange_end>";
				$final_xml .= $comp_sbg_group;
				$final_xml .= "\t"."</group2>";
				$final_xml .= "\t</SexbyAgeGroup>"."\n";
				$final_xml .= "\t<StressandDepressionResultsfromGeneralHealthAssessment>"."\n";
				$final_xml .= "\t"."<group1>";
				$final_xml .= "\t"."<daterange_begin>";
				$final_xml .=  $input->param('s_month')."-".$input->param('s_day')."-".$input->param('s_year') if($input->param('date_range') eq '');
				$final_xml .= $input->param('date_range') if($input->param('date_range') ne '');
				$final_xml .= "</daterange_begin>";
				$final_xml .= "\t"."<daterange_end>";
				$final_xml .=  $input->param('e_month')."-".$input->param('e_day')."-".$input->param('e_year') if($input->param('date_range') eq '');
				$final_xml .= "</daterange_end>";
				$final_xml .= $sdr_group;
				$final_xml .= "\t"."</group1>";
				$final_xml .= "\t"."<group2>";
				$final_xml .= "\t"."<daterange_begin>";
				$final_xml .=  $input->param('comp_s_month')."-".$input->param('comp_s_day')."-".$input->param('comp_s_year') if($input->param('comp_date_range') eq '');
				$final_xml .= $input->param('comp_date_range') if($input->param('comp_date_range') ne '');
				$final_xml .= "</daterange_begin>";
				$final_xml .= "\t"."<daterange_end>";
				$final_xml .=  $input->param('comp_e_month')."-".$input->param('comp_e_day')."-".$input->param('comp_e_year') if($input->param('comp_date_range') eq '');
				$final_xml .= "</daterange_end>";
				$final_xml .= $comp_sdr_group;
				$final_xml .= "\t"."</group2>"."\n";
				$final_xml .= "\t\t</StressandDepressionResultsfromGeneralHealthAssessment>"."\n";
				$final_xml .= "</ComparitiveReport>"."\n";
				#print $xml;
				print XML $final_xml . "\n";
			}
			else
			{
					print XML $xml . "\n";
			}
			close (XML);
			}
		elsif ( $format eq 'pdf' )
			{
			if ( lc($input->param('rpt_type')) eq 'agrgt_data' )
				{
				#create the PDF file
				%Defaults = 	(
						FileName => $output_file_name
						);

				my $vars = $input->Vars;
				%vars = %$vars;

				print '<br>creating graphs:<br>';

				my $h_ref = prepare_graphs_arg_pdf(\%hash, $config->ggr_adv_page_dir, $assessments_ref, \@assessment_count,$config->font_directory, $blank_data, \%PARMS, \%COMPPARMS, \%GROUP, \%COMPGROUP, $hra_cnt, $config );
				my %PARMS = %{$h_ref};

				$vars{image_dir} = $config->ggr_adv_page_dir;
				$vars{assessments_used_hash} = \%assessments_used_hash;
				$vars{fixed_images} = $config->fixed_images;
				$vars{ggr_branding} = $config->ggr_branding;
				foreach (keys %PARMS) { $vars{$_} = $PARMS{$_} }
				print '<br>generating PDF</p>';

				my $ggr_template = $GGR_PDF;

	# build the intermediate xml file from a template.
				my $pdfoutput = new Text::Template (SOURCE => $ggr_template, HASH => \%vars  )
				or die qq|Couldn't fill in template: $Text::Template::ERROR<br>$ggr_template| ;


				my $data = $pdfoutput->fill_in() or die qq|Couldn't fill in template: $Text::Template::ERROR<br>$GGR_PDF|;

				print '<p class="maintext-b">Report completed, creating output file.</p>';
	# save the intermediate xml file (mainly for debugging purposes)
				open (PDF , "> " . $config->ggr_adv_page_dir . "ggr_adv_xml.xml");
				print PDF $data;
				close PDF;
	# this creates the PDF
				{
					my $newdir = $config->ggr_adv_page_dir . $set->{work_dir} ;					
					#carp "$newdir\n";
					#carp "$output_file_name\n";
					if (-e $output_file_name) {
						my $cnt = unlink $output_file_name;
						die "couldn't erase $output_file_name\n" if (!$cnt);
					}
                    carp "line 1785::::::$wd_time:::::$output_file_name"; 
					PDFDoc->importXML( $data )->writePDF( $output_file_name );
				}
				}
			}
		}
# if they want any of the files emailed, do that here
	if ( lc($input->param('rpt_email')) eq 'on' && $input->param('email') gt '' )
		{
		my $email_address = $input->param('email');
		send_email_attachment( $user, $config, $format, $email_address, $output_file_name);
		}
	if ( lc($input->param('rpt_type')) eq 'indv_data' && $format eq 'pdf' ){
	   	my $zip = Archive::Zip->new();
		carp "line 1800::::::$wd_time"; 
	   	my $member = $zip->addTreeMatching( $config->ggr_adv_page_dir . $wd_time, '' , '\.pdf$' );		
	   	$wd_time =~ s|/||;		
	   	die 'write error' unless $zip->writeToFileNamed( $config->ggr_adv_page_dir . $wd_time.'.zip' ) == AZ_OK;
        carp "file name::::$file_name";
        $file_name =~ s|/||;		
		print qq|<p class="maintext-b">Your PDF files are stored in the report output area in directory | . $file_name . '. They are also in a zip file <a href="' . $config->ggr_adv . '?view=1&rpt_format=zip&file_name=' . $wd_time . '">Click here to download</a>.</p>';
		}
	else	{
		print '<p class="maintext-b">' . $input->param('rpt_format') . ' output file is written.  <a href="' . $config->ggr_adv . '?view=1&rpt_format=' . $input->param('rpt_format') . '&file_name=' . $file_name . '" target=_blank>Click here to view</a>';
		}

	if($input->param('ggr2_batch')){
	       close FILE;
	       unlink($config->conf_data_dir.'/saved_reports/'.$input->param('site_selection').'.log ');
	       }
	else   {
		my $ggr1 = $config->ggr_adv || $config->cgi_dir . '/ggr_adv2.cgi';
		print '<p class="maintext-b">[ <a href="' . $ggr1 . '">run another group report</a> ]';
		my $member = $config->member_page || $config->cgi_dir . '/assessment_recs.cgi';
		print '<p class="maintext-b">[ <a href="' . $member . '">assessment records page</a> ]';
		}

}
sub date_queries
{
	my $input = shift;
	my $order_key = shift;
	my $temp_id = shift;
	my $prefix = shift;
	my @date_conditions ;

	my $date_select_field = "A.adate";
	if( lc($config->db_driver) eq 'oracle' ){$date_select_field = "A.ADATE";}
	if ($input->param($prefix.'date') eq $prefix.'date_range') {
		if($input->param($prefix.'date_range') eq 'yesterday'){
			($w_year,$w_month,$w_day) = Add_Delta_Days($curr_year, $curr_month, $curr_day, -1);
			push @date_conditions, " $date_select_field>='" . $w_year . "-" . sprintf("%02d",$w_month) . "-" . sprintf("%02d",$w_day) ." 00:00:00'";
			push @date_conditions, " $date_select_field<='" . $w_year . "-" . sprintf("%02d",$w_month) . "-" . sprintf("%02d",$w_day) . " 23:59:59'";
		}
		if($input->param($prefix.'date_range') eq 'this_week'){
			my ($week,$year) = Week_of_Year($curr_year, $curr_month, $curr_day);
			($w_year,$w_month,$w_day) = Monday_of_Week($week,$year);
			($w1_year,$w1_month,$w1_day) = Monday_of_Week($week+1,$year);
			push @date_conditions, " $date_select_field>='" . $w_year . "-" . sprintf("%02d",$w_month) . "-" . sprintf("%02d",$w_day) ." 00:00:00'";
			push @date_conditions, " $date_select_field<'" . $w1_year . "-" . sprintf("%02d",$w1_month) . "-" . sprintf("%02d",$w1_day) . " 00:00:00'";

		}
		if($input->param($prefix.'date_range') eq 'last_week'){
			my ($week,$year) = Week_of_Year($curr_year, $curr_month, $curr_day);
			($w_year,$w_month,$w_day) = Monday_of_Week($week-1,$year);
			($w1_year,$w1_month,$w1_day) = Monday_of_Week($week,$year);
			push @date_conditions, " $date_select_field>='" . $w_year . "-" . sprintf("%02d",$w_month) . "-" . sprintf("%02d",$w_day) ." 00:00:00'";
			push @date_conditions, " $date_select_field<'" . $w1_year . "-" . sprintf("%02d",$w1_month) . "-" . sprintf("%02d",$w1_day) . " 00:00:00'";

		}
		if($input->param($prefix.'date_range') eq 'this_month'){
			my $day = Days_in_Month( $curr_year, $curr_month );
			push @date_conditions, " $date_select_field>='" . $curr_year . "-" . sprintf("%02d",$curr_month) . "-01 00:00:00'";
			push @date_conditions, " $date_select_field<='" . $curr_year . "-" . sprintf("%02d",$curr_month) . "-" . sprintf("%02d",$day) . " 23:59:59'";

		}
		if($input->param($prefix.'date_range') eq 'last_month'){
			if($curr_month == 1){ $curr_year = $curr_year - 1; $curr_month = 12; } else { $curr_month = $curr_month - 1;}
			my $day = Days_in_Month( $curr_year, $curr_month );
			push @date_conditions, " $date_select_field>='" . $curr_year . "-" . sprintf("%02d",$curr_month) . "-01 00:00:00'";
			push @date_conditions, " $date_select_field<='" . $curr_year . "-" . sprintf("%02d",$curr_month) . "-" . sprintf("%02d",$day) . " 23:59:59'";
		}
		if ($input->param($prefix.'date_range') eq 'this_quarter'){
			my @quarters_defined;
			@quarters_defined = (0,1,1,1,2,2,2,3,3,3,4,4,4);
			push @date_conditions, " $date_select_field>='" . $curr_year . "-" . $quarters_hash{$quarters_defined[$curr_month]}{beg_mon} . "-" . $quarters_hash{$quarters_defined[$curr_month]}{beg_day} . " 00:00:00'";
			push @date_conditions, " $date_select_field<='" . $curr_year . "-" . $quarters_hash{$quarters_defined[$curr_month]}{end_mon} . "-" . $quarters_hash{$quarters_defined[$curr_month]}{end_day} . " 23:59:59'";

		}
		if ($input->param($prefix.'date_range') eq 'last_quarter'){
			my @quarters_defined;
			@quarters_defined = (0,4,4,4,1,1,1,2,2,2,3,3,3);
			if($quarters_defined[$curr_month] == 4){ $curr_year = $curr_year - 1; }
			push @date_conditions, " $date_select_field>='" . $curr_year . "-" . $quarters_hash{$quarters_defined[$curr_month]}{beg_mon} . "-" . $quarters_hash{$quarters_defined[$curr_month]}{beg_day} . " 00:00:00'";
			push @date_conditions, " $date_select_field<='" . $curr_year . "-" . $quarters_hash{$quarters_defined[$curr_month]}{end_mon} . "-" . $quarters_hash{$quarters_defined[$curr_month]}{end_day} . " 23:59:59'";
		}
		if ($input->param($prefix.'date_range') eq 'this_year' || $input->param($prefix.'date_range') eq 'last_year'){
			$curr_year = $curr_year - 1 if (lc($input->param($prefix.'date_range')) eq 'last_year');
			push @date_conditions, " $date_select_field>='" . $curr_year . "-01-01 00:00:00'";
			push @date_conditions, " $date_select_field<='" . $curr_year . "-12-31 23:59:59'";
		}
	}
	if ($input->param($prefix.'date') eq 'specific' || $input->param($prefix.'date') eq 'specific1' || $input->param($prefix.'date') eq 'specific2'  ){
		if ($input->param($prefix.'s_month') > 0 && $input->param($prefix.'s_month') <= 12 ){
			my $day = $input->param($prefix.'s_day');
			if (Days_in_Month( $input->param($prefix.'s_year'), $input->param($prefix.'s_month') ) < $day ){
				$day = Days_in_Month( $input->param($prefix.'s_year'), $input->param($prefix.'s_month') );
			}
			push @date_conditions, " $date_select_field>='" . $input->param($prefix.'s_year') . "-" . sprintf("%02d",$input->param($prefix.'s_month')) . "-" . sprintf("%02d",$day) . " 00:00:00'";

		}
		if( $input->param($prefix.'e_month') > 0 && $input->param($prefix.'e_month') <= 12 ){
			if( $input->param($prefix.'s_month') ){
				my $bad_date = FALSE;
				if ( $input->param($prefix.'s_month') <= 0 || $input->param($prefix.'s_month') > 12 ){
					$bad_date = TRUE
				}
				if ( $input->param($prefix.'e_month') <= 0 || $input->param($prefix.'e_month') > 12 ){
					$bad_date = TRUE
				}
				my $Dd = Delta_Days($input->param($prefix.'s_year'),$input->param($prefix.'s_month'),$input->param($prefix.'s_day'), $input->param($prefix.'e_year'),$input->param($prefix.'e_month'),$input->param($prefix.'e_day'));
				if ($Dd < 0 || $bad_date) {
					my %hash;
					error( "Your beginning date is after your end date, no data will be returned." );
					$hash{error_msg} = "There is a problem with your dates.";
					my $form = $config->template_directory . $config->error_user;
					HealthStatus::fill_and_send( $form, $user, \%hash, $config->html_use_ssi );
					exit;
				}
			}
			my $day = $input->param($prefix.'e_day');
			if (Days_in_Month( $input->param($prefix.'e_year'), $input->param($prefix.'e_month') ) < $day ){
				$day = Days_in_Month( $input->param($prefix.'e_year'), $input->param($prefix.'e_month') );
			}
			push @date_conditions, " $date_select_field<='" . $input->param($prefix.'e_year') . "-" . sprintf("%02d",$input->param($prefix.'e_month')) . "-" . sprintf("%02d",$day) . " 23:59:59'";
		}
	}

	my $date_condition_str = '';
	$date_condition_str .= $date_conditions[0] . ' AND ' . $date_conditions[1] . ' AND ' if( scalar(@date_conditions) > 1 );

	my $date_stipulations = "WHERE " . $date_condition_str ;
	my $participation_date = $date_condition_str;
	$date_stipulations .= " U.$temp_id=XX_X_XX AND U.$temp_id=A.$temp_id ORDER BY $date_select_field $order_key";

	return ($date_stipulations, $participation_date);;
}

sub participating_users {}