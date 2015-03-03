#!/usr/local/bin/perl
use File::Basename        qw( dirname );
use File::Spec::Functions qw( rel2abs );

use lib dirname(rel2abs($0)),'.','/usr/local/www/vhosts/managed2/modules/pdf', '/usr/local/www/vhosts/managed2/modules';
if (!do('common.inc')) {
   my $error = $@ ? $@
             : $! ? $!
             : 'did not return a true value';
   die("Unable to load common stuff: $error\n");
}

use vars qw( %Tables %Fields );

use DBI;
use DBIx::Sequence;
use CGI qw /:standard/;
use CGI::Carp qw(fatalsToBrowser);
use HealthStatus::Config;
use HealthStatus;
use HealthStatus::Database;
use HealthStatus::User;
use HealthStatus::Constants;
use Mail::Sendmail;

my $q=new CGI;
my $config = getConfig($q->param('extracfg'));

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

my $Debug = $ENV{HS_DEBUG} || 0;

my $FONT = "<FONT FACE=\"verdana,helvetica,arial\" SIZE=\"-1\">";

$| = 1;

# create a CGI object

my $q=new CGI;
my $overwrite = $q->param('overwrite');
my $getsql = $q->param('getsql');

if($getsql && $overwrite eq '') {$overwrite=1;}
if($getsql) {$silent=1;}
my $sql = '';

print $q->header, $q->start_html(-title=>'HealthStatus.com Database Table Setup',
				-author=>'Greg White gwhite@healthstatus.com',
				-bgcolor=>'#FFFFFF',
				-text=>'#666666',
				-link=>'#666666',
				-vlink=>'#669933',
				-alink=>'#666666'),
				img{src=>$config->html_base."images/global/hs_logo_77.jpg", align=>'center'},
				h3("HealthStatus.com") if !$silent;

# Environmental variables used by Oracle
 if ( lc($config->db_driver) eq 'oracle' ) {
	$ENV{ORACLE_SID}   = $config->db_database;
	$ENV{ORACLE_HOME}  = $config->db_oracle_home;
	$ENV{EPC_DISABLED} = "TRUE";
	$ENV{ORAPIPES} = "V2";
	}

if ($Debug) {
	$config->pretty_print if !$silent;
}

#########################################################################################
#
#					Start of Page
#Connect to database and display results.
#########################################################################################
print "Database = ".$config->db_database."<br>" if !$silent;

my $db1 = HealthStatus::Database->new( $config );
my $dbh  =  DBI->connect($config->db_connect, $config->db_user, $config->db_pass );
if($dbh) {
    print "<I><H1 ALIGN=\"CENTER\">DB CONNECTED</H1></I><P>\n" if !$silent;
} else {
	if($silent) {print "Content-Type: text/html\n\n";}
    print "<P><FONT COLOR=\"RED\"><H1 ALIGN=\"CENTER\">DB NOT CONNECTED!!</H1></FONT><P>using connection string: $config->db_connect<br>$DBI::errstr</body></html>\n";
    exit;
}

if((!$overwrite || lc($config->authenticate_method) eq 'debug') && !$silent) {
	print "<p><b>USAGE:
	<br />Authenticate method in configuration file is set to debug, change to hs before proceeding.
	<br />To force the table creation - rather than just table indexing - the web address
	for this page must end like:
	<br />&nbsp; &nbsp; <a href=\"hs_make_tables.cgi?overwrite=1\">\"hs_make_tables.cgi?overwrite=1\"</a>
	- THIS WILL WIPE OUT ANY EXISTING DATABASE INFORMATION.
	<br><br />To generate the SQL statements without performing any actions, it must end like:
	<br />&nbsp; &nbsp;<a href=\"hs_make_tables.cgi?getsql=1\">\"hs_make_tables.cgi?getsql=1\"</a></b>";
}

my @tables = $dbh->tables();
my %exists;

