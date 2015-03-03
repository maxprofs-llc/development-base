#!/usr/bin/perl 

# this sets our path statement to look for the different modules
BEGIN{($_=$0)=~s![\\/][^\\/]+$!!;push@INC,$_}

use CGI qw /:standard/;
use CGI::Carp qw(fatalsToBrowser);
use File::Find  qw(find);
use Getopt::Std qw(getopts);
use ExtUtils::MakeMaker;
require 5.6.1;

# Set test_data_dir to the directory where temporary files can be written to
# full path is best and end with a /
# my $test_data_dir = "../data/";
my $test_data_dir = "/opt/app/apache/app/data/";

#my $we_can_fix = eval 'use CPANPLUS::Backend; 1';
my $we_can_fix = 0;

my $cp;
if($we_can_fix){
#	use CPANPLUS::Backend;
	$cp = new CPANPLUS::Backend(conf => {	debug => 0,
						prereqs => 1,
						verbose => 1});
	}

# set some global variables
use vars(q!$opt_v!, q!$opt_w!, q!$opt_a!, q!$opt_s! );
use vars ( q!$Start_Dir!, q!%Future! );

# set the local variables
my ( $sendmail, $perlocation, $version, $use_me, $key, $mloc, $ploc, $dev, $ino );
my ( @dbd, %pm, @xpm, @perlat, @mailat );
my %visited;

#check command line options - NOT USED
getopts('wvas') or die "bad usage";
my @ARGV = @INC unless @ARGV;

# create a CGI object
my $q=new CGI;

# array of crucial modules in alpha order
%pm = ("Archive::Zip"=> 0, "Bit::Vector" => 6.3 , "Carp" => 0, "CGI" => 2.75, "CGI::Carp"=>1.20, "CGI::SSI"=>0, "CGI::Session"=>0, "CGI::Util"=>1.1, "Class::Struct"=>0.59, "Compress::Zlib"=>1.16, "Config"=>0, "ConfigReader::Simple"=>1.28, "Crypt::Blowfish"=>0, "Crypt::CBC"=>2.08,
	"Crypt::DES"=>2.03, "Date::Calc"=>5.3, "DBI"=>1.28, "DBIx::Sequence" => 0, "File::Copy"=>2.03, "HTML::Entities"=>1.23, "HTML::Lint"=>0, "HTML::FillInForm"=>1.01, "HTML::Parser"=>3.26,
	"HTML::Tagset"=>3.03, "IO::File"=> 0, "LWP::Simple"=>1.36, "Mail::Sendmail"=>0.79, "MIME::Base64"=>2.12, "MIME::QuotedPrint"=>2.03, "OLE::Storage_Lite"=>0, "SDBM_File"=>1.03, "Spreadsheet::ReadSXC"=> 0.20, "Spreadsheet::ParseExcel"=> 0.58, "Spreadsheet::XLSX"=> 0.13, "Spreadsheet::WriteExcel" => 0, "Text::CSV"=> 0,"Text::Tabs"=>98.11, "Text::Template"=>1.43,
	"Text::Wrap"=>2001.0, "Time::Local"=>0, "Time::localtime"=>1.01, "Time::tm"=>0, "URI"=>1.19, "XML::Parser"=>2.27  );

my @hs_modules = ( "HealthStatus", "HealthStatus::CalcRisk", "HealthStatus::Config","HealthStatus::Constants","HealthStatus::Database","HealthStatus::Report","HealthStatus::User",
"HealthStatus::Error","HealthStatus::CalcRisk","HealthStatus::CRC","HealthStatus::DRC","HealthStatus::FIT","HealthStatus::HRA");

$sendmail	=`whereis sendmail`;
$perlocation	=`whereis perl`;
@perlat = split(" ",$perlocation);
@mailat = split(" ",$sendmail);

# print an html header
print $q->header, $q->start_html(-title=>'HealthStatus.com Configuration Seeker',
				-author=>'Greg White gwhite@healthstatus.com',
				-bgcolor=>'#FFFFFF',
				-text=>'#666666',
				-link=>'#666666',
				-vlink=>'#669933',
				-alink=>'#666666'),
				img{src=>"http://www.healthstatus.net/images/hs_logo.gif", align=>'center'},
				h3("HealthStatus.com");
