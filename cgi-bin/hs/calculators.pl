# $Id: calculators.pl,v 1.2 2010/03/10 12:01:45 code4hs Exp $
use strict;

=head1 NAME

calculators.pl

=head1 SYNOPSIS

require calculators.pl;

=head1 DESCRIPTION

Each calculator is represented by a subroutine that takes a hash
reference as its argument.  The hash reference holds the input
data, and the calculator adds computed values to it.  The
documentation for each of the calculators lists the input and
output keys for the hash.

Some calculators return dimensional values.  In these cases, the
output units are the same as the input units.  Given metric
data the calculators return metric values, and likewise for
imperial units.

=over 4

=item blood_alcohol( HASH_REF )

Input form names

	sex     'Male' or 'Female'
	weight  weight, in pounds or kilograms
	number  number of drinks
	type    double pipe separated list of type of drink
		singular name||plural name||potency
	time    time frame, in hours, for number of drinks specified
	measure   'Metric' or 'Imperial'

Output values

	drink       singular or plural form from 'type'
	bac         blood alcohol content
	sex_factor  gender multiplier for alcohol effect

=cut

# Removing warnings in log while module is being used with CGI version 4 or above
$CGI::LIST_CONTEXT_WARN = 0;

use Carp qw(croak);

use constant MALE      => 'Male';
use constant METRIC    => 'Metric';
use constant KG_TO_LBS => 2.2046;

my $DEBUG = 0;

my $Calorie_data_missing = <<"TXT";
Could not load calorie data for HealthStatus calculators.
Make sure that calorie_data.pl is in your Perl search path
or in the same directory as calculators.pl
TXT

sub blood_alcohol
	{
	print "In blood_alcohol\n" if $DEBUG;

	my $hash = shift;

	if( $hash->{weight} < 50 || $hash->{weight} > 950 )
		{
		@{$hash->{'ERROR_FIELDS'}}{qw(sex weight number type time measure)} =
			[ @$hash{ qw( sex weight number type time measure )} ];
		$hash->{ERROR_MSG}   = "The weight you entered ($$hash{weight}) is out of range, valid weights are between 50 and 950 pounds";
		$hash->{ERROR_TITLE} = "Bad Input";
		$hash->{ERROR_NAME}  = "Invalid weight";

		return;
		}

	if( $hash->{number} < 1 || $hash->{number} > 20 )
		{
		@{$hash->{'ERROR_FIELDS'}}{qw(sex weight number type time measure)} =
			[ @$hash{qw( sex weight number type time measure )} ];
		$hash->{ERROR_MSG}   = "The number you entered is not reasonable, you entered ($$hash{number}), reasonable quantities for this calculator are between 1 and 20";
		$hash->{ERROR_TITLE} = "Bad Input";
		$hash->{ERROR_NAME}  = "Invalid number of drinks";

		return;
		}

	if( $hash->{'time'} < 0.2 || $hash->{'time'} > 10 )
		{
		@{$hash->{'ERROR_FIELDS'}}{qw(sex weight number type time measure)} =
			[ @$hash{qw( sex weight number type time measure )} ];
		$hash->{ERROR_MSG}   = "The time you entered is not reasonable, you entered ($$hash{time}), reasonable quantities for this calculator are between .2 and 10";
		$hash->{ERROR_TITLE} = "Bad Input";
		$hash->{ERROR_NAME}  = "Invalid time";

		return;
		}

	# the 'type' parameter has the singular and plural forms of the
	# type of drink, and the relative strength of the drink, as a
	# double pipe (||) separated list.
	my( $singular, $plural, $potency ) = split /\|\|/, $hash->{type};

	$hash->{drink}      = $hash->{number} == 1 ? $singular : $plural;

	$hash->{sex_factor} = $hash->{sex} eq MALE ? 0.58 : 0.49;

	my $factor = $hash->{measure} eq METRIC ? 1 : KG_TO_LBS;

	$hash->{bac} = eval { sprintf "%.2f",
		 23.36 /
		 ( $hash->{weight} / $factor * $hash->{sex_factor} * 1000 )
		 * 0.806 * 100 * $potency * $hash->{number}
		 -.012 * $hash->{'time'}
	 	};
	$hash->{bac} = 0 if $hash->{bac} < 0;

	return 1;
	}

=item body_fat( HASH_REF )

Input form names

	sex     'Male' or 'Female'
	waist   waist circumference, in inches or cm
	weight  weight in pounds or kilograms
	measure   'Metric' or 'Imperial'

Output values

	preferred_body_fat   in percent fat

=cut

