#!/usr/local/bin/perl
use strict;

=head1 NAME

ptracker.cgi - personal tracker

=head1 DESCRIPTION

This program will keep track and graph user vital health statistics and
measures.

=head1 INPUT

action parameter can be one of the following:
	ptshow 
	savept1 
	savept2 
	pt_review 
	review

=head2 OUTPUT


=head1 ERRORS

=cut

use File::Basename        qw( dirname );
use File::Spec::Functions qw( rel2abs );

use lib dirname(rel2abs($0)),'.','/usr/local/www/vhosts/managed2/modules/pdf', '/usr/local/www/vhosts/managed2/modules';

use vars qw( $Debug $production $cook $config_file);

use vars qw( %Tables %Fields );
=head1 Name
ptracker.cgi- personal health measure information of users

=cut


use subs qw( error );

if (!do('common.inc')) {
   my $error = $@ ? $@
             : $! ? $!
             : 'did not return a true value';
   die("Unable to load common stuff: $error\n");
}
use CGI qw(-no_xhtml -debug);
use CGI::Carp qw(fatalsToBrowser);
use Date::Calc;

use HealthStatus qw( fill_and_send error html_error );
use HealthStatus::Authenticate;
use HealthStatus::CalcRisk;
use HealthStatus::Config;
use HealthStatus::Constants;
use HealthStatus::Database;
use HealthStatus::User;
use HealthStatus::PT;
use perlchartdir;
use Date::Calc::Iterator;
my $input = new CGI();
my $config = getConfig($input->param('extracfg'));

my %hash = map { $_, $input->param($_) } $input->param();

my %config = map { $_, $config->$_ } $config->directives;

$hash{config} = \%config;

my %input = $input->Vars();
my($have_a_bmi,$have_a_bfat,$have_a_hdl,$have_a_chol,$have_a_dbp,$have_a_sbp,$have_a_hip,$have_a_waist,$have_a_neck)=(0,0,0,0,0,0,0,0,0);

############################################################################
### Comment out the following line before going into production ############
$Debug = $input->param("HS_Debug") || $ENV{HS_DEBUG} || $Debug if !$production;
#### only uncomment if you need to debug the input scripts      ############
############################################################################

# authenticate_user redirects the user if they not allowed to
# view this page
my $user = authenticateUser('', $input, $config) or die "You should never see this message.";

## common.inc does this for us, don't need it.
my $config_file = '/usr/local/www/vhosts/managed2/base/conf/healthstatus.conf';
print "Config file = $config_file\n" if $Debug;
$config->set( "config_file", $config_file );

my $db = HealthStatus::Database->new( $config );
$db->debug_on( \*STDERR) if $Debug; 
# place the db_handle into the config for passing to other routines.
$config->set( "db_handle", $db );
if ($Debug) {
	print "Content-type: text/plain\n\n";
	$config->pretty_print if $Debug;
	my %config_dump = map { $_, $config->$_ } $config->directives;
	foreach my $t_key (sort keys %config_dump)
		{
		print "$t_key = " . $config_dump{$t_key} . "\n";
		}
	print " *********  HS_IDENT Cookies or param ************************\n";
	print "This is what I see in the cookie hs_ident - ". $input->cookie('hs_ident')  . "\n" ;
	print "This is what I see in the parameter hs_ident - ". $input->param('hs_ident')  . "\n" ;
	print " **************************************************************\n";
	$user->pretty_print;
}

my %Allowed_actions = map { ( $_, 1 ) }
	 qw(ptshow savept1 savept2 pt_review review);
my $action = lc $input->param('action');


print "Action = $action\n" if $Debug;
unless (exists $Allowed_actions{$action}){
	my $form = $config->template_directory . $config->login_register_retry;
	$hash{error_msg} = "That action is not permitted, please login again.";
	fill_and_send( $form, $user, \%hash, $config->html_use_ssi );
	exit;
	}
	
	if($action eq 'review')
	{
## just do this
		my $where = " where hs_uid='".$user->db_id."'";
		my $count = $db->hs_count('PT', $where);

		if($count >= 1)
		{
			my $form = $config->template_directory . $config->ptreview;
			$hash{pt_title} = $config->pt_title1;
			$hash{ptracker} = 'pt_review';
			fill_and_send( $form, $user, \%hash, $config->html_use_ssi );
		}
		else
		{
## we just rearrange the order of the action checks, and if we get to here we need to do ptshow, we just change the action
			$action = 'ptshow';
		}
	}
	if($action eq 'ptshow')
	{		
		my $status=$db->get_users_first_assessment($user, $config, 'PT');
		if(!$status)
		{
			my $form = $config->template_directory . $config->pt_user_input;
			$hash{pt_title} = $config->pt_title1;
			$hash{ptracker} = 'savept1';
			fill_and_send( $form, $user, \%hash, $config->html_use_ssi );
			exit;
		}
		else
		{
			$action = 'savept1';
		}
	}
	if($action eq 'savept1')
	{
		my $form = $config->template_directory . $config->pt_medical_specific_info;
		$hash{pt_title} = $config->pt_title1;
		$hash{ptracker} = 'savept2';
		my @ignore = ('weight','bp_dias','bp_sys','cholesterol','hdl','waist','hip','neck');
		fill_and_send( $form, $user, \%hash, $config->html_use_ssi, \@ignore );
		exit;
	}
