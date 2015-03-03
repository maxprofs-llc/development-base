package HealthStatus::Report;
use strict;


use HealthStatus::Database;
use HealthStatus::User;
use HealthStatus::Constants;

use base qw( Exporter );

use subs qw();
use vars qw( $VERSION $AUTOLOAD @EXPORT_OK %X_Y %assessment_names_short %assessment_names);

use Carp;

( $VERSION ) = q$Revision: 1.2 $ =~ m/ (\d+ \. \d+ \. \d+ \. \d+ \. \d+ \. \d+) /gx;

my %assessment_names = ( HRA	=> 'General Health assesments ',
			 GHA	=> 'Health Risk assesments (original)',
			 CRC	=> 'Cardiac Risk assesments',
			 DRC	=> 'Diabetes Risk assesments',
			 FIT	=> 'Fitness assesments',
			 GWB	=> 'General Well Being assesments',
			 OHA    => 'Health and Brain Trauma',
			 );
%assessment_names_short = ( HRA	=> 'General Health ',
			 GHA	=> 'Health Risk',
			 CRC	=> 'Cardiac Risk',
			 DRC	=> 'Diabetes Risk',
			 FIT	=> 'Fitness',
			 GWB	=> 'General Well-Being',
			 OHA    => 'Health and Brain Trauma',
			 REG	=> 'Participation Report');


sub new {
	my( $class, $args ) = @_;

	my $config = HealthStatus::Config->new( $args->{config} );
	croak "Could not create configuration object [$config]"
		unless ref $config;

	my $self = {
		debug   => $args->{debug} ? 1 : 0,
		config_file => $args->{config},
		config      => $config,
	 	};

	bless( $self, $class );
}

sub config
	{
	my $self = shift;

	return $self->{config};
	}

