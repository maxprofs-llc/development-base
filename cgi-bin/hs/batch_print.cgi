#!/usr/local/bin/perl
use strict;

use File::Basename        qw( dirname );
use File::Spec::Functions qw( rel2abs );

use lib dirname(rel2abs($0)),'.','/usr/local/www/vhosts/managed2/modules/pdf', '/usr/local/www/vhosts/managed2/modules';

use vars qw( $Debug $production $config_file $cook $nph);

if (!do('common.inc')) {
   my $error = $@ ? $@
             : $! ? $!
             : 'did not return a true value';
   die("Unable to load common stuff: $error\n");
}

$| = 1;
############################################################################
### Change the following line before going into production      ############
$production = 1;
#### 1 = production server, 0 = setup/test server               ############
############################################################################

use CGI qw(-no_xhtml -debug);
if (!$production) {
	use CGI::Carp qw(fatalsToBrowser);
	}
else {
	use CGI::Carp;
	}
$CGI::POST_MAX=1024 * 100;  # max 100K posts
$CGI::DISABLE_UPLOADS = 1;  # no uploads
use Date::Calc;
use Archive::Zip qw( :ERROR_CODES :CONSTANTS );

use HealthStatus qw( fill_and_send error html_error );
use HealthStatus::Authenticate;
use HealthStatus::CalcRisk;
use HealthStatus::Config;
use HealthStatus::Constants;
use HealthStatus::Database;
use HealthStatus::User;
use Text::Template;

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
my %hash1 = $input->Vars();
my %hash;
my %vars;
my $batch_user;
my $operating_system = $^O;
my @to_print_list;
my @to_process_list;
my @been_printed_list;

my( $year, $month, $day, $hour, $min, $sec ) = (localtime)[5,4,3,2,1,0];
$year  += 1900;
$month += 1;

my $date = sprintf("As of %02d/%02d/%04d", $month, $day, $year);
my $date_stamp = sprintf("%02d-%02d-%04d-%02d-%02d-%02d", $month, $day, $year, $hour, $min, $sec);
my $tight_date = sprintf("%04d%02d%02d%02d%02d%02d", $year, $month, $day, $hour, $min, $sec);

############################################################################
### Comment out the following line before going into production ############
$Debug = $input->param("HS_Debug") || $ENV{HS_DEBUG} || 0;
#### only uncomment if you need to debug the input scripts      ############
############################################################################


my @batch_assessments = @{$$config{batch_assessments}};
my @assessments = @{$$config{common_assessments}};

if ($Debug) {
	print "Content-type: text/plain\n\n";

	print "$ENV{SCRIPT_NAME} - $ENV{QUERY_STRING}\n";
	print "Modules Versions:\nHealthStatus - $HealthStatus::VERSION\nHealthStatus::Authenticate - $HealthStatus::Authenticate::VERSION\nHealthStatus::Database - $HealthStatus::Database::VERSION\n";
	print "HealthStatus::Config - $HealthStatus::Config::VERSION\nHealthStatus::User - $HealthStatus::User::VERSION\n\n";
	foreach my $key ( sort keys %hash )
		{
		print "\t$key\t\t$hash{$key}\n";
		}
	$config->pretty_print;
	print " *********  HS_IDENT Cookies or param ************************\n";
	print "This is what I see in the cookie hs_ident - ". $input->cookie('hs_ident')  . "\n" ;
	print "This is what I see in the parameter hs_ident - ". $input->param('hs_ident')  . "\n" ;
	print " **************************************************************\n";
	}

if ($input->param('report_config') || $config->ggr_adv_conf){
	my $report_cfg = $input->param('report_config') || $config->ggr_adv_conf;
	$config->add_config_file( $report_cfg );
	}

my %config = map { $_, $config->$_ } $config->directives;

my $user = authenticateUser('all', $input, $config) or exit();

$user->pretty_print if $Debug;

my  $data;
# users aren't allowed to enter batch forms so just return them to the assessment recs page.
if($user->hs_administration eq 'user') {
	my $tnum = $user->db_number;
	my $expire_time = $config->session_timeout;
	my $cookie=$input->cookie(-name=>'hs_ident', -value=>"$tnum", -expires=> "+{$expire_time}m");
	print $input->redirect( -cookie=>$cookie, -uri=> $config->member_page );
	exit;
	}

