#!/usr/local/bin/perl
use strict;

use File::Basename        qw( dirname );
use File::Spec::Functions qw( rel2abs );

use lib dirname(rel2abs($0)),'.','/usr/local/www/vhosts/managed2/modules/pdf', '/usr/local/www/vhosts/managed2/modules';

use vars qw( $Debug $production %setup_tables %field_info %computed_info);

if (!do('common.inc')) {
   my $error = $@ ? $@
             : $! ? $!
             : 'did not return a true value';
   die("Unable to load common stuff: $error\n");
}
use Spreadsheet::ReadSXC;
use Spreadsheet::ParseExcel;
use Spreadsheet::XLSX;
use Spreadsheet::Read;

use CGI qw(-no_xhtml -debug);
use CGI::Carp qw(fatalsToBrowser);
use HealthStatus qw( fill_and_send error html_error );
use HealthStatus::Authenticate;
use HealthStatus::Config;
use HealthStatus::Constants;
use HealthStatus::Database;

my $input = new CGI();
my $config = getConfig($input->param('extracfg'));
if (!do($config->conf_config_dir.'/healthstatus_db.conf')) {
   my $error = $@ ? $@
             : $! ? $!
             : 'did not return a true value';
   die("Unable to load ".$config->conf_config_dir."/healthstatus_db.conf: $error\n");
}

my %hash = map { $_, $input->param($_) } $input->param();

my %config = map { $_, $config->$_ } $config->directives;

$hash{config} = \%config;

my %input = $input->Vars();

############################################################################
### Comment out the following line before going into production ############
$Debug = $input->param("HS_Debug") || $ENV{HS_DEBUG} || 0;
#### only uncomment if you need to debug the input scripts      ############
############################################################################

# authenticate_user redirects the user if they not allowed to
# view this page
my $user = authenticateUser(["admin"], $input, $config) or die "You should never see this message.";

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

my %assessment_names = ( 
			 HRA	=> 'General Health assessment ',
			 GHA	=> 'Health Risk assessment',
			 CRC	=> 'Cardiac Risk assessment',
			 DRC	=> 'Diabetes Risk assessment',
			 FIT	=> 'Fitness assessment',
			 GWB	=> 'General Well Being assessment');

my @assessments_allowed = split /\s+/, $config->ggr_adv_tables;

my %assessments_allowed_hash;
foreach (@assessments_allowed){
	$assessments_allowed_hash{$_} = $assessment_names{$_};
	
}
my $upload_dir 			= $config->conf_data_dir . "/IMPORT/";
if (! -d $upload_dir)
{
        mkdir $upload_dir;
}

