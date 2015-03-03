#!/usr/local/bin/perl
# $Id: calculator.cgi,v 1.2 2003/04/06 21:50:30 healthst Exp $

#use strict;

use lib qw(.);
use subs qw(get_calorie_data commify);

use Fcntl qw(:seek :flock);
use File::Spec;

BEGIN { require "/usr/local/www/vhosts/managed2/base/cgi-bin/hs/adv_calculators.pl"; }

=head1 NAME

adv_calculator.cgi

=head1 SYNOPSIS

call as a CGI script

=head1 DESCRIPTION

Each calculator is represented by a subroutine (from calculators.pl).
This script wraps a CGI interface around them.

=head1 INPUT

The input comes from the HTML form.  Some the of input
form names are used by every calculator:

	config_file	    name of configuration file
	debug           some true value for debugging output
	calculator      the name of the calculator
	units           type of measurements being input
	                Metric or Imperial (default is Imperial)

Each calculator uses additional input form names which
we document before each calculator.  The valid calculator
names are

	bac		blood alcohol
	bfc		body fat
	bfn     navy body fat
	bfb     body fat (both at same time)
	bmi		body mass
	cbc		calorie calculator
	dee		daily caloric requirements
	fsz		frame size
	iwc		ideal weight
	lbm		lean body mass
	lop		lose one pound
	lok     lose one kilogram
	smc		cigarette cost
	thr		target heart rate
	whr		waist hip ratio
	due     delivery due date
	ovu     ovulation calendar

The name of the configuration file in C<config_file> is combined
with the hard-coded value of the configuration directory in
C<$Config_dir>.  This script uses the following configuration
values:

	directory       directory to find output templates. it should
                        end with a directory separator.
    default_out     the template to use if a calculator specific template
                        is not found
	write_stats     a true value if we should write stats
	stats_file      the file in which to store the stats. it should
	                    be an absolute path
	banner          a true value if we should include a banner ad
	referrers       a space separated list of valid referrers
	error_form      the template to use for error output.  it should
                        be an absolute path.
    hs_root         directory to find the input forms. it should
                        end with a directory separator.
    link_dir        url to the directory with the input forms.
    partner         your website without the http://

=head2 Sample configuration file

	directory    ../output/
	default_out  hs_calc.tmpl
	partner      www.howismyhealth.com
	referrers    howismyhealth.com howismyhealth.com 209.95.107.139
	write_stats  1
	banner       0
	stats_file   /usr/local/www/secure2k/data/calcshow.txt
	error_form   /usr/local/www/secure2k/misc/error.tmpl
	hs_root      /usr/local/www/howismyhealth.com/docs
	link_dir     http://www.howismyhealth.com

=head1 OUTPUT

The scripts looks for an output template in the directory
specified in the configuration value C<directory>.  The
file name is formed from the name of the calculator and
the string C<_out.html>.  For example, the output template
for the calculator C<lbm> would be C<lbm_out.html>.  If this
template is not located the template specified in
C<default_out> is used.

=head2 Errors

If an error occurs, the scripts does its best to recover and
provide some sort of meaningful response.  It  looks for
the file specified in the configuration directive C<error_form>.

=cut

use subs qw(form_error MALE METRIC KG_TO_LBS);
use vars qw(%Jumps);

use CGI qw(:standard -no_xhtml -debug);
use CGI::SSI;
use CGI::Carp qw(fatalsToBrowser);
use ConfigReader::Simple;
use Cwd;
use Fcntl qw(:flock);
use Text::Template;
use URI;
use Carp;

use constant COOKIE    => 'calcs';
use constant COOKIE1    => 'hs_calc';

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# get input variables, and add a few of our own
my $input = CGI->new();
my %input = $input->Vars();

my $DEBUG = $ENV{HS_DEBUG} || $input{debug} || 0;

if( $DEBUG )
	{
	print "Content-type: text/plain\n\n";
	foreach my $key ( sort keys %input )
		{
		print "\t$key\t\t$input{$key}\n";
		}
	}

my $cookie1 = cookie( COOKIE1 );
my $cookie;
{
$cookie = cookie( COOKIE );
print "cookie is [$cookie] and cookie1 is [$cookie1]\n" if $DEBUG;
read_cookie( \%input, $cookie );
}

