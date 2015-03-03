#!/usr/local/bin/perl
use strict;

# $Id: pager.cgi.PL,v 1.2 2010/04/27 11:01:23 code4hs Exp $

=head1 NAME

pager.cgi - pass data along a CGI template chain

=head1 SYNOPSIS

http://www.example.com/pager.cgi?#query_string#

=head1 DESCRIPTION

This CGI script accepts input from an HTML form, loads
a configuration, and a template specified by an image
submit input variable.

The control parameters for the templates are deleted,
and the rest of the parameters become hidden fields in
the template.

You specify the template file name with the name
of the image submit button.  That button name shows
up in the parameter list as C<name.x> and C<name.y>.
This script looks for the parameters ending in C<.x>
or C<.y>, then uses the preceding part of the parameter
name as the filename portion of the template.  The
template directory name comes from the configuration
file.

The C<Text::Template> template can access the following
variables:

	$hidden	- the hidden fields, as one string ready to use
	%config - this hash correspond directly to configuration directives

Additionally, all of the CGI parameters are available to
the template as variables of the same name.  Parameter
names show up as variables of the same name with non-word
characters removed. If you do not want problems with this,
don't use non-word characters in your parameter names.  (Word
characters are A-Z, a-z, 0-9, and the _ (underscore) ).  Note
that you can use non-word characters, specifically the . (full stop),
in the name of the image submit button since this parameter is
not available to the template.

=head1 ERRORS

This script will issue an error if it cannot read the
configuration or template file.  A short, vague message
is sent to the browser and a more detailed message should
show up in the error log.

=cut
use File::Basename        qw( dirname );
use File::Spec::Functions qw( rel2abs );

use lib dirname(rel2abs($0)),'.','/usr/local/www/vhosts/managed2/modules/pdf', '/usr/local/www/vhosts/managed2/modules';

use vars qw( $Debug $production $cook $config_file $nph);

# Removing warnings in log while module is being used with CGI version 4 or above
$CGI::LIST_CONTEXT_WARN = 0;

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
$CGI::POST_MAX=1024 * 100;  # max 100K posts
$CGI::DISABLE_UPLOADS = 1;  # no uploads
# Removing warnings in log while module is being used with CGI version 4 or above
$CGI::LIST_CONTEXT_WARN = 0;

use HealthStatus qw( fill_and_send error html_error );
use HealthStatus::Authenticate;
use HealthStatus::Config;
use HealthStatus::Constants;
use HealthStatus::Database;
use HealthStatus::User;

CGI->nph($nph) if $nph;
my $input = new CGI();
my $config = getConfig($input->param('extracfg'));
my $session = new CGI::Session(undef, undef, {Directory=>'../../sessions'}) or die CGI::Session->errstr;
#carp "Session id in pager is: ".$session->id();
my $cook = $session->param('hs_ident') || $input->param('hs_ident') || $input->cookie('hs_ident');
carp "Session id in pager is: ".$session->id()." cook is: ".$cook;
$session->save_param($input);
$session->clear(['page', 'prev.x', 'prev.y', 'next.x', 'next.y', 'next', 'prev']);
my @image_submits = map { lc } grep { m/\.[xy]$/i } $session->param;
$session->clear(\@image_submits);
$session->load_param($input);

my %hash = map { $_, $input->param($_) } $input->param();

my %config = map { $_, $config->$_ } $config->directives;

$hash{config} = \%config;

my %input = $input->Vars();

$cook = $session->param('hs_ident') || $input->param('hs_ident') || $input->cookie('hs_ident');

# authenticate_user redirects the user if they not allowed to
# view this page
my $user = authenticateUser('all', $input, $config) or die "You should never see this message.";

############################################################################
### Comment out the following line before going into production ############
$Debug = $input->param("HS_Debug") || $ENV{HS_DEBUG} || $Debug if !$production;
#### only uncomment if you need to debug the input scripts      ############
############################################################################

if ($Debug) {
	print "Content-type: text/plain\n\n";
	print "$ENV{SCRIPT_NAME} - $ENV{QUERY_STRING}\n";
	print "Modules Versions:\nHealthStatus - $HealthStatus::VERSION\nHealthStatus::Authenticate - $HealthStatus::Authenticate::VERSION\nHealthStatus::Database - $HealthStatus::Database::VERSION\n";
	print "HealthStatus::Config - $HealthStatus::Config::VERSION\nHealthStatus::User - $HealthStatus::User::VERSION\n\n";
	$config->pretty_print;
	$user->pretty_print;
}

# to get the name of the next template, look for parameters
# that end with .x or .y -- the result of the image submit
# the name of the parameter is the template name.
my @image_submit = grep m/\.[xy]$/, $input->param;

my( $template_name ) = $image_submit[0] =~ m/(.*)\.[xy]/i;
my $language = $input->param('language');
# delete control variables
$input->delete( $_ ) foreach @image_submit;

# make sure that the template exists
my $file = $config->template_directory . $template_name;

print "Template file = $file - $template_name\n" if $Debug;

html_error( $config, "Could not find output template - $file - $template_name",
	"Was looking for $file: $!" ) unless -r $file;

# pass along all of the data in hidden fields
#$hash{hidden_cgi_fields} = join "\n", map { $input->hidden($_) } $input->param;
$hash{language} = $language;
fill_and_send( $file, $user, \%hash, $config->html_use_ssi );

=head1 BUGS

=head1 TO DO

* it would be nice if the templates names in the HTML forms
were not the same as the actual file names.  that way, we could
allow only certain template names and never tell the user what
the file names are.

* the same problem exists for configuration files.

* you can specify different configuration files by modifying
the script to take the configuration file name from the input.
see the commented line with "hs_config".

=head1 AUTHOR

brian d foy E<lt>bdfoy@cpan.orgE<gt>
Greg White <gwhite@healthstatus.com>

=head1 COPYRIGHT

Copyright 2001-2007, HealthStatus.com

=cut

1;
