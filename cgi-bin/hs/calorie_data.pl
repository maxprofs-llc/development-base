# $Id: calorie_data.pl,v 1.1.1.1 2007/09/05 13:56:07 gwhite Exp $

=head1 NAME

calorie_data.pl

=head1 SYNOPSIS

	require calorie_data.pl
	
	my $activity = 'T1';
	
	my( $calories, $description ) = get_calorie_data();

	my $factor      = $calories->{$activity};
	my $description = $description->{$activity};
	
=head1 DESCRIPTION

This library provides one function, get_calorie_data,
which returns two hash references.  The first contains
activity and calorie factor data, and the second contains
activity descriptions for the keys in the first hash.

=head1 AUTHOR

brian d foy, E<lt>bdfoy@cpan.orgE<lt>

=head1 COPYRIGHT

Copyright 2002, HealthStatus.com, All rights reserved

=cut

# a couple of routines use the same data, so here's
# a common way to get it.
sub get_calorie_data
	{
	my $measure = shift;

	my %calories = qw(
			   T1  .046   T2  .053
			   T3  .053   T4  .066
			   T5  .064   T6  .136
			   T7  .169   T8  .053
			   T9  .053  T10  .086
			  T11  .053  T12  .08
			  T13  .073  T14  .021
			  T15  .033  T16  .039
			  T17  .026  T18  .046
			  T19  .062  T20  .083
			  T21  .066  T22  .08
			  T23  .034  T24  .07
			  T25  .073  T26  .066
			  T27  .046  T28  .026
			  T29  .038  T30  .069
			  T31  .086  T32  .066
			  T33  .046  T34  .074
			  T35  .046  T36  .032
			  T37  .033  T38  .026
			  T39  .046  T40  .041
			  T41  .022  T42  .033
			  T43  .011  T44  .032
			  T45  .018  T46  .046
			  T47  .008  T48  .007
			  T49  .026  T50  .053
			  T51  .034  T52  .053
			  T53  .034  T54  .030
			  T55  .019  T56  .023
			  T57  .091  T58  .045
			  T59  .038  T60  .019
			  T61  .034  T62  .061
			  T63  .042  T64  .023
			  T65  .045  T66  .023
			  T67  .091  T68  .045
			  T69  .061  T70  .038
			  T71  .076  T72  .038
			  T73  .045  T74  .053
			  T75  .030  T76  .030
			  T77  .076  T78  .076
			  T79  .087  T80  .102
			  T81  .030  T82  .061
			  T83  .030  T84  .064
			  T85  .030  T86  .019
			  T87  .023  T88  .045
			  T89  .019  T90  .049
			  T91  .061  T92  .030
			  T93  .053  T94  .076
			  T95  .038  T96  .045
			  T97  .052  T98  .026
			  T99  .053  T100 .076
			  T101 .038  T102 .023
			  T103 .030  T104 .083
			  T105 .086  T106 .061
			  T107 .019  T108 .017
			  T109 .034  T110 .038
			  T111 .021  T112 .050
			  T113 .034  T114 .017
			  T115 .020  T116 .016
			  T117 .024  T118 .008
			  T119 .032  T120 .009
			  T121 .014  T122 .008
			  T123 .008  T124 .020 
			  T125 .028  T126 .056 
			  T127 .028  T128 .012 
			  T129 .012  T130 .024 
			  T131 .016  T132 .032 
			  T133 .044  T134 .020 
			  T135 .036  T136 .040 
			  T137 .028  T138 .020 
			  T139 .020  T140 .028
			  T141 .064  T142 .040
			  T143 .016  T144 .040 
			  T145 .040  T146 .080 
			  T147 .064 
			  );
			  
my %caldesc;
unless(lc $measure eq 'metric'){
	%caldesc = ("T1" => "Aerobics - low impact",
			   "T2" => "Aerobics - high impact",
			   "T3" => "Rowing Machine - moderate",
			   "T4" => "Rowing Machine - vigorous",
			   "T5" => "Running 5 mph",
			   "T6" => "Running 10 mph",
			   "T7" => "Running 12 mph",
			   "T8" => "Stair Step Machine",
			   "T9" => "Stationary Bicycle - moderate",
			  "T10" => "Stationary Bicycle - vigorous",
			  "T11" => "Step Aerobics - low impact",
			  "T12" => "Step Aerobics - high impact",
			  "T13" => "Ski Machine",
			  "T14" => "Walking 2 mph",
			  "T15" => "Walking 3 mph",
			  "T16" => "Walking 4 mph",
			  "T17" => "Weight lifting - general",
			  "T18" => "Weight lifting - vigorous",
			  "T19" => "Basketball 1/2 court",
			  "T20" => "Basketball full court",
			  "T21" => "Bicycling 12-14 mph",
			  "T22" => "Bicycling 14-16 mph",
			  "T23" => "Canoeing 2 mph",
			  "T24" => "Canoeing 4 mph",
			  "T25" => "Football - full contact",
			  "T26" => "Football - touch",
			  "T27" => "Golf - carry clubs",
			  "T28" => "Golf - cart",
			  "T29" => "Skating - moderate",
			  "T30" => "Skating - vigorous",
			  "T31" => "Skiing - cross country",
			  "T32" => "Skiing - downhill",
			  "T33" => "Swimming - moderate",
			  "T34" => "Swimming - vigorous",
			  "T35" => "Tennis - singles",
			  "T36" => "Tennis - doubles",
			  "T37" => "Volleyball - competitive",
			  "T38" => "Volleyball - recreation",
			  "T39" => "Chop Wood",
			  "T40" => "Garden",
			  "T41" => "Housework",
			  "T42" => "Mowing - push",
			  "T43" => "Sex - foreplay",
			  "T44" => "Sex - intercourse",
			  "T45" => "Shopping",
			  "T46" => "Shovel Snow",
			  "T47" => "Sitting",
			  "T48" => "Sleeping",
			  "T49" => "Archery",
			  "T50" => "Backpacking",
			  "T51" => "Badminton",
			  "T52" => "Basketball - officiating",
			  "T53" => "Basketball - shooting baskets",
			  "T54" => "Bicycling - leisure",
			  "T55" => "Billiards",
			  "T56" => "Bowling",
			  "T57" => "Boxing - in ring",
			  "T58" => "Boxing - punching bag",
			  "T59" => "Cricket",
			  "T60" => "Croquet",
			  "T61" => "Calisthenics - moderate",
			  "T62" => "Calisthenics - vigorous",
			  "T63" => "Dancing - fast ballroom",
			  "T64" => "Dancing - ballroom slow",
			  "T65" => "Fencing",
			  "T66" => "Fishing",
			  "T67" => "Handball",
			  "T68" => "Hiking",
			  "T69" => "Hockey",
			  "T70" => "Hunting",
			  "T71" => "Judo - martial arts",
			  "T72" => "Kayaking",
			  "T73" => "Dancing - aerobic, ballet, modern",
			  "T74" => "Jogging",
			  "T75" => "Raking lawn",
			  "T76" => "Walk/run play with kids",
			  "T77" => "Rope jumping",
			  "T78" => "Running 6 mph",
			  "T79" => "Running 7 mph",
			  "T80" => "Running 8 mph",
			  "T81" => "Stretching",
			  "T82" => "Walking - up stairs",
			  "T83" => "Water Aerobics",
			  "T84" => "Bicycling - Mountain",
			  "T85" => "Coaching - team sports",
			  "T86" => "Football - playing catch",
			  "T87" => "Frisbee playing",
			  "T88" => "Horse grooming",
			  "T89" => "Horseback riding - walking",
			  "T90" => "Horseback riding - trotting",
			  "T91" => "Horseback riding - galloping",
			  "T92" => "Paddleboat",
			  "T93" => "Racquetball casual",
			  "T94" => "Racquetball competitive",
			  "T95" => "Skateboarding",
			  "T96" => "Skiing - water",
			  "T97" => "Sledding, toboganning",
			  "T98" => "Snowmobiling",
			  "T99" => "Soccer casual",
			 "T100" => "Soccer competitive",
			 "T101" => "Softball or baseball",
			 "T102" => "Surfing",
			 "T103" => "Table tennis",
			 "T104" => "Rock climbing",
			 "T105" => "Elliptical trainer",
			 "T106" => "Repelling",
			 "T107" => "Brush teeth",
			 "T108" => "Ironing",
			 "T109" => "Mopping",
			 "T110" => "Painting House",
			 "T111" => "Playing Piano",
			 "T112" => "Rearranging Furniture",
			 "T113" => "Washing car",
			 "T114" => "Washing dishes",
			 "T115" => "Cooking",
			 "T116" => "Driving",
			 "T117" => "Playing Guitar",
			 "T118" => "Reading",
			 "T119" => "Showering",
			 "T120" => "Standing",
			 "T121" => "Studying",
			 "T122" => "Talking on phone",
			 "T123" => "Writing",			 
			 "T124" => "Hairstyling",
			 "T125" => "Hang Gliding",
			 "T126" => "Backpacking",
			 "T127" => "Carrying an Infant",
			 "T128" => "Card playing",
			 "T129" => "Playing board games",
			 "T130" => "Loading/Unloading a car",
			 "T131" => "Touring/Traveling",
			 "T132" => "Elder care, Disabled adult",
			 "T133" => "Construction/Remodeling",
			 "T134" => "Push stroller with child",
			 "T135" => "Farming/Feeding livestock",
			 "T136" => "Hopscotch/Dodge ball",
			 "T137" => "Carpentry/Workshop",
			 "T138" => "Putting away Groceries",
			 "T139" => "Tailoring, Cutting",
			 "T140" => "Weaving cloth",			 
			 "T141" => "Frisbee, Ultimate",
			 "T142" => "Cleaning Gutters",
			 "T143" => "Packing Suitcase",
			 "T144" => "Using Crutches",
			 "T145" => "Snorkeling",
			 "T146" => "Rugby",
			 "T147" => "Lacrosse",
			  );
	}
else	{

	%caldesc = ("T1" => "Aerobics - low impact",
			   "T2" => "Aerobics - high impact",
			   "T3" => "Rowing Machine - moderate",
			   "T4" => "Rowing Machine - vigorous",
			   "T5" => "Running 8 kph",
			   "T6" => "Running 16 kph",
			   "T7" => "Running 19 kph",
			   "T8" => "Stair Step Machine",
			   "T9" => "Stationary Bicycle - moderate",
			  "T10" => "Stationary Bicycle - vigorous",
			  "T11" => "Step Aerobics - low impact",
			  "T12" => "Step Aerobics - high impact",
			  "T13" => "Ski Machine",
			  "T14" => "Walking 3 kph",
			  "T15" => "Walking 5 kph",
			  "T16" => "Walking 6.5 kph",
			  "T17" => "Weight lifting - general",
			  "T18" => "Weight lifting - vigorous",
			  "T19" => "Basketball 1/2 court",
			  "T20" => "Basketball full court",
			  "T21" => "Bicycling 19-22 kph",
			  "T22" => "Bicycling 22-26 kph",
			  "T23" => "Canoeing 3 kph",
			  "T24" => "Canoeing 6.5 kph",
			  "T25" => "Football - full contact",
			  "T26" => "Football - touch",
			  "T27" => "Golf - carry clubs",
			  "T28" => "Golf - cart",
			  "T29" => "Skating - moderate",
			  "T30" => "Skating - vigorous",
			  "T31" => "Skiing - cross country",
			  "T32" => "Skiing - downhill",
			  "T33" => "Swimming - moderate",
			  "T34" => "Swimming - vigorous",
			  "T35" => "Tennis - singles",
			  "T36" => "Tennis - doubles",
			  "T37" => "Volleyball - competitive",
			  "T38" => "Volleyball - recreation",
			  "T39" => "Chop Wood",
			  "T40" => "Garden",
			  "T41" => "Housework",
			  "T42" => "Mowing - push",
			  "T43" => "Sex - foreplay",
			  "T44" => "Sex - intercourse",
			  "T45" => "Shopping",
			  "T46" => "Shovel Snow",
			  "T47" => "Sitting",
			  "T48" => "Sleeping",
			  "T49" => "Archery",
			  "T50" => "Backpacking",
			  "T51" => "Badminton",
			  "T52" => "Basketball - officiating",
			  "T53" => "Basketball - shooting baskets",
			  "T54" => "Bicycling - leisure",
			  "T55" => "Billiards",
			  "T56" => "Bowling",
			  "T57" => "Boxing - in ring",
			  "T58" => "Boxing - punching bag",
			  "T59" => "Cricket",
			  "T60" => "Croquet",
			  "T61" => "Calisthenics - moderate",
			  "T62" => "Calisthenics - vigorous",
			  "T63" => "Dancing - fast ballroom",
			  "T64" => "Dancing - ballroom slow",
			  "T65" => "Fencing",
			  "T66" => "Fishing",
			  "T67" => "Handball",
			  "T68" => "Hiking",
			  "T69" => "Hockey",
			  "T70" => "Hunting",
			  "T71" => "Judo - martial arts",
			  "T72" => "Kayaking",
			  "T73" => "Dancing - aerobic, ballet, modern",
			  "T74" => "Jogging",
			  "T75" => "Raking lawn",
			  "T76" => "Walk/run play with kids",
			  "T77" => "Rope jumping",
			  "T78" => "Running 9.6 kph",
			  "T79" => "Running 11.2 kph",
			  "T80" => "Running 12.8 kph",
			  "T81" => "Stretching",
			  "T82" => "Walking - up stairs",
			  "T83" => "Water Aerobics",
			  "T84" => "Bicycling - Mountain",
			  "T85" => "Coaching - team sports",
			  "T86" => "Football - playing catch",
			  "T87" => "Frisbee playing",
			  "T88" => "Horse grooming",
			  "T89" => "Horseback riding - walking",
			  "T90" => "Horseback riding - trotting",
			  "T91" => "Horseback riding - galloping",
			  "T92" => "Paddleboat",
			  "T93" => "Racquetball casual",
			  "T94" => "Racquetball competitive",
			  "T95" => "Skateboarding",
			  "T96" => "Skiing - water",
			  "T97" => "Sledding, toboganning",
			  "T98" => "Snowmobiling",
			  "T99" => "Soccer casual",
			 "T100" => "Soccer competitive",
			 "T101" => "Softball or baseball",
			 "T102" => "Surfing",
			 "T103" => "Table tennis",
			 "T104" => "Rock climbing",
			 "T105" => "Elliptical trainer",
			 "T106" => "Repelling",
			 "T107" => "Brush teeth",
			 "T108" => "Ironing",
			 "T109" => "Mopping",
			 "T110" => "Painting House",
			 "T111" => "Playing Piano",
			 "T112" => "Rearranging Furniture",
			 "T113" => "Washing car",
			 "T114" => "Washing dishes",
			 "T115" => "Cooking",
			 "T116" => "Driving",
			 "T117" => "Playing Guitar",
			 "T118" => "Reading",
			 "T119" => "Showering",
			 "T120" => "Standing",
			 "T121" => "Studying",
			 "T122" => "Talking on phone",
			 "T123" => "Writing",			 
			 "T124" => "Hairstyling",
			 "T125" => "Hang Gliding",
			 "T126" => "Backpacking",
			 "T127" => "Carrying an Infant",
			 "T128" => "Card playing",
			 "T129" => "Playing board games",
			 "T130" => "Loading/Unloading a car",
			 "T131" => "Touring/Traveling",
			 "T132" => "Elder care, Disabled adult",
			 "T133" => "Construction/Remodeling",
			 "T134" => "Push stroller with child",
			 "T135" => "Farming/Feeding livestock",
			 "T136" => "Hopscotch/Dodge ball",
			 "T137" => "Carpentry/Workshop",
			 "T138" => "Putting away Groceries",
			 "T139" => "Tailoring, Cutting",
			 "T140" => "Weaving cloth",			 
			 "T141" => "Frisbee, Ultimate",
			 "T142" => "Cleaning Gutters",
			 "T143" => "Packing Suitcase",
			 "T144" => "Using Crutches",
			 "T145" => "Snorkeling",
			 "T146" => "Rugby",
			 "T147" => "Lacrosse",
			  );
	}
	my %skip_these = (
			"T43" => 1,
			"T44" => 1
			);
	return ( \%calories, \%caldesc, \%skip_these );
	}

1;
