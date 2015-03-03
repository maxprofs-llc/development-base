#!/usr/local/bin/perl
use strict;

#  This includes the current directory in the list of places to check for
# modules and other files, mainly for NT systems.
use File::Basename        qw( dirname );
use File::Spec::Functions qw( rel2abs );
use Date::Language;
use Date::Parse;
use Date::Format;

use lib dirname(rel2abs($0)),'.','/usr/local/www/vhosts/managed2/modules/pdf', '/usr/local/www/vhosts/managed2/modules';
use vars qw( $Debug $production $cook $config_file %setup_tables %field_info %Tables %Fields);

if (!do('common.inc')) {
   my $error = $@ ? $@
             : $! ? $!
             : 'did not return a true value';
   die("Unable to load common stuff: $error\n");
}

use CGI qw(-no_xhtml -debug);
if (!$production) {
	use CGI::Carp qw(fatalsToBrowser);
	}
else {
	use CGI::Carp;
	}
# Removing warnings in log while module is being used with CGI version 4 or above
$CGI::LIST_CONTEXT_WARN = 0;	

use HealthStatus qw( fill_and_send error check_digit );
use HealthStatus::Authenticate;
use HealthStatus::Config;
use HealthStatus::Constants;
use HealthStatus::Database;
use HealthStatus::User;
use HealthStatus::Email;

use Spreadsheet::ParseExcel;
use Spreadsheet::Read;
use Data::Dumper;
#use DBIx::Admin::BackupRestore;

my $input = new CGI();

my $config = getConfig($input->param('extracfg'));
my %config = map { $_, $config->$_ } $config->directives;

if (!do($config->conf_config_dir.'/healthstatus_db.conf')) {
   my $error = $@ ? $@
             : $! ? $!
             : 'did not return a true value';
   die("Unable to load ".$config->conf_config_dir."/healthstatus_db.conf: $error\n");
}

if (!do($config->db_config_file)) {
   my $error = $@ ? $@
             : $! ? $!
             : 'did not return a true value';
   die("Unable to load ".$config->db_config_file.": $error\n");
}

my %input = $input->Vars();

############################################################################
### Comment out the following line before going into production ############
$Debug = $input->param("HS_Debug") || $ENV{HS_DEBUG} || 0;
#### only uncomment if you need to debug the input scripts      ############
############################################################################

# authenticate_user redirects the user if they not allowed to
# view this page
my $user = authenticateUser(["admin"], $input, $config) or die "You should never see this message.";

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

my $upload_dir 			= $config->conf_data_dir . "/IMPORT/";
if (! -d $upload_dir)
{
        mkdir -p $upload_dir;
}
my $temp_file_name 		= $config->authenticate_dir;
my $temp_file 			= '0';
my $filename			= $upload_dir.$user->db_id . ".txt";
my $progressFile;
my $fh;
my $health;
my %vars;
my( $year, $month, $day, $hour, $min, $sec ) = (localtime)[5,4,3,2,1,0];
$year  += 1900;
$month += 1;

my $time = sprintf("%04d%02d%02d%02d%02d%02d", $year, $month, $day, $hour, $min, $sec);

my $process_file;
my $doImport = 0;
my $doReview = 0;
my $review_start = 0;
my $rev_count;
if($input->param('submit') eq 'Import Data')
{
        $doImport=1;
}
elsif ($input->param('submit') eq 'Review Data')
{
        $doReview=1;
        $review_start=1;
	my $rev_file=$upload_dir . "/" . $process_file . "_review";
	unlink $rev_file if (-e $rev_file);
}

