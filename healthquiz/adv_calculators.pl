# $Id: calculators.pl,v 1.2 2002/12/05 08:47:31 healthst Exp $
use strict;



use Carp qw(croak);

use constant MALE      => 'Male';
use constant METRIC    => 'Metric';
use constant KG_TO_LBS => 2.2046;

my $DEBUG = 0;

# AUDIT alcohol score
sub alcohol_calc
	{
	my $hash = shift;
        $hash->{'alcohol'}=$hash->{drink1}+$hash->{drink2}+$hash->{drink3}+$hash->{drink4}+$hash->{drink5}+$hash->{drink6}+$hash->{drink7}+$hash->{drink8}+$hash->{drink9}+$hash->{drink10};
        $hash->{'alcoholic'} = $hash->{'alcohol'}>=8?1:0;
	return 1;
	}
# attention deficit disorder
sub adult_sr
	{
	my $hash = shift;
        $hash->{'adultsr'}=$hash->{challengingparts}+$hash->{organization}+$hash->{appointments}+$hash->{delay}+$hash->{restless}+$hash->{feeloverly};
	$hash->{'adultsr_frequent'} += $hash->{challengingparts}>=3?1:0;
	$hash->{'adultsr_frequent'} += $hash->{organization}>=3?1:0;
	$hash->{'adultsr_frequent'} += $hash->{appointments}>=3?1:0;
	$hash->{'adultsr_frequent'} += $hash->{delay}>=3?1:0;
	$hash->{'adultsr_frequent'} += $hash->{restless}>=3?1:0;
	$hash->{'adultsr_frequent'} += $hash->{feeloverly}>=3?1:0;
	$hash->{'adultsr_adult'} += $hash->{challengingparts}>=2?1:0;
	$hash->{'adultsr_adult'} += $hash->{organization}>=2?1:0;
	$hash->{'adultsr_adult'} += $hash->{appointments}>=2?1:0;
	$hash->{'adultsr_adult'} += $hash->{delay}>=3?1:0;
	$hash->{'adultsr_adult'} += $hash->{restless}>=3?1:0;
	$hash->{'adultsr_adult'} += $hash->{feeloverly}>=3?1:0;
	$hash->{'adultsr_adhd'} = $hash->{adultsr_adult}>=4?1:0;
	return 1;
	}


sub copd_as
	{
	    my $hash = shift;
	     $hash->{age}>70?$hash->{copd_as}+= 11:$hash->{copd_as}+=0;
	     $hash->{age}>60?$hash->{copd_as}+= 9:$hash->{copd_as}+=0;
	     $hash->{age}>50?$hash->{copd_as}+= 5:$hash->{copd_as}+=0;
	     $hash->{packs}>=50?$hash->{copd_as}+= 9:$hash->{copd_as}+=0;
	     $hash->{packs}>=25?$hash->{copd_as}+= 7:$hash->{copd_as}+=0;
	     $hash->{packs}>=15?$hash->{copd_as}+= 3:$hash->{copd_as}+=0;
	     $hash->{sputumproduced}>=15?$hash->{copd_as}+= 4:$hash->{copd_as}+=0;
	     $hash->{copd_as}+=$hash->{breathingproblems};
	     $hash->{copd_as}+=$hash->{admithospital};
	     $hash->{copd_as}+=$hash->{shortbreath};
	     $hash->{copd_as}+=$hash->{cold};
	     $hash->{copd_as}+=$hash->{treatment};
	     return 1;
	}