## reorganized this to save the assessment then change the action to pt_review and pass it along
	if($action eq 'savept2')
	{
		$db->save_users_assessment($user,'PT');	
		$action = 'pt_review';
	}
		
	if($action eq 'pt_review')
	{
		my $graph_type = $input->param('graph_type')||30;
		my $id = $user->db_id;
## instead of all these individual variables, one hash, or a hash per graph would make much more sense, then you just pass the reference of the one hash
		my($wimage,$bmimage,$bfimage,$hdlimage,$cholimage,$bpimage,$mesimage,$wieghtcount);
## instead of having this call in each graph type, just call it here, then proceed.
		my ($bmi,$bodyfat,$lowweight,$highweight,$dcr,$idealweight,$lean_mass,$lean_ideal,$thr_low,$thr_medium,$thr_high,$waist_to_hip,$waist_to_hip_shape,$date,$bmi_al,$bmi_ah,$bmi_opti,$bmi_uhl,$bmi_uhh,$maxbmi,$fat_average,$fat_ideal,$fat_fitlow,$fat_fithigh,$fat_noeat,$maxbfat,$hdl_min,$hdl_zero,$hdl,$maxhdl,$chol_lgreen,$chol_red,$chol_min,$chol_max,$maxchol,$chol,$bp_sys,$maxbp_sys,$bp_dias,$maxbp_dias,$bp_average,$bp_limit,$bp_max,$hip,$neck,$waist,$startdate,$enddate,$bmi_min,$bmi_max,$have_a_bmi,$have_a_bfat,$have_a_hdl,$have_a_chol,$have_a_dbp,$have_a_sbp,$have_a_hip,$have_a_waist,$have_a_neck,$ydate,$have_a_weight,$weight,$max_weight,$high_range,$low_range,$ideal_range)=get_content_onemonth($config, $user, $graph_type);
## I consolidated all the graphs into one routine, set the length of graph you want in months (1,3,6,12 or 60) would need to 
## make it smarter to handle any months but that would not be hard
		my $length = 1;
		if($input->param('graph_type')==90)
		{
			$length=3;
		}
		if($input->param('graph_type')==180)
		{
			$length=6;
		}
		if($input->param('graph_type')==365)
		{
			$length=12;
			
		}
		if($input->param('graph_type')==1825)
		{
			$length=60;
		}
## renamed the graph routine, added length to the call
##		create_PT_graph($length,'bmi',$config,$date,$startdate,$enddate,$bmi,$bmi_al,$bmi_ah,$bmi_opti,$bmi_uhl,$bmi_uhh,$maxbmi,$bmi_min,$bmi_max);
		create_PT_graph($length,'bmi',$config,$date,$startdate,$enddate,$bmi,$maxbmi,);
		create_PT_graph($length,'bfat',$config,$date,$startdate,$enddate,$maxbfat,$bodyfat);
		create_PT_graph($length,'waist',$config,$date,$startdate,$enddate,$waist_to_hip,$waist_to_hip_shape);
		create_PT_graph($length,'hdl',$config,$date,$startdate,$enddate,$hdl_min,$hdl_zero,$hdl,$maxhdl);
		create_PT_graph($length,'chol',$config,$date,$startdate,$enddate,$chol_min,$chol_max,$chol_red,$chol_lgreen,$maxchol,$chol);
		create_PT_graph($length,'bp',$config,$date,$startdate,$enddate,$bp_sys,$maxbp_sys,$bp_dias,$maxbp_dias,$bp_average,$bp_limit,$bp_max);
		create_PT_graph($length,'mes',$config,$date,$startdate,$enddate,$hip,$neck,$waist);
		create_PT_graph($length,'weight',$config,$date,$startdate,$enddate,$weight,$low_range,$high_range,$ideal_range,$max_weight);
		
		$wimage = $id."_weight_". $length . ".png";
		$bmimage = $id."_bmi_". $length . ".png";
		$bfimage = $id."_bfat_". $length . ".png";
		$hdlimage = $id."_hdl_". $length . ".png";
		$cholimage = $id."_chol_". $length . ".png";
		$bpimage = $id."_bp_". $length . ".png";
		$mesimage = $id."_mes_". $length . ".png";
			
		my $form = $config->template_directory . $config->ptreview;
		
## we are moving the graphic name to the hash not the whole image tag, then we can do other things with the images if we want in the output step
## email, pdf files or html, keeping logic and output as separate as possible		
		$hash{wimage}=$wimage ;
		$hash{bmimage}=$bmimage;
		$hash{bfimage}=$bfimage;
		$hash{hdlimage}=$hdlimage;
		$hash{cholimage}=$cholimage;
		$hash{bpimage}=$bpimage;
		$hash{mesimage}=$mesimage;
		$hash{wieghtcount}=$have_a_weight ;
		$hash{have_a_bmi}=$have_a_bmi;
		$hash{have_a_bfat}=$have_a_bfat;
		$hash{have_a_hdl}=$have_a_hdl;
		$hash{have_a_chol}=$have_a_chol;
		$hash{have_a_dbp}=$have_a_dbp;
		$hash{have_a_sbp}=$have_a_sbp;
		$hash{have_a_hip}=$have_a_hip;
		$hash{have_a_waist}=$have_a_waist;
		$hash{have_a_neck}=$have_a_neck;
		fill_and_send( $form, $user, \%hash, $config->html_use_ssi );
		exit;
	}