if($input->param('submit_batch') eq "submit"){
	my @batch= $input->param('checkbox_batch');
	my @check_this = split(/-/, $batch[0]);
	my $pretty_batch = "b" . $check_this[4] . $check_this[2] . $check_this[3] . $check_this[5] . $check_this[6] . $check_this[7];
	my $url;
	my @val=join(',',@batch);
    my $val1=join(',',@batch);
	my $db = HealthStatus::Database->new( $config );		 
		my $desired_field = "rank";
		my $desired_table = "hs_userdata";
		my $stipulations = "where hs_uid='$pretty_batch'";
	    $data = $db->select_one_value( $desired_field, $desired_table, $stipulations );
			  
  if ($input->param('select_batch') eq "enter_more" ) {         	        
		
        if($data eq 'closed_batch' ){		
			 $url= $config->html_home . "/cgi-bin/hs/batch_print.cgi?list=1&batch_status=$data&msg_close=1";  			                			  
		   }
		elsif($data eq 'printed_batch'){		      	              			  
			 $url= $config->html_home . "/cgi-bin/hs/batch_print.cgi?list=1&batch_status=$data&msg_print=1";			                			  
		   }  
		else{
 		       $url = $config->html_home . "/cgi-bin/hs/batch_entry.cgi?batch_status=$data&restart=@val&assessment=GHA";
		    }		
	    }
 elsif ($input->param('select_batch') eq "print") {
	        if($data eq 'batch' ){ 
	   	    	
		      $url = $config->html_home . "/cgi-bin/hs/batch_print.cgi?close=1&batch_status=$data&db_batch_number=$val1";
			}
			else{
			  $url = $config->html_home . "/cgi-bin/hs/batch_print.cgi?print=1&batch_status=$data&db_batch_number=$val1";
            }			 
	   }
elsif ($input->param('select_batch') eq "close" ) {
	       if($data eq 'closed_batch' ){
		       $url= $config->html_home . "/cgi-bin/hs/batch_print.cgi?list=1&batch_status=$data&msg_close=1";
			}
		   else{
		      $url = $config->html_home . "/cgi-bin/hs/batch_entry.cgi?close=1&batch_status=$data&db_batch_number=@val";
           }		   
	  }
	 
	  print $input->redirect (-uri => $url );
	  exit;
 }	
	