sub body_fat
	{
	print "In body_fat\n" if $DEBUG;

	my $hash = shift;
	my $factor = $hash->{measure} eq METRIC ? 0.3937 : 1;
	my $weight_factor = $hash->{measure} eq METRIC ?  KG_TO_LBS : 1;
	my $abd2 =  $hash->{abd2};
	$abd2 *= 0.3937 if $hash->{measure} eq METRIC;
	my $weight = $hash->{weight};
	$weight *= KG_TO_LBS if $hash->{measure} eq METRIC;
	
	@{$hash->{'ERROR_FIELDS'}}{qw( sex abd2 weight )} =
		[ @$hash{qw( sex abd2 weight )} ];

	$hash->{title} = "Body Fat";

	if( (($hash->{weight} < 50 || $hash->{weight} > 950) &&  $hash->{measure} ne METRIC ) ||
		(($hash->{weight} < 22 || $hash->{weight} > 430) &&  $hash->{measure} eq METRIC ) )
		{
		$hash->{ERROR_MSG}   = qq{The weight you entered ($$hash{weight}) is out of range, valid weights are between 50 and 950 pounds or 22 kg and 430 kg};
		$hash->{ERROR_TITLE} = 'Bad Input';
		$hash->{ERROR_NAME}  = 'Invalid weight';
		return;
		}

	if( $hash->{abd2} < 10 || $hash->{abd2} > 96 )
		{
		$hash->{ERROR_MSG}   = qq{The waist size you entered ($$hash{abd2}) is out of range, valid waist sizes are between 10" and 96"};
		$hash->{ERROR_TITLE} = 'Bad Input';
		$hash->{ERROR_NAME}  = 'Invalid waist size';
		return;
		}

	my $sex_factor = $hash->{sex} eq MALE ? -98.42 : -76.76;

	$hash->{preferred_body_fat} = sprintf "%.2f",
		( $sex_factor + 4.15 * $abd2
			- .082 * $weight )
			/
		$weight * 100;
	return 1;
	}

=item navy_body_fat

Input form names - different for male and female

	sex
	height   in inches
	mheight  in inches from the metric pulldown
	measure   'Metric' or 'Imperial'
	neck     neck measurement, in inches or centimeters

	abd1     female abdominal width, in inches or centimeters
	hip      hip circumference, in inches or centimeters

	abd2     male abdominal width, in inches or centimeters

Output form names

	navy_body_fat

NOTE: this calculator uses centimeters, so we have to convert
Imperial units to metric.

=cut

sub navy_body_fat
	{
	my $hash = shift;

	my $height = $hash->{height} || $hash->{mheight};
	my $factor = $hash->{measure} eq METRIC ? 1 : 2.54;

	@{$hash->{'ERROR_FIELDS'}}{qw( sex height )} =
		[ @$hash{qw( sex height )} ];

	@{$hash->{'ERROR_FIELDS'}}{qw( abd1 hip neck )} =
		[ @$hash{qw( abd1 hip neck )} ] unless $hash->{sex} eq MALE;

	@{$hash->{'ERROR_FIELDS'}}{qw( abd2 neck )} =
		[ @$hash{qw( abd2 neck )} ] if $hash->{sex} eq MALE;

	require POSIX;

	$hash->{navy_body_fat} = sprintf "%.2f", do {
		if( $hash->{sex} ne MALE )
			{
			# R = 0.85, SEE=3.72 %fat for n=214
			my $diff = $hash->{abd1} + $hash->{hip} - $hash->{neck};
			eval { 495 / ( 1.29579 - 0.35005 * POSIX::log10( $diff * $factor )
			           +
			        0.22100 * POSIX::log10( $height * 2.54 )
			      ) - 450 };
			}
		else
			{
			# R = 0.90, SEE=3.52 %fat for n=602
			my $diff = $hash->{abd2} - $hash->{neck};
			eval { 495 / ( 1.0324 - 0.19077 * POSIX::log10( $diff * $factor )
			           +
			        0.15456 * POSIX::log10( $height * 2.54 )
			      ) - 450 };
			}
		};

	return $@ if $@;

	return 1;
	}

=item body_fat_both( HASH_REF )

Computes body_fat and navy_body_fat at the same time.

=cut

sub body_fat_both
	{
	my $hash = shift;

	body_fat( $hash);
	navy_body_fat( $hash );

	return 1;
	}

=item body_mass( HASH_REF )

Input form values

	height   in inches
	mheight  in inches from the metric pulldown
	measure   'Metric' or 'Imperial'
	weight   in pounds or kilograms

Output values, in either METRIC or IMPERIAL

	bmi
	low_weight
	high_weight

=cut

