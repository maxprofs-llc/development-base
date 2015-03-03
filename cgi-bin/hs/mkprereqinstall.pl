#!/usr/bin/perl -w
# -*- perl -*-

#
# $Id: mkprereqinstall.pl,v 1.2 2010/06/25 15:42:56 code4hs Exp $
# Author: Slaven Rezic
#
# Copyright (C) 2002, 2003 Slaven Rezic. All rights reserved.
# This package is free software; you can redistribute it and/or
# modify it under the same terms as Perl itself.
#
# Mail: slaven@rezic.de
# The latest version of mkprereqinst may be found at
# http://www.perl.com/CPAN-local/authors/id/S/SR/SREZIC/
#
use English;
use Config;
use Getopt::Long;
use strict;
use vars qw($VERSION);
use ExtUtils::MakeMaker;
use File::Basename qw(basename);

$VERSION = sprintf("%d.%02d", q$Revision: 1.2 $ =~ /(\d+)\.(\d+)/);


my $v;
my $exec;
my $do_cpan;
my $do_ppm;
my $o = "prereqinst.pl";
my $Makefile_PL;

if (!GetOptions("v!" => \$v,
		"exec!" => \$exec,
		"cpan!" => \$do_cpan,
		"ppm!" => \$do_ppm,
		"o=s" => \$o,
	       )) {
    require Pod::Usage;
    Pod::Usage::pod2usage(1);
}
my %pm;
if($^O eq 'Win32'){
	# PPM version (Windows based)
	%pm = ("Bit::Vector" => 6.3 , "Carp" => 0, "CGI" => 2.75, "CGI::Carp"=>1.20, "CGI::Util"=>1.1, "Class::Struct"=>0.59, "Compress::Zlib"=>1.16, "Config"=>0, "ConfigReader::Simple"=>1.16, "Crypt::CBC"=>2.08, 
	"Crypt::DES"=>2.03, "Date::Calc"=>5.3, "Date::Format"=>0, "DBI"=>1.28, "DBD::ODBC"=>0, "DBD::mysql"=>0, "File::Copy"=>2.03, "HTML::Entities"=>1.23, "HTML::FillInForm"=>1.01, "HTML::Parser"=>3.26, 
	"HTML::Tagset"=>3.03, "LWP::Simple"=>1.36, "Mail::Sendmail"=>0.79, "MIME::Base64"=>2.12, "MIME::QuotedPrint"=>2.03, "SDBM_File"=>1.03, "Text::Tabs"=>98.11, "Text::Template"=>1.43, 
	"Text::Wrap"=>2001.0, "Time::Local"=>0, "Time::localtime"=>1.01, "Time::tm"=>0, "URI"=>1.19, "XML::Parser"=>2.27, "CGI::SSI"=>0, "DBIx::Sequence"=>0, "Net::SFTP" =>0, "Spreadsheet::Read" =>0, "DateTime::Format::MySQL" =>0, "DateTime"	=>0,"DateTime::Format::Duration" =>0);
	}
else	{
	# CPAN version
	%pm = ("Archive::Zip"=>0, "Bit::Vector" => 6.3 , "Carp" => 0, "CGI" => 2.75, "CGI::Carp"=>1.20, "CGI::Util"=>1.1, "Class::Struct"=>0.59, "Compress::Zlib"=>1.16, "Config"=>0, "ConfigReader::Simple"=>1.16, "Crypt::Blowfish_PP"=>0, "Crypt::CBC"=>2.08, 
	"Crypt::DES"=>2.03, "Date::Calc"=>5.3, "DBI"=>1.28, "File::Copy"=>2.03, "GD"=>0, "GD::Graph"=>1.39, "GD::Text"=> 0.83, "HTML::Entities"=>1.23, "HTML::FillInForm"=>1.01, "HTML::Parser"=>3.26, 
	"HTML::Tagset"=>3.03, "LWP::Simple"=>1.36, "Mail::Sendmail"=>0.79, "MIME::Base64"=>2.12, "MIME::QuotedPrint"=>2.03, "OLE::Storage_Lite"=>0, "SDBM_File"=>1.03, "Spreadsheet::WriteExcel" => 0, "Text::CSV"=> 0, "Text::Tabs"=>98.11, "Text::Template"=>1.43, 
	"Text::Wrap"=>2001.0, "Time::Local"=>0, "Time::localtime"=>1.01, "Time::tm"=>0, "URI"=>1.19, "XML::Parser"=>2.27, "CGI::SSI"=>0, "Crypt::Blowfish"=>0, "DBIx::Sequence"=>0, "DBD::mysql"=>3, "Net::SFTP" =>0, "Spreadsheet::Read" =>0, "DateTime::Format::MySQL" =>0, "DateTime"	=>0,"DateTime::Format::Duration" =>0);
	}

my $prereq_pm = \%pm;


my $code = "";

$code .= <<EOF;
$Config{startperl}
# -*- perl -*-
#
# DO NOT EDIT, created automatically by
# $0
# on @{[ scalar localtime ]}
#
# The latest version of @{[ basename($0) ]} may be found at
# http://www.perl.com/CPAN-local/authors/id/S/SR/SREZIC/

use Getopt::Long;
EOF

$code .= <<'EOF';
my $require_errors;
my $use = 'cpan';

if (!GetOptions("ppm"  => sub { $use = 'ppm'  },
		"cpan" => sub { $use = 'cpan' },
	       )) {
    die "usage: $0 [-ppm | -cpan]\n";
}

EOF

