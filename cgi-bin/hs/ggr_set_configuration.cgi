#!/usr/local/bin/perl
use strict;

use File::Basename        qw( dirname );
use File::Spec::Functions qw( rel2abs );

use lib dirname(rel2abs($0)),'.','/usr/local/www/vhosts/managed2/modules/pdf', '/usr/local/www/vhosts/managed2/modules';

use vars qw( $Debug $production $cook $config_file $nph %field_info %computed_info);

if (!do('common.inc')) {
   my $error = $@ ? $@
             : $! ? $!
             : 'did not return a true value';
   die("Unable to load common stuff: $error\n");
}

use CGI::Carp;
use HealthStatus qw ( error html_error fill_and_send );
use Date::Calc;

my $input = new CGI();
my $config = getConfig($input->param('extracfg'));
if (!do($config->conf_config_dir.'/healthstatus_db.conf')) {
   my $error = $@ ? $@
             : $! ? $!
             : 'did not return a true value';
   die("Unable to load ".$config->conf_config_dir."/healthstatus_db.conf: $error\n");
}
my $default_config_file = $config->conf_config_dir.'/default_config.conf';
my $default;
if(-e $default_config_file) {
	$default = new HealthStatus::Config($default_config_file);
} else {
 print "Unable to load ".$default_config_file.": file\n"
}

# authenticate_user redirects the user if they are not allowed to
# view this page
my $user = authenticateUser('all', $input, $config) or die "You should never see this message.";

my @assessments_allowed = @{$$config{common_assessments}};

my (%assessment_stuff, %vars, $restriction, %defined_reports_list,%defined_reports_list_part, @rpt_list, @rpt_friendly_list, @rpt_list_part, @rpt_friendly_list_part, %report_column_hash, %default_avl_column_hash, $report_column_string);

# get the predefined field groups
@rpt_list_part 			= split / /,$config->ggr_adv_rpt_participation_db;
@rpt_friendly_list_part = split /,/,$config->ggr_adv_rpt_participation_friendly;
@rpt_list 				= split / /,$config->ggr_adv_rpt_list_db;
@rpt_friendly_list 		= split /,/,$config->ggr_adv_rpt_list_friendly;

my $t_cnt=0;
foreach my $rpt_group (@rpt_list){
	$defined_reports_list{$rpt_group} = $rpt_friendly_list[$t_cnt];
	++$t_cnt;
}
my $t_cnt_part=0;
foreach my $rpt_group_part (@rpt_list_part) {
	$defined_reports_list_part{$rpt_group_part} = $rpt_friendly_list_part[$t_cnt_part];
	++$t_cnt_part;
}

$vars{config} 				= $config->as_hash();
$vars{assessment_types}	 	= \@assessments_allowed;
$vars{defined_reports_list} = \%defined_reports_list;
$vars{defined_reports_list_part} = \%defined_reports_list_part;

$$config{db}->debug_on( \*STDERR ) if $Debug ;
foreach (@assessments_allowed){
	$assessment_stuff{$_}{name} = assessment_name($_);
}
$vars{assessment_stuff} 	= \%assessment_stuff;

my ($config_var, %field_name_hash, %new_values, %new_friendly_values);