if ($input->param('Process') eq 'Next') {
#User clicked Next from template: admin_data_administration.tmpl


        if ($input->param('data_type1') eq 'historical'){
                $hash{display_message}			= "Please select type of Historical Profile :";
                $hash{assessments_allowed_hash}         = \%assessments_allowed_hash;
                my $template 				= $config->template_directory . 'import_historical_profile.tmpl';
                fill_and_send( $template, $user, \%hash , $config->html_use_ssi );
                exit;
        } else {
		$hash{display_message}                  = "Please select type of Biometric Profile :";
                $hash{assessments_allowed_hash}         = \%assessments_allowed_hash;
                my $template 				= $config->template_directory . 'input_import_profile.tmpl';
                fill_and_send( $template, $user, \%hash , $config->html_use_ssi );
                exit;

        }
}
elsif  ($input->param('Submit') eq 'Create Profile') {
#user clicked Create Profile from template: create_import_profile.tmpl

	my $filename			= $upload_dir."/".$user->db_id . ".txt";

	# If profile exists, check for unique profile name
        # open file in read mode
        open ( FH, "$filename" );
        while (<FH>){
                chomp;
                my @fields = split(/\|/, $_);
                if ($fields[0] eq $input->param('profile_name'))
                {
                      $hash{create_profile}           	= 1;
                      $hash{message}          		= "Profile name is not unique.";
                      my $template = $config->template_directory . 'create_import_profile.tmpl';
                      fill_and_send( $template, $user, \%hash , $config->html_use_ssi ); 
                      exit;
                } 
        }
        close FH;

        $hash{create_profile}           = 1;
        # create and write a profile
        # open file in append mode
        my $flag=1;
        open ( FH, ">> $filename" ) or do {$hash{message} ="Unable to open profile file to write !!"; $flag=0; };
        if ($flag == 1)
        {
		print FH $input->param('profile_name') . "|" . $input->param('profile_desc') . "|" . $input->param('data_type') . "|" . $input->param('assessment') . "|" . $input->param('profile') . "\n" ;
		close FH;
                $hash{message}          = "Profile has been created successfully.";
        }
	
	my $template 		= $config->template_directory . 'create_import_profile.tmpl';
	fill_and_send( $template, $user, \%hash , $config->html_use_ssi );

}
elsif ($input->param('Submit') eq 'View Profile') {
#user clicked View profile

        my $filename                   = $upload_dir."/".$user->db_id . ".txt";
        my $str;
        open ( FH, "$filename" ) or do {$str="<span style=\"color: #660000;\"><b>No Profiles exist. Please create an Import Profile first !!</b></span>"; };
        my @array;
        my @fields;
        while (<FH>){
                chomp;
                @fields 		 = split(/\|/, $_);
                my $temp		 = substr($fields[4],1);
                my @pairs		 = split(/\,/, $temp);
                $str 			.= "<table width=700px border=0 style=\"border: 2px solid gray;\">";
                $str 			.= "<tr><td colspan=2 bgcolor=#cccccc><b><font color=#660000>      $fields[0]                    </font></b></td></tr>";
                $str 			.= "<tr><td width=200px><b>Profile Desc:           </b></td><td>   $fields[1]                               </td></tr>";
                $str 			.= "<tr><td><b>Profile Type:           		   </b></td><td>   $fields[2]                               </td></tr>";
                $str 			.= "<tr><td><b>Profile Assessment Type:		   </b></td><td>   $assessments_allowed_hash{$fields[3]}    </td></tr>";  
                $str 			.= "<tr><td><b>Database Field:         		   </b></td><td><b>User Field:                          </b></td></tr>";
                
                foreach (@pairs)
                {
                        my ( $table, $key, $value ) = split /=/;
                        $value = $value+1;
                        $str 		.= "<tr><td>$key 		       </td><td>    $value                                   </td></tr>";
                }
                $str 			.= "</table><br>";

        }
        if ($str eq '')
        {
                $str="<span style=\"color: #660000;\"><b>No Profiles exist. Please create an Import Profile first !!</b></span>";
        }
        $hash{message}                  = $str;
        my $template                    = $config->template_directory . 'view_import_profile.tmpl';
        fill_and_send( $template, $user, \%hash , $config->html_use_ssi );

}
elsif ($input->param('Submit') eq 'Next step') {
#user clicked Next Step from input_import_profile.tmpl OR import_historical_profile.tmpl

        my $file 				= $input->param("sample_file");
        my $pos					= rindex $file, ".";
        my $filename 				= substr ($file, 0, $pos);	
        my $ext      				= substr ($file, $pos+1);
	
	my @local_table_columns;

        #Read only 1st row of uploaded file	
	#Ensure that uploaded file has column headings in 1st row
	#Extract user columns
	if($ext eq 'xls'){
	
		my $xls 		= ReadData ($input->param("sample_file"), sep => ',', quote => '"');
		@local_table_columns 	= Spreadsheet::Read::row ($xls->[1], 1);

        } elsif($ext eq 'xlsx'){
                my $upload_filehandle   = $input->upload("sample_file");
                &do_upload($filename,$upload_filehandle,$upload_dir);
                $filename 		= "$upload_dir/$filename";
                my $xls 		= Spreadsheet::XLSX->new($filename);
                foreach my $sheet (@{$xls -> {Worksheet}}) {
                        $sheet -> {MaxRow} ||= $sheet -> {MinRow};
                        foreach my $row ($sheet -> {MinRow} .. $sheet -> {MinRow}) {

                                $sheet -> {MaxCol} ||= $sheet -> {MinCol};

                                foreach my $col ($sheet -> {MinCol} .. $sheet -> {MaxCol}) {

                                        my $cell= $sheet -> {Cells} [$row] [$col];
                                        if ($cell) {
                                                my $val = $cell -> {Val};
                                                push (@local_table_columns, $val);
                                        }
                                } 
                        }
                }
		
	} else {
		my $upload_filehandle 	= $input->upload("sample_file");
		my $file		= $input->param("sample_file");
		do_upload($file,$upload_filehandle,$upload_dir);
		
		open ( FH, "$upload_dir/$file" ) or die "$!";  
		my $data_columns		= <FH> ;
		close FH;
		@local_table_columns 		= split(',',$data_columns);
		
	}

	my @user_table_columns;
        my @table_info;
	if($input->param('data_type') eq 'demographic') {

		@user_table_columns			= split /\s+/, $setup_tables{USER}{fields};

                my $count=$#user_table_columns+1;
                @table_info = ('USER') x $count;

                my @pass_table_columns                  = split /\s+/, $setup_tables{PASS}{fields};
                $count = $#pass_table_columns+1;
                for(my $i=0; $i<$count; $i++){
                    push (@table_info, 'PASS');
                }

		@user_table_columns 			= (@user_table_columns, @pass_table_columns);

	} 
        elsif ($input->param('data_type') eq 'biometric_demographic') {

                @user_table_columns                             = split /\s+/, $setup_tables{USER}{fields};
                my $count=$#user_table_columns+1;
                @table_info = ('USER') x $count;

                my @pass_table_columns                          = split /\s+/, $setup_tables{PASS}{fields};
                $count = $#pass_table_columns+1;
                for(my $i=0; $i<$count; $i++){
                    push (@table_info, 'PASS');
                }

                my @assessment_table_columns                     = split /\s+/, $setup_tables{HRA}{fields};
                $count = $#assessment_table_columns+1;
                for(my $i=0; $i<$count; $i++){
                    push (@table_info, 'HRA');
                }

                my @assessment_table_columns1                    = split /\s+/, $setup_tables{GHA}{fields};
                $count = $#assessment_table_columns1+1;
                for(my $i=0; $i<$count; $i++){
                    push (@table_info, 'GHA');
                }

                @user_table_columns            		        = (@user_table_columns, @pass_table_columns, @assessment_table_columns, @assessment_table_columns1);
        }
        elsif ($input->param('data_type') eq 'biometric_only') {

                @user_table_columns                             = split /\s+/, $setup_tables{USER}{fields};
                my $count=$#user_table_columns+1;
                @table_info = ('USER') x $count;

                my @pass_table_columns                 		= split /\s+/, $setup_tables{PASS}{fields};
                $count = $#pass_table_columns+1;
                for(my $i=0; $i<$count; $i++){
                    push (@table_info, 'PASS');
                }

                my @assessment_table_columns                    = split /\s+/, $setup_tables{$input->param('assessment')}{fields};
                $count = $#assessment_table_columns+1;
                for(my $i=0; $i<$count; $i++){
                    push (@table_info, $input->param('assessment'));
                }

                @user_table_columns                     	= (@user_table_columns, @pass_table_columns, @assessment_table_columns);
        }
        else {
                @user_table_columns                             = split /\s+/, $setup_tables{USER}{fields};
                my $count=$#user_table_columns+1;
                @table_info = ('USER') x $count;

                my @assessment_table_coumns                     = split /\s+/, $setup_tables{$input->param('assessment')}{fields};
                my $count=$#assessment_table_coumns+1;
                @table_info = ($input->param('assessment')) x $count;

                @user_table_columns                     = (@user_table_columns, @assessment_table_coumns);
        }
	my %newHash;
        foreach (@user_table_columns)
        {
                my $key = $field_info{$_}{group};
                push @{$newHash{$key}}, $_;
        }
                
	$hash{local_table_columns}		= \@local_table_columns;
        $hash{user_table_columns}              = \%newHash;
	$hash{field_info}			= \%field_info;
        $hash{table_info}                       = \@table_info;
	$hash{display_message}			= "Please drag the Available Import Fields from left table and drop them on matching Database Fields in right table";
	my $template = $config->template_directory . 'create_import_profile.tmpl';
	fill_and_send( $template, $user, \%hash , $config->html_use_ssi );
    
} 
else {
	$hash{assessments_allowed_hash}		= \%assessments_allowed_hash;
        $hash{display_message}			= "Please select type of Import :";
        my $template = $config->template_directory . 'admin_data_administration.tmpl';
	fill_and_send( $template, $user, \%hash , $config->html_use_ssi );
	exit;
}

# file upload subroutine
sub do_upload(){
	my $filename 			= shift ;
	my $upload_filehandle 		= shift ;  
	my $upload_dir 			= shift ;  
	open ( UPLOADFILE, ">$upload_dir/$filename" ) or die "$!";  
	binmode UPLOADFILE;  
	 
	while ( <$upload_filehandle> )  
	{  
	     print UPLOADFILE;  
	}  
	 
	close UPLOADFILE;
}
