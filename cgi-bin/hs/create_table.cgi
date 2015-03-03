#!/usr/local/bin/perl
use strict;


use File::Basename        qw( dirname );
use File::Spec::Functions qw( rel2abs );

use lib dirname(rel2abs($0)),'.','/usr/local/www/vhosts/managed2/modules/pdf', '/usr/local/www/vhosts/managed2/modules';

use vars qw( $Debug $production $cook $config_file %ORACLE_CVRT %setup_tables %field_info %Tables %Fields);

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
my $input = new CGI();
my $config = getConfig($input->param('extracfg'));
my %hash = map { $_, $input->param($_) } $input->param();

my %config = map { $_, $config->$_ } $config->directives;

$hash{config} = \%config;
my $silent;
my %input = $input->Vars();
my $getsql = $input->param('getsql');
if($getsql) {$silent=1;}
my $sql = '';

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



my $db1 = HealthStatus::Database->new( $config );
my $dbh  =  DBI->connect($config->db_connect, $config->db_user, $config->db_pass );

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
my @tables;
if ( lc($config->db_driver) eq 'mssql' ){
   my @row;
   my $str = 'select table_name from information_schema.tables';
   my $tables_from_db = $dbh->prepare($str);
		$tables_from_db->execute();
		 while ( @row = $tables_from_db->fetchrow_array ) { 
			push(@tables, @row[$_]);
		}
}elsif ( lc($config->db_driver) eq 'oracle' ){ 
   my @row;
   my $str = "SELECT TABLE_NAME FROM USER_TABLES WHERE TABLE_NAME LIKE 'HS%'";
   my $tables_from_db = $dbh->prepare($str);
		$tables_from_db->execute();
		 while ( @row = $tables_from_db->fetchrow_array ) { 
			push(@tables, @row[$_]);			
		} 
}else{
 @tables = $dbh->tables();
 }
	
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
	 # To find database tables
	 my @database_tables;
     foreach my $db_key(@modify_tables){
		  if ( lc($config->db_driver) eq 'oracle' ){
				push(@database_tables, $ORACLE_CVRT{$db_key});	
			}else{
			@database_tables = @modify_tables;
			}
		 }
     # To find config tables		 
	 foreach my $hs_table (keys %Tables){
			if ( lc($config->db_driver) eq 'oracle' ){
				push(@hs_table, $Tables{$hs_table});	
			}else{
			push(@hs_table, $Tables{$hs_table});
			}
	  }	 	
	  my %total_tables;
	  my @config_tables = @hs_table;	        
	  @total_tables{@database_tables} = ();
	  @noexist_tables = grep{!exists $total_tables{$_}} @config_tables; 
      
