#!/usr/local/bin/perl
use strict;

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
# Removing warnings in log while module is being used with CGI version 4 or above
$CGI::LIST_CONTEXT_WARN = 0;

use HealthStatus qw( fill_and_send error html_error );
use HealthStatus::Constants;
use HealthStatus::Database;
use CGI::Carp;
use CGI::Carp qw(fatalsToBrowser);

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

my $user = authenticateUser(["admin", 'coach'], $input, $config) or die "You should never see this message.";

my @assessments_allowed = @{$$config{common_assessments}};
my %vars;

my $db = HealthStatus::Database->new($config);
my $dbh = $db->getDbh;

my %table_names = $db->all_table_names();

my %vars;
$vars{config} = $config->as_hash();
$vars{assessment_types} = $$config{common_assessments};

my $stipulations;
# If group limitation is on, make sure the results consist only of their group members
if ($config->group_limit_admin && $user->db_id ne $config->group_limit_admin_master) {
	$stipulations =  "where " . $config->group_limit_admin_key . " LIKE " . $$config{db}->quote($user->{$config->group_limit_admin_value} . "%")  ;
}

#$vars{site_list} = [$$config{db}->site_list($stipulations)];
my $table = $table_names{REG};
#my $stipulation = 'where group_status = "active"';

my $email_sql =  "select * from $table_names{GRP} where group_status='active'";
#my $email_sth = $dbh->prepare($email_sql);
my $email_sth = $dbh->prepare($email_sql);
$email_sth->execute();
my @email;
#print "Content-type:text/html \n\n";
my (@results, $hash_ref);
while( my $hash_ref  = $email_sth->fetchrow_hashref())
{
	  my %lc_hash;
      @lc_hash{ map { lc($_) } keys(%{$hash_ref}) }  =  values(%{$hash_ref});
      $hash_ref  =  \%lc_hash;
       push @results, $hash_ref;
}
$vars{site_list} = \@results;

# authenticate_user redirects the user if they are not allowed to
# view this page
my $user = authenticateUser(["admin", 'coach'], $input, $config) or html_error( "There was a problem with your login and accessing this area.");
fill_and_send( $config->template_directory . "admin_search_assessments.tmpl", $user, \%vars, $config->html_use_ssi );