if ($doImport || $doReview)
{
	my $upload_filehandle 	        = $input->upload("data_file"); 
	my $filename			= $input->param("data_file") ;
	my @array_profile		= split(',', $input->param('profile'));

        my $temp                        = shift @array_profile;
        my @tempValue                   = split('\|', $temp);
        my $profileName                 = shift @tempValue;
        my $description                 = shift @tempValue;
        my $data_type                   = shift @tempValue;
        my $assessment                  = shift @tempValue;

        my $pos                         = rindex ($filename, ".");
        my $file                        = substr ($filename, 0, $pos);
        my $ext                         = substr ($filename, $pos+1);
        $pos                            = rindex ($filename, "/");
        if ($pos == -1)
        {
                $file                   = substr ($filename, $pos+1);
        }
        else
        {
                $file                   = $filename;
        }

        $process_file   		= $file;
        $progressFile                   = $upload_dir . "/" . $process_file. "_progress.txt";
        open( $fh, '>', $progressFile) or die $! if($doImport);
        print $fh "Start Import Data for file: $filename\n" if($doImport);

	my $db 				= HealthStatus::Database->new( $config );

        $health 			= HealthStatus->new({
                                		assessment => 'HRA',
                                		user       => $user,
                                		config     => $config_file,
                                		});

        #Get records from DB
        my $stipulations = "WHERE hs_uid='$user->{'db_id'}' AND profile LIKE '$profileName' AND filename like '$file'";
        my $recordsDB    = $db->select_one_value( "records", $Tables{IMP_COUNT}, $stipulations)|| 0;
        my $records	 = 0;
        my $status       = $db->select_one_value( "status", $Tables{IMP_COUNT}, $stipulations) || "pending";
        print $fh "Searching for previous execution of file: $file against profile: $profileName by user: '$user->{'db_id'}'\n" if($doImport);
        print $fh "Found: $recordsDB Status: $status\n" if($doImport);
        my ($allCols, @tempCols);

        if ($status eq "pending")
        {
	        if($ext eq 'xls')
                {
                        print $fh "Start parsing xls file\n" if($doImport);
		        my $xls 	= ReadData ($filename, sep => ',', quote => '"');
                        $records 	= $recordsDB + 2;  # we add 2 because we want to skip 1st row of excel and it's count begins with 1
                        #Save Column Headings in a || separated manner
                        @tempCols 	= Spreadsheet::Read::row ($xls->[1], 1);
                        foreach my $val (@tempCols ){
                                $allCols .= $val . "||";
                        }
        
		        for(my $i=$records; $i <= $xls->[1]{maxrow} ; $i++) 
                        {
                                print $fh "Reading row: $i\n" if($doImport); 
			        my @column 	= Spreadsheet::Read::row ($xls->[1], $i);
                                my $allContents;
                                #Save each Row in a || separated manner
                                foreach my $val (@column ){
                                        $allContents .= $val . "||";
                                }
                                my %insert_hash = (data_type    => $data_type,
					           assessment   => $assessment,
                                                   profileName  => $profileName,
                                                   allContents  => $allContents,
                                                   allColumns   => $allCols);
                                
                                &insert_data($db, $config, \@array_profile, \@column, \%insert_hash);
                                $recordsDB++;
				if ($doImport)
                                {
                                	$status = ($i == $xls->[1]{maxrow})? "complete" : "pending";
                                	print $fh "Saving import count. Total records in database: $recordsDB. Status: $status\n" if($doImport);
        
                                	%vars = (db_id    => $user->{'db_id'},
                                            	profile  => $profileName,
                                            	filename => $file,
                                            	records  => $recordsDB,
                                            	status   => $status,);
                                	$db->save_import_count($user, "IMP_COUNT",\%vars);
                                }
                                $review_start++   ;
		        }
                } 
                elsif ($ext eq 'xlsx')
                {
                        print $fh "Start parsing xlsx file\n" if($doImport);
                        &do_upload($filename,$upload_filehandle,$upload_dir);
                        $filename 	= "$upload_dir/$filename";
                        my $xls 	= Spreadsheet::XLSX->new($filename);
                        $records 	= $recordsDB + 2;  # we add 2 because we want to skip 1st row of excel and it's count begins with 1

                        foreach my $sheet (@{$xls -> {Worksheet}}) 
                        {
                                $sheet -> {MaxRow} ||= $sheet -> {MinRow};
                                foreach my $col ($sheet -> {MinCol} ..  $sheet -> {MinCol})
                                {
                                        my $cell= $sheet -> {Cells} [1] [$col];
                                        if ($cell) {
                                                 my $val= $cell -> {Val};
                                                 push (@tempCols, $val);
                                                 $allCols .= $val . "||";
                                        }
                                }

                                foreach my $row ($sheet -> {MinRow}+$records .. $sheet -> {MaxRow}) 
                                {
                                        print $fh "Reading row: $records\n" if($doImport);
                                        my @column;
                                        my $allContents;
         
 		                        $sheet -> {MaxCol} ||= $sheet -> {MinCol};
 		
 		                        foreach my $col ($sheet -> {MinCol} ..  $sheet -> {MaxCol}) 
                                        {
 		
 			                        my $cell= $sheet -> {Cells} [$row] [$col];
 			                        if ($cell) {
                                                        my $val= $cell -> {Val};
                                                        push (@column, $val);
                                                        $allContents .= $val . "||";
                                                }
                                        }
                                        my %insert_hash = (data_type    => $data_type,
                                                   assessment   => $assessment,
                                                   profileName  => $profileName,
                                                   allContents  => $allContents,
                                                   allColumns   => $allCols);

                                        &insert_data($db, $config, \@array_profile, \@column, \%insert_hash);
                                        $recordsDB++;
					if ($doImport)
					{
                                        	$status = ($recordsDB  == $sheet -> {maxrow})? "complete" : "pending";
                                        	print $fh "Saving import count. Total records in database: $recordsDB. Status: $status\n" if($doImport);

                                        	%vars = (db_id    => $user->{'db_id'},
                                    	            	profile  => $profileName,
                                    	            	filename => $file,
                                    	            	records  => $recordsDB,
                                                    	status   => $status,);
                        	        	$db->save_import_count($user, "IMP_COUNT",\%vars);
					}
					$review_start   = 0;
                                }
                        }
	        } 
                else 
                {
                        print $fh "Start parsing csv file\n" if($doImport);
		        &do_upload($filename,$upload_filehandle,$upload_dir);
		        open ( FILE, "$upload_dir/$filename" ) or die "$!";  
                        $records = $recordsDB + 2;  # we add 1 because we want to skip 1st row of csv and it's count begins with 0

                        my $allContents;
                        my @data = <FILE>;
                        close (FILE);
                        my $i=1;
                        foreach my $line (@data)
                        {         
                                chomp $line;
                                $line =~ s,[\r\n]+$,,g;
                                next if ($line eq '');
                                if ($i == 1)
                                {
                                        $allContents =  $line;
                                        $line =~ s/[\n\r]+//g;
                                        @tempCols = split(',', $line);
                                        $allCols                =~ s/,/||/g;
                                }
                                elsif ($i >= $records)
                                {
                                        print $fh "Reading row: $i\n" if($doImport);
                                        my $allContents =  $line;
			                $line =~ s/[\n\r]+//g;
			                my @column 		= split(',', $line);
                                        $allContents            =~ s/,/||/g;
                                        my %insert_hash         = (data_type    => $data_type,
                                                   assessment   => $assessment,
                                                   profileName  => $profileName,
                                                   allContents  => $allContents,
                                                   allColumns   => $allCols);


                                        &insert_data($db, $config, \@array_profile, \@column, \%insert_hash);
                                        $recordsDB++;
                                        if ($doImport)
					{
                                        	$status = ($i-1 == $recordsDB)? "complete" : "pending"; #we subtract 1 to ignore columns heading in csv file
                                        	print $fh "Saving import count. Total records in database: $recordsDB. Status: $status\n" if($doImport);
                                        	%vars = (db_id      => $user->{'db_id'},
                                                    	profile    => $profileName,
                                                    	filename   => $file,
                                                    	records    => $recordsDB,
                                                    	status     => $status,);
                                        	$db->save_import_count($user, "IMP_COUNT",\%vars);
                                        }
                                        $review_start   = 0;
                                }
                        	$i++;
		        }
        
	        }
	
                #Send email to admin about count, profile used, userid, filename
                if ($doImport)
		{
                	%vars = (db_id    => $user->{'db_id'},
                            	profile  => $profileName,
                            	filename => $file,
                            	records  => $recordsDB,
                            	status   => $status,
                            	date     => $time);
                	#$vars->{'home'} = $config->{'html_home'};
                	#$vars->{'date'} = Date::Calc::Today_and_Now();
                	print $fh "All rows parsed.\n" if($doImport);
                	print $fh "Sending email to admin: details: profile: $profileName, File: $file, records uploaded: $recordsDB. status: $status\n" if($doImport);
                	HealthStatus::Email::sendEmailFromConfig($health, 'import_admin', 'admin', 'admin', \%vars);

                	if ($status eq "complete")
                	{
	                	$vars{message}			= "Data has been imported successfully.";
                        	print $fh "SUCCESS\n" if($doImport);
                        	my $complete = $upload_dir . "/" . $file . "_completed.txt";
                        	rename ($progressFile, $complete);
                	}
                	else
                	{
                        	$vars{message}                  = "Data imported with errors.";
                        	print $fh "FAILED\n" if($doImport);
                	}
		}
       	}
        else
        {
                $vars{message}                  = "Data already imported.";
        }

        $db->disconnect( );
        close $fh if($doImport);
        #call template
        if ($doImport)
        {
        	$vars{data_import_msg}                  = 1 ;
		my $template				= $config->template_directory . 'data_import.tmpl';
		fill_and_send( $template, $user, \%vars , $config->html_use_ssi );
        }
        else
        {
                my $goto_page = "review_import.cgi?file=$process_file&page=1";
                print $input->redirect(-uri=> $goto_page );
        }

}
elsif($input->param('submit') eq 'View History')
{
        my $db 			= HealthStatus::Database->new( $config );
        my $stipulation;
        $stipulation 		= " WHERE hs_uid='$user->{'db_id'}' ";
        my @query_results  	=  $db->select( '*',$HealthStatus::Database::Tables{IMP_COUNT}, $stipulation, 1 );
        my %hash;
        my $str;
        foreach my $query (@query_results)
        {
                $str .= "<table width=700px border=0 style=\"border: 1px solid black;\">";
                $str .= "<tr><td colspan=2 bgcolor=#cccccc><b><font color=#660000>                  $query->{'filename'}                  </font></b></td></tr>";
                $str .= "<tr><td width=200px><b>Profile Used:                       </b></td><td>   $query->{'profile'} 	          </td></tr>";
                $str .= "<tr><td><b>Date Uploaded:                       	    </b></td><td>   $query->{'adate'} 			  </td></tr>";
                $str .= "<tr><td><b>Records Uploaded :                       	    </b></td><td>   $query->{'records'} 	          </td></tr>";
                $str .= "<tr><td><b>Status:                       		    </b></td><td>   $query->{'status'} 			  </td></tr>";
                $str .= "</table><br>";
        }
        $str = "<span style=\"color: #660000;\"><b>No Profile History exists !!</b></span>" if ($str eq '');

        $hash{message}                  = $str;
        my $template                    = $config->template_directory . 'view_import_profile.tmpl';
        fill_and_send( $template, $user, \%hash , $config->html_use_ssi );

}
elsif($input->param('submit') eq 'View Pending')
{
        my $db 			= HealthStatus::Database->new( $config );
        my $unum 		= $input->param('pos');
        my $stipulation 	= " WHERE unum=$unum ";
        my @query_results  	= $db->select( '*',$HealthStatus::Database::Tables{IMP}, $stipulation, 1); 
        my %hash;
        my $str;
        foreach my $query (@query_results)
        {
                my $data 	= $query->{'profile_data'};
                my @prof_data 	= split(/\|\|/, $data);
                my $cols 	= $query->{'profile_cols'};
                my @prof_column = split (/\|\|/, $cols);
                $str 		.= "<table width=700px border=1 style=\"border: 1px solid black;\">";
                $str 		.= "<tr><td colspan=2 bgcolor=#cccccc><b><font color=#660000>                  DETAILS:                  </font></b></td></tr>";

                for (my $i=0; $i <$#prof_data && $i <$#prof_column; $i++)
                {
                        my $key = $prof_column[$i];
                        my $val = $prof_data[$i];
                        if ($val =~ /^\s*$/)
                        { 
                                $val 	= "<img src=\"images/global/trans.gif\" width=\"1\" height=\"22\">";
                        }
                	$str 	.= "<tr><td width=200px><b>$key                    </b></td><td width=200px>   $val                        </td></tr>";
                }
                $str 		.= "</table><br>";
        }
        $hash{message}                  = $str;
        my $template                    = $config->template_directory . 'view_import_profile.tmpl';
        fill_and_send( $template, $user, \%hash , $config->html_use_ssi );

}
elsif($input->param('submit') eq 'Download')
{
        my $db 			= HealthStatus::Database->new( $config );
        my $unum 		= $input->param('pos');
        my $stipulation 	= " WHERE unum=$unum ";
        my @query_results  	= $db->select( '*',$HealthStatus::Database::Tables{IMP}, $stipulation, 1);
        my $short_name; 
        my $filename;

        foreach my $query (@query_results)
        {
                $short_name                  = $query->{'profile'} . ".csv";
                $filename                    = $upload_dir."/".$short_name;
		open ( FH, "> $filename" ) or die "$!";
                my $data 		     = $query->{'profile_data'};
                my $cols 		     = $query->{'profile_cols'};
                $data 			     =~ s/\|\|/,/g;
                $cols 			     =~ s/\|\|/,/g;
                print FH "$cols\n$data";
                close FH;
        }
        my $fh = new IO::File "$filename", "r" or die "$filename: $!\n";
        my $file = do { local $/; binmode $fh; <$fh> };
        print $input->header(-type=>'text/plain', -attachment =>$short_name ), $file;
}
else 
{
	my %profile_hash;
	# if profile exist for this user, extract the pairing details from import txt file
        print STDERR "fileeee: $filename\n";
	if(-e $filename) {
		open ( FH, "$filename" ) or die "$!";  
		while(<FH>) {
			chomp($_);
			my @profile_array = split('\|', $_);
                        my $temp=$_;
                        my $pos = index $temp, "|";
                        my $profileName = substr($temp, 0, $pos);
                        $profile_hash{$profileName} = $temp;
		}
		close FH;
	} else {
		$vars{data_import_msg}			= 1 ; 
		$vars{message}				= "Please create a profile to import the data.";
	}

	$vars{profile_hash}		= \%profile_hash;
	my $template = $config->template_directory . 'data_import.tmpl';
	fill_and_send( $template, $user, \%vars , $config->html_use_ssi );
	exit;
}

#upload a file 
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

#insert the data for each row to the Healthstatus database 
sub insert_data() 
{
        my ($db, $config, $array_profile, $column, $insert_hash) = @_;

        my $data_type   = $insert_hash->{'data_type'};
        my $assessment  = $insert_hash->{'assessment'};
        my $profileName = $insert_hash->{'profileName'};
        my $allContents = $insert_hash->{'allContents'};
        my $allColumns  = $insert_hash->{'allColumns'};

	my @data_column = @$column;
	my %hash;
        foreach my $profile_data (@$array_profile){
                my @hash_data = split('=', $profile_data);
		$hash{$hash_data[1]} .= ' ' if ($hash{$hash_data[1]});
                $hash{$hash_data[1]} .= $data_column[$hash_data[2]] ;
        }

	if (!$hash{db_fullname} || !$hash{first_name} || !$hash{last_name})
	{	
		do_name_customization(\%hash);
	}

        if (defined $hash{birth_month} && defined $hash{birth_date} && defined $hash{birth_year})
        {
                if ($hash{birth_month} eq $hash{birth_date} && $hash{birth_month} eq $hash{birth_year})
                {
                       do_date_customization(\%hash);
                }
        }
        if (defined $hash{weight})
        {
                do_weight_customization(\%hash);
        }
        if (defined $hash{height})
        {
                do_height_customization(\%hash);
        }
	$db->debug_on( \*STDERR ) if $Debug;

        if(!$hash{db_number}) { $hash{db_number} = $temp_file }
	my $file                = $upload_dir . "/" . "IMPORT_" .  $time if ($doImport);

        my $approved = HealthStatus::Authenticate->new( $config, $temp_file_name, $temp_file );

        $approved->debug_on( \*STDERR ) if $Debug;
        my $stipulation;
        my @query_results;
        $stipulation         	= " WHERE hs_uid='$hash{'db_id'}'" if($hash{'db_id'});
        @query_results       	= $db->select( ['unum'],$HealthStatus::Database::Tables{REG}, $stipulation, 1 ) if($hash{'db_id'});
        my $unum_from_db 	= $query_results[0]->{unum} || 0;
        print $fh "Searching for existing user with " .  $hash{'db_id'}. ". Found: $unum_from_db\n" if ($doImport);


        my %flags 		= { };
        my $user_new             = HealthStatus::User->new( \%hash );
        if (!$unum_from_db && $data_type ne 'biometric' && $doImport)
        {
                #In all cases but biometric we add the user, if, he doesn't already exist
                print $fh "User does not exists. Adding in database\n";
                $approved->add( $config, $user_new, \%flags );
                print $fh "Taking backup of tables REG and PASS in file: $file\n";
                create_backup($file, $HealthStatus::Database::Tables{REG}, $stipulation);
                create_backup($file, $HealthStatus::Database::Tables{PASS}, $stipulation);
                
        }
        @query_results  	= $db->select( ['unum'],$HealthStatus::Database::Tables{REG}, $stipulation, 1 );
        $hash{db_number}   	= $query_results[0]->{unum};
        $user_new->{unum} 	= $query_results[0]->{unum};

	print $fh "Working for data type: $data_type\n" if ($doImport);
	if($data_type eq "demographic") 
        {
                #demographic: Merge Biometric -> Demographic Data
                #IF user already exists, update his information from excel
                if ($doImport)
                {
			if ($unum_from_db)
			{
                        	print $fh "Updating user information in database\n";
                        	$db->update_user($user_new);
			}
                	my %var = (fname => $user_new->{'full_name'},
                           	home  => $config->{'html_home'}); 
                	print $fh "Sending email to user: $user_new->{full_name}, email: $user_new->{db_email}\n"; 
			#HealthStatus::Email::sendEmailFromConfig($health, 'import_user', $user_new->{db_email}, "admin", \%var  );
		}
		else
		{
                        review_data($user_new, 'USER');
                        review_data($user_new, 'PASS');
		}

	} 
        elsif ($data_type eq 'biometric_demographic') 
        {
                #biometric_demographic: Import Historical -> Biometric and Demographic Data

		if ($doImport)
		{
                	#once the user is added we save it's assessments
                	print $fh "Saving user's HRA assessment.\n";
                	$db->save_users_assessment( $user_new, 'HRA' );
                	my $tempx = $user_new->{'xnum'};
                	print STDERR "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX: $tempx";
                	print $fh "XNum: $tempx\n";

                	my $stipulation1       = " WHERE hs_uid='$hash{'db_id'}' AND xnum=$tempx";
                	print $fh "Creating backup of table HRA in file: $file\n";
                	create_backup($file, $HealthStatus::Database::Tables{HRA}, $stipulation1);

                	print $fh "Saving user's GHA assessment.\n";
                	$db->save_users_assessment( $user_new, 'GHA' );
                	$tempx = $user_new->{'xnum'};
                	print $fh "XNum: $tempx\n";

                	$stipulation1       = " WHERE hs_uid='$hash{'db_id'}' AND xnum=$tempx";
                	print $fh "Creating backup of table GHA in file: $file\n";
                	create_backup($file, $HealthStatus::Database::Tables{GHA}, $stipulation1);

                	my %var = (fname => $user->{'full_name'},
                           	home  => $config->{'html_home'});
                	print $fh "Sending email to user: $user_new->{'full_name'}, email: $user_new->{db_email}\n";
                	#HealthStatus::Email::sendEmailFromConfig($health, 'import_user', $user_new->{db_email}, "admin", \%var  );
		}
		else
		{
                        review_data($user_new, 'USER');
                        review_data($user_new, 'PASS');
			review_data($user_new, 'HRA' );
                        review_data($user_new, 'GHA' );
		}
        }
        elsif ($data_type eq 'biometric_only') 
        {
                #biometric_only: Import Historical -> Biometric Data

		if ($doImport)
		{
                	#once the user is added we save it's assessments
                	print $fh "Saving user's $assessment assessment.\n";
                	$db->save_users_assessment( $user_new, uc($assessment));
                	my $tempx = $user_new->{'xnum'};
                	print STDERR "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX: $tempx";
                	print $fh "XNum: $tempx\n";

                	my $stipulation1 = " WHERE hs_uid='$hash{'db_id'}' AND xnum=$tempx";
                	print $fh "Creating backup of table $assessment in file: $file\n";
                	create_backup($file, uc($assessment), $stipulation1);

                	my %var = (fname => $user_new->{'full_name'},
                           	home  => $config->{'html_home'});
                	print $fh "Sending email to user: $user_new->{'full_name'}, email: $user_new->{db_email}\n";
                	#HealthStatus::Email::sendEmailFromConfig($health, 'import_user', $user_new->{db_email}, "admin", \%var  );
		}
                else
                {
			review_data($user_new, 'USER');
			review_data($user_new, 'PASS');
                        review_data($user_new, uc($assessment) );
		}
        }
        else 
        {
                #biometric: Merge Biometric -> Biometric and Informational Data

                #For a Biometric data, if user doesn't exist, don't add but insert in Import Table
                if ($hash{db_number} == 0)
                {
			if ($doImport)
			{
                        	print STDERR "Contents: $allContents\n";
                        	print $fh "Saving import data for Admin's approval\n";
                        	$db->save_import_data($user_new, $user->db_id, $allContents, $profileName, $allColumns);
			}
                }
                else 
                {
			if ($doImport)
			{
                        	print $fh "Saving user's $assessment assessment.\n";
                        	$db->save_users_assessment( $user_new, uc($assessment));

                        	my $tempx = $user_new->{'xnum'};
                        	print STDERR "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX: $tempx";
                        	print $fh "XNum: $tempx\n";
                        	my $stipulation1 = " WHERE hs_uid='$hash{'db_id'}' AND xnum=$tempx";
	
                        	print $fh "Creating backup of table $assessment in file: $file\n";
                        	create_backup($file, uc($assessment), $stipulation1);

                        	my %var = (fname => $user->{'full_name'},
                                   	home  => $config->{'html_home'});
                        	print $fh "Sending email to user: $user_new->{'full_name'}, email: $user_new->{db_email}\n";
                        	HealthStatus::Email::sendEmailFromConfig($health, 'import_user', $user_new->{db_email}, "admin", \%var  );
			}
			else
			{
		                review_data($user_new, 'USER');
                        	review_data($user_new, 'PASS');
				review_data($user_new, uc($assessment) );
			}
                }
	}
        $db->finish( );
}

sub do_date_customization(\%)
{
        my $hash          = shift;
        my $date          = $hash->{birth_date};
        my @dateArr       = strptime($date);
        my ($mm, $dd, $yyyy)= strftime("%m, %d, %Y", @dateArr);
        $hash->{birth_date} = $dd;
        $hash->{birth_month}= $mm;
        $hash->{birth_year} = $yyyy;
        
        print STDERR "Date : mm: $mm ==== dd: $dd ===== yy: $yyyy\n";

}

sub do_weight_customization(\%)
{
}
sub do_height_customization(\%)
{
        my $hash          = shift;
        my $height        = $hash->{height};
        my ($feet, $inch) = split('\'', $height);
        if ($feet != $height && $inch)
        {
                my $newInch = split('\"', $inch);
                $inch       = $newInch;
                $height     = ($feet*12)+$inch
        }
        $hash->{height} = $height;
        print STDERR "Height Converted: $height";
 
}
sub do_name_customization(\%)
{
        my $hash          = shift;
        my $first_name	  = $hash->{first_name};
	my $last_name	  = $hash->{last_name};
	my $full_name	  = $hash->{db_fullname};

	if ($first_name eq '' && $last_name eq '')
	{
		$full_name =~ s/\s+/ /g;
		($first_name, $last_name) = split (/ /, $full_name);
	}
	elsif($full_name eq '')
	{	
		$full_name = $first_name . ' ' . $last_name;
	}
	$hash->{first_name}	= $first_name;
	$hash->{last_name}	= $last_name;
	$hash->{db_fullname}	= $full_name;
		
}

sub create_backup()
{
        my $file = shift;
        my $table = shift;
        my $value = shift;
        if ($table && $value)
	{
		open ( FILE, ">>$file" ) or die "$!";
		print FILE "DELETE FROM $table $value; \n";	
		close FILE;
	}
        else
	{
		print $fh "Failed to create Backup File\n";
	}
}

sub review_data()
{
        my $rev_user = shift;
        my $table = shift;
        my %rev_data;
        my $file = $upload_dir . "/" . $process_file . "_review";
        my $str;
	$rev_count = $review_start;

        open ( FH, ">> $file");

        my @field_kys = keys %{$HealthStatus::Database::Fields{$table}};

        foreach my $field ( @field_kys )
        {
                my $user_obj = $HealthStatus::Database::Fields{$table}{$field};
                if( $user_obj ne 'null' && $user->get($user_obj) )    {
                        $rev_data{$field} = $rev_user->$user_obj;
                        $str .= ",$field,$rev_user->{$user_obj}";
                }
        }
        print FH "$rev_count,$table$str\n";
        close FH;
}

1;