if ($input->param('Submit') eq 'Next step' || $input->param('Submit') eq 'Update') {
	$vars{submit_value} = $input->param('Submit');
	
	if($input->param('rpt_type') eq 'participation') {
		$vars{rpt_friendly_string} = $config->ggr_adv_rpt_participation_friendly;
		if($input->param('new_report')){
			# set the configuration name and values for insert the database in the case of new report
			$config_var 						= 'rpt_new'. scalar(@rpt_list_part) .'_participation_fields';
			$new_values{conf_name}				= 'ggr_adv_rpt_participation_db';
			$new_values{conf_value} 			= $config->ggr_adv_rpt_participation_db . ' new' . scalar(@rpt_list_part) ;
			$new_friendly_values{conf_name}		= 'ggr_adv_rpt_participation_friendly';
			$new_friendly_values{conf_value} 	= $config->ggr_adv_rpt_participation_friendly . ', ' . $input->param('rpt_name') ;
		} else {
			$config_var 						= 'rpt_'. $input->param('part_field_groups') .'_participation_fields';
		}
	} else {
		$vars{rpt_friendly_string} = $config->ggr_adv_rpt_list_friendly;
		if($input->param('new_report')){
			# set the configuration name and values for insert into database in the case of new report
			$config_var 						= 'rpt_new'. scalar(@rpt_list) .'_'. lc($input->param('assessment_list')) .'_fields';
			$new_values{conf_name}				= 'ggr_adv_rpt_list_db';
			$new_values{conf_value} 			= $config->ggr_adv_rpt_list_db . ' new' . scalar(@rpt_list) ;
			$new_friendly_values{conf_name}		= 'ggr_adv_rpt_list_friendly';
			$new_friendly_values{conf_value} 	= $config->ggr_adv_rpt_list_friendly . ', ' . $input->param('rpt_name') ;
		} else {
			$config_var 						= 'rpt_'. $input->param('indv_field_groups') .'_'. lc($input->param('assessment_list')) .'_fields';
		}
	}
	if($input->param('Submit') eq 'Update') {
		my %values			= ();
		my $conf_value 		= $input->param('conf_value');
		$conf_value 		=~ s/-/\_/g ;
		$conf_value 		=~ s/,/ /g ;
		$values{conf_value} = $conf_value;
		my $stipulations 	= "WHERE conf_name='".$config_var."'";
		my $number_of_rows  = $$config{db}->count( 'hs_configuration', $stipulations );
		
		# if configuration variable exists then update else insert into databse
		if($number_of_rows) {
			$$config{db}->update('hs_configuration',\%values,$stipulations);
		} else {
			 $values{conf_name} = $config_var;
			 $$config{db}->insert( 'hs_configuration',\%values ); 
			 if($input->param('new_report')){
				my $new_stipulations 			= "WHERE conf_name='".$new_values{conf_name}."'";
				my $new_friendly_stipulations 	= "WHERE conf_name='".$new_friendly_values{conf_name}."'";
				my $count_rows  				= $$config{db}->count( 'hs_configuration', $new_stipulations );
				
				# update if exists else insert the predefined field group list values  into database in the case of new report
				if($count_rows) {
					$$config{db}->update('hs_configuration',\%new_values,$new_stipulations);
					$$config{db}->update('hs_configuration',\%new_friendly_values,$new_friendly_stipulations);
				
				} else {
					$$config{db}->insert( 'hs_configuration',\%new_values ); 
					$$config{db}->insert( 'hs_configuration',\%new_friendly_values );
				}
			 }
		}
	} else {
		$vars{part_field_groups} 	= $input->param('part_field_groups');
		$vars{field_groups}	 		= $input->param('part_field_groups');
		$vars{indv_field_groups}	= $input->param('indv_field_groups');
		$vars{rpt_type} 			= $input->param('rpt_type');

		# create the new hash from field_info hash for get the user_element as a key 
		foreach (keys %field_info){
			if($field_info{$_}{name}) {
				$field_name_hash{$field_info{$_}{user_element}}{name} 			= $field_info{$_}{name} ;
				$field_name_hash{$field_info{$_}{user_element}}{description} 	= $field_info{$_}{description};
			}
		}
		my $report_config_var 	= $$config{db}->get_default_config_variables("where conf_name='$config_var'");
		
		# create the array of report fields from database
		my @report_fields_array 	= split(/\s+/, $report_config_var->{$config_var});
		my %report_fields_hash 		= map { $_ => 1 } @report_fields_array;

		# create the array of availabe  fields for creating the reports
		my @default_fields_array 	= split(/\s+/,$default->{config_data}->{$config_var});
		
		# copy report fields array to availabe  fields array if availabe  fields not exists in the case of new report
		# this is using for disaplying the new report fields name
		@default_fields_array 		= @report_fields_array if(!@default_fields_array);
		
		foreach (@default_fields_array){
			my ($field_name, $field_desc, $config_value);
			if($field_name_hash{$_}{name}) {
				$field_name 	= $field_name_hash{$_}{name} ;
				$field_desc 	= $field_name_hash{$_}{description} ;
			} elsif($field_info{$_}{name}) {
				$field_name 	= $field_info{$_}{name} ;
				$field_desc 	= $field_info{$_}{description} ;
			} elsif($computed_info{$_}) {
				$field_name 	= $computed_info{$_}{name} ;
				$field_desc 	= $computed_info{$_}{description} ;
			}else {
				$field_name 	= $_ ;
				$field_desc 	= $field_info{$_}{description};
			}
			$config_value 		= $_ ;
			#replace  key string "_" with "-" for rerrange order functionality behaviour in column 
			$config_value 		=~ s/\_/-/g ;
			
			#if fields exists in reports fields column then they will not display in default available fields column
			if (exists $report_fields_hash{$_}) {
				$report_column_hash{$config_value}{name} 				= $field_name;
				$report_column_hash{$config_value}{description} 		= $field_desc;
			} else {
				$default_avl_column_hash{$config_value}{name} 			= $field_name;
				$default_avl_column_hash{$config_value}{description} 	= $field_desc;
			}
			
		}
		$report_column_string 			= $report_config_var->{$config_var};
		$report_column_string 			=~ s/\s+/,/g ;
		$report_column_string 			=~ s/\_/-/g ;
		$vars{report_fields_array} 		= \@report_fields_array;
		$vars{report_column_string} 	= $report_column_string;
		$vars{report_column_hash} 		= \%report_column_hash;;
		$vars{default_avl_column_hash} 	= \%default_avl_column_hash;
		 
	}
	
	fill_and_send( $config->template_directory . "admin_set_configuration.tmpl", $user, \%vars, $config->html_use_ssi );
} else{
	fill_and_send( $config->template_directory . "admin_input_configuration.tmpl", $user, \%vars, $config->html_use_ssi );
}
exit;

