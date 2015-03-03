#!/usr/local/bin/perl
use strict;

=head1 Name
create_category.pl-groups a certain number of  groups under each category

*********** NOTES *************************
fix to use user elements not hardcoded field names
then use hs database functions to read/write/update

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

use CGI qw(-no_xhtml -debug);
use CGI::Carp qw(fatalsToBrowser);
use File::Basename;
use HealthStatus qw( fill_and_send error html_error );
use HealthStatus::Authenticate;
use HealthStatus::Config;
use HealthStatus::Constants;
use HealthStatus::Database;

my $input = new CGI();
my $config = getConfig($input->param('extracfg'));

my %hash = map { $_, $input->param($_) } $input->param();

my %config = map { $_, $config->$_ } $config->directives;

$hash{config} = \%config;
my @good_extensions = ('gif','jpg','png');
my $upload_logo_dir = $config->conf_htdoc_dir."/groups/logo"; 
my $upload_css_dir  = $config->conf_htdoc_dir."/groups/css"; 
my %input = $input->Vars();

############################################################################
### Comment out the following line before going into production ############
$Debug = $input->param("HS_Debug") || $ENV{HS_DEBUG} || 0;
#### only uncomment if you need to debug the input scripts      ############
############################################################################

$cook = $input->cookie('hs_ident') || $input->param('hs_ident');

# authenticate_user redirects the user if they not allowed to
# view this page
my $user = authenticateUser(["admin"], $input, $config) or die "You should never see this message.";

my $db = HealthStatus::Database->new( $config );
$db->debug_on( \*STDERR) if $Debug;

my %tables = %{$db->all_table_names};
my %name_hash = %{$db->assessment_user_to_db('GRP')};

# place the db_handle into the config for passing to other routines.
$config->set( "db_handle", $db );
if ($Debug) {
	print "Content-type: text/plain\n\n";
	$config->pretty_print if $Debug;
	my %config_dump = map { $_, $config->$_ } $config->directives;
	foreach my $t_key (sort keys %config_dump)
		{
		print "$t_key = " . $config_dump{$t_key} . "\n";
		}
	print " *********  HS_IDENT Cookies or param ************************\n";
	print "This is what I see in the cookie hs_ident - ". $input->cookie('hs_ident')  . "\n" ;
	print "This is what I see in the parameter hs_ident - ". $input->param('hs_ident')  . "\n" ;
	print " **************************************************************\n";
	$user->pretty_print;
}

my %Allowed_actions = map { ( $_, 1 ) }
	 qw(create  save list edit update delete);

my $action = lc $input->param('action');
print "Action = $action\n" if $Debug;
unless (exists $Allowed_actions{$action}){
	print $input->redirect( -uri=> $config->admin_path );
	exit;
	}
my %assessment_names = ( 
			
			 GHA	=> 'Health Risk assessment',
			 CRC	=> 'Cardiac Risk assessment',
			 DRC	=> 'Diabetes Risk assessment',
			 FIT	=> 'Fitness assessment',
			);

my @assessments_allowed = split /\s+/, $config->show_order;

my %assessments_allowed_hash;
foreach (@assessments_allowed){
	$assessments_allowed_hash{$_} = $assessment_names{$_};
}