sub set_counters
{
	my $self = shift;
	my ($config_file, $user_list, $PARMS,  $GROUP, $assessments_ref, $cnt_ref, $set, $Debug) = @_;

	print 'in counters @ Report.pm' if $Debug;

	my $operating_system = $^O;

	my (@assessments, $user, $health, $high, $medium, $moderate, $high_cnt, $medium_cnt, $moderate_cnt, $low_cnt, $ach_high, $ach_medium, $ach_moderate, $ach_high_cnt, $ach_medium_cnt, $ach_moderate_cnt, $ach_low_cnt, $risks, $hash, $riskFactor, $riskAvg, $riskDesc, $riskAch);

	my $cnt = $$cnt_ref;
	@assessments = @$assessments_ref;

	my %settings = %$set;

	my $config = $self->config;

	carp 'opening DB @ Report.pm' if $Debug;
	my $db = HealthStatus::Database->new( $config );

	$db->debug_on( \*STDERR ) if $Debug;

	my $workbook_ref;
#	foreach (keys %settings){
#	print $_ .' - '. $settings{$_}.'<br>';}

	my $date_restriction = "WHERE tmplte <> 'needs bio' " if ($config->biofilter);
	my $date_restriction = "WHERE 1=1 " unless ($config->biofilter);
	if($settings{'participation_date'}){

		if($settings{'anonymous'}){
			if($settings{'stipulation'}){
				$date_restriction .=  ' and '. $settings{'stipulation'}.' and ';
				}
			$date_restriction .= ' and '. $settings{'participation_date'};
			$date_restriction =~ s/A\.//g;
			$date_restriction =~ s/ AND $//g;
			}
		else	{
			$date_restriction .= ' AND ' . $settings{'participation_date'};
			$date_restriction =~ s/A\.//g;
			$date_restriction =~ s/ AND $//g;
			carp "$date_restriction" if $Debug;
			}
		}
	if($settings{'participation_date'} && $settings{sex_restriction})
	{
		$date_restriction .= ' AND ' . $settings{'sex_restriction'};
	}
	elsif(defined $settings{sex_restriction})
	{
#		$date_restriction = 'WHERE ' . $settings{'sex_restriction'};
	}
#print 'Report date restriction = ' . $settings{'participation_date'}. ' - '.$settings{'date_restrict'}. ' - '.$date_restriction. ' - '.$settings{'stipulation'};
	foreach ( keys %$user_list )
	{
		carp "user $cnt - $_\n" if $Debug;
		if ( ( $PARMS->{user_count} % 50 ) == 0 && $PARMS->{user_count} > 1)
			{
			if ($PARMS->{user_count} == 50)	{
				if($config->ggr_ajax){ print qq|<script language="javascript" type="text/javascript"> document.getElementById('ggr_status').innerHTML+='processing data - $PARMS->{user_count} users with a qualifying assessment completed';   </script>|;}
 				else { print "processing data - $PARMS->{user_count} users with a qualifying assessment completed<br>" if(!$config->aggregate_binary);}
 				$db->debug_off();
 				}
			else	{
				if($config->ggr_ajax){ print qq|<script language="javascript" type="text/javascript">  document.getElementById('ggr_status').innerHTML='processing data - $PARMS->{user_count} users with a qualifying assessment completed';   </script>|;}
				else { print "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;$PARMS->{user_count} users with a qualifying assessment completed<br>" if(!$config->aggregate_binary);}
				}
			}
		print "<p>" if ( ( $cnt % 1000 ) == 0 && $cnt > 1 && !$config->aggregate_binary && !$config->ggr_ajax);
		last if ($cnt >= $settings{max_to_process}+50  && $settings{max_to_process} > 0);

		foreach my $alist( @assessments )
		{
			if (ref($user_list->{$_}) eq "HASH"){
				if($user_list->{$_}{$alist} > 1){ ++$PARMS->{'users_back'}{$alist} }
				$PARMS->{assessment}{$alist} = 0;
				$PARMS->{$alist} += $user_list->{$_}{$alist};
			}
		}

		undef $user;
		undef $health;
		my $not_a_batch = 1;

		my ($set_age, $set_weight, $set_misc, $set_risk, $set_cardiac, $set_depression, $set_riskdetails, $set_history, $set_diabetes) = 0;

		my $user = HealthStatus::User->new( );

		$user->db_id ($_);

		my ($db_status, $db_mult) = $db->lookup_user ( $user, $config, 'user' );

		if ($operating_system ne 'MSWin32'){
			print "\0" if(!$config->aggregate_binary);
			}

		$PARMS->{assessment}{user} = 0;

		if(substr($user->db_fullname, 0, 5) eq 'batch' || $config->ggr_all_users_batch) { $not_a_batch = 0; }
		if($config->anonymous_users) { $not_a_batch = 0; }

		++$cnt if ($not_a_batch);  # if this is not a batch add one the number of users processed
		my @returned_recs  =  $db->get_users_assessments_taken( $user, $config, $assessments_ref, $date_restriction );

		carp "number of returned recs for $_ - ". scalar(@returned_recs)."\n" if $Debug;
#print "number of returned recs for $_ - ". scalar(@returned_recs)."\n";

		foreach my $this_user ( @returned_recs )
		{
			next if ( $PARMS->{assessment}{$this_user->{'assessment'}} && lc $settings{all_records} ne 'all' && $not_a_batch);
			++$PARMS->{assessment}{$this_user->{'assessment'}};
			carp $this_user->{'assessment'}." xnum - ". $this_user->{'db_record'}."\n" if $Debug;

			++$cnt if (!$not_a_batch); # if this is a batch there are multiple users data under one user record (the batch) so we have to increment for each assessment

			my $db_found = $db->get_users_assessment( $user, $config, $this_user->{'assessment'}, $this_user->{'xnum'});

			if ($db_found == 0)
			{
#				carp "record not found " . $this_user->{'xnum'} . " for assessment " . $this_user->{'assessment'} . "\n";
				--$PARMS->{assessment}{$this_user->{'assessment'}};
				next;
			}

# this could happen
			if ( $user->{'db_template'} eq 'needs bio' ){
				carp "Skipped ".$user->{'assessment'}." xnum - ". $user->{'db_record'}." template - ".$user->{'db_template'} ."\n" if $Debug;
				--$PARMS->{assessment}{$this_user->{'assessment'}};
				next;
			}

			$user->set_non_standard;

			$health = HealthStatus->new(
			{
				assessment => $this_user->{'assessment'},
				user       => $user,
				config     => $config_file,
			} );

			$health->assess( $user );

			if( !$PARMS->{assessment}{user}  || !$not_a_batch)
			{
				++$PARMS->{user_count};
				++$PARMS->{assessment}{user};
				$set_age = 0;
				$set_weight = 0;
			}

			if( $user->sex eq MALE && !$set_age)
			{
				++$PARMS->{'male'};
				++$PARMS->{'m_lt_19'} if ($user->age <= 19);
				++$PARMS->{'m_20_29'} if ($user->age >= 20 && $user->age <= 29);
				++$PARMS->{'m_30_39'} if ($user->age >= 30 && $user->age <= 39);
				++$PARMS->{'m_40_49'} if ($user->age >= 40 && $user->age <= 49);
				++$PARMS->{'m_50_59'} if ($user->age >= 50 && $user->age <= 59);
				++$PARMS->{'m_60'} if ($user->age >= 60);
				$set_age = 1 if $not_a_batch;
			}
			elsif( $user->sex eq FEMALE && !$set_age)
			{
				++$PARMS->{'female'};
				++$PARMS->{'f_lt_19'} if ($user->age <= 19);
				++$PARMS->{'f_20_29'} if ($user->age >= 20 && $user->age <= 29);
				++$PARMS->{'f_30_39'} if ($user->age >= 30 && $user->age <= 39);
				++$PARMS->{'f_40_49'} if ($user->age >= 40 && $user->age <= 49);
				++$PARMS->{'f_50_59'} if ($user->age >= 50 && $user->age <= 59);
				++$PARMS->{'f_60'} if ($user->age >= 60);
				$set_age = 1 if $not_a_batch;
			}

			if( !$set_weight &&
				($this_user->{'assessment'} eq 'FIT' ||
				$this_user->{'assessment'} eq 'DRC' ||
				$this_user->{'assessment'} eq 'CRC' ||
				$this_user->{'assessment'} eq 'GHA' ||
				$this_user->{'assessment'} eq 'OHA' ||
				$this_user->{'assessment'} eq 'HRA'))
			{
				++$PARMS->{'wt_under'} if ($user->bmi <= BMI_LOW);
				++$PARMS->{'wt_good'} if ($user->bmi <= BMI_GOOD && $user->bmi > BMI_LOW);
				++$PARMS->{'wt_over'} if ($user->bmi < BMI_OBESE && $user->bmi > BMI_GOOD);
				++$PARMS->{'wt_obese'} if ($user->bmi >= BMI_OBESE);
				$set_weight = 1 if $not_a_batch;
			}
			if( !$set_misc &&
				($this_user->{'assessment'} eq 'CRC' ||
				$this_user->{'assessment'} eq 'DRC' ||
				$this_user->{'assessment'} eq 'GHA' ||
				$this_user->{'assessment'} eq 'OHA' ||
				$this_user->{'assessment'} eq 'HRA'))
			{
				++$PARMS->{'r2c_exercise'}{$user->r2c_exercise} if ($user->r2c_exercise);
				++$PARMS->{'r2c_weight'}{$user->r2c_weight} if ($user->r2c_weight);
			}
			if( !$set_misc &&
				($this_user->{'assessment'} eq 'CRC' ||
				$this_user->{'assessment'} eq 'GHA' ||
				$this_user->{'assessment'} eq 'OHA' ||
				$this_user->{'assessment'} eq 'HRA'))
			{
				++$PARMS->{'sm_still'} if ($user->smoke_status eq 'Still smoke');
				++$PARMS->{'sm_never'} if ($user->smoke_status eq NEVER_SMOKED);
				++$PARMS->{'sm_quit'} if ($user->smoke_status eq USE_TO_SMOKE);
				++$PARMS->{'exer_none'} if($user->exercise eq 'Less than one time per week' || $user->exercise eq '' ||
							($user->exercise == 0 && $this_user->{'assessment'} eq 'CRC'));
				++$PARMS->{'exer_some'} if($user->exercise eq 'One or two times per week' ||
							(($user->exercise == 1  ||
							$user->exercise == 2) && $this_user->{'assessment'} eq 'CRC'));
				++$PARMS->{'exer_good'} if(($user->exercise eq 'At least three times per week'||
							$user->exercise eq 'Three or four times per week'||
							$user->exercise eq 'At least three times per week' ||
							$user->exercise eq 'At least five times per week') ||
							($user->exercise > 2 && $this_user->{'assessment'} eq 'CRC'));
				++$PARMS->{'chol_high'} if($user->cholesterol > CHOL_HIGH ||
							$user->cholesterol_check eq HIGH);
				++$PARMS->{'chol_med'} if(($user->cholesterol >= CHOL_MARGINAL &&
							$user->cholesterol <= CHOL_HIGH) && $user->cholesterol_check ne HIGH);
				++$PARMS->{'chol_low'} if($user->cholesterol_check ne HIGH &&
							(($user->cholesterol > 1 &&
							$user->cholesterol < CHOL_MARGINAL) ||
							($user->cholesterol < CHOL_MARGINAL &&
							$user->cholesterol_check eq NORMAL_OR_LOW)));
				++$PARMS->{'cholknown_high'} if($user->cholesterol > CHOL_HIGH );
				++$PARMS->{'cholknown_med'} if(($user->cholesterol >= CHOL_MARGINAL &&
							$user->cholesterol <= CHOL_HIGH));
				++$PARMS->{'cholknown_low'} if($user->cholesterol > 1 &&
							$user->cholesterol < CHOL_MARGINAL);
				++$PARMS->{'cholknown_count'} if($user->cholesterol > 1);
				++$PARMS->{'cholcheck_high'} if($user->cholesterol < 1 && $user->cholesterol_check eq HIGH);
				++$PARMS->{'cholcheck_low'} if($user->cholesterol < 1 && $user->cholesterol_check eq NORMAL_OR_LOW);
				++$PARMS->{'cholcheck_count'} if($user->cholesterol < 1 && ($user->cholesterol_check eq NORMAL_OR_LOW || $user->cholesterol_check eq HIGH));
				++$PARMS->{'chol_unknown'} if($user->cholesterol < 1 && $user->cholesterol_check eq DONT_KNOW);
				++$PARMS->{'diet_fiber_good'} if($user->fiber eq YES);
				++$PARMS->{'diet_fiber_bad'} if($user->fiber eq NO);
				++$PARMS->{'diet_fat_good'} if($user->fat eq NO);
				++$PARMS->{'diet_fat_bad'} if($user->fat eq YES);				
				if($user->HgA1C < 1){
					++$PARMS->{'HgA1C_unknown'};
					}
				else	{
					++$PARMS->{'HgA1C_high'} if ($user->HgA1C > HGA1C_HIGH);
					++$PARMS->{'HgA1C_low'} if ($user->HgA1C < HGA1C_MARGINAL);
					++$PARMS->{'HgA1C_med'} if ($user->HgA1C >= HGA1C_MARGINAL &&
								$user->HgA1C <= HGA1C_HIGH);
					}
				++$PARMS->{'HgA1C_count'};	
				if($user->waist > 1){
					if (($user->waist > 40 && $user->sex eq MALE ) || ($user->waist > 35 && $user->sex eq FEMALE )){
						++$PARMS->{'waist_high'} ;
						}
					else	{
						++$PARMS->{'waist_ok'};
						}
					++$PARMS->{'waist_count'};
					}
				
				if($user->ldl < 1){
					++$PARMS->{'LDL_unknown'};
					}
				else	{
					++$PARMS->{'LDL_high'} if ($user->ldl > LDL_HIGH);
					++$PARMS->{'LDL_low'} if ($user->ldl < LDL_MARGINAL);
					++$PARMS->{'LDL_med'} if ($user->ldl >= LDL_MARGINAL &&
								$user->ldl <= LDL_HIGH);
					}
				++$PARMS->{'LDL_count'};	

				if($user->triglycerides < 1){
					++$PARMS->{'TRI_unknown'} ;
					}
				else	{
					++$PARMS->{'TRI_high'} if ($user->triglycerides > TRI_HIGH);
					++$PARMS->{'TRI_below150'} if ($user->triglycerides < 150);
					++$PARMS->{'TRI_150_199'} if ($user->triglycerides >= 150 && $user->triglycerides < 200);
					++$PARMS->{'TRI_200_499'} if ($user->triglycerides >= 200 && $user->triglycerides < 500);
					++$PARMS->{'TRI_above500'} if ($user->triglycerides > 500);
					}
				++$PARMS->{'TRI_count'};
				

				if($user->hdl < 1) {
					++$PARMS->{'HDL_unknown'};
					}
				else	{
					++$PARMS->{'HDL_low'} if (($user->hdl < HDL_LOW_MALE && $user->sex eq MALE) ||
								($user->hdl < HDL_LOW_FEMALE && $user->sex eq FEMALE));
					++$PARMS->{'HDL_high'} if (($user->hdl > HDL_LOW_MALE && $user->sex eq MALE) ||
								($user->hdl > HDL_LOW_FEMALE && $user->sex eq FEMALE));
					}
				++$PARMS->{'HDL_count'};
				
				if($user->glucose < 1){
					++$PARMS->{'GLUCOSE_unknown'};
					}
				else	{
					++$PARMS->{'GLUCOSE_low'} if (($user->glucose < GLUCOSE_LOW_MALE && $user->sex eq MALE) || ($user->glucose < GLUCOSE_LOW_FEMALE && $user->sex eq FEMALE));
					++$PARMS->{'GLUCOSE_good'} if (($user->glucose > GLUCOSE_LOW_MALE && $user->sex eq MALE) || ($user->glucose > GLUCOSE_LOW_FEMALE && $user->sex eq FEMALE) && $user->glucose < GLUCOSE_MARGINAL);
					++$PARMS->{'GLUCOSE_med'} if($user->glucose >= GLUCOSE_MARGINAL && $user->glucose <= GLUCOSE_HIGH);
					++$PARMS->{'GLUCOSE_high'} if ($user->glucose > GLUCOSE_HIGH);
					}
				++$PARMS->{'GLUCOSE_count'};
				
				++$PARMS->{'fh_cancer'}		if ( $user->fam_breast_cancer eq 'One' || $user->fam_breast_cancer eq "Two" || $user->fh_cancer_chk == 1);
				++$PARMS->{'fh_heart'}		if ( $user->fh_heart_attack_chk == 1 || $user->family_heart_attack  eq YES);
				++$PARMS->{'fh_diabetes'}	if ( $user->siblings_have_diabetes eq YES ||$user-> parents_have_diabetes eq YES || $user->fh_diabetes_chk == 1 || $user->family_diabetes eq YES);
				++$PARMS->{'fh_copd'}		if ( $user->fh_copd_chk == 1 );
				++$PARMS->{'fh_ibs'}		if ( $user->fh_ibs_chk == 1 );
				++$PARMS->{'my_heart'}		if ( $user->heart_attack_chk == 1 || $user->heart_attack eq YES);
				++$PARMS->{'my_diabetes'}	if ( $user->diabetes_chk == 1  || $user->diabetes eq YES);
				if(($user->bp_sys >= BP_HIGH_SYSTOLIC ||
							$user->bp_dias >= BP_HIGH_DIASTOLIC) ||
							$user->bp_check eq HIGH) { ++$PARMS->{'bp_high'} ;}
				elsif(($user->bp_sys >= BP_MARGINAL_SYSTOLIC ||
							$user->bp_dias >= BP_MARGINAL_DIASTOLIC) &&
							($user->bp_sys < BP_HIGH_SYSTOLIC &&
							$user->bp_dias < BP_HIGH_DIASTOLIC)  &&
							$user->bp_check ne HIGH
							){++$PARMS->{'bp_med'};}
				elsif(
							($user->bp_sys > 1 &&
							$user->bp_sys < BP_MARGINAL_SYSTOLIC) &&
							($user->bp_dias > 1 &&
							$user->bp_dias < BP_MARGINAL_DIASTOLIC) ||
							($user->bp_check eq NORMAL_OR_LOW)  &&
							$user->bp_check ne HIGH
							){++$PARMS->{'bp_low'};}
				elsif($user->bp_check eq DONT_KNOW ||
							(($user->bp_dias < 1 ||
							$user->bp_sys < 1)   &&
							($user->bp_check ne HIGH ||
							$user->bp_check eq NORMAL_OR_LOW))
							){++$PARMS->{'bp_unknown'} ;}
				++$PARMS->{'r2c_smoke'}{$user->r2c_smoke} if ($user->r2c_smoke);
				++$PARMS->{'r2c_drink'}{$user->r2c_exercise} if ($user->r2c_exercise);
				++$PARMS->{'r2c_stress'}{$user->r2c_stress} if ($user->r2c_stress);
				++$PARMS->{'r2c_autosafety'}{$user->r2c_autosafety} if ($user->r2c_autosafety);
				++$PARMS->{'r2c_fat'}{$user->r2c_fat} if ($user->r2c_fat);
				++$PARMS->{'r2c_bp'}{$user->r2c_bp} if ($user->r2c_bp);
				++$PARMS->{'r2c_cholesterol'}{$user->r2c_cholesterol} if ($user->r2c_cholesterol);
				++$PARMS->{'r2c_checkups'}{$user->r2c_checkups} if ($user->r2c_checkups);
				++$PARMS->{'r2c_immunizations'}{$user->r2c_immunizations} if ($user->r2c_immunizations);
				$set_misc = 1 if $not_a_batch;
			}

			if( !$set_diabetes && ($this_user->{'assessment'} eq 'DRC' || ($this_user->{'assessment'} eq 'GHA' && $config->MHA )) )
			{
				++$PARMS->{DRC_cnt};
				++$PARMS->{'diabetes_low'} if ( $user->diabetes_points <= 5);
				++$PARMS->{'diabetes_med'} if ( $user->diabetes_points > 5 &&
								$user->diabetes_points < 9 );
				++$PARMS->{'diabetes_high'} if ( $user->diabetes_points > 9);
				++$PARMS->{'fh_diabetes'}	if ( $user->siblings_have_diabetes eq "Yes" || $user->parents_have_diabetes eq "Yes");
				$set_diabetes = 1 if $not_a_batch;
			}

			if( !$set_cardiac && ($this_user->{'assessment'} eq 'CRC'  || ($this_user->{'assessment'} eq 'GHA' && $config->MHA ) ) )
			{
				++$PARMS->{CRC_cnt};
				++$PARMS->{'cardiac_high'} if ( $user->cardiac_risk/3 > $user->cardiac_average_risk );
				++$PARMS->{'cardiac_med'} if ( $user->cardiac_risk/2 > $user->cardiac_average_risk &&  $user->cardiac_risk/3 <= $user->cardiac_average_risk );
				++$PARMS->{'cardiac_mod'} if ( $user->cardiac_risk > $user->cardiac_average_risk && $user->cardiac_risk/2 <= $user->cardiac_average_risk );
				++$PARMS->{'cardiac_low'} if ( $user->cardiac_risk <= $user->cardiac_average_risk );
				$set_cardiac = 1 if $not_a_batch;
			}

			if( $this_user->{'assessment'} eq 'FIT' )
			{
				++$PARMS->{FIT_cnt};
				++$PARMS->{'fit_step_high'} 	if ( $user->step_flag == 0 	||
									$user->step_flag == 1 );
				++$PARMS->{'fit_step_med'} 	if ( $user->step_flag == 2 );
				++$PARMS->{'fit_step_low'} 	if ( $user->step_flag == 3 	||
									$user->step_flag == 4 );
				++$PARMS->{'fit_push_high'} 	if ( $user->push_up_flag == 0 	||
									$user->push_up_flag == 1 );
				++$PARMS->{'fit_push_med'} 	if ( $user->push_up_flag == 2 );
				++$PARMS->{'fit_push_low'} 	if ( $user->push_up_flag == 3 	||
									$user->push_up_flag == 4 );
				++$PARMS->{'fit_sits_high'} 	if ( $user->sit_up_flag == 0 	||
									$user->sit_up_flag == 1 );
				++$PARMS->{'fit_sits_med'} 	if ( $user->sit_up_flag == 2 );
				++$PARMS->{'fit_sits_low'} 	if ( $user->sit_up_flag == 3 	||
									$user->sit_up_flag == 4 );
				++$PARMS->{'fit_flex_high'} 	if ( $user->flexibility_flag == 0 ||
									$user->flexibility_flag == 1 );
				++$PARMS->{'fit_flex_med'} 	if ( $user->flexibility_flag == 2 );
				++$PARMS->{'fit_flex_low'} 	if ( $user->flexibility_flag == 3 ||
									$user->flexibility_flag == 4 );
			}

			if( $this_user->{'assessment'} eq 'GWB' )
			{
				++$PARMS->{'gwb_stress_low'} 	if ( $user->stress_flag == 0 );
				++$PARMS->{'gwb_stress_med'} 	if ( $user->stress_flag == 1 );
				++$PARMS->{'gwb_stress_high'} 	if ( $user->stress_flag == 2 );
				++$PARMS->{'gwb_depression_high'} if ( $user->depression_flag == 2 );
				++$PARMS->{'gwb_depression_med'} 	if ( $user->depression_flag == 1 );
				++$PARMS->{'gwb_depression_low'} 	if ( $user->depression_flag == 0 );
				++$PARMS->{'gwb_health_high'} 	if ( $user->health_flag == 0 );
				++$PARMS->{'gwb_health_med'} 	if ( $user->health_flag == 1 );
				++$PARMS->{'gwb_health_low'} 	if ( $user->health_flag == 2 );
				++$PARMS->{'gwb_control_high'} 	if ( $user->control_flag == 0 );
				++$PARMS->{'gwb_control_med'} 	if ( $user->control_flag == 1 );
				++$PARMS->{'gwb_control_low'} 	if ( $user->control_flag == 2 );
				++$PARMS->{'gwb_being_high'} 	if ( $user->being_flag == 0 );
				++$PARMS->{'gwb_being_med'} 	if ( $user->being_flag == 1 );
				++$PARMS->{'gwb_being_low'} 	if ( $user->being_flag == 2 );
				++$PARMS->{'gwb_vitality_high'} 	if ( $user->vitality_flag == 0 );
				++$PARMS->{'gwb_vitality_med'} 	if ( $user->vitality_flag == 1 );
				++$PARMS->{'gwb_vitality_low'} 	if ( $user->vitality_flag == 2 );
				++$PARMS->{GWB_cnt};
			}

			if( !$set_history && $this_user->{'assessment'} eq 'HRA' )
			{
				++$PARMS->{'my_cancer'}		if ( $user->cancer_chk == 1 );
				++$PARMS->{'my_hrtdisease'}	if ( $user->heart_disease_chk == 1 );
				++$PARMS->{'fh_hrtdisease'}	if ( $user->fh_heart_disease_chk == 1 );
				++$PARMS->{'my_bp'}		if ( $user->high_bp_chk == 1 );
				++$PARMS->{'fh_bp'}		if ( $user->fh_high_bp_chk == 1 );
				++$PARMS->{'my_chol'}		if ( $user->high_cholesterol_chk == 1 );
				++$PARMS->{'fh_chol'}		if ( $user->fh_high_cholesterol_chk == 1 );
				++$PARMS->{'my_stroke'}		if ( $user->stroke_chk == 1 );
				++$PARMS->{'fh_stroke'}		if ( $user->fh_stroke_chk == 1 );
				$set_history = 1 if $not_a_batch;
			}

			if( !$set_depression  && ($this_user->{'assessment'} eq 'HRA'  || ($this_user->{'assessment'} eq 'GHA' && $config->MHA ) ) )
			{
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

				++$PARMS->{'gwb_stress_low'} 	if ( $stress_flag == 0 );
				++$PARMS->{'gwb_stress_med'} 	if ( $stress_flag == 1 );
				++$PARMS->{'gwb_stress_high'} 	if ( $stress_flag == 2 );
				++$PARMS->{'gwb_depression_high'} if ( $depression_flag == 2 );
				++$PARMS->{'gwb_depression_med'} 	if ( $depression_flag == 1 );
				++$PARMS->{'gwb_depression_low'} 	if ( $depression_flag == 0 );
				$set_depression = 1 if $not_a_batch;
			}

			if( !$set_riskdetails  && ($this_user->{'assessment'} eq 'GHA' || $this_user->{'assessment'} eq 'OHA' ||
					$this_user->{'assessment'} eq 'HRA'))
			{
				++$PARMS->{GHA_cnt} if( $this_user->{'assessment'} eq 'GHA') ;
				++$PARMS->{HRA_cnt} if( $this_user->{'assessment'} eq 'HRA');
				++$PARMS->{'flu_no'} if($user->flushot eq NO);
				++$PARMS->{'flu_old'} if($user->flushot eq 'Yes, more than ten');
				++$PARMS->{'flu_current'} if($user->flushot eq YES);
				++$PARMS->{'sb_never'} if($user->seat_belt eq 'Never, 0%');
				++$PARMS->{'sb_seldom'} if($user->seat_belt eq 'Seldom, 1%-40%');
				++$PARMS->{'sb_some'} if($user->seat_belt eq 'Sometimes, 41%-80%');
				++$PARMS->{'sb_usually'} if($user->seat_belt eq NEARLY_ALWAYS);
				++$PARMS->{'sb_always'} if($user->seat_belt eq ALWAYS_100);
				++$PARMS->{'sb_drinkdrive'} if ($user->drink_and_drive  > 0);
				++$PARMS->{'sb_speed'} if ($user->speed eq 'More than 15 mph over limit');
				++$PARMS->{'alc_high'} if($user->drinks_week > 20);
				++$PARMS->{'alc_medium'} if($user->drinks_week <= 20 &&
								$user->drinks_week >= 13);
				++$PARMS->{'alc_low'} if($user->drinks_week < 13);
				$PARMS->{'alc_drinks'} += $user->drinks_week;
				++$PARMS->{'bp_meds'} if($user->bp_meds eq YES);
				++$PARMS->{'bp_no_meds'} if($user->bp_meds eq NO &&
								(($user->bp_sys >= BP_HIGH_SYSTOLIC ||
								$user->bp_dias >= BP_HIGH_DIASTOLIC) ||
								$user->bp_check eq HIGH));

				++$PARMS->{gen_exam_under2} if($user->general_exam eq "Less than two years ago");
				++$PARMS->{gen_exam_2to5} if($user->general_exam eq "Two to five years ago");
				++$PARMS->{gen_exam_5plus} if($user->general_exam eq "Five or more years ago");
				++$PARMS->{gen_exam_never} if($user->general_exam eq "Never");

				++$PARMS->{days_missed_none} if ($user->days_missed eq "None");
				++$PARMS->{days_missed_1to5} if ($user->days_missed eq "One to five");
				++$PARMS->{days_missed_6to10} if ($user->days_missed eq "Six to ten");
				++$PARMS->{days_missed_10plus} if ($user->days_missed eq "More than 10");
				++$PARMS->{days_missed_not_apply} if ($user->days_missed eq "Does not apply");

				if ($user->age >= 50)
				{
					++$PARMS->{'colonoscopy_good'} if( $user->colon_exam eq  LESS_THAN_A_YEAR ||
										$user->colon_exam eq  ONE_YEAR_AGO );
					++$PARMS->{'colonoscopy_med'} if( $user->colon_exam  eq TWO_YEARS_AGO );
					++$PARMS->{'colonoscopy_bad'}  if( $user->colon_exam eq  THREE_YEARS_AGO ||
										$user->colon_exam eq  NEVER );
				}
				if( $user->sex eq MALE )
				{
					if ($user->age >= 40)
					{
						++$PARMS->{'male_prostate_good'} if( $user->rectal_male eq  LESS_THAN_A_YEAR ||
											$user->rectal_male eq  ONE_YEAR_AGO );
						++$PARMS->{'male_prostate_med'}  if( $user->rectal_male eq TWO_YEARS_AGO );
						++$PARMS->{'male_prostate_bad'}  if( $user->rectal_male eq  THREE_YEARS_AGO ||
											$user->rectal_male eq  NEVER );
					}
					#lvh medical director wants prostate information for over 50 only
					if ($user->age >= 50)
					{
						++$PARMS->{'male_prostate50_good'} if( $user->rectal_male eq  LESS_THAN_A_YEAR ||
											$user->rectal_male eq  ONE_YEAR_AGO );
						++$PARMS->{'male_prostate50_med'}  if( $user->rectal_male eq TWO_YEARS_AGO );
						++$PARMS->{'male_prostate50_bad'}  if( $user->rectal_male eq  THREE_YEARS_AGO ||
											$user->rectal_male eq  NEVER );
					}
				}
				else
				{
					if ($user->age >= 40)
					{
						++$PARMS->{'mammo_good'} if( $user->mammogram_flag <  2 );
						++$PARMS->{'mammo_med'}  if( $user->mammogram_flag == 2 );
						++$PARMS->{'mammo_bad'}  if( $user->mammogram_flag >  2 );
					}
					++$PARMS->{'pap_good'}  if( $user->pap_flag <   2 );
					++$PARMS->{'pap_med'}   if( $user->pap_flag ==  2 );
					++$PARMS->{'pap_bad'}   if( $user->pap_flag >   2 );

					++$PARMS->{'self_breast_good'}  if( $user->self_breast_exam_flag <   1 );
					++$PARMS->{'self_breast_med'}   if( $user->self_breast_exam_flag ==  1 );
					++$PARMS->{'self_breast_bad'}   if( $user->self_breast_exam_flag >   1 );
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

				$risks = $user->risk_data || next;
				if($set_risk){
					$set_risk = 0;
					next;
					}
				$set_risk = 1 if $not_a_batch;
				for(my $i = 1; $i <= 43; $i++)
				{
					$hash = $risks->record( $i );
					$riskFactor = $hash->{user_risk};
					$riskAvg = $hash->{average_risk};
					$riskDesc = $hash->{name};
					$riskAch = $hash->{achievable_risk};
					++$GROUP->{$riskDesc} if ($riskFactor > $riskAvg);
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
					++$PARMS->{'high'} ;
					$PARMS->{'high_cnt'} += $high;
				}
				elsif($medium_cnt)
				{
					++$PARMS->{'medium'};
					$PARMS->{'medium_cnt'} += $medium;
				}
				elsif ($moderate_cnt)
				{
					++$PARMS->{'moderate'};
					$PARMS->{'moderate_cnt'} += $moderate;
				}
				elsif ($low_cnt)
				{
					++$PARMS->{'low'};
				}
				if ($ach_high_cnt)
				{
					++$PARMS->{'ach_high'} ;
					$PARMS->{'ach_high_cnt'} += $ach_high;
				}
				elsif($ach_medium_cnt)
				{
					++$PARMS->{'ach_medium'};
					$PARMS->{'ach_medium_cnt'} += $ach_medium;
				}
				elsif ($ach_moderate_cnt)
				{
					++$PARMS->{'ach_moderate'};
					$PARMS->{'ach_moderate_cnt'} += $ach_moderate;
				}
				elsif ($ach_low_cnt)
				{
					++$PARMS->{'ach_low'};
				}
				$set_riskdetails = 1 if $not_a_batch;
			}
		my %stuff = (
			assessment=> $this_user->{assessment},
			report_name => $settings{report_name},
			file_name => $settings{file_name},
			assessment_list => $assessments_ref,
			);

		if($settings{report_type} eq 'indv_data')
			{
			if($settings{report_format} eq 'XML')
				{
				$workbook_ref = xml($config, $user, $workbook_ref, \%stuff );
				}
			elsif($settings{report_format} eq 'XLS' )
				{
				$workbook_ref = xls($config, $user, $workbook_ref, \%stuff );
				}
			elsif($settings{report_format} eq 'CSV')
				{
				$workbook_ref = csv($config, $user, $workbook_ref, \%stuff );
				}
			elsif($settings{report_format} eq 'PDF' )
				{
				my $file_cnt = sprintf("%05d",  $cnt);
				my $newdir = $config->ggr_adv_page_dir . $set->{work_dir} ;
				if (!(-e $newdir)) {
					mkdir $newdir, 0766 or die "couldn't mkdir $newdir because: $!\n";
					chmod (0777, $newdir)or die "couldn't chmod $newdir because: $!\n";
				}
				$config->set('save_pdf_file_as', $newdir . $file_cnt . '_' . $user->assessment . '_' . $user->db_id . '.pdf');
				my $data = $health->output( 'PDFE' , $settings{pdf_template} );
				}
			}
		}
	}
	if($config->ggr_ajax){ print qq|<script language="javascript" type="text/javascript"> document.getElementById('ggr_status').innerHTML='processing complete - $PARMS->{user_count} users with a qualifying assessment completed';   </script>|;}
	else { print "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;$PARMS->{user_count} users with a qualifying assessment completed<br>" if(!$config->aggregate_binary);}
	$db->finish;
	$db->disconnect;
	if($settings{report_type} eq 'indv_data' && $settings{report_format} eq 'XML')
		{
		my $output = $settings{file_name};
		open(XML, ">>$output" ) or die "Failed xml end file - $output\n$!"; print XML "</hsdata>"; close XML;
		}

	$$cnt_ref = $cnt;
}

# Accounting report
# provide counts by site/client/custom fields as specified by config value: ggr_adv_group_list_db
# break these out by assessment/date
sub accounting
	{
	my $self = shift;
	my ($config_file, $user_list, $PARMS,  $GROUP, $assessments_ref, $cnt_ref, $set, $Debug) = @_;

	print 'in accounting @ Report.pm' if $Debug;

	use Time::localtime;
	use Date::Calc qw(:all);

	my %settings = %$set;
	my %hash = %settings;
	my $user = $hash{'user'};

	my $config = $self->config;

	my $db = HealthStatus::Database->new( $config );

	$db->debug_on( \*STDOUT ) if $Debug;

	my $adate = 'adate';

	if( lc($config->db_driver) eq 'oracle' )
	{
		my $APrev = "ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY-MM-DD HH24:MI:SS'";
		$db->execute_sql($APrev);
		$adate = 'ADATE';
	}

	my @assessments_allowed = split /\s+/, $config->ggr_adv_tables;
	my $assessment = lc $hash{assessment} ;
	my $report = lc $hash{report_name};
	my $daily = lc $hash{daily};
	my $twelve_month = lc $hash{twelve_month};

	my @assessment_list = @{$assessments_ref};
#
#	# get the user elements from the config fields
	my $config_title_field = 'acct_' . $report . '_fields';
	my @titles = split(" ",$config->$config_title_field);

	my ($year,$month,$day) = Today();
	my ($year1,$month1,$day1) = Add_Delta_Days($year,$month,$day,-1);

#	my $sdte1 = sprintf("%04d-%02d-%02d", $year,$month,$day);
#	my $sdte = sprintf("%04d-%02d-%02d", $year1,$month1,$day1);
#	my $g_year = $year;
#	my $g_month = $month;
#	my $g_day = $day;
	my %number_of_rows;

#	my ($year,$month,$day) = Today();
#	my ($year1,$month1,$day1) = Add_Delta_Days($year,$month,$day,-1);
	my ($year2,$month2,$day2) = Add_Delta_Days($year,$month,$day,-7);
	my $sdte1 = sprintf("%04d-%02d-%02d 00:00:00", $year,$month,$day);
	my $sdte = sprintf("%04d-%02d-%02d", $year1,$month1,$day1);
	my $curr_year_dte = sprintf("%04d-01-01 00:00:00", $year);
	my $week_dte = sprintf("%04d-%02d-%02d", $year2,$month2,$day2);
	my $month_dte = sprintf("%04d-%02d-%02d", $year,$month,1);
	my $prev_month_dte = sprintf("%04d-%02d-%02d", Add_Delta_YM($year,$month,1,0,-1));

	my $g_year = $year;
	my $g_month = $month;
	my $g_day = $day;


	my $sqlintro;
	if($hash{stipulation} &&  $hash{stipulation} ne 'anonymous'){ $sqlintro = $hash{stipulation} . ' and ';  }
	else { $sqlintro = 'where ';}
carp 'Report  A ' . $sqlintro . $hash{stipulation};

	my %count_stip = (
		'A-Today' => $sqlintro . "$adate>='$sdte1'",
		'B-Yesterday' => $sqlintro . "$adate>'$sdte' and $adate<'$sdte1'",
		'C-This week' => $sqlintro . "$adate>='$week_dte'",
		'D-This month' => $sqlintro . "$adate>='$month_dte'",
		'E-Last month' => $sqlintro . "$adate>='$prev_month_dte' and $adate<'$month_dte'",
		'F-This year' => $sqlintro . "$adate>='$curr_year_dte'",
		'F-Total assessments taken (all time)' => "");
	if($hash{date_condition_str} gt ''){
		my $dte_range = $hash{date_condition_str} =~ s/ AND $//;
		$dte_range =~ s/ A\./ /;
		$count_stip{'Your Range'} = $sqlintro . $dte_range;
		}
	foreach my $count_key (sort keys %count_stip){
		foreach (@assessment_list){
#			carp "count key = " . $count_stip{$count_key} . "\n";
			$PARMS->{'accounting'}{'assessments'}{$count_key}{$_}  =  $db->hs_count( $_, $count_stip{$count_key} );
#carp $count_key." - ".$_." - ".$count_stip{$count_key}." - ".$PARMS->{'accounting'}{'assessments'}{$count_key}{$_};
			}
		}
	if($daily){
		for(my $i=-365;$i <= 0;++$i)
			{
			my ($year1,$month1,$day1) = Add_Delta_Days($year,$month,$day,$i);
			my ($year2,$month2,$day2) = Add_Delta_Days($year,$month,$day,$i+1);
			my $stipulation = $sqlintro;
			my $mdte = sprintf("%04d-%02d-%02d", $year1,$month1,$day1);
			my $mdte2 = sprintf("%04d-%02d-%02d", $year2,$month2,$day2);
			$stipulation .= " $adate>='" . $mdte ." 00:00:00'";
			$stipulation .= " AND $adate<'" . $mdte2 . " 00:00:00'";

			my $keydte = sprintf("%04d-%02d-%02d", $year1,$month1,$day1);

			foreach my $alist (@assessment_list){
				$PARMS->{'accounting'}{'daily_assessments'}{$keydte}{$alist}  =  $db->hs_count( $alist, $stipulation );
				}
			}
		}
	if($twelve_month){
		for(my $i=-12;$i <= 0;++$i)
			{
			my $sync_year = $year;
			my $sync_month = $month + $i;
			if($sync_month < 1){ $sync_month = 12 + $month + $i; $sync_year = $year - 1;}
			my $sync_year2 = $year;
			my $sync_month2 = $month + $i + 1;
			if($sync_month2 < 1){ $sync_month2 = 12 + $month + $i + 1; $sync_year2 = $year - 1;}
			my $stipulation = $sqlintro;
			my $mdte = sprintf("%04d-%02d-%02d", $sync_year,$sync_month,'01');
			my $mdte2 = sprintf("%04d-%02d-%02d", $sync_year2,$sync_month2,'01');
			$stipulation .= " $adate>='" . $mdte ." 00:00:00'";
			$stipulation .= " AND $adate<'" . $mdte2 . " 00:00:00'";
			my $keydte = sprintf("%04d-%02d-%02d", $sync_year,$sync_month,'01');
			foreach my $alist (@assessment_list){
				$PARMS->{'accounting'}{'monthly_assessments'}{$keydte}{$alist}  =  $db->hs_count( $alist, $stipulation );
				}
			}
		}
	print "Assessments counted<br>Getting groups to count<br>";

	# specified which userdata fields will be used to select the data out
	my %ggr_global_group_lists;
	my @group_db_list = split / /,$config->ggr_adv_group_list_db;
	my @group_friendly_list = split /,/,$config->ggr_adv_group_list_friendly;
	my $t_cnt = 0;

	foreach my $db_group (@group_db_list)
		{
		my $tname = $db_group . "_selection";
		my $pname = $hash{$tname};
		my $tgroup = $db_group . "_selectgroup";
		my $pgroup = $hash{$tgroup};
#carp 'Report  ' . $tname . ' - ' . $pname . ' - ' . $tgroup . ' - ' . $pgroup . ' - '. $db_group;
		if ($pname  ne '')
			{
			my $connector = '=';
			my $close = "'";
			$_ = $pname;
			my $temp_id = $db_group;
			$temp_id = uc ($db_group) if( lc($config->db_driver) eq 'oracle' );
			if($pname =~ m/\/$/){
				$connector = ' LIKE ';
				$close = q|%'|; #'
				}
#			push (@stip_conditions, $temp_id . $connector . " '" . $pname . $close);
			}
		else
			{
			my $restrict_name = 'ggr_adv_group_' . $db_group . '_restriction';
			my $restriction;
			my $stipulations;
			# If group limitation is on, make sure the results consist only of their group members
			if ($config->group_limit_admin && $user->db_id ne $config->group_limit_admin_master) {
				$restriction =  "where " . $config->group_limit_admin_key . " LIKE " . $$config{db}->quote($user->{$config->group_limit_admin_value} . "%")  ;	}
			elsif($config->{$restrict_name}){
				$restriction = $config->$restrict_name; }
			elsif($pgroup) {
				my $connector = '=';
				my $close = "'";
				$_ = $pgroup;
				my $temp_id = $db_group;
				$temp_id = uc ($db_group) if( lc($config->db_driver) eq 'oracle' );
				if($pgroup =~ m/\/$/){
					$connector = ' LIKE ';
					$close = q|%'|; #'
					}
				$restriction = 'where ' . $temp_id . $connector . " '" . $pgroup . $close;}
#			carp 'Report restriction = ' . $restriction . ' - ' . $tgroup . ' - ' . $pgroup;
			my @pgroup_list;
			if( $config->authenticate_method eq 'hs' || $config->authenticate_method eq 'client'){
				@pgroup_list  =  $db->reg_group_list( $db_group, $restriction . ' ORDER by ' . $db_group ) ;
				}
			else	{
				@pgroup_list  =  $db->assessment_group_list( $db_group, \@assessments_allowed, $restriction . ' ORDER by ' . $db_group ) ;
				}

			$ggr_global_group_lists{$db_group}{list} = \@pgroup_list;

			$ggr_global_group_lists{$db_group}{count} = scalar(@pgroup_list);

			$ggr_global_group_lists{$db_group}{human} = $group_friendly_list[$t_cnt];
			++$t_cnt;
			}
		}
	print "Have groups to count<br>Counting ";

	foreach my $db_group (@group_db_list)
		{
		print "\0";
		my @parsed_list = ();
		foreach my $group ( @{$ggr_global_group_lists{$db_group}{list}} )
			{
			print ". ";

#carp $db_group." - ".$group;
			$_ = $group;
			if($group =~ m/\//)
				{
				my @split_list = split /\//;
				my $split_count = scalar(@split_list);
				my $scnt=0;
				while ( $scnt < ($split_count-1) ){ $split_list[$scnt] .= '/';  ++$scnt; }
				$scnt=1;
				while ( $scnt < $split_count )
					{
#carp 'split '.$split_count." - ".$scnt." - ".$split_list[$scnt-1]." - ".$split_list[$scnt];
					$split_list[$scnt] = $split_list[$scnt-1] . $split_list[$scnt];
					push @split_list , $split_list[$scnt]  if ($scnt < ($split_count - 1));
					++$scnt;
					}
				my %in_list = ();
				foreach my $item ( @parsed_list ) { $in_list{$item}=1; }
				foreach my $split_item ( @split_list )
					{
#					if($split_item !~ m/\/$/){ $split_item .= '/'; }
					unless ($in_list{$split_item}){
						push @parsed_list, $split_item;
						$in_list{$split_item}=1;
						}
					}
				}
			else 	{
				push @parsed_list, $group;
				}
			}
		$PARMS->{'accounting'}{'human'}{$db_group} = $ggr_global_group_lists{$db_group}{human};
#	$db->debug_on( \*STDERR );
		foreach my $pgroup (@parsed_list)
			{
			print "<br>Counting $pgroup";
			my $connector = '=';
			my $open = " '";
			my $close = "'";
			my $temp_id = $db_group;
			$temp_id = uc ($db_group) if( lc($config->db_driver) eq 'oracle' );
			if($pgroup =~ m/\/$/){
				$connector = ' LIKE ';
				$close = q|%'|;   # '
				}
			if(!$pgroup){
				$connector = ' is NULL';
				$open = '';
				$close = '';
				}
			my $stip1 = $temp_id . $connector . $open . $pgroup . $close;
			my $stipulations = 'WHERE ' . $temp_id . $connector . $open . $pgroup . $close;
#carp "*A ".$db_group." - ".$pgroup . ' - '.$stip1. ' - '.$stipulations;
			if( $config->authenticate_method eq 'hs' || $config->authenticate_method eq 'client'){
				my @tables_list = ( 'REG' );
				$PARMS->{'accounting'}{'groups'}{$db_group}{$pgroup}{'users'}  =  $db->count_users( $config, \@tables_list, $stipulations );
#carp "B";
				foreach (@assessment_list){
					$PARMS->{'accounting'}{'groups'}{$db_group}{$pgroup}{$_}  =  $db->group_assessment_count( $temp_id, $_, $stip1, 0, 0 );
#carp "B".$db_group." - ".$pgroup." - ".$_." - ".$PARMS->{'accounting'}{'groups'}{$db_group}{$pgroup}{$_};
					}
				}
			else	{
#carp "C ";
				foreach (@assessment_list){
#carp "*C ".$_." - ".$stipulations;
					$PARMS->{'accounting'}{'groups'}{$db_group}{$pgroup}{'users'} += $db->hs_count($_, $stipulations );
					$PARMS->{'accounting'}{'groups'}{$db_group}{$pgroup}{$_}  =   $db->hs_count($_, $stipulations );
#carp "**C ".$db_group." - ".$pgroup." - ".$_." - ".$PARMS->{'accounting'}{'groups'}{$db_group}{$pgroup}{$_};
					}
				}
			}
		}

	my @tables_list = ( 'REG' );
	my $stipulations = "";
	if( $config->authenticate_method eq 'hs' || $config->authenticate_method eq 'client'){
		$PARMS->{'accounting'}{'group_total'}{'all'}  =  $db->count_users( $config, \@tables_list, $stipulations ) ;
		foreach (@assessment_list){
			$PARMS->{'accounting'}{'group_total'}{$_}  =  $db->hs_count( $_, '' );
			}
		}
	else	{
		foreach (@assessment_list){
			$PARMS->{'accounting'}{'group_total'}{$_}  =  $db->hs_count( $_, '' );
			$PARMS->{'accounting'}{'group_total'}{'all'}  +=   $db->hs_count( $_, '' );
			}
		}

	my %stuff = (
		report_name => $set->{report_name},
		file_name => $set->{file_name},
		assessment_list => $assessments_ref,
		);

	if($set->{report_format} eq 'XML')
		{
#		my $workbook_ref = xml($config, $user, $workbook_ref, \%stuff );
		}
	elsif($set->{report_format} eq 'XLS' )
		{
		my $workbook_ref = xls_account($config,\%stuff, $PARMS );
		return 1;
		}

	}

# Creates a participation report - one sheet listing the users that took any of the selected assessments
# within the appropriate selected parameters set by the admin

# process is: 	make a temporary table of users that meet any user restrictions (site, db_employer, group codes, client codes)
#		make a temporary table of assessments that meet any assessment restrictions (date, assessment, sex, wellness score)
#		go through one table and find the matches for the other.
sub participation
	{
	my $self = shift;
	my ($config_file, $user_list, $PARMS,  $GROUP, $assessments_ref, $cnt_ref, $set) = @_;

	my (@assessments, $user, $health, $high, $medium, $moderate, $high_cnt, $medium_cnt, $moderate_cnt, $low_cnt, $ach_high, $ach_medium, $ach_moderate, $ach_high_cnt, $ach_medium_cnt, $ach_moderate_cnt, $ach_low_cnt, $risks, $hash, $riskFactor, $riskAvg, $riskDesc, $riskAch);

	@assessments = @$assessments_ref;

	my %settings = %$set;

	my $config = $self->config;

	my $db = HealthStatus::Database->new( $config );

	my %table_names = %{$db->table_names($assessments_ref)};

	my $workbook_ref;

	my $report = lc $settings{report_name};
	my $assessment = lc $settings{assessment} ;

	my $main_temp = 'd_' . $settings{work_dir} . '_mytmp';
	$main_temp =~ s/\///g;

#	carp 'main temp = ' . $main_temp;

	# get the user elements from the config fields
	my $config_title_field = 'rpt_' . $report . '_participation_fields';
	my @titles = split(" ",$config->$config_title_field);
	my @titles2;
	my $fields_to_retrieve = '';
	my $fields_to_retrieve_2 = $config->db_id . ', ';
	my @fields;
	my ($db_user_fields_ref) = $db->user_to_db( \@titles, \@fields, 'REG');
	my %db_user_fields = %$db_user_fields_ref;
	# we want the date of the particular assessment that is meeting the criteria, this removes the user signup date
	delete $db_user_fields{'user'}{'db_sortdate'} if exists( $db_user_fields{'user'}{'db_sortdate'} );
	delete $db_user_fields{'db'}{'adate'} if exists( $db_user_fields{'db'}{'adate'} );
	my %db_user_more_fields;
	foreach (keys %{$db_user_fields{'db'}}){
		$fields_to_retrieve .= 't1.' . $_ . ', ';
		}
	foreach (@titles){
		unless ( defined $db_user_fields{'user'}{$_} ){
			push @titles2, $_;
			}
		}
	if(@titles2){
		my ($db_user_more_fields_ref) = $db->user_to_db( \@titles2, \@fields, 'GHA');
		%db_user_more_fields = %$db_user_more_fields_ref;
		foreach (keys %{$db_user_more_fields{'db'}}){
			if($_ ne 'adate'){
				$fields_to_retrieve .= 't3.' . $_ . ', ';
				$fields_to_retrieve_2 .= $_ . ', ';
				}
			else	{
				$fields_to_retrieve .= 't3.' . $_ . ', ';
				$fields_to_retrieve_2 .= 't3.' . $_ . ', ';
				}
			}
		}
	$fields_to_retrieve =~ s/, $//;
	$fields_to_retrieve_2 =~ s/, $//;

	my $dateline = $settings{participation_date};
	carp 'dateline = ' . $dateline . "\n";
	$dateline =~ s/A\.//g;
	$dateline =~ s/ AND $//;
	$dateline =~ s/^WHERE //;
	$dateline =~ s/adate/t3\.adate/g;
	my $short_stipulation = $settings{stipulation};
	$short_stipulation =~ s/^WHERE //;

	my $sql_restriction = '';
	$sql_restriction .= $short_stipulation if ($short_stipulation);
	$sql_restriction .= ' and ' if($dateline && $short_stipulation);
	$sql_restriction .= $dateline if($dateline);

	carp 'REPORT.pm sql_restriction = ' . $sql_restriction . "\n";

	my %table_pointers;

	my $jcnt=0;
	my $jmax = scalar(@assessments);
	my $sql_statement = 'select distinct ' . $fields_to_retrieve . ' from ' . $HealthStatus::Database::Tables{REG};
	my $sql_statement_new = 'select distinct ' . $fields_to_retrieve . ' from ' . $HealthStatus::Database::Tables{REG};
	if($jmax > 0) {
		$sql_statement .= ' as t1 join (SELECT ';
		$sql_statement_new .= ' as t1 inner join (SELECT ';
		foreach my $alist( @assessments )
			{
			++$jcnt;
			$sql_statement_new .= $fields_to_retrieve_2 . ' from ' . $table_names{$alist} . '  AS t3 inner join ' . $main_temp . ' on hs_uid=hsuid where hs_uid=hsuid and tableCode='. $jcnt . ' ' if ($config->db_driver eq 'postgres');
			$sql_statement_new .= $fields_to_retrieve_2 . ' from ' . $table_names{$alist} . '  AS t3 inner join ' . $main_temp . ' where hs_uid=hsuid and tableCode='. $jcnt . ' ' if ($config->db_driver eq 'mysql');
			$sql_statement_new .= 'and ' . $sql_restriction . ' ' if $sql_restriction;
			$sql_statement_new .= ' union select ' if($jcnt < $jmax) ;
			$table_pointers{$alist} = $jcnt;
			}
		$sql_statement_new .= ')as t3 on t3.' . $config->db_id . ' = t1.' . $config->db_id . ' order by t1.grpID; ' if ($config->db_driver eq 'mysql' || $config->db_driver eq 'mssql');
		}

	my $if_exists = 'if exists ' if ($config->db_driver eq 'mysql');
	my $sql_create = 'DROP TABLE ' . $if_exists . $main_temp;
	$db->execute_sql( $sql_create, 1);
	my $serial = 'SERIAL' ;
	$serial = 'INT auto_increment' if ($config->db_driver eq 'mysql');
	$serial = 'int PRIMARY KEY IDENTITY' if ($config->db_driver eq 'mssql');
#	my $dte_time = 'timestamp';
	my $dte_time = 'smalldatetime';
	$dte_time = 'datetime'  if ($config->db_driver eq 'mysql');
	my $pkey= ' )' ;
	$pkey = ', Primary key (tmpID) )' if ($config->db_driver eq 'mysql');
	$pkey = ' )' if ($config->db_driver eq 'mssql');

# Create a temporary table
	my $sql_create = 'CREATE TABLE ' . $main_temp . ' (tmpID ' . $serial . ', hsuid VARCHAR(90), adate ' . $dte_time . ', name varchar(45), TableCode INT, xnum varchar(30)'.$pkey;
	$db->execute_sql( $sql_create, 1);

	$sql_restriction = 'where ' . $sql_restriction if($dateline || $short_stipulation);

	carp 'sql_restriction (2) = ' . $sql_restriction . "\n";
	my @messages_1;
	my $mess_cnt=1;

# Push the pieces we need to do lookups later into the temporary table, only use the selected assessments
	my $sql_create1;
	$sql_create1 = 'INSERT INTO ' . $main_temp . " (hsuid, adate, tableCode, xnum ) (SELECT * FROM ( ";
	$sql_create1 = 'INSERT INTO ' . $main_temp . " (hsuid, adate, tableCode, xnum ) SELECT * FROM ( " if ($config->db_driver eq 'mssql');
	foreach (keys %table_names){
		push @messages_1, "SELECT hs_uid, adate, $table_pointers{$_}, xnum FROM $table_names{$_}  AS t3  $sql_restriction  " unless ($config->db_driver eq 'mssql');
		push @messages_1, "SELECT hs_uid, adate, $table_pointers{$_} as col, xnum FROM $table_names{$_}  AS t3  $sql_restriction  " if ($config->db_driver eq 'mssql');
		++$mess_cnt;
	}

	$sql_create1 .= join " UNION ", @messages_1;
	$sql_create1 .= ") as t3)" unless ($config->db_driver eq 'mssql');
	$sql_create1 .= ") as t3" if ($config->db_driver eq 'mssql');

	carp 'Temp Creation SQL = '.$sql_create1 . "\n";
##	my $sql_create1 = 'INSERT INTO ' . $main_temp . " (hs_uid, adate, name) (SELECT hs_uid, adate, full_name FROM  $table_names{'REG'} ". $sql_restriction . ")";
	$db->execute_sql( $sql_create1, 1);

# Create some indexes on that data
	print "\0";
	my $sql_create2 = 'CREATE INDEX ix1 ON ' . $main_temp . ' (hsuid, adate)';
	$db->execute_sql( $sql_create2, 1) if ($config->db_driver eq 'mysql');

	my $tname = 'mytmp2';

	$sql_create = "CREATE TEMPORARY TABLE $tname (tmpID " . $serial . ', hsuid VARCHAR(90), adate ' . $dte_time . ', TableCode INT'.$pkey unless ($config->db_driver eq 'mssql');
	$sql_create = "CREATE TABLE $tname (tmpID " . $serial . ', hsuid VARCHAR(90), adate ' . $dte_time . ', TableCode INT'.$pkey if ($config->db_driver eq 'mssql');
	$db->execute_sql( $sql_create, 1);

	my $sql_create1 = 'INSERT INTO '.$tname.' (hsuid, adate, tableCode) SELECT hsuid, adate, tableCode FROM ' . $main_temp ;
	$db->execute_sql( $sql_create1, 1);

	print "\0";
	my $sql_create2 = 'CREATE INDEX ix2 ON '.$tname.' (hsuid, adate)';
	$db->execute_sql( $sql_create2, 1) if ($config->db_driver eq 'mysql');


	my $sql_create3 = 'DELETE FROM ' . $main_temp . ' WHERE EXISTS ( SELECT hsuid FROM '.$tname.' t2 WHERE t2.hsuid = ' . $main_temp . '.hsuid AND ( t2.adate < ' . $main_temp . '.adate OR ( t2.adate = ' . $main_temp . '.adate AND t2.tableCode < ' . $main_temp . '.tableCode ) ) )';
	carp 'Report.pm Delete from temp: '.$sql_create3 . "\n";
	$db->execute_sql( $sql_create3, 1);

	print "\0";
	my $max_to_process = $settings{max_to_process} || '';
	carp 'REPORT.pm SQL statement - ' . $sql_statement_new;
	my @returned_recs;
	if ($max_to_process) {
		@returned_recs  =  $db->execute_sql_return( $sql_statement_new, 1, $max_to_process);
		}
	else	{
		@returned_recs  =  $db->execute_sql_return( $sql_statement_new, 1);
		}
	$jcnt=0;
	my @assessment_array;
	push @assessment_array, 'REG';
	my $assessments_array_ref = \@assessment_array;
	$X_Y{'reg'}{row} = 2;
	$X_Y{'reg'}{col} = 0;
	my %stuff = (
		assessment=> 'reg',
		report_name => 'participation',
		sheetname => 'participation',
		title => 'Assessment Participation Report',
		file_name => $set->{file_name},
		assessment_list => $assessments_array_ref,
		config_titles => $config_title_field
		);

# Output report in desired format
	print "Writing ". $settings{report_format} . "</br>";
	foreach my $this_user(@returned_recs){
		my %converted_user;
		my @record;
		foreach (@titles){
			if(exists $db_user_fields{'user'}{$_}){
				push @record, $this_user->{$db_user_fields{'user'}{$_}};
				$converted_user{$_} = $this_user->{$db_user_fields{'user'}{$_}};}
			else	{
				push @record, $this_user->{$db_user_more_fields{'user'}{$_}};
				$converted_user{$_} = $this_user->{$db_user_more_fields{'user'}{$_}};}
			}
		print "\0";

		if(uc($settings{report_format}) eq 'XML')
			{
			$workbook_ref = xml($config, \%converted_user, $workbook_ref, \%stuff );
			}
		elsif(uc($settings{report_format}) eq 'XLS' )
			{
			$workbook_ref = xls_basic_rows($config, \@titles, \%stuff, '') if ($jcnt == 0);
			$workbook_ref = xls_basic_rows($config, \@record, \%stuff, $workbook_ref, 1);
			}
		elsif(uc($settings{report_format}) eq 'CSV')
			{
			$workbook_ref = csv_basic($config, \@titles, \%stuff, \%converted_user, 0) if ($jcnt == 0);
			$workbook_ref = csv_basic($config, \@record, \%stuff, \%converted_user, 1);
			}
		++$jcnt;

		}
		
		if($stuff{report_name} eq 'participation' && $settings{report_format} eq 'XML')
		{
		my $output = $settings{file_name};
		open(XML, ">>$output" ) or die "Failed xml end file - $output\n$!"; 
		print XML "</hsdata>"; 
		close XML;
		}

# Drop the temporary table created above
    my $if_exists = 'if exists ' if ($config->db_driver eq 'mysql');
	my $sql_create = 'DROP TABLE ' . $if_exists . $main_temp;
	$db->execute_sql( $sql_create, 1);
	
	$db->finish;
	$db->disconnect;

	$$cnt_ref = $jcnt;

	}

sub xls_account
	{
	my $config = shift;
	my $settings = shift;
	my $PARMS = shift;

	my %set = %$settings;

	use Spreadsheet::WriteExcel;
	use Spreadsheet::WriteExcel::Utility;

	my ($yr,$mo,$da) = Date::Calc::Today();
	my $date = xl_date_list($yr,$mo,$da);

	# Create a new Excel workbook
	my $sheet_name = $set{file_name};
	my $workbook = Spreadsheet::WriteExcel->new($sheet_name);
	$workbook->compatibility_mode();
	#  Add and define a format
	my $bold = $workbook->add_format(bold => 1); # Add a format
	my $bold_center = $workbook->add_format(bold => 1);
	my $bold_right_bg = $workbook->add_format(bold => 1);
	$bold_right_bg->set_align('right');
	$bold_right_bg->set_bg_color(0x29);
	my $bold_right = $workbook->add_format(bold => 1);
	$bold_center->set_align('center');
	$bold_right->set_align('right');
	my $dates = $workbook->add_format(bold => 1); # Add a format
	$dates->set_num_format('yyyy-mm-dd');
	$dates->set_align('right');
	my $date_format = $workbook->add_format(bold => 1); # Add a format
	$date_format->set_num_format('mmm d yyyy');
	my $bg_blue = $workbook->add_format();
	$bg_blue->set_bg_color(0x29);


	{
	my $ws = $workbook->add_worksheet('Grouping');
	$ws->set_column('A:L', 15);
	$ws->write('A1', "HealthStatus Assessment Accounting Data - Group", $bold);
	$ws->write('A2', "$date", $date_format);
	my $row = 5;
	$ws->write('A5', "Grouping", $bold_center);
	$ws->write('B5', "Detail Level", $bold_center);
	$ws->write('C5', "Users", $bold_center);
	my $column = 3;
	foreach (sort @{$set{assessment_list}})
		{$ws->write(4, $column, $assessment_names_short{$_} , $bold_center); ++$column;}
	foreach my $group(sort keys %{$PARMS->{'accounting'}{'groups'}})
		{
		$ws->write($row, 0, $PARMS->{'accounting'}{'human'}{$group} , $bold_right);
		foreach my $specific_group(sort keys %{$PARMS->{'accounting'}{'groups'}{$group}})
			{
			$ws->set_row($row, undef, $bg_blue) if ($specific_group =~ m/\/$/);
			if ($specific_group =~ m/\/$/){$ws->write($row, 1, $specific_group , $bold_right_bg) ;}
			else {	$ws->write($row, 1, $specific_group , $bold_right);}
			$ws->write($row, 2, $PARMS->{'accounting'}{'groups'}{$group}{$specific_group}{users} );
			my $col = 3;
			foreach (sort @{$set{assessment_list}})
				{
#carp $group." - ".$specific_group." - ".$_;
				$ws->write($row, $col, $PARMS->{'accounting'}{'groups'}{$group}{$specific_group}{$_});
				++$col;
				}
			++$row;
			}
		++$row;
		}
	$ws->write($row, 0, "Total Users in Database" , $bold);
	$ws->write($row, 1, "All Groups" , $bold_right);
	$ws->write($row, 2, $PARMS->{'accounting'}{'group_total'}{'all'} );
	my $col = 3;
	foreach (sort @{$set{assessment_list}})
		{
		$ws->write($row, $col, $PARMS->{'accounting'}{'group_total'}{$_});
		++$col;
		}
	++$row;
	}

	{
	my $ws = $workbook->add_worksheet('Assessments');
	$ws->set_column('A:L', 15);
	$ws->write('A1', "HealthStatus Assessment Accounting Data - Assessment Totals", $bold);
	$ws->write('A2', "$date", $date_format);
	my $row = 4;
	my $col = 0;
	$ws->write($row, $col, "Time Period" , $bold_center);
	++$col;
	foreach (sort @{$set{assessment_list}})
		{$ws->write($row, $col, $assessment_names_short{$_} , $bold_center); ++$col;}
		$ws->write($row, $col, "Total" , $bold_center);
	++$row;
	foreach my $timeframe(sort keys %{$PARMS->{'accounting'}{'assessments'}})
		{
		my $col = 1;
		$ws->write($row, 0, $timeframe , $bold_right);
		my $beg_cell = xl_rowcol_to_cell($row, $col);
		foreach (sort keys %{$PARMS->{'accounting'}{'assessments'}{$timeframe}})
			{
			$ws->write($row, $col, $PARMS->{'accounting'}{'assessments'}{$timeframe}{$_} );
			++$col;
			}
		my $end_cell = xl_rowcol_to_cell($row, $col-1);
		$ws->write($row, $col, '=SUM('. $beg_cell . ':' . $end_cell . ')' );
		++$row;
		}
	}

	{
	my $ws = $workbook->add_worksheet('Daily Totals');
	$ws->set_column('A:L', 15);
	$ws->write('A1', "HealthStatus Assessment Accounting Data - Daily Assessment Totals", $bold);
	$ws->write('A2', "$date", $date_format);
	my $row = 5;
	my $col = 0;
	$ws->write($row, $col, "Date" , $bold_center);
	++$col;
	foreach (sort @{$set{assessment_list}})
		{
		$ws->write($row, $col, $assessment_names_short{$_} , $bold_center);
		++$col;
		}
	$ws->write($row, $col, "Total" , $bold_center);
	++$row;
	foreach my $timeframe(sort keys %{$PARMS->{'accounting'}{'daily_assessments'}})
		{
		$ws->write($row, 0, $timeframe , $dates);
		my $col = 1;
		my $beg_cell = xl_rowcol_to_cell($row, $col);
		foreach (sort keys %{$PARMS->{'accounting'}{'daily_assessments'}{$timeframe}})
			{
			$ws->write($row, $col, $PARMS->{'accounting'}{'daily_assessments'}{$timeframe}{$_} );
			++$col;
			}
		my $end_cell = xl_rowcol_to_cell($row, $col-1);
		$ws->write($row, $col, '=SUM('. $beg_cell . ':' . $end_cell . ')' );
		++$row;
		}
	}

	{
	my $ws = $workbook->add_worksheet('Monthly Totals');
	$ws->set_column('A:L', 15);
	$ws->write('A1', "HealthStatus Assessment Accounting Data - Monthly Assessment Totals", $bold);
	$ws->write('A2', "$date", $date_format);
	my $row = 5;
	my $col = 0;
	$ws->write($row, $col, "Date" , $bold_center);
	++$col;
	foreach (sort @{$set{assessment_list}})
		{
		$ws->write($row, $col, $assessment_names_short{$_} , $bold_center);
		++$col;
		}
	$ws->write($row, $col, "Total" , $bold_center);
	++$row;
	foreach my $timeframe(sort keys %{$PARMS->{'accounting'}{'monthly_assessments'}})
		{
		$ws->write($row, 0, $timeframe , $dates);
		my $col = 1;
		my $beg_cell = xl_rowcol_to_cell($row, $col);
		foreach (sort keys %{$PARMS->{'accounting'}{'monthly_assessments'}{$timeframe}})
			{
			$ws->write($row, $col, $PARMS->{'accounting'}{'monthly_assessments'}{$timeframe}{$_} );
			++$col;
			}
		my $end_cell = xl_rowcol_to_cell($row, $col-1);
		$ws->write($row, $col, '=SUM('. $beg_cell . ':' . $end_cell . ')' );
		++$row;
		}
	}

	return $workbook;
	}

sub xls_setup_basic
	{
	my $user = shift;
	my $config = shift;
	my $fname = shift;
	my $report = shift;

	use Spreadsheet::WriteExcel;
	use Spreadsheet::WriteExcel::Utility;

        # Create a new Excel workbook
        my $sheet_name = $fname;
        my $workbook = Spreadsheet::WriteExcel->new($sheet_name);
	$workbook->compatibility_mode();
      	return $workbook;
	}

sub xls_basic_sheet
	{
	my( $config, $user, $workbook, $var, $cells, $cell_vals ) = @_;

	use Spreadsheet::WriteExcel;
	use Spreadsheet::WriteExcel::Utility;

	my %hash = %$var;
	my %cell_locations = %$cells;
	my %cell_values = %$cell_vals;

	my $report = lc $hash{report_name};

	if( ref $workbook ne 'Spreadsheet::WriteExcel' )
		{
		print "initializing worksheet....<br>";
		$workbook = xls_setup_basic($user, $config, $hash{file_name}, $report);
		print "initializing done....<br>";
		}

        #  Add and define a format
        my $bold = $workbook->add_format(bold => 1); # Add a format
        my $date_format = $workbook->add_format(bold => 1); # Add a format
        $date_format->set_num_format('mmm d yyyy');

	my ($yr,$mo,$da) = Date::Calc::Today();
        my $date = xl_date_list($yr,$mo,$da);

	my %frmt=();
	my $ws = $workbook->add_worksheet($cell_values{'sheetname'});
	$ws->write('A1', "HealthStatus Aggregate Report Data - $cell_values{'title'}", $bold);
	$ws->write('F1', "$date", $date_format);
	foreach my $cell_detail (keys %cell_locations){
		$ws->write($cell_locations{$cell_detail}, $cell_values{$cell_detail});
		}
	return $workbook;
	}

sub xls_basic_rows
	{
	my( $config, $record_ref, $var, $workbook, $all_text ) = @_;

	use Spreadsheet::WriteExcel;
	use Spreadsheet::WriteExcel::Utility;

	my %hash = %$var;

	my $report = lc $hash{report_name};
	my $ws;

	if( ref $workbook ne 'Spreadsheet::WriteExcel' )
		{
		print "initializing worksheet....<br>";
		$workbook = xls_setup_basic($var, $config, $hash{file_name}, lc $hash{report_name});
		print "initializing done....<br>";
		$ws = $workbook->add_worksheet($hash{'sheetname'});
		}
        #  Add and define a format
        my $bold = $workbook->add_format(bold => 1); # Add a format
        my $date_format = $workbook->add_format(bold => 1); # Add a format
        $date_format->set_num_format('mmm d yyyy');

	my ($yr,$mo,$da) = Date::Calc::Today();
        my $date = xl_date_list($yr,$mo,$da);

	my $assessment = lc $hash{assessment} ;

	$ws = $workbook->sheets(0);

	my $row = $X_Y{$assessment}{row};
	my $col = $X_Y{$assessment}{col};

	my %frmt=();
	my $format2 = $workbook->add_format(num_format => '@');
	$ws->write('B1', "HealthStatus Report Data - $hash{'title'}", $bold);
	$ws->write('A1', "$date", $date_format);
	$ws->write($row, $col, $record_ref) if !$all_text;
	$ws->write($row, $col, $record_ref) if $all_text;
	$X_Y{$assessment}{row}++;

	return $workbook;
	}


sub xls_setup
	{
	my $user = shift;
	my $config = shift;
	my $fname = shift;
	my $report = shift;

	use Spreadsheet::WriteExcel;
	use Spreadsheet::WriteExcel::Utility;

	my ($yr,$mo,$da) = Date::Calc::Today();
        my $date = xl_date_list($yr,$mo,$da);

	# use the ggr_tables configuration setting to determine which assessments we use
	my @assessments = split /\s+/, $config->ggr_adv_tables;

        # Create a new Excel workbook
        my $sheet_name = $fname;
        my $workbook = Spreadsheet::WriteExcel->new($sheet_name);
	$workbook->compatibility_mode();
        #  Add and define a format
        my $bold = $workbook->add_format(bold => 1); # Add a format
        my $date_format = $workbook->add_format(bold => 1); # Add a format
        $date_format->set_num_format('mmm d yyyy');

        # Add a worksheet for each assessment
        my $cnt=0;
        foreach (@assessments){
        	my $assessment = lc($_);
		my $row_lookup = 'xls_' . $assessment . '_row';
		my $col_lookup = 'xls_' . $assessment . '_column';
		my $row = $X_Y{$assessment}{row} = $config->$row_lookup;
		my $col = $X_Y{$assessment}{col} = $config->$col_lookup;
		my $name = $assessment_names_short{ uc $assessment};
		my $ws = $workbook->add_worksheet($name);
		$ws->write($config->xls_title_cell, "HealthStatus Group Report Data - $name", $bold);
		$ws->write($config->xls_created_cell, "$date", $date_format);

		# get the user elements from the config fields
		my $config_title_field = 'rpt_' . $report . '_' . $assessment . '_fields';
		my @titles = split(" ",$config->$config_title_field);

		# write each element name in the title row
		my $risk_print = 0;
		foreach (@titles){
                	if($_ eq 'risk_print'){ $risk_print=1;next;}
			$ws->write($row, $col, $_, $bold);
			$col++;
			}
		if($risk_print && ($assessment eq 'gha' || $assessment eq 'hra')){
			my $risks  = HealthStatus::CalcRisk->calculate_risk($user, $config );
			$user->risk_data( $risks );
			for(my $i=1;$i<=43;$i++){
				my $risk = $user->risk_data->record( $i )->{ name };
				$ws->write($row, $col, $risk , $bold);
				$ws->write($row, $col+1, "Average $risk" , $bold);
				$ws->write($row, $col+2, "Achievable $risk" , $bold);
        			$col=$col+3;
				}
			}
		$X_Y{$assessment}{row}++;
		$X_Y{$assessment}{sheet} = $cnt;
		$cnt++;
		$X_Y{$assessment}{written} = 0;
	       }

      	return $workbook;
	}

sub xls
	{
	my( $config, $user, $workbook, $var ) = @_;

	use Spreadsheet::WriteExcel;
	use Spreadsheet::WriteExcel::Utility;

	my %hash = %$var;

	my $report = lc $hash{report_name};

	if( ref $workbook ne 'Spreadsheet::WriteExcel' )
		{
		print "initializing worksheet....<br>";
		$workbook = xls_setup($user, $config, $hash{file_name}, $report);
		print "initializing done....<br>";
		}

	my %frmt=();

	my $assessment = lc $hash{assessment} ;

	my $name = $assessment_names_short{ uc $assessment};
	my $row = $X_Y{$assessment}{row};
	my $col = $X_Y{$assessment}{col};

	# get the user elements from the config fields
	my $config_title_field = 'rpt_' . $report . '_' . $assessment . '_fields';
	my @titles = split(" ",$config->$config_title_field);

	my $ws = $workbook->sheets($X_Y{$assessment}{sheet});
	my $risk_print = 0;
        foreach (@titles){
                if($_ eq 'risk_print'){ $risk_print=1;next;}
        	my $val = $user->{$_};
        	$ws->keep_leading_zeros();
        	$ws->write($row, $col, $val );
        	$col++;
        	}
		if($risk_print && ($assessment eq 'gha' || $assessment eq 'hra')){
			for(my $i=1;$i<=43;$i++){
				my $risk = sprintf("%.4f",($user->risk_data->record( $i )->{ user_risk } * 1000));
				$ws->write($row, $col, $risk);
				$risk = sprintf("%.4f",($user->risk_data->record( $i )->{ average_risk } * 1000));
				$ws->write($row, $col+1, $risk);
				$risk = sprintf("%.4f",($user->risk_data->record( $i )->{ achievable_risk } * 1000));
				$ws->write($row, $col+2, $risk);
        			$col=$col+3;
				}
			}
        $X_Y{$assessment}{row}++;
	$X_Y{$assessment}{written}++;

        return $workbook;

	}

sub xml
	{
	my( $config, $user, $xml_work, $var ) = @_;

	my %hash = %$var;
	use XML::Simple;

	my %xml_frmt;

	my $assessment = lc $hash{assessment} ;
	my $report = lc $hash{report_name};

	my $name = $assessment_names_short{ uc $assessment};
	$xml_frmt{$assessment}{'assessment_names_short'} = $assessment_names_short{ uc $assessment};
	# get the user elements from the config fields
	my $config_title_field = $hash{'config_titles'}  || 'rpt_' . $report . '_' . $assessment . '_fields';
	my @titles = split(" ", $config->$config_title_field);

       foreach (@titles){
       		$xml_frmt{$assessment}{$_} = $user->{$_};
       	}

    	my $xml = XMLout(\%xml_frmt, RootName => 'hs_assessment', NoAttr => 1, SuppressEmpty => 1);

	my $output = $hash{file_name};

	if($xml_work)	{
		open(XML, ">>$output" ) or die "Failed xml open - $output\n$!";}
	else	{
		open(XML, ">$output" ) or die "Failed xml user - $output\n$!"; print XML "<hsdata>\n";}

	print XML $xml;
	close XML;

        return 1;

	}
sub csv
	{
	my( $config, $user, $csv_work, $var ) = @_;

	use Text::CSV;

	my %hash = %$var;

	my $assessment = lc $hash{assessment} ;
	my $report = lc $hash{report_name};

#
#	# get the user elements from the config fields
	my $config_title_field = $hash{'config_titles'}  || 'rpt_' . $report . '_' . $assessment . '_fields';
	my @titles = split(" ",$config->$config_title_field);

	my @record= ();
	push @record, $assessment;
	my $risk_print=0;
       	foreach (@titles){
                if($_ eq 'risk_print'){ $risk_print=1;next;}
	       	my $val = $user->{$_};
	       	push @record, $val;
       	}
	if($risk_print && ($assessment eq 'gha' || $assessment eq 'hra')){
		for(my $i=1;$i<=43;$i++){
			my $risk = sprintf("%.4f",($user->risk_data->record( $i )->{ user_risk } * 1000));
			push @record, $risk;
			$risk = sprintf("%.4f",($user->risk_data->record( $i )->{ average_risk } * 1000));
			push @record,  $risk;
			$risk = sprintf("%.4f",($user->risk_data->record( $i )->{ achievable_risk } * 1000));
			push @record,  $risk;
			}
		}

	my $ok= csv_basic($config, \@record, $var, $user, $csv_work);

        return 1;

	}

sub csv_basic
	{
	my ( $config, $record_ref, $var, $user, $csv_work) = @_;

	use Text::CSV;

	my %hash = %$var;
	my @record = @$record_ref;

	my $assessment = lc $hash{assessment} ;
	my $report = lc $hash{report_name};
	
	my $seperator = $config->ggr_divider_character || ",";
	my $quotes = $config->ggr_quote_character || '"';
	$quotes = '' if $config->ggr_no_quotes;

 	my $csv = Text::CSV->new({sep_char => $seperator, quote_char => $quotes, binary => 1});
 	
	my $status = $csv->combine(@record);

	my $line = $csv->string();

	my $output = $hash{file_name};;

	if($csv_work)	{
		open(CSV, ">>$output" ) or die "Failed csv open - $output\n$!";}
	else	{
		open(CSV, ">$output" ) or die "Failed csv open - $output\n$!";
		# write each element name in the title row
		my @assessment_list = @{$hash{assessment_list}};
		foreach my $al (@assessment_list)
			{
			my $config_title_field = $hash{'config_titles'}  || 'rpt_' . $report . '_' . lc($al) . '_fields';
			my @a_titles = split(" ",$config->$config_title_field);
			my @a_record = ();
			push @a_record, lc($al);
			my $risk_print_1=0;
			foreach (@a_titles){
                		if($_ eq 'risk_print'){ $risk_print_1=1;next;}
				push @a_record, $_;
				}
			if($risk_print_1 && (lc($al) eq 'gha' ||lc($al) eq 'hra' )){
				my $risks  = HealthStatus::CalcRisk->calculate_risk($user, $config );
				$user->risk_data( $risks );
				for(my $i=1;$i<=43;$i++){
					my $risk = $user->risk_data->record( $i )->{ name };
					push @a_record,$risk;
					push @a_record, "Average $risk";
					push @a_record, "Achievable $risk";
					}
				}
			my $a_status = $csv->combine(@a_record);
			my $t_line = $csv->string();
			print CSV $t_line . "\n";
			}
		}
	print CSV $line . "\n";
	close (CSV);


        return 1;

	}

1;