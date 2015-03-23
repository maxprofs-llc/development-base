#!/usr/local/bin/perl

use File::Basename        qw( dirname );
use File::Spec::Functions qw( rel2abs );

use lib dirname(rel2abs($0)),'.','/usr/local/www/vhosts/managed2/modules/pdf', '/usr/local/www/vhosts/managed2/modules';

if (!do('assessment_language.tmpl')) {
   my $error = $@ ? $@
             : $! ? $!
             : 'did not return a true value';
   die("Unable to load language.tmpl: $error\n");
}
use Data::Dumper;
#my @array = map [ values %{ $lang{$_}{english} } ], keys %lang;
my @array=map {  my $x=$_;[map { $lang{$x}{$_} } keys %{$lang{$x}} ]  } keys %lang;
print STDERR Dumper(@array);
foreach my $find (@array ) {
    #print "key : $find <br>";
    #print $find."\n";
	}