$input{'lang'} = lc $input{'lang'};
$input{'calculator'} = lc $input{'calculator'};
print "Calculator is $input{'calculator'}\n" if $DEBUG;
$input{'config_dir'} = '/usr/local/www/vhosts/managed2/base/conf/';
my $snum = $input{'snum'};

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# create a closure to wrap the form_error subroutine so we can make
# the code simpler later.
my $error = do { my $ref = \%input; sub {
	form_error( { %$ref, ERROR_MSG => $_[0], ERROR_TITLE => $_[1] } )
	} };

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
{
my( $year, $month, $day ) = ( localtime )[5,4,3];
$input{date} = sprintf "%04d-%02d-%02d", $year + 1900, $month + 1, $day;
}
print "Date is $input{'date'}\n" if $DEBUG;

$input{referrer} = $ENV{HTTP_REFERER} || '';
print "Referrer is $input{'referrer'}\n" if $DEBUG;

# read configuration file
$input{_sub_file} = $input{'config_dir'};
$input{_sub_file} .=  $input{snum} || $ENV{HS_SUB_CONF} || "advc_000000";
$input{_sub_file} .= ".conf";
$input{_config_file} = $input{'config_dir'};
$input{_config_file} .=  $ENV{HS_CALC_CONF} || "advanced_calc.conf";
print "Config files are $input{_config_file}, $input{_sub_file}\n" if $DEBUG;
$error->( 'Invalid configuration name', "Invalid configuration file - $input{_config_file} - $input{_sub_file}" )
	unless -f $input{_config_file};

$input{_config} = ConfigReader::Simple->new_multiple(Files => [  $input{_config_file} , $input{_sub_file} ] );
print "Config is $input{_config}\n" if $DEBUG;

$input{config} = $input{_config};

$error->( 'Could not read configuration', "Invalid configuration file - $input{_config_file} - $input{_sub_file}" )
	unless UNIVERSAL::isa( $input{_config}, 'ConfigReader::Simple' );
print "Config file read\n" if $DEBUG;

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# do the calculation
$error->( "Unknown calculator [$input{calculator}]", "Invalid calculator" )
   unless exists $Jumps{ $input{'calculator'} };
print "Calculator valid\n" if $DEBUG;

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# add a couple of config items to the input hash,
# so we can get to them in templates
{
my @keys = qw(directory link_dir hs_root partner header_file
		footer_file css cgi java cells_title cells_even
		cells_odd menu_page template_set other_link faq graphic_group image_host
		menu_page html color_set input_variables wholesome);
@input{ @keys } = map { $input{_config}->$_ } @keys;
}


# what have we got?
print join( "\n", map { "$_ - $input{$_}" } keys %input ) if $DEBUG;

$error->() unless $Jumps{ $input{'calculator'} }->( \%input );
print "Back from processing\n" if $DEBUG;

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# write statistics
# we need the seesion id that the cookie decides, so we have to
# make the cookie first
my $cookie = make_cookie( \%input );

write_stats( \%input ) if $input{_config}->write_stats;

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# load and output template
my $directory = File::Spec->canonpath( $input{_config}->directory )
	|| File::Spec->curdir;

my $template = File::Spec->catfile(
	$directory, "$input{'calculator'}_out.html"
	);
print "Template is $template\n" if $DEBUG;

my $file = $input{_config}->default_out || "adv_calc.tmpl";

$template = File::Spec->catfile( $directory, $file ) unless -f $template;

print "Current working directory is ", cwd(), "\n" if $DEBUG;
print "Template is $template\n" if $DEBUG;

$error->( 'Could not read template file', 'Could not read template file' )
	unless -f $template;
my $data = Text::Template::fill_in_file( $template, HASH => \%input );
$error->( $Text::Template::ERROR, 'Template file error' )
	if $Text::Template::ERROR;

my $ssi = CGI::SSI->new();

my $html = $ssi->process($data);

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# print the data
print header( -cookie => $cookie, -expires => 'now' ), $html;

=head2 Subroutines

=over 4

=item write_stats( HASH_REF )

Logs the transaction information to the file in the configuration
directive C<stats_file>.  The data are double pipe delimited.

	session -- from cookie value
	date
	partner
	calculator
	banner_desc
	sex
	age
	bmi
	height
	weight
	waist
	preferred_body_fat
	referrer

=cut

