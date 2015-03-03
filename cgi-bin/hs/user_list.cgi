#!/usr/local/bin/perl

use strict;

=head1 NAME

user_list.cgi User List Report

=head1 SYNOPSIS

user_list.cgi 	  		=> will prompt you for sql parameters that can be changed
user_list.cgi?process=1 	=> will process the report with no sql restrictions (all records)
user_list.cgi?view=1    	=> will show you the most recent PDF file created
user_list.cgi?max=xx 	  	=> will stop processing after xx records
user_list.cgi?pgraphs=all 	=> will print all the graph pages

=head1 DESCRIPTION

The user list report, grabs a list of users that meets the criteria specified
in the query screen, and creates email lists for the different criteria.

Queries can be made based on the site field or the date assessments were taken.

The templates used are:
	user_list_in.html for input
	user_list_check.html for query verification

Output files are created in the data directory and have the prefix user_

=cut


if (!do('common.inc')) {
   my $error = $@ ? $@
             : $! ? $!
             : 'did not return a true value';
   die("Unable to load common stuff: $error\n");
}

use CGI qw(-no_xhtml -debug);
use Date::Calc;
use Text::Template;
use HTML::FillInForm;
use Time::localtime;
use GD::Graph::mixed;
use GD::Graph::pie;
use GD::Graph::bars;
use File::Copy;
use Carp;
use PDF;

use HealthStatus::CalcRisk;

use vars qw(%vars %Defaults);

my ( %PARMS , %GROUP, %CONFIG);
my ($high, $medium, $moderate, $high_cnt, $medium_cnt, $moderate_cnt, $low_cnt, $ach_high, $ach_medium, $ach_moderate);
my ($ach_high_cnt, $ach_medium_cnt, $ach_moderate_cnt, $ach_low_cnt, $ach_age, $mfactor, $ts, $risks, $hash);
my ($b_graph, $b1_graph, $b2_graph, $b3_graph, $b4_graph, $b5_graph, $b6_graph, $b7_graph, $b8_graph, $b9_graph, $b10_graph);
my ($b11_graph, $b12_graph, $b13_graph, $b14_graph, $b15_graph, $b16_graph, $b17_graph, $b18_graph, $b19_graph, $b20_graph );
my ($b21_graph, $b22_graph);
my (@g_data, @g1_data, @g2_data, @g3_data, @g4_data, @g5_data, @g6_data, @g7_data, @g8_data, @g9_data, @g10_data);
my (@g11_data, @g12_data, @g13_data, @g14_data, @g15_data, @g16_data, @g17_data, @g18_data, @g19_data, @g20_data);
my (@g21_data, @g22_data);
my ($health, $riskFactor, $riskAvg, $riskDesc, $riskAch, $gd_graph, $hra_cnt, $o_file );
my (@site_list, $stipulation, $user_list_ref, %user_list, $html_string, $select_string );

my $input = new CGI();
my $config = getConfig($input->param('extracfg'));

my $fixed_images = "/usr/local/www/vhosts/managed2/base/htdocs/images/global/";
my $font_dir = "/usr/local/www/vhosts/managed2/base/template/ttf";
my $GGR_PDF = $config->ggr_pdf_template;
$ENV{TEMP} = $config->ggr_page_dir;
my $GGR_PAGE_DIR = $config->ggr_page_dir;
my $blank_data = $config->ggr_blank_image;

my @assessments = split /\s+/, $config->ggr_tables;
my $assessments_ref = \@assessments;
my %assessment_names = ( HRA	=> 'General Health assesments ',
			 GHA	=> 'Health Risk assesments (original)',
			 CRC	=> 'Cardiac Risk assesments',
			 DRC	=> 'Diabetes Risk assesments',
			 FIT	=> 'Fitness assesments',
			 GWB	=> 'General Well Being assesments');

my $cnt = 0;

my @parm_list = ( 'm_lt_19','f_lt_19','m_19_29','f_19_29','m_30_39','f_30_39','m_40_49','f_40_49','m_50_59','f_50_59','m_60','f_60',
'sm_still','sm_never','sm_quit','males','females','wt_under','wt_good','wt_over','wt_obese','sb_never','sb_seldom','sb_some','sb_usually','sb_always','sb_speed','sb_drinkdrive',
'chol_high','chol_med','chol_low','chol_unknown','bp_high','bp_med','bp_low','bp_unknown','bp_no_meds','bp_meds','alc_high','alc_medium','alc_low','alc_drinks','exer_none','exer_some','exer_good',
'pap_good','pap_med','pap_bad','high','high_cnt','medium','medium_cnt','low','ach_high_cnt','ach_high','ach_medium_cnt','ach_medium','ach_moderate','ach_moderate_cnt','ach_low','user_count');

foreach (@parm_list){
	$PARMS{$_} = 0;
	}

my @group_list = ( 'Throat Cancer Mortality','Flu/Pneumonia Mortality','Liver Mortality','Lung Cancer Mortality','Esophageal Cancer Mortality','Pancreatic Cancer Mortality','Uterine Cancer Mortality',
	'Emphysema Mortality','Laryngeal Cancer Mortality','Kidney Failure Mortality','Heart Attack Mortality','Breast Cancer Mortality','Diabetes Mellitus Mortality','Motor Vehicle Mortality',
	'Cervical Cancer Mortality','Stroke Mortality','Mouth Cancer Mortality','Bladder Cancer Mortality','Peptic Ulcer Mortality');

foreach (@group_list){
	$GROUP{$_} = 0;
	}

foreach (@assessments){
	$PARMS{'users_back'}{$_}=0;
	$PARMS{'assessment'}{$_}=0;
	$PARMS{$_}=0;
	}

my $user = HealthStatus::User->new( );

if( $config->authenticate_admin == YES )
	{
	my $temp_file_dir = $config->authenticate_dir;
	my $temp_file = $input->cookie('hs_ident') || $input->param('hs_ident') || '10001';

	my $approved = HealthStatus::Authenticate->new( $config, $temp_file_dir, $temp_file );

	my $status = $approved->check( $config, $user );

	if ( $status eq TIMEOUT )
		{
		print $input->redirect (-uri => $config->timeout_page );
		exit 1;
		}
	elsif ( $status eq NOT_LOGGED )
		{
		print $input->redirect (-uri => $config->login_page );
		exit 1;
		}
	elsif ( $status ne APPROVED)
		{
		error( "There is a problem with your login" );
		exit 1;
		}
	if( !$user->hs_administration ){
		error( "You are not authorized to run this program" );
		exit 1;
		}
	}

my $db = HealthStatus::Database->new( $config );

if ($input->param('view'))
	{
	print $input->header(-type=>'application/pdf');
	binmode STDOUT;
	open (PDF , "< ${GGR_PAGE_DIR}ggr_output.pdf");
	sysread PDF, my $content, -s PDF;
	print $content;
	close PDF;
	exit;
	}
