#!/usr/bin/perl
use strict;

use CGI qw(:standard);
use JSON;
print header('application/json');
my %hash ;
$hash{assess_date} = 'manoj';
print STDERR "helloG";
my $json_text = to_json(\%hash);
print $json_text;