sub write_stats
	{
	my( $hash ) = @_;

	my $file = $hash->{_config}->stats_file;

	open  STATS, ">> $file" or return;
	flock STATS, LOCK_NB;
	seek  STATS, 0, SEEK_END;

	my $record = join "||" ,
		map { defined $_ ? $_ : '' }
			@{$hash}{ qw(session date partner calculator banner_desc
			sex age bmi height weight waist preferred_body_fat referrer) };

	print STATS $record, "\n";

	close STATS;
	}

BEGIN {
%Jumps = (
        alcohol =>\&alcohol_calc,
        adultsr =>\&adult_sr,
        copdas => \&copd_as,
        copddx => \&copd_dx,
        dmdi   => \&dmdi,
        dwho => \&dwho,
        edisorder => \&edisorder,
        lbp => \&lbw,
        lbw => \&lbw,
        lexercise => \&leisure_exercise,
        motionsick => \&motion_sick,
        vod => \&vod,
	);
}

=item make_cookie

Create the cookie for this transaction.  If the script was called
with a cookie (for this script), the new cookie uses the session
identifier from the old cookie.

The cookie name is C<calcs>

The cookie value is a double pipe delimited list of these values:

	sex         1 for Male, 0 for Female
	age
	units       1 for Metric, 0 for Imperial
	weight      kilograms for metric, pounds for imperial
	height      inches for either system
	waist
	bmi
	bfc
	smoker      1 if used smoking calculator, 0 otherwise
	session     the time the first cookie was made, with the
	            process-id of the first CGI script access


The cookie expires at the end of the browser session.

The default path and domain come from CGI::cookie() which
chooses the right values.

=cut

sub make_cookie
	{
	my $hash = shift;

	my $session = $hash->{session} || time . $$;

	my $gender = $hash->{sex} eq MALE ? 1 : 0;
	my $units  = $hash->{units} eq METRIC ? 1 : 0;
	my $height = $hash->{height} || $hash->{mheight};
	my $smoker
		= $hash->{smoker} || $hash->{calculator} eq 'smc' ? 1 : 0;

	my $value = join "||", map { defined $_ ? $_ : '' }
		$gender, $hash->{age}, $hash->{units},
		$hash->{weight}, $height, $hash->{waist}, $hash->{bmi},
		$hash->{bfc}, $smoker, $session;

	my $cookie = cookie(
		-name  => COOKIE,
		-value => $value,
		-path  => '/',
		);

	return $cookie;
	}

=item read_cookie

Read the C<calcs> cookie value and reset the smoker and session
values.

=cut

sub read_cookie
	{
	my $hash  = shift;
	my $value = shift;

	if(!$value){return}
	my @bits = split (/\|\|/, $value);

	my $session = $bits[-1];

	$hash->{smoker}  = $bits[-2] ||  0;
	$hash->{session} = $session  || '';
	}

sub commify # from perlfaq5
	{
	my $number = shift;
	1 while ($number =~ s/^([-+]?\d+)(\d{3})/$1,$2/);
	return $number;
	}

sub form_error
	{
	my $hash = shift;

	use CGI qw(:standard -no_xhtml -debug);

	print header();

	my $data;

	$hash->{ERROR_MSG}   ||= "Sorry, an unexpected error occurred. $hash->{'cycle'}";
	$hash->{ERROR_TITLE} ||= 'UNEXPECTED ERROR';
	$hash->{ERROR_NAME}  ||= $hash->{ERROR_TITLE};

	while( my( $k, $v ) = each %{ $hash->{'ERROR_FIELDS'} } )
		{
		$hash->{hidden} .= hidden( $k, $v );
		}

	unless( exists $hash->{_config} and
		UNIVERSAL::can( $hash->{_config}, 'error_form' ) )
		{
		print <<"HTML";
<html>
<head><title>$$hash{ERROR_TITLE}</title></head>
<body><h1>$$hash{ERROR_TITLE}</h1>
$$hash{ERROR_MSG}
</body>
</html>
HTML
		}
	else
		{
		my $file = $hash->{_config}->error_form;

		print "ERROR Template is $file\n" if $DEBUG;

		$data = Text::Template::fill_in_file( $file,
			HASH => $hash );

		$data ||= '';
		}

    print $data;

    exit 1;
	}

=back

=head1 BUGS

* nothing identified

=head1 TO DO

=head1 SEE ALSO

calculators.pl, calorie_data.pl, banners.pl

=head1 AUTHOR

brian d foy <bdfoy@cpan.org>
Greg White <gwhite@healthstatus.com>

=head1 COPYRIGHT

Copyright 2001-2002, HealthStatus.com

=cut
