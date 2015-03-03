#!/usr/local/bin/perl
use strict;

=head1 NAME

admin_group_modify.cgi - Provides group administration features.

=head1 DESCRIPTION

This script provides the basic functions of modifying group records

=head1 INPUT

This script depends on certain control parameters to tell it what to
do.

	action -  update
	
	groupID - ID of group to modify or update
	

=head2 OUTPUT

The script loads a template file with C<Text::Template> and fills in
the template.  

=head1 ERRORS

This script will issue an error if it cannot read the
configuration or template file.  A short, vague message
is sent to the browser and a more detailed message should
show up in the error log.

If the script cannot recognize the value of the control parameter
C<action> it outputs
an error page.

=cut

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


use HealthStatus qw( fill_and_send error html_error );
use HealthStatus::Authenticate;
use HealthStatus::Config;
use HealthStatus::Constants;
use HealthStatus::Database;
use HealthStatus::User;

use CGI::Carp;
my $input = new CGI();
my $config = getConfig($input->param('extracfg'));

my %input = $input->Vars();  # Hash containing query inputs
my $groups_shown = 50;

$cook = $input->cookie('hs_ident') || $input->param('hs_ident');

############################################################################
$Debug = ($input->param("HS_Debug") || $ENV{HS_DEBUG} || 0) && !$config->production;
############################################################################

if( $Debug ) {
	print "Content-type: text/plain\n\n" if $Debug;

	print "$ENV{SCRIPT_NAME} - $ENV{QUERY_STRING}\n";
	print "Modules Versions:\nHealthStatus - $HealthStatus::VERSION\nHealthStatus::Authenticate - $HealthStatus::Authenticate::VERSION\nHealthStatus::Database - $HealthStatus::Database::VERSION\n";
	print "HealthStatus::Config - $HealthStatus::Config::VERSION\nHealthStatus::User - $HealthStatus::User::VERSION\n\n";
	foreach my $key ( sort keys %input ) {print "\t$key\t\t$input{$key}\n";}
	print "my cookie = $cook\ncookie - " . $input->cookie('hs_ident') . "\nparam - " . $input->param('hs_ident') . "\n";
	$config->pretty_print if $Debug;
}

my $user = authenticateUser(["admin"], $input, $config) or die "You should never see this message.";

if( $config->authenticate_admin == 1 ) {
	if( $user->hs_administration ne 'admin' ){
		error( "You are not authorized to run this program" );
		exit 1;
	}
}

my $db = HealthStatus::Database->new( $config );
my %vars = ();

$vars{'input'} = \%input;

#######################################################
## Form Processing
#######################################################
my $action = $input{action};

if ($action eq 'update') {
	show_group();
} else {
	fill_and_send( $config->template_directory . "admin_group_modify.tmpl", $user, \%vars, $config->html_use_ssi);
	exit;
}


sub show_group {
	my $error = shift;
	my ($grp) = $input{'groupID'};
	$grp =~ s/'/\\'/;
	my(%assessments_allowed_hash, %restrict_hash, @restrict_array, @assessments_allowed, %assessment_names, @ignore_array, @names_array, @desc_array, @logo_array);
	my $stipulation = " WHERE groupID='$grp'";
	my $query_results = $db->select_one_row('*', $HealthStatus::Database::Tables{GRP}, $stipulation, 1);	

	# If group id not exists then display a error message 
	if(!defined $query_results) {
		$vars{display_message}	= "Group Id not found.";
		fill_and_send( $config->template_directory . "admin_group_modify.tmpl", $user, \%vars, $config->html_use_ssi);
	}
	my %vars = %{$query_results};
	
	@ignore_array = ('subgroupNames','subgroupDescriptions','groupRestrict');
	%assessment_names = ( 
			
			 GHA	=> 'Health Risk assesment',
			 CRC	=> 'Cardiac Risk assesment',
			 DRC	=> 'Diabetes Risk assesment',
			 FIT	=> 'Fitness assesment'
			 );

	@assessments_allowed = split /\s+/, $config->show_order;
	foreach (@assessments_allowed){
		$assessments_allowed_hash{$_} = $assessment_names{$_};
	}
	@restrict_array = split(',',$vars{groupRestrict});
	foreach(@restrict_array) {
		$restrict_hash{$_} = 1;
	}
	@names_array 						= split(',',$vars{subgroupNames});
	@desc_array 						= split(',',$vars{subgroupDescriptions});
	$vars{assessments_allowed_hash}		= \%assessments_allowed_hash;
	@logo_array							= split('\.',$vars{groupLogo});	
	$vars{restrict_hash}				= \%restrict_hash;
	$vars{random}				 		= time();
	$vars{form_action} 					= "create_groups.cgi";
	$vars{display_message}				= $error;
	$vars{logo_name}					= $vars{groupID}.".".$logo_array[1];
	$vars{names_array}					= \@names_array;
	$vars{desc_array}					= \@desc_array;
	$vars{logo_uploaded}				= $vars{groupLogo};
	$vars{css_uploaded}					= $vars{groupCSS};
	
	fill_and_send( $config->template_directory . "group_create.tmpl", $user, \%vars, $config->html_use_ssi, \@ignore_array);
	exit;
}



