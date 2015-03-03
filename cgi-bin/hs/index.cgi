#!/usr/local/bin/perl
use strict;

use File::Basename        qw( dirname );
use File::Spec::Functions qw( rel2abs );

use lib dirname(rel2abs($0)),'.','/usr/local/www/vhosts/managed1/modules/pdf', '/usr/local/www/vhosts/managed1/modules';

use vars qw( $Debug $production $cook $config_file $nph);

if (!do('common.inc')) {
   my $error = $@ ? $@
             : $! ? $!
             : 'did not return a true value';
   die("Unable to load common stuff: $error\n");
}
# Removing warnings in log while module is being used with CGI version 4 or above
$CGI::LIST_CONTEXT_WARN = 0;

use CGI::Carp;
use HealthStatus qw ( error html_error fill_and_send );
use Date::Calc;


my $input = new CGI();
my $config = getConfig($input->param('extracfg'));
my $session = new CGI::Session(undef, undef, {Directory=>'../../sessions'}) or die CGI::Session->errstr;
carp "Session id in assessment_recs is: ".$session->id();
$session->save_param();

my %hash = map { $_, $input->param($_) } $input->param();

my %config = map { $_, $config->$_ } $config->directives;

$hash{config} = \%config;

my %input = $input->Vars();

$cook = $session->param('hs_ident') || $input->param('hs_ident') || $input->cookie('hs_ident');
$session->param('hs_ident',$cook);
$session->load_param($input);

my %vars;
# authenticate_user redirects the user if they are not allowed to
# view this page
my $user = authenticateUser('all', $input, $config) or die "You should never see this message.";
#$user->pretty_print(\*STDERR);

my @assessments_allowed = 'GHA';
#my @assessments_allowed = @{$$config{common_assessments}};
my @batch_assessments = @{$$config{batch_assessments}};

my $restriction;
if($config->ggr_adv_multi_admin){
	my @sname = split /\s+/, $config->ggr_adv_multi_admin_key;
	my @svalue = split /\s+/, $config->ggr_adv_multi_admin_value;
	my @smaster = split /\s+/, $config->ggr_adv_multi_admin_master;
	my $cnt=0;

        while ($cnt < scalar(@sname) && $smaster[$cnt] ne $user->db_id){
		my $restrict_full = $user->{$svalue[$cnt]};
		$restriction = "where " if $cnt == 0;
		$restriction .= " and " if $cnt != 0;
		$restriction .= "$sname[$cnt] like '" . $restrict_full . "%'";
		$cnt++;
		}
	}

$vars{config} = $config->as_hash();
$vars{assessment_types} = \@assessments_allowed;
$vars{batch_assessment_types} = \@batch_assessments;
$vars{user_count} = $$config{db}->count_of_hs_users($restriction);
my %assessment_stuff;
foreach (@assessments_allowed){
	$assessment_stuff{$_}{name} = assessment_name($_);
	$assessment_stuff{$_}{count} = $$config{db}->count_of_hs_assessments($_, $restriction);
	}
$vars{assessment_stuff} = \%assessment_stuff;

$config->template_directory . $config->login_failed;

fill_and_send( $config->template_directory . "admin_home.tmpl", $user, \%vars, $config->html_use_ssi );