#  first, lets see what version of perl we have
$version = `perl -v`;
my $operating_system = $^O;
print "<table border=0 width=640><TR align=CENTER, valign=TOP><td><br><b>Server Perl Version Information</b> $version<br><br><b>Running on $operating_system</b></p></td></tr></table>";
#  $0 is the current script, complete with the path
print "<p>Currently running $0<p>";
#  cycle through the environment hash, information
#  is stored as key/value pairsprint "Next the web server environment info:<p>";
print "<table border=2 width=640 bordercolor=\"#333366\"><TR align=CENTER, valign=TOP><th>Variable</th><th>Content</th></tr>";
foreach (keys %ENV) {
	print qq|<TR><td>$_</td><td>$ENV{$_}</td></tr>|;
}
#  next step, list out everything in the places Perl
#  will automagically look for libraries and modules
print "</table>";
print "<h3>Existing HealthStatus modules already installed</h3>";
my $hs_cnts = 0;
my $try_the_graph = 0;
foreach $use_me(sort @hs_modules){
	if (eval "require ($use_me)"){
		$t1= '$' . $use_me . '::VERSION';
		$t2 = eval "$t1";
		++$hs_cnts;
		$try_the_graph = 1 if ($use_me eq "GD::Graph");
		print "found $use_me - installed version $t2<br>";
		}
	}
print "<p>No HealthStatus modules found</p>" unless $hs_cnts;

print "<h3>Programs to be installed</h3><p>Load these from your packages or ports collection, or click on the links for recently known locations of these open source programs.<br><a href=\"http://www.zlib.org\">zlib</a><br><a href=\"http://expat.sourceforge.net\">expat</a><br><a href=\"http://www.libpng.org\">libpng</a><br><a href=\"http://www.ijg.org/\">jpeg-6b</a><br><a href=\"http://www.freetype.org/\">freetype</a><br><a href=\"http://www.boutell.com/gd/\">gd</a><br>also your database, Oracle, MS SQL, mySQL or other supported database should be installed and running.</p><p><h3>Important Modules</h3><p>We have found them to be most easily installed from the top of the list down.</p><p>";
	foreach $use_me(sort keys %pm){
		if (eval "require ($use_me)"){
			$t1= '$' . $use_me . '::VERSION';
			$t2 = eval "$t1";
			if ($t2 < $pm{$use_me}){
				if($we_can_fix){
					my $result = $cp->install(modules => [$use_me], fetchdir => '/usr/local/www/vhosts/chi-ubh/temp', extractdir => '/usr/local/www/vhosts/chi-ubh/temp');
					print '<b>Error: '.$err->stack().' ############################## Trouble </b>' unless ($result);
					print '<b>Upgraded $use_me.</b>' if ($result); }
				else 	{ print "<b>Upgrade this module to at least $pm{$use_me} or higher.</b>  " }
				}
			print "found $use_me - installed version $t2<br>";
			if($use_me eq 'DBI'){
				@dbd = DBI->available_drivers($quiet);
				if (scalar(@array) > 0){
					foreach $key (@dbd){
						print "--- DBD - $key<br>";
					}
				}else{
					print "--- no database specific DBI drivers found, make sure they are loaded for your database!<br>"
				}
			}
		}else{
			if($we_can_fix){
					my $result = $cp->install(modules => [$use_me], fetchdir => '/usr/local/www/vhosts/chi-ubh/temp', extractdir => '/usr/local/www/vhosts/chi-ubh/temp');
					print '<b>Error: '.$err->stack().' ############################## Trouble </b>' unless ($result);}
				else 	{ print "<b>####### need to get $use_me - $pm{$use_me} #########</b><br>"; }
		}
	}
print "</table><h3>Extra Features Modules</h3><p>";
	foreach $use_me(@xpm){
		if (eval "require ($use_me)"){
			print "found $use_me<br>";
		}else{
			print "<b>####### would be nice to have $use_me #########</b><br>";
		}
	}
print "</p><h3>Sendmail</h3><p>";
	foreach $mloc(@mailat){
		print "$mloc<BR>\n";
	}
print "</p><h3>Perl</h3><p>";
	foreach $ploc(@perlat){
		print "$ploc<BR>\n";
	}
