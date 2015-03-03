#!/usr/local/bin/perl
use strict;
use CGI::Carp;
use File::Basename        qw( dirname );
use File::Spec::Functions qw( rel2abs );

use lib dirname(rel2abs($0)),'.','/usr/local/www/vhosts/managed2/modules/pdf', '/usr/local/www/vhosts/managed2/modules';

use warnings;
use Net::SFTP;

my $host = 'ec2-54-85-108-184.compute-1.amazonaws.com';
my %args = ( user     => 'manoj',
             password => 'Sojg68',
             debug    => '1');
             
my $sftp = Net::SFTP->new( $host, %args );
$sftp->put('/vhosts/managed2/base/cgi-bin/api/api_mchcp.cgi',
           '/var/www/mobile/');

exit;