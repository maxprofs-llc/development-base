#!/usr/local/bin/perl
use strict; 

if (!do('common.inc')) {
   my $error = $@ ? $@
             : $! ? $!
             : 'did not return a true value';
   die("Unable to load common stuff: $error\n");
}
use File::Basename        qw( dirname );
use File::Spec::Functions qw( rel2abs );

use lib dirname(rel2abs($0)),'.','/usr/local/www/vhosts/managed2/modules/pdf', '/usr/local/www/vhosts/managed2/modules';
use vars qw( $Debug );
use CGI;
use Net::SFTP;
use Math::BigInt;
use Date::Calc qw( Date_to_Days check_date);
use HealthStatus qw( fill_and_send error html_error );
use Carp;

my $input 		= new CGI();
my $config 		= getConfig($input->param('extracfg'));

my %input 		= $input->Vars();
my %hash 		= map { $_, $input->param($_) } $input->param();
my %config 		= map { $_, $config->$_ } $config->directives;

$hash{config} 	= \%config;
$input{config} 	= $config->as_hash();

my ($results, $output, $display_message, %version_hash);
# authenticate_user redirects the user if they is not allowed to
# view this page
my $user 		= authenticateUser("admin", $input, $config) or die "You should never see this message.";
############################################################################
### Comment out the following line before going into production ############
$Debug = $input->param("HS_Debug") || $ENV{HS_DEBUG} || 0;
#### only uncomment if you need to debug the input scripts      ############
############################################################################

if ($Debug) {
	print "Content-type: text/plain\n\n";
	print "Modules Versions:\nHealthStatus - $HealthStatus::VERSION\nHealthStatus::Authenticate - $HealthStatus::Authenticate::VERSION\nHealthStatus::Database - $HealthStatus::Database::VERSION\n";
	print "HealthStatus::Config - $HealthStatus::Config::VERSION\nHealthStatus::User - $HealthStatus::User::VERSION\n\n";
	$config->pretty_print;
}

my $remote = "/usr/local/www/vhosts/current_files/data/";

# connect to remote healthstatus server 
my $sftp = eval {  Net::SFTP->new("216.235.79.100", user => $config->sftp_username, password => $config->sftp_password, ssh_args => [ options => [ "UserKnownHostsFile ".$config->ggr_adv_page_dir.".ssh/known_hosts2" ] ]); };


if(!$@){
	if($input->param('update') && $input->param('filename')) {
		my $remote_file = $remote.$input->param('filename');
		my $local  = $config{$input->param('local_config')};
		   $local .= $input->param('filename') if(!($input->param('filename') eq "male.dat" or $input->param('filename') eq "female.dat")) ; 
		
		# get the file from the remote server 
		my $file_content = $sftp->get($remote_file);
		
		# update the local file from the remote server 
		open (FH, "> $local") || die ("Could not open file <br> $!");
		print FH $file_content;
		close (FH); 
		$display_message = $input->param('filename')." has been updated successfully.";
	}
	my @dir_lit = $sftp->ls($remote );
	my @filenames;
	
	#get the file names from the directory
	foreach( @dir_lit)	{
		my %file_hash = %{$_};
		next if $file_hash{filename} eq '.' or $file_hash{filename} eq '..' ;
		push @filenames,$file_hash{filename};
	}
	carp @filenames;
	
	foreach my $file(@filenames) {
		my $path = $remote.$file;
		#read the version and config variable of remote server file
		my $handle = $sftp->do_open($path);
		my $remote_data = $sftp->do_read($handle,0,50);
		$sftp->do_close($handle);
	
		$remote_data =~ m/<!--(.*)-->/;
		$remote_data = $1;
		carp "remote_data=".$remote_data."\n";
		my ($remote_file_version,$file_config) = split(',',$remote_data);
				
		my $local_file_path  = $config{$file_config};
		   $local_file_path .= $file if(!($file eq "male.dat" or $file eq "female.dat")) ; 
		carp "local_file_path=".$local_file_path."\n";  
		if (-e $local_file_path) {
			#read the version and config variable of local server file
			open (FILE, $local_file_path) || die ("Could not open file <br> $!");
			my $local_file_data = <FILE>;
			close (FILE); 
			
			$local_file_data =~ m/<!--(.*)-->/;
			carp "local_file_data=".$1."\n";
			my ($local_file_version, $local_config) = split(',', $1);
			carp "local_file_version=".$local_file_version."\n";
			my ($year1,$month1,$day1) = split('/',$remote_file_version);
			my ($year2,$month2,$day2) = split('/',$local_file_version);

			if (check_date($year1,$month1,$day1) && check_date($year2,$month2,$day2)) {
				# compare remote file version to local file version
				if (Date_to_Days($year1,$month1,$day1)  > Date_to_Days($year2,$month2,$day2)) {
					$version_hash{$file}{old} = 1;
				} else {
					$version_hash{$file}{old} = 0;
				}
				$version_hash{$file}{server_file_date} = $remote_file_version;
				$version_hash{$file}{local_file_date} = $local_file_version;
			} else {
				$version_hash{$file}{server_file_date} = "Invalid Date";
				$version_hash{$file}{local_file_date} = "Invalid Date";
			}
			$version_hash{$file}{local_config} = $local_config;
		}
		
		
	}
} else {
	$display_message	= "You are not able to connect Healthstatus server.";
}

$input{version_hash}	= \%version_hash;
$input{display_message}	= $display_message;


fill_and_send( $config->template_directory . 'update_files.tmpl', $user, \%input, $config->html_use_ssi );		
	
exit;