print "<ul>" if !$silent;
foreach (@tables){
	if ( lc($config->db_driver) eq 'oracle' ){
		my $usr = uc($config->db_user);
		s("$usr".")();
		s("SYS".")();
		s(")();
		}
	if ( lc($config->db_driver) eq 'mssql' ){
		my $dbname = $config->db_database;
		my $usr = lc($config->db_user);
		s("$dbname"."$usr".")();
		s("$dbname"."dbo".")();
		s(")();
		}
	if ( lc($config->db_driver) eq 'postgres' ){
	        next if(/pg_catalog/);
	        next if(/information_/);
		s(public.)();
		s(")();
		}
        if(lc($config->db_driver) eq 'mysql')
        {
              my $dbname = $config->db_database;
              s(`$dbname`.`)();
              s(`)();
        }
        print "<li>$_</li>" if !$silent;
	$exists{lc($_)} = 1; }
print "</ul>" if !$silent;

########################################################################################"
#
#					Build the SQL
#
#########################################################################################
# which tables do we need
my @reg_list = ('user', 'pass', 'dbi_seq1', 'dbi_seq2', 'em', 'grp', 'grpcat', 'imp', 'imp_count','conf');
@reg_list = ('em') if (lc($config->authenticate_method) eq 'client');
my @assessments = split /\s+/, $config->ggr_adv_tables;
push (@assessments, 'pt') if ($config->ptracker_on);
push (@assessments, 'bio') if ($config->biometric_file_pre || $config->biometric_file_post);

my @build_list = (@assessments, @reg_list);
# for each table delete the old, create the new
foreach my $key (@build_list){
	$key = uc($key);
	my @field_list = split /\s+/, $setup_tables{$key}{fields};
	my @create_fields = ();
	my @indices = ();

	foreach my $field (@field_list) {
		my $temp = $field . ' ' . $field_info{$field}{lc($config->db_driver)};
		push @create_fields, $temp;
		if ($field_info{$field}{index}) {push @indices, $field;}
	}

	my $field_data = join ", ", @create_fields;
	my $sql_drop = 'drop table ' . $setup_tables{$key}{name};
	my $sql_create = 'create table ' . $setup_tables{$key}{name} . '(' . $field_data . ')';
	my $primary_create = '';
	my $primary_add = '';
	my $table_name = $setup_tables{$key}{name};

	if ($setup_tables{$key}{primary} ne ''){
		if ( lc($config->db_driver) eq 'mysql') {
			$primary_add = ', PRIMARY KEY (' . $setup_tables{$key}{primary} .')';
			}
		else	{
			$primary_create = 'Alter table ' . $setup_tables{$key}{name} . ' add primary key (' . $setup_tables{$key}{primary} .')';
			}
		}

	my $sql_create = 'create table ' . $setup_tables{$key}{name} . '(' . $field_data . $primary_add . ')';

	if ( lc($config->db_driver) eq 'oracle' ){
		$sql_drop = uc($sql_drop);
		$sql_create = uc($sql_create);
		$primary_create = uc($primary_create);
		$table_name = uc($table_name);
		}
	print "<P><DL>\n" if !$silent;
	    print "<DT><B>Table: $setup_tables{$key}{desc}...</B>\n" if !$silent;

	if ( ($exists{lc($table_name)}==1) && ($overwrite==1)){
		print "<br>Dropping $setup_tables{$key}{name}....\n" if (!$silent);
		if($getsql) {$sql .= "\n$sql_drop;"; }
		else { eval { $dbh->do("$sql_drop") }; }

		print "<br><b>Dropping $setup_tables{$key}{name} failed: $@ </b>" if $@ && !$silent;
		$exists{lc($table_name)} = 0;
	}

	if(!$exists{lc($table_name)}) {
		print "<br>creating $setup_tables{$key}{name}" if (!$silent);

			if($getsql) {$sql .= "\n$sql_create;"; }
			else {
				my $results = $dbh->do($sql_create) or die "execute failed:  $DBI::errstr\n$key - $sql_create\n";
			}

		if ( $primary_create ){
			print "<br>creating primary key for $setup_tables{$key}{name}" if (!$silent);

			if($getsql) {$sql .= "\n$primary_create;"; }
			else {
				my $results = $dbh->do($primary_create) or die "execute failed:  $DBI::errstr\n$key - $primary_create\n";
			}
		}
	}

	foreach (@indices) {
		next if $_ eq $setup_tables{$key}{primary};
		print "<br />Adding index ${table_name}_$_ to $setup_tables{$key}{name}" if !$silent;
		my $idx_sql = "CREATE INDEX ${table_name}_$_ ON $table_name ($_)";

		if($getsql) {$sql .= "\n$idx_sql;"; }
		else {
			my $results = $dbh->do($idx_sql) or print "<br>&nbsp; &nbsp; Could not add index ${table_name}_$_: " . print DBI::errstr if (!$silent);
		}
	}

	print "</P></DL><P>\n" if !$silent;
}

if ( lc($config->db_driver) eq 'mysql') {
	print "<B>Creating Indexes</b><br /> " if !$silent;
	my @sql_index;
	@sql_index = ('CREATE INDEX hs_hradata_hs_uid ON hs_hradata (hs_uid);',
			'CREATE INDEX hs_hradata_adate ON hs_hradata (adate);',
			'CREATE INDEX hs_hradata_site ON hs_hradata (site);',
			'CREATE INDEX hs_hradata_first_name ON hs_hradata (first_name);',
			'CREATE INDEX hs_hradata_last_name ON hs_hradata (last_name);',
			'CREATE INDEX hs_hradata_bYear ON hs_hradata (bYear);',
			'CREATE INDEX hs_hradata_Personal_Sex ON hs_hradata (Personal_Sex);',
			'CREATE INDEX hs_hradata_ts ON hs_hradata (ts);',
			'CREATE INDEX hs_ghadata_hs_uid ON hs_ghadata (hs_uid);',
			'CREATE INDEX hs_ghadata_adate ON hs_ghadata (adate);',
			'CREATE INDEX hs_ghadata_site ON hs_ghadata (site);',
			'CREATE INDEX hs_ghadata_first_name ON hs_ghadata (first_name);',
			'CREATE INDEX hs_ghadata_last_name ON hs_ghadata (last_name);',
			'CREATE INDEX hs_ghadata_bYear ON hs_ghadata (bYear);',
			'CREATE INDEX hs_ghadata_Personal_Sex ON hs_ghadata (Personal_Sex);',
			'CREATE INDEX hs_ghadata_ts ON hs_ghadata (ts);',
			'CREATE INDEX hs_crcdata_hs_uid ON hs_crcdata (hs_uid);',
			'CREATE INDEX hs_crcdata_adate ON hs_crcdata (adate);',
			'CREATE INDEX hs_crcdata_site ON hs_crcdata (site);',
			'CREATE INDEX hs_crcdata_first_name ON hs_crcdata (first_name);',
			'CREATE INDEX hs_crcdata_last_name ON hs_crcdata (last_name);',
			'CREATE INDEX hs_crcdata_bYear ON hs_crcdata (bYear);',
			'CREATE INDEX hs_crcdata_Personal_Sex ON hs_crcdata (Personal_Sex);',
			'CREATE INDEX hs_crcdata_ts ON hs_crcdata (ts);',
			'CREATE INDEX hs_drcdata_hs_uid ON hs_drcdata (hs_uid);',
			'CREATE INDEX hs_drcdata_adate ON hs_drcdata (adate);',
			'CREATE INDEX hs_drcdata_site ON hs_drcdata (site);',
			'CREATE INDEX hs_drcdata_first_name ON hs_drcdata (first_name);',
			'CREATE INDEX hs_drcdata_last_name ON hs_drcdata (last_name);',
			'CREATE INDEX hs_drcdata_bYear ON hs_drcdata (bYear);',
			'CREATE INDEX hs_drcdata_Personal_Sex ON hs_drcdata (Personal_Sex);',
			'CREATE INDEX hs_drcdata_ts ON hs_drcdata (ts);',
			'CREATE INDEX hs_fitdata_hs_uid ON hs_fitdata (hs_uid);',
			'CREATE INDEX hs_fitdata_adate ON hs_fitdata (adate);',
			'CREATE INDEX hs_fitdata_site ON hs_fitdata (site);',
			'CREATE INDEX hs_fitdata_first_name ON hs_fitdata (first_name);',
			'CREATE INDEX hs_fitdata_last_name ON hs_fitdata (last_name);',
			'CREATE INDEX hs_fitdata_bYear ON hs_fitdata (bYear);',
			'CREATE INDEX hs_fitdata_Personal_Sex ON hs_fitdata (Personal_Sex);',
			'CREATE INDEX hs_fitdata_ts ON hs_fitdata (ts);',
			'CREATE INDEX hs_gwbdata_hs_uid ON hs_gwbdata (hs_uid);',
			'CREATE INDEX hs_gwbdata_adate ON hs_gwbdata (adate);',
			'CREATE INDEX hs_gwbdata_site ON hs_gwbdata (site);',
			'CREATE INDEX hs_gwbdata_first_name ON hs_gwbdata (first_name);',
			'CREATE INDEX hs_gwbdata_last_name ON hs_gwbdata (last_name);',
			'CREATE INDEX hs_gwbdata_bYear ON hs_gwbdata (bYear);',
			'CREATE INDEX hs_gwbdata_Personal_Sex ON hs_gwbdata (Personal_Sex);',
			'CREATE INDEX hs_gwbdata_ts ON hs_gwbdata (ts);',
			'CREATE INDEX hs_userdata_hs_uid ON hs_userdata (hs_uid);',
			'CREATE INDEX hs_userdata_adate ON hs_userdata (adate);',
			'CREATE INDEX hs_userdata_rank ON hs_userdata (rank);',
			'CREATE INDEX hs_userdata_grpID ON hs_userdata (grpID);',
			'CREATE INDEX hs_userdata_site ON hs_userdata (site);',
			'CREATE INDEX hs_userdata_coach ON hs_userdata (coach);',
			'CREATE INDEX hs_userdata_full_name ON hs_userdata (full_name);',
			'CREATE INDEX hs_userdata_email ON hs_userdata (email);',
			'CREATE INDEX hs_userdata_ts ON hs_userdata (ts);',
			'CREATE INDEX hs_pass_hs_uid ON hs_pass (hs_uid);',
			'CREATE INDEX hs_emaildata_hs_uid ON hs_emaildata (hs_uid);',
			'CREATE INDEX hs_emaildata_site ON hs_emaildata (site);',
			'CREATE INDEX hs_emaildata_email ON hs_emaildata (email);',
			'CREATE INDEX hs_emaildata_ts ON hs_emaildata (ts);');
	foreach (@sql_index) {
		print "<br />$_ " if !$silent;
		if($getsql) {$sql .= "\n$_;"; }
		else {
			my $results = $dbh->do($_) or print "<br>&nbsp; &nbsp; Could not add index ${table_name}_$_: " . print DBI::errstr if (!$silent);}
		}
	}
#######################################################################################
#
#					Test Database
if ( lc($config->db_driver) ne 'mssql' ) {
print "<br />&nbsp;<br /><B>Testing Database</b><br /> " if !$silent;

my $user1 = HealthStatus::User->new();
my $user2 = HealthStatus::User->new();
my @assessments = @{$$config{common_assessments}};
my @list = $user1->attributes;
my @assessment = @{$$config{common_assessments}};
#$db->init_seq();
my @sex = ('female','male');
foreach my $assessment(@assessment)
	{
	foreach my $sex (@sex)
		{
		print "$assessment - $sex  creating<br />" if !$silent;
		my $dumpfile = $config->conf_auth_dir.'/'.$assessment.'_dump_of_'.$sex.'.user';
		print $dumpfile . " being loaded and tested<br />";
		if (!do($dumpfile))
			{
   			my $error = $@ ? $@
			: $! ? $!
			: 'did not return a true value';
   			die("Unable to load dumpfile ". $dumpfile.": $error\n");
			#next;
			}
		$user1 = do $dumpfile;
		bless($user1, "HealthStatus::User");
		$user1->{config} = \%config;
		#delete($user1->{xnum});
		#delete($user1->{db_record});
		#delete($user1->{db_numbder});
		$db1->save_users_assessment( $user1, uc($assessment) );
		$user2->db_id( $user1->db_id);
		$db1->get_users_last_assessment($user2, $config, $assessment);
		my $stipulation = " where xnum =". $user1->db_record." ";
		$db1->delete($Tables{$assessment},$stipulation);
		print "checking<br />" if !$silent;
		foreach (@list)
			{
			next if ($_ eq 'db_ip_address');
			if(defined $user1->{$_} && defined $user2->{$_})
				{
				if($user1->{$_} eq $user2->{$_})
					{
					 next;
					 }
				print '****** >> ERROR keys don\'t match for ';
				print $_;
				print "<br />Notify HealthStatus - (317)-823-2687<br />"
				}
			}
		print "deleted<br />" if !$silent;
		}
	}
}
#################### Insert Default Configuration settings in hs_configuration table
my $config_file = $config->conf_config_dir.'/default_config.conf';
if(-e $config_file) 
{
	my $default = new HealthStatus::Config($config_file);
	my $dbh_default = HealthStatus::Database->new( $config );
	foreach my $key (keys %{$default->{config_data}}) {
		my %new_data=();
		 $new_data{conf_name} = $key;
		 $new_data{conf_value} = $default->{config_data}->{$key};
		 $dbh_default->insert($setup_tables{CONF}{name},\%new_data);
	}
	print "Configuration data has been inserted successfully <br />";
}
else 
{
	print "Default configuration file (".$config->conf_config_dir."/default_config.conf) does not exist <br />";
}
###################
my $where = " where rank = 'admin' ";
my $temp_file_dir = $config->authenticate_dir;
my $temp_file = 'o';
my $approved = HealthStatus::Authenticate->new($config,$temp_file_dir,$temp_file);
$approved->debug_on( \*STDERR  );
my $count = $db1->hs_count('REG',$where);
if($count == 0)
{
	my $user = HealthStatus::User->new();
	my $count1 = 0;
	my $users;
	my @fullname = ( 'HealthStatus Admin', $config->client.' Admin');
	my @email = ( 'websupport@healthstatus.com', $config->email_admin );
	my @group_id = ( 'zz_hs_testing', 'zz_internal_testing' );
	while($count1 < 2)
	{
		$user->{db_id} = setup_user('hsadmin_');
		$user->{auth_password} = $user->{db_id};
		$user->{hs_administration} = 'admin';
		$user->{db_fullname} = $fullname[$count1];
		$user->{db_email} = $email[$count1];
		$user->{db_employer} = $group_id[$count1];
		$user->{db_emailOK} = 1;
		$user->{auth_emailCheck} = 0;

# add other user elements that should be setup for us.... fullname, rank, email, etc....
		my $status = $approved->add( $config, $user);
		while ($status eq 'DUPLICATE')
		{
			$user->{db_id} = setup_user('hsadmin_');
			$user->{auth_password} = $user->{db_id};
		 	$status = $approved->add( $config, $user);
		}
		print "Admin account added: $status <br />" if !$silent;

	if($count1==0)
	{
		$users .= "Admin-Username = ".$user->{db_id}."\n";
		$users .= "password-Admin = ".$user->{db_id}."\n";
	}
	if($count1==1)
	{
		$users .= "Client-Username = ".$user->{db_id}."\n";
		$users .= "password-Admin = ".$user->{db_id}."\n";
	}
	$count1++;
	}

# we want a fixed location so the user doesn't put this in an insecure location, so use $config->conf_config_dir as the directory.
# and name it

	my $file = $config->conf_config_dir."/admin_user.conf";
	open(FILEHANDLE, ">$file") or die "cannot open file for reading: $!";
	print FILEHANDLE "$users \n";
	close(FILEHANDLE);
	print "file with admin logins has been created at the following location:  <br />";
	print $file." <br />";
	my %mail = (       To      => 'websupport@healthstatus.com',
			From    => $config->email_admin,
			Subject => 'Database Setup for '. $config->client,
			Message => "$users created, summary file at $file",
			smtp   => $smtp
		 );
	sendmail(%mail);
	carp("Couldn't send email: $Mail::Sendmail::error")
		if $MAIL::Sendmail::error;

}
else
{
	print "There is already a user with admin privileges <br />";
}

$approved->debug_off(  );

#######################################################################################
#
#					Bootstrap
	print "</P></DL><P>Bootstrapping sequence numbers</p>\n" if !$silent;

	my $sequence = new DBIx::Sequence({ dbh => $dbh });
#	$sequence->Bootstrap($Tables{REG},$Tables{REG},'unum');
	foreach (@assessments){
#		$sequence->Bootstrap($Tables{$_},$Tables{$_},'xnum');
		}

	print "</P>\n" if !$silent;

#######################################################################################
#
#					End of Page
my $tempdb = $config->db_database;

if(!$getsql) {
	if($overwrite) {$msg = "Your HealthStatus tables were created successfully in database $tempdb.";}
	else {$msg = "Your HealthStatus tables were indexed successfully in database $tempdb.";}
}
else {$msg = "SQL Generated.";}

print "<CENTER><BIG><B>$msg</B></BIG></CENTER><P>Please remove this script from public access.</p></FONT></BODY></HTML>\n" if !$silent;

if($getsql) {
	print "Content-Type: text/plain\n\n";
	$sql = "-- HealthStatus Table Generation --\n" . $sql;
	print $sql;
}

if($db1) {$db1->disconnect}
if($dbh) {$dbh->disconnect}
if($dbh_default) {$dbh_default->disconnect}
exit;

sub setup_user {
	my ($prefix) = @_;
	my @alphanum = ( 0 .. 9);
	my $random = join('', map($alphanum[rand($#alphanum)],(1..4)));
	my $username = $prefix.$random;
	return $username;

}
