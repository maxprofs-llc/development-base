#!/usr/local/bin/perl
use strict;
use File::Basename        qw( dirname );
use File::Spec::Functions qw( rel2abs );

use lib dirname(rel2abs($0)),'.','/usr/local/www/vhosts/managed2/modules/pdf', '/usr/local/www/vhosts/managed2/modules';

use vars qw( $Debug $production $cook $config_file);

if (!do('common.inc')) {
   my $error = $@ ? $@
             : $! ? $!
             : 'did not return a true value';
   die("Unable to load common stuff: $error\n");
}

use CGI::Carp;
use CGI::Carp qw(fatalsToBrowser);
use HealthStatus qw( fill_and_send error html_error );
use HealthStatus::Config;

my $config = getConfig();
my $input = new CGI();

my $MAX_PER_PAGE = 20;
my $page = ($input->param('page') || 1);

# authenticate_user redirects the user if ey is not allowed to
# view this page
my $user = authenticateUser(['admin','coach'], $input, $config) or die "You should never see this message.";
$config->template_directory . $config->login_failed;

###########################################################
#### Create WHERE clause and perform assessment search ####
my @search_terms;

my @assessments_search = ( $HealthStatus::Database::Tables{GRP} );
my @fields = qw( groupID groupName groupStatus groupLaunch groupDescription groupPhone groupAdminEmail);

my $skipto = $input->param('skipto');
if($skipto) {
	errorPageAndExit("Record number must be an integer: \"12345\" (Invalid number: '$skipto')", $user, $config) unless $skipto =~/^[+]?\d+$/;
	$input->delete('skipto');
	}
###########################################################
#### Grab the assessments and build the navbar ####
my %vars;
my $sth;
my %navbar;

my $extra_options;
$$extra_options{order_by} = ' ORDER BY groupID';
$$extra_options{limit} = $MAX_PER_PAGE;
$$extra_options{offset} = ($page - 1) * $MAX_PER_PAGE if(!$skipto);
$$extra_options{offset} = $skipto - 1 if($skipto);
$$extra_options{lo_string} = ' LIMIT '. $$extra_options{offset} .', '.$$extra_options{limit};
$vars{config} = $config->as_hash();


($vars{assessment_list}) = [$$config{db}->select 
	( \@fields , \@assessments_search, $$extra_options{order_by}.$$extra_options{lo_string}, 1 ) ];

if($skipto){ 
	$page = int(($skipto)/$MAX_PER_PAGE) + 1 || 1;
	++$page if($MAX_PER_PAGE > $skipto && $skipto % $MAX_PER_PAGE);
	}

$navbar{start} = ($page - 1) * $MAX_PER_PAGE + 1;
$navbar{start} = 1 if ($navbar{start} < 1);
$navbar{end} = $navbar{start} + $MAX_PER_PAGE - 1;

#my $rows = $$config{db}{sth}->rows();
#if ($navbar{end} > $rows) {$navbar{end} = $rows;}

$navbar{url} = $input->self_url();
$navbar{url} =~ s/([\?\;\&])skipto=\d*//g;
$navbar{url} =~ s/([\?\;\&])page\=\d*//g;
if ($navbar{url} !~ /[\&\;\?]$/) {$navbar{url} .= ($navbar{url} =~ /\?/) ? '&' : '?';}

if ($navbar{end} < $navbar{start} + $MAX_PER_PAGE - 1) {$navbar{total} = $navbar{end};}
#if ($navbar{end} < $rows) {$navbar{total} = $rows;}
$navbar{page} = $page;

$vars{navbar} = \%navbar;

###########################################################
#### Show the page ####
fill_and_send( $config->template_directory . "admin_group_list.tmpl", $user, \%vars, $config->html_use_ssi );
