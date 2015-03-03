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

carp "back from authenticate";

## common.inc does this for us, don't need it.
my $config_file = "/home/workout/conf/healthstatus.conf";
$config->set( "config_file", $config_file );

carp "open db";
my $db = HealthStatus::Database->new( $config );
$db->debug_on( \*STDERR) if $Debug;
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


carp "actions";
my %Allowed_actions = map { ( $_, 1 ) }
	 qw(create  save list edit update delete);

my $action = lc $input->param('action');
print "Action = $action\n" if $Debug;
carp "unless";
unless (exists $Allowed_actions{$action}){
	my $form = $config->template_directory . $config->login_register_retry;
	$hash{error_msg} = "That action is not permitted, please login again.";
	fill_and_send( $form, $user, \%hash, $config->html_use_ssi );
	exit;
	}
carp "action is $action";

if($action eq 'save')
{
     my $table = 'hs_category';
    my @column = $db->select_one_column('category_name',$table);
 #   print "Content-type:text/html\n\n";
    my $category = $input->param('category');
    if(grep(/^$category$/,@column ) == 1)
    {
      $hash{error_category} = 'Please use a different category name';
      $action = 'create';
    }
   else
   {
      if($input->param('category') eq '' || $input->param('group') eq '')
      {
         $hash{error_category} = 'Please enter category name and also select atleast one group';
         $action = 'create';
      }
      else
      {
         my @tmpData = $input->param;
         foreach my $dataField (@tmpData)
         {
            $hash{$dataField} = join(',', $input->param($dataField));
            print $hash{$dataField}."=>".$dataField;
            print "<BR>";
         }
         my %values=();
         $values{category_name} = $hash{category};
         $values{groups} = $hash{group};
         $db->insert($table,\%values);
         $action = 'list';
      }
   }
}
if($action eq 'create')
{
   my @group_list = $db->reg_group_list('GRPID');
   $hash{group_list} = \@group_list;
   my $form = $config->template_directory . $config->create_category;
   fill_and_send( $form, $user, \%hash , $config->html_use_ssi );
   exit;
}
if($action eq 'update')
{

   if($input->param('category') eq '' || $input->param('group') eq '')
   {
      $hash{error_category} = 'Please enter category name and also select atleast one group';
      $action = 'list';
   }
   my @tmpData = $input->param;

   foreach my $dataField (@tmpData)
   {
      $hash{$dataField} = join(',', $input->param($dataField));
      print $hash{$dataField}."=>".$dataField;
      print "<BR>";
   }

   my $table = 'hs_category';
   my %values=();
    my @column = $db->select_one_column('category_name',$table);
    if(grep(/^$hash{category}$/,@column ) != 1)
    {
      $values{category_name} = $hash{category};
      $values{groups} = $hash{group};
      my $stipulations = 'where category_name = "'.$hash{category}.'"';
      $db->update($table,\%values,$stipulations);
      $action = 'list';
    }
    else
    {
      $action = 'edit';
      $input->param('gid') = $hash{category};
    }

}
if($action eq 'delete')
{
   my $table = 'hs_category';
   my $stipulations = 'where category_name = "'.$hash{gid}.'"';
   $db->delete($table,$stipulations);
   $action = 'list';
}
if($action eq 'list')
{
   my $table = 'hs_category';
   my $stipulation = 'where 1 ';
   my @query_results = $db->select_all($table,$stipulation,1);
   $hash{group_list} = \@query_results;
   my $form = $config->template_directory . $config->category_listing;
    fill_and_send( $form, $user, \%hash , $config->html_use_ssi );
    exit;
}
if($action eq 'edit')
{
   my $table = 'hs_category';
   my $stipulation = 'where  category_name = "'.$input->param('gid').'"';
   my $query_results = $db->select_one_row('groups',$table,$stipulation);
   my @query_results = split(',',$query_results->[0]);
    my @group_list = $db->reg_group_list('GRPID');
    $hash{group_list} = \@group_list;
   $hash{gid} = $input->param('gid');
   $hash{group_selected_list} =\@query_results;
   my $form = $config->template_directory . $config->edit_category;
    fill_and_send( $form, $user, \%hash , $config->html_use_ssi );
    exit;
}
