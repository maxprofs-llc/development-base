#!/usr/local/bin/perl

use strict;

=head1 NAME

logout.cgi - Log out process

=head1 SYNOPSIS

=head1 DESCRIPTION

=head2 Expected input


=head2 Output

This will read the users ID redirect them to the specified logout page and
delete the authentication file.

=cut

use File::Basename        qw( dirname );
use File::Spec::Functions qw( rel2abs );

use lib dirname(rel2abs($0)),'.','/usr/local/www/vhosts/managed2/modules/pdf', '/usr/local/www/vhosts/managed2/modules';

use vars qw( $Debug $production $cook $config_file $nph);

if (!do('common.inc')) {
   my $error = $@ ? $@
             : $! ? $!
             : 'did not return a true value';
   die("Unable to load common stuff: $error\n");
}
# Removing warnings in log while module is being used with CGI version 4 or above
$CGI::LIST_CONTEXT_WARN = 0;
use HealthStatus qw ( error html_error fill_and_send );
use HealthStatus::Constants;
use Date::Calc;
use Text::Template;
use Data::Dumper;

my $input = new CGI();
my $config = getConfig($input->param('extracfg'));
my $sid = $input->cookie('CGISESSID');
my $session = new CGI::Session(undef, $sid, {Directory=>'../../sessions'}) or die CGI::Session->errstr;
#my $session = new CGI::Session($sid) or die CGI::Session->errstr;
$session->delete();

##Delete sessions files if exists any
if($sid){
	my $session_dir = "/usr/local/www/vhosts/managed2/base/sessions";	
	opendir DIR, $session_dir or die "Cannot open dir $session_dir: $!";
	for (readdir DIR) {
		next if /^\.{1,2}$/;
		my $path = "$session_dir/$_"; 	
		unlink $path if -f $path;		
	}
	closedir DIR; 	
}
# End of delete session file
	 
my %input = $input->Vars();

# authenticate_user redirects the user if they not allowed to
# view this page
my $user = authenticateUser('all', $input, $config) or die "You should never see this message.";

my $cookie=$input->cookie(-name=>'hs_ident',
       -value=>"",
       -expires=> '-1M');
my $session_cookie=$input->cookie(-name=>'CGISESSID',
       -value=>"",
       -expires=> '-1M');
my $redir = $config->logout_page ;

print $input->redirect(-uri => $redir, -cookie=> [$cookie,$session_cookie] );

sub error
	{
	my $message = shift;
	my $error   = shift;

	print "Content-type: text/plain\n\n$message";

	warn "$message: $error";

	exit 1;
	}


=head1 BUGS

=head1 TO-DO

=head1 SEE ALSO

L<HealthStatus>,
L<HealthStatus::User>,
L<CGI>

=head1 AUTHOR

	Greg White, HealthStatus.com <gwhite@healthstatus.com>

=head1 COPYRIGHT

	Copyright 1999-2008 HealthStatus.com, Inc., all rights reserved

=cut
