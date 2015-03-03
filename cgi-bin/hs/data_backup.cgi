#!/usr/local/bin/perl

use strict;
use DBI;
use File::Basename        qw( dirname );
use File::Spec::Functions qw( rel2abs );

use lib dirname(rel2abs($0)),'.','/usr/local/www/vhosts/managed2/modules/pdf', '/usr/local/www/vhosts/managed2/modules';

use vars qw( $Debug $production $config_file $cook $nph);

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
my $input = CGI->new();
my $config = getConfig($input->param('extracfg'));

my %hash = map { $_, $input->param($_) } $input->param();

my %config = map { $_, $config->$_ } $config->directives;

$hash{config} = \%config;

my %input = $input->Vars();
my $operating_system = $^O;

use Date::Calc;
use Archive::Zip qw( :ERROR_CODES :CONSTANTS );

use HealthStatus qw( fill_and_send error html_error );
use HealthStatus::Authenticate;
use HealthStatus::CalcRisk;
use HealthStatus::Config;
use HealthStatus::Constants;
use HealthStatus::Database;
use HealthStatus::User;
use Text::Template;


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

my $db = HealthStatus::Database->new( $config );
my $dbh  =  DBI->connect($config->db_connect, $config->db_user, $config->db_pass );
my $backup_folder = $config->backup_directory. "databases";
my $database = $config->db_database;
my $domain = $config->conf_install_site;
my @domain = split(/\./, $domain);
my $filename = $domain[0]. "_" .$date_stamp;

my $content;
if($input->param('Submit') eq 'Backup Now'){      
	    
		my $file_title = $input->param("db_backup");
		$file_title =~ s/\s+/\_/g;
	   (-d($backup_folder) or mkdir(($backup_folder || die("Failed to create $backup_folder: $!\n"))));        
		chdir($backup_folder) or die("Cannot go to folder '$backup_folder'");	 
		$content .=  "Backing up database ...<br> ";
		my $backup_tofile = $filename;        	
		$backup_tofile .= ".sql";
        $db->getDatabaseBackup($backup_tofile);     		
		$content .= "Backup has been completed successfully.<br>"; 
		$content .= "Compressing the file ... <br>";
		my $zip = Archive::Zip->new();
		my $member = $zip->addTreeMatching( $backup_folder, '' , '\.sql$' );
		die 'write error' unless $zip->writeToFileNamed( $file_title.'.zip' ) == AZ_OK;
		$content .= "Compression has been completed successfully.\n\n";
	    $hash{content} = $content;
		# Write the values in text file
		my $file_name = $backup_folder. "/" . "backup.txt"; 
		open (FILE,">>$file_name") || die("Can't open '$file_name': $!");
		print FILE "$file_title $backup_tofile $date\n";
		close(FILE);	
		  
	   
	   my $template = $config->template_directory . "data_backup.tmpl";
	   fill_and_send( $template, $user, \%hash , $config->html_use_ssi );
}else {
    	
		my $template = $config->template_directory . 'data_backup.tmpl';
		fill_and_send( $template, $user, \%hash , $config->html_use_ssi );
		exit;
 }
sub getFileContents {
	my $file = shift;
	open (FILE,$file) || die("Can't open '$file': $!");
	my @lines=<FILE>;
	close(FILE);

	return @lines;
}


