#!/usr/local/bin/perl
# $Id: calc.cgi.PL,v 1.2 2010/03/10 12:10:59 code4hs Exp $

use strict;

use File::Basename        qw( dirname );
use File::Spec::Functions qw( rel2abs );

use lib dirname(rel2abs($0)),'.','/usr/local/www/vhosts/managed2/modules/pdf', '/usr/local/www/vhosts/managed2/modules';

use vars qw( $Debug $production $cook $config_file);

# Removing warnings in log while module is being used with CGI version 4 or above
$CGI::LIST_CONTEXT_WARN = 0;

use Fcntl qw(:seek :flock);
use File::Spec;

BEGIN {require "calorie_data.pl"; }

use subs qw(get_calorie_data commify);

=head1 NAME

calc.cgi

=head1 SYNOPSIS

call as a CGI script

=head1 DESCRIPTION

This script loads a calculator input form, using the correct
template and banners and delivers it to the user via the browser.

=head1 INPUT

The input comes from the HTML form.  Some the of input
form names are used by every calculator:

	snum     	subscriber number
	hs_debug        some true value for debugging output
	calc	        the name of the calculator

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

use HTML::FillInForm;
use CGI qw(:standard -no_xhtml -debug);
use ConfigReader::Simple;
use Cwd;
use Fcntl qw(:flock);
use Text::Template;
use URI;
use CGI::SSI;
use Carp;
use CGI::Session;

my $ssi = CGI::SSI->new();

use constant COOKIE    => 'calcs';
use constant COOKIE1    => 'hs_calc';

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# get input variables, and add a few of our own
my $input = CGI->new();
my %input = $input->Vars();

my $session = new CGI::Session(undef, undef, {Directory=>'../../sessions'}) or die CGI::Session->errstr;
$session->save_param();

my $DEBUG = $ENV{HS_DEBUG} || $input{HS_Debug} || 0;

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
$cook = $input->param('hs_ident') || $input->cookie('hs_ident');
print STDERR "\ncookie is=====$cook";
$input{cookie} = $cook;
$input{'calc'} = lc $input{'calc'};
$input{'calculator'} = $input{'calc'};
print "Calculator is $input{'calc'}\n" if $DEBUG;

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
print "Referrer is [$input{'referrer'}] - [$ENV{HTTP_REFERER}]\n" if $DEBUG;

# read configuration file
my $extraconfig;
my $domain = $ENV{SERVER_NAME};
my @domain_parts = split /\./,$domain;
my $subdomain = $domain_parts[0];		
$extraconfig = $subdomain . '_calc.conf';
# $input{_sub_file} = $input{'config_dir'};
# $input{_sub_file} .=  $input{snum} || $ENV{HS_SUB_CONF} || "000000";
$input{_sub_file} .= $input{'config_dir'}.$extraconfig;
$input{_config_file} = $input{'config_dir'};

$input{_config_file} .=  $ENV{HS_CALC_CONF} || "calculator.conf";
print "Config files are $input{_config_file}, $input{_sub_file}\n" if $DEBUG;
#$error->( 'Invalid configuration name', "Invalid configuration name - $input{_sub_file} - $input{_config_file}" )
#	unless -f $input{_config_file};

$input{_config} = ConfigReader::Simple->new_multiple(Files => [  $input{_config_file} , $input{_sub_file} ] );
print "Config is $input{_config}\n" if $DEBUG;

$input{config} = $input{_config};

$error->( 'Could not read configuration', "Invalid configuration name x $input{_sub_file} x $input{_config_file}" )
	unless UNIVERSAL::isa( $input{_config}, 'ConfigReader::Simple' );
print "Config file read\n" if $DEBUG;

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# do the calculation
$error->( "Unknown calculator [$input{calc}]", "Invalid calculator" )
   unless exists $Jumps{ $input{'calc'} };
print "Calculator valid\n" if $DEBUG;


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# add a couple of config items to the input hash,
# so we can get to them in templates
{
my @keys = qw(directory link_dir hs_root partner header_file 
		footer_file css cgi java cells_title cells_even
		cells_odd menu_page template_set other_link faq 
		menu_page html color_set input_variables wholesome graphic_group base brand_logo client);
@input{ @keys } = map { $input{_config}->$_ } @keys;
}

$input{'siteid'} = $session->param('siteid');
$input{'lang'} = lc $input{'lang'};

if ($input{'calc'} eq 'ova' || $input{'calc'} eq 'due' ) {
	$input{cycle} = $input{month} . "/" . $input{day} . "/" . $input{year};
	}

$input{db_id} = $session->param('db_id');

# what have we got?
print join( "\n", map { "$_ - $input{$_}" } keys %input ) if $DEBUG;

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# choose an ad banner
if( $input{_config}->banner )
	{
	require "banners.pl";
	my $html =  pick_banners( \%input ) ;
	$input{'banner1'} = $html->[0];
	$input{'banner2'} = $html->[1];
	$input{'banner3'} = $html->[2];
	}

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# load and output the input form
my $directory = File::Spec->canonpath( $input{_config}->directory.$input{_config}->template_set."/" )
	|| File::Spec->curdir;

my $template;
if( $input{_config}->new_template ){

	print "\nsetting up new template\n" if $DEBUG;	
	my $ttemp = $input{_config}->new_template_name;
	$template = File::Spec->catfile(
			$directory, $ttemp
		);
	print "$directory - $ttemp\n" if $DEBUG;	
	}
else	{
	print "\nusing old template\n" if $DEBUG;	
	$template = File::Spec->catfile(
		$directory, "$input{'calc'}.html"
		);
	}
	
print "Template is $template\n" if $DEBUG;

print "Current working directory is ", cwd(), "\n" if $DEBUG;
print "Template is $template\n" if $DEBUG;

$error->( "Could not read template file - $template", 'Could not read template file' )
	unless -f $template;

my $data = Text::Template::fill_in_file( $template, HASH => \%input );
$error->( $Text::Template::ERROR, 'Template file error' )
	if $Text::Template::ERROR;

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# load the input form variables
my $fif = new HTML::FillInForm;
my $output = $fif->fill(scalarref => \$data, fobject => $input);

my $html = $ssi->process($output);

print header(-expires=>'now'), $html;
exit;

=head2 Subroutines

=over 4

=cut

BEGIN {
%Jumps = (
	bac => \&blood_alcohol,
	bfc => \&body_fat,
	bfn => \&navy_body_fat,
	bfb => \&body_fat_both,
	bmi => \&body_mass,
	cbc => \&calorie_calculator,
	dee => \&daily_caloric_requirements,
	fsz => \&frame_size,
	iwc => \&ideal_weight,
	lbm => \&lean_body_mass,
	lop => \&lose_one_pound,
	lwc	=> \&lose_weight_calorie,
	lok => \&lose_one_kilogram,
	men => menu,
	smc => \&cigarette_cost,
	thr => \&target_heart_rate,
	whr => \&waist_hip_ratio,
	due => \&due_date,
	ova => \&ovulation,
	);
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

	$hash->{ERROR_MSG}   ||= 'Sorry, an unexpected error occurred.';
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

    print header(), $data;

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

Copyright 2001-2005, HealthStatus.com

=cut
