#!/usr/local/bin/perl
use strict;

$| = 1;

=head1 NAME

show_template.cgi - Displays a template file.

=head1 DESCRIPTION

This script provides the basic functions of output of a template file to the screen.


=head1 INPUT

This script depends on certain control parameters to tell it what to
do.

	template - name of the file to be retrieved

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

my $input = new CGI();
my $config = getConfig($input->param('extracfg'));

my %hash = map { $_, $input->param($_) } $input->param();

my %config = map { $_, $config->$_ } $config->directives;

$hash{config} = \%config;

# authenticate_user redirects the user if they are not allowed to
# view this page
my $user = authenticateUser('all', $input, $config) or die "You should never see this message.";

my @assessments_allowed = @{$$config{common_assessments}};
my %vars;
$hash{config} = $config->as_hash();
$vars{assessment_types} = \@assessments_allowed;
$vars{site_list} = [$$config{db}->site_list()];

my $template =  $config->template_directory . $input->param('template');

foreach my $key ( $user->attributes ) { $hash{$key} = $user->get($key) }

fill_and_send( $template, $user, \%hash, $config->html_use_ssi );
