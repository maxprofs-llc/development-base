#!/usr/local/bin/perl

#use strict;

use lib qw(.);
use subs qw(get_calorie_data commify);

use Fcntl qw(:seek :flock);
use File::Spec;

=head1 NAME

reload.pl

=head1 DESCRIPTION

???

=cut

BEGIN{($_=$0)=~s![\\/][^\\/]+$!!;push@INC,$_}

use subs qw(form_error MALE METRIC KG_TO_LBS);
use vars qw(%Jumps);

use HTML::FillInForm;
use Text::Template;
use CGI qw/:standard/;
use CGI::SSI;
use ConfigReader::Simple;
use Cwd;
use Fcntl qw(:flock);
use Text::Template;
use URI;

use constant COOKIE    => 'calcs';
use constant COOKIE1    => 'hs_calc';

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# get input variables, and add a few of our own
my $input = CGI->new();
my %input = $input->Vars();

my $DEBUG = $ENV{HS_DEBUG} || $input{hs_debug} || 0;

my $cookie1 = cookie( COOKIE1 );
{
my $cookie = cookie( COOKIE );
print STDERR "cookie is [$cookie]\n" if $DEBUG;
read_cookie( \%input, $cookie );
}

if( $DEBUG )
	{
	print "Content-type: text/plain\n\n";
	foreach my $key ( sort keys %input )
		{
		print "\t$key\t\t$input{$key}\n";
		}
	}

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
print "Referrer is $input{'referrer'}\n" if $DEBUG;

# read configuration file
$input{_sub_file} = $input{'config_dir'};
$input{_sub_file} .=  $input{snum} || $ENV{HS_SUB_CONF} || "advc_000000";
$input{_sub_file} .= ".conf";
$input{_config_file} = $input{'config_dir'};
$input{_config_file} .=  $ENV{HS_CALC_CONF} || "advanced_calc.conf";
print "Config files are $input{_config_file}, $input{_sub_file}\n" if $DEBUG;
$error->( 'Invalid configuration name', 'Invalid configuration name' )
	unless -f $input{_config_file};

$input{_config} = ConfigReader::Simple->new_multiple(Files => [  $input{_config_file} , $input{_sub_file} ] );
print "Config is $input{_config}\n" if $DEBUG;

$error->( 'Could not read configuration '. $input{_sub_file}, 'Invalid configuration file' )
	unless UNIVERSAL::isa( $input{_config}, 'ConfigReader::Simple' );
print "Config file read\n" if $DEBUG;

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# do a referrer check
{
my $referlist = lc($input{_config}->referrers);
my %Referrers = map { $_, 1 } split /\s+/, $referlist;

my $tmp = 'http://';
$tmp .= $input{_config}->partner;

if( $input{referrer}  )
	{
	my $temp = lc($input{referrer});
	if( $temp =~ m/^(x+):(\++)$/ )
		{
		if($cookie1 =~ m/^hs_calc/){
			print "no referrer but found cookie\n" if $DEBUG;
			}
		else	{
			print "In referrer check - [$temp]\n" if $DEBUG;
			warn "reload.cgi - failed: $cookie1 - $cookie - $input{referrer}";
			print $input->redirect($input{_config}->problem_page);
			}
		}
	else	{
		my $url = URI->new( lc($input{referrer}), "http" );
		my $domain = $url->host;
		print "In else referrer check - [$temp]\n"  if $DEBUG;
		print $input->redirect($tmp)
			unless exists $Referrers{$domain};
		}
	}
elsif( !$input{demo_hs} )
	{
	if($cookie1 =~ m/^hs_calc/){
		print "no referrer but found cookie\n" if $DEBUG;
		}
	else	{
		warn "reload.cgi - failed(2): $cookie1 - $cookie - $input{referrer}";
		print $input->redirect($input{_config}->menu_page);
		}
	}

}
print "referrer checked\n" if $DEBUG;

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
		menu_page html color_set input_variables wholesome  graphic_group image_host);
@input{ @keys } = map { $input{_config}->$_ } @keys;
}

if ($input{'calc'} eq 'ova' || $input{'calc'} eq 'due' ) {
	$input{cycle} = $input{month} . "/" . $input{day} . "/" . $input{year};
	}

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
# load the template for the input form
my $directory = File::Spec->canonpath( $input{_config}->directory.$input{_config}->template_set."/" )
	|| File::Spec->curdir;

my $template = File::Spec->catfile(
	$directory, "$input{'calc'}.tmpl"
	);
#print "Template is $template\n" if $DEBUG;

print "Current working directory is ", cwd(), "\n" if $DEBUG;
print "Template is $template\n" if $DEBUG;

$error->( 'Could not read template file', 'Could not read template file' )
	unless -f $template;

my $data = Text::Template::fill_in_file( $template, HASH => \%input );
$error->( $Text::Template::ERROR, 'Template file error' )
	if $Text::Template::ERROR;

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# load the input form variables
my $fif = new HTML::FillInForm;
$output = $fif->fill(scalarref => \$data, fobject => $input);
print header(), $output;
exit;

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
	men => menu,
        motionsick => \&motion_sick,
        vod => \&vod,
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

=head1 AUTHOR

???

=head1 COPYRIGHT

???

=cut
