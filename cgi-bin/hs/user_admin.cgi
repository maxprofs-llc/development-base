#!/usr/local/bin/perl
use strict;

=head1 NAME

user_admin.cgi - Provides user administration features.

=head1 DESCRIPTION

This script provides the basic functions of deleting users
and changing a user's rank.

=head1 INPUT

This script depends on certain control parameters to tell it what to
do.

	action - delete delete_group change_rank

	userid - ID of user that will be deleted/changed

	group - ID of group to delete

	confirm - Deletion functions have a confirmation stage.  This param will
		be set to 1 if the deletion has been confirmed.


=head2 OUTPUT

The script loads a template file with C<Text::Template> and fills in
the template.  The result is a <form> offering basic user functions,
plus a quick results string if the form has already been submitted
and processed (E.g: "User X was successfully deleted")

=head1 ERRORS

This script will issue an error if it cannot read the
configuration or template file.  A short, vague message
is sent to the browser and a more detailed message should
show up in the error log.

If the script cannot recognize the value of the control parameter
C<action> it outputs
an error page.

=cut

use CGI::Carp;
use File::Basename        qw( dirname );
use File::Spec::Functions qw( rel2abs );

use lib dirname(rel2abs($0)),'.','/usr/local/www/vhosts/managed2/modules/pdf', '/usr/local/www/vhosts/managed2/modules';

use vars qw( $Debug $production $cook $config_file $nph %Allowed_assessments %field_info);

if (!do('common.inc')) {
   my $error = $@ ? $@
             : $! ? $!
             : 'did not return a true value';
   die("Unable to load common stuff: $error\n");
}
# Removing warnings in log while module is being used with CGI version 4 or above
$CGI::LIST_CONTEXT_WARN = 0;

use HealthStatus qw ( error html_error fill_and_send );
use CGI::Carp;

my $input = new CGI();
my $config = getConfig($input->param('extracfg'));
if (!do($config->conf_config_dir.'/healthstatus_db.conf')) {
   my $error = $@ ? $@
             : $! ? $!
             : 'did not return a true value';
   die("Unable to load ".$config->conf_config_dir."/healthstatus_db.conf: $error\n");
}

if (!do($config->conf_config_dir.'/db_hs.conf')) {
   my $error = $@ ? $@
             : $! ? $!
             : 'did not return a true value';
   die("Unable to load ".$config->conf_config_dir."/db_hs.conf: $error\n");
}


my $session = new CGI::Session(undef, undef, {Directory=>'../../sessions'}) or die CGI::Session->errstr;
$session->save_param();

my %hash = map { $_, $input->param($_) } $input->param();

my %config = map { $_, $config->$_ } $config->directives;

$hash{config} = \%config;

my %input = $input->Vars();

$cook = $session->param('hs_ident') || $input->param('hs_ident') || $input->cookie('hs_ident');
$session->param('hs_ident',$cook);
$session->load_param($input);

my $users_shown = 500;

############################################################################
$Debug = ($input->param("HS_Debug") || $ENV{HS_DEBUG} || 0) && !$config->production;
############################################################################

if( $Debug ) {
	print "Content-type: text/plain\n\n";
	print "$ENV{SCRIPT_NAME} - $ENV{QUERY_STRING}\n";
	print "Modules Versions:\nHealthStatus - $HealthStatus::VERSION\nHealthStatus::Authenticate - $HealthStatus::Authenticate::VERSION\nHealthStatus::Database - $HealthStatus::Database::VERSION\n";
	print "HealthStatus::Config - $HealthStatus::Config::VERSION\nHealthStatus::User - $HealthStatus::User::VERSION\n\n";
	foreach my $key ( sort keys %input ) {print "\t$key\t\t$input{$key}\n";}
	print "my cookie = $cook\ncookie - " . $input->cookie('hs_ident') . "\nparam - " . $input->param('hs_ident') . "\n";
	$config->pretty_print if $Debug;
}

my $user = authenticateUser(["admin"], $input, $config) or die "You should never see this message.";
#my $user = login ( $config, \%input, $input);

if( $config->authenticate_admin == 1 ) {
	if( $user->hs_administration ne 'admin' ){
		error( "You are not authorized to run this program" );
		exit 1;
	}
}
my $db = HealthStatus::Database->new( $config );
my %vars = ();

# %Allowed_assessments not only tells us which assessments we
# can do, but how many pages of input to expect
%Allowed_assessments = map
	{
	my $assessment = lc $_;
	my $method     = lc $_."_max_pages";
	my $max_pages  = $config->$method;

	( $assessment, $max_pages )
	} @{$$config{common_assessments}};


#######################################################
## Form Processing
#######################################################
my $action = $input{action};
my @batch= $input->param('checkbox_batch');

