#!/usr/local/bin/perl
use strict;

use vars qw( $Debug $production $cook $config_file $nph);

if (!do('common.inc')) {
   my $error = $@ ? $@
             : $! ? $!
             : 'did not return a true value';
   die("Unable to load common stuff: $error\n");
}
# Removing warnings in log while module is being used with CGI version 4 or above
$CGI::LIST_CONTEXT_WARN = 0;

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

my $MAX_PER_PAGE = 50;
my $page = ($input->param('page') || 1);

# authenticate_user redirects the user if ey is not allowed to
# view this page
my $user = authenticateUser(['admin','coach'], $input, $config) or die "You should never see this message.";
$config->template_directory . $config->login_failed;

###########################################################
#### Create WHERE clause and perform assessment search ####
my @search_terms;

# If group limitation is on, make sure the results consist only of their group members
if ($config->group_limit_on) {
	push @search_terms, "u." . $config->group_limit_field . "= " . $$config{db}->quote($user->{$config->group_limit_user_val}) ;
#	carp "group limit = u." . $config->group_limit_field . " = " . $$config{db}->quote($user->{$config->group_limit_user_val}) ;
}

# If the user is a coach, make sure the results consist only of their coachees
if ($user->hs_administration() eq 'coach') {
	push @search_terms, "u.coach=" . $$config{db}->quote($user->db_number);
}

if ($input->param('coach')) {
	push @search_terms, "u.coach=" . $$config{db}->quote(input->param('coach'));
}

if($input->param('search_uname')) {
	my $quoted = $$config{db}->quote(lc($input->param('search_uname')) . '%');
	push @search_terms, "(LOWER(a.first_name) LIKE $quoted OR LOWER(a.last_name) LIKE $quoted)";
}

if($input->param('search_uid')) {
	my $quoted = $$config{db}->quote(lc($input->param('search_uid')) . '%');
	push @search_terms, "(LOWER(a.hs_uid) LIKE $quoted)";
}
my @requested_assessments = $input->param('search_assessment_type');

my $from_date = $input->param('search_from');
if($from_date) {
	if ($from_date !~ /^(\d{2})\/(\d{2})\/(\d{4})$/) {errorPageAndExit("Dates must be in the format: \"mm/dd/yyyy\" (Invalid date: '$from_date')", $user, $config);}
	push @search_terms, "a.adate >= '$3-$1-$2'";
}

my $to_date = $input->param('search_to');
if($to_date) {
	if ($to_date !~ /^(\d{2})\/(\d{2})\/(\d{4})$/) {errorPageAndExit("Dates must be in the format: \"mm/dd/yyyy\" (Invalid date: '$to_date')", $user, $config);}
	push @search_terms, "a.adate <= '$3-$1-$2'";
}

my $skipto = $input->param('skipto');
if($skipto) {
	errorPageAndExit("Record number must be an integer: \"12345\" (Invalid number: '$skipto')", $user, $config) unless $skipto =~/^[+]?\d+$/;
	$input->delete('skipto');
	}

my $site = $input->param('search_site');

if($site) {
	if ($site =~ /\/$/) {
		push @search_terms, 'u.site LIKE ' . $$config{db}->quote($site . '%');
	}
	else {
		push @search_terms, 'u.site=' . $$config{db}->quote($site);
	}
}

my $where = join " AND ", @search_terms;
$where = ($where ? "WHERE $where" : "");

my @requested_assessments = $input->param('search_assessment_type');
my $request_count = scalar(@requested_assessments);

my @assessments_search;

if ($request_count && $requested_assessments[0] ne '') {
	foreach (@requested_assessments) {
		if($_ eq 'ALL'){
			@assessments_search = @{$$config{common_assessments}};
			last;
			}
		else {
			if ($_ !~ /^\w+$/  && !grep(/$_/,@assessments_search)) {die "Unknown assessment type requested: $_";}
			push @assessments_search, $_;}
			}
	}
else	{
	#@assessments_search = split /\s+/, $config->ggr_adv_tables;
    @assessments_search = 'GHA';
	}


###########################################################
#### Grab the assessments and build the navbar ####
my %vars;
my $sth;
my %navbar;

my $extra_options;
$$extra_options{order_by} = ' ORDER BY last_name, first_name, adate';
$$extra_options{limit} = $MAX_PER_PAGE;
$$extra_options{offset} = ($page - 1) * $MAX_PER_PAGE if(!$skipto);
$$extra_options{offset} = $skipto - 1 if($skipto);
$vars{config} = $config->as_hash();

($vars{assessment_list}) = [$$config{db}->get_assessments
	(\@assessments_search, $where, ['LOWER(a.first_name) AS first_name', 'LOWER(a.last_name) AS last_name', 'adate', 'unum', 'u.hs_uid AS hs_uid'],
	$extra_options)];

if($skipto){
	$page = int(($skipto)/$MAX_PER_PAGE) + 1 || 1;
	++$page if($MAX_PER_PAGE > $skipto && $skipto % $MAX_PER_PAGE);
	}

$navbar{start} = ($page - 1) * $MAX_PER_PAGE + 1;
$navbar{start} = 1 if ($navbar{start} < 1);
$navbar{end} = $navbar{start} + $MAX_PER_PAGE - 1;

my $rows = $$config{db}{sth}->rows();
if ($navbar{end} > $rows) {$navbar{end} = $rows;}

$navbar{url} = $input->self_url();
$navbar{url} =~ s/([\?\;\&])skipto=\d*//g;
$navbar{url} =~ s/([\?\;\&])page\=\d*//g;
if ($navbar{url} !~ /[\&\;\?]$/) {$navbar{url} .= ($navbar{url} =~ /\?/) ? '&' : '?';}

if ($navbar{end} < $navbar{start} + $MAX_PER_PAGE - 1) {$navbar{total} = $navbar{end};}
if ($navbar{end} < $rows) {$navbar{total} = $rows;}
$navbar{page} = $page;

$vars{navbar} = \%navbar;

###########################################################
#### Show the page ####
fill_and_send( $config->template_directory . "admin_assessment_list.tmpl", $user, \%vars, $config->html_use_ssi );
