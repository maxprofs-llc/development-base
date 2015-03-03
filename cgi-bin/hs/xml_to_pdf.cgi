#!/usr/local/bin/perl

use strict;
use bytes;
use File::Basename        qw( dirname );
use File::Spec::Functions qw( rel2abs );

use lib dirname(rel2abs($0)),'.','/usr/local/www/vhosts/managed2/modules/pdf', '/usr/local/www/vhosts/managed2/modules';

require PDF;

my $xml;
open (XML,"<","/usr/local/www/vhosts/managed2/base/data/m_review_esp.xml");
my @input = <XML>;
foreach (@input){
	$xml .= $_;
	}
PDFDoc->importXML( $xml )->writePDF( );
exit;
