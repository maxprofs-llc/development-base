#!/usr/local/bin/perl
use strict;

#  This includes the current directory in the list of places to check for
# modules and other files, mainly for NT systems.
use File::Basename        qw( dirname );
use File::Spec::Functions qw( rel2abs );

use lib dirname(rel2abs($0)),'.','/usr/local/www/vhosts/managed2/modules/pdf', '/usr/local/www/vhosts/managed2/modules';

use vars qw( $Debug $production $cook $config_file %ORACLE_CVRT %setup_tables %field_info %Tables %Fields $nph);

if (!do('common.inc')) {
   my $error = $@ ? $@
             : $! ? $!
             : 'did not return a true value';
   die("Unable to load common stuff: $error\n");
}
# Removing warnings in log while module is being used with CGI version 4 or above
$CGI::LIST_CONTEXT_WARN = 0;

$| = 1;
############################################################################
### Change the following line before going into production      ############
$production = 1;
#### 1 = production server, 0 = setup/test server               ############
############################################################################

use CGI qw(-no_xhtml -debug);
if (!$production) {
	use CGI::Carp qw(fatalsToBrowser);
	}
else {
	use CGI::Carp;
	}

use HealthStatus qw( fill_and_send error check_digit );
use HealthStatus::Authenticate;
use HealthStatus::Config;
use HealthStatus::Constants;
use HealthStatus::Database;
use HealthStatus::User;
use Spreadsheet::Read;
use Data::Dumper;
use HealthStatus;
use DBI;
use DBIx::Sequence;

my $input = new CGI();

my $silent;
my %input = $input->Vars();
my $config = getConfig($input->param('extracfg'));
my $getsql = $input->param('getsql');
if($getsql) {$silent=1;}
my $sql = '';

my( $year, $month, $day, $hour, $min, $sec ) = (localtime)[5,4,3,2,1,0];
$year  += 1900;
$month += 1;

my $date = sprintf("%02d-%02d-%04d", $month, $day, $year);
my $date_stamp = sprintf("%02d-%02d-%04d-%02d-%02d-%02d", $month, $day, $year, $hour, $min, $sec);
my $tight_date = sprintf("%04d%02d%02d%02d%02d%02d", $year, $month, $day, $hour, $min, $sec);

############################################################################
### Comment out the following line before going into production ############
$Debug = $input->param("HS_Debug") || $ENV{HS_DEBUG} || 0;
#### only uncomment if you need to debug the input scripts      ############
############################################################################
# authenticate_user redirects the user if they not allowed to
# view this page
my $user = authenticateUser(["admin"], $input, $config) or die "You should never see this message.";

if (!do($config->conf_config_dir.'/healthstatus_db.conf')) {
   my $error = $@ ? $@
             : $! ? $!
             : 'did not return a true value';
   die("Unable to load ".$config->conf_config_dir."/healthstatus_db.conf: $error\n");
}

if (!do($config->conf_config_dir.'/db_hs.conf')) {
   my $error = $@ ? $@
             : $! ? $!
             : 'did not return a true value';
   die("Unable to load ".$config->conf_config_dir."/db_hs.conf: $error\n");
}

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
my $db1 = HealthStatus::Database->new( $config );
my $dbh  =  DBI->connect($config->db_connect, $config->db_user, $config->db_pass );
my %hash = map { $_, $input->param($_) } $input->param();

my %config = map { $_, $config->$_ } $config->directives;

$hash{config} = \%config;

my $upload_dir 	= $config->conf_config_dir;
my %vars;
my @hs_tables; 
my @db_tables;
my @hs_table;
my @noexist_tables;
my @noexist_tables_upload;
my @modify_tables;
my %hs_table_upload;
my @hs_table_uploads;
my %exists;
my @create_fields;
my @indices;
my @field_list;
my @row;
my $field_data;
my @existing_column_list;
my @tables = $dbh->tables();
my @fields_desc;
my %field_hash;
my @noexist_columns_upload;
 