my(@installs, @ppm_installs, @requires, @modlist);
while(my($mod, $ver) = each %$prereq_pm) {
    my $check_mod = "require $mod";
    if ($ver) {
	$check_mod .= "; $mod->VERSION($ver)";
    }
    push @installs, "install '$mod' if !eval '$check_mod';";
    (my $ppm = $mod) =~ s/::/-/g;
    push @ppm_installs, "do { print STDERR 'Install $ppm'.qq(\\n); PPM::InstallPackage(package => '$ppm') or warn ' (not successful)'.qq(\\n); } if !eval '$check_mod';";
    push @requires, "if (!eval 'require $mod;" . ($ver ? " $mod->VERSION($ver);" : "") . '\') { warn $@; $require_errors++ }';
    push @modlist, $mod . ($ver ? " $ver" : "");
}

$code .= <<EOF;
if (\$use eq 'ppm') {
    require PPM;
@{[ join("\n", map("    $_", @ppm_installs)) ]}
} else {
    use CPAN;
@{[ join("\n", map("    $_", @installs)) ]}
}
EOF

$code .= join("\n", @requires) . "\n\n";

$code .= 'if (!$require_errors) { warn "Autoinstallation of prerequisites completed\n" } else { warn "$require_errors error(s) encountered while installing prerequisites\n" } ' . "\n\n" . 'print "\n\nRun /cgi-bin/sleuth.pl from your browser to make sure everything is in place.";' . "\n";

if ($exec) {
    package Prereqinst;
    local @ARGV;
    if    ($do_cpan) { push @ARGV, "-cpan" }
    elsif ($do_ppm)  { push @ARGV, "-ppm"  }
    eval $code;
    die $@ if $@;
} else {
    open(F, "> $o") or die "Can't write $o: $!";
    print F $code;
    close F;
    chmod 0755, $o;
}

if ($v) {
    require Text::Wrap;
    print STDERR Text::Wrap::wrap("Dependencies: ", "              ",
				  join(", ", @modlist) . "\n");
}

sub set_prereq_pm {
    my(@args) = @_;
    my $prereq_pm = {};
    my $curr_mod;
    for(my $i=0; $i<=$#args; $i++) {
	if ($args[$i] =~ /^\d/) {
	    if (!defined $curr_mod) {
		die "Got version <$args[$i]>, but expected module name!";
	    }
	    $prereq_pm->{$curr_mod} = $args[$i];
	    undef $curr_mod;
	} else {
	    if (defined $curr_mod) {
		$prereq_pm->{$curr_mod} = undef;
	    }
	    $curr_mod = $args[$i];
	}
    }
    if (defined $curr_mod) {
	$prereq_pm->{$curr_mod} = undef;
    }
    $prereq_pm;
}

__END__

=head1 NAME

mkprereqinst - create a prereqinst file for perl module distributions

=head1 DESCRIPTION

C<mkprereqinst> creates a C<prereqinst.pl> file. The created file can
be included to perl module and script distributions to help people to
get and install module prerequisites through C<CPAN.pm> or C<PPM.pm>.

The standard installation process of perl distributions with a
prereqinst file will look as following:

    perl Makefile.PL
    (if there are some modules missing then execute the next line)
    perl prereqinst
    make all test install

For a Build.PL-based distribution, use the following

    perl Build
    (if there are some modules missing then execute the next line)
    perl prereqinst
    perl Build test
    perl Build install

If the user needs superuser privileges to install something on his
system, then C<perl prereqinst.pl> and C<make install> should be run
as superuser, e.g. with help of the C<su> or C<sudo> command.

ActivePerl users may use

    perl prereqinst.pl -ppm

to fetch the modules through C<PPM> instead of C<CPAN>.

For an alternative approach see the CPAN module
L<ExtUtils::AutoInstall>. Some differences are:

                            | mkpreqinst | ExtUtils::AutoInstall
 ---------------------------+------------+----------------------
 Support for CPAN           |    yes     |    yes
 Support for CPANPLUS       |	 no    	 |    yes
 Support for PPM            |	 yes	 |    no
 Needs Makefile.PL changes  |	 no 	 |    yes
 Support for Build.PL       |    yes     |    ???
 Different build process    |    yes     |    no
 Has a lot of fancy options |	 no    	 |    yes

=head2 OPTIONS

C<mkprereqinst> accepts the following options:

=over

=item C<-v>

Be verbose.

=item C<-exec>

Instead of creating the C<prereqinst.pl>, execute the generated code.

=item C<-cpan>, C<-ppm>

These options are only useful in conjunction with the C<-exec> option
and force the type of auto-installation.

=item C<-o> outfile

Use another output file than the default C<prereqinst.pl>.

=back

It is also possible to supply a list of modules and version numbers on
the command line. In this case the Makefile.PL and Build.PL are
ignored. Example:

    mkprereqinst XML::Parser 2.30 Tk GD

=head1 BUGS and TODO

The script does nasty things with C<ExtUtils::MakeMaker> and the
C<WriteMakefile> subroutine.

It is annoying to create the prereqinst.pl file if the Makefile.PL is
interactive.

OS-related or other conditions in C<PREREQ_PM> are not handled.

There are problems with the mapping of perl module names to PPM
package names.

prereqinst.pl should autodetected whether the system is a CPAN or a
PPM system. With -cpan or -ppm it would be possible to change the
default.


=head1 README

mkprereqinst creates a prereqinst file. The created file can be
included to perl module and script distributions to help people to get
and install module dependecies through CPAN.pm or PPM.pm

=head1 PREREQUISITES

only standard perl modules

=head1 COREQUISITES

YAML

=head1 OSNAMES

any

=head1 SCRIPT CATEGORIES

CPAN

=head1 AUTHOR

Slaven Rezic <slaven@rezic.de>

=head1 SEE ALSO

L<CPAN>, L<PPM>, L<ExtUtils::MakeMaker>, L<Module::Build>.

=cut


