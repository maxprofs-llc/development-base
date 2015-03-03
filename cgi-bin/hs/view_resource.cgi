#!/usr/local/bin/perl

use strict;

=head1 NAME

view_resource.cgi view resource(PDF) files

=cut

use File::Basename        qw( dirname );
use File::Spec::Functions qw( rel2abs );

use lib dirname(rel2abs($0)),'.','/usr/local/www/vhosts/managed2/modules/pdf', '/usr/local/www/vhosts/managed2/modules';

use vars qw( $Debug $production $cook $config_file $nph);

if (!do('common.inc')) {
   my $error = $@ ? $@
             : $! ? $!
             : 'did not return a true value';
   die("Unable to load common stuff: $error\n");
}
use IO::File;
use HealthStatus;


my $input = new CGI();
my $config = getConfig($input->param('extracfg'));

my %hash = map { $_, $input->param($_) } $input->param();

my %config = map { $_, $config->$_ } $config->directives;

$hash{config} = \%config;

my %input = $input->Vars();

$cook = $input->param('hs_ident') || $input->cookie('hs_ident');

############################################################################
$Debug = $input->param("HS_Debug") || $ENV{HS_DEBUG} || $Debug if !$production;
#### only uncomment if you need to debug the input scripts      ############
############################################################################

if ($Debug) {
	print "Content-type: text/plain\n\n";
	print "$ENV{SCRIPT_NAME} - $ENV{QUERY_STRING}\n";
	print "Modules Versions:\nHealthStatus - $HealthStatus::VERSION\nHealthStatus::Authenticate - $HealthStatus::Authenticate::VERSION\nHealthStatus::Database - $HealthStatus::Database::VERSION\n";
	print "HealthStatus::Config - $HealthStatus::Config::VERSION\nHealthStatus::User - $HealthStatus::User::VERSION\n\nText::Template - $Text::Template::VERSION\nHTML::FillInForm - $HTML::FillInForm::VERSION\n\n";
	foreach my $key ( sort keys %input )
		{
		print "\t$key\t\t$input{$key}\n";
		}
	print "Cookie hs_ident = " .$input->cookie('hs_ident') ."\n";
	}

my $user = authenticateUser(["admin"], $input, $config) or die "You should never see this message.";

my $format = lc($input->param('format')) || 'pdf';

print "$format\n" if $Debug;

my $shortfile_name = $input->param('file_name');
my $no_ext_shortfile_name = $shortfile_name;
$shortfile_name .= '.' . $format ;
my $resource_path;
if($ENV{HTTP_HOST} =~ m/healthstatus\.com/) {
	$resource_path = "/usr/local/www/hs_utils/resource_pdf/";
} else {
	$resource_path = $config{pdf_base}."/resource/";
}

my $output_file_name = $resource_path . $shortfile_name  ;

# View the different output files in the browser.

	my $type;
	if($format eq 'pdf')
		{
		$type='application/pdf';
		}
	if($format eq 'xls')
		{
		$type='application/vnd.ms-excel';
		}
	if($format eq 'zip')
		{
		$type='application/x-zip-compressed';
		}
	if($format eq 'xml')
		{
		$type='text/xml';
		}
	if($format eq 'csv')
		{
		$type='text/plain';
		}
	my $f = new IO::File "$output_file_name", "r" or die "$output_file_name: $!\n";
	my $file = do { local $/; binmode $f; <$f> };

	print $input->header(-type=>$type, -attachment =>$shortfile_name ), $file;
	exit;
