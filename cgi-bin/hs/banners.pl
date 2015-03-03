# $Id: banners.pl,v 1.1.1.1 2007/09/05 13:56:07 gwhite Exp $
use strict;

use File::Spec;

=head1 NAME

banners.pl - choose a banner for HealthStatus calculators

=head1 SYNOPSIS

	require "banners.pl";

	my $html = pick_banners( $user );
	
	my $banner1 = $html->[0];
	my $banner2 = $html->[1];
	my $banner3 = $html->[2];
	
=head1 DESCRIPTION

=head2 CONFIGURATION

In the configuration file, the banner system needs several entries
to find the right HTML.

=over 4

=item banner_dir

The directory which has the files with the banner HTML.

=item banner_priorities

The list of banner classes, in order of preference, from highest
to lowest.

	banner_priorities smoking fitness ...

=item banner_*

Each banner priority should have a configuration file entry. Its
value is a list of banner file names.

	banner_smoking banner1.html banner2.html ...
	
=back

=head2 Functions

=cut

sub _check_hash
	{
	my $hash = shift;
	return unless UNIVERSAL::isa( $hash, 'HASH' );
	return unless( exists $hash->{config} and
		UNIVERSAL::isa( $hash->{config}, 'ConfigReader::Simple' )
		);
		
	return 1;
	}	

=over 4

=item pick_banners( USER )

Return a set of banners for the first configured priority
it can satisfy.  If you don't specify a priority array,
pick_banners uses a default list.

=cut

sub pick_banners
	{
	my $hash     = shift;
	
	return unless _check_hash($hash);
	
	my $priority   = get_priorities( $hash );
	my $priorities = pick_priority( $hash );
	
	my $names;
	foreach my $priority ( @$priorities )
		{
		$names = get_banner_files( $hash, $priority->[0] );
		# stop when we get back something in names
		last if defined $names;
		}
		
	my $banners  = get_banners_html( $hash, @$names );

	return $banners;
	}

=item pick_priority( USER )