## these two functions are almost too short to make functions
## you are replacing one line of code in the program with one line of code to call the function
	#################################################
	#function: get_before_date
	#argument: No. of days
	#Description: returns dates
	################################################
	sub get_before_date
	{
		my $noof_days = shift;
		my ($mday, $mon, $year) = (localtime(time()-($noof_days*24*60*60)))[3,4,5];
		return(sprintf("%04d-%02d-%02d", $year+1900, $mon+1, $mday),sprintf("%02d-%02d-%04d-",  $mon+1, $mday,$year+1900));
        }
	sub datesplit
	{
		my $date = shift;
		my ($year,$month,$date) = split(/-/,$date,3);
		return ($year,$month,$date);
		
	}
	#################################################
	#function: get_content_onemonth
	#argument: configuration,userelement and graph type
	#Description: generates values which are required for the creation of graph
	################################################
	sub get_content_onemonth
	{
		my ($config, $user, $graph_type) = @_;
		$db->debug_on( \*STDERR ) if $Debug;
		my $db = $config->db_handle;
		my (@bmi,@bodyfat,@weight,@lowweight,@highweight,@dcr,@idealweight,@lean_mass,@lean_ideal,@thr_low,@thr_medium,@thr_high,@waist_to_hip,@date,@waist_to_hip_shape,@hdl,@chol);
		my (@bmi_al,@bmi_ah,@bmi_opti,@bmi_uhl,@bmi_uhh,@fat_average,@fat_ideal,@fat_fitlow,@fat_fithigh,@fat_noeat,@hdl_min,@hdl_zero,@chol_lgreen,@chol_red,@chol_min,@chol_max);
		my(@bp_sys,@bp_dias,$maxbp_sys,$maxbp_dias,$max_weight,@bp_average,@bp_limit,@bp_max,@hip,@neck,@waist,@bmi_min,@bmi_max,@ydate);
		my $maxweight = 0;
                my $have_a_weight = 0;
		my $maxbmi=0;
		my $maxbfat = 0;
		my $maxhdl = 0;
		my $maxcol = 0;
		$db->get_users_first_assessment($user, $config, 'PT');
		my $health = HealthStatus->new(
				{
					assessment => 'PT',
					user       => $user,
					config     => $config->config_file,
				}      );
		my ($low,$high,$ideal)=($user->low_weight,$user->high_weight,$user->ideal_weight);
		my($fat_average,$fat_ideal,$fat_fitlow,$fat_fithigh);
		my (@high_range,@low_range,@ideal_range);
		if($user->sex eq MALE)
		{
			$fat_average=23;
			$fat_ideal=15;
			$fat_fitlow=5;
			$fat_fithigh=10;
		}
		else
		{
			$fat_average=32;
			$fat_ideal=22;
			$fat_fitlow=15;
			$fat_fithigh=20;
		}
		#my $startdate=0;
		#my $enddate;		

## this date is a mess, the beginning date is the first date we want, and the end_date is now		
## this organizes it that way
		my ($beg_date,$startdate) = get_before_date($graph_type);
		my ($end_date,$enddate) = get_before_date($startdate);
		#$startdate = $beg_date;
		#$enddate = $end_date;
## get only the assessments we are configured to run for group reporting
	my @assessments = split(/\s/,$config->ggr_adv_tables);
## add PT to the assessments
	push  @assessments, 'PT';
## added a routine to HealthStatus::Database to return table names
## whenever possible we want to do database stuff in the database modules
        my $table_hash = $db->table_names(\@assessments);
        
	my $sql = " Select * from (select adate, Weight, 'EMPTY' as Feet, Inches, BPsys, BPdias, CHOL, HDL, Waist, Hip, Neck, Units, '1PT' as assessment from ".$table_hash->{'PT'}." where hs_uid='".$user->db_id."' Union"
		." select adate, Weight, Feet, Inches, BPsys, BPdias, CHOL, HDL, 'EMPTY' ,'EMPTY' ,'EMPTY' , Units, '2HRA' as assessment from ".$table_hash->{'HRA'}." where hs_uid='".$user->db_id."' Union"
		." select adate, Weight, Feet, Inches, BPsys, BPdias, CHOL, HDL, 'EMPTY' ,'EMPTY' ,'EMPTY' , Units, '3GHA'  as assessment from ".$table_hash->{'GHA'}." where hs_uid='".$user->db_id."' Union"
		." select adate, Weight, 'EMPTY' as Feet, Height, 'EMPTY', 'EMPTY', 'EMPTY', 'EMPTY', 'EMPTY', 'EMPTY', 'EMPTY', Units, '6FIT'  as assessment from ".$table_hash->{'FIT'}." where hs_uid='".$user->db_id."' Union"
		." select adate, Weight, Feet, Inches, BPsys, BPdias, CHOL, HDL, 'EMPTY' ,'EMPTY' ,'EMPTY' , Units, '4CRC' as assessment from ".$table_hash->{'CRC'}." where hs_uid='".$user->db_id."' ) as t1 order by adate, assessment";
#		print"Content-type:text/html\n\n";
		
	my @results = $db->execute_sql_return($sql,1);
		my %raw_data;
		my %datelist;
		my %dataassess;
## added a hash to use as starting plot data
		my %starting_points;
		# this block gets executed for each returned record (may be several for a day)
## load the hash with data from each day that we have found data
		foreach(@results)
		 {
			my %temp_hash = %$_;
			my @day = split(/\s/,$temp_hash{'adate'});
			my $date_to_save = $day[0];
			 $raw_data{$date_to_save}{'weight'} = $temp_hash{'Weight'} if ($temp_hash{'Weight'}  && !exists $raw_data{$date_to_save}{'weight'});
			 $maxweight = $raw_data{$date_to_save}{'weight'} + 25 if ( $raw_data{$date_to_save}{'weight'} + 25 > $maxweight );
			 
			 if($temp_hash{'assessment'} eq '6FIT')
			 {
				$raw_data{$date_to_save}{'height'} = $temp_hash{'Height'} if ($temp_hash{'Height'} && !exists $raw_data{$date_to_save}{'height'});
			 }
			 else
			 {
				$raw_data{$date_to_save}{'height'} = $temp_hash{'Inches'} if ($temp_hash{'Inches'} && !exists $raw_data{$date_to_save}{'height'} && $temp_hash{'Inches'} > 12 );
				$raw_data{$date_to_save}{'height'} = ($temp_hash{'Feet'} * 12) + $temp_hash{'Inches'} if ($temp_hash{'Inches'} && !exists $raw_data{$date_to_save}{'height'} && $temp_hash{'Inches'} < 12 );
			 }
			 
			 $raw_data{$date_to_save}{'bp_sys'} = $temp_hash{'BPsys'} if ($temp_hash{'BPsys'} && ((!exists $raw_data{$date_to_save}{'bp_sys'}) || (lc($temp_hash{'bp_sys'}) ne 'empty' && lc($temp_hash{'bp_sys'}) ne 'null')) && ($temp_hash{'BPsys'} ne 'EMPTY') );
			 $raw_data{$date_to_save}{'bp_dias'} = $temp_hash{'BPdias'} if ($temp_hash{'BPdias'} && ((!exists $raw_data{$date_to_save}{'bp_dias'})|| (lc($temp_hash{'bp_dias'}) ne 'empty' && lc($temp_hash{'bp_dias'}) ne 'null'))&& ($temp_hash{'BPdias'} ne 'EMPTY') );
			 
			 $raw_data{$date_to_save}{'cholesterol'} = $temp_hash{'CHOL'} if ($temp_hash{'CHOL'} && ((!exists $raw_data{$date_to_save}{'cholesterol'})|| (lc($temp_hash{'cholesterol'}) ne 'empty' && lc($temp_hash{'cholesterol'}) ne 'null'))&& ($temp_hash{'CHOL'} ne 'EMPTY') );
			 
			 $raw_data{$date_to_save}{'hdl'} = $temp_hash{'HDL'} if ($temp_hash{'HDL'} && ((!exists $raw_data{$date_to_save}{'hdl'})|| (lc($temp_hash{'hdl'}) ne 'empty' && lc($temp_hash{'hdl'}) ne 'null'))&& ($temp_hash{'HDL'} ne 'EMPTY') );
			 
			 $raw_data{$date_to_save}{'waist'} = $temp_hash{'Waist'} if ($temp_hash{'Waist'} && ((!exists $raw_data{$date_to_save}{'waist'})|| (lc($temp_hash{'waist'}) ne 'empty' && lc($temp_hash{'waist'}) ne 'null'))&& ($temp_hash{'Waist'} ne 'EMPTY') );
			 
			 $raw_data{$date_to_save}{'hip'} = $temp_hash{'Hip'} if ($temp_hash{'Hip'} && ((!exists $raw_data{$date_to_save}{'hip'})|| (lc($temp_hash{'hip'}) ne 'empty' && lc($temp_hash{'hip'}) ne 'null'))&& ($temp_hash{'Hip'} ne 'EMPTY') );
			 
			 $raw_data{$date_to_save}{'neck'} = $temp_hash{'Neck'} if ($temp_hash{'neck'} && ((!exists $raw_data{$date_to_save}{'neck'})|| (lc($temp_hash{'neck'}) ne 'empty' && lc($temp_hash{'neck'}) ne 'null'))&& ($temp_hash{'Neck'} ne 'EMPTY') );
			 
			 $datelist{$date_to_save}=$date_to_save if (!exists $datelist{$date_to_save});
			if ($date_to_save <= $beg_date) {
## we do it this way because we may not have every field for each date so we keep adding the more recent one to the starting_points
## hash until we get to the beg_date
				 my %temp_hash = %{$raw_data{$date_to_save}};
				 foreach (keys %temp_hash){
					$starting_points{$_} = $temp_hash{$_};
				}
			}
		}
	my (@dates1,@dates);
	my($byear,$bmonth,$bdate) = datesplit($beg_date);
	my($eyear,$emonth,$edate) = datesplit($end_date);
	my @byear = ($byear,$bmonth,$bdate);
	my @eyear = ($eyear,$emonth,$edate);
	carp "dates: $beg_date to $end_date\n";
	my $i1 = Date::Calc::Iterator->new(from => [@byear], to => [@eyear]) ;
	push @dates1,$_ while $_ = $i1->next ;
	my($cont_weight,$cont_bmi,$cont_chol,$cont_bpsys,$cont_bpdias,$cont_hdl,$cont_bfat,$cont_dcr,$cont_hip,$cont_neck,$cont_waist,$cont_high_weight,$cont_low_weight,$cont_ideal_weight,$cont_lean_mass,$cont_lean_ideal,$cont_thr_low,$cont_thr_medium,$cont_thr_high,$cont_waist_to_hip,$cont_waist_to_hip_shape);
	
	foreach my $dates1 (@dates1)
	{
## this is much cleaner
		push(@dates, sprintf("%04d-%02d-%02d", @$dates1->[0], @$dates1->[1], @$dates1->[2]));		
	}
	my %counters;
## datecount is initialized here
	my $datecount = 0;
	my $user1;
		foreach my $date (@dates)		
		{	
			my($xyear,$xmonth,$xdate) = datesplit($date);
			my $mdate = $xmonth."-".$xdate;
			push(@date,$mdate);
			my $fresh_data=0;
			if(exists $datelist{$date} || $datecount == 0){
## this little section initializes the user for each pass
## it was set with a bunch of if statements into raw_data
## flipping it and setting this hash makes it cleaner and easier to read
## none of the values except height exist in our SQL statement so there was no 
## need for the ifs it should also remove all the need for the $cont_ values (if they are what I think they are....
				my %this_day_hash;
				%this_day_hash = %starting_points if $datecount == 0;
				%this_day_hash = %{$raw_data{$datelist{$date}}} if exists $datelist{$date};
				$this_day_hash{'height'} = $user->height if(!exists($raw_data{$datelist{$date}}{'height'})|| !defined($this_day_hash{'height'}));
				$this_day_hash{'sex'} = $user->sex ;
				$this_day_hash{'first_name'} = $user->first_name;
				$this_day_hash{'last_name'} = $user->last_name;				
				$this_day_hash{'full_name'} = $user->db_fullname;				
				$this_day_hash{'birth_month'} = $user->birth_month;				
				$this_day_hash{'birth_date'} = $user->birth_date;				
				$this_day_hash{'birth_year'} = $user->birth_year;				
				$this_day_hash{'units'} = $user->units || IMPERIAL;				
				 if (!exists($this_day_hash{hip}))
				 {
					$this_day_hash{hip} = '';
				 }				 
				 if($this_day_hash{hip} eq 'EMPTY')
				 {
					$this_day_hash{hip} = '';
				 }
				 $user1 = HealthStatus::User->new( \%this_day_hash );
				 $health->assess( $user1 );
				 $fresh_data=1;
			}
## end of the datelist if 
## then load the array with either fresh data or the nodata value
			if($user1->bmi && $fresh_data)
			{
				push(@bmi,$user1->bmi);
				$counters{'bmi'}++ if $datecount != 0;
				$maxbmi = $user1->bmi if ($user1->bmi > $maxbmi);
			}
			else	
			{
				push(@bmi,'1.7E+308');
			}
			if($user1->body_fat_percent && $fresh_data)
			{
				$counters{'bfat'}++ if $datecount != 0;
				push(@bodyfat,$user1->body_fat_percent);
                        }
			else	
			{
				push(@bodyfat,'1.7E+308');
			}
			if($user1->daily_caloric_requirements && $fresh_data)
			{					
				$counters{'dcr'}++ if $datecount != 0;
				push(@dcr,$user1->daily_caloric_requirements);
			}
			else
			{
				push(@dcr,'1.7E+308') ;
			}

## graph this on the weight graph
				if($user1->lean_mass && $fresh_data)
				{					
					push(@lean_mass,$user1->lean_mass);
				}
				else
				{					
				       push(@lean_mass,'1.7E+308');
				}
## graph this on the weight graph
				if($user1->lean_ideal && $fresh_data)
				{					
					push(@lean_ideal,$user1->lean_ideal);
				}
				else
				{				    
					push(@lean_ideal,'1.7E+308');	       
				}
				if($user1->thr_low && $fresh_data)
				{				
					push(@thr_low,$user1->thr_low);				
				}
				else
				{				    
					push(@thr_low,'1.7E+308');				
				}
				if($user1->thr_medium && $fresh_data)
				{
					push(@thr_medium,$user1->thr_medium);					
				}
				else
				{
				       push(@thr_medium,'1.7E+308');
				}
				if($user1->thr_high && $fresh_data)
				{
					push(@thr_high,$user1->thr_high);
				}
				else
				{	
				       push(@thr_high,'1.7E+308');
				}
				if($user1->waist_to_hip && $fresh_data)
				{				
					push(@waist_to_hip,$user1->waist_to_hip);			
				}
				else
				{					
						push(@waist_to_hip,'1.7E+308');					
				}
				if($user1->waist_to_hip_shape && $fresh_data)
				{				
					push(@waist_to_hip_shape,$user1->waist_to_hip_shape);
				}
				else
				{					
					push(@waist_to_hip_shape,'1.7E+308');					
				}
				if($user1->hdl && $fresh_data)
				{					
					$counters{'hdl'}++ if $datecount != 0;
					push(@hdl,$user1->hdl);	    
					if($user1->hdl > $maxhdl)
					{
						$maxhdl= $user1->hdl;
					}
				}
				else
				{				
					push(@hdl,'1.7E+308') ;				
				}
				if($user1->cholesterol && $fresh_data)
				{				
					$counters{'chol'}++ if $datecount != 0;
					push(@chol,$user1->cholesterol);
					if($user1->cholesterol > $maxcol)
					{
						$maxcol= $user1->cholesterol;
					}
				}
				else
				{
					$counters{'chol_not'}++;		
                           		push(@chol,'1.7E+308') ;		
				}
				if($user1->bp_sys && $fresh_data)
				{					
					$counters{'bp_sys'}++ if $datecount != 0;
					push(@bp_sys,$user1->bp_sys);				    
					if($user1->bp_sys > $maxbp_sys)
					{
						$maxbp_sys= $user1->bp_sys;
					}
				}
				else
				{
					$counters{'bp_sys_not'}++;					
				       push(@bp_sys,'1.7E+308') ;					
				}
				if($user1->bp_dias && $fresh_data)
				{					
					$counters{'bp_dias'}++ if $datecount != 0;
					push(@bp_dias,$user1->bp_dias);			      
					if($user1->bp_sys > $maxbp_dias)
					{
						$maxbp_dias= $user1->bp_dias;
					}
				}
				else
				{
					$counters{'bp_dias_not'}++;					
					push(@bp_dias,'1.7E+308') ;					
				}
				if($user1->hip && $fresh_data)
				{									
					$counters{'hip'}++ if $datecount != 0;
					push(@hip,$user1->hip);				       
				}
				else
				{
					$counters{'hip_not'}++;				    
					push(@hip,'1.7E+308');
				       
				}
				if($user1->neck && $fresh_data)
				{	
					$counters{'neck'}++ if $datecount != 0;				
					push(@neck,$user1->neck);					
				}
				else
				{
					$counters{'neck_not'}++;					
					push(@neck,'1.7E+308');					
				}
				if($user1->waist && $fresh_data)
				{					
					$counters{'waist'}++ if $datecount != 0;
					push(@waist,$user1->waist);					
				}
				else
				{
					$counters{'waist_not'}++;					
					push(@waist,'1.7E+308');					
				}
				if($user1->weight && $fresh_data)
				{
					$counters{'weight'}++ if $datecount != 0;
					push(@weight,$user1->weight);
## $maxweight was set up above as weight + 25, now $max_weight is being set as = weight
					if($user1->weight > $max_weight)
					{
						$max_weight= $user1->weight;
					}					
				}
				else
				{
					$counters{'weight_not'}++;					
				        push(@weight,'1.7E+308') ;
					
				}			      
## increment datecount from up above
			++$datecount;			
		}
## you always push some value onto the array, so these are always going to be positive or am I missing something?
## either change your return to return a reference to the %counters hash and get rid of these or fill these with the appropriate counter
		$have_a_bmi=$counters{'bmi'};
		$have_a_bfat=$counters{'bfat'};
		$have_a_hdl = $counters{'hdl'};
		$have_a_chol = $counters{'chol'};
		$have_a_dbp = $counters{'bp_dias'};
		$have_a_sbp = $counters{'bp_sys'};
		$have_a_hip = $counters{'hip'};
		$have_a_waist = $counters{'waist'};
		$have_a_neck = $counters{'neck'};
		$have_a_weight = $counters{'weight'};
##		foreach (sort keys %counters){ carp "$_ - $counters{$_} -- " }
		
##		carp("@bodyfat \n");
	   return(\@bmi,\@bodyfat,\@lowweight,\@highweight,\@dcr,\@idealweight,\@lean_mass,\@lean_ideal,\@thr_low,\@thr_medium,\@thr_high,\@waist_to_hip,\@waist_to_hip_shape,\@date,\@bmi_al,\@bmi_ah,\@bmi_opti,\@bmi_uhl,\@bmi_uhh,$maxbmi,\@fat_average,\@fat_ideal,\@fat_fitlow,\@fat_fithigh,\@fat_noeat,$maxbfat,\@hdl_min,\@hdl_zero,\@hdl,$maxhdl,\@chol_lgreen,\@chol_red,\@chol_min,\@chol_max,$maxcol,\@chol,\@bp_sys,$maxbp_sys,\@bp_dias,$maxbp_dias,\@bp_average,\@bp_limit,\@bp_max,\@hip,\@neck,\@waist,$startdate,$enddate,\@bmi_min,\@bmi_max,$have_a_bmi,$have_a_bfat,$have_a_hdl,$have_a_chol,$have_a_dbp,$have_a_sbp,$have_a_hip,$have_a_waist,$have_a_neck,\@ydate,$have_a_weight,\@weight,$max_weight,\@high_range,\@low_range,\@ideal_range);	
	}
	
	#################################################
	#function: creategraph_fiveyear
	#argument: configuration,graph type,date
	#Description: generates graph for one year values
	################################################