elsif ($input->param('process'))
	{

	$| = 1;
	print $input->header(-type=>'text/html');
	print $input->start_html(-title=>'User List Report Processor',
		    -author=>'gwhite@healthstatus.com',
		    -style=>{'src'=>'http://www.healthstatus.net/HSstyles/ggr_style.css'} );
	print "<p><b>Report being generated</b></p>";
	print "<p>getting user list<br>";

	if ($input->param('ggr_sql'))
		{
		 $stipulation = $input->param('user_list_sql');

		 print "filtering<br>";

		 $user_list_ref  =  $db->get_users_by_stipulation( $config, $assessments_ref, $stipulation );
		}
	else	{
		print "all sites, all dates<br>";

		$user_list_ref  =  $db->get_users( $config, $assessments_ref );
		}

	%user_list = %{$user_list_ref};

	print "have the list, processing begins<p>";

	foreach ( sort keys %user_list )
		{
		if ( ( $cnt % 50 ) == 0 && $cnt > 1)
			{
			if ($cnt == 50)
				{ print "processing data - $cnt users completed<br>"; }
			else	{ print "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;$cnt users completed<br>"; }
			}

		print "<p>" if ( ( $cnt % 1000 ) == 0 && $cnt > 1);

		last if ($cnt >= $max_to_process  && $max_to_process > 0);

		++$cnt;

		foreach my $alist( @assessments ) {
			if($user_list{$_}{$alist} > 1){ ++$PARMS{'users_back'}{$alist} }
			$PARMS{assessment}{$alist} = 0;
			$PARMS{$alist} += $user_list{$_}{$alist};
			}

		undef $user;
		undef $health;

		my $user = HealthStatus::User->new( );
		$user->db_id ($_);

		$PARMS{assessment}{user} = 0;

		my @returned_recs  =  $db->get_users_assessments_taken( $user, $config, $assessments_ref );

		foreach my $this_user ( @returned_recs )
			{
			next if ( $PARMS{assessment}{$this_user->{'assessment'}} );
			++$PARMS{assessment}{$this_user->{'assessment'}};

			$db->get_users_assessment( $user, $config, $this_user->{'assessment'}, $this_user->{'xnum'});

			if ($user->error)
				{
				--$PARMS{assessment}{$this_user->{'assessment'}};
				next;
				}

			$user->set_non_standard;

			$health = HealthStatus->new(
				{
				assessment => $this_user->{'assessment'},
				user       => $user,
				config     => $config_file,
				}
				);

			$health->assess( $user );

			if( !$PARMS{assessment}{user} )
				{
				++$PARMS{user_count};
				++$PARMS{assessment}{user};
				if( $user->sex eq MALE )
					{
					++$PARMS{'male'};
					++$PARMS{'m_lt_19'} if ($user->age <= 19);
					++$PARMS{'m_20_29'} if ($user->age >= 20 && $user->age <= 29);
					++$PARMS{'m_30_39'} if ($user->age >= 30 && $user->age <= 39);
					++$PARMS{'m_40_49'} if ($user->age >= 40 && $user->age <= 49);
					++$PARMS{'m_50_59'} if ($user->age >= 50 && $user->age <= 59);
					++$PARMS{'m_60'} if ($user->age >= 60);
					}
				else
					{
					++$PARMS{'female'};
					++$PARMS{'f_lt_19'} if ($user->age <= 19);
					++$PARMS{'f_20_29'} if ($user->age >= 20 && $user->age <= 29);
					++$PARMS{'f_30_39'} if ($user->age >= 30 && $user->age <= 39);
					++$PARMS{'f_40_49'} if ($user->age >= 40 && $user->age <= 49);
					++$PARMS{'f_50_59'} if ($user->age >= 50 && $user->age <= 59);
					++$PARMS{'f_60'} if ($user->age >= 60);
					}
				if( $this_user->{'assessment'} eq 'FIT' ||
					$this_user->{'assessment'} eq 'DRC' ||
					$this_user->{'assessment'} eq 'CRC' ||
					$this_user->{'assessment'} eq 'GHA' ||
					$this_user->{'assessment'} eq 'HRA')
					{
					++$PARMS{'wt_under'} if ($user->bmi <= BMI_LOW);
					++$PARMS{'wt_good'} if ($user->bmi <= BMI_GOOD && $user->bmi > BMI_LOW);
					++$PARMS{'wt_over'} if ($user->bmi < BMI_OBESE && $user->bmi > BMI_GOOD);
					++$PARMS{'wt_obese'} if ($user->bmi >= BMI_OBESE);
					}
				if( $this_user->{'assessment'} eq 'CRC' ||
					$this_user->{'assessment'} eq 'GHA' ||
					$this_user->{'assessment'} eq 'HRA')
					{
					++$PARMS{'sm_still'} if ($user->smoke_status eq 'Still smoke');
					++$PARMS{'sm_never'} if ($user->smoke_status eq NEVER_SMOKED);
					++$PARMS{'sm_quit'} if ($user->smoke_status eq USE_TO_SMOKE);
					++$PARMS{'exer_none'} if($user->exercise eq 'Less than one time per week' ||
								$user->exercise == 0);
					++$PARMS{'exer_some'} if($user->exercise eq 'One or two times per week' ||
								$user->exercise == 1  ||
								$user->exercise == 2);
					++$PARMS{'exer_good'} if($user->exercise eq 'At least three times per week'||
								$user->exercise > 2);
					++$PARMS{'chol_high'} if($user->cholesterol > CHOL_HIGH ||
								$user->cholesterol_check eq HIGH);
					++$PARMS{'chol_med'} if($user->cholesterol >= CHOL_MARGINAL &&
								$user->cholesterol <= CHOL_HIGH);
					++$PARMS{'chol_low'} if(($user->cholesterol > 1 &&
								$user->cholesterol < CHOL_MARGINAL) ||
								$user->cholesterol_check eq NORMAL_OR_LOW);
					++$PARMS{'chol_unknown'} if($user->cholesterol_check eq DONT_KNOW);
					++$PARMS{'HDL_low'} if ($user->hdl < HDL_LOW &&
								$user->hdl > 0);
					++$PARMS{'bp_high'} if(($user->bp_sys >= BP_HIGH_SYSTOLIC &&
								$user->bp_dias >= BP_HIGH_DIASTOLIC) ||
								$user->bp_check eq HIGH);
					++$PARMS{'bp_med'}if(($user->bp_sys >= BP_MARGINAL_SYSTOLIC ||
								$user->bp_dias >= BP_MARGINAL_DIASTOLIC) &&
								($user->bp_sys <= BP_HIGH_SYSTOLIC ||
								$user->bp_dias <= BP_HIGH_DIASTOLIC));
					++$PARMS{'bp_low'}if(($user->bp_sys > 1 &&
								$user->bp_sys < BP_MARGINAL_SYSTOLIC) &&
								($user->bp_dias > 1 &&
								$user->bp_dias < BP_MARGINAL_DIASTOLIC) ||
								$user->bp_check eq NORMAL_OR_LOW);
					++$PARMS{'bp_unknown'} if($user->bp_check eq DONT_KNOW);
					}

				}

			if( $this_user->{'assessment'} eq 'DRC' )
				{
				++$PARMS{DRC_cnt};
				++$PARMS{'diabetes_low'} if ( $user->diabetes_points <= 6);
				++$PARMS{'diabetes_med'} if ( $user->diabetes_points > 6 &&
								$user->diabetes_points < 9 );
				++$PARMS{'diabetes_high'} if ( $user->diabetes_points > 9);
				}

			if( $this_user->{'assessment'} eq 'CRC' )
				{
				++$PARMS{CRC_cnt};
				++$PARMS{'cardiac_high'} if ( $user->cardiac_risk/3 > $user->cardiac_average_risk );
				++$PARMS{'cardiac_med'} if ( $user->cardiac_risk/2 > $user->cardiac_average_risk &&  $user->cardiac_risk/3 <= $user->cardiac_average_risk );
				++$PARMS{'cardiac_mod'} if ( $user->cardiac_risk > $user->cardiac_average_risk && $user->cardiac_risk/2 <= $user->cardiac_average_risk );
				++$PARMS{'cardiac_low'} if ( $user->cardiac_risk <= $user->cardiac_average_risk );
				}

			if( $this_user->{'assessment'} eq 'FIT' )
				{
				++$PARMS{FIT_cnt};
				++$PARMS{'fit_step_high'} 	if ( $user->step_flag == 0 	||
									$user->step_flag == 1 );
				++$PARMS{'fit_step_med'} 	if ( $user->step_flag == 2 );
				++$PARMS{'fit_step_low'} 	if ( $user->step_flag == 3 	||
									$user->step_flag == 4 );
				++$PARMS{'fit_push_high'} 	if ( $user->push_up_flag == 0 	||
									$user->push_up_flag == 1 );
				++$PARMS{'fit_push_med'} 	if ( $user->push_up_flag == 2 );
				++$PARMS{'fit_push_low'} 	if ( $user->push_up_flag == 3 	||
									$user->push_up_flag == 4 );
				++$PARMS{'fit_sits_high'} 	if ( $user->sit_up_flag == 0 	||
									$user->sit_up_flag == 1 );
				++$PARMS{'fit_sits_med'} 	if ( $user->sit_up_flag == 2 );
				++$PARMS{'fit_sits_low'} 	if ( $user->sit_up_flag == 3 	||
									$user->sit_up_flag == 4 );
				++$PARMS{'fit_flex_high'} 	if ( $user->flexibility_flag == 0 ||
									$user->flexibility_flag == 1 );
				++$PARMS{'fit_flex_med'} 	if ( $user->flexibility_flag == 2 );
				++$PARMS{'fit_flex_low'} 	if ( $user->flexibility_flag == 3 ||
									$user->flexibility_flag == 4 );
				}

			if( $this_user->{'assessment'} eq 'GWB' )
				{
				++$PARMS{'gwb_stress_low'} 	if ( $user->stress_flag == 0 );
				++$PARMS{'gwb_stress_med'} 	if ( $user->stress_flag == 1 );
				++$PARMS{'gwb_stress_high'} 	if ( $user->stress_flag == 2 );
				++$PARMS{'gwb_depression_high'} if ( $user->depression_flag == 2 );
				++$PARMS{'gwb_depression_med'} 	if ( $user->depression_flag == 1 );
				++$PARMS{'gwb_depression_low'} 	if ( $user->depression_flag == 0 );
				++$PARMS{'gwb_health_high'} 	if ( $user->health_flag == 0 );
				++$PARMS{'gwb_health_med'} 	if ( $user->health_flag == 1 );
				++$PARMS{'gwb_health_low'} 	if ( $user->health_flag == 2 );
				++$PARMS{'gwb_control_high'} 	if ( $user->control_flag == 0 );
				++$PARMS{'gwb_control_med'} 	if ( $user->control_flag == 1 );
				++$PARMS{'gwb_control_low'} 	if ( $user->control_flag == 2 );
				++$PARMS{'gwb_being_high'} 	if ( $user->being_flag == 0 );
				++$PARMS{'gwb_being_med'} 	if ( $user->being_flag == 1 );
				++$PARMS{'gwb_being_low'} 	if ( $user->being_flag == 2 );
				++$PARMS{'gwb_vitality_high'} 	if ( $user->vitality_flag == 0 );
				++$PARMS{'gwb_vitality_med'} 	if ( $user->vitality_flag == 1 );
				++$PARMS{'gwb_vitality_low'} 	if ( $user->vitality_flag == 2 );
				++$PARMS{GWB_cnt};
				}

			if( $this_user->{'assessment'} eq 'HRA' )
				{
				++$PARMS{'my_cancer'}		if ( $user->cancer_chk == 1 );
				++$PARMS{'fh_cancer'}		if ( $user->fh_cancer_chk == 1 );
				++$PARMS{'my_diabetes'}		if ( $user->diabetes_chk == 1 );
				++$PARMS{'fh_diabetes'}		if ( $user->fh_diabetes_chk == 1 );
				++$PARMS{'my_heart'}		if ( $user->heart_attack_chk == 1 );
				++$PARMS{'fh_heart'}		if ( $user->fh_heart_attack_chk == 1 );
				++$PARMS{'my_hrtdisease'}	if ( $user->heart_disease_chk == 1 );
				++$PARMS{'fh_hrtdisease'}	if ( $user->fh_heart_disease_chk == 1 );
				++$PARMS{'my_bp'}		if ( $user->high_bp_chk == 1 );
				++$PARMS{'fh_bp'}		if ( $user->fh_high_bp_chk == 1 );
				++$PARMS{'my_chol'}		if ( $user->high_cholesterol_chk == 1 );
				++$PARMS{'fh_chol'}		if ( $user->fh_high_cholesterol_chk == 1 );
				++$PARMS{'my_stroke'}		if ( $user->stroke_chk == 1 );
				++$PARMS{'fh_stroke'}		if ( $user->fh_stroke_chk == 1 );

				## stress and depression
				my $t_wellbeing = $user->q5 + $user->q8 + $user->q17 + $user->q19 + $user->q22;
				my $t_depression = $user->q3 + $user->q7 + $user->q11;

				my $stress_flag = do
					{
					if(    $t_wellbeing > 18) {  0 }
					elsif( $t_wellbeing <  8) {  2 }
					else                 {       1 }
					};

				my $depression_flag = do
					{
					if(    $t_depression > 10 ) {  0 }
					elsif( $t_depression <  6 ) {  2 }
					else                      {    1 }
					};

				++$PARMS{'gwb_stress_low'} 	if ( $stress_flag == 0 );
				++$PARMS{'gwb_stress_med'} 	if ( $stress_flag == 1 );
				++$PARMS{'gwb_stress_high'} 	if ( $stress_flag == 2 );
				++$PARMS{'gwb_depression_high'} if ( $depression_flag == 2 );
				++$PARMS{'gwb_depression_med'} 	if ( $depression_flag == 1 );
				++$PARMS{'gwb_depression_low'} 	if ( $depression_flag == 0 );
				}

			if( $this_user->{'assessment'} eq 'GHA' ||
					$this_user->{'assessment'} eq 'HRA')
				{
				++$PARMS{GHA_cnt} if( $this_user->{'assessment'} eq 'GHA') ;
				++$PARMS{HRA_cnt} if( $this_user->{'assessment'} eq 'HRA');
				++$PARMS{'sb_never'} if($user->seat_belt eq 'Never, 0%');
				++$PARMS{'sb_seldom'} if($user->seat_belt eq 'Seldom, 1%-40%');
				++$PARMS{'sb_some'} if($user->seat_belt eq 'Sometimes, 41%-80%');
				++$PARMS{'sb_usually'} if($user->seat_belt eq NEARLY_ALWAYS);
				++$PARMS{'sb_always'} if($user->seat_belt eq ALWAYS_100);
				++$PARMS{'sb_drinkdrive'} if ($user->drink_and_drive  > 0);
				++$PARMS{'sb_speed'} if ($user->speed eq 'More than 15 mph over limit');
				++$PARMS{'alc_high'} if($user->drinks_week > 20);
				++$PARMS{'alc_medium'} if($user->drinks_week <= 20 &&
								$user->drinks_week >= 13);
				++$PARMS{'alc_low'} if($user->drinks_week < 13);
				$PARMS{'alc_drinks'} += $user->drinks_week;
				++$PARMS{'bp_meds'}if($user->bp_meds eq YES);
				++$PARMS{'bp_no_meds'}if((($user->bp_sys > BP_HIGH_SYSTOLIC &&
								$user->bp_dias > BP_HIGH_DIASTOLIC) ||
								$user->bp_check eq HIGH) &&
								$user->bp_meds eq NO);

				if( $user->sex eq MALE )
					{
					if ($user->age >= 40)
						{
						++$PARMS{'male_prostate_good'} if( $user->rectal_male eq  LESS_THAN_A_YEAR ||
											$user->rectal_male eq  ONE_YEAR_AGO );
						++$PARMS{'male_prostate_med'}  if( $user->rectal_male eq TWO_YEARS_AGO );
						++$PARMS{'male_prostate_bad'}  if( $user->rectal_male eq  THREE_YEARS_AGO ||
											$user->rectal_male eq  NEVER );
						}
					}
				else
					{
					if ($user->age >= 50)
						{
						++$PARMS{'mammo_good'} if( $user->mammogram_flag <  2 );
						++$PARMS{'mammo_med'}  if( $user->mammogram_flag == 2 );
						++$PARMS{'mammo_bad'}  if( $user->mammogram_flag >  2 );
						}
					++$PARMS{'pap_good'}  if( $user->pap_flag <   2 );
					++$PARMS{'pap_med'}   if( $user->pap_flag ==  2 );
					++$PARMS{'pap_bad'}   if( $user->pap_flag >   2 );
					}
				$high = 0;
				$medium = 0;
				$moderate = 0;
				$high_cnt=0;
				$medium_cnt=0;
				$moderate_cnt=0;
				$low_cnt=0;
				$ach_high = 0;
				$ach_medium = 0;
				$ach_moderate = 0;
				$ach_high_cnt=0;
				$ach_medium_cnt=0;
				$ach_moderate_cnt=0;
				$ach_low_cnt=0;

				$risks = $user->risk_data;
				for(my $i = 1; $i <= 43; $i++)
					{
					$hash = $risks->record( $i );
					$riskFactor = $hash->{user_risk};
					$riskAvg = $hash->{average_risk};
					$riskDesc = $hash->{name};
					$riskAch = $hash->{achievable_risk};
					++$GROUP{$riskDesc} if ($riskFactor > $riskAvg);
					if($riskFactor/3 > $riskAvg)
						{
						++$high;
						$high_cnt=1;
						$medium_cnt=0;
						$moderate_cnt=0;
						$low_cnt=0;
						}
					elsif($riskFactor/2 > $riskAvg && $high_cnt == 0)
						{
						++$medium;
						$medium_cnt=1;
						$moderate_cnt=0;
						$low_cnt=0;
						}
					elsif($riskFactor > $riskAvg && $high_cnt==0 && $medium_cnt==0)
						{
						$moderate_cnt=1;
						++$moderate;
						$low_cnt=0;
						}
					elsif($high_cnt==0 && $medium_cnt==0 && $moderate_cnt==0)
						{
						$low_cnt=1;
						}
					if($riskAch/3 > $riskAvg)
						{
						++$ach_high;
						$ach_high_cnt=1;
						$ach_medium_cnt=0;
						$ach_moderate_cnt=0;
						$ach_low_cnt=0;
						}
					elsif($riskAch/2 > $riskAvg && $ach_high_cnt == 0)
						{
						++$ach_medium;
						$ach_medium_cnt=1;
						$ach_moderate_cnt=0;
						$ach_low_cnt=0;
						}
					elsif($riskAch > $riskAvg && $ach_high_cnt==0 && $ach_medium_cnt==0)
						{
						$ach_moderate_cnt=1;
						++$ach_moderate;
						$ach_low_cnt=0;
						}
					elsif($ach_high_cnt==0 && $ach_medium_cnt==0 && $ach_moderate_cnt==0)
						{
						$ach_low_cnt=1;
						}
					}
				if ($high_cnt)
					{
					++$PARMS{'high'} ;
					$PARMS{'high_cnt'} += $high;
					}
				elsif($medium_cnt)
					{
					++$PARMS{'medium'};
					$PARMS{'medium_cnt'} += $medium;
					}
				elsif ($moderate_cnt)
					{
					++$PARMS{'moderate'};
					$PARMS{'moderate_cnt'} += $moderate;
					}
				elsif ($low_cnt)
					{
					++$PARMS{'low'};
					}
				if ($ach_high_cnt)
					{
					++$PARMS{'ach_high'} ;
					$PARMS{'ach_high_cnt'} += $ach_high;
					}
				elsif($ach_medium_cnt)
					{
					++$PARMS{'ach_medium'};
					$PARMS{'ach_medium_cnt'} += $ach_medium;
					}
				elsif ($ach_moderate_cnt)
					{
					++$PARMS{'ach_moderate'};
					$PARMS{'ach_moderate_cnt'} += $ach_moderate;
					}
				elsif ($ach_low_cnt)
					{
					++$PARMS{'ach_low'};
					}
				}
			}
		}
	$db->finish;
	$db->disconnect;

	undef (%{$user_list_ref});
	undef (%user_list);

	$PARMS{'cnt'} = $cnt;
	$hra_cnt = $PARMS{HRA_cnt} + $PARMS{GHA_cnt};

	my @assessment_count;
	my $max_value = 0;

	foreach (@assessments)
		{
		my $t = $_ . '_cnt';
		print "$assessment_names{$_} = $PARMS{$t}<br>";
		push (@assessment_count, $PARMS{$t});
		$max_value = $PARMS{$t} + 100 if ($max_value < ($PARMS{$t} + 100));
		}

	print "<p>preparing graphs<br>";
	my $graph_cnt = 0;

	if ($input->param('pgraphs') eq 'all' || $input->param('print_totalassessments') == 1){
		++$graph_cnt;
		print "$graph_cnt, ";
		#### Total Assessments Taken  #######
		$b_graph = GD::Graph::bars->new(400,230);
		$o_file = $GGR_PAGE_DIR . "ggr_ta.png";

		@g_data=(
			$assessments_ref, \@assessment_count
			);
#			[ $PARMS{HRA}, $PARMS{GHA}, $PARMS{CRC}, $PARMS{DRC}, $PARMS{FIT}, $PARMS{GWB} ]
		$b_graph->set(
				interlaced 	=> undef,
				bgclr 		=> 'white',
				transparent 	=> undef,
				x_label         => 'Assessments',
				y_label         => 'Number taken',
				title           => 'Number of Assessments Taken',
				cumulate 	=> 1,
				show_values     => 1,
				y_max_value     => $max_value,
				y_tick_number   => 8,
				y_label_skip    => 2,
				y_number_format => '%d',
				long_ticks	=> 0,
				cycle_clrs 	=> 1,
				dclrs 		=> [ qw(green lyellow lred) ],
				borderclrs 	=> [ qw(black black black) ],
				bar_spacing 	=> 15
				);
				$b_graph->set_title_font("$font_dir/arial.ttf", 14);
				$b_graph->set_x_label_font("$font_dir/arial.ttf", 10);
				$b_graph->set_y_label_font("$font_dir/arial.ttf", 10);
				$b_graph->set_x_axis_font("$font_dir/arial.ttf", 8);
				$b_graph->set_y_axis_font("$font_dir/arial.ttf", 8);
				$b_graph->set_legend_font("$font_dir/arial.ttf", 9);

		$gd_graph = $b_graph->plot(\@g_data);

		if ( $gd_graph ) {
			open(IMG, ">$o_file") or die "$! - $o_file";
			binmode IMG;
			print IMG $gd_graph->png;
			close IMG;
			}
		else 	{
			copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
			}
		}
		if ($input->param('pgraphs') eq 'all' || $input->param('print_achievable') == 1){
		++$graph_cnt;
		print "$graph_cnt, ";
		### Achievable Group levels
		$b1_graph = GD::Graph::pie->new(320,320)
			or die GD::Graph->error;

		$o_file = $GGR_PAGE_DIR . "ggr_risks_ach.png";

		my ($alparm, $amparm, $ahparm, $avparm, $albasis);
		$albasis = $PARMS{'ach_low'} + $PARMS{'ach_moderate'} + $PARMS{'ach_medium'} + $PARMS{'ach_high'};
		if( $albasis )
			{
			$alparm = sprintf("%.1f",($PARMS{'ach_low'}/$albasis * 100));
			$amparm = sprintf("%.1f",($PARMS{'ach_moderate'}/$albasis * 100));
			$ahparm = sprintf("%.1f",($PARMS{'ach_medium'}/$albasis * 100));
			$avparm = sprintf("%.1f",($PARMS{'ach_high'}/$albasis * 100));

			@g1_data = (
				["Low Risk - $alparm%", "Moderate Risk - $amparm%", "High Risk - $ahparm%", "Very High - $avparm%"],
				[ $alparm, $amparm, $ahparm, $avparm]
				);

			$b1_graph->set(
					interlaced 	=> undef,
					bgclr 		=> 'white',
					transparent 	=> undef,
					label 		=> 'Participants achievable risk levels',
					axislabelclr 	=> 'black',
					pie_height 	=> 18,
					show_values 	=> 1,
					title           => 'Achievable Group Risk',
					legend_placement=> 'RT',
					l_margin 	=> 10,
					r_margin 	=> 10,
					shadow_depth 	=> 6,
					dclrs 		=> [ qw(green lgreen lyellow lred) ],
					start_angle 	=> -85,
					);
					$b1_graph->set_title_font("$font_dir/arial.ttf", 14);
					$b1_graph->set_value_font("$font_dir/arial.ttf", 8);
					$b1_graph->set_label_font("$font_dir/arial.ttf", 8);

			$gd_graph = $b1_graph->plot(\@g1_data);

			if ( $gd_graph ) {
				open(IMG, ">$o_file") or die "$! - $o_file";

				binmode IMG;

				print IMG $gd_graph->png;

				close IMG;
				}
			else 	{
				copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
				}
			}
		else 	{
			copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
			}

		}
		if ($input->param('pgraphs') eq 'all' || $input->param('print_preventable') == 1){
		++$graph_cnt;
		print "$graph_cnt, ";
		##### Preventable deaths by disease
		$b2_graph = GD::Graph::pie->new(320,320);

		$o_file = $GGR_PAGE_DIR . "ggr_disease.png";

		if( $hra_cnt )
			{
	#			[(int($GROUP{'Throat Cancer Mortality'}/$hra_cnt * 100)),(int($GROUP{'Flu/Pneumonia Mortality'}/$hra_cnt * 100)),(int($GROUP{'Liver Mortality'}/$hra_cnt * 100)),(int($GROUP{'Lung Cancer Mortality'}/$hra_cnt * 100)),(int($GROUP{'Kidney Failure Mortality'}/$hra_cnt * 100)),(int($GROUP{'Esophageal Cancer Mortality'}/$hra_cnt * 100)),(int($GROUP{'Pancreatic Cancer Mortality'}/$hra_cnt * 100)),(int($GROUP{'Uterine Cancer Mortality'}/$hra_cnt * 100)),(int($GROUP{'Emphysema Mortality'}/$hra_cnt * 100)),(int($GROUP{'Laryngeal Cancer Mortality'}/$hra_cnt * 100)),(int($GROUP{'Heart Attack Mortality'}/$hra_cnt * 100)),(int($GROUP{'Breast Cancer Mortality'}/$hra_cnt * 100)),(int($GROUP{'Diabetes Mellitus Mortality'}/$hra_cnt * 100)),(int($GROUP{'Motor Vehicle Mortality'}/$hra_cnt * 100)),(int($GROUP{'Cervical Cancer Mortality'}/$hra_cnt * 100)),(int($GROUP{'Stroke Mortality'}/$hra_cnt * 100)),(int($GROUP{'Mouth Cancer Mortality'}/$hra_cnt * 100)),(int($GROUP{'Bladder Cancer Mortality'}/$hra_cnt * 100)),(int($GROUP{'Peptic Ulcer Mortality'}/$hra_cnt * 100))]
			@g2_data=(
				['Throat Cancer',                                   'Flu/Pneumonia',                                    'Liver',                                        'Lung Cancer',                                     'Kidney Failure',                                 'Esophageal Cancer',                            'Pancreatic Cancer',                                       'Uterine Cancer',                                   'Emphysema',                           'Laryngeal Cancer',                                           'Heart Attack',                               'Breast Cancer',                                      'Diabetes Mellitus',                              'Motor Vehicle',                                     'Cervical Cancer',                                    'Stroke',                                'Mouth Cancer',                                 'Bladder Cancer',                                   'Peptic Ulcer'],
				[(int($GROUP{'Throat Cancer'}/$hra_cnt * 100)),(int($GROUP{'Flu/Pneumonia'}/$hra_cnt * 100)),(int($GROUP{'Liver Cirrhosis'}/$hra_cnt * 100)),(int($GROUP{'Lung Cancer'}/$hra_cnt * 100)),(int($GROUP{'Kidney Failure'}/$hra_cnt * 100)),(int($GROUP{'Esophageal Cancer'}/$hra_cnt * 100)),(int($GROUP{'Pancreatic Cancer'}/$hra_cnt * 100)),(int($GROUP{'Uterine Cancer'}/$hra_cnt * 100)),(int($GROUP{'Emphysema'}/$hra_cnt * 100)),(int($GROUP{'Laryngeal Cancer'}/$hra_cnt * 100)),(int($GROUP{'Heart Attack'}/$hra_cnt * 100)),(int($GROUP{'Breast Cancer'}/$hra_cnt * 100)),(int($GROUP{'Diabetes Mellitus'}/$hra_cnt * 100)),(int($GROUP{'Motor Vehicle'}/$hra_cnt * 100)),(int($GROUP{'Cervical Cancer'}/$hra_cnt * 100)),(int($GROUP{'Stroke'}/$hra_cnt * 100)),(int($GROUP{'Mouth Cancer'}/$hra_cnt * 100)),(int($GROUP{'Bladder Cancer'}/$hra_cnt * 100)),(int($GROUP{'Peptic Ulcer'}/$hra_cnt * 100))]
				);
			my $printme = 0;
			foreach (keys %GROUP){
				if(int($GROUP{$_}/$hra_cnt * 100)){ ++$printme }
				}
			$b2_graph->set(
					interlaced 	=> undef,
					bgclr 		=> 'white',
					transparent 	=> undef,
					label 		=> 'Elevated risk within group',
					axislabelclr 	=> 'black',
					pie_height 	=> 18,
					show_values 	=> 1,
					title           => 'Preventable Deaths by Disease',
					legend_placement=> 'RT',
					l_margin 	=> 10,
					r_margin 	=> 10,
					shadow_depth 	=> 6,
					dclrs 		=> [ qw(lyellow lblue red lgreen marine white green lred cyan yellow lgray orange lbrown pink lorange purple cyan yellow lgray) ],
					start_angle 	=> 75,
					);
					$b2_graph->set_title_font("$font_dir/arial.ttf", 14);
					$b2_graph->set_value_font("$font_dir/arial.ttf", 8);
					$b2_graph->set_label_font("$font_dir/arial.ttf", 8);

			$gd_graph = $b2_graph->plot(\@g2_data);

			if ( $gd_graph ) {
				open(IMG, ">$o_file") or die "$! - $o_file";

				binmode IMG;

				print IMG $gd_graph->png;

				close IMG;
				}
			else 	{
				copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
				}
			}
		else 	{
			copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
			}


		}
		if ($input->param('pgraphs') eq 'all' || $input->param('print_riskfactors') == 1){
		++$graph_cnt;
		print "$graph_cnt, ";
		####  Risk Factors
		$b3_graph = GD::Graph::pie->new(320,320);

		$o_file = $GGR_PAGE_DIR . "ggr_factors.png";

		if (my $be_basis = $PARMS{'exer_none'}+$PARMS{'sm_still'}+$PARMS{'HDL_low'}+$PARMS{'chol_high'}+$PARMS{'alc_high'}+$PARMS{'bp_high'}+$PARMS{'sb_speed'}+$PARMS{'sb_some'}+$PARMS{'sb_never'}+$PARMS{'mammo_bad'}+$PARMS{'pap_bad'}+$PARMS{'wt_obese'})
			{
			@g3_data = (
				['Lack of Exercise', 'Smoking', 'Low HDL', 'High Cholesterol', 'Alcohol Use', 'High Blood Pressure', 'Speeding', 'Seat Belt Use', 'Mammograms', 'Pelvic Exams', 'Weight'],
				[(int($PARMS{'exer_none'}/$be_basis*100)),(int($PARMS{'sm_still'}/$be_basis*100)),(int($PARMS{'HDL_low'}/$be_basis*100)),(int($PARMS{'chol_high'}/$be_basis*100)),(int($PARMS{'alc_high'}/$be_basis*100)),(int($PARMS{'sb_speed'}/$be_basis*100)),(int(($PARMS{'sb_some'}+$PARMS{'sb_never'})/$be_basis*100)),(int($PARMS{'mammo_bad'}/$be_basis*100)),(int($PARMS{'pap_bad'}/$be_basis*100)),(int($PARMS{'wt_obese'}/$be_basis*100))]
				);

			$b3_graph->set(
					interlaced 	=> undef,
					bgclr 		=> 'white',
					transparent 	=> undef,
					label 		=> 'Modifiable behaviors',
					axislabelclr 	=> 'black',
					pie_height 	=> 18,
					show_values 	=> 1,
					title           => 'Group Contributing Risk Factors',
					legend_placement=> 'RT',
					l_margin 	=> 10,
					r_margin 	=> 10,
					shadow_depth 	=> 6,
					dclrs 		=> [ qw(green lgray red lgreen marine white lyellow lred yellow lpurple orange ) ],
					start_angle 	=> -11,
					);
					$b3_graph->set_title_font("$font_dir/arial.ttf", 14);
					$b3_graph->set_value_font("$font_dir/arial.ttf", 8);
					$b3_graph->set_label_font("$font_dir/arial.ttf", 8);

			$gd_graph = $b3_graph->plot(\@g3_data);

			if ( $gd_graph ) {
				open(IMG, ">$o_file") or die "$! - $o_file";

				binmode IMG;

				print IMG $gd_graph->png;

				close IMG;
				}
			else 	{
				copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
				}
			}
		else 	{
			copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
			}


		}
		if ($input->param('pgraphs') eq 'all' || $input->param('print_risklevels') == 1){
		++$graph_cnt;
		print "$graph_cnt, ";
		$b4_graph = GD::Graph::pie->new(321,321);

		$o_file = $GGR_PAGE_DIR . "ggr_risks.png";

		my ($lparm, $mparm, $hparm, $vparm, $b4_basis);
		$b4_basis = $PARMS{'low'} + $PARMS{'moderate'} + $PARMS{'medium'} + $PARMS{'high'};
		if( $b4_basis )
			{
			$lparm = (int($PARMS{'low'}/$b4_basis * 100));
			$mparm = (int($PARMS{'moderate'}/$b4_basis * 100));
			$hparm = (int($PARMS{'medium'}/$b4_basis * 100));
			$vparm = (int($PARMS{'high'}/$b4_basis * 100));

			if ($hparm > 33 || $vparm > 33 || $vparm+$hparm > 50)
				{
				$PARMS{'group_msg'}='Your group is at higher risk levels than average.  It is important that you work to educate the participants of their elevated risks and how to bring them down to a more desireable level';
				}
			else
				{
				$PARMS{'group_msg'}='Your group is doing well in controlling risks.  Continue to provide opportunities for those in the high risk and very high risk groups to reduce risky behaviors.';
				}

			@g4_data = (
				["Low Risk - $lparm%", "Moderate Risk - $mparm%", "High Risk - $hparm%", "Very High Risk - $vparm%"],
				[$lparm,$mparm,$hparm,$vparm]
				);

			$b4_graph->set(
					interlaced 	=> undef,
					bgclr 		=> 'white',
					transparent 	=> undef,
					label 		=> 'Current health risk levels',
					axislabelclr 	=> 'black',
					pie_height 	=> 18,
					show_values 	=> 1,
					title           => 'Group Health Risk',
					legend_placement=> 'RT',
					l_margin 	=> 10,
					r_margin 	=> 10,
					shadow_depth 	=> 6,
					dclrs 		=> [ qw(green lgreen lyellow lred) ],
					start_angle 	=> -85,
					);
					$b4_graph->set_title_font("$font_dir/arial.ttf", 14);
					$b4_graph->set_value_font("$font_dir/arial.ttf", 8);
					$b4_graph->set_label_font("$font_dir/arial.ttf", 8);

			$gd_graph = $b4_graph->plot(\@g4_data);

			if ( $gd_graph ) {
				open(IMG, ">$o_file") or die "$! - $o_file";

				binmode IMG;

				print IMG $gd_graph->png;

				close IMG;
				}
			else 	{
				copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
				}
			}
		else 	{
			copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
			}


		}
		if ($input->param('pgraphs') eq 'all' || $input->param('print_agegroups') == 1){
		++$graph_cnt;
		print "$graph_cnt, ";
		####  Age Range by sex
		$b5_graph = GD::Graph::mixed->new(430, 200);

		$o_file = $GGR_PAGE_DIR . "ggr_age.png";

		if(my $age_basis = ($PARMS{'m_lt_19'}+$PARMS{'m_20_29'}+$PARMS{'m_30_39'}+$PARMS{'m_40_49'}+$PARMS{'m_50_59'}+$PARMS{'m_60'}+$PARMS{'f_lt_19'}+$PARMS{'f_20_29'}+$PARMS{'f_30_39'}+$PARMS{'f_40_49'}+$PARMS{'f_50_59'}+$PARMS{'f_60'}))
			{
			@g5_data = (
			    ["<19",                                           "20-29",                                 "30-39",                            "40-49",                                          "50-59",                          "60+"],
			    [(int($PARMS{'m_lt_19'}/$age_basis*100)), (int($PARMS{'m_20_29'}/$age_basis*100)), (int($PARMS{'m_30_39'}/$age_basis*100)), (int($PARMS{'m_40_49'}/$age_basis*100)), (int($PARMS{'m_50_59'}/$age_basis*100)), (int($PARMS{'m_60'}/$age_basis*100))],
			    [(int($PARMS{'f_lt_19'}/$age_basis*100)), (int($PARMS{'f_20_29'}/$age_basis*100)), (int($PARMS{'f_30_39'}/$age_basis*100)), (int($PARMS{'f_40_49'}/$age_basis*100)), (int($PARMS{'f_50_59'}/$age_basis*100)), (int($PARMS{'f_60'}/$age_basis*100))]
			  );
			$b5_graph->set(
					interlaced 	=> undef,
					bgclr 		=> 'white',
					transparent 	=> undef,
					x_label 	=> 'Age groups',
					y_label 	=> '% Participants',
					title 		=> 'Sex by Age Group',
					cumulate 	=> 1,
					y_max_value  	=> 100,
					y_tick_number   => 10,
					y_label_skip    => 2,
					y_number_format => '%d',
					types 		=> [qw(bars bars)],
					show_values     => 0,
					legend_placement=> 'RT',
					dclrs 		=> [ qw(lblue pink lyellow lblue red lgreen marine white green lred cyan yellow lgray orange lbrown pink lorange purple cyan yellow lgray) ],
					borderclrs 	=> [ qw(black black) ],
					bar_spacing 	=> 15
					);
					$b5_graph->set_legend( 'Males', 'Females' );
					$b5_graph->set_title_font("$font_dir/arial.ttf", 14);
					$b5_graph->set_x_label_font("$font_dir/arial.ttf", 10);
					$b5_graph->set_y_label_font("$font_dir/arial.ttf", 10);
					$b5_graph->set_x_axis_font("$font_dir/arial.ttf", 8);
					$b5_graph->set_y_axis_font("$font_dir/arial.ttf", 8);
					$b5_graph->set_legend_font("$font_dir/arial.ttf", 9);

			$gd_graph = $b5_graph->plot(\@g5_data);

			if ( $gd_graph ) {
				open(IMG, ">$o_file") or die "$! - $o_file";

				binmode IMG;

				print IMG $gd_graph->png;

				close IMG;
				}
			else 	{
				copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
				}
			}
		else 	{
			copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
			}

		}
		if ($input->param('pgraphs') eq 'all' || $input->param('print_smoking') == 1){
		++$graph_cnt;
		print "$graph_cnt, ";
		#### Smoking Habits
		$b6_graph = GD::Graph::bars->new(400,230);

		$o_file = $GGR_PAGE_DIR . "ggr_sm.png";

		my ($sm_never, $sm_quit, $sm_still, $sm_basis);

		if($sm_basis= ($PARMS{'sm_never'}+$PARMS{'sm_quit'}+$PARMS{'sm_still'}))
			{
			$sm_never=sprintf("%.2f",($PARMS{'sm_never'}/$sm_basis*100));
			$sm_quit=sprintf("%.2f",($PARMS{'sm_quit'}/$sm_basis*100));
			$sm_still=sprintf("%.2f",($PARMS{'sm_still'}/$sm_basis*100));

			if ($sm_still > 26) 	{ $PARMS{smoke_msg} = 'This group has smoking habits higher than the national average of 24% smokers.' }
			elsif ($sm_still < 22)	{ $PARMS{smoke_msg} = 'This group has smoking habits less than the national average of 24% smokers.' }
			else			{ $PARMS{smoke_msg} = 'This group has smoking habits about the sames as the national average of 24% smokers.' }

			@g6_data=(
				["Non-smokers", "Ex-smokers", "Smokers"],
				[ $sm_never,       $sm_quit,   $sm_still]
				);

			$b6_graph->set(
					interlaced 	=> undef,
					bgclr 		=> 'white',
					transparent 	=> undef,
					x_label         => 'Smoking status',
					y_label         => '% of Participants',
					title           => 'Group Smoking Habits',
					cumulate 	=> 1,
					show_values     => 1,
					y_max_value     => 100,
					y_tick_number   => 20,
					y_label_skip    => 4,
					y_number_format => '%d',
					long_ticks	=> 0,
					cycle_clrs 	=> 1,
					dclrs 		=> [ qw(green lyellow lred) ],
					borderclrs 	=> [ qw(black black black) ],
					bar_spacing 	=> 15
					);
					$b6_graph->set_title_font("$font_dir/arial.ttf", 14);
					$b6_graph->set_x_label_font("$font_dir/arial.ttf", 10);
					$b6_graph->set_y_label_font("$font_dir/arial.ttf", 10);
					$b6_graph->set_x_axis_font("$font_dir/arial.ttf", 8);
					$b6_graph->set_y_axis_font("$font_dir/arial.ttf", 8);
					$b6_graph->set_legend_font("$font_dir/arial.ttf", 9);

			$gd_graph = $b6_graph->plot(\@g6_data);

			if ( $gd_graph ) {
				open(IMG, ">$o_file") or die "$! - $o_file";

				binmode IMG;

				print IMG $gd_graph->png;

				close IMG;
				}
			else 	{
				copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
				}
			}
		else 	{
			copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
			}

		}
		if ($input->param('pgraphs') eq 'all' || $input->param('print_alcohol') == 1){
		++$graph_cnt;
		print "$graph_cnt, ";
		#### Alcohol Habits
		$b7_graph = GD::Graph::bars->new(400,230);

		$o_file = $GGR_PAGE_DIR . "ggr_alc.png";

		my ($alc_good, $alc_over, $alc_obese, $alc_basis);

		if($alc_basis = $PARMS{'alc_low'} + $PARMS{'alc_medium'} + $PARMS{'alc_high'})
			{
			$alc_good = sprintf("%.2f",($PARMS{'alc_low'}/$alc_basis*100));
			$alc_over = sprintf("%.2f",($PARMS{'alc_medium'}/$alc_basis*100));
			$alc_obese = sprintf("%.2f",($PARMS{'alc_high'}/$alc_basis*100));

			if ($alc_obese + $alc_over > 8 ) 	{ $PARMS{alcohol_msg} = 'This group has more moderate and heavy drinkers than the US average.' }
			else 					{ $PARMS{alcohol_msg} = 'This group has fewer moderate and heavy drinkers than the US average.' }

			if ($PARMS{'sb_drinkdrive'}) 	{ $PARMS{alcohol_msg} .= "  Of this group, $PARMS{'sb_drinkdrive'} participants reported either drinking and driving or riding with someone who had too much to drink in the last month." }

			@g7_data = (
				["Low", "Moderate", "High"],
				[$alc_good ,            $alc_over ,     $alc_obese]
				);

			$b7_graph->set(
					interlaced 	=> undef,
					bgclr 		=> 'white',
					transparent 	=> undef,
					x_label         => 'Group Alcohol Use',
					y_label         => '% of Participants',
					title           => 'Drinks in a Week',
					cumulate 	=> 1,
					show_values     => 1,
					y_max_value     => 100,
					y_tick_number   => 20,
					y_label_skip    => 4,
					y_number_format => '%d',
					long_ticks	=> 0,
					cycle_clrs 	=> 1,
					dclrs 		=> [ qw(green lyellow lred lyellow lblue red lgreen marine white green lred cyan yellow lgray orange lbrown pink lorange purple cyan yellow lgray) ],
					borderclrs 	=> [ qw(black black black) ],
					bar_spacing 	=> 15
					);
					$b7_graph->set_title_font("$font_dir/arial.ttf", 14);
					$b7_graph->set_x_label_font("$font_dir/arial.ttf", 10);
					$b7_graph->set_y_label_font("$font_dir/arial.ttf", 10);
					$b7_graph->set_x_axis_font("$font_dir/arial.ttf", 8);
					$b7_graph->set_y_axis_font("$font_dir/arial.ttf", 8);
					$b7_graph->set_legend_font("$font_dir/arial.ttf", 9);

			$gd_graph = $b7_graph->plot(\@g7_data);

			if ( $gd_graph ) {
				open(IMG, ">$o_file") or die "$! - $o_file";

				binmode IMG;

				print IMG $gd_graph->png;

				close IMG;
				}
			else 	{
				copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
				}
			}
		else 	{
			copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
			}

		}
		if ($input->param('pgraphs') eq 'all' || $input->param('print_weight') == 1){
		++$graph_cnt;
		print "$graph_cnt, ";
		####  Weight Status
		$b8_graph = GD::Graph::bars->new(400,230);

		$o_file = $GGR_PAGE_DIR . "ggr_wt.png";

		my ($wt_good, $wt_under, $wt_over, $wt_obese, $wt_basis);

		if($wt_basis = $PARMS{'wt_under'} + $PARMS{'wt_good'} + $PARMS{'wt_over'} + $PARMS{'wt_obese'})
			{
			$wt_under = sprintf("%.2f",($PARMS{'wt_under'}/$wt_basis*100));
			$wt_good = sprintf("%.2f",($PARMS{'wt_good'}/$wt_basis*100));
			$wt_over = sprintf("%.2f",($PARMS{'wt_over'}/$wt_basis*100));
			$wt_obese = sprintf("%.2f",($PARMS{'wt_obese'}/$wt_basis*100));

			if ($wt_obese >= 20 ||
				$wt_obese + $wt_over >= 40)	{ $PARMS{wt_msg} = "There is a large percentage of participants above their healthy weight." }
			else					{ $PARMS{wt_msg} = "This group is doing a good job maintaining proper weight." }

			@g8_data = (
				["Under Weight", "Proper Weight", "Overweight", "Obese"],
				[$wt_under,         $wt_good ,     $wt_over ,   $wt_obese]
				);
			$b8_graph->set(
					interlaced 	=> undef,
					bgclr 		=> 'white',
					transparent 	=> undef,
					x_label         => 'Weight classification',
					y_label         => '% of Participants',
					title           => 'Group Weight',
					cumulate 	=> 1,
					show_values     => 1,
					y_max_value     => 100,
					y_tick_number   => 20,
					y_label_skip    => 4,
					y_number_format => '%d',
					long_ticks	=> 0,
					cycle_clrs 	=> 1,
					dclrs 		=> [ qw(lyellow green lyellow lred) ],
					borderclrs 	=> [ qw(black black black) ],
					bar_spacing 	=> 15
					);
					$b8_graph->set_title_font("$font_dir/arial.ttf", 14);
					$b8_graph->set_x_label_font("$font_dir/arial.ttf", 10);
					$b8_graph->set_y_label_font("$font_dir/arial.ttf", 10);
					$b8_graph->set_x_axis_font("$font_dir/arial.ttf", 8);
					$b8_graph->set_y_axis_font("$font_dir/arial.ttf", 8);
					$b8_graph->set_legend_font("$font_dir/arial.ttf", 9);

			$gd_graph = $b8_graph->plot(\@g8_data);

			if ( $gd_graph ) {
				open(IMG, ">$o_file") or die "$! - $o_file";

				binmode IMG;

				print IMG $gd_graph->png;

				close IMG;
				}
			else 	{
				copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
				}
			}
		else 	{
			copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
			}


		}
		if ($input->param('pgraphs') eq 'all' || $input->param('print_mammogram') == 1){
		++$graph_cnt;
		print "$graph_cnt, ";
		####  Mammogram
		$b9_graph = GD::Graph::bars->new(400,230);

		$o_file = $GGR_PAGE_DIR . "ggr_mammo.png";

		my ($mammo_good, $mammo_med, $mammo_bad, $mammo_basis);

		if($mammo_basis = $PARMS{'mammo_good'} + $PARMS{'mammo_med'} + $PARMS{'mammo_bad'})
			{
			$mammo_good = sprintf("%.2f",($PARMS{'mammo_good'}/$mammo_basis*100));
			$mammo_med = sprintf("%.2f",($PARMS{'mammo_med'}/$mammo_basis*100));
			$mammo_bad = sprintf("%.2f",($PARMS{'mammo_bad'}/$mammo_basis*100));

			if ($mammo_bad + $mammo_med > 10)	{ $PARMS{mammo_msg} = "There are a high number of participants that have not had a screening recently." }
			else					{ $PARMS{mammo_msg} = "This group is doing well in getting recommended screenings." }

			@g9_data = (
				["1 year or less", "1 to 3 years", "Over 3 years"],
				[$mammo_good ,       $mammo_med ,    $mammo_bad]
				);
			$b9_graph->set(
					interlaced 	=> undef,
					bgclr 		=> 'white',
					transparent 	=> undef,
					x_label 	=> 'Time since last mammogram',
					y_label 	=> '% of Participants',
					title 		=> 'Group Mammogram (females 50 and older)',
					cumulate 	=> 1,
					show_values 	=> 1,
					y_max_value 	=> 100,
					y_tick_number 	=> 20,
					y_label_skip 	=> 4,
					y_number_format => '%d',
					long_ticks	=> 0,
					cycle_clrs 	=> 1,
					dclrs 		=> [ qw(green lyellow lred) ],
					borderclrs 	=> [ qw(black black black) ],
					bar_spacing 	=> 15
					);
					$b9_graph->set_title_font("$font_dir/arial.ttf", 14);
					$b9_graph->set_x_label_font("$font_dir/arial.ttf", 10);
					$b9_graph->set_y_label_font("$font_dir/arial.ttf", 10);
					$b9_graph->set_x_axis_font("$font_dir/arial.ttf", 8);
					$b9_graph->set_y_axis_font("$font_dir/arial.ttf", 8);
					$b9_graph->set_legend_font("$font_dir/arial.ttf", 9);

			$gd_graph = $b9_graph->plot(\@g9_data);
			if ( $gd_graph )
				{
				open(IMG, ">$o_file") or die "$! - $o_file";

				binmode IMG;

				print IMG $gd_graph->png;

				close IMG;
				}
			else 	{
				copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
				}
			}
		else
			{
			copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
			}


		}
		if ($input->param('pgraphs') eq 'all' || $input->param('print_pap') == 1){
		++$graph_cnt;
		print "$graph_cnt, ";
		#### Pap Exams
		$b10_graph = GD::Graph::bars->new(400,230);

		$o_file = $GGR_PAGE_DIR . "ggr_pap.png";

		my ($pap_good, $pap_med, $pap_bad, $pap_basis);

		if ($pap_basis = $PARMS{'pap_good'} + $PARMS{'pap_med'} + $PARMS{'pap_bad'})
			{
			$pap_good = sprintf("%.2f",($PARMS{'pap_good'}/$pap_basis*100));
			$pap_med = sprintf("%.2f",($PARMS{'pap_med'}/$pap_basis*100));
			$pap_bad = sprintf("%.2f",($PARMS{'pap_bad'}/$pap_basis*100));

			if ($pap_bad + $pap_med > 10)	{ $PARMS{pap_msg} = "There are a high number of participants that have not had a screening recently." }
			else				{ $PARMS{pap_msg} = "This group is doing well in getting recommended screenings." }

			@g10_data = (
				["1 year or less", "1 to 3 years", "Over 3 years"],
				[$pap_good ,         $pap_med ,       $pap_bad]
				);
			$b10_graph->set(
					interlaced 	=> undef,
					bgclr 		=> 'white',
					transparent 	=> undef,
					x_label 	=> 'Time since last pap',
					y_label 	=> '% of Participants',
					title 		=> 'Group Pap Smear (all females)',
					cumulate	=> 0,
					overwrite	=> 1,
					show_values     => 1,
					y_max_value     => 100,
					y_tick_number  	=> 20,
					y_label_skip    => 4,
					y_number_format => '%d',
					long_ticks	=> 0,
					cycle_clrs 	=> 1,
					dclrs 		=> [ qw(green lyellow lred) ],
					borderclrs 	=> [ qw(black black black) ],
					bar_spacing 	=> 15
					);
					$b10_graph->set_title_font("$font_dir/arial.ttf", 14);
					$b10_graph->set_x_label_font("$font_dir/arial.ttf", 10);
					$b10_graph->set_y_label_font("$font_dir/arial.ttf", 10);
					$b10_graph->set_x_axis_font("$font_dir/arial.ttf", 8);
					$b10_graph->set_y_axis_font("$font_dir/arial.ttf", 8);
					$b10_graph->set_legend_font("$font_dir/arial.ttf", 9);

				$gd_graph = $b10_graph->plot(\@g10_data);

				if ( $gd_graph ) {
					open(IMG, ">$o_file") or die "$! - $o_file";

					binmode IMG;

					print IMG $gd_graph->png;

					close IMG;
					}
				else 	{
					copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
					}
				}
		else 	{
			copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
			}

		}
		if ($input->param('pgraphs') eq 'all' || $input->param('print_prostate') == 1){
		++$graph_cnt;
		print "$graph_cnt, ";
		####  Male Prostate
		$b11_graph = GD::Graph::bars->new(400,230);

		$o_file = $GGR_PAGE_DIR . "ggr_prostate.png";

		my ($male_good, $male_med, $male_bad, $male_prostate_basis);

		if ($male_prostate_basis = $PARMS{'male_prostate_good'} + $PARMS{'male_prostate_med'} + $PARMS{'male_prostate_bad'})
			{
			$male_good = sprintf("%.2f",($PARMS{'male_prostate_good'}/$male_prostate_basis*100));
			$male_med = sprintf("%.2f",($PARMS{'male_prostate_med'}/$male_prostate_basis*100));
			$male_bad = sprintf("%.2f",($PARMS{'male_prostate_bad'}/$male_prostate_basis*100));

				if ($male_bad + $male_med > 10)	{ $PARMS{male_msg} = "There are a high number of participants that have not had a screening recently." }
				else				{ $PARMS{male_msg} = "This group is doing well in getting recommended screenings." }

				@g11_data = (
					["1 year or less", "1 to 3 years", "Over 3 years"],
					[$male_good ,       $male_med ,    $male_bad]
					);
				$b11_graph->set(
						interlaced 	=> undef,
						bgclr 		=> 'white',
						transparent 	=> undef,
						x_label 	=> 'Time since last prostate exame',
						y_label 	=> '% of Participants',
						title 		=> 'Group Prostate Exams (males 40 and older)',
						cumulate 	=> 1,
						show_values 	=> 1,
						y_max_value 	=> 100,
						y_tick_number 	=> 20,
						y_label_skip 	=> 4,
						y_number_format => '%d',
						long_ticks	=> 0,
						cycle_clrs 	=> 1,
						dclrs 		=> [ qw(green lyellow lred) ],
						borderclrs 	=> [ qw(black black black) ],
						bar_spacing 	=> 15
						);
						$b11_graph->set_title_font("$font_dir/arial.ttf", 14);
						$b11_graph->set_x_label_font("$font_dir/arial.ttf", 10);
						$b11_graph->set_y_label_font("$font_dir/arial.ttf", 10);
						$b11_graph->set_x_axis_font("$font_dir/arial.ttf", 8);
						$b11_graph->set_y_axis_font("$font_dir/arial.ttf", 8);
						$b11_graph->set_legend_font("$font_dir/arial.ttf", 9);

				$gd_graph = $b11_graph->plot(\@g11_data);

				if ( $gd_graph ) {
					open(IMG, ">$o_file") or die "$! - $o_file";

					binmode IMG;

					print IMG $gd_graph->png;

					close IMG;
					}
				else 	{
					copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
					}
				}
			else 	{
				copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
				}

		}
		if ($input->param('pgraphs') eq 'all' || $input->param('print_exercise') == 1){
		++$graph_cnt;
		print "$graph_cnt, ";
		#### Exercise Habits
		$b12_graph = GD::Graph::bars->new(400,230);

		$o_file = $GGR_PAGE_DIR . "ggr_exer.png";

		my ($exer_basis, $exer_good, $exer_some, $exer_none);

		if($exer_basis = $PARMS{'exer_good'} + $PARMS{'exer_some'} + $PARMS{'exer_none'})
			{
			$exer_good = sprintf("%.2f",($PARMS{'exer_good'}/$exer_basis*100));
			$exer_some = sprintf("%.2f",($PARMS{'exer_some'}/$exer_basis*100));
			$exer_none = sprintf("%.2f",($PARMS{'exer_none'}/$exer_basis*100));

			@g12_data = (
				["3+/week", "1-2/week", "Sedentary"],
				[$exer_good ,$exer_some ,$exer_none]
				);
			$b12_graph->set(
					interlaced 	=> undef,
					bgclr 		=> 'white',
					transparent 	=> undef,
					x_label 	=> 'Exercise frequency',
					y_label 	=> '% of Participants',
					title 		=> 'Group Exercise Habits',
					cumulate 	=> 1,
					show_values 	=> 1,
					y_max_value  	=> 100,
					y_tick_number 	=> 20,
					y_label_skip 	=> 4,
					y_number_format => '%d',
					long_ticks	=> 0,
					cycle_clrs 	=> 1,
					dclrs 		=> [ qw(green lyellow lred) ],
					borderclrs 	=> [ qw(black black black) ],
					bar_spacing 	=> 15
					);
					$b12_graph->set_title_font("$font_dir/arial.ttf", 14);
					$b12_graph->set_x_label_font("$font_dir/arial.ttf", 10);
					$b12_graph->set_y_label_font("$font_dir/arial.ttf", 10);
					$b12_graph->set_x_axis_font("$font_dir/arial.ttf", 8);
					$b12_graph->set_y_axis_font("$font_dir/arial.ttf", 8);
					$b12_graph->set_legend_font("$font_dir/arial.ttf", 9);

			$gd_graph = $b12_graph->plot(\@g12_data);

			if ( $gd_graph ) {
				open(IMG, ">$o_file") or die "$! - $o_file";

				binmode IMG;

				print IMG $gd_graph->png;

				close IMG;
				}
			else 	{
				copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
				}
			}
		else 	{
			copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
			}

		}
		if ($input->param('pgraphs') eq 'all' || $input->param('print_seatbelts') == 1){
		++$graph_cnt;
		print "$graph_cnt, ";
		#### Seat Belt Habits
		$b13_graph = GD::Graph::bars->new(400,230);

		$o_file = $GGR_PAGE_DIR . "ggr_sb.png";

		my ($sb_basis, $sb_never, $sb_some, $sb_seldom, $sb_usually, $sb_always);

		if($sb_basis = $PARMS{'sb_never'} + $PARMS{'sb_some'} + $PARMS{'sb_seldom'} + $PARMS{'sb_usually'} + $PARMS{'sb_always'})
			{
			$sb_never = sprintf("%.2f",($PARMS{'sb_never'}/$sb_basis*100));
			$sb_some = sprintf("%.2f",($PARMS{'sb_some'}/$sb_basis*100));
			$sb_seldom = sprintf("%.2f",($PARMS{'sb_seldom'}/$sb_basis*100));
			$sb_usually = sprintf("%.2f",($PARMS{'sb_usually'}/$sb_basis*100));
			$sb_always = sprintf("%.2f",($PARMS{'sb_always'}/$sb_basis*100));

			if ($sb_usually + $sb_always >= 70)	{ $PARMS{sb_msg} = "This group of participants is doing very well in regards to seatbelt usage.  " }
			else					{ $PARMS{sb_msg} = "This group of participants needs to improve their seatbelt wearing habits.  " }

			if ($PARMS{'sb_drinkdrive'}) 		{ $PARMS{sb_msg} .= "Of this group, $PARMS{'sb_drinkdrive'} participants reported either drinking and driving or riding with someone who had too much to drink in the last month." }

			@g13_data = (
				["Always",    "81-99%",    "41-80%", "1-40%",    "Never"],
				[$sb_always ,$sb_usually ,$sb_some, $sb_seldom, $sb_never]
				);
			$b13_graph->set(
					interlaced 	=> undef,
					bgclr 		=> 'white',
					transparent 	=> undef,
					x_label   	=> '% of trips seatbelts used',
					y_label 	=> '% of Participants',
					title 		=> 'Group Seatbelt Use',
					cumulate 	=> 1,
					show_values 	=> 1,
					y_max_value  	=> 100,
					y_tick_number 	=> 20,
					y_label_skip  	=> 4,
					y_number_format => '%d',
					long_ticks	=> 0,
					cycle_clrs 	=> 1,
					dclrs 		=> [ qw(green lgreen lyellow lred red) ],
					borderclrs 	=> [ qw(black black black black black) ],
					bar_spacing 	=> 15
					);
					$b13_graph->set_title_font("$font_dir/arial.ttf", 14);
					$b13_graph->set_x_label_font("$font_dir/arial.ttf", 10);
					$b13_graph->set_y_label_font("$font_dir/arial.ttf", 10);
					$b13_graph->set_x_axis_font("$font_dir/arial.ttf", 8);
					$b13_graph->set_y_axis_font("$font_dir/arial.ttf", 8);
					$b13_graph->set_legend_font("$font_dir/arial.ttf", 9);

			$gd_graph = $b13_graph->plot(\@g13_data);

			if ( $gd_graph ) {
				open(IMG, ">$o_file") or die "$! - $o_file";

				binmode IMG;

				print IMG $gd_graph->png;

				close IMG;
				}
			else 	{
				copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
				}
			}
		else 	{
			copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
			}

		}
		if ($input->param('pgraphs') eq 'all' || $input->param('print_cholesterol') == 1){
		++$graph_cnt;
		print "$graph_cnt, ";
		##### Cholesterol Status
		$b14_graph = GD::Graph::bars->new(400,230);

		$o_file = $GGR_PAGE_DIR . "ggr_chol.png";

		my ($chol_basis, $chol_high, $chol_med, $chol_low, $chol_unknown);

		if($chol_basis = $PARMS{'chol_high'} + $PARMS{'chol_med'} + $PARMS{'chol_low'} + $PARMS{'chol_unknown'})
			{
			$chol_high = sprintf("%.2f",($PARMS{'chol_high'}/$chol_basis*100));
			$chol_med = sprintf("%.2f",($PARMS{'chol_med'}/$chol_basis*100));
			$chol_low = sprintf("%.2f",($PARMS{'chol_low'}/$chol_basis*100));
			$chol_unknown = sprintf("%.2f",($PARMS{'chol_unknown'}/$chol_basis*100));

			if ($chol_high > 21)	{ $PARMS{chol_msg} = "There are a high number of participants with cholesterol higher than recommended." }
			else			{ $PARMS{chol_msg} = "This group is below the US average for high cholesterol." }

			if ($chol_unknown > 5 ) {$PARMS{chol_msg} .= "  Screening should be done for those in this group that do not know their cholesterol."}

			my %chol_lab = (
				low	=> "Under " . CHOL_MARGINAL,
				med	=> CHOL_MARGINAL . " to " . CHOL_HIGH,
				high	=> "Over " . CHOL_HIGH
				);

			@g14_data = (
				[$chol_lab{low}, $chol_lab{med}, $chol_lab{high}, "unknown"],
				[$chol_low ,$chol_med ,$chol_high, $chol_unknown]
				);
			$b14_graph->set(
					interlaced 	=> undef,
					bgclr 		=> 'white',
					transparent 	=> undef,
					x_label 	=> 'Cholesterol levels',
					y_label 	=> '% of Participants',
					title 		=> 'Group Cholesterol',
					cumulate 	=> 1,
					show_values  	=> 1,
					y_max_value 	=> 100,
					y_tick_number 	=> 20,
					y_label_skip 	=> 4,
					y_number_format => '%d',
					long_ticks	=> 0,
					cycle_clrs 	=> 1,
					dclrs 		=> [ qw( lgreen lyellow lred red) ],
					borderclrs 	=> [ qw(black black black black) ],
					bar_spacing 	=> 15
					);
					$b14_graph->set_title_font("$font_dir/arial.ttf", 14);
					$b14_graph->set_x_label_font("$font_dir/arial.ttf", 10);
					$b14_graph->set_y_label_font("$font_dir/arial.ttf", 10);
					$b14_graph->set_x_axis_font("$font_dir/arial.ttf", 8);
					$b14_graph->set_y_axis_font("$font_dir/arial.ttf", 8);
					$b14_graph->set_legend_font("$font_dir/arial.ttf", 9);

			$gd_graph = $b14_graph->plot(\@g14_data);

			if ( $gd_graph ) {
				open(IMG, ">$o_file") or die "$! - $o_file";

				binmode IMG;

				print IMG $gd_graph->png;

				close IMG;
				}
			else 	{
				copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
			}
			}
		else 	{
			copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
			}

		}
		if ($input->param('pgraphs') eq 'all' || $input->param('print_bloodpressure') == 1){
		++$graph_cnt;
		print "$graph_cnt, ";
		#### Blood Pressure
		$b15_graph = GD::Graph::bars->new(400,230);

		$o_file = $GGR_PAGE_DIR . "ggr_bp.png";

		my ($bp_basis, $bp_high, $bp_med, $bp_low, $bp_unknown);

		if($bp_basis = $PARMS{'bp_high'} + $PARMS{'bp_med'} + $PARMS{'bp_low'} + $PARMS{'bp_unknown'})
			{
			$bp_high = sprintf("%.2f",($PARMS{'bp_high'}/$bp_basis*100));
			$bp_med = sprintf("%.2f",($PARMS{'bp_med'}/$bp_basis*100));
			$bp_low = sprintf("%.2f",($PARMS{'bp_low'}/$bp_basis*100));
			$bp_unknown = sprintf("%.2f",($PARMS{'bp_unknown'}/$bp_basis*100));

			if ($bp_med + $bp_high > 28)	{ $PARMS{bp_msg} = "There are a high number of participants with blood pressure higher than recommended.  Of these, $PARMS{bp_meds} are on medication to reduce their blood pressure." }
			else				{ $PARMS{bp_msg} = "This group is below the US average for high blood pressure." }

			if ($PARMS{bp_no_meds})		{ $PARMS{bp_msg} .= "  $PARMS{bp_no_meds} individuals in this group have high blood pressure and are not taking medicine for it." }
			if ($bp_unknown > 5 ) 		{ $PARMS{bp_msg} .= "  Screening should be done for those in this group that do not know their blood pressure." }

			my %bp_lab = (
				low	=> "Under " . BP_MARGINAL_SYSTOLIC . "/" . BP_MARGINAL_DIASTOLIC,
				med	=> BP_MARGINAL_SYSTOLIC . "/" . BP_MARGINAL_DIASTOLIC . " to " . BP_HIGH_SYSTOLIC . "/" . BP_HIGH_DIASTOLIC,
				high	=> "Over " . BP_HIGH_SYSTOLIC . "/" . BP_HIGH_DIASTOLIC
				);

			@g15_data = (
				[$bp_lab{low}, $bp_lab{med}, $bp_lab{high}, "unknown"],
				[$bp_low ,$bp_med ,$bp_high, $bp_unknown]
				);
			$b15_graph->set(
					interlaced 	=> undef,
					bgclr 		=> 'white',
					transparent 	=> undef,
					x_label  	=> 'Blood pressure levels',
					y_label 	=> '% of Participants',
					title  		=> 'Group Blood Pressure',
					cumulate 	=> 1,
					show_values 	=> 1,
					y_max_value  	=> 100,
					y_tick_number 	=> 20,
					y_label_skip    => 4,
					y_number_format => '%d',
					long_ticks	=> 0,
					cycle_clrs 	=> 1,
					dclrs 		=> [ qw( lgreen lyellow lred red) ],
					borderclrs 	=> [ qw(black black black black) ],
					bar_spacing 	=> 15
					);
					$b15_graph->set_title_font("$font_dir/arial.ttf", 14);
					$b15_graph->set_x_label_font("$font_dir/arial.ttf", 10);
					$b15_graph->set_y_label_font("$font_dir/arial.ttf", 10);
					$b15_graph->set_x_axis_font("$font_dir/arial.ttf", 8);
					$b15_graph->set_y_axis_font("$font_dir/arial.ttf", 8);
					$b15_graph->set_legend_font("$font_dir/arial.ttf", 9);

			$gd_graph = $b15_graph->plot(\@g15_data);

			if ( $gd_graph ) {
				open(IMG, ">$o_file") or die "$! - $o_file";

				binmode IMG;

				print IMG $gd_graph->png;

				close IMG;
				}
			else 	{
				copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
				}
			}
		else 	{
			copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
			}

		}
		if ($input->param('pgraphs') eq 'all' || $input->param('print_diabetes') == 1){
		++$graph_cnt;
		print "$graph_cnt, ";
		####  Diabetes Assessment Risk levels
		$b16_graph = GD::Graph::pie->new(321,321);

		$o_file = $GGR_PAGE_DIR . "ggr_diabrisks.png";

		my ($dlparm, $dmparm, $dhparm, $b16_basis);

		$b16_basis = $PARMS{diabetes_low} + $PARMS{diabetes_med} + $PARMS{diabetes_high};

		if ( $b16_basis )
			{
			$dlparm = sprintf("%.2f",($PARMS{diabetes_low}/$b16_basis * 100));
			$dmparm = sprintf("%.2f",($PARMS{diabetes_med}/$b16_basis * 100));
			$dhparm = sprintf("%.2f",($PARMS{diabetes_high}/$b16_basis * 100));

			@g16_data = (
				["Low Risk - $dlparm%", "Moderate Risk - $dmparm%", "High Risk - $dhparm%"],
				[$dlparm,                  $dmparm,                       $dhparm]
				);

			$b16_graph->set(
					interlaced 	=> undef,
					bgclr 		=> 'white',
					transparent 	=> undef,
					title 		=> 'Diabetes Assessment Results',
					axislabelclr 	=> 'black',
					pie_height 	=> 18,
					show_values 	=> 1,
					label           => 'Group Risk Levels',
					legend_placement=> 'RT',
					l_margin 	=> 10,
					r_margin 	=> 10,
					shadow_depth 	=> 6,
					dclrs 		=> [ qw(green lyellow lred) ],
					start_angle 	=> -85,
					);
					$b16_graph->set_title_font("$font_dir/arial.ttf", 14);
					$b16_graph->set_value_font("$font_dir/arial.ttf", 8);
					$b16_graph->set_label_font("$font_dir/arial.ttf", 8);

			$gd_graph = $b16_graph->plot(\@g16_data);

			if ( $gd_graph ) {
				open(IMG, ">$o_file") or die "$! - $o_file";

				binmode IMG;

				print IMG $gd_graph->png;

				close IMG;
				}
			else 	{
				copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
				}
			}
		else 	{
			copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
			}

		}
		if ($input->param('pgraphs') eq 'all' || $input->param('print_cardiac') == 1){
		++$graph_cnt;
		print "$graph_cnt, ";
		####  Cardiac Assessment Risk levels
		$b17_graph = GD::Graph::pie->new(321,321);

		$o_file = $GGR_PAGE_DIR . "ggr_cardrisks.png";

		my ($clparm, $cmedparm, $cmodparm, $chparm, $b17_basis);

		$b17_basis = $PARMS{cardiac_low} + $PARMS{cardiac_med} + $PARMS{cardiac_mod} + $PARMS{cardiac_high};

		if ( $PARMS{CRC_cnt} > 0 )
			{
			$clparm = sprintf("%.2f",($PARMS{cardiac_low}/$b17_basis * 100));
			$cmedparm = sprintf("%.2f",($PARMS{cardiac_med}/$b17_basis * 100));
			$cmodparm = sprintf("%.2f",($PARMS{cardiac_mod}/$b17_basis * 100));
			$chparm = sprintf("%.2f",($PARMS{cardiac_high}/$b17_basis * 100));

			@g17_data = (
				["Low Risk - $clparm%", "Moderate Risk - $cmodparm%", "High Risk - $cmedparm%", "Very High Risk - $chparm%"],
				[$clparm,$cmodparm,$cmedparm,$chparm]
				);

			$b17_graph->set(
					interlaced 	=> undef,
					bgclr 		=> 'white',
					transparent 	=> undef,
					label 		=> 'Group Risk Levels',
					axislabelclr 	=> 'black',
					pie_height 	=> 18,
					show_values 	=> 1,
					title           => 'Cardiac Assessment Results',
					legend_placement=> 'RT',
					l_margin 	=> 10,
					r_margin 	=> 10,
					shadow_depth 	=> 6,
					dclrs 		=> [ qw(green lgreen lyellow lred) ],
					start_angle 	=> -85,
					);
					$b17_graph->set_title_font("$font_dir/arial.ttf", 14);
					$b17_graph->set_value_font("$font_dir/arial.ttf", 8);
					$b17_graph->set_label_font("$font_dir/arial.ttf", 8);

			$gd_graph = $b17_graph->plot(\@g17_data);

			if ( $gd_graph ) {
				open(IMG, ">$o_file") or die "$! - $o_file";

				binmode IMG;

				print IMG $gd_graph->png;

				close IMG;
				}
			else 	{
				copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
				}
			}
		else 	{
			copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
			}

		}
		if ($input->param('pgraphs') eq 'all' || $input->param('print_fitness') == 1){
		++$graph_cnt;
		print "$graph_cnt, ";
		####  Fitness assessment results
		$b18_graph = GD::Graph::mixed->new(430, 200);

		$o_file = $GGR_PAGE_DIR . "ggr_fit.png";

		if ( $PARMS{FIT_cnt} > 0 )
			{
			my $fit_step_basis = ($PARMS{'fit_step_low'}+$PARMS{'fit_step_med'}+$PARMS{'fit_step_high'});
			my $fit_sits_basis = ($PARMS{'fit_sits_low'}+$PARMS{'fit_sits_med'}+$PARMS{'fit_sits_high'});
			my $fit_push_basis = ($PARMS{'fit_push_low'}+$PARMS{'fit_push_med'}+$PARMS{'fit_push_high'});
			my $fit_flex_basis = ($PARMS{'fit_flex_low'}+$PARMS{'fit_flex_med'}+$PARMS{'fit_flex_high'});


			@g18_data = (
			    ["Pulse",                                           "Sit ups",                                 "Push ups",                            "Flexibility"],
			    [(int($PARMS{'fit_step_low'}/$fit_step_basis*100)), (int($PARMS{'fit_sits_low'}/$fit_sits_basis*100)), (int($PARMS{'fit_push_low'}/$fit_push_basis*100)), (int($PARMS{'fit_flex_low'}/$fit_flex_basis*100))],
			    [(int($PARMS{'fit_step_med'}/$fit_step_basis*100)), (int($PARMS{'fit_sits_med'}/$fit_sits_basis*100)), (int($PARMS{'fit_push_med'}/$fit_push_basis*100)), (int($PARMS{'fit_flex_med'}/$fit_flex_basis*100))],
			    [(int($PARMS{'fit_step_high'}/$fit_step_basis*100)), (int($PARMS{'fit_sits_high'}/$fit_sits_basis*100)), (int($PARMS{'fit_push_high'}/$fit_push_basis*100)), (int($PARMS{'fit_flex_high'}/$fit_flex_basis*100))]
			  );
			$b18_graph->set(
					interlaced 	=> undef,
					bgclr 		=> 'white',
					transparent 	=> undef,
					x_label 	=> 'Fitness Levels',
					y_label 	=> '% of Participants',
					title 		=> 'Fitness Assessment Results',
					cumulate 	=> 1,
					y_min_value 	=> 0,
					y_max_value  	=> 100,
					y_tick_number   => 10,
					y_label_skip    => 2,
					y_number_format => '%d',
					types 		=> [qw( bars bars bars )],
					show_values     => 0,
					legend_placement=> 'RT',
					dclrs 		=> [ qw(lred yellow green) ],
					borderclrs 	=> [ qw(black black) ],
					bar_spacing 	=> 15
					);
					$b18_graph->set_legend( 'Low Fitness', 'Medium Fitness', 'High Fitness' );
					$b18_graph->set_title_font("$font_dir/arial.ttf", 14);
					$b18_graph->set_x_label_font("$font_dir/arial.ttf", 10);
					$b18_graph->set_y_label_font("$font_dir/arial.ttf", 10);
					$b18_graph->set_x_axis_font("$font_dir/arial.ttf", 8);
					$b18_graph->set_y_axis_font("$font_dir/arial.ttf", 8);
					$b18_graph->set_legend_font("$font_dir/arial.ttf", 9);

			$gd_graph = $b18_graph->plot(\@g18_data);

			if ( $gd_graph ) {
				open(IMG, ">$o_file") or die "$! - $o_file";

				binmode IMG;

				print IMG $gd_graph->png;

				close IMG;
				}
			else 	{
				copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
				}
			}
		else 	{
			copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
			}

		}
		if ($input->param('pgraphs') eq 'all' || $input->param('print_wellbeing') == 1){
		++$graph_cnt;
		print "$graph_cnt, ";
		####  General Well-being assessment results
		$b19_graph = GD::Graph::mixed->new(460, 220);

		$o_file = $GGR_PAGE_DIR . "ggr_gwb.png";

		if ( $PARMS{GWB_cnt} > 0 )
			{
			my $gwb_stress_basis = ($PARMS{'gwb_stress_low'}+$PARMS{'gwb_stress_med'}+$PARMS{'gwb_stress_high'});
			my $gwb_depression_basis = ($PARMS{'gwb_depression_low'}+$PARMS{'gwb_depression_med'}+$PARMS{'gwb_depression_high'});
			my $gwb_health_basis = ($PARMS{'gwb_health_low'}+$PARMS{'gwb_health_med'}+$PARMS{'gwb_health_high'});
			my $gwb_control_basis = ($PARMS{'gwb_control_low'}+$PARMS{'gwb_control_med'}+$PARMS{'gwb_control_high'});
			my $gwb_being_basis = ($PARMS{'gwb_being_low'}+$PARMS{'gwb_being_med'}+$PARMS{'gwb_being_high'});
			my $gwb_vitality_basis = ($PARMS{'gwb_vitality_low'}+$PARMS{'gwb_vitality_med'}+$PARMS{'gwb_vitality_high'});


			@g19_data = (
			    ["Stress",                                           "Depression",                                                     "Self Control",                                                "Well-being",                                    "Vitality",                                                 "Health"],
			    [(int($PARMS{'gwb_stress_low'}/$gwb_stress_basis*100)), (int($PARMS{'gwb_depression_low'}/$gwb_depression_basis*100)), (int($PARMS{'gwb_control_high'}/$gwb_control_basis*100)), (int($PARMS{'gwb_being_high'}/$gwb_being_basis*100)), (int($PARMS{'gwb_vitality_high'}/$gwb_vitality_basis*100)), (int($PARMS{'gwb_health_high'}/$gwb_health_basis*100))],
			    [(int($PARMS{'gwb_stress_med'}/$gwb_stress_basis*100)), (int($PARMS{'gwb_depression_med'}/$gwb_depression_basis*100)), (int($PARMS{'gwb_control_med'}/$gwb_control_basis*100)), (int($PARMS{'gwb_being_med'}/$gwb_being_basis*100)), (int($PARMS{'gwb_vitality_med'}/$gwb_vitality_basis*100)), (int($PARMS{'gwb_health_med'}/$gwb_health_basis*100))],
			    [(int($PARMS{'gwb_stress_high'}/$gwb_stress_basis*100)), (int($PARMS{'gwb_depression_high'}/$gwb_depression_basis*100)), (int($PARMS{'gwb_control_low'}/$gwb_control_basis*100)), (int($PARMS{'gwb_being_low'}/$gwb_being_basis*100)), (int($PARMS{'gwb_vitality_low'}/$gwb_vitality_basis*100)), (int($PARMS{'gwb_health_low'}/$gwb_health_basis*100))]
			  );
			$b19_graph->set(
					interlaced 	=> undef,
					bgclr 		=> 'white',
					transparent 	=> undef,
					x_label 	=> 'Participant Perceptions',
					y_label 	=> '% of Participants',
					title 		=> 'General Well-being Assessment Results',
					cumulate 	=> 1,
					y_min_value 	=> 0,
					y_max_value  	=> 100,
					y_tick_number   => 10,
					y_label_skip    => 2,
					y_number_format => '%d',
					types 		=> [qw( bars bars bars )],
					show_values     => 0,
					legend_placement=> 'RT',
					dclrs 		=> [ qw(green yellow lred) ],
					borderclrs 	=> [ qw(black black) ],
					bar_spacing 	=> 15
					);
					$b19_graph->set_legend( 'Good', 'Medium', 'Poor' );
					$b19_graph->set_title_font("$font_dir/arial.ttf", 14);
					$b19_graph->set_x_label_font("$font_dir/arial.ttf", 10);
					$b19_graph->set_y_label_font("$font_dir/arial.ttf", 10);
					$b19_graph->set_x_axis_font("$font_dir/arial.ttf", 7);
					$b19_graph->set_y_axis_font("$font_dir/arial.ttf", 8);
					$b19_graph->set_legend_font("$font_dir/arial.ttf", 9);

			$gd_graph = $b19_graph->plot(\@g19_data);

			if ( $gd_graph ) {
				open(IMG, ">$o_file") or die "$! - $o_file";

				binmode IMG;

				print IMG $gd_graph->png;

				close IMG;
				}
			else 	{
				copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
				}
			}
		else 	{
			copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
			}

		}
		if ($input->param('pgraphs') eq 'all' || $input->param('print_wellbeing2') == 1){
		++$graph_cnt;
		print "$graph_cnt, ";
		####  General Well-being assessment results new HRA format
		$b20_graph = GD::Graph::mixed->new(460, 220);

		$o_file = $GGR_PAGE_DIR . "ggr1_gwb.png";

		if ( $hra_cnt > 0 )
			{
			my $gwb_stress_basis = ($PARMS{'gwb_stress_low'}+$PARMS{'gwb_stress_med'}+$PARMS{'gwb_stress_high'});
			my $gwb_depression_basis = ($PARMS{'gwb_depression_low'}+$PARMS{'gwb_depression_med'}+$PARMS{'gwb_depression_high'});


			@g20_data = (
			    ["Stress",                                           "Depression"],
			    [(int($PARMS{'gwb_stress_low'}/$gwb_stress_basis*100)), (int($PARMS{'gwb_depression_low'}/$gwb_depression_basis*100))],
			    [(int($PARMS{'gwb_stress_med'}/$gwb_stress_basis*100)), (int($PARMS{'gwb_depression_med'}/$gwb_depression_basis*100))],
			    [(int($PARMS{'gwb_stress_high'}/$gwb_stress_basis*100)), (int($PARMS{'gwb_depression_high'}/$gwb_depression_basis*100))]
			  );
			$b20_graph->set(
					interlaced 	=> undef,
					bgclr 		=> 'white',
					transparent 	=> undef,
					x_label 	=> 'Participant Perceptions',
					y_label 	=> '% of Participants',
					title 		=> 'Stress & Depression Results',
					cumulate 	=> 1,
					y_min_value 	=> 0,
					y_max_value  	=> 100,
					y_tick_number   => 10,
					y_label_skip    => 2,
					y_number_format => '%d',
					types 		=> [qw( bars bars bars )],
					show_values     => 0,
					legend_placement=> 'RT',
					dclrs 		=> [ qw(green yellow lred) ],
					borderclrs 	=> [ qw(black black) ],
					bar_spacing 	=> 15
					);
					$b20_graph->set_legend( 'Good', 'Medium', 'Poor' );
					$b20_graph->set_title_font("$font_dir/arial.ttf", 14);
					$b20_graph->set_x_label_font("$font_dir/arial.ttf", 10);
					$b20_graph->set_y_label_font("$font_dir/arial.ttf", 10);
					$b20_graph->set_x_axis_font("$font_dir/arial.ttf", 8);
					$b20_graph->set_y_axis_font("$font_dir/arial.ttf", 8);
					$b20_graph->set_legend_font("$font_dir/arial.ttf", 9);

			$gd_graph = $b20_graph->plot(\@g20_data);

			if ( $gd_graph ) {
				open(IMG, ">$o_file") or die "$! - $o_file";

				binmode IMG;

				print IMG $gd_graph->png;

				close IMG;
				}
			else 	{
				copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
				}
			}
		else 	{
			copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
			}

		}
		if ($input->param('pgraphs') eq 'all' || $input->param('print_selfreported') == 1){
		++$graph_cnt;
		print "$graph_cnt, ";
		####  Self Reported disease
		$b21_graph = GD::Graph::bars->new(500, 250);

		$o_file = $GGR_PAGE_DIR . "ggr_srd.png";

		my $disease_max = $hra_cnt *.8;

		$disease_max = 10 if $disease_max < 10;

		if($hra_cnt > 0)
			{
			@g21_data = (
			    ["Cancer",            "Diabetes",            "Heart attack",     "Heart disease",         "High BP",       "High cholesterol","Stroke"],
			    [$PARMS{'my_cancer'}, $PARMS{'my_diabetes'}, $PARMS{'my_heart'}, $PARMS{'my_hrtdisease'}, $PARMS{'my_bp'}, $PARMS{'my_chol'}, $PARMS{'my_stroke'}],
			  );
			$b21_graph->set(
					interlaced 	=> undef,
					bgclr 		=> 'white',
					transparent 	=> undef,
					x_label 	=> 'Disease',
					y_label 	=> 'Participants',
					title 		=> 'Personal Conditions',
					cumulate 	=> 1,
					y_max_value  	=> $disease_max,
					y_tick_number   => 20,
					y_label_skip    => 4,
					y_number_format => '%d',
					y_min_value     => 0,
					show_values     => 1,
					long_ticks	=> 0,
					cycle_clrs 	=> 1,
					dclrs 		=> [ qw(lyellow lblue red lgreen marine white green lred cyan yellow lgray orange lbrown pink lorange purple cyan yellow lgray) ],
					borderclrs 	=> [ qw(black black black black black black black) ],
					bar_spacing 	=> 15
					);
					$b21_graph->set_title_font("$font_dir/arial.ttf", 14);
					$b21_graph->set_x_label_font("$font_dir/arial.ttf", 10);
					$b21_graph->set_y_label_font("$font_dir/arial.ttf", 10);
					$b21_graph->set_x_axis_font("$font_dir/arial.ttf", 6);
					$b21_graph->set_y_axis_font("$font_dir/arial.ttf", 8);
					$b21_graph->set_legend_font("$font_dir/arial.ttf", 9);

			$gd_graph = $b21_graph->plot(\@g21_data);

			if ( $gd_graph ) {
				open(IMG, ">$o_file") or die "$! - $o_file";

				binmode IMG;

				print IMG $gd_graph->png;

				close IMG;
				}
			else 	{
				copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
				}
			}
		else 	{
			copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
			}

		}
		if ($input->param('pgraphs') eq 'all' || $input->param('print_familyhistory') == 1){
		++$graph_cnt;
		print "$graph_cnt, ";
		####  Self Reported family history
		$b22_graph = GD::Graph::bars->new(500, 250);

		$o_file = $GGR_PAGE_DIR . "ggr_srfh.png";

		my $disease_max = $hra_cnt *.8;

		$disease_max = 10 if $disease_max < 10;

		if($hra_cnt > 0)
			{
			@g22_data = (
			    ["Cancer",            "Diabetes",            "Heart attack",     "Heart disease",         "High BP",       "High cholesterol","Stroke"],
			    [$PARMS{'fh_cancer'}, $PARMS{'fh_diabetes'}, $PARMS{'fh_heart'}, $PARMS{'fh_hrtdisease'}, $PARMS{'fh_bp'}, $PARMS{'fh_chol'}, $PARMS{'fh_stroke'}],
			  );
			$b22_graph->set(
					interlaced 	=> undef,
					bgclr 		=> 'white',
					transparent 	=> undef,
					x_label 	=> 'Disease',
					y_label 	=> 'Participants',
					title 		=> 'Family History Conditions',
					cumulate 	=> 1,
					y_max_value  	=> $disease_max,
					y_tick_number   => 20,
					y_label_skip    => 4,
					y_number_format => '%d',
					y_min_value     => 0,
					show_values     => 1,
					long_ticks	=> 0,
					cycle_clrs 	=> 1,
					dclrs 		=> [ qw(lyellow lblue red lgreen marine white green lred cyan yellow lgray orange lbrown pink lorange purple cyan yellow lgray) ],
					borderclrs 	=> [ qw(black black black black black black black) ],
					bar_spacing 	=> 15
					);
					$b22_graph->set_title_font("$font_dir/arial.ttf", 14);
					$b22_graph->set_x_label_font("$font_dir/arial.ttf", 10);
					$b22_graph->set_y_label_font("$font_dir/arial.ttf", 10);
					$b22_graph->set_x_axis_font("$font_dir/arial.ttf", 6);
					$b22_graph->set_y_axis_font("$font_dir/arial.ttf", 8);
					$b22_graph->set_legend_font("$font_dir/arial.ttf", 9);

			$gd_graph = $b22_graph->plot(\@g22_data);

			if ( $gd_graph ) {
				open(IMG, ">$o_file") or die "$! - $o_file";

				binmode IMG;

				print IMG $gd_graph->png;

				close IMG;
				}
			else 	{
				copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
				}
			}
		else 	{
			copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
			}
		}

		print "<br>Graphs done!</p><p>PDF being generated</p>";

	#create the PDF file
	%Defaults = 	(
			FileName => "${GGR_PAGE_DIR}ggr_output.pdf"
			);

	%vars = %PARMS;
	%vars = map { $_, $input->param($_) } $input->param();
	$vars{image_dir} = $GGR_PAGE_DIR;
	$vars{fixed_images} = $fixed_images;

	my %config_temp;

	foreach my $key ( $config->directives )
		{
		$config_temp{$key} = $config->$key;
		}

	my $pdfoutput = new Text::Template (SOURCE => $GGR_PDF, HASH => \%PARMS  )
	  or die qq|Couldn't fill in template: $Text::Template::ERROR<br>$GGR_PDF|;

	my $data = $pdfoutput->fill_in() or die qq|Couldn't fill in template: $Text::Template::ERROR<br>$GGR_PDF|;

	print "<p>Template completed</p>";

	my $pdf_doc = "${GGR_PAGE_DIR}ggr_output.pdf";


	open (PDF , "> ${GGR_PAGE_DIR}ggr_xml.xml");
	print PDF $data;
	close PDF;

	{
	PDFDoc->importXML( $data )->writePDF( "${GGR_PAGE_DIR}ggr_output.pdf" );
	}

	print qq|<p>PDF output file is written.  <a href="ggr.cgi?view=1">Click here to view</a>|;

	print $input->end_html;

	}
