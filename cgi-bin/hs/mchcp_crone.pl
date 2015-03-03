#!/usr/local/bin/perl
use strict;

=head1 NAME
mchcp_crone.cgi - update GHA table for missing inches field value from temp table
=cut
use File::Basename        qw( dirname );
use File::Spec::Functions qw( rel2abs );

use lib dirname(rel2abs($0)),'.','/usr/local/www/vhosts/managed2/modules/pdf', '/usr/local/www/vhosts/managed2/modules';

use HealthStatus;
use DBI;
use Data::Dumper;

my $dbh  =  DBI->connect('dbi:mysql:hs_mchcptest_data:local-db.healthstatus.com', 'As!an9books', 'hrX1hs0' );

my @existing_column_db;
my @hs_uids;
my $column_str = "SHOW COLUMNS FROM hs_ghadata";
my $fields_from_db = $dbh->prepare($column_str);
$fields_from_db->execute();
 while (my @row = $fields_from_db->fetchrow_array()) {
	next if($row[0] eq 'hs_uid' || $row[0] eq 'unum' || $row[0] eq 'xnum' || $row[0] eq 'adate');
	push(@existing_column_db, $row[0]); 
}
print STDERR "Wait while processing....\n";
my (%inches_hs_uids,@inches_uids);
my $inches_str = "SELECT * FROM hs_ghadata WHERE Inches IS NULL"; 
my $hsuid_from_gha = $dbh->prepare($inches_str);
$hsuid_from_gha->execute();
 while (my $hs_uid = $hsuid_from_gha->fetchrow_hashref()) {	
	my @column_ref ;
	
	foreach(@existing_column_db){
		if(!$hs_uid->{$_}){
			push(@column_ref,$_);
		}
	}
	$inches_hs_uids{$hs_uid->{hs_uid}}= \@column_ref; 
}	 
	
foreach my $hsuid( keys %inches_hs_uids) {		
	my $select_temp_str = "SELECT * FROM hs_tmp_ghadata WHERE hs_uid = $hsuid";
	my $column_from_tempgha = $dbh->prepare($select_temp_str);
	$column_from_tempgha->execute();
	my $qry;		
	while (my $hs_uid = $column_from_tempgha->fetchrow_hashref()) {		
		foreach(@{$inches_hs_uids{$hsuid}}){			
			if($hs_uid->{$_}){
			$qry .= "$_='$hs_uid->{$_}',";
			}
		}
	}
	if($qry){
		 chop($qry);
		 my $update_str = "UPDATE hs_ghadata set $qry WHERE hs_uid=$hsuid ";			
		 my $update_db = $dbh->prepare($update_str);
		 $update_db->execute();
		 #print STDERR "Updated record for hs_uid : $update_str\n";			
		}
}	


print STDERR "...processing completed\n";
$dbh->disconnect;