sub copd_dx
	{
	    my $hash = shift;
	    my $packsperyear = $hash->{years} * $hash->{packsperday};
	    my $height = $hash->{height} || $hash->{mheight};
	    my $square = $height**2;
	    my $weight = $hash->{weight};
	    $weight *= KG_TO_LBS if $hash->{measure} eq METRIC;

	    my $bmi = sprintf "%3.1f", $weight / $square * 704.5;

	    if( $hash->{age}>70 ){ $hash->{copd_dx}+= 10; }
	    elsif( $hash->{age}>60 ){ $hash->{copd_dx}+= 8; }
	    elsif( $hash->{age}>50 ){ $hash->{copd_dx}+= 4; }

	    if( $packsperyear>=50 ){ $hash->{copd_dx}+= 7; }
	    elsif( $packsperyear>=25 ){ $hash->{copd_dx}+= 3; }
	    elsif( $packsperyear>=15 ){ $hash->{copd_dx}+= 2; }

	    if( $bmi>=29.7 ){ $hash->{copd_dx}+= 0; }
	    elsif( $bmi>=25.4 ){ $hash->{copd_dx}+= 1; }
	    elsif( $bmi<25.4 ){ $hash->{copd_dx}+= 5; }

	    $hash->{copd_dx}+=$hash->{cold};
	    $hash->{copd_dx}+=$hash->{morning};
	    $hash->{copd_dx}+=$hash->{allergies};
	    $hash->{copd_dx}+=$hash->{cough};
	    $hash->{copd_dx}+=$hash->{wheezing};

	    return 1;
	}

sub dmdi
	{
	    my $hash = shift;
	    $hash->{dmdi} = $hash->{lowspirits}+$hash->{lossofinterest}+$hash->{energy}+$hash->{selfconfident}+$hash->{guilt}+$hash->{depress1}+$hash->{concentrating}+$hash->{sleeping};
	    $hash->{dmdi} += ($hash->{restless}>$hash->{subdued})?$hash->{restless}:$hash->{subdued};
	    $hash->{dmdi} += ($hash->{appetite}>$hash->{increased})?$hash->{appetite}:$hash->{increased};
	    $hash->{ats} = $hash->{dmdi}*2/100;
	    $hash->{high_freq} += ($hash->{lowspirits}>=4)?1:0;
	    $hash->{high_freq} += ($hash->{lossofinterest}>=4)?1:0;
	    $hash->{high_freq} += ($hash->{energy}>=4)?1:0;
	    $hash->{high_freq} += ($hash->{selfconfident}>=4)?1:0;
	    $hash->{high_freq} += ($hash->{guilt}>=4)?1:0;
	    $hash->{high_freq} += ($hash->{depress1}>=4)?1:0;
	    $hash->{high_freq} += ($hash->{concentrating}>=4)?1:0;
	    $hash->{high_freq} += ($hash->{sleeping}>=4)?1:0;
	    $hash->{high_freq} += ($hash->{restless}>=4)?1:$hash->{subdued}>=4?1:0;
	    $hash->{high_freq} += $hash->{appetite}>4?1:$hash->{increased}>4?1:0;
	    $hash->{b42} = $hash->{depress1}>=4?1:0;
	    $hash->{b42} += $hash->{lossofinterest}>=4?1:0;
	    $hash->{b43} = $hash->{b42};
	    $hash->{b43} += $hash->{energy}>=4?1:0;
	    $hash->{b44} = ($hash->{selfconfident}>=4)?1:0;
	    $hash->{b44} += ($hash->{guilt}>=4)?1:0;
	    $hash->{b44} += ($hash->{depress1}>=4)?1:0;
	    $hash->{b44} += ($hash->{concentrating}>=4)?1:0;
	    $hash->{b44} += $hash->{restless}>4?1:$hash->{subdued}>4?1:0;
	    $hash->{b44} += ($hash->{sleeping}>=4)?1:0;
	    $hash->{b44} += $hash->{appetite}>4?1:$hash->{increased}>4?1:0;
	    $hash->{b45} = ($hash->{depress1}>=4)?1:0;
	    $hash->{b45} += ($hash->{lowspirits}>=4)?1:0;
	    $hash->{b45} += ($hash->{lossofinterest}>=4)?1:0;
	    $hash->{b45} += ($hash->{energy}>=4)?1:0;
	    $hash->{b45} += $hash->{selfconfident}>4?1:$hash->{guilt}>4?1:0;
	    $hash->{b45} += ($hash->{concentrating}>=4)?1:0;
	    $hash->{b45} += $hash->{restless}>4?1:$hash->{subdued}>4?1:0;
	    $hash->{b45} += ($hash->{sleeping}>=4)?1:0;
	    $hash->{b45} += $hash->{appetite}>4?1:$hash->{increased}>4?1:0;
	    $hash->{dmdi_level} = do {
	    	if($hash->{b43}==3 && $hash->{b44}>=5)		{ "severe" }
	    	elsif($hash->{b43}==2 && $hash->{b44}>=4)	{ "moderate" }
	    	elsif($hash->{b43}==2 && $hash->{b44}>=2)	{ "mild" }
	    	else						{ "no" }
	    	};
	    $hash->{dmdi_dsmiv} = do {
	    	if($hash->{b42}>=1 && $hash->{b45}>=5)	{ 1 }
	    	else					{ 0 }
	    	};
	    return 1;
	}