if($input->param('submit') eq 'Upload') {
        
		my $upload_filehandle = $input->upload("data_file"); 
		my $filename		  = $input->param("data_file") ;	
		
		chdir($upload_dir) or die("Cannot go to folder '$upload_dir'");
	  if ( -e $filename){	   

			my $backup_file = $config->conf_config_dir. "/" .$filename;			
			my $final_file  .= $backup_file . "_". "backup" . "_". $date_stamp;
			rename ($backup_file, $final_file );
			
	   }
		   &do_upload($filename,$upload_filehandle,$upload_dir); 		
		    
		my @database_tables;
        foreach my $db_key(@modify_tables){
		  if ( lc($config->db_driver) eq 'oracle' ){
				push(@database_tables, $ORACLE_CVRT{$db_key});	
			}else{
			@database_tables = @modify_tables;
			}
		 } 		   
		foreach my $hs_table_uploads (keys %Tables){
				if ( lc($config->db_driver) eq 'oracle' ){
				push(@hs_table_uploads, $Tables{$hs_table_uploads});	
			   }else{			
				push(@hs_table_uploads, $Tables{$hs_table_uploads});					
			  }
		}	  
		  my %total_tables_upload;
		  my @config_tables = @hs_table_uploads;		            		  
		  @total_tables_upload{@database_tables} = ();
		  @noexist_tables_upload = grep{!exists $total_tables_upload{$_}} @config_tables; 
		
		foreach my $keys (keys %Tables){	    
			$hs_table_upload{$keys}= $Tables{$keys};         	  
	         }
		$vars{no_table} = \@noexist_tables_upload;	  
		$vars{db_table} = \@database_tables;	 
		$vars{hs_tables} = \%hs_table_upload;
        $vars{data_msg}		  = 1 ; 
		$vars{message}		  = $filename. " ". "has been uploaded successfully. Plz upload healthstatus_db.conf file if not uploaded yet." if $filename eq 'db_hs.conf';
		$vars{message}		  = $filename. " ". "has been uploaded successfully. Plz upload db_hs.conf file if not uploaded yet." if $filename eq 'healthstatus_db.conf';
		my $template		  = $config->template_directory . 'add_tables.tmpl';   		
		fill_and_send( $template, $user, \%vars , $config->html_use_ssi );
	
}elsif($input->param('table_add') eq 'add') { 
        my $value = $input->param('add_table'); 			
		my @arr;
		my $my_key;
		foreach my $key_value(keys %setup_tables){
		   if($setup_tables{$key_value}{name} eq $input->param('add_table')) {
		        $my_key =  $key_value;
				@arr = split /\s+/, $setup_tables{$key_value}{fields};
		   }
		 }
        if (exists($setup_tables{$my_key})){		   	  
		  
			my @field_list = split /\s+/, $setup_tables{$my_key}{fields};			
			my @create_fields = ();
			my @indices = ();

			foreach my $field (@field_list) {
				my $temp = $field . ' ' . $field_info{$field}{lc($config->db_driver)};
				push @create_fields, $temp;
				if ($field_info{$field}{index}) {push @indices, $field;}
			}

			my $field_data = join ", ", @create_fields;
			my $sql_drop = 'drop table ' . $setup_tables{$my_key}{name};
			my $sql_create = 'create table ' . $input->param('add_table') . '(' . $field_data . ')';
			my $primary_create = '';
			my $primary_add = '';
			my $table_name = $setup_tables{$my_key}{name};

			if ($setup_tables{$my_key}{primary} ne ''){
				if ( lc($config->db_driver) eq 'mysql') {
					$primary_add = ', PRIMARY KEY (' . $setup_tables{$my_key}{primary} .')';
					}
				else	{
					$primary_create = 'Alter table ' . $setup_tables{$my_key}{name} . ' add primary key (' . $setup_tables{$my_key}{primary} .')';
					}
				}
			my $sql_create = 'create table ' . $setup_tables{$my_key}{name} . '(' . $field_data . $primary_add . ')';
            
			if ( lc($config->db_driver) eq 'oracle' ){
				$sql_drop = uc($sql_drop);
				$sql_create = uc($sql_create);
				$primary_create = uc($primary_create);
				$table_name = uc($table_name);
				}			
            
			if(!$exists{lc($table_name)}) {			

					if($getsql) {$sql .= "\n$sql_create;"; 					
					}
					else {					   
						my $results = $dbh->do($sql_create) or die "execute failed:  $DBI::errstr\n$my_key - $sql_create\n";
					}

				if ( $primary_create ){
					# print "<br>creating primary key for $setup_tables{$my_key}{name}" if (!$silent);

					if($getsql) {$sql .= "\n$primary_create;"; }
					else {
						my $results = $dbh->do($primary_create) or die "execute failed:  $DBI::errstr\n$my_key - $primary_create\n";
					}
				}
			}

			foreach (@indices) {
				next if $_ eq $setup_tables{$my_key}{primary};
				# print "<br />Adding index ${table_name}_$_ to $setup_tables{$my_key}{name}" if !$silent;
				my $idx_sql = "CREATE INDEX ${table_name}_$_ ON $table_name ($_)";

				if($getsql) {$sql .= "\n$idx_sql;"; }
				else {
					my $results = $dbh->do($idx_sql) or print "<br>&nbsp; &nbsp; Could not add index ${table_name}_$_: " . print DBI::errstr if (!$silent);
				}
			}      
                 $vars{add_message} = 1;			
		         $vars{add_msg} = 'Table has been added successfully.';
				 my $template = $config->template_directory . 'add_tables.tmpl';
				 fill_and_send( $template, $user, \%vars , $config->html_use_ssi );
		   }else{
		         $vars{add_message} = 1;
			     $vars{add_msg} = 'Data is not available for this table, plz upload the updated config file.';
				 my $template = $config->template_directory . 'add_tables.tmpl';
				 fill_and_send( $template, $user, \%vars , $config->html_use_ssi ); 
             }
 			 
}else{   
				
			  $vars{no_table} = \@noexist_tables;	  
			  $vars{db_table} = \@database_tables;	 
			  $vars{hs_tables} = \%Tables;      
			  my $template = $config->template_directory . 'create_table.tmpl';
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
