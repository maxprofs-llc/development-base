#!/usr/local/bin/perl
use strict;
use File::Basename        qw( dirname );
use File::Spec::Functions qw( rel2abs );

use lib dirname(rel2abs($0)),'.','/usr/local/www/vhosts/managed2/modules/pdf', '/usr/local/www/vhosts/managed2/modules';

use vars qw( $Debug $production $cook $config_file);

use subs qw( error );

if (!do('common.inc')) {
   my $error = $@ ? $@
             : $! ? $!
             : 'did not return a true value';
   die("Unable to load common stuff: $error\n");
}

use CGI qw(-no_xhtml -debug);
use CGI::Carp qw(fatalsToBrowser);
use Date::Calc;
use HTML::FillInForm;
use Text::Template;

use HealthStatus::Config;
use HealthStatus;
use HealthStatus::User;
use HealthStatus::Constants;

my $input = new CGI();
my $config = getConfig($input->param('extracfg'));

my @assessments_allowed = split /\s+/, $config->ggr_adv_tables;
my %vars;
$vars{config_names} = $config->pretty_dump;
$vars{config} = $config->as_hash();
$vars{assessment_types} = \@assessments_allowed;
$vars{site_list} = [$$config{db}->site_list()];

# authenticate_user redirects the user if ey is not allowed to
# view this page
my $user = authenticateUser(["admin"], $input, $config) or die "You should never see this message.";
fill_and_send( $config->template_directory . "admin_config_list.tmpl", $user, \%vars, $config->html_use_ssi ); 