if($input->param('list')){
	my $template = $config->template_directory . "batch_options.tmpl";
	print "template is $template<br>\n" if $Debug;
	my $db = HealthStatus::Database->new( $config );
	$db->debug_on( \*STDERR ) if $Debug;
    my $id = $config->db_id;
	$id = uc $id if ($config->db_driver eq 'oracle');
    if ($operating_system eq 'MSWin32'){
#	my @to_print_list = $db->batch_list( ('full_name', ', "where rank='closed_batch' order by full_name" );

	 @to_print_list = $db->batch_list( $id ,\@batch_assessments, "where rank='closed_batch' order by ". $id);
	 print "@to_print_list<br>" if $Debug;
	 @to_process_list = $db->batch_list( $id ,\@batch_assessments, "where rank='batch' order by ". $id);
	 print "@to_process_list<br>" if $Debug;
	 @been_printed_list = $db->batch_list(  $id ,\@batch_assessments, "where rank='printed_batch' order by ". $id );
	 print "@been_printed_list<br>" if $Debug;
	 }
	else{
	   @to_print_list = $db->batch_list( $id ,\@batch_assessments, "where rank='closed_batch' order by ". $id);
	 print "@to_print_list<br>" if $Debug;
	 @to_process_list = $db->batch_list( $id ,\@batch_assessments, "where rank='batch' order by ". $id );
	 print "@to_process_list<br>" if $Debug;
	 @been_printed_list = $db->batch_list(  $id ,\@batch_assessments, "where rank='printed_batch' order by ". $id );
	 print "@been_printed_list<br>" if $Debug;
	 }

	$db->HealthStatus::Database::finish( );
	$db->HealthStatus::Database::disconnect( );
	%vars = map { my $x = $_; $x =~ tr/A-Za-z_//c; $x, $input->param($_) }
		$input->param;
	$vars{config} = \%config;
	$vars{user_rank} = $user->hs_administration;
	$vars{user_db_id} = $user->db_id;
	$vars{want_process_list} = 1;
	$vars{hs_administration} = $user->hs_administration; # To display in admin side bar on batch_print.cgi 
	$vars{db_fullname} = $user->db_fullname;    # To display in admin side bar on batch_print.cgi
	$vars{msg} = "<b>Batch is already closed. You can't restart or close.</b>" if($input->param('msg_close'));
	$vars{msg} = "<b>Batch is already printed.You have to create a new batch to enter more forms.</b>" if($input->param('msg_print'));
	foreach(@to_process_list){
		$vars{to_process_list} .= "$_,";}
	print "$vars{to_process_list}\n" if $Debug;
	foreach(@to_print_list){
		$vars{to_print_list} .= "$_,";}
	print "$vars{to_print_list}\n" if $Debug;
	foreach(@been_printed_list){
		$vars{been_printed_list} .= "$_,";}
	print "$vars{been_printed_list}\n" if $Debug;
	fill_and_send( $template, $batch_user, \%vars, $config->html_use_ssi );
	exit;
	}
if($input->param('close') || $input->param('print')){
     
	   my $str='';
	   $str=$input->param('db_batch_number');
       my $batch_status = $input->param('batch_status');
       my @db_batch_number=split(/,/,$str);
	   my $c=0;   
	   my $footer_content; 
	   my $member;
	   my $db = HealthStatus::Database->new( $config );
       while($db_batch_number[$c] ne ''){
	   if(!$input->param('db_id')){	    
			my @batch_pieces = $db_batch_number[$c];
			my @batch_pieces_1 = split(/-/,$batch_pieces[2]);
			$hash1{$db_batch_number[$c]} = $batch_pieces[2];
			$hash1{db_batch_entered_by} = $batch_pieces_1[0];
			$batch_user = HealthStatus::User->new( \%hash1 );
			print "In CLOSE - $hash1{$db_batch_number[$c]}\n" if $Debug;
			
			# this gets the counts based on the batch number passed to us
			my $status = get_counts($db_batch_number[$c], $batch_user, $config);
			print "$status\n" if $Debug;
			if(!$status){ error("batch not found - $hash1{$db_batch_number[$c]} - cannot close");}
			
			$batch_user->pretty_print if $Debug;
		}
		else{
		
			my $str1='';
			$str1=$db_batch_number[$c];		
			# if you are here, you closed an active batch, so we don't need to look stuff up
			$hash1{db_number} = '';
			$hash1{db_email} = 'null@healthstatus.com';
			$hash1{db_emailOK} = '0';
			$hash1{hs_administration} = 'closed_batch';
			$hash1{db_employer} = '';
			$hash1{db_fullname} = 'batch - ' . $user->$str1;
			$hash1{db_id} = $input->param('db_id');

			$batch_user = HealthStatus::User->new( \%hash1 );
		}

	$batch_user->pretty_print if $Debug;
	my $temp_file_dir = $config->authenticate_dir;
	my $temp_file = '10001';
	my $approved1 = HealthStatus::Authenticate->new( $config, $temp_file_dir, $temp_file );
    if($batch_status eq 'closed_batch'){
	   $batch_user->hs_administration('closed_batch');	   
	}else{
	   $batch_user->hs_administration('printed_batch');
    }
	$hash1{hs_administration} = $batch_user->hs_administration;
	my $status1 = $approved1->change( $config, $batch_user );
	print "Login change status = $status1\n" if $Debug;		
	 %vars = map { my $x = $_; $x =~ tr/A-Za-z_//c; $x, $input->param($_) }
		 $input->param;
	$vars{config} = \%config;
	$vars{want_print_list} = 1;	
	my $batch_collector = "$config{batch_collector}" || "$config{cgi_dir}/batch_entry.cgi";
    my $batch_printer	= "$config{batch_printer}" || "$config{cgi_dir}/batch_print.cgi";
	my $batch_print = "$config{batch_printing}" || "$config{cgi_dir}/batch_print.cgi";
	my $member = $config{member_page} || "$config{cgi_dir}/assessment_recs.cgi";
    my $print_batch = $config->html_home."$batch_printer?print=1&db_batch_number=batch - " .$batch_user->db_batch_number; 
	  
	    $footer_content .= "<table border=0 cellspacing=0 cellpadding=0>";
		$footer_content .= "<tr>";
		$footer_content .= "<td></td>";
		$footer_content .= "<td align=left class=HStitle>";
		$footer_content .= "Printing Batch -" .$batch_user->db_batch_number. "<br>";
		$footer_content .= "</td></tr>";
		$footer_content .=  "<tr>";	
		$footer_content .=  "<td width=12>&nbsp;</td>";
		$footer_content .=  "<td align=center valign=top>";		
		$footer_content .=  "<table border=0 cellspacing=0 cellpadding=0 align=right>";
		$footer_content .=  "<tr><td class=HSbodytext colspan=3><br />&nbsp;<br />";
		$footer_content .=  "Entered by:" .$batch_user->db_batch_entered_by. "<br>";
		$footer_content .=  "Entered on:" .$date. " <br />&nbsp;<br />";
		$footer_content .=   "</td></tr>";
		$footer_content .=   "<tr><td align=right class=HSbodytext>";
		$footer_content .=   "Assessment &nbsp;&nbsp;&nbsp;  count<br /> ";
		$footer_content .=   "---------------------<br />";				
	    $footer_content .= "Cardiac &nbsp;&nbsp;&nbsp;"   .$batch_user->db_batch_count_crc . "<br>" ;
		$footer_content .= "Diabetes &nbsp;&nbsp;&nbsp;"   .$batch_user->db_batch_count_drc . "<br>" ;
		$footer_content .= "Fitness &nbsp;&nbsp;&nbsp;"   .$batch_user->db_batch_count_fit  . "<br>";
		$footer_content .= "General Health &nbsp;&nbsp;&nbsp;"   .$batch_user->db_batch_count_gha . "<br>" ;
		$footer_content .= "Well-being &nbsp;&nbsp;"  .$batch_user->db_batch_count_gwb . "<br>" ;
		$footer_content .= "Health Risk &nbsp;&nbsp;" .$batch_user->db_batch_count_hra . "<br>";
		$footer_content .= "---------------------<br />";
		$footer_content .= "Total &nbsp;&nbsp;&nbsp;"   .$batch_user->db_batch_count . "<br>";
		$footer_content .= "<br />&nbsp;<br /><br />&nbsp;<br />";
		$footer_content .= "Batch number - "   .$batch_user->db_batch_number . "<br>";
		$footer_content .= "Batch id - "   .$batch_user->db_id . "<br>";
		$footer_content .= "<br />&nbsp;<br />";
		$footer_content .= "Starting to print files:<br />";
		$footer_content .=  "</td></tr>";		
		$footer_content .=  "</table></td></tr>";
		$footer_content .=  "<tr><td width=12 height=30>&nbsp;</td><td align=center valign=top height=30>&nbsp;</td></tr>";
	    $footer_content .= "<tr><td align=right colspan=3 class=HSbodytext>";
	
#my $db = HealthStatus::Database->new( $config );

$db->debug_on( \*STDERR ) if $Debug;

my @returned_recs  =  $db->get_users_assessments_taken( $batch_user, $config, \@assessments );

if ($Debug){ foreach (@returned_recs) { print "$_\n"; } }

my $cnt = 0;

my $base_dir = $config->ggr_adv_page_dir . $batch_user->db_id . '/';

my @pdf_filelist;

my $trouble;
my $trouble_cnt=0;

foreach my $batched(@returned_recs){
	if ( ( $cnt % 5 ) == 0 && $cnt > 1)
		{
		if ($cnt == 5)	{ $footer_content .= "processing data - $cnt users completed<br />";
			}
		else	{ $footer_content .= "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;$cnt users completed<br />";
			}
		}

	my $this_assessment = $batched->{'assessment'};
	my $this_xnum = $batched->{'xnum'};

	my $got_it = $db->get_users_assessment( $batch_user, $config, uc ($this_assessment), $this_xnum );

	$batch_user->assessment(uc ($this_assessment));

	$batch_user->pretty_print if $Debug;

	if(!$got_it) { 	next; }

	++$cnt;

	if($cnt == 1){ mkdir $base_dir, 0777;	$footer_content .= "making the directory<br>";  }

	$batch_user->set_non_standard;

	my $health = HealthStatus->new(
		{
		assessment => uc($this_assessment),
		user       => $batch_user,
		config     => $config_file,
		}
		);

	$health->assess( $batch_user );

	my $pdf_file = $base_dir . $batch_user->db_id . "_" . $this_assessment . "_" . $cnt . ".pdf";

	$config->set('save_pdf_file_as', $pdf_file );

	my $m_format = 'PDFE' ;

	eval {my $data = $health->output( lc $m_format, $batch_user->db_template );};
	if ($@) {
		#carp $@ ." in creating output files, user=".$batch_user->db_id . "- record: $cnt - batch_print.cgi" ;
		$trouble .= "<strong>there was a problem creating the PDF for ".$batch_user->db_id." - $cnt</strong><br>";
		++$trouble_cnt;
		}

	push @pdf_filelist, $pdf_file;
	}

$footer_content .= "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;$cnt users completed<br />" if $cnt > 5;
$footer_content .= "***** ".$trouble." Please contact HealthStatus and let them know you received this message.<br>" if $trouble;
$footer_content .= "$trouble_cnt of $cnt had problems, the remaining reports in the zip file are OK.<br>" if ($trouble && $trouble_cnt < $cnt);
$footer_content .= "$trouble_cnt of $cnt had problems, no good reports were created.<br>" if ($trouble && $trouble_cnt >= $cnt);
$footer_content .= "processing completed<br>";
if($cnt && $cnt > $trouble_cnt){
	$footer_content .= "<br>creating zip file of reports<br>";
	# here we zip all the files
	# and give them a link to them

	$footer_content .= "processing" . $base_dir . $batch_user->db_id . ".zip<br>";

	my $zip = Archive::Zip->new();
	my $member = $zip->addTreeMatching( $base_dir, '' , '\.pdf$' );
	die 'write error' unless $zip->writeToFileNamed( $base_dir . $batch_user->db_id .'.zip' ) == AZ_OK;

	my $zip_file = $batch_user->db_id . '/' . $batch_user->db_id ;

	$footer_content .= qq|<p class="maintext-b">Your PDF files are stored in the report output area in directory | . $batch_user->db_id . '/. They are also in a zip file <a href="' . $config->ggr_adv . '?view=1&rpt_format=zip&file_name=' . $zip_file . '">Right click here to download</a>.  Save the file as ' . $batch_user->db_id . '.zip<br>&nbsp;<br> </p>';
	}
else	{
	$footer_content .= "<br><strong>No ASSESSMENTS IN BATCH</strong><br><strong>Nothing to Print</strong></p>";
	}
	 $footer_content .= "</td></tr>";
	 $footer_content .=  "<tr><td></td></tr>";
	 $footer_content .=  "<tr><td align=center class=HSbodytext colspan=3>[ <a href='$member'>assessment records page</a> ]</td><tr>";
	 $footer_content .=  "<tr><td>&nbsp;</td></tr><br>";
	 $footer_content .=  "<tr><td align=center class=HSbodytext colspan=3>[ <a href='$batch_print?list=1'>batch maintenance page</a> ]</td></tr>";
	 $footer_content .= "<tr><td>&nbsp;</td></tr>";

# %vars = map { my $x = $_; $x =~ tr/A-Za-z_//c; $x, $input->param($_) }
	# $input->param;
# $vars{config} = \%config;
# $vars{want_print_list} = 1;
# $vars{no_cgi_header} = 1;
    $db->finish( );
    $db->disconnect( ); 
    $c=$c+1;
   }
        $vars{footer_content} = $footer_content;
		my $template = $config->template_directory . "print_content.tmpl";
	    print "template is $template<br>\n" if $Debug;
	    fill_and_send( $template, $batch_user, \%vars, $config->html_use_ssi );
	    exit;   

}
# login
sub login
	{

	my ($config, $hash_ref) = @_;

        error( "The configuration object is bad after passing it to login." ) unless ref $config eq 'HealthStatus::Config';

	require HealthStatus::Authenticate;

	my %hash = %$hash_ref;

	my $user = HealthStatus::User->new( \%hash );

	my $temp_file_name = $config->authenticate_dir;
	my $temp_file = $input->cookie('hs_ident') || $input->param('hs_ident') || '10001';

	$user->db_number ( $input->cookie('hs_ident') );

	print "Temp file = $temp_file\n" if $Debug;

	my %config = map { $_, $config->$_ } $config->directives;

	$hash{config} = \%config;

	delete($hash{'Submit.x'}) if (exists($hash{'Submit.x'}));
	delete($hash{'Submit.y'}) if (exists($hash{'Submit.y'}));
	delete($hash{'action'}) if (exists($hash{'action'}));

	my $approved = HealthStatus::Authenticate->new( $config, $temp_file_name, $temp_file );

	my $status = $approved->check( $config, $user );

	print "Login status = $status\n" if $Debug;

	if ($config->authenticate_method eq 'client'){
		if ( $status eq TIMEOUT )
			{
			print $input->redirect (-uri => $config->timeout_page );
			exit;
			}
		elsif ( $status eq NOT_LOGGED )
			{
			print $input->redirect (-uri => $config->login_page );
			exit;
			}
		elsif ( $status ne APPROVED)
			{
			error( "There is a problem with your login." );
			exit;
			}
		}
	else	{
		if ( $status eq TIMEOUT )
			{
			$hash{cookie}=$input->cookie(-name=>'hs_ident',
			       -value=>"",
			       -expires=> '+1m');
			my $form = $config->template_directory . $config->timeout_page;
			fill_and_send( $form, $user, \%hash, $config->html_use_ssi );
			exit;
			}
		elsif ( $status eq NOT_LOGGED )
			{
			$hash{cookie}=$input->cookie(-name=>'hs_ident',
			       -value=>"",
			       -expires=> '+1m');
			my $form = $config->template_directory . $config->login_page;
			fill_and_send( $form, $user, \%hash, $config->html_use_ssi );
			exit;
			}
		elsif ( $status ne APPROVED)
			{
			error( "There is a problem with your login." );
			$hash{error_msg} = "There is a problem with your login.";
			my $form = $config->template_directory . $config->login_failed;
			fill_and_send( $form, $user, \%hash, $config->html_use_ssi );
			exit;
			}
		}
	return ($user);
	}

sub get_counts
	{
	my ($db_batch_number, $batch_user, $config) = @_;
	if ($Debug) {
		print "** In get_counts\n$db_batch_number, $batch_user, $config\n";
		$batch_user->pretty_print;
		$config->pretty_print;
	}
	my $db = HealthStatus::Database->new( $config );
	$db->debug_on( \*STDERR ) if $Debug;

	return FALSE if(!$db_batch_number);

    my $stip = "where full_name='$db_batch_number'";
	$stip= "WHERE FULL_NAME='$db_batch_number'"  if ($config->db_driver eq 'oracle');
	my $found = $db->_lookup_user( $batch_user, $config, $stip );

	return FALSE if(!$found);

	my $temp_id = $batch_user->db_id;
	$batch_user->db_batch_count_crc($db->hs_count('CRC',"where hs_uid='$temp_id'"));
	$batch_user->db_batch_count( $batch_user->db_batch_count + $batch_user->db_batch_count_crc );
	$batch_user->db_batch_count_drc($db->hs_count('DRC',"where hs_uid='$temp_id'"));
	$batch_user->db_batch_count( $batch_user->db_batch_count + $batch_user->db_batch_count_drc);
	$batch_user->db_batch_count_fit($db->hs_count('FIT',"where hs_uid='$temp_id'"));
	$batch_user->db_batch_count( $batch_user->db_batch_count + $batch_user->db_batch_count_fit);
	$batch_user->db_batch_count_gha($db->hs_count('GHA',"where hs_uid='$temp_id'"));
	$batch_user->db_batch_count( $batch_user->db_batch_count + $batch_user->db_batch_count_gha);
#	$batch_user->db_batch_count_hra($db->hs_count('HRA',"where hs_uid='$temp_id'"));
#	$batch_user->db_batch_count( $batch_user->db_batch_count + $batch_user->db_batch_count_hra);
#	$batch_user->db_batch_count_hra($db->hs_count('GWB',"where hs_uid='$temp_id'"));
#	$batch_user->db_batch_count( $batch_user->db_batch_count + $batch_user->db_batch_count_gwb);
#	$batch_user->db_batch_count_mr($db->hs_count('MR',"where hs_uid='$temp_id'"));
#	$batch_user->db_batch_count( $batch_user->db_batch_count + $batch_user->db_batch_count_mr);
#	$batch_user->db_batch_count_pt($db->hs_count('PT',"where hs_uid='$temp_id'"));
#	$batch_user->db_batch_count( $batch_user->db_batch_count + $batch_user->db_batch_count_pt);
	$batch_user->pretty_print if $Debug;
	$db->finish( );
	$db->disconnect( );
	return TRUE;
	}

=head1 BUGS

* none that i've found so far.

=head1 TO DO

* it would be nice if the templates names in the HTML forms
were not the same as the actual file names.  that way, we could
allow only certain template names and never tell the user what
the file names are.

* the same issue exists for configuration files.

* the error routine is simple, but you can't do much when
you can't find the right files.

=head1 AUTHOR

brian d foy <bdfoy@cpan.org>
Greg White <gwhite@healthstatus.com>

=head1 COPYRIGHT

Copyright 2001-2006, HealthStatus.com

=cut

1;
