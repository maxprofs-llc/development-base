#!/usr/local/bin/perl

use strict;

=head1 NAME

fitme.cgi - web pretest for Fitness Assessment

=head1 SYNOPSIS

=head1 DESCRIPTION

=head2 Expected input


=head2 Output

The output is the filled-in template for the specified
format in output_format, preceded by an appropriate
CGI header.

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

use HealthStatus qw ( error html_error fill_and_send );
use HealthStatus::Constants;

my $input = new CGI();
my $config = getConfig($input->param('extracfg'));

my %hash = map { $_, $input->param($_) } $input->param();

my %config = map { $_, $config->$_ } $config->directives;

$hash{config} = \%config;

my $sid = $input->cookie('hs_ident');
my $session = new CGI::Session($sid) or die CGI::Session->errstr;

# authenticate_user redirects the user if they not allowed to
# view this page
my $user = authenticateUser('all', $input, $config) or die "You should never see this message.";
if($input->param('page') == 0 && !$config->{prepopulate}) {
	$session->clear();
	}
if($input->param('page') == 0 && $config->prepopulate) {
	foreach my $assess(@{$$config{common_assessments}}){
		my $db = HealthStatus::Database->new( $config );
			my $status = $db->get_users_last_assessment($user, $config, $assess);
			if($status){
				my @list=$user->attributes;
				foreach my $list (@list){
					print $list." = ".$user->{$list}."\n" if $Debug;
					$session->param($list,$user->{$list}) unless (substr $list,0,4 eq 'auth' || substr $list,0,2 eq 'db' || substr $list,0,5 eq 'batch');
					}
				}
		$session->load_param($input);
		$db->disconnect;
		}
}
if($input->param('page') != 0){ $session->clear('page'); }
if($input->param('page') != 0 && $input->param('assessment') eq "FIT") {
	$session->save_param($input,["first_name", "last_name", "birth_month", "birth_date", "birth_year", "sex", "height", "weight", "waist", "units"]);
	$session->load_param($input);
	}
my %input = $input->Vars();

delete($hash{'Submit.x'}) if (exists($hash{'Submit.x'}));
delete($hash{'Submit.y'}) if (exists($hash{'Submit.y'}));
delete($hash{'action'}) if (exists($hash{'action'}));


if ($Debug) {
	print "Content-type: text/plain\n\n";
	print "$ENV{SCRIPT_NAME} - $ENV{QUERY_STRING}\n";
	print "Modules Versions:\nHealthStatus - $HealthStatus::VERSION\nHealthStatus::Authenticate - $HealthStatus::Authenticate::VERSION\nHealthStatus::Database - $HealthStatus::Database::VERSION\n";
	print "HealthStatus::Config - $HealthStatus::Config::VERSION\nHealthStatus::User - $HealthStatus::User::VERSION\n\n";
	$config->pretty_print;
	$user->pretty_print;

}

my $cleared = $input->param('Cleared');
my $page = $input->param('page');
my $language = $input->param('language');
my %configlist = ();

foreach my $key ( $config->directives )
	{
	$configlist{$key} = $config->$key;
	}

my %vars = ( 'config' => \%configlist );

foreach my $key ( $user->attributes ) { $vars{$key} = $user->get($key) }

if($page eq 'fit1.html' || $page eq 'fit_pre.html') {

	my $templte = $config->template_directory . $page ;

	fill_and_send( $templte, $user, \%vars, $config->html_use_ssi );

	exit;
}else{
	if(	($input->param('C1') eq 'ON')||
		($input->param('C2') eq 'ON')||
		($input->param('C3') eq 'ON')||
		($input->param('C4') eq 'ON')||
		($input->param('C5') eq 'ON')||
		($input->param('C6') eq 'ON')||
		($input->param('C7') eq 'ON')||
		($input->param('C8') eq 'ON')||
		($input->param('C9') eq 'ON')){

			my $templte = $config->template_directory . "fit_not.html";

			fill_and_send( $templte, $user, \%vars, $config->html_use_ssi );

			exit;
	}else{
		$cleared = 'ON';
	}
	if ($cleared ne 'ON'){
		my $redir = $config->member_page ;

		print $input->redirect(-uri => $redir );
	}else{
		my $qset = "_" . $input->param('qset') if ($input->param('qset')  && lc($input->param('qset')) ne 'imperial');
		my $template = $config->template_directory . 'fit' . $qset . "_qset.html";

		# pass along all of the data in hidden fields
		$hash{curr_page} = 1;
		$hash{page} = 1;

		foreach my $key ( $user->attributes ) { $hash{$key} = $user->get($key) }

		fill_and_send( $template, $user, \%hash, $config->html_use_ssi );
	}
}

=head1 BUGS

=head1 TO-DO

=head1 SEE ALSO

L<HealthStatus>,
L<HealthStatus::User>,
L<HealthStatus::FIT>,
L<CGI>

=head1 AUTHOR

	Greg White, HealthStatus.com <gwhite@healthstatus.com>

=head1 COPYRIGHT

	Copyright 1999-2007 HealthStatus.com, Inc., all rights reserved

=cut
