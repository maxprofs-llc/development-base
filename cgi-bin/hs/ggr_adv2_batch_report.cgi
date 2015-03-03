#!/usr/local/bin/perl
use strict;

use File::Basename        qw( dirname );
use File::Spec::Functions qw( rel2abs );

use lib dirname(rel2abs($0)),'.','/usr/local/www/vhosts/managed2/modules/pdf', '/usr/local/www/vhosts/managed2/modules';

use HTTP::Request;
use HTTP::Cookies;
use LWP::UserAgent;
use Archive::Zip qw( :ERROR_CODES :CONSTANTS );
use Mail::Sendmail;
my  $ua = LWP::UserAgent->new( timeout=> 7200 );
use subs qw( error );

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
my %vars1;
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
	 qw(default send_request);

my $action = lc $input->param('action');
if($action eq '' )
{
     $action = 'default';
}
if(($input->param('use_saved') eq 0)||($input->param('category') eq 0))
{
   if($input->param('use_saved') eq 0)
   {
      $vars1{error_report} = 'Please select a saved report';
   }
   if($input->param('category') eq 0)
   {
      $vars1{error_category} = 'Please select a group';
   }
   $action = 'default';
}
print "Action = $action\n" if $Debug;
unless (exists $Allowed_actions{$action}){
	my $form = $config->template_directory . $config->login_register_retry;
	$hash{error_msg} = "That action is not permitted, please login again.";
	fill_and_send( $form, $user, \%hash, $config->html_use_ssi );
	exit;
	}
	
	
if($action  eq 'default')
{
    chdir ($config->ggr_adv_page_dir . 'saved_reports/');
    my @saved_reports = glob ('*.conf');
    my (%saved_reports_list);
    foreach my $rpt_cfg(@saved_reports)
    {
	my $rpt_config = ConfigReader::Simple->new($rpt_cfg);
	error( "Could not find configuration file $rpt_cfg" ) unless ref $rpt_config;
	my $hd = $rpt_config->get( 'human_desc' );
	$saved_reports_list{$rpt_cfg} = $hd;
    }
    my %config = map { $_, $config->$_ } $config->directives;
    $vars1{config} = \%config;
    $vars1{saved_reports_list} = \%saved_reports_list;
    $vars1{saved_reports_array} = \@saved_reports;
    my @query_results = $db->select_all('hs_category',' where 1 ',1);
    $vars1{category_list} = \@query_results;
    my $hidden = "<input type='hidden' name='action' value='send_request'>";
    $vars1{hidden_values} = $hidden;
    my @ignore_array = ('assessment_list');
    fill_and_send( $config->template_directory . $config->ggr_adv_report_template, $user, \%vars1, $config->html_use_ssi, \@ignore_array);
}