print "</p>";


@Future{@ARGV} = (1) x @ARGV;

# go through all the directories in our path and find the modules we can use in each
print "<table border=2 width=640 bordercolor=\"#333366\"><TR align=CENTER, valign=TOP><th>Module</th><th>Description</th></tr>";

foreach $Start_Dir (@ARGV) {
	delete $Future{Start_Dir};
	print "<tr><td colspan=2 align=center><b>Modules from $Start_Dir</b>";
	next unless ($dev,$ino) = stat($Start_Dir);
	next if $visited{$dev,$ino}++;
	next unless $opt_a || $Start_Dir =~ m!^/!;
	find(\&wanted, $Start_Dir);
}
print "</table>";

print "<table border=2 width=640 bordercolor=\"#333366\"><TR align=CENTER, valign=TOP><th>Module</th><th>Version</th><th>Description</th></tr>";

for my $inc_dir (sort { length $b <=> length $a } @ARGV) {
	print "<tr><td colspan=3 align=center><b>Modules from $inc_dir</b></td></tr>";
	find({
		wanted => sub {
			return unless /\.p(?:m|od)\z/ && -f;

			my $module  = get_module_name($File::Find::name, $inc_dir);
			my $version = get_module_version($_);
			my $desc    = get_module_description($_);

			$version = defined $version ? "($version)" : "";
			$desc    = defined $desc    ? "- $desc"    : "";
			print "<tr><td>$module</td><td>$version</td><td>$desc</td></tr>";
		},
		preprocess => sub {
			my ($dev, $inode) = stat $File::Find::dir or return;
			$visited{"$dev:$inode"}++ ? () : @_;
		},
	},
	$inc_dir);
}


print "</table>";
print "<br><p>Email the results of this page to gwhite\@healthstatus.com";
exit;
# that does it

# subroutine to find the files in the path
sub modname {
	local $_ = $File::Find::name;

	if (index($_, $Start_Dir. '/') == 0) {
		substr($0, 0, 1+length($Start_Dir)) = '';
	}
	s { /              }   {::}gx;
	s { \.p(m|od)$     }   {}x;

	return $_;
}
# is the file we found a perl module (*.pm)
sub wanted {
	if ( $Future{File::find::name}) {
		$File::Find::prune = 1;
		return;
	}
	return unless /\.pm$/ && -f;
	my $Module = &modname;
	if ($Module =~ /^CPAN(\Z|::)/) {
		return;
	}
	my $file = $_;
	unless ( open(POD, "< $file")) {
		return 0;
	}

	$: = " -:";
	local $/ = '';
	local $_;
	while (<POD>) {
		if (/=head\d\s+NAME/) {
			chomp($_ = <POD>);
			s/^.*?-\s+//s;
			s/\n/ /g;
			if (defined (my $v = getversion($Module))) {
				print "<tr><td>$Module ($v) </td>";
			} else {
				print "<tr><td>$Module </td>";
			}
			print "<td>$_</td></tr>";
			return 1;
		}
	}
	return 0;
}

# get the version of the module
sub getversion {
	my $mod = shift;
	my $vers = `$^X -m$mod -e 'print \$${mod}::VERSION' 2>/dev/null`;
	$vers =~ s/^\s*(.*?)\s*$/$1/;
	return ($vers || undef);
}

sub get_module_name {
	my ($path, $relative_to) = @_;

	local $_ = $path;
	s!\A\Q$relative_to\E/?!!;
	s! \.p(?:m|od) \z!!x;
	s!/!::!g;

	return $_;
}

sub get_module_description {
	my ($file) = @_;

	open my $pod, "<", $file
		or (warn("\tCannot open $file: $!"), return);

	local $_;
	local $/ = '';
	while (<$pod>) {
		if (/=head\d\s+NAME/) {
			$_ = <$pod>;
			return unless $_; # $_ may be undefined
			chomp;
			s/ \A .*? - \s+ //sx;
			tr/\n/ /;
			return $_;
		}
	}

	return;
}

sub get_module_version {
	local $_;     # MM->parse_version is naughty
	my $vers_code = MM->parse_version($File::Find::name) || '';
	return eval $vers_code || undef;
}