else 	{

	my @stip_conditions = ('WHERE');
	my $site_count;
	my $debug_string;

#	$db->debug_on( \*STDERR );

	my $site = $input->param('site');
	if ($site ne '')
		{
		my $connector = '=';
		my $close = "'";
		$_ = ($input->param('site'));
		if(/\/$/){
			$connector = 'LIKE';
			$close = q|%'|;
			}
		push @stip_conditions, " site " . $connector . " '" . $input->param('site') . $close;
		}
	else
		{
		@site_list  =  $db->site_list( ) ;

		$site_count = @site_list;

		if($site_count > 1)
			{
			my @parsed_list;

			foreach my $group ( @site_list )
				{
				$_ = $group;
				if(!/\//)
					{
					push @parsed_list, $group;
					}
				else 	{
					my @split_list = split /\//;
					my $split_count = @split_list;
					my $scnt=0;
					while ( $scnt < ($split_count - 1) ){	$split_list[$scnt] .= '/'; ++$scnt; }
					$scnt=1;
					while ( $scnt < $split_count )
						{
						$split_list[$scnt] = $split_list[$scnt-1] . $split_list[$scnt];
						push @split_list , $split_list[$scnt]  if ($scnt < ($split_count - 1));
						++$scnt;
						}
					my %in_list = ();
					foreach my $item ( @parsed_list ) { $in_list{$item}=1 }
					foreach my $split_item ( @split_list )
						{
						unless ($in_list{$split_item}){
							push @parsed_list, $split_item;
							$in_list{$split_item}=1;
							}
						}
					}
				}

			$select_string = qq|<option value="" selected> </option>|;

			foreach (@parsed_list) { $select_string .= qq|<option value="$_">$_</option>|; }
			}

		$db->finish;
		}
	if ($input->param('bdate_month'))
		{
		if( lc($config->db_driver) eq 'oracle' )
			{
			push @stip_conditions, " ADATE>='" . $input->param('bdate_year') . "-" . $input->param('bdate_month') . "-01 00:00:00'";}
		else	{
			push @stip_conditions, " ADATE>='" . $input->param('bdate_month') . "/01/" . $input->param('bdate_year') . "'";}

		}
	if ($input->param('edate_month'))
		{
		if( lc($config->db_driver) eq 'oracle' )
			{
			push @stip_conditions, " ADATE<'" . $input->param('edate_year') . "-" . $input->param('edate_month') . "-01 00:00:00'";}
		else	{
			push @stip_conditions, " ADATE<'" . $input->param('edate_month') . "/01/" . $input->param('edate_year') . "'";}
		}

	my $stipulations = '';

	my $user_footer = $input->param('user_footer');

	if ($#stip_conditions > 0)
		{
		my $j=0;
		foreach (@stip_conditions)
			{
			$stipulations .= " AND " if $j > 1;
			$stipulations .= "$_";
			++$j;
			}
		$html_string =  qq|<p>All records $stipulations will be processed: <form method=post action="ggr.cgi"><input type=hidden name=ggr_sql value="$stipulations"><input type=hidden name=process value=1><br>&nbsp;<br>Footer on each page will be: $user_footer<p>Note: ADATE is the date an assessment was taken.</p>|;

		}
	else	{
		$html_string =  qq|<p>All records for all sites will be processed: <form method=post action="ggr.cgi"><input type=hidden name=process value=1><br>&nbsp;<br>Footer on each page will be: $user_footer<br>&nbsp;<br>|;
		}

	$db->disconnect;

	if($input->param('defaults') == 1)	{
		# pass along all of the data in hidden fields
		my %vars1 = map { my $x = $_; $x =~ tr/A-Za-z_//c; $x, $input->param($_) }
			$input->param;

		my %config = map { $_, $config->$_ } $config->directives;

		$vars1{config} = \%config;

		$vars1{html_string} = $html_string;

		my $template = $config->template_directory . "ggr_check.html";

		my $data = Text::Template::fill_in_file( $template, HASH => \%vars1  );
		error( "Could not find template [ $template ]" ) unless $data;

		my $form   = new HTML::FillInForm;
		my $output = $form->fill( scalarref => \$data, fobject => $input );

		#output the next template
		print $input->header(), $output;
		}
	else	{

		# pass along all of the data in hidden fields
		my %vars1 = map { my $x = $_; $x =~ tr/A-Za-z_//c; $x, $input->param($_) }
			$input->param;

		my %config = map { $_, $config->$_ } $config->directives;

		$vars1{config} = \%config;

		$vars1{site_count} = $site_count;

		$vars1{html_string} = $select_string;

		$vars1{html_string} .= $debug_string;

		my $template = $config->template_directory . "ggr_input.html";

		my $data = Text::Template::fill_in_file( $template, HASH => \%vars1 );
		error( "Could not find template [ $template ]" ) unless $data;

		my $form   = new HTML::FillInForm;
		my $output = $form->fill( scalarref => \$data, fobject => $input );

		#output the next template
		print $input->header(), $output;
		}

	}

# handle errors
sub error
	{
	my $message = shift;
	my $error   = shift;

	print "Content-type: text/plain\n\n$message";

	warn "$message: $error";

	exit 1;
	}

=head1 BUGS

=head1 TO-DO
Save processing incrementally
Have printing pickup processing data files
XML output


=head1 SEE ALSO

L<HealthStatus>,
L<HealthStatus::User>,
L<HealthStatus::CalcRisk>,

=head1 AUTHOR

	Greg White <gwhite@healthstatus.com>

=head1 COPYRIGHT

	Copyright 1999-2002 HealthStatus.com, Inc., all rights reserved

=cut