sub body_mass
	{
	my $hash = shift;

	my $height = $hash->{height} || $hash->{mheight};

	my $weight = $hash->{weight};
	$weight *= KG_TO_LBS if $hash->{measure} eq METRIC;

	$hash->{title} = "Body Mass Index (BMI)";

	if( $height < 20 || $height > 90 )
		{
		@{$hash->{'ERROR_FIELDS'}}{qw( weight height measure mheight )} =
			@$hash{qw( weight height measure mheight )};
		$hash->{ERROR_MSG}   = qq|The height you entered ($$hash{height}) is out of range, valid heights are between 1'8" and 7'6" (US) or 1.4 m and 2.7 m.|;
		$hash->{ERROR_TITLE} = 'Bad Input';
		$hash->{ERROR_NAME}  = 'Invalid height';
		return;
		}

	if( (($hash->{weight} < 50 || $hash->{weight} > 950) &&  $hash->{measure} ne METRIC ) ||
		(($hash->{weight} < 22 || $hash->{weight} > 430) &&  $hash->{measure} eq METRIC ) )
		{
		@{$hash->{'ERROR_FIELDS'}}{qw( height weight )} =
			@$hash{qw( height weight )};
		$hash->{ERROR_MSG}   = qq{The weight you entered ($$hash{weight}) is out of range, valid weights are between 50 and 950 pounds or 22 kg and 430 kg};
		$hash->{ERROR_TITLE} = 'Bad Input';
		$hash->{ERROR_NAME}  = 'Invalid weight';
		return;
		}

	my $square = $height**2;

	$hash->{bmi}      = sprintf "%3.1f", $weight / $square * 704.5;

	# calculate low optimum range (BMI 19.6)
	$hash->{low_weight} = sprintf "%3.0f", 19.6 * $square / 704.5;

	# calculate high optimum range (BMI 24.9)
	$hash->{high_weight} = sprintf "%3.0f", 24.9 * $square / 704.5;

	@{ $hash }{ qw(low_weight high_weight) } = map { sprintf "%3.0f", ($_ / KG_TO_LBS ) }
		@{ $hash }{ qw(low_weight high_weight) } if $hash->{measure} eq METRIC;

	return 1;
	}

=item calorie_calculator( HASH_REF )

Input form values

    weight      in pounds or kilograms
    measure      'Metric' or 'Imperial'
    T*          where * is a number that corresponds to
                a calorie category. the value is the
                number of minutes for this activity. the
                calorie value for this activity is
                multiplied by this value.

Output form values

	calories - a hash whose keys are the activity descriptions
		and whose values are the number of calories

=cut

sub calorie_calculator
	{
	my $hash = shift;

	$hash->{title} = "Calories Burned";

	my $weight = $hash->{weight};
	$weight *= KG_TO_LBS if $hash->{measure} eq METRIC;

	if( (($hash->{weight} < 50 || $hash->{weight} > 950) &&  $hash->{measure} ne METRIC ) ||
		(($hash->{weight} < 22 || $hash->{weight} > 430) &&  $hash->{measure} eq METRIC ) )
		{
		@{$hash->{'ERROR_FIELDS'}}{qw( weight )} =
			@$hash{( $$hash{weight} )};
		$hash->{ERROR_MSG}   = qq{The weight you entered ($$hash{weight}) is out of range, valid weights are between 50 and 950 pounds or 22 kg and 430 kg};
		$hash->{ERROR_TITLE} = 'Bad Input';
		$hash->{ERROR_NAME}  = 'Invalid weight';
		return;
		}

	croak $Calorie_data_missing
		unless eval { require "calorie_data_lang.pl"; };

	my $measure = lc $hash->{measure} || 'imperial';
	my $language = lc $hash->{lang} || 'en';
	
	my( $calories, $description, $skip ) = get_calorie_data($measure,$language);
	
#	my $calories = $calories1->{$measure};

	foreach my $key ( keys %{$calories} )
		{
		if( defined $hash->{$key} && $hash->{$key} > 0 )
			{
			my $t1 = $calories->{$key} * $weight * $hash->{$key};
			$hash->{total_calories} += $t1;

			$hash->{calories}{ $description->{$key} }
				=  sprintf "%.0f", $t1 ;
			}
		}

	$hash->{total_calories} = commify( int $hash->{total_calories} );

	return 1;
	}

=item daily_caloric_requirements( HASH_REF )

Input form values

	sex      'Male' or 'Female'
	height   in inches
	mheight  in inches from the metric pulldown
	measure   'Metric' or 'Imperial'
	weight   in pounds
	age      in years

Output values

	daily_caloric_requirements

=cut

