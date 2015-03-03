#!/usr/local/bin/perl

use strict;

$| = 1;
####################################################################
# cron script to compute number of assessments taken and send out
# birthday emails
####################################################################
BEGIN{($_=$0)=~s![\\/][^\\/]+$!!;push@INC,$_}

use File::Basename        qw( dirname );
use File::Spec::Functions qw( rel2abs );

use lib dirname(rel2abs($0)),'.','/usr/local/www/vhosts/managed2/modules/pdf', '/usr/local/www/vhosts/managed2/modules';

use vars qw( $Debug $production $cook $config_file);

if (!do('common.inc')) {
   my $error = $@ ? $@
             : $! ? $!
             : 'did not return a true value';
   die("Unable to load common stuff: $error\n");
}

use Time::localtime;
use Mail::Sendmail;
use Mail::CheckUser qw(check_email);
use Text::Template;
use Date::Calc qw(:all);

use HealthStatus::Config;
use HealthStatus;
use HealthStatus::User;
use HealthStatus::Constants;
use HealthStatus::Database;

my $config = getConfig();

error( "Could not find configuration file" ) unless ref $config;

my ($year,$month,$day) = Today();
my ($year1,$month1,$day1) = Add_Delta_Days($year,$month,$day,-1);

my $sdte1 = sprintf("%04d-%02d-%02d", $year,$month,$day);
my $sdte = sprintf("%04d-%02d-%02d", $year1,$month1,$day1);
my $g_year = $year;
my $g_month = $month;
my $g_day = $day;
my @assessments = split /\s+/, $config->ggr_tables;
my %assessment_names = ( HRA	=> 'General Health assesments (new format)',
			 GHA	=> 'General Risk assesments (original)',
			 CRC	=> 'Cardiac Risk assesments',
			 DRC	=> 'Diabetes Risk assesments',
			 FIT	=> 'Fitness assesments',
			 GWB	=> 'General Well Being assesments');
%assessment_names_short = ( HRA	=> 'General Health (new format)',
			 GHA	=> 'General Risk(original)',
			 CRC	=> 'Cardiac Risk',
			 DRC	=> 'Diabetes Risk',
			 FIT	=> 'Fitness',
			 GWB	=> 'General Well-Being');

require $config->db_config_file;

my $db = HealthStatus::Database->new( $config );

my %number_of_rows;

my $count_stip = "where adate>'$sdte' and adate<'$sdte1'";

my %query_results;
my $bdaynumrows;
my @desired_fields = ( $config->db_id, 'unum', 'first_name', 'last_name', 'bMonth', 'bDay', 'bYear', 'Personal_Sex' );
my $stipulation = "where bMonth=$g_month and bDay=$g_day order by unum";

$number_of_rows{'REG'}  =  $db->count( $Tables1{'REG'}, $count_stip );

foreach (@assessments){
	$number_of_rows{$_}  =  $db->count( $Tables1{$_}, $count_stip );
	my @query = $db->select( \@desired_fields, $Tables1{$_}, $stipulation, 1);
	foreach my $person (@query){
		foreach (keys %$person){
			$query_results{$person->{hs_uid}}{$_} = $person->{$_};
			 } }
	$bdaynumrows = $db->count( $Tables1{$_}, $stipulation );
#	print "\n$_ - $bdaynumrows ";
	}

my $last_hs_uid='';
my @email_list;
my @bad_list;
my $bad_cnt = 0;
my $cnt = 0;
my $emailbody = new Text::Template (SOURCE => $config->template_directory .$config->bday_text )
  or die "Couldn't construct template: $Text::Template::ERROR";
if ($bdaynumrows > 0){
	foreach my $person ( sort keys %query_results ) {
#		print "$person -> $last_hs_uid\n ";

		if ($last_hs_uid ne $person){
			$last_hs_uid = $person;
			my $email_stip = qq|where hs_uid='$last_hs_uid'|;
			my @email_db = $db->select( ['email', 'emailOK' ], 'hs_userdata', $email_stip, 1);
#			print "$person, $email_db[0]->{emailOK}\n";

			if($email_db[0]->{emailOK}){
				my $email_to_check = $email_db[0]->{email};
				if(!check_email($email_to_check)) {
					my %new_data = (
						emailOK => 0,
						emailCheck => 0);
					my $stips = qq|where hs_uid='$last_hs_uid'|;
					$db->update( $Tables1{REG}, \%new_data, $stips );
					push @bad_list, "$email_db[0]->{email} - $query_results{$person}{first_name} $query_results{$person}{last_name} *found out today";
					}
				else	{
					my $years = ($g_year - $query_results{$person}{bYear});
					$years = 'How many ' if $years > 85;

					my %var1 = (fname => $query_results{$person}{first_name},
						    age => $years,
						    );
					my $body = $emailbody->fill_in(HASH => \%var1);
					if (!defined $body) {
						die "Couldn't fill in template: $Text::Template::ERROR" }

					my %mail = (   To      => $email_db[0]->{email},
						    From    => $config->email_from,
						    Subject => $config->bday_subject,
						    Message => $body,
						    smtp    =>  $config->email_smtp
						   );
					sendmail(%mail);
						@email_list[$cnt]= "**** email error **** $Mail::Sendmail::error -- " if($Mail::Sendmail::error);
	#				if ($cnt <= 5){ foreach (keys %mail){ print "$_ - $mail{$_}\n"} }
					@email_list[$cnt].= "$email_db[0]->{email} - $query_results{$person}{first_name} $query_results{$person}{last_name} - $years";
					++$cnt;
					}
				}
			else 	{
				push @bad_list, "$email_db[0]->{email} - $query_results{$person}{first_name} $query_results{$person}{last_name}";
				}
			}
		}
	}

my $message = "Number of assessments taken: \n";
foreach (sort keys %number_of_rows){
	$message .= "$assessment_names{$_} - $number_of_rows{$_} \n";
	}

$message .= "\nNumber of birthdays $cnt. \nSent to the following: \n \n";
foreach (@email_list){
	$message .= "$_ \n";
}

$message .= "\nBirthdays with Bad Emails\n";
foreach (@bad_list){
	$message .= "$_ \n";
}

my %mail = ( To      => $config->email_admin,
	    From    => $config->email_from,
	    Subject => 'Birthday Daily Processing',
	    Message => $message,
	    smtp    =>  $config->email_smtp
	   );

sendmail(%mail) or die $Mail::Sendmail::error;
$db->finish();
$db->disconnect;

exit;