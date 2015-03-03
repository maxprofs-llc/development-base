#!/usr/local/bin/perl
use strict;

#  This includes the current directory in the list of places to check for
# modules and other files, mainly for NT systems.
use File::Basename        qw( dirname );
use File::Spec::Functions qw( rel2abs );
use Date::Language;
use Date::Parse;
use Date::Format;
use lib dirname(rel2abs($0)),'.','/usr/local/www/vhosts/managed2/modules/pdf', '/usr/local/www/vhosts/managed2/modules';

use vars qw( $Debug $production $cook $config_file);

if (!do('common.inc')) {
   my $error = $@ ? $@
             : $! ? $!
             : 'did not return a true value';
   die("Unable to load common stuff: $error\n");
}

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
use HealthStatus::Email;

use Data::Dumper;

	my $input 			= new CGI();

	my $config 			= getConfig($input->param('extracfg'));
	my %config 			= map { $_, $config->$_ } $config->directives;

	my %input 			= $input->Vars();

	############################################################################
	### Comment out the following line before going into production ############
	$Debug = $input->param("HS_Debug") || $ENV{HS_DEBUG} || 0;
	#### only uncomment if you need to debug the input scripts      ############
	############################################################################

	# authenticate_user redirects the user if they not allowed to
	# view this page
	my $user 	= authenticateUser(["admin"], $input, $config) or die "You should never see this message.";

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

	my %vars;
	my $upload_dir                  = $config->conf_data_dir . "/IMPORT";
	if($input->param('submit') eq 'Undo Import')
	{
        	my $selectedtime 	= $input->param('undo_file');

        	my $db 			= HealthStatus::Database->new( $config );

		open (FILE, "$upload_dir/IMPORT_$selectedtime") ;
		while (<FILE>)
		{
                	chomp;
                	next if ($_ =~ /^\s*$/);
                	$_ =~ s/\'//g;
                	$db->execute_sql($_);
        	}

        	$db->disconnect( );
        	$vars{data_undo_msg}            = 1;
        	$vars{message}                  = "Data undo Successful\n";
	}
	else
	{
        	my %undo_file_hash;
        	opendir (DIR, $upload_dir) or die  $!;
		my $flag=0;
	
        	while (my $file = readdir(DIR))
        	{
			# Use a regular expression to ignore files beginning with a period
                	next if ($file =~ m/^\./);

                	if ($file =~ m/IMPORT_(\d{14})$/)
                	{
                        	my $year 	= 	substr($1, 0, 4);
                        	my $month 	= 	substr($1, 4, 2);
                        	my $day 	= 	substr($1, 6, 2);
                        	my $hr 		= 	substr($1, 8, 2);
                        	my $min		= 	substr($1, 10, 2);
                        	my $sec 	= 	substr($1, 12, 2);
                        	my $timestamp 	= 	sprintf("%02d-%02d-%04d %02d:%02d:%02d", $month, $day, $year, $hr, $min, $sec);
                        	$undo_file_hash{$timestamp}= $1;
				$flag		=	1;

                	}
        	}
        	$vars{undo_file_hash} = \%undo_file_hash;
		$vars{data_undo_msg}	= "No Previous Import done to undo data." if (!$flag);
	}
        my $template = $config->template_directory . 'undo_import.tmpl';
        fill_and_send( $template, $user, \%vars, $config->html_use_ssi );


1;