sub daily_caloric_requirements
	{
	print "In daily_caloric_requirements\n" if $DEBUG;

	my $hash = shift;

	my $height = $hash->{height} || $hash->{mheight};

	my $weight = $hash->{weight};
	$weight *= KG_TO_LBS if $hash->{measure} eq METRIC;

	$hash->{title} = "Daily Caloric Requirements";

	@{$hash->{'ERROR_FIELDS'}}{qw( weight height age sex )} =
		[ @$hash{qw( pounds inches age sex )} ];

	if( $height < 20 || $height > 90 )
		{
		$hash->{ERROR_MSG}   = qq{The height you entered ($hash->{inches}) is out of range, valid heights are between 1'8" and 7'6" (US) or 1.4 m and 2.7 m.}; #"
		$hash->{ERROR_TITLE} = 'Bad Input';
		$hash->{ERROR_NAME}  = 'Invalid height';

		return;
		}

	if( (($hash->{weight} < 50 || $hash->{weight} > 950) &&  $hash->{measure} ne METRIC ) ||
		(($hash->{weight} < 22 || $hash->{weight} > 430) &&  $hash->{measure} eq METRIC ) )
		{
		$hash->{ERROR_MSG}   = qq{The weight you entered ($hash->{pounds}) is out of range, valid weights are between 50 and 950 pounds or 22 kg and 430 kg};
		$hash->{ERROR_TITLE} = 'Bad Input';
		$hash->{ERROR_NAME}  = 'Invalid weight';

		return;
		}

	if( $hash->{age} < 18 || $hash->{age} > 110 )
		{
		$hash->{ERROR_MSG}   = qq{The age you entered ($$hash{age}) is out of range, valid ages are between 18 and 110};
		$hash->{ERROR_TITLE} = 'Bad Input';
		$hash->{ERROR_NAME}  = 'Invalid age';

		return;
		}

	$hash->{daily_caloric_requirements} = do {
		if( $hash->{sex} eq MALE )
			{
			sprintf "%.2f",
				66.47 + 13.75 * $weight +
				         5.0  * $height -
				         6.76 * $hash->{age};
			}
		else
			{
			sprintf "%.2f",
				655.1 + 9.56 * $weight +
					    1.85 * $height -
					    4.68 * $hash->{age};
			}
		};

	return 1;
	}

=item frame_size( HASH_REF )

Input form values

    sex     'Male' or 'Female'
    height   in inches
    mheight  in inches from the metric pulldown
    measure   'Metric' or 'Imperial'

    wrist   in inches, possibly with decimal places (optional)
    elbow   in inches, possibly with decimal places

Output values

    ratio   height / wrist ratio, if wrist is specified
    size    'Small', 'Medium', or 'Large'

=cut

sub frame_size
	{
	my $hash = shift;

	@{$hash->{'ERROR_FIELDS'}}{qw( wrist elbow height sex )} =
		[ @$hash{ qw( wrist elbow height sex )} ];

	my $height = $hash->{height} || $hash->{mheight};

	{
	$^W = 0;
	if( $hash->{wrist} < 1 && $hash->{elbow} < 1 )
		{
		$hash->{ERROR_MSG}   = qq{You must enter a value for either wrist circumference or elbow breadth.};
		$hash->{ERROR_TITLE} = 'Bad Input';
		$hash->{ERROR_NAME}  = 'Invalid wrist/elbow';

		return;
		}

	if( $height < 20 || $height > 90 )
		{
		$hash->{ERROR_MSG}   = qq{The height you entered ($$hash{height}) is out of range, valid heights are between 1'8" and 7'6" (US) or 1.4 m and 2.7 m.}; #"
		$hash->{ERROR_TITLE} = 'Bad Input';
		$hash->{ERROR_NAME}  = 'Invalid height';

		return;
		}
	}

	if( $hash->{wrist} > 0)
		{
		$hash->{ratio} = eval { $height / $hash->{wrist} };

		$hash->{size} = do {
			if( $hash->{sex} eq MALE )
				{
				if(    $hash->{ratio} > 10.39 ) { "small" }
				elsif( $hash->{ratio} <  9.61 ) { "large" }
				}
			else
				{
				if(    $hash->{ratio} > 10.99 ) { "small" }
				elsif( $hash->{ratio} < 10.11 ) { "large" }
				}
			};

		$hash->{size} ||= "medium";
		}
	else
		{
		$hash->{size} = do {
			if( $hash->{sex} eq MALE )
				{
				if( ( $height <= '63' && $hash->{elbow} < 2.5   ) ||
					( $height <= '67' && $hash->{elbow} < 2.625 ) ||
					( $height <= '75' && $hash->{elbow} < 2.75  ) ||
					( $hash->{elbow}  < 2.875) )
					{
					"small";
					}
				elsif( ( $height <= '67' && $hash->{elbow} > 2.875 ) ||
					( $height <= '71' && $hash->{elbow} > 3     ) ||
					( $height <= '75' && $hash->{elbow} > 3.125 ) ||
					( $hash->{elbow}  > 3.25) )
					{
					"large";
					}
				}
			else
				{
				if( ( $height <= '63' && $hash->{elbow} < 2.25  ) ||
					( $height <= '71' && $hash->{elbow} < 2.375 ) ||
					( $hash->{elbow}  < 2.5))
					{
					"small";
					}
				elsif( ( $height <= '63' && $hash->{elbow} > 2.5   ) ||
					( $height <= '71' && $hash->{elbow} > 2.625 ) ||
					( $hash->{elbow}  > 2.75 ) )
					{
					"large";
					}
				}
			};

		$hash->{size} ||= 'medium';
		}

	return 1;
	}

=item ideal_weight( HASH_REF )

Input form values

	height      height in inches, from imperial pulldown
	mheight	    height in inches, from metric pulldown
	measure       METRIC or IMPERIAL

Output values

	low_weight
	mid_weight
	high_weight

=cut

sub ideal_weight
	{
	print "In ideal_weight\n" if $DEBUG;

	my $hash = shift;
	
	my $height = $hash->{height} || $hash->{mheight};

	if( $height < 20 || $height > 90 )
		{
		@{$hash->{'ERROR_FIELDS'}}{qw( height mheight )} =
			[ @$hash{qw( height mheight )} ];
		$hash->{ERROR_MSG}   = qq{The height you entered ($height") is out of range, valid heights are between 1'8" and 7'6" (US) or 1.4 m and 2.7 m.}; #"
		$hash->{ERROR_TITLE} = 'Bad Input';
		$hash->{ERROR_NAME}  = 'Invalid height';
		return;
		}

	my( $base, $factor ) = do {
		if( $hash->{sex} eq MALE ) { ( 106, 6 ) }
		else                       { ( 100, 5 ) }
		};

	# these values are in pounds
	my $hfactor = 1;
	if ($height > 90){
		$hash->{mid_weight} = $base + ( $factor	* ( $height - 60 ) );
		}
	else	{
		$hash->{mid_weight} = sprintf "%d",( 22.5 / 704.5  ) * $height**2;
		}

	@{$hash}{qw(low_weight high_weight)}
		= map { sprintf "%d", ( $_ / 704.5  ) * $height**2 } ( 20, 25 );

	# convert to kilograms if necessary
	@{$hash}{qw(low_weight high_weight mid_weight)}
		= map {  sprintf "%3.1f", ($_ / KG_TO_LBS ) }
		@{$hash}{qw(low_weight high_weight mid_weight)}
		if $hash->{measure} eq METRIC;

	return 1;
	}

=item lean_body_mass( HASH_REF )

Input form values

    weight   weight, in pounds or kilograms (see units)
    sex      'Male" or 'Female'
    height   height, in inches, from imperial pulldown
    mheight  height, in inches, from metric pulldown
    measure    METRIC or IMPERIAL

Output values

	lbm2
	ideal

=cut

sub lean_body_mass
	{
	print "In lean_body_mass\n" if $DEBUG;

	my $hash = shift;

	my $height = $hash->{height} || $hash->{mheight};

	my $weight = $hash->{weight};
	$weight *= KG_TO_LBS if $hash->{measure} eq METRIC;

	if( (($hash->{weight} < 50 || $hash->{weight} > 950) &&  $hash->{measure} ne METRIC ) ||
		(($hash->{weight} < 22 || $hash->{weight} > 430) &&  $hash->{measure} eq METRIC ) )
		{
		@{$hash->{'ERROR_FIELDS'}}{qw( sex height weight )} =
			[ @$hash{qw( sex height weight )} ];
		$hash->{ERROR_MSG}   = qq{The weight you entered ($$hash{weight}) is out of range, valid weights are between 50 and 950 pounds or 22 kg and 430 kg};
		$hash->{ERROR_TITLE} = 'Bad Input';
		$hash->{ERROR_NAME}  = 'Invalid weight';
		return;
		}

	if( $height < 20 || $height > 90 )
		{
		@{$hash->{'ERROR_FIELDS'}}{qw( sex height weight )} =
			[ @$hash{qw( sex height weight )} ];
		$hash->{ERROR_MSG}   = qq{The height you entered is out of range, valid heights are between 1'8" and 7'6" (US) or 1.4 m and 2.7 m.}; #"
		$hash->{ERROR_TITLE} = 'Bad Input';
		$hash->{ERROR_NAME}  = 'Invalid height';
		return;
		}

	my( $f1, $f2, $g1, $g2 ) = do {
		if( $hash->{sex} eq MALE ) { ( 1.10, 128, 50,   0.85 ) }
		else                       { ( 1.07, 148, 45.5, 0.78 ) }
		};

	my $weight1 = $weight * 0.454;
	my $height1 = $height * 2.54 / 100;

	print "formula is $f1, $weight1, $f2, $height1, $g1, $height, $g2\n" if $DEBUG;
	$hash->{lbm2}  = sprintf "%.2f",
		(($f1 * $weight1) - $f2 * ( $weight1**2 / ( 100*$height1 )**2 )) /.454;

	$hash->{ideal} = sprintf "%.2f", (($g1 + 2.3 * ($height - 60))/0.454 * $g2);

	print "Lean body mass is $$hash{lbm2}\n" if $DEBUG;

	if ($hash->{measure} eq METRIC)
		{
		@{ $hash }{ qw( lbm2 ideal ) } = map { sprintf "%3.1f", ($_ / KG_TO_LBS ) }
			@{ $hash }{ qw( lbm2 ideal ) };
		}

	return 1;
	}

=item lose_one_pound( HASH_REF )

Input form values

	weight   in pounds or kilograms
	measure    METRIC or IMPERIAL
	age

Output form values

	how_long - a hash whose keys are the activity descriptions
		and whose values are the time to burn a pound of fat

=cut

sub lose_one_pound
	{
	my $hash = shift;

	my $weight = $hash->{weight};
	$weight *= KG_TO_LBS if $hash->{measure} eq METRIC;

	if( (($hash->{weight} < 50 || $hash->{weight} > 950) &&  $hash->{measure} ne METRIC ) ||
		(($hash->{weight} < 22 || $hash->{weight} > 430) &&  $hash->{measure} eq METRIC ) )
		{
		@{$hash->{'ERROR_FIELDS'}}{qw( weight age )} =
			[ @$hash{qw( weight age )} ];
		$hash->{ERROR_MSG}   = qq{The weight you entered ($$hash{weight}) is out of range, valid weights are between 50 and 950 pounds or 22 kg and 430 kg};
		$hash->{ERROR_TITLE} = 'Bad Input';
		$hash->{ERROR_NAME}  = 'Invalid weight';
		return;
		}

	croak $Calorie_data_missing
		unless eval { require "calorie_data_lang.pl"; };

	my $measure = lc $hash->{measure} || 'imperial';
	my $language = lc $hash->{lang} || 'en';
	
	my( $calories, $description, $skip ) = get_calorie_data($measure, $language);

	my %skip_hash = %{$skip};


	foreach my $key ( keys %$calories )
		{
			if(!$hash->{'wholesome'} || ($hash->{'wholesome'} && !$skip_hash{$key})){
				$hash->{how_long}{ $description->{$key} }
					= int( 3500 / ($weight * $calories->{$key}) );
				}
		}

	return 1;
	}
=item lose_weight_calorie( HASH_REF )

Input form values

	weight   in pounds or kilograms
	measure    METRIC or IMPERIAL
	age
	number
	lose

Output form values

	how_long - a hash whose keys are the activity descriptions
		and whose values are the time to burn a pound of fat

=cut

sub lose_weight_calorie
	{
	my $hash = shift;

	my $calorie = $hash->{number};
	$calorie = 3500 * $hash->{number} if $hash->{lose} eq 'pound';
	$calorie = 7700 * $hash->{number} if $hash->{lose} eq 'kilogram';

	my $weight = $hash->{weight};
	$weight *= KG_TO_LBS if $hash->{measure} eq METRIC;

	if( (($hash->{weight} < 50 || $hash->{weight} > 950) &&  $hash->{measure} ne METRIC ) ||
		(($hash->{weight} < 22 || $hash->{weight} > 430) &&  $hash->{measure} eq METRIC ) )
		{
		@{$hash->{'ERROR_FIELDS'}}{qw( weight age )} =
			[ @$hash{qw( weight age )} ];
		$hash->{ERROR_MSG}   = qq{The weight you entered ($$hash{weight}) is out of range, valid weights are between 50 and 950 pounds or 22 kg and 430 kg};
		$hash->{ERROR_TITLE} = 'Bad Input';
		$hash->{ERROR_NAME}  = 'Invalid weight';
		return;
		}

	croak $Calorie_data_missing
		unless eval { require "calorie_data_lang.pl"; };
	my $measure = lc $hash->{measure} || 'imperial';	
	my $language = lc $hash->{lang} || 'en';	

	my( $calories1, $description, $skip ) = get_calorie_data($measure,$language);

	my %skip_hash = %{$skip};
	
	my $calories = $calories1->{$measure};

	foreach my $key ( keys %$calories )
		{
			if(!$hash->{'wholesome'} || ($hash->{'wholesome'} && !$skip_hash{$key}))
				{
				$hash->{how_long}{ $description->{$key} }
					= int( $calorie / ($weight * $calories->{$key}) );
				}
			
			if($hash->{how_long}{ $description->{$key} } > 60 )
				{
					my $how_long = $hash->{how_long}{ $description->{$key} };
					$hash->{how_long}{ $description->{$key} }= int($how_long/60) ." hours " . $how_long % 60  ; 
				}
			$hash->{how_long}{ $description->{$key} } .= " minutes";
		}

	return 1;
	}
=item lose_one_kilogram( HASH_REF )

Input form values

	weight   in pounds or kilograms
	measure    METRIC or IMPERIAL
	age

Output form values

	how_long - a hash whose keys are the activity descriptions
		and whose values are the time to burn a kilogram of fat

=cut

sub lose_one_kilogram
	{
	my $hash = shift;

	my $weight = $hash->{weight};
	$weight *= KG_TO_LBS if $hash->{measure} eq METRIC;

	if( (($hash->{weight} < 50 || $hash->{weight} > 950) &&  $hash->{measure} ne METRIC ) ||
		(($hash->{weight} < 22 || $hash->{weight} > 430) &&  $hash->{measure} eq METRIC ) )
		{
		@{$hash->{'ERROR_FIELDS'}}{qw( weight age )} =
			[ @$hash{qw( weight age )} ];
		$hash->{ERROR_MSG}   = qq{The weight you entered ($$hash{weight}) is out of range, valid weights are between 50 and 950 pounds or 22 kg and 430 kg};
		$hash->{ERROR_TITLE} = 'Bad Input';
		$hash->{ERROR_NAME}  = 'Invalid weight';
		return;
		}

	croak $Calorie_data_missing
		unless eval { require "calorie_data_lang.pl"; };

	my $measure = lc $hash->{measure} || 'imperial';
	my $language = lc $hash->{lang} || 'en';
	
	my( $calories, $description ) = get_calorie_data($measure,$language);

	foreach my $key ( keys %$calories )
		{
		$hash->{how_long}{ $description->{$key} }
			= int( 3500 * 2.2 / ($weight * $calories->{$key}) );
		}

	return 1;
	}

=item cigarette_cost( HASH_REF )

Input form values

    cigsaday
    cigsapack
    priceapack  in your local currency

Output values - as decimal numbers.  You have to add your own
currency symbols.

	smoker   1 (so future things know you tried a smoke related calc.
    cig1     number of cigs in one year
    cig3     number of cigs in three years
    cig5     number of cigs in five years
    year1    price of cigs in one year
    year3    price of cigs in three years
    year5    price of cigs in five years

=cut

sub cigarette_cost
	{
	print "In cigarette_cost\n" if $DEBUG;

	my $hash = shift;

	$hash->{smoker} = 1;

	@{$hash->{'ERROR_FIELDS'}}{qw( cigarettesperday cigarettesperpack priceperpack )} =
		[ @$hash{qw( cigarettesperday cigarettesperpack priceperpack )} ];

	if( $hash->{cigarettesperpack} < 1 )
		{
		$hash->{ERROR_MSG}   = qq{You must enter a number for number of cigarettes in each pack.};
		$hash->{ERROR_TITLE} = 'Bad Input';
		$hash->{ERROR_NAME}  = 'Invalid cigarettes per pack';
		return;
		}

	if( $hash->{cigarettesperday} < 1 )
		{
		$hash->{ERROR_MSG}   = qq{You must enter a number for number of cigarettes you smoke each day};
		$hash->{ERROR_TITLE} = 'Bad Input';
		$hash->{ERROR_NAME}  = 'Invalid cigarettes smoked each day';
		return;
		}

	if( $hash->{priceperpack} < 0.01 )
		{
		$hash->{ERROR_MSG}   = qq{You must enter an amount for the price per pack};
		$hash->{ERROR_TITLE} = 'Bad Input';
		$hash->{ERROR_NAME}  = 'Invalid price per pack';
		return;
		}

	my $price_per_year = $hash->{priceperpack}/$hash->{cigarettesperpack} *
		$hash->{cigarettesperday} * 365;

	@{ $hash }{ qw( cig1 cig3 cig5 ) } =
		map { $hash->{cigarettesperday} * 365 * $_ } qw( 1 3 5 );

	@{ $hash }{ qw( year1 year3 year5 ) } =
		map { sprintf "%.2f", $price_per_year * $_ }
			qw( 1 3 5 );

	return 1;
	}

=item target_heart_rate( HASH_REF )

Input form values

	age       in years

Output values as keys in HASH_REF, in beats/minute

	tmedlow
	tmedhigh
	tmed
	thigh

	tseclow
	tsecmhigh
	tsecmed
	tsechigh

=cut

sub target_heart_rate
	{
	print "In target_heart_rate\n" if $DEBUG;

	my $hash = shift;

	@{$hash->{'ERROR_FIELDS'}}{qw( age )} =
		[ @$hash{qw( age )} ];

	if( $hash->{age} < 18 || $hash->{age} > 110 )
		{
		$hash->{ERROR_MSG}   = qq{The age you entered ($$hash{age}) is out of range, valid ages are between 18 and 110};
		$hash->{ERROR_TITLE} = 'Bad Input';
		$hash->{ERROR_NAME}  = 'Invalid age';

		return;
		}

	my $base = 220 - $hash->{age};

	@{ $hash }{ qw( tmedlow tmedhigh tmed thigh ) } =
		map { int( $base * $_ ) } qw( 0.5 0.7 0.7 0.85 );

	@{ $hash }{ qw( tseclow tsecmhigh tsecmed tsechigh ) } =
		map { int( $_ / 6 ) } @{ $hash }{ qw( tmedlow tmedhigh tmed thigh ) };

	return 1;
	}

=item waist_hip_ratio( HASH_REF )

The input values of can be either imperial or metric measure since
we calculate the ratio.

Input form values

    sex     'Male' or 'Female'
    waist   waist circumference
    hip     hip circumference

Output values

    ratio   a unitless number
    shape   'pear' or 'apple'

=cut

sub waist_hip_ratio
	{
	print "In waist_hip_ratio\n" if $DEBUG;

	my $hash = shift;

	@{$hash->{'ERROR_FIELDS'}}{qw( waist hip sex )} =
		[ @$hash{qw( waist hip sex )} ];

	if( (($hash->{waist} < 10 || $hash->{waist} > 96) &&  $hash->{measure} ne METRIC ) ||
		(($hash->{waist} < 25 || $hash->{waist} > 243) &&  $hash->{measure} eq METRIC ) )
		{
		$hash->{ERROR_MSG}   = qq{The waist size you entered ($$hash{waist}) is out of range, valid waist sizes are between 10" and 96"}; #"
		$hash->{ERROR_TITLE} = 'Bad Input';
		$hash->{ERROR_NAME}  = 'Invalid waist size';
		return;
		}
	if( (($hash->{hip} < 10 || $hash->{hip} > 96) &&  $hash->{measure} ne METRIC ) ||
		(($hash->{hip} < 25 || $hash->{hip} > 243) &&  $hash->{measure} eq METRIC ) )
		{
		$hash->{ERROR_MSG}   = qq{The hip size you entered ($$hash{hip}) is out of range, valid hip sizes are between 10" and 96"}; #"
		$hash->{ERROR_TITLE} = 'Bad Input';
		$hash->{ERROR_NAME}  = 'Invalid hip size';
		return;
		}

	$hash->{ratio} = sprintf "%.2f", $hash->{waist} / $hash->{hip};

	$hash->{shape} = do {
		if( $hash->{sex} eq MALE )
			{
			if( $hash->{ratio} < 0.95 ) { 'pear'  }
			else                        { 'apple' }
			}
		else
			{
			if( $hash->{ratio} < 0.81 ) { 'pear'  }
			else                        { 'apple' }
			}
		};

	return 1;
	}

=item due_date

Input values

	cycle      date of next menstrual cycle, in mm/dd/yy

Output values

	conception
	fetal_risk
	fetal_risk_end
	organ_end
	organ_start
	first_trimester
	preemie_survival
	second_trimester
	due_date

=cut

sub due_date
	{
	my $hash = shift;

	return if $hash->{sex} eq MALE;

	my @date = parse_calc_date( $hash->{cycle} );
	return unless $#date == 2;  # XXX: blimey!  do this right!

	my $day = do { my $d = \@date;
		sub {  sprintf "%d/%d/%d", (
				Date::Calc::Add_Delta_YMD( @$d, 0, 0, $_[0] )
				)[1,2,0]
			}
		};

	my $input = 1;

	$hash->{conception}       = $day->( 14 );

	$hash->{fetal_risk}       = $day->(35);
	$hash->{fetal_risk_end}   = $day->(70);
	$hash->{organ_start}        = $day->(35);
	$hash->{organ_end}      = $day->(70);

	$hash->{first_trimester}  = $day->(84);
	$hash->{preemie_survival} = $day->(161);
	$hash->{second_trimester} = $day->(189);
	$hash->{due_date}         = $day->(280);

	return 1;
	}

=item ovulation

Input values

	cycle      date of next menstrual cycle, in mm/dd/yy
	days_in_cycle   average number of days in cycle

Output values

	ovulation_day   expected date of next ovulation

=cut

sub ovulation
	{
	my $hash = shift;

	return if $hash->{sex} eq MALE;

	my @date = parse_calc_date( $hash->{cycle} );
	return unless $#date == 2;  # XXX: blimey!  do this right!

	my $offset = $hash->{days_in_cycle} - 14;

	# cycle date + days in cycle - 14
	$hash->{ovulation_day} = sprintf "%d/%d/%d", (
		Date::Calc::Add_Delta_YMD( @date, 0, 0, $offset )
		)[1,2,0];

	return 1;
	}

=item parse_calc_date

The calculators expect dates in the format mm/dd/yyyy. This function
parses that date, checks to see if it is a valid date, and returns
the list ( YEAR, MONTH, DAY ).

On any failure, it returns the empty list.

The function croaks when used in scalar context (because you shouldn't
do that, and errors are subtle).

=cut

sub parse_calc_date
	{
	my $date = shift;

	croak "Can't can parse_calc_date in scalar context\n"
		unless wantarray;

	my @date = ( split m|/|, $date )[2,0,1];

	return unless eval { require Date::Calc; };

	return unless Date::Calc::check_date( @date );

	@date;
	}

1;

=back

=head1 BUGS

* nothing identified

=head1 TO DO

* some functions need work on their input checking

=head1 AUTHOR

brian d foy <bdfoy@cpan.org>,
Greg White <gwhite@healthstatus.com>

=head1 COPYRIGHT

Copyright 2001-2005, HealthStatus.com

=cut
