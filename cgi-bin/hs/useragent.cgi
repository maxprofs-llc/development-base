#!/usr/local/bin/perl
    use strict;
    use warnings;
    use LWP::UserAgent;
    use HTTP::Request::Common qw(GET);   

    my $ua = LWP::UserAgent->new;    

    # Request object
    my $req = GET 'https://base1.hra.net';

    # Make the request
    my $res = $ua->request($req);

    # Check the response
    if ($res->is_success) {
        print $res->content;
    } else {
        print $res->status_line . "\n";
    }

    exit 0;