if ($action eq 'usertype') {
	my $flag=0;
	foreach my $entry (@batch)
	{
		change_user($entry, $input{new_type});
		$flag=1;
	}
	if ($flag){$vars{display_message} = "User type has been changed.";}
}
elsif ($action eq 'delete') {
	my $flag=0;
	my $count=0;
    foreach my $entry (@batch)
    {
		delete_user($entry);
		$flag=1;
		$count++;
	}
	if ($flag){
		if ($count>1){$vars{display_message} = "Users have been deleted.  A backup has been stored on the server.";}
		else{$vars{display_message} = "User has been deleted.  A backup has been stored on the server.";}
	}
}
elsif ($action eq 'delete_group') {
	my $tmp = delete_group($input{dgroup});
	if ($tmp) {
		$vars{display_message} = "Group has been deleted.  A backup has been stored on the server.  Deleted user ids: (" .
			join(',', @$tmp) . ')';
	}
}
elsif ($action eq 'Search User') {
	$vars{search_result} = search_user();
	fill_and_send( $config->template_directory . "admin_user_list.tmpl", $user, \%vars, $config->html_use_ssi );
	exit;
}
elsif ($action eq 'Edit User') {
    $vars{edit_result} = edit_user($input{pf});
	$vars{field_info} = \%field_info;
	fill_and_send( $config->template_directory . "edit_user.tmpl", $user, \%vars, $config->html_use_ssi );
    exit;
}
elsif ($input{submit} eq 'Edit Profile') {
	my $result = edit_user_details();
	if ($result){
		$vars{display_message} = "User has been edited.";
	}
	else{
		$vars{display_message} = "Unable to edit User. Please try again.";
	}
	fill_and_send( $config->template_directory . "edit_user.tmpl", $user, \%vars, $config->html_use_ssi );
	exit;

}

sub edit_user_details()
{
	if ($input{unum})
	{
		my $stipulation;
		my %values;
		foreach my $fields (sort keys %input)
		{
			next if $fields eq 'submit';
			$values{$fields} = $input{$fields};
		}
		
		$stipulation = "WHERE unum=$input{unum}";
	 	$db->update( $HealthStatus::Database::Tables{REG}, \%values, $stipulation);	
		return 1;
	}
	return 0;
}
sub edit_user()
{
	my $unum = shift;
	my $stipulation = "WHERE unum=$unum";
	my @result = $db->select_all( [$HealthStatus::Database::Tables{REG}], $stipulation, 1);
	return (\@result);	
}
sub search_user()
{
	my $name = $input->param('partial_name');
	my $email = $input->param('partial_email');
	my $user_group = $input->param('type');
	my $login_id = $input->param('login_id');
	my @search_fields = ("full_name", "email", "rank", "hs_uid");

    my $stipulation = '';
	my $found = 0;
	
	foreach my $field (@search_fields)
	{
		$found = 0;

		if ($field eq "full_name" && $name )
		{
			$stipulation .= " AND  " if ($stipulation);
			$stipulation .= " $field LIKE " . $db->quote('%' . $name . '%');
			$found = 1;
		}
		if ($field eq "email" && $email )
		{
			$stipulation .= " AND  " if ($stipulation);
			$stipulation .= " $field LIKE " . $db->quote('%' . $email . '%');
			$found = 1;
        }
        if ($field eq "rank" && $user_group)
		{
			$stipulation .= " AND  " if ($stipulation);
			$stipulation .= " $field LIKE " . $db->quote('%' . $user_group . '%');
			$found = 1;
		}
		if ($field eq "hs_uid" && $login_id )
		{
			$stipulation .= " AND  " if ($stipulation);
			$stipulation .= " $field LIKE " . $db->quote('%' . $login_id . '%');
			$found = 1;
		}
	}
	$stipulation = " WHERE " . $stipulation if ($stipulation);
	$stipulation .= " ORDER BY full_name";

    my @result =$db->select(['unum', 'full_name', 'hs_uid', 'rank', 'email'], [$HealthStatus::Database::Tables{REG}],$stipulation, 1);
	return (\@result);
}

sub backup_user {
	my ($unum) = @_;
	my $backup_txt = '';
	my $tname;
	my @tables;

	foreach my $table_key (keys %HealthStatus::Database::Tables) {
		# If this is a table that is tied to a user...
		if (($table_key eq 'REG' || $table_key eq 'PASS') || (exists ($Allowed_assessments{$table_key}) && exists($HealthStatus::Database::Fields{$table_key}{unum})) ) {
			$tname = $HealthStatus::Database::Tables{$table_key};
			push @tables, $tname;
			my @backup = $db->select_all([$tname], " WHERE unum=$unum", 1);

			foreach(@backup) {
				$backup_txt .= "\nINSERT INTO $tname(" . join(",", keys %$_) . ") VALUES (";

				my $first = 1;
				foreach(values %$_) {
					$backup_txt .= "," if !$first;
					$first = 0;
					$backup_txt .= $db->{db}->quote($_);
				}

				$backup_txt .= ");";
			}
		}
	}

	open (FH, ">" . $config->backup_directory . "user_${unum}_backup.sql")
				or ($vars{display_message} = "Could not open backup file" && return 0);
	print FH $backup_txt;
	close FH;
	return \@tables;
}