sub create_PT_graph
	{
		my $length = shift;
		my $graph = shift;
		my $config = shift;
		my $date = shift;
## getting the dates here no
		my $startdate = shift;
		my $enddate = shift;
		my $id = $user->db_id;		
		my $c = new XYChart($config->pt_plotarea_x_axis,$config->pt_plotarea_y_axis,oct( $config->pt_body_color),oct($config->pt_graph_boder_color), 1);
		my @ybar =();
		my ($pt_graph_title_background,$pt_graph_title_color,$pt_graph_title_color,$pt_graph_personal_weight,$pt_graph_personal_weight_marker,$pt_graph_hlrange_weight,$pt_graph_ideal_weight,$pt_graph_hlrange_bmi,$pt_graph_ideal_bmi,$pt_graph_danger_level,$pt_graph_bp_interliner,$pt_graph_average_bfat,$pt_graph_athle_bfat,$pt_graph_danger_bfat,$pt_graph_min_hdl,$pt_graph_hdl_interliner,$pt_graph_red_chol,$pt_graph_opt_chol,$pt_graph_chol_interliner,$pt_graph_chol_interliner1,$pt_graph_sysbp,$pt_graph_opt_bp,$pt_graph_bp_interliner,$pt_graph_dbp,$pt_graph_personal_sbp,$pt_graph_hip,$pt_graph_personal_neck,$pt_graph_waist,$pt_graph_ideal_bfat,$pt_graph_dbp_marker,$pt_graph_personal_sbp_marker)=graphcolors();
		my %colors = %{graphcolors()};
		$c->setRoundedFrame();
		$c->setPlotArea($config->pt_horizontal_alignment,$config->pt_vertical_alignment,$config->pt_pixel_x_plotarea,$config->pt_pixel_y_plotarea,oct($config->pt_graph_background), -1, -1,oct($config->pt_horizontal_gridlines),oct($config->pt_vertical_gridlines));
		$c->addLegend(50, 30, 0, "arialbd.ttf", 9)->setBackground($perlchartdir::Transparent);		
		
		my $layer = $c->addLineLayer2();
## gap color was not getting set on the longer graphs and that was what was causing most of them to appear to not plot
		$layer->setGapColor(oct($colors{pt_graph_personal_weight})) if ($graph eq 'weight' || $graph eq 'bmi' || $graph eq 'bfat' || $graph eq 'hdl' || $graph eq 'chol' );

## these are the same in each graph, set them here
		$c->xAxis()->setLabels($date);
## set the step based on the length of time
		if ($length == 1){
			$c->xAxis()->setLabelStep(5,1);
		}
		elsif ($length == 3){
			$c->xAxis()->setLabelStep(7,1);
		}
		elsif ($length == 6){
			$c->xAxis()->setLabelStep(14,7);
		}
		elsif ($length == 12){
			$c->xAxis()->setLabelStep(28,7);
		}
		else {
			$c->xAxis()->setLabelStep(360,60);
		}
		$c->xAxis()->setTitle("Data from $startdate ---> $enddate");			
		if($graph eq 'weight')
		{
			my $weight = shift;
			my $low = shift;
			my $high = shift;
			my $ideal = shift;
			my $maxweight = shift;
			
			$maxweight = $maxweight+25;
			#print "weight";

			my $graph_title = $config->pt_graph_title_weight || 'Your Weight';
$colors{pt_good_color} = $config->pt_good_color || 0x8099f090;
		$colors{pt_verygood_color} = $config->pt_verygood_color ||0x52AA00;
                $colors{pt_warning_color} =   $config->pt_warning_color || 0x99f0ff00;
                $colors{pt_bad_color} =  $config->pt_bad_color || 0x99e02200;
                $colors{pt_verybad_color} =  $config->pt_verybad_color || 0xFF0000;
                $colors{pt_graph_waist} = $config->pt_graph_waist || 0xC66963;
                $colors{pt_graph_personal_neck} = $config->pt_graph_personal_neck || 0x8CBEFF;
                $colors{pt_graph_hip} = $config->pt_graph_hip || 0xFFCB63;
			$c->addTitle($graph_title, "timesbi.ttf", 15)->setBackground(oct($colors{pt_graph_title_background}),oct($colors{pt_graph_title_color}), perlchartdir::glassEffect());
			$c->yAxis()->setTitle("Weight");
			#$c->yAxis()->setLabels(\@ybar);
			#$c->yAxis()->setAutoScale(0, 0, 1);
			$c->yAxis()->setLinearScale(100,$maxweight,5);
			$c->yAxis()->setLabelStep(5,1);
			#$c->YAxis()->setTickOffset(0.1); 		
			#my $layer = $c->addLineLayer2();
             
                        $layer->setLineWidth(3);
			if($length <= 6){
				$layer->addDataSet($weight,oct($colors{pt_graph_personal_marker}), 'Your Weight')->setDataSymbol(
						$perlchartdir::CircleSymbol, 4, oct($colors{pt_graph_personal_marker}));
			}
			else	{
				$layer->addDataSet($weight,oct($colors{pt_graph_personal_marker}), 'Your Weight')->setDataSymbol(
						$perlchartdir::CircleSymbol, 3, oct($colors{pt_graph_personal_marker}));
			}                      
                        $c->yAxis()->addMark($user->ideal_weight,oct($colors{pt_verygood_color}),'Ideal ')->setLineWidth(2);
			$c->yAxis()->addZone($user->low_weight, $user->high_weight, oct($colors{pt_good_color}));		  
		}
		if($graph eq 'bmi')
		{
			my $bmi =shift;
			my $mbmi  = shift;
			my $maxbmi = BMI_OBESE + 2;
			$maxbmi = $mbmi+8 if ($mbmi > (BMI_OBESE - 2));
			my $graph_title = $config->pt_graph_title_bmi || 'Your BMI';
			$c->addTitle($graph_title, "timesbi.ttf", 15)->setBackground(oct($colors{pt_graph_title_background}),oct($colors{pt_graph_title_color}), perlchartdir::glassEffect());
			$c->yAxis()->setTitle("BMI");
			$c->yAxis()->setLinearScale(14,$maxbmi,1);
			$c->yAxis()->setLabelStep(2,1);
                        $layer->setLineWidth(3);                             
			if($length <= 6){
				$layer->addDataSet($bmi,oct($colors{pt_graph_personal_weight}), 'Your BMI')->setDataSymbol(
	    				$perlchartdir::CircleSymbol, 4, oct($colors{pt_graph_personal_weight_marker}));
			}
			else	{
				$layer->addDataSet($bmi,oct($colors{pt_graph_personal_marker}), 'Your BMI')->setDataSymbol(
	    				$perlchartdir::CircleSymbol, 3, oct($colors{pt_graph_personal_marker}));
			}
			$c->yAxis()->addMark(BMI_BEST,oct($colors{pt_verygood_color}),'Ideal')->setLineWidth(2);
			$c->yAxis()->addZone(0, BMI_LOWEST, oct($colors{pt_bad_color}));
			$c->yAxis()->addZone(BMI_LOWEST, BMI_LOW, oct($colors{pt_warning_color}));
			$c->yAxis()->addZone(BMI_LOW, BMI_GOOD, 0x8099f090);
			$c->yAxis()->addZone(BMI_GOOD, BMI_OBESE, oct($colors{pt_warning_color}));
			$c->yAxis()->addZone(BMI_OBESE, 1000, oct($colors{pt_bad_color}));
		}
		if($graph eq 'bfat')
		{
			
			my $mbfat = shift;
			my $bodyfat = shift;			
			my $maxbfat = $mbfat +10;
			my $counter=0;
			my @bfatx = @$bodyfat;
			foreach (@bfatx){ carp "$counter. bf=$_ -- " if $_ != '1.7E+308';$counter++;}
			my $graph_title = $config->pt_graph_title_bfat || 'Your Your Body Fat Estimate';
			$c->addTitle($graph_title, "timesbi.ttf", 15)->setBackground(oct($colors{pt_graph_title_background}),oct($colors{pt_graph_title_color}), perlchartdir::glassEffect());
			$c->yAxis()->setTitle("Body Fat Estmate");
			$c->yAxis()->setLinearScale(0,60,1);
			$c->yAxis()->setLabelStep(10,2);                          
                        $layer->setLineWidth(3);
			if ($length <= 6){
				$layer->addDataSet($bodyfat,oct($colors{pt_graph_personal_marker}), 'Your Body Fat')->setDataSymbol(
					$perlchartdir::CircleSymbol, 4, oct($colors{pt_graph_personal_marker}));
			}
			else	{
				$layer->addDataSet($bodyfat,oct($colors{pt_graph_personal_marker}), 'Your Body Fat')->setDataSymbol(
					$perlchartdir::CircleSymbol, 3, oct($colors{pt_graph_personal_marker}));
			}
                        if($user->sex eq MALE)
                        {
                           $c->yAxis()->addMark(FAT_AVERAGE_MALE,oct($colors{pt_graph_average_bfat}),'Average')->setLineWidth(2);
                           $c->yAxis()->addMark(FAT_IDEAL_MALE,oct($colors{pt_verygood_color}),'Ideal')->setLineWidth(2);
                           $c->yAxis()->addMark(FAT_FITLOW_MALE,oct($colors{pt_verygood_color}),'Atheletic')->setLineWidth(2);                          
                           $c->yAxis()->addMark(FAT_FITHIGH_MALE,oct($colors{pt_verygood_color}),'Atheletic')->setLineWidth(2);                          
                           $c->yAxis()->addMark(FAT_NOEAT,oct($colors{pt_verybad_color}),'Atheletic')->setLineWidth(2);                         
                        }
                        else
                        {
                           $c->yAxis()->addMark(FAT_AVERAGE_FEMALE,oct($colors{pt_graph_average_bfat}),'Average')->setLineWidth(2);
                           $c->yAxis()->addMark(FAT_IDEAL_FEMALE,oct($colors{pt_verygood_color}),'Ideal')->setLineWidth(2);
                           $c->yAxis()->addMark(FAT_FITLOW_FEMALE,oct($colors{pt_verygood_color}),'Atheletic')->setLineWidth(2);
                            $c->yAxis()->addMark(FAT_FITHIGH_FEMALE,oct($colors{pt_verygood_color}),'Atheletic')->setLineWidth(2);                          
                           $c->yAxis()->addMark(FAT_NOEAT,oct($colors{pt_verybad_color}),'Atheletic')->setLineWidth(2);                         
                        }
		}
		if($graph eq 'hdl')
		{
			my $hdl_min = shift;
			my $hdl_zero = shift;
			my $hdl = shift;
			my $maxhdl = shift;
			my $mhdl = $maxhdl+25;
			my $graph_title = $config->pt_graph_title_bfat || 'Your Your Body Fat Estimate';
			$c->addTitle('Your HDL Levels', "timesbi.ttf", 15)->setBackground(oct($colors{pt_graph_title_background}),oct($colors{pt_graph_title_color}), perlchartdir::glassEffect());
			$c->yAxis()->setTitle("HDL Level");			
			$c->yAxis()->setLinearScale(0,$mhdl,2);
			$c->yAxis()->setLabelStep(10,2);                           
                        $c->yAxis()->addMark(HDL_LOW,oct($colors{pt_verygood_color}),'Ideal')->setLineWidth(2);
			$c->yAxis()->addZone(0, HDL_LOW, oct($colors{pt_warning_color}));
                        $c->yAxis()->addZone(HDL_LOW, $mhdl, oct($colors{pt_good_color}));
                        $layer->setLineWidth(3);
			if ($length <= 6){
				$layer->addDataSet($hdl,oct($colors{pt_graph_personal_marker}),'Your HDL')->setDataSymbol(
				 $perlchartdir::CircleSymbol, 4, oct($colors{pt_graph_personal_marker}));
			}
			else	{
				$layer->addDataSet($hdl,oct($colors{pt_graph_personal_marker}),'Your HDL')->setDataSymbol(
				 $perlchartdir::CircleSymbol, 3, oct($colors{pt_graph_personal_marker}));
			}
		}
		if($graph eq 'chol')
		{
			my $chol_min = shift;
			my $chol_max = shift;
			my $chol_red = shift;
			my $chol_lgreen = shift;
			my $maxchol = shift;
			my $chol = shift;
			my $mcol = $maxchol+20;
			my $graph_title = $config->pt_graph_title_chol || 'Your Cholestrol Levels';
			$c->addTitle($graph_title, "timesbi.ttf", 15)->setBackground(oct($colors{pt_graph_title_background}),oct($colors{pt_graph_title_color}), perlchartdir::glassEffect());
			$c->yAxis()->setTitle("Cholestrol Level");
			#$c->yAxis()->setLabels(\@ybar);
			#$c->yAxis()->setAutoScale(0, 0, 1);
			$c->yAxis()->setLinearScale(85,340,4);
			$c->yAxis()->setLabelStep(10,2);
			#$c->YAxis()->setTickOffset(0.1);
                        $layer->setLineWidth(3);                
			$c->yAxis()->addMark(CHOL_HIGH,oct($colors{pt_verybad_color}),'High ')->setLineWidth(2);
			$c->yAxis()->addZone(CHOL_HIGH, $chol_max, oct($colors{pt_bad_color}));	    
                        $c->yAxis()->addMark(CHOL_MARGINAL,oct($colors{pt_verygood_color}),'Healthy ')->setLineWidth(2);			
                        $c->yAxis()->addZone(CHOL_MARGINAL, CHOL_HIGH, oct($colors{pt_warning_color}));	    
			if($length <= 6){
				$layer->addDataSet($chol,oct($colors{pt_graph_personal_marker}), 'Your Total Cholesterol')->setDataSymbol(
				 $perlchartdir::CircleSymbol, 4, oct($colors{pt_graph_personal_marker}));
			}
			else	{
				$layer->addDataSet($chol,oct($colors{pt_graph_personal_marker}), 'Your Total Cholesterol')->setDataSymbol(
				 $perlchartdir::CircleSymbol, 3, oct($colors{pt_graph_personal_marker}));
			}
		}
		if($graph eq 'bp')
		{
			my $bp_sys = shift;
			my $maxbp_sys = shift;
			my $bp_dias = shift;
			my $maxbp_dias = shift;
			my $bp_average = shift;
			my $bp_limit = shift;
			my $bp_max = shift;
##			my $startdate = shift;
##			my $enddate = shift;
			my $graph_title = $config->pt_graph_title_bp || 'Your BP Levels';
			$c->addTitle($graph_title, "timesbi.ttf", 15)->setBackground(oct($colors{pt_graph_title_background}),oct($colors{pt_graph_title_color}), perlchartdir::glassEffect());
			$c->yAxis()->setTitle("Blood Pressure Level");
			#$c->yAxis()->setLabels(\@ybar);
			#$c->yAxis()->setAutoScale(0, 0, 1);
			$c->yAxis()->setLinearScale(40,200,2);
			$c->yAxis()->setLabelStep(10,2);
			#$c->YAxis()->setTickOffset(0.1);
			       
			$layer->setGapColor($perlchartdir::SameAsMainColor);
                        $layer->setLineWidth(3);
                        $c->yAxis()->addMark(BP_HIGH_SYSTOLIC,oct($colors{pt_verybad_color}),'High ')->setLineWidth(2);
			$c->yAxis()->addZone(BP_HIGH_SYSTOLIC, BP_MAX, oct($colors{pt_bad_color}));	    			
                        $c->yAxis()->addMark(BP_OPTIMUM_SYSTOLIC,oct($colors{pt_verygood_color}),'Optimum')->setLineWidth(2);			
                        $c->yAxis()->addZone(BP_OPTIMUM_SYSTOLIC, BP_HIGH_SYSTOLIC, oct($colors{pt_warning_color}));	    						
			if($length <= 6){
				$layer->addDataSet($bp_sys,oct($colors{pt_graph_personal_sbp}),'Systolic blood pressure.')->setDataSymbol(
				  	$perlchartdir::DiamondSymbol, 4, oct($colors{pt_graph_personal_sbp}));
				$layer->addDataSet($bp_dias,oct($colors{pt_graph_dbp}),'Diastolic blood pressure')->setDataSymbol(
				 	$perlchartdir::CircleSymbol, 6, oct($colors{pt_graph_dbp}));
			}
			else	{
				$layer->addDataSet($bp_sys,oct($colors{pt_graph_personal_sbp}),'Systolic blood pressure.')->setDataSymbol(
				  	$perlchartdir::DiamondSymbol, 3, oct($colors{pt_graph_personal_sbp}));
				$layer->addDataSet($bp_dias,oct($colors{pt_graph_dbp}),'Diastolic blood pressure')->setDataSymbol(
				 	$perlchartdir::CircleSymbol, 3, oct($colors{pt_graph_dbp}));
			}
		}
		if($graph eq 'mes')
		{
			my $hip = shift;
			my $neck = shift;
			my $waist =shift;
##			my $startdate = shift;
##			my $enddate = shift;
			my $graph_title = $config->pt_graph_title_measures || 'Your Measures';
			$c->addTitle($graph_title, "timesbi.ttf", 15)->setBackground(oct($colors{pt_graph_title_background}),oct($colors{pt_graph_title_color}), perlchartdir::glassEffect());
			$c->yAxis()->setTitle("Body Measures");
			#$c->yAxis()->setLabels(\@ybar);
			#$c->yAxis()->setAutoScale(0, 0, 1);
			$c->yAxis()->setLinearScale(5,85,2);
			$c->yAxis()->setLabelStep(5,1);
			#$c->YAxis()->setTickOffset(0.1);
                        $layer->setLineWidth(3);
			$layer->setGapColor($perlchartdir::SameAsMainColor);
			if($length <= 6){
				$layer->addDataSet($hip,oct($colors{pt_graph_hip}),'Hip')->setDataSymbol(
				 	$perlchartdir::CircleSymbol, 4, oct($colors{pt_graph_hip}));
				$layer->addDataSet($neck,oct($colors{pt_graph_personal_neck}),'Neck')->setDataSymbol(
					$perlchartdir::DiamondSymbol, 4, oct($colors{pt_graph_personal_neck}));
				$layer->addDataSet($waist,oct($colors{pt_graph_waist}),'Waist')->setDataSymbol(
				 	$perlchartdir::SquareSymbol, 4, oct($colors{pt_graph_waist}));
			}
			else	{
				$layer->addDataSet($hip,oct($colors{pt_graph_hip}),'Hip')->setDataSymbol(
				 	$perlchartdir::CircleSymbol, 3, oct($colors{pt_graph_hip}));
				$layer->addDataSet($neck,oct($colors{pt_graph_personal_neck}),'Neck')->setDataSymbol(
					$perlchartdir::DiamondSymbol, 3, oct($colors{pt_graph_personal_neck}));
				$layer->addDataSet($waist,oct($colors{pt_graph_waist}),'Waist')->setDataSymbol(
				 	$perlchartdir::SquareSymbol, 3, oct($colors{pt_graph_waist}));
			}
			#$layer->setGapColor($config->pt_graph_waist);
		}
		#$layer->setGapColor(oct(0xFFFF0007));			
		binmode(STDOUT);
		my $oi_file = $config->pt_image_dir."$id"."_".$graph."_".$length.".png";
		#print "Content-type: image/png\n\n";
		$c->makeChart($oi_file);
	}
	sub graphcolors
	{
		my %colors;
		$colors{pt_good_color} = $config->pt_good_color || 0x8099f090;
		$colors{pt_verygood_color} = $config->pt_verygood_color ||0x52AA00;
                $colors{pt_warning_color} =   $config->pt_warning_color || 0x99f0ff00;
                $colors{pt_bad_color} =  $config->pt_bad_color || 0x99e02200 ;
                $colors{pt_verybad_color} =  $config->pt_verybad_color || 0xFF0000;
                $colors{pt_graph_waist} = $config->pt_graph_waist || 0xC66963;
                $colors{pt_graph_personal_neck} = $config->pt_graph_personal_neck || 0x8CBEFF;
                $colors{pt_graph_hip} = $config->pt_graph_hip || 0xFFCB63;
                $colors{pt_graph_personal_marker} =  $config->pt_graph_personal_marker || 0x21459c;
                $colors{pt_graph_average_bfat} =$config->pt_graph_average_bfat || 0xEFB208;
                $colors{pt_graph_title_background} =  $config->pt_graph_title_background || 0xccccf;
		$colors{pt_graph_title_color} =  $config->pt_graph_title_colo || 0x000000;
                $colors{pt_graph_dbp} = $config->pt_graph_dbp || 0x8CBEFF;
                $colors{pt_graph_personal_sbp} = $config->pt_graph_personal_sbp || 0x949294;
## this makes the return much easier
##		return($pt_graph_title_background,$pt_graph_title_color,$pt_graph_title_color,$pt_graph_personal_weight,$pt_graph_personal_weight_marker,$pt_graph_hlrange_weight,$pt_graph_ideal_weight,$pt_graph_hlrange_bmi,$pt_graph_ideal_bmi,$pt_graph_danger_level,$pt_graph_bp_interliner,$pt_graph_average_bfat,$pt_graph_athle_bfat,$pt_graph_danger_bfat,$pt_graph_min_hdl,$pt_graph_hdl_interliner,$pt_graph_red_chol,$pt_graph_opt_chol,$pt_graph_chol_interliner,$pt_graph_chol_interliner1,$pt_graph_sysbp,$pt_graph_opt_bp,$pt_graph_bp_interliner,$pt_graph_dbp,$pt_graph_personal_sbp,$pt_graph_hip,$pt_graph_personal_neck,$pt_graph_waist,$pt_graph_ideal_bfat,$pt_graph_dbp_marker,$pt_graph_personal_sbp_marker);
		return (\%colors);
		
	}	