foreach (@tables){
	if ( lc($config->db_driver) eq 'oracle' ){
			my $usr = uc($config->db_user);
			s("$usr".")();
			s("SYS".")();
			s(")();
		}
	if ( lc($config->db_driver) eq 'mssql' ){
			my $dbname = $config->db_database;
			my $usr = lc($config->db_user);
			s("$dbname"."$usr".")();
			s("$dbname"."dbo".")();
			s(")();
			
		}
	if ( lc($config->db_driver) eq 'postgres' ){
	        next if(/pg_catalog/);
	        next if(/information_/);
			s(public.)();
			s(")();
		}
    if(lc($config->db_driver) eq 'mysql')
        {
              my $dbname = $config->db_database;
              s(`$dbname`.`)();
              s(`)();
			  
        }  
          $exists{lc($_)} = 1;          	  
	      push( @db_tables, $_);		  
	}
	 
	 foreach(@db_tables){
		if($_ ne 'dbix_sequence_release' && $_ ne 'dbix_sequence_state'){
			push(@modify_tables,$_);
		}	
	}	 
	 foreach my $hs_table (keys %Tables){	    
        push(@hs_table, $Tables{$hs_table});				
	}		   
    
if($input->param('add_column')) {
        my $str;
		my @config_field_list;
		# find the tables when user select a table
		my $tables = $input->param("add_column");
        # find the selected columns to add		
		my @checked_column = $input->param('add_check');
		
		if ( lc($config->db_driver) eq 'mssql' ){
			$str = 'select column_name from information_schema.columns where table_name =' . "'" .$tables . "'";			
		}elsif(lc($config->db_driver) eq 'oracle' ){
		    $str = 'SELECT column_name FROM user_tab_cols WHERE table_name='. "UPPER"."("."'" .$tables . "'".")";
		}
		else{
		   $str = 'show columns from ' . $tables;
		}
		my $fields_from_db = $dbh->prepare($str);
		$fields_from_db->execute();
		 while (my @row = $fields_from_db->fetchrow_array ) {
               	 
		       if(lc($config->db_driver) eq 'oracle' ){
				push(@existing_column_list, lc($row[$_]));			
		       }else{
			     push(@existing_column_list, $row[$_]);               		 
		      }
		}   		
		my $my_key;
		foreach my $key_value(keys %setup_tables){
		   if($setup_tables{$key_value}{name} eq $input->param('add_column')) {
		        $my_key =  $key_value;				
		   }
		 } 		 	
        if (exists($setup_tables{$my_key})){		
		    if(lc($config->db_driver) eq 'oracle' ){			 
			  my @field_list_oracle = split /\s+/, $setup_tables{$my_key}{fields};
				  foreach my $field_list_oracle (@field_list_oracle)
				  {
					push(@field_list, lc($field_list_oracle));
				  }
			 }else{
				@field_list = split /\s+/, $setup_tables{$my_key}{fields};
             }			
			@create_fields = ();
		    @indices = ();
			my @noexist_columns_uploads ;
            my @database_columns;
			if(!@existing_column_list){
			    foreach (@field_list){
                   push @database_columns , ($_)	 
				}            
			}else{
			    @database_columns = @existing_column_list;
            }			
            
			 my %total_columns_upload;
			 my @config_field_list = @field_list;			           		  
			 @total_columns_upload{@database_columns} = ();
			 my @noexist_columns_upload = grep{!exists $total_columns_upload{$_}} @config_field_list;		
		     my $temp_field1;
			 my $temp_field;
             my $last_index;
             my $last_element;
            # find the description of the non exist columns	  			  
			 foreach my $fields (@noexist_columns_upload) {				 
                if(lc($config->db_driver) eq 'oracle' ){
				     my $temp_field_oracle = uc($fields);					 
					 $temp_field1 = $ORACLE_CVRT{$temp_field_oracle};
					 $temp_field = $field_info{$temp_field1}{description};					   				  
				}else{
                     $temp_field = $field_info{$fields}{description};				
				     $temp_field1 = $fields;
				}
				   $field_hash{$temp_field1}= $temp_field;
			  }             			
			 my $flag=0;
             my $field_data_mysql;		 
             foreach my $field (@checked_column) {
			    for (my $i = 0; $i < @field_list; $i++) {		        
		        if($field_list[$i] eq $field ){				
                $last_index = $i-1;
				$last_element =  $field_list[$last_index];							
			     }
		       }
				my $temp = $field . ' ' . $field_info{$field}{lc($config->db_driver)};				                   
				push @create_fields, $temp;				    				
				if ($field_info{$field}{index}) {push @indices, $field;}
				# Add columns in order according to config file 
				if( lc($config->db_driver) eq 'mysql' ){				
				$field_data_mysql .= ', ' if($flag == 1);
			    $field_data_mysql .= "add column " .$temp." after $last_element";				
				$flag=1;
				
				}
			 }
			 $field_data = join ", ", @create_fields;
			my $sql_create;
			if ( lc($config->db_driver) eq 'mssql' ){				
				$sql_create = 'Alter table ' . $setup_tables{$my_key}{name} . ' '. 'add' . ' ' . $field_data . ' ' ;		
			}elsif( lc($config->db_driver) eq 'mysql' ){
                $sql_create =  'Alter table ' . $setup_tables{$my_key}{name} . ' '. $field_data_mysql ;					 
			}else{
			    $sql_create =  'Alter table ' . $setup_tables{$my_key}{name} . ' '. 'add' . '(' . $field_data . ' )' ;							 
			 }		
			 if ( lc($config->db_driver) eq 'oracle' ){				
				$sql_create = uc($sql_create);		
			}
			# When user clicks on the add button
			if($input->param('column_add') eq 'Add'){
               	my $results = $dbh->do($sql_create) or die "execute failed:  $DBI::errstr\n$my_key - $sql_create\n";		 
				$vars{column_added} = 1;
                $vars{column_added_msg} = 'Column(s) has been added successfully';
				my $template = $config->template_directory . 'add_column.tmpl';
			   fill_and_send( $template, $user, \%vars , $config->html_use_ssi );
			         		  
			}			  
             $vars{column_exist} = 1;
             $vars{data_msg} = 'There are no fields to be added to this table.' if(!@noexist_columns_upload) ;			 
			 $vars{field_list} = \@noexist_columns_upload;
			 $vars{field_desc} = \@fields_desc;
			 $vars{hs_tables} = \%Tables;
             $vars{field_hash} = \%field_hash;					 
			 my $template = $config->template_directory . 'create_column.tmpl';
			 fill_and_send( $template, $user, \%vars , $config->html_use_ssi );
		}else{
			  $vars{data_message} = 1;
			  $vars{hs_tables} = \%Tables;			  
			  $vars{data_msg} = 'No more columns defined for this table in config file, plz upload updated .conf file' ;
			  my $template = $config->template_directory . 'create_column.tmpl';
			  fill_and_send( $template, $user, \%vars , $config->html_use_ssi );
		 }
			 
}elsif($input->param('submit') eq 'Upload') {
        
		my $upload_filehandle 	= $input->upload("data_file"); 
		my $filename			= $input->param("data_file") ;	
		$vars{msg_upload}		= 1 ; 
		$vars{message}			= $filename. " ". "has been uploaded successfully. Plz upload healthstatus_db.conf file if not uploaded yet." if $filename eq 'db_hs.conf';
		$vars{message}			= $filename. " ". "has been uploaded successfully. Plz upload db_hs.conf file if not uploaded yet." if $filename eq 'healthstatus_db.conf';
		my $template			= $config->template_directory . 'add_column.tmpl';
		chdir($upload_dir) or die("Cannot go to folder '$upload_dir'");
	    # Back up the existing files
		if ( -e $filename){	   

			my $backup_file = $config->conf_config_dir. "/" .$filename;			
			my $final_file  .= $backup_file . "_". "backup" . "_". $date_stamp;
			rename ($backup_file, $final_file );
			
	    }
		   &do_upload($filename,$upload_filehandle,$upload_dir);			 
		    fill_and_send( $template, $user, \%vars , $config->html_use_ssi );
#first time when template load
}else{   	  
			  	 
			  $vars{hs_tables} = \%Tables;      
			  my $template = $config->template_directory . 'create_column.tmpl';
			  fill_and_send( $template, $user, \%vars , $config->html_use_ssi );
}

#upload a file 
sub do_upload(){
	my $filename 			= shift ;
	my $upload_filehandle 	= shift ;  
	my $upload_dir 			= shift ;  
	open ( UPLOADFILE, ">$upload_dir/$filename" ) or die "$!";  
	binmode UPLOADFILE;  
	 
	while ( <$upload_filehandle> )  
	{  
	 print UPLOADFILE;  
	}  
	 
	close UPLOADFILE;
}

1;