sub change_user {
	my ($unum, $new_type) = @_;
	if ($unum == $user->db_number) {
		$vars{display_message} = "You may not edit yourself.";
		return 0;
	}
	#my $change_user = new HealthStatus::User({hs_ident => $unum});
	$db->update($HealthStatus::Database::Tables{REG}, {rank => $new_type}, " WHERE unum=\'$unum\'");
	return 1;
}

sub delete_group {
	my ($grp) = @_;
	my $user_list = [];
	$vars{display_message} = "Deleting groups not yet supported.";
	$grp =~ s/'/\\'/;
	my @ulist = $db->select(['unum'], [$HealthStatus::Database::Tables{REG}], " WHERE grpID LIKE '$grp%'");
	foreach(@ulist) {
		if (!delete_user($$_[0])) {
			$vars{display_message} = "An error occurred removing the group.  Some users may not have been removed.  A backup has been made of all removed users.";
			return 0;
		}
		push @$user_list, $$_[0];
	}

	return $user_list;
}

sub delete_user {
	my ($unum) = @_;

	if ($unum == $user->db_number) {
		$vars{display_message} = "You may not delete yourself.";
		return 0;
	}

	my $tables = backup_user($unum);

	if ($tables) {
		foreach(@$tables) {$db->delete($_, " WHERE unum=$unum");}
		return 1;
	}

	return 0;
}

#######################################################
## Form Display
#######################################################

sub getGroupHash {
	my @glist = $db->select(['grpID'], [$HealthStatus::Database::Tables{REG}], " ORDER BY grpID ");

	# Each group will be split into its components.  @group_path will hold
	# those components in order.  E.g "bodybuilder/male" will be stored
	# as ["bodybuilder", "male"]
	my @group_path;

	# A "pointer" to the current group level.
	my $gptr;

	# A hash of hashes (of hashes?) that stores the list of groups and subgroups.
	# Each key is a group name, and each value is a hash containing subgroups
	# (which can in turn contain subgroups, ad infinitum).
	my %groups;

	foreach(@glist) {
		@group_path = split '/', $$_[0];
		$gptr = \%groups;

		foreach(@group_path) {
			# Check if the current group already exists in the group array.  If it doesn't,
			# add it as an empty hash.
			$gptr = (exists $$gptr{$_} ? $$gptr{$_} : ($$gptr{$_} = {}));
		}
	}

	return \%groups;
}

sub getUserList {
	my $name = $input->param('partial_name');
	my $email = $input->param('partial_email');

	my $where = '';

	if($name) {$where .= " full_name LIKE " . $db->quote($name . '%');}
	if($email) {$where .= ($where ? ' AND ' : '') . " email LIKE " . $db->quote($email . '%');}

	return $db->select(['unum', 'full_name', 'hs_uid', 'rank'], [$HealthStatus::Database::Tables{REG}],
		($where ? " WHERE $where " : '') . " ORDER BY full_name", undef, $users_shown);
}

sub getGroupOptions {
	my ($g, $to_return, $prefix, $text_prefix) = @_;
	my $str;
	if (!defined $to_return) {$to_return = []; $text_prefix = "";}
	else {$prefix = "$prefix/";}

	foreach(keys %$g) {
		$str = "$prefix$_";
		push @$to_return, [$str,"$text_prefix$str"];
		getGroupOptions($$g{$_}, $to_return, $str, $text_prefix . "   ");
	}

	return $to_return;
}


my @ulist = getUserList();

#my @glist = $db->select(['grpID'], [$HealthStatus::Database::Tables{REG}], " ORDER BY grpID ");
#my $glist = getGroupOptions(getGroupHash());

foreach (@ulist) {if (!defined($$_[1]) || $$_[1] eq '') {$$_[1] = "[User $$_[0]]";}}
foreach (@ulist) {$$_[1] = ($$_[1] || $$_[2]) . " ($$_[3])";}

my %config = map { $_, $config->$_ } $config->directives;
$vars{config} = \%config;
$vars{user_list} = \@ulist;
#$vars{group_list} = $glist;
$vars{suser} = 1;
$vars{new_options} = 1;
$vars{partial_name} = $input->param('partial_name');
$vars{partial_email} = $input->param('partial_email');
$vars{users_shown} = $users_shown;

fill_and_send( $config->template_directory . "admin_user_functions_new.tmpl", $user, \%vars, $config->html_use_ssi );