#create or update the groups
if(($action eq 'create'  && $input->param('create') eq 'Create Group') || ($action eq 'update' && $input{update} eq 'Update Group')) {
	my (%values);
	if($input->param('groupID') eq '' ) {
         create_group("Please enter group ID.");
    }
    if($input->param('groupName') eq '' ) {
         create_group("Please enter group name.");
    }
    if($input->param('groupRestrict') eq '' ) {
         create_group("Please select any assessment(s) name.");
    }	
	if( $input->param('numberSubgroups') > 0 &&  $input->param('subgroupNames') eq '') {
         create_group("Please enter subgroup name.");
	} 
	if( $input->param('subgroupNames') ne '') {
		my @subgroups = split(',',join(',', $input->param('subgroupNames')));
		foreach my $name(@subgroups) {
			if($name =~ m/\W/ ){
				create_group("Invalid subgroup name: $name. Only alphanumeric characters are allowed. ");
			}
		}
	}
	 my %hash = %{$name_hash{'db'}} ; 
	 foreach my $dataField (keys %hash) {
		if($input->param($dataField) eq 'No limit'){
					 my $desired_field =  $config->show_order;
					 $desired_field =~ s/\s+/\,/g;	
					 $values{$dataField} = $desired_field;					 					 
			}else{						 
		            $values{$dataField} = join(',', $input->param($dataField));
		   }
	 }
	if($action eq 'create'  && $input->param('create')) {
		my $stipulations = "where groupID='".$input->param('groupID')."'";
		#carp $stipulations;
		my	$number_of_rows  =  $db->count( $tables{GRP}, $stipulations );
		if($number_of_rows) {
			create_group("Please enter another Group Id. ".$input->param('groupID')." already exists.");
		} else {
			 $db->insert($tables{GRP},\%values);
		}
	} 
	my $filename_logo = $input->param("groupLogo"); 
		# upload the logo starts
		if ($filename_logo) {  
			##### check the extension
			my @ext = split(/\./, $filename_logo);
			my $extension = lc($ext[$#ext]);
			my $valid_extension;
			foreach (@good_extensions) {
				if ($extension eq $_) {
					$valid_extension = 1;
					last;
				}
			}
			if(!$valid_extension){
				create_group("$filename_logo: Invalid File Type");
			}
			my $upload_filehandle = $input->upload("groupLogo"); 
			my $new_filename= $input->param("groupID").".".$extension ;
			do_upload($new_filename,$upload_filehandle,$upload_logo_dir);
		}  
		my $filename_css = $input->param("groupCSS");  
		# upload the css starts
		if ($filename_css) {  
			my @ext = split(/\./, $filename_css);
			my $extension = lc($ext[$#ext]);
			if ($extension ne 'css') {
				create_group("$filename_css: Invalid File Type");
			}
			
			my $upload_filehandle = $input->upload("groupCSS"); 
			my $new_filename= $input->param("groupID").".".$extension ;
			do_upload($new_filename,$upload_filehandle,$upload_css_dir);
		}
		
		if($action eq 'update' && $input{update} eq 'Update Group') {	
			if (change_group($input{groupID}, \%input)) {$hash{display_message} = "Group $input{groupID} has been modified.";}
			fill_and_send( $config->template_directory . "admin_group_message.tmpl", $user, \%hash, $config->html_use_ssi );
		} else {
			$hash{display_message} = "Group has been created successfully.";
			fill_and_send( $config->template_directory . "admin_group_message.tmpl", $user, \%hash, $config->html_use_ssi );
		}
		exit;
}
if($action eq 'create') {
	create_group() ;
}

sub create_group() {
	my $error = shift;
	$hash{display_message} 	= $error;
	$hash{form_action} 		= "create_groups.cgi";
	$hash{assessments_allowed_hash}		= \%assessments_allowed_hash;
   my $form = $config->template_directory . $config->group_create;
   fill_and_send( $form, $user, \%hash , $config->html_use_ssi );
   exit;
}
sub do_upload(){
	my $filename 			= shift ;
	my $upload_filehandle 	= shift ;  
	my $upload_dir 			= shift ;  
	open ( UPLOADFILE, ">$upload_dir/$filename" ) or die "$!";  
	binmode UPLOADFILE;  
	 
	while ( <$upload_filehandle> )  
	{  
	 print UPLOADFILE;  
	}  
	 
	close UPLOADFILE;
}
sub change_group {
	my ($groupID, $hash_in) = @_;
	my %hash = %$hash_in;
	$hash{subgroupDescriptions} = join(',', $input->param('subgroupDescriptions'));
	$hash{subgroupNames} = join(',', $input->param('subgroupNames'));
	if($input->param('groupRestrict') eq 'No limit' || $input->param('groupRestrict') eq ''){
	 my $desired_field =  $config->show_order;
	 $desired_field =~ s/\s+/\,/g;	
	 $hash{groupRestrict} = $desired_field;		
	}else{
	 $hash{groupRestrict} = join(',', $input->param('groupRestrict'));
	}
	$hash{groupLogo} 	= $input->param('logo_uploaded') if(!$input->param('groupLogo'));
	$hash{groupCSS} 	= $input->param('css_uploaded') if(!$input->param('groupCSS'));
	
	$db->update($HealthStatus::Database::Tables{GRP}, {groupName => $hash{groupName}, groupDescription => $hash{groupDescription}, groupLaunch=> $hash{groupLaunch}, groupPhone => $hash{groupPhone}, groupSignature => $hash{groupSignature}, groupLogo=> $hash{groupLogo}, groupCSS => $hash{groupCSS}, groupStatus => $hash{groupStatus}, groupRestrict=> $hash{groupRestrict}, groupResetDate => $hash{groupResetDate}, groupAdminEmail=> $hash{groupAdminEmail}, subgroupNames=> $hash{subgroupNames}, subgroupDescriptions=> $hash{subgroupDescriptions}}, " WHERE groupID='$groupID'");
	return 1;
}