sub dwho
{
    my $hash = shift;
    $hash->{dwho} = $hash->{cheerful}+$hash->{relaxed}+$hash->{vigorous}+$hash->{feelingfresh}+$hash->{dailylife};
    $hash->{cps} = $hash->{dwho}*4;
    $hash->{poorwellbeing} = ($hash->{cheerful}<=1)?1:0;
    $hash->{poorwellbeing} += ($hash->{relaxed}<=1)?1:0;
    $hash->{poorwellbeing} += ($hash->{vigorous}<=1)?1:0;
    $hash->{poorwellbeing} += ($hash->{feelingfresh}<=1)?1:0;
    $hash->{poorwellbeing} += ($hash->{dailylife}<=1)?1:0;
    $hash->{pre_test} = $hash->{depression}/100;
    $hash->{not_depressed} = ($hash->{pre_test}/(1-$hash->{pre_test})) * ((0.11/(($hash->{pre_test}/(1-$hash->{pre_test})))*0.11+1));
    $hash->{depressed} = ($hash->{pre_test}/(1-$hash->{pre_test})) * ((2.58/(($hash->{pre_test}/(1-$hash->{pre_test})))*2.58+1));
    return 1;
}

sub edisorder
{
    my $hash = shift;
    $hash->{edisorder} = $hash->{feeluncomfortable}+$hash->{eatingworry}+$hash->{stone}+$hash->{fat}+$hash->{fooddominates};
    $hash->{badeater} = $hash->{edisorder}>=2?1:0;
    return 1;
}
sub lbw
{
    my $hash = shift;
    $hash->{lbw} = $hash->{painintensity}+$hash->{personalcare}+$hash->{lifting}+$hash->{walking}+$hash->{sitting}+$hash->{standing}+$hash->{sleeping}+$hash->{sexlife}+$hash->{sociallife}+$hash->{travelling};
    $hash->{disability} = $hash->{lbw}/50;
    if( $hash->{disability} > 0.8 ) { $hash->{backscore} = 5 }
    elsif( $hash->{disability} > 0.6 ) { $hash->{backscore} = 4 }
    elsif( $hash->{disability} > 0.4 ) { $hash->{backscore} = 3 }
    elsif( $hash->{disability} > 0.2 ) { $hash->{backscore} = 2 }
    else { $hash->{backscore} = 1 }

    return 1;
}
sub leisure_exercise
{
    my $hash = shift;
    $hash->{lex} = (9*$hash->{strenuously})+(5*$hash->{moderately})+(3*$hash->{mildly});
    $hash->{sweat_freq} = ($hash->{sweat}==1)?'good':($hash->{sweat}==2)?'fair':'poor';
    return 1;
}
sub motion_sick
{
    my $hash = shift;
    my %risk;
    $risk{1}{1}=1;
    $risk{1}{2}=0;
    $risk{1}{3}=0;
    $risk{1}{4}=0;
    $risk{1}{5}=0;
    $risk{2}{1}=2;
    $risk{2}{1}=0;
    $risk{2}{1}=2;
    $risk{2}{1}=3;
    $risk{2}{1}=4;
    $risk{3}{1}=3;
    $risk{3}{2}=0;
    $risk{3}{3}=4;
    $risk{3}{4}=5;
    $risk{3}{5}=6;
    $risk{4}{1}=4;
    $risk{4}{1}=0;
    $risk{4}{1}=6;
    $risk{4}{1}=7;
    $risk{4}{1}=8;
    $risk{5}{1}=5;
    $risk{5}{1}=0;
    $risk{5}{1}=8;
    $risk{5}{1}=9;
    $risk{5}{1}=10;
    $hash->{transportation}= $hash->{cars}+$hash->{buses}+$hash->{trains}+$hash->{airplanes}+$hash->{small_boats}+$hash->{ships}+$hash->{swingsk}+$hash->{rotating_rides}+$hash->{gaint_swing_rides};
    $hash->{subscore} += $hash->{car_feeling} = $risk{$hash->{nauseated1}}{$hash->{cars}};
    $hash->{subscore} += $hash->{bus_feeling} = $risk{$hash->{nauseated2}}{$hash->{buses}};
    $hash->{subscore} += $hash->{train_feeling} = $risk{$hash->{nauseated3}}{$hash->{trians}};
    $hash->{subscore} += $hash->{airplanes_feeling} = $risk{$hash->{nauseated4}}{$hash->{airplanes}};
    $hash->{subscore} += $hash->{boats_feeling} = $risk{$hash->{nauseated5}}{$hash->{small_boats}};
    $hash->{subscore} += $hash->{ships_feeling} = $risk{$hash->{nauseated6}}{$hash->{ships}};
    $hash->{subscore} += $hash->{swing_feeling} = $risk{$hash->{nauseated7}}{$hash->{swingsk}};
    $hash->{subscore} += $hash->{rotating_rides_feeling} = $risk{$hash->{nauseated8}}{$hash->{rotating_rides}};
    $hash->{subscore} += $hash->{swing_rides_feeling} = $risk{$hash->{nauseated9}}{$hash->{gaint_swing_rides}};
    $hash->{subscore} += $hash->{car_vomit} = $risk{$hash->{vomited1}}{$hash->{cars}};
    $hash->{subscore} += $hash->{bus_vomit} = $risk{$hash->{vomited2}}{$hash->{buses}};
    $hash->{subscore} += $hash->{train_vomit} = $risk{$hash->{vomited3}}{$hash->{trians}};
    $hash->{subscore} += $hash->{airplanes_vomit} = $risk{$hash->{vomited4}}{$hash->{airplanes}};
    $hash->{subscore} += $hash->{boats_vomit} = $risk{$hash->{vomited5}}{$hash->{small_boats}};
    $hash->{subscore} += $hash->{ships_vomit} = $risk{$hash->{vomited6}}{$hash->{ships}};
    $hash->{subscore} += $hash->{swing_vomit} = $risk{$hash->{vomited7}}{$hash->{swingsk}};
    $hash->{subscore} += $hash->{rotating_rides_vomit} = $risk{$hash->{vomited8}}{$hash->{rotating_rides}};
    $hash->{subscore} += $hash->{swing_rides_vomit} = $risk{$hash->{vomited9}}{$hash->{gaint_swing_rides}};
    $hash->{final_subscore} = ($hash->{subscore}/$hash->{transportation})*9;
    $hash->{final_subscore_percentage} = ($hash->{final_subscore}/180)*100;
    return 1;
}

sub vod
{
    my $hash = shift;
    $hash->{vod}  = $hash->{whiledriving}+$hash->{familymembers}+$hash->{othercars}+$hash->{seeingsigns}+$hash->{otherdrivers}+$hash->{honk}+$hash->{drivingstresses}+$hash->{afterdriving}+$hash->{nearmisses}+$hash->{intersections}+$hash->{lefthand}+$hash->{headlights}+$hash->{dizzy}+$hash->{steeringwheel}+$hash->{gaspedal}+$hash->{shoulder}+$hash->{police}+$hash->{rides}+$hash->{night}+$hash->{parking};
    $hash->{capacity} = ($hash->{vod}>=1)?'yes':'not at this time';
    return 1;
}

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
