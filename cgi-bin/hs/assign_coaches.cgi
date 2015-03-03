#!/usr/local/bin/perl
use strict;

use CGI::Carp;
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

my $input = CGI->new();
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

my %vars;
$vars{config} = $config->as_hash();

# authenticate_user redirects the user if ey is not allowed to
# view this page
my $user = authenticateUser("admin", $input, $config) or die "You should never see this message.";
my $action = $input->param('action');
my $coach = get_coach();
$vars{coach_user} = $coach;

## Main action loop
if ($action eq 'view_coached') {
	send_coach_view();
}
elsif ($action eq 'add_coachee') {
	set_coach($input->param('new_coachee'), $coach);
	send_coach_view();
}
elsif ($action eq 'remove_coachees') {
	remove_coachees($coach, [$input->param('select_coached')]);
	$vars{msg} = "The specified users have been removed from this coaching list.";
	send_coach_view();
}
else {
	$vars{coach_list} = get_user_names(' WHERE rank=\'coach\'');
	fill_and_send( $config->template_directory . "admin_assign_coach1.tmpl", $user, \%vars, $config->html_use_ssi );
}


sub get_coach {
	my $coach = $input->param('coach');
	if (!defined $coach || $coach !~ /^\d+$/) {return undef;}
	return @{get_user_names(" WHERE unum=$coach AND rank='coach'")}[0];
}


# Gets minimal list of users - just the username, full name, and unum
sub get_user_names {
	my ($stipulations) = @_;
	my @ulist = $$config{db}->select([qw(unum full_name hs_uid)], $HealthStatus::Database::Tables{REG}, $stipulations, 1);
	if(!@ulist) {return [];}
	foreach my $c (@ulist) {$$c{name} = "$$c{full_name} ($$c{hs_uid})";}
	return \@ulist;
}

sub remove_coachees {
	my ($coach, $coachee_list) = @_;
	if (grep (/\D/, @$coachee_list)) {die "Non-numeric coachee requested for deletion.";}
	return $$config{db}->update($HealthStatus::Database::Tables{REG}, {coach=>undef}, " WHERE coach=$$coach{unum} AND unum IN (" .
															join(',',@$coachee_list) . ')')
}

sub send_coach_view {
	$vars{coached_list} = get_user_names(" WHERE coach=$vars{coach_user}{unum}");
	$vars{potential_coachees_list} = get_user_names(" WHERE rank='user' AND (coach IS NULL OR coach='')");
	fill_and_send( $config->template_directory . "admin_assign_coach_view.tmpl", $user, \%vars, $config->html_use_ssi );
}

sub set_coach {
	my ($coachee, $coach) = @_;
	if ($coachee !~ /^\d+$/ || $$coach{unum} !~ /^\d+$/) {die "Coachee or coach number was invalid.";}
	return $$config{db}->update($HealthStatus::Database::Tables{REG}, {coach=>$$coach{unum}}, " WHERE unum=$coachee");
}
