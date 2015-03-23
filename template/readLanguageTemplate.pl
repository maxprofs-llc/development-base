#!/usr/local/bin/perl

use File::Basename        qw( dirname );
use File::Spec::Functions qw( rel2abs );

use lib dirname(rel2abs($0)),'.','/usr/local/www/vhosts/managed2/modules/pdf', '/usr/local/www/vhosts/managed2/modules';

if (!do('/usr/local/www/vhosts/managed2/language.tmpl')) {
   my $error = $@ ? $@
             : $! ? $!
             : 'did not return a true value';
   die("Unable to load language.tmpl: $error\n");
}


foreach my $find (sort keys %{$lang{english}} ) {
    #print "key : $find <br>";
    print '"'.$find.'","'.$lang{english}{$find}.'"'."\n";
	}