Returns a list of priorities that match the input.  It
returns an anonymous array of arrays whose elements have
both the name of the priority and its value:  For instance,
[ 'sex', 'Male' ], [ 'smoker', 1 ], or [ 'frame, 'large' ].
Once you have the array, you can use it to get banner file
names with get_banner_files().  If you can't load the banner
for that priority, you can move onto the next priority.

The priority list comes from the banner_priorities configuration
directive.

=cut

# the dispatch table defines subroutines for different banner
# priorities.  each sub should return true if the input matches
# the priority.  the input is the $hash from pick_priority.

my $Dispatch = {
	# these are true if the user simply filled in the form
	smoker     => sub {  $_[0]->{smoker}        ? 1 : 0  }, # smoking cost
	drinker    => sub {  $_[0]->{drink}         ? 1 : 0  }, # blood alcohol
	ovulating  => sub {  $_[0]->{ovulation_day} ? 1 : 0  }, # ovulation
	pregnant   => sub {  $_[0]->{due_date}      ? 1 : 0  }, # due date
	
	# these functions return a value that needs further inspection
	# almost all calculators fill in all of these values
	age        => sub {  $_[0]->{age}         },
	sex        => sub {  $_[0]->{sex}         },
	calculator => sub {  $_[0]->{calculator}  },
	frame      => sub {  $_[0]->{size}        }, #frame size
	
	# the default priority should always be true
	default    => sub { 1 },
	
	# these values need calculation
	bodymass   => sub {  
		my $bmi = $_[0]->{bmi};
		do {   
			if   ( $bmi < 1 )    { ''      }
			elsif( $bmi < 19.5 ) { 'Under' }
			elsif( $bmi < 25.5 ) { 'Good'  }
			elsif( $bmi < 30   ) { 'Over'  }
			else                 { 'Obese' }  };
		},
	
	bodyfat    => sub {  
		my $bfp = $_[0]->{body_fat};
		my $splits = $_[0]->{sex} eq 'Male' ?
			[  7, 17, 21, ] : [ 12, 24, 28, ];
			
		do {
			if   ( $bfp < 1 )	     { ''	  }
			elsif( $bfp < $splits->[0] ) { 'Low'      }
			elsif( $bfp < $splits->[1] ) { 'Lean'     }
			elsif( $bfp < $splits->[2] ) { 'Moderate' }
			else                         { 'Over'     }
			};
				
		},

	};
	
sub pick_priority
	{
	my $hash     = shift;
	return unless _check_hash($hash);
	
	my $priorities = get_priorities( $hash );
	my @matched    = ();

	foreach my $try ( @$priorities )
		{
		next unless exists $Dispatch->{$try};
		my $result = $Dispatch->{$try}->( $hash );
		push @matched, [ $try, $result ] if $result;
		$hash->{_banner}{$try} = $result;
		}

	return unless @matched;
	return \@matched;
	}

=back

=head2 Single step functions

These functions perform a particular part of the task.
If you want greater control than pick_banners allows,
you can use these individually.  Each function returns
the information needed for the next step.  The steps are,
in order, shown below.

	my $priorities = get_priorities( $hash );
	my $priority   = pick_priority( $hash, $priorities );
	my $files      = get_banner_files( $hash, $priority );
	my $html       = get_banner_html( $hash, $files );

	@array = @$html;

=over 4
	
=item get_priorities

Return an array reference of configured priorities.

This function relies on these configuration directives:

	banner_priorities

Returns undef or the empty list on failure.

=cut

sub get_priorities
	{
	my $hash = shift;
	
	return unless _check_hash($hash);
		
	my $config = $hash->{config}->banner_priorities;
	
	my @priorities = grep { not /default/ } split /\s+/, $config;
	push @priorities, 'default';
	
	return \@priorities;
	}
	
=item get_banner_files( USER [, PRIORITY] )

Returns the banner names defined for the specified banner
priority, or if no priority is specified, the default
priority.

If PRIORITY is "smoker", for instance, it gets the
banner files for banner_smoker in the configuration file.

Returns undef if the priority is not in the configuration
file or the priority has no configured files.

=cut

my %Foo = map { $_, 1 } qw( bodymass bodyfat sex frame calculator);
		
sub get_banner_files
	{
	my $hash     = shift;
	my $priority = lc shift;
	
	return unless _check_hash($hash);
	
	my $directive = "banner_$priority";
	$directive .= "_" . $hash->{_banner}{$priority} 
		if exists $Foo{$priority};

	my $names = $hash->{config}->get( $directive );
	return unless defined $names;
	
	my @names = split /\s+/, $names;
	return unless @names;
	
	return \@names;	
	}
	
=item get_banners_html( USER, FILES )

Get the banner HTML for the listed files.  FILES is an
list (not an array reference like the return value of 
get_banner_files).

This function relies on these configuration directives:

	banner_dir
	
=cut

sub get_banners_html
	{
	my $hash    = shift;
	my @files   = @_;
	my @banners = ();
	
	return unless _check_hash($hash);

	my $dir = $hash->{config}->banner_dir;
	return unless -d $dir;
	
	foreach my $name ( @files )
		{
		my $html = open_banner( $dir, $name );
		push @banners, $html;
		}
	
	return \@banners;
	}

=back

=head2 Utility Functions
	
=over 4

=item open_banner( DIR, FILE )

Fetch the banner HTML from the directory DIR and file FILE.

Returns undef or the empty list on failure.

=cut

sub open_banner($$)
	{
	my( $dir, $file ) = @_;
		
	my $abs_file = File::Spec->catfile( $dir, $file );
	return unless -r $abs_file;
	return unless -f $abs_file; # don't try to open a directory
	
	return do {
		if( open my $file, $abs_file ) { do { local $/; <$file> } }
		else { wantarray ? () : undef }
		};
		
	}

=item name_to_file( NAME )

Takes the banner name in NAME and turns it into a suitable
filename by stripping out unwanted characters and turning
whitespace in underscores.

Returns false if the resulting filename is longer than the
setting in $MAX_FILENAME_LENGTH.

=cut

my $MAX_FILENAME_LENGTH = 16;

sub name_to_file($)
	{
	my $name = shift;
	
	# remove unallowed characters
	$name = s/[^a-zA-Z\d\s]//g;
	
	# compress and replace whitespace
	$name = s/\s+/_/g;
	
	return unless $name < $MAX_FILENAME_LENGTH;
	}

=item file_to_name( FILE )

Takes the banner file name FILE and turn it into the user-
defined banner name.  The FILE parameter is only the file
portion, not the absolute path.

=cut

sub file_to_name($)
	{
	my $file = shift;
	
	$file =~ tr/_/ /;
	
	return $file;
	}
	
=back

=head1 AUTHOR

brian d foy, E<lt>bdfoy@cpan.orgE<gt>

=head1 COPYRIGHT

Copyright 2002, HealthStatus.com, All rights reserved.

This is commerical software. You must have a license to
use it.

=cut	

1;
