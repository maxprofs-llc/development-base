#!/usr/local/bin/perl
use strict;

if (!do('common.inc')) {
   my $error = $@ ? $@
             : $! ? $!
             : 'did not return a true value';
   die("Unable to load common stuff: $error\n");
}

use HealthStatus::CalcRisk;
use HTML::Lint;

my $input = new CGI();
my $config = getConfig($input->param('extracfg'));

my ($data, $got_it, $assessment, $health, $page, $template, $template_name);

############################################################################
### Comment out the following line before going into production ############
$Debug = $input->param("HS_Debug") || $ENV{HS_DEBUG} || 0;
#### only uncomment if you need to debug the input scripts      ############
############################################################################

print "Content-type: text/html\n\n";

$| = 1;

if ($Debug) {
	print "Modules Versions:\nHealthStatus - $HealthStatus::VERSION\nHealthStatus::Authenticate - $HealthStatus::Authenticate::VERSION\nHealthStatus::Database - $HealthStatus::Database::VERSION\n";
	print "HealthStatus::Config - $HealthStatus::Config::VERSION\nHealthStatus::User - $HealthStatus::User::VERSION\n\n";
	$config->pretty_print;
}

# %Allowed_assessments not only tells us which assessments we
# can do, but how many pages of input to expect
my %Allowed_assessments = map
	{
	my $assessment = $_;
	my $method     = "${_}_max_pages";
	my $max_pages  = $config->$method;

	( $assessment, $max_pages )
	} @{$$config{common_assessments}};

my %hash;

my %config = map { $_, $config->$_ } $config->directives;

$hash{config} = \%config;

foreach my $assessment ( sort keys %Allowed_assessments){

	my $io = 'input';

	my $user = HealthStatus::User->new( \%hash );

	$user->pretty_print if $Debug;

	# now grab the user date saved previously
		my $dumpfile = $config->authenticate_dir . "/dump_of_" . $assessment . "_1.user";

		$user = do $dumpfile;

		bless($user, "HealthStatus::User");

		$user->{config} = \%config;

		$user->pretty_print if $Debug;

		++$got_it;

		if(!$got_it) { 	print "Could not locate the assessment data file $dumpfile\n$!\n"; }

		my $pages = $Allowed_assessments{$assessment} ;
		$page=1;
	# this does the input pages
		while ( $page <= $pages ) {

			# set the variable for the next template
			my $qset = "_" . $input->param('qset') if ($input->param('qset'));
			my $template = $config->template_directory . $assessment . $qset . "_qset.html";
			# stay compatible with old template retrieval method (1 file per page)
			unless (-e $template) {
				$template = $config->template_directory . $assessment . "_q$page.html";
				}
			print "template is $template<br>\n" if $Debug;

			my %vars = map { my $x = $_; $x =~ tr/A-Za-z_//c; $x, $input->param($_) }
				$input->param;

			my %config = map { $_, $config->$_ } $config->directives;

			$vars{config} = \%config;
			$vars{page} = $page;

			foreach my $key ( $user->attributes ) { $vars{$key} = $user->get($key) }

			$data = fill_and_return( $template, $user, \%vars, $config->html_use_ssi );

			lint_me($data, $assessment, $page, $io);

			++$page;

			}

	# this does the first page of the report
		$user->set_non_standard;

		my $health = HealthStatus->new(
			{
			assessment => uc($assessment),
			user       => $user,
			config     => $config_file,
			}
			);

		$health->assess( $user );

		my $m_format = $input->param('output_format') || DEFAULT_OUTPUT_FORMAT ;

		$data = $health->output( 'html' );

		my $mime = $health->mime(  lc $m_format );

		if ($config->html_use_ssi){
			require CGI::SSI;
			my $use_ssi = CGI::SSI->new();
			$data = $use_ssi->process($data);
			}

		$io = 'output';
		$page = 1;

		lint_me($data, $assessment, $page, $io);

	# this goes through the rest of the report
		++$page;
		$template = $config->template_directory . $assessment . "_$page.tmpl";

		while (-r $template) {

			print "Template file = $template - $template_name\n" if $Debug;

			# pass along all of the data in hidden fields
			my %vars = map { my $x = $_; $x =~ tr/A-Za-z_//c; $x, $input->param($_) }
				$input->param;
			my %config = map { $_, $config->$_ } $config->directives;

			$vars{config} = \%config;

			$vars{hidden_cgi_fields} = join "\n", map { $input->hidden($_) } $input->param;

			$data = fill_and_return( $template, $user, \%vars, $config->html_use_ssi );

			lint_me($data, $assessment, $page, $io);

			++$page;
			$template = $config->template_directory . $assessment . "_$page.tmpl";

			}
	}

sub lint_me{
	no strict;
	use HealthStatus qw( fill_and_send error html_error );

	my ($data, $assessment, $page, $io) = @_;

        print "Parsing " . uc($assessment) . " - $io - page $page<br>";
        my $lint = HTML::Lint->new;
        $lint->only_types( );
        $lint->parse( $data );

        my $error_count = $lint->errors;

        if ($error_count == 0) {
        	print "no errors<br>" ;
        	}
        else	{
        	print "<b>(Line:Column) Error</b><br>";
        	}

        foreach my $error ( $lint->errors ) {
            my $err_line = $error->as_string;
            print CGI::escapeHTML($err_line);
            print "<br>";
        }

        print "<br> ";
        return;

}

sub fill_and_return
	{
	use HealthStatus qw( fill_and_send error html_error );
	my $form = shift;
	my $user = shift;
	my $other = shift;
	my $ssi  = shift;
	my $ignore = shift;

	my $results;

	require CGI;
	CGI->import( -no_xhtml );
	if ($ssi) { require CGI::SSI; }
	require HTML::FillInForm;

	my $input = CGI->new();
	my %input = $input->Vars();
	my @ignore = ('action','auth_password_entry','auth_password','page');
	if ($ignore) {
		foreach (@$ignore){ push @ignore, $_; }
		}

	foreach my $key ( keys %$other )
		{
		$input{$key} = $other->{$key};
		$input->param("$key","$other->{$key}") if ($key ne 'action');
		}
	foreach my $key ( keys %$user )
		{
		$input{$key} = $user->{$key};
		$input->param("$key","$user->{$key}");
		}

	error( "Could not read template file - $form" )
		unless -f $form;

	my $data = Text::Template::fill_in_file( $form, HASH => \%input );
	error( $Text::Template::ERROR, 'Template file error' )
		if $Text::Template::ERROR;

	my $fif = new HTML::FillInForm;
	my $output = $fif->fill(scalarref => \$data, fobject => $input, ignore_fields => \@ignore);

	if ($ssi){
		my $use_ssi = CGI::SSI->new();
		$results = $use_ssi->process($output);
		}
	else 	{ $results = $output }

	return $results;
	}

=head1 BUGS

* none that i've found so far.

=head1 TO DO

* nothing yet

=head1 AUTHOR

Greg White <gwhite@healthstatus.com>

=head1 COPYRIGHT

Copyright 2001-2004, HealthStatus.com

=cut

1;