if($action eq 'send_request')
{  
	$| = 1;
	my $url = $config{'html_home'}.$config{'ggr_adv'};
	my $file_param = ConfigReader::Simple->new($config->conf_data_dir.'/saved_reports/'.$hash{'use_saved'});

	my %form;
	my @field_list = $file_param->directives;
	foreach (@field_list){
		if($_ eq 'ggr_sql' || $_ eq 'site_selection'){
			next;
		}
		else {
			$form{$_} = $file_param->$_;
		}
	}
	$form{use_saved} = $hash{'use_saved'};
	$form{hs_ident} = $cook;
  	$form{site_selection_file} = 'healthstatus';
  	
	my $cookie_jar = HTTP::Cookies->new;
	$cookie_jar->set_cookie("hs_ident=".$cook."");
	$ua->cookie_jar($cookie_jar);
	
	my @query_results = $db->select_all('hs_category',' where category_name = "'.$input->param('category').'"',1);
	my ($resp,$content);
	my @values = split(',', $query_results[0]->{groups});
	my %files;

	print $input->header(-type=>'text/html');
	print $input->start_html(-title=>'Advanced Graphic Group Report Batch Processor',
		    -style=>{'src'=> $config->html_base . $config->ggr_adv_styles } );
	print '<p class="maintext-n"><span  class="maintext-b">Batch Reports are being generated, this will take an extended amount of time, please be patient.</span></p>';
	my $wait_flag = 0;
	if( -e $config->conf_data_dir."/healthstatus.log") { 
		$wait_flag=1;
		print '<p class="maintext-n"><span  class="maintext-b">Batch Reports are being run by another user, your request will wait until that job is complete.</span> The system will automatically start your processing as soon as the other job is finished.</p>';
	}
	while( -e $config->conf_data_dir."/healthstatus.log") { sleep 30; print "&nbsp;"; };
	if($wait_flag){print '<p class="maintext-n"><span  class="maintext-b">Your batch is now cleared to process.</span></p>';}		
	print '<p class="maintext-n">Getting the group list and saved parameters. <br>';
	print '<p class="maintext-n">Starting to generate reports<br>';

   foreach my $group (@values)
   {	
	print "<br>&nbsp;<br>generating report for $group";      

	$form{site_selection} = $group;
	$form{ggr2_batch} = $group;     
	my $connector = '=';
	my $close = "'";
	my $temp_id = $config->ggr_adv_group_list_db;
	$temp_id = uc ($temp_id) if( lc($config->db_driver) eq 'oracle' );
	if($group =~ /\/$/){
		$connector = ' LIKE ';
		$close = q|%'|;
		}
	$form{ggr_sql} = 'where ' . $temp_id  . $connector . " '" . $group . $close;
	$resp = $ua->post( $url, \%form );
	local $/ = undef;
	open (MYFILE ,$config->conf_data_dir.'/saved_reports/'.$group.'.log ')or warn "cannot open file ". $config->conf_data_dir.'/saved_reports/'.$group.'.log '. "- error: $! ;; processing group - $group";;
	$files{$group} = <MYFILE>;
	while( -e $config->conf_data_dir.'/saved_reports/'.$input->param('site_selection').'.log ') { sleep 30; print "&nbsp;"; };
	$content .= "<br>&nbsp;<br>Group - ". $group . $resp->content;
	print $content;
   }
   if( -e $config->conf_data_dir."/healthstatus.log")
   {
      open(DAT, $config->conf_data_dir."/healthstatus.log") || die("Could not open file!");
      my @raw_data=<DAT>;
      my $zip = Archive::Zip->new();
      my $toc = "Group\t\t\tFile name\n";
      foreach my $file (@raw_data)
      {
         	chomp $file;
         	my @parts = split(/,/,$file);
         	my $status = $zip->addFile($parts[1]);
         	warn 'write error '.$parts[0]. '  '.$parts[1]. '  '.$status unless $status == AZ_OK;
         	my @fname_parts = split(/\//,$parts[1]);
         	my $part_count=@fname_parts;
         	$toc.= $parts[0]. "\t\t\t".$fname_parts[($part_count-1)]."\n";
      }
      my $status1 = $zip->addString( $toc, '_table_of_contents_.txt' );
	warn 'write error table of contents'.$toc. '  '.$status1 unless $status1 == AZ_OK;
      my $status = $zip->writeToFileNamed($config->conf_htdoc_dir.'/'.$hash{use_saved}.'_'.$hash{category}.'.zip');
	die 'write error final zip '.$config->conf_htdoc_dir.'/'.$hash{use_saved}.'_'.$hash{category}.'.zip'. '  '.$status unless $status == AZ_OK;

   print '<br><hr></p><p class="maintext-n"><span  class="maintext-b">BATCH REPORTING IS COMPLETE!<br>&nbsp;<br>Zip output file is written. ';
   print  "&nbsp;<a href = '".$config->html_home.'/'.$hash{use_saved}.'_'.$hash{category}.'.zip'."'>Click here to download the zip file.</a></span>";
   print "<br>&nbsp;<br>There is a file named '_table_of_contents_.txt' in the zip file that lists the files created and the group that goes with each.</p>";
   print $input->end_html;

   my $message = "BATCH REPORTING IS COMPLETE!\n\nClick the link to download the zip file\n\n".$config->html_home.'/'.$hash{use_saved}.'_'.$hash{category}.'.zip'."\n\nThere is a file named '_table_of_contents_.txt' in the zip file that lists the files created and the group that goes with each.";
   
	my %mail;

	%mail = (       
		To      => $user->db_email,
		From    => $config->email_from,
		Subject => 'Batch Processing of Group Reports is complete',
		Message => $message,
		smtp   => $config->email_smtp
	);
	sendmail(%mail);
	carp("Couldn't send email: $Mail::Sendmail::error")
	if $MAIL::Sendmail::error;

       close DAT;
       unlink($config->conf_data_dir."/healthstatus.log");
   }
}