=head1
####################personal tracker templates and template names in healthstatus.conf######################
pt_user_input			personaltracker.tmpl
pt_medical_specific_info	pt_medical_info.tmpl
pt_review			pt_review.tmpl
ptreview                        ptreview.tmpl
pt_title1               'Personal Information'
pt_image_dir             /usr/local/www/vhosts/managed1/ybrant/htdocs/images/pt_images/
pt_image_html            images/pt_images/

#######################personal tracker URL def in healthstatus.conf################
ptracker_url                /cgi-bin/hs/ptracker.cgi

#####################personal tracker directories############################
pt_page_dir /home/workout/data

######################personal tracker color configuration options in health status.conf#########
pt_plotarea_x_axis              600
pt_plotarea_y_axis              300
pt_body_color                   0xeeeeff
pt_graph_boder_color            0x000000
pt_horizontal_alignment         55
pt_vertical_alignment           58
pt_pixel_x_plotarea             520
pt_pixel_y_plotarea             195
pt_graph_background             0xffffff
pt_horizontal_gridlines        0xcccccc
pt_vertical_gridlines          0xcccccc
pt_graph_title                 'Your Weight'
pt_graph_title_background       0xccccff
pt_graph_title_color            0x000000
pt_graph_personal_weight        0x4A65AD
pt_graph_personal_weight_marker 0x21459c
pt_graph_ideal_weight           0x52AA00
pt_graph_hlrange_weight         0x84ff84
pt_graph_danger_level           0xE74952
pt_graph_ideal_bmi              0x52AA00
pt_graph_hlrange_bmi            0x84ff84
pt_graph_average_bfat           0xEFB208
pt_graph_ideal_bfat             0x52AA00
pt_graph_athle_bfat             0x94CBFF
pt_graph_danger_bfat            0xFF0000
pt_graph_min_hdl                0x84ff84
pt_graph_hdl_interliner1        0x8099ff99
pt_graph_hdl_interliner        0x99f0ff00
pt_graph_opt_chol              0x84ff84
pt_graph_red_chol              0xFF0000
pt_graph_min_chol              0x84ff84
pt_graph_chol_interliner        0x99f0ff00
pt_graph_chol_interliner1       0x99e02200
pt_graph_sysbp                  0xFF0000
pt_graph_opt_bp                 0x84ff84
pt_graph_bp_interliner          0x99f0ff00
pt_graph_dbp                    0xE7EBEF
pt_graph_dbp_marker             0xE7EBEF
pt_graph_personal_sbp           0x949294
pt_graph_personal_sbp_marker    0x949294
pt_graph_hip                    0xFFCB63
pt_graph_personal_neck          0x8CBEFF
pt_graph_waist                  0xC66963

=head1 BUGS

* none that i've found so far.

=head1 TO DO

* nothing yet

=head1 AUTHOR

Visu, Greg White <gwhite@healthstatus.com>

=head1 COPYRIGHT

Copyright 2001-2008, HealthStatus.com

=cut
