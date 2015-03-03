#!/usr/local/bin/perl
use strict;

$| = 1;

=head1 NAME

show_docs.cgi - Prints files from non-web accessible areas.

=head1 DESCRIPTION

This script provides the basic functions of printing non-html files,
PDF, XML, XLS and such for documentation or output for various reasons.

User must be an administrator, coach or clerk to view the requested files.

=head1 INPUT

This script depends on certain control parameters to tell it what to
do.

	file_name - name of the file (without extension) to be retrieved

	file_fmt - extension to be printed (so we can set the mime time)

	global - flag to indicate that a file should be found in the central
	         repository (not customized)

=head2 OUTPUT

The script creates a mime header and uploads the file to the browser.

=head1 ERRORS

This script will issue an error if it cannot read the
configuration or template file.  A short, vague message
is sent to the browser and a more detailed message should
show up in the error log.

If the script cannot recognize the value of the control parameter
C<action> it outputs
an error page.

=cut

use vars qw( $Debug $production $cook $config_file $nph);

if (!do('common.inc')) {
   my $error = $@ ? $@
             : $! ? $!
             : 'did not return a true value';
   die("Unable to load common stuff: $error\n");
}
# Removing warnings in log while module is being used with CGI version 4 or above
$CGI::LIST_CONTEXT_WARN = 0;
use IO::File;

my $input = new CGI();
my $config = getConfig($input->param('extracfg'));
my $session = new CGI::Session(undef, undef, {Directory=>'../../sessions'}) or die CGI::Session->errstr;
$session->save_param();

my %hash = map { $_, $input->param($_) } $input->param();

my %config = map { $_, $config->$_ } $config->directives;

$hash{config} = \%config;

my %input = $input->Vars();

$cook = $session->param('hs_ident') || $input->param('hs_ident') || $input->cookie('hs_ident');
$session->param('hs_ident',$cook);
$session->load_param($input);

# authenticate_user redirects the user if they are not allowed to
# view this page
my $user = authenticateUser(["admin", 'coach', 'clerk'], $input, $config) or die "You should never see this message.";

my @assessments_allowed = @{$$config{common_assessments}};
my %vars;
$vars{config} = $config->as_hash();
$vars{assessment_types} = \@assessments_allowed;
$vars{site_list} = [$$config{db}->site_list()];

my $format = lc($input->param('file_format')) || 'pdf';

print "$format\n" if $Debug;

my $shortfile_name = $input->param('file_name') || 'ggr_output';
my $shortfile_name_no_ext = $shortfile_name;
$shortfile_name .= '.' . $format ;
my $dir;
if($input->param('global')){
	$dir = $config->documentation_page_dir ||  $config->template_directory;
	}
else	{
	$dir = $config->template_directory;
	}
my $output_file_name = $dir . $shortfile_name;

# View the different output files in the browser.
my $bin_set = 0;
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

my $f = new IO::File "$output_file_name", "r" or errorPageAndExit("Output file not found: $output_file_name", $user, $config);
my $file = do { local $/; binmode $f; <$f> };

if($input->param('lw')){
	print $input->header(-type=>$type), $file;
	}
else	{
	print $input->header(-type=>$type, -attachment =>$shortfile_name ), $file;
	}
