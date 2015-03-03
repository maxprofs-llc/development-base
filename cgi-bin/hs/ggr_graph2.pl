sub prepare_graphs_arg_pdf
{
	my ( $input, $GGR_PAGE_DIR, $assessments_ref, $assessment_count_ref, $font_dir, $blank_data, $PARMS_ref, $COMPPARMS_ref, $GROUP_ref, $COMPGROUP_ref, $hra_cnt, $config ) = @_;

	my @assessment_count = @$assessment_count_ref;
	my %PARMS = %{$PARMS_ref};
	my %COMPPARMS = %{$COMPPARMS_ref};
	my %GROUP = %{$GROUP_ref};
	my %COMPGROUP = %{$COMPGROUP_ref};
	my @assessments = @{$assessments_ref};
	my %assessments_chk;
	my %empty_chart;
	foreach ( @assessments ) { $assessments_chk{uc $_} = 1; }

#	my $isComparative = 1;# if $PARMS{comparative} == 2;
	my $isComparative = 1 if $PARMS{comparative} == 2;

#print "Is comparitive = $isComparative <br>";
	my $show_numbers =1;

	$PARMS{'files_prefix'} =~ s/\///g;
	

	my @graph_files = qw ( ggr_risks_ach.png ggr_age.png ggr_ta.png ggr_disease.png ggr_factors.png ggr_risks.png ggr_sm.png ggr_alc.png ggr_flu.png ggr_wt.png
		ggr_mammo.png ggr_pap.png ggr_breast_self.png ggr_prostate.png ggr_prostate50.png ggr_exer.png ggr_sb.png ggr_chol.png ggr_bp.png ggr_diabrisks.png ggr_cardrisks.png
		ggr_fit.png ggr_gwb.png ggr1_gwb.png ggr_srd.png ggr_srfh.png ggr_gluc.png ggr_hga1c.png ggr_ldl.png ggr_trig.png ggr_days.png ggr_colon.png ggr_general.png ggr_hdl.png ggr_heart.png
		ggr_waist.png ggr_diet.png);

	foreach (@graph_files){ copy ($blank_data, $GGR_PAGE_DIR . $PARMS{'files_prefix'} . '_' . $_) or die "$! - " . $blank_data . " graphics initialization of " . $GGR_PAGE_DIR . $PARMS{'files_prefix'} . '_' . $_ . " error"; my $x=chmod 0777, $GGR_PAGE_DIR . $PARMS{'files_prefix'} . '_' . $_; }

# set each report_page to being empty, then we will turn them "on" as we produce a graph for each, this gets passed along so we don't print blank data pages (unless the user wants to

	my @report_page = qw ( print_achievable print_risklevels print_agegroups print_totalassessments print_preventable print_riskfactors print_smoking print_alcohol print_weight print_mammogram
		print_pap print_breast_self print_prostate print_exercise print_seatbelts print_cholesterol print_bloodpressure print_diabetes print_cardiac print_fitness print_wellbeing print_wellbeing2
		print_selfreported print_familyhistory print_colon_exam print_days_missed print_general_exam print_glucose print_ldl print_triglycerides print_hga1c print_hdl print_flu print_market
		print_heart print_waist print_diet);

	foreach (@report_page){ $empty_chart{$_} = 1; }

	my $bars_preferred = 1;
	my $silent = 0;
	my $custom = 0;
	my $manual_crc = 0;
	my $manual_drc = 0;

	my $graph_cnt = 0;
	my $message = "<br />";
	if($config{ggr_ajax}){
#		print qq|<script language="javascript" type="text/javascript"> document.getElementById('ggr_file').innerHTML=$message; </script>|;
		}
	else	{
#		print $message;
		}


	my ( $pie_chartwide, $pie_charthigh, $pie_text_right, $pie_text_top, $pie_centerx,
	     $pie_centery, $pie_size, $pie_centerx_small, $pie_centery_small, $pie_size_small,
	     $pie_legendx_small, $pie_legendy_small, $pie_background,);

	$pie_chartwide = 390;
	$pie_charthigh = 332;
	$pie_centerx = 147;
	$pie_centery = 160;
	$pie_size = 135;
	$pie_text_right = 235;
	$pie_text_top = 1;
	$pie_background = $GGR_PAGE_DIR . "pie_bg.png";
	$pie_centerx_small = 107;
	$pie_centery_small = 160;
	$pie_size_small = 95;
	$pie_legendx_small = 204;
	$pie_legendy_small = 22;
	my ( $bar_chartwide, $bar_charthigh, $bar_text_right, $bar_text_top, $bar_centerx, $bar_centery, $bar_size, $bargap);
	$comp_bar_chartwide = 350;
	$comp_bar_charthigh = 290;
	$bar_chartwide = 350;
	$bar_charthigh = 320;
	$bar_centerx = 143;
	$bar_centery = 185;
	$bar_size = 140;
	$bar_text_right = 200;
	$bar_text_top = 2;
	$bargap = $perlchartdir::TouchBar;
	$wbar_chartwide = 450;
	$wbar_charthigh = 310;

#	my $five_colors = [0xa1b69a, 0xadaa8e, 0xe7cfa5, 0x9bb1be, 0xcb8368];
	my $five_colors = [0x9bb1be, 0x9bb1be, 0x9bb1be, 0x9bb1be, 0x9bb1be, 0x9bb1be, 0x9bb1be];
	my $ten_colors = [0x9bb1be, 0x9bb1be, 0x9bb1be, 0x9bb1be, 0x9bb1be, 0x9bb1be, 0x9bb1be, 0x9bb1be, 0x9bb1be, 0x9bb1be, 0x9bb1be, 0x9bb1be, 0x9bb1be, 0x9bb1be];
#	my $ten_colors = [0x9bb1be, 0xcb8368, 0xadaa8e, 0xffe19b, 0xbab1bc, 0x95b4de, 0xa1b69a, 0xb07661, 0x907577, 0xe7cfa5 ];
	my $twelve_colors = [0x9bb1be, 0x9bb1be, 0x9bb1be, 0x9bb1be, 0x9bb1be, 0x9bb1be, 0x9bb1be, 0x9bb1be, 0x9bb1be, 0x9bb1be, 0x9bb1be, 0x9bb1be];
	my $five_colors = [0x9bb1be, 0x9bb1be, 0x9bb1be, 0x9bb1be, 0x9bb1be, 0x9bb1be, 0x9bb1be];

#1 Achievable Risks
	if ( ($input->{'pgraphs'} eq 'all' || $input->{'print_achievable'} == 1) &&
		($assessments_chk{GHA} || $assessments_chk{HRA} || $assessments_chk{OHA} ))
		{
		++$graph_cnt;
		print $graph_cnt.". Achievable risks<br>" unless $silent;
		### Achievable Group levels
		my $o_file = $GGR_PAGE_DIR . $PARMS{'files_prefix'} . '_ggr_risks_ach.png';

		my ($alparm, $amparm, $ahparm, $avparm, $albasis);
		$albasis = $PARMS{'ach_low'} + $PARMS{'ach_moderate'} + $PARMS{'ach_medium'} + $PARMS{'ach_high'};

		my ($comp_alparm, $comp_amparm, $comp_ahparm, $comp_avparm, $comp_albasis);
		$comp_albasis = $COMPPARMS{'ach_low'} + $COMPPARMS{'ach_moderate'} + $COMPPARMS{'ach_medium'} + $COMPPARMS{'ach_high'};

		if( $albasis )
			{
			$alparm = sprintf("%.1f",($PARMS{'ach_low'}/$albasis * 100));
			$amparm = sprintf("%.1f",($PARMS{'ach_moderate'}/$albasis * 100));
			$ahparm = sprintf("%.1f",($PARMS{'ach_medium'}/$albasis * 100));
			$avparm = sprintf("%.1f",($PARMS{'ach_high'}/$albasis * 100));

			if($isComparative && $comp_albasis){
				$comp_alparm = sprintf("%.1f",($COMPPARMS{'ach_low'}/$comp_albasis * 100));
				$comp_amparm = sprintf("%.1f",($COMPPARMS{'ach_moderate'}/$comp_albasis * 100));
				$comp_ahparm = sprintf("%.1f",($COMPPARMS{'ach_medium'}/$comp_albasis * 100));
				$comp_avparm = sprintf("%.1f",($COMPPARMS{'ach_high'}/$comp_albasis * 100));
				}

			# The data for the pie chart
			my @data_list;
			my @labels_list;
			my @labels1_list;
			my $numbers;
			my $data;
			my $labels;
			my $labels1;
			if($bars_preferred){
				$numbers = [ $PARMS{'ach_low'}, $PARMS{'ach_moderate'}, $PARMS{'ach_medium'}, $PARMS{'ach_high'} ];
				$data = [ $alparm,       $amparm,   $ahparm,  $avparm ];
				$markdata = [ $comp_alparm,       $comp_amparm,   $comp_ahparm,  $comp_avparm ] if $isComparative;
				$labels = ["Low Risk", "Moderate\nRisk", "High Risk", "Very High"];
				}
			else	{
				# The labels for the pie chart
				my $labels_tmp = ["Very High", "High Risk", "Moderate Risk", "Low Risk"];
				my %data_hash;
				$data_hash{"Very High"} = $avparm;
				$data_hash{"High Risk"} = $ahparm;
				$data_hash{"Moderate Risk"} = $amparm;
				$data_hash{"Low Risk"} = $alparm;
				foreach my $label (sort { $data_hash{$a} <=> $data_hash{$b} } keys %data_hash) {
					if ( $data_hash{$label}  > .01) {
						push @data_list, $data_hash{$label};
						push @labels_list, $label;
						push @labels1_list, $data_hash{$label};
						}
					}
				$data = \@data_list;
				$labels = \@labels_list;
				$labels1 = \@labels1_list;
				}

			my $d;
			my $legendBox;
			my $textbox;
			my $labellayer;
			my $markLayer;
			my $layer;
			unless ($bars_preferred){
				# Create a PieChart object
			# ** needs editing to be a $d object
				my $c = new PieChart($pie_chartwide, $pie_charthigh);

				# Set the center of the pie at (x, y) and the radius
				$c->setPieSize($pie_centerx_small, $pie_centery_small, $pie_size_small);

				$c->addText($pie_text_right, $pie_text_top, "<*block,linespacing=.7, halign=right*>Participants achievable\nrisk levels<*/*>", "arial.ttf", 9, 0x000000,9);

				#$c->addTitle("Custom Colors");
				# set the LineColor to light gray
				$c->setColor($perlchartdir::LineColor, 0xc0c0c0);
				# use given color array as the data colors (sector colors)
				$c->setColors2($perlchartdir::DataColor, $five_colors);
				$c->setBgImage($pie_background, 7);

				$c->setStartAngle(25);
				$c->setLabelStyle("arial.ttf", 7);
				$c->setLabelFormat("{label}<*br*>{percent|1}%");

				# Set the pie data and the pie labels
				$c->setData($data, $labels);
				$c->getDrawArea()->setPaletteMode($perlchartdir::ForcePalette);

				my $sum = 0;
				foreach (@$data) {  $sum += $_; }
				my $cutoff = 0;
				for (my $i = 0; $i < scalar(@$data); ++$i) {
					$cutoff += $$data[$i]/$sum;
					$c->sector($i)->setLabelStyle("arial.ttf", 7);
					if ($$data[$i]/$sum < 0.07 || $cutoff < .42) {
						 $c->sector($i)->setLabelLayout($perlchartdir::SideLayout);
						 $c->sector($i)->setJoinLine(0x000000);
						 $c->sector($i)->setLabelFormat("{label} - {percent|1}%");
						}
					else 	{
						 $c->sector($i)->setLabelLayout(1,-40);
						 $c->sector($i)->setLabelFormat("{label}<*br*>{percent|1}%");
						}

					}
				}
			else	{
				# create the bar chart
				$d = new XYChart($bar_chartwide, $bar_charthigh, 0xffffff);

				$d->setPlotArea(90, 50, 255, 180, $perlchartdir::Transparent, -1, $perlchartdir::Transparent, 0xe0e0e0);

				my $title = $d->addTitle2(8, "Participants achievable risk levels", "arial.ttf", 12);

				if($isComparative && $comp_albasis){
					$legendBox = $d->addLegend($d->getWidth() / 2, $title->getHeight()-7, "arial.ttf", 8);
					$legendBox->setBackground($perlchartdir::Transparent, $perlchartdir::Transparent);
					$legendBox->setAlignment($perlchartdir::TopCenter);
					$legendBox->setLineStyleKey();
					}


#				$textbox = $d->yAxis()->setTitle("% of Participants");
				# $textbox->setFontStyle("arial.ttf");
				# $textbox->setFontSize(7);
				$d->yAxis()->setLabelFormat("{value}%");

				$d->xAxis()->setLabels($labels);
				$d->xAxis()->setTickLength(0);
				$d->yAxis()->setLinearScale(0,100,20);

				# Convert the labels on the x-axis to a CDMLTable
				my $table = $d->xAxis()->makeLabelTable();
				# Set the default top/bottom margins of the cells to 3 pixels
				$table->getStyle()->setMargin2(0, 0, 3, 3);
				# Use Arial Bold as the font for the first row
				$table->getRowStyle(0)->setFontStyle("arial.ttf");
				$table->getRowStyle(0)->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent);
				$table->appendRow()->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent);
				$table->appendRow()->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent);
				for(my $i = 0; $i < scalar(@$data); ++$i) {
					$table->setText($i, 2, $data->[$i].'%');
					}
				$table->appendRow()->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent) if($show_numbers);
				for(my $i = 0; $i < scalar(@$numbers); ++$i) {
					$table->setText($i, 3, $numbers->[$i]) if($show_numbers);
					}
				$table->insertCol(0)->setMargin2(5, 5, 3, 3);
				$table->setText(0, 0, "Risk Level");
				$table->setText(0, 2, "% of Participants");
				$table->setText(0, 3, "# of Participants") if($show_numbers);


				if($isComparative && $comp_albasis){
					$labellayer = $d->addBarLayer($data, $perlchartdir::Transparent);
					$labellayer->setBorderColor($perlchartdir::Transparent);
					# $labellayer->setAggregateLabelFormat("{value|1}%");
					#  $labellayer->setAggregateLabelStyle("arial.ttf", 7) ;

					$markLayer = $d->addBoxWhiskerLayer(undef, undef, undef, undef, $markdata, -1, 0x333333);
					$markLayer->setLineWidth(2);
#					$markLayer->setDataGap(0.4);
					# Add the legend key for the mark line
					$legendBox->addKey("Comparative Group", 0x333333, 2);

					$layer = $d->addBarLayer3($data, $five_colors);$layer->setBarGap($bargap);
					$layer->setBorderColor(0x000033);
					}
				else	{
					$layer = $d->addBarLayer3($data, $five_colors, $labels);
					$layer->setBarGap($bargap);
					$layer->setBorderColor(0x000033);
					#  $layer->setAggregateLabelFormat("{value|1}%");
#					# $layer->setAggregateLabelStyle("arial.ttf", 7) ;
					}
				}

			$d->getDrawArea()->setPaletteMode($perlchartdir::ForcePalette);

			if( !$d->makeChart($o_file) )
				{
					copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
				}
			else	{
					$empty_chart{print_achievable} = 0;
				}
			}
		else	{
				copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
			}

		}

#2  Group Risk
	if (($input->{'pgraphs'} eq 'all' || $input->{'print_risklevels'} == 1) &&
		($assessments_chk{GHA} || $assessments_chk{HRA} || $assessments_chk{OHA} ))
		{
		++$graph_cnt;
		print $graph_cnt.". Group risk<br>" unless $silent;
		my $o_file = $GGR_PAGE_DIR . $PARMS{'files_prefix'} . "_ggr_risks.png";

		my ($lparm, $mparm, $hparm, $vparm, $b4_basis);
		$b4_basis = $PARMS{'low'} + $PARMS{'moderate'} + $PARMS{'medium'} + $PARMS{'high'};

		my ($comp_lparm, $comp_mparm, $comp_hparm, $comp_vparm, $comp_lbasis);
		$comp_basis = $COMPPARMS{'low'} + $COMPPARMS{'moderate'} + $COMPPARMS{'medium'} + $COMPPARMS{'high'};

		if( $b4_basis )
			{
			$lparm = sprintf("%.1f",($PARMS{'low'}/$b4_basis * 100));
			$mparm = sprintf("%.1f",($PARMS{'moderate'}/$b4_basis * 100));
			$hparm = sprintf("%.1f",($PARMS{'medium'}/$b4_basis * 100));
			$vparm = sprintf("%.1f",($PARMS{'high'}/$b4_basis * 100));

			if( $isComparative && $comp_basis) {
				$comp_lparm = sprintf("%.1f",($COMPPARMS{'low'}/$comp_basis * 100));
				$comp_mparm = sprintf("%.1f",($COMPPARMS{'moderate'}/$comp_basis * 100));
				$comp_hparm = sprintf("%.1f",($COMPPARMS{'medium'}/$comp_basis * 100));
				$comp_vparm = sprintf("%.1f",($COMPPARMS{'high'}/$comp_basis * 100));
				}

			if ($hparm > 33 || $vparm > 33 || $vparm+$hparm > 50)
				{
				$PARMS{'group_msg'}='Your group is at higher risk levels than average.  It is important that you work to educate the participants of their elevated risks and how to bring them down to a more desireable level';
				}
			else
				{
				$PARMS{'group_msg'}='Your group is doing well in controlling risks.  Continue to provide opportunities for those in the high risk and very high risk groups to reduce risky behaviors.';
				}



			# The labels for the pie chart
			my $labels_tmp = ["Very High", "High Risk", "Moderate Risk", "Low Risk"];
			my %data_hash;
			$data_hash{"Very High"} = $vparm;
			$data_hash{"High Risk"} = $hparm;
			$data_hash{"Moderate Risk"} = $mparm;
			$data_hash{"Low Risk"} = $lparm;

			# The data for the pie chart
			my @data_list;
			my @labels_list;
			my $data;
			my $labels;
			if($bars_preferred){
				$numbers = [ $PARMS{'low'}, $PARMS{'moderate'}, $PARMS{'medium'}, $PARMS{'high'} ];
				$data = [ $lparm,       $mparm,   $hparm,  $vparm ];
				$markdata = [ $comp_lparm,       $comp_mparm,   $comp_hparm,  $comp_vparm ] if $isComparative;
				$labels = ["Low Risk", "Moderate Risk", "High Risk", "Very High"];
				}
			else	{
				foreach my $label (sort { $data_hash{$a} <=> $data_hash{$b} } keys %data_hash) {
					if ( $data_hash{$label}  > .01) {
						push @data_list, $data_hash{$label};
						push @labels_list, $label;
						}
					}
				$data = \@data_list;
				$labels = \@labels_list;
				}
			my $d;
			my $legendBox;
			my $textbox;
			my $labellayer;
			my $markLayer;
			my $layer;
			unless ($bars_preferred){
				# Create a PieChart object
			# ** needs editing to be a $d object

				# Create a PieChart object
				my $c = new PieChart($pie_chartwide, $pie_charthigh);

				# Set the center of the pie at (x, y) and the radius
	#			$c->setPieSize($pie_centerx, $pie_centery, $pie_size);
				$c->setPieSize($pie_centerx_small, $pie_centery_small, $pie_size_small);

				$c->addText($pie_text_right, $pie_text_top, "<*block,linespacing=.7, halign=right*>Current health\nrisk levels<*/*>", "arial.ttf", 9, 0x000000,9);

				#$c->addTitle("Custom Colors");
				# set the LineColor to light gray
				$c->setColor($perlchartdir::LineColor, 0xc0c0c0);
				# use given color array as the data colors (sector colors)
				$c->setColors2($perlchartdir::DataColor, $five_colors);
				$c->setBgImage($pie_background, 7);

	#			$c->addLegend($pie_legendx_small, $pie_legendy_small);
	#			$c->setLabelLayout($perlchartdir::SideLayout);

				$c->setStartAngle(25);
				$c->setLabelStyle("arial.ttf", 7);

				# Set the pie data and the pie labels
				$c->getDrawArea()->setPaletteMode($perlchartdir::ForcePalette);

				#set data to pie chart as usual
				$c->setData($data, $labels);

				my $sum = 0;
				foreach (@$data) {  $sum += $_; }
				my $cutoff = 0;
				for (my $i = 0; $i < scalar(@$data); ++$i) {
				     $cutoff += $$data[$i]/$sum;
				     $c->sector($i)->setLabelStyle("arial.ttf", 7);
				     if ($$data[$i]/$sum < 0.07 || $cutoff < .42) {
					 $c->sector($i)->setLabelLayout($perlchartdir::SideLayout);
					 $c->sector($i)->setJoinLine(0x000000);
					 $c->sector($i)->setLabelFormat("{label} - {percent|1}%");
				     }
				     else {
					 $c->sector($i)->setLabelLayout(1,-40);
					 $c->sector($i)->setLabelFormat("{label}<*br*>{percent|1}%");
				     }

				}
				}
			else	{
				# create the bar chart
				$d = new XYChart($bar_chartwide, $bar_charthigh, 0xffffff);

				$d->setPlotArea(90, 50, 255, 180, $perlchartdir::Transparent, -1, $perlchartdir::Transparent, 0xe0e0e0);

				my $title = $d->addTitle2(8, "Current health risk levels", "arial.ttf", 12);

				if($isComparative && $comp_basis){
					$legendBox = $d->addLegend($d->getWidth() / 2, $title->getHeight()-7, "arial.ttf", 8);
					$legendBox->setBackground($perlchartdir::Transparent, $perlchartdir::Transparent);
					$legendBox->setAlignment($perlchartdir::TopCenter);
					$legendBox->setLineStyleKey();
					}


#				$textbox = $d->yAxis()->setTitle("% of Participants");
				# $textbox->setFontStyle("arial.ttf");
				# $textbox->setFontSize(7);
				$d->yAxis()->setLabelFormat("{value}%");

				$d->xAxis()->setLabels($labels);
				$d->xAxis()->setTickLength(0);
				$d->yAxis()->setLinearScale(0,100,20);

				# Convert the labels on the x-axis to a CDMLTable
				my $table = $d->xAxis()->makeLabelTable();
				# Set the default top/bottom margins of the cells to 3 pixels
				$table->getStyle()->setMargin2(0, 0, 3, 3);
				# Use Arial Bold as the font for the first row
				$table->getRowStyle(0)->setFontStyle("arial.ttf");
				$table->getRowStyle(0)->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent);
				$table->appendRow()->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent);
				$table->appendRow()->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent);
				for(my $i = 0; $i < scalar(@$data); ++$i) {
					$table->setText($i, 2, $data->[$i].'%');
					}
				$table->appendRow()->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent) if($show_numbers);
				for(my $i = 0; $i < scalar(@$numbers); ++$i) {
					$table->setText($i, 3, $numbers->[$i]) if($show_numbers);
					}
				$table->insertCol(0)->setMargin2(5, 5, 3, 3);
				$table->setText(0, 0, "Risk Level");
				$table->setText(0, 2, "% of Participants");
				$table->setText(0, 3, "# of Participants") if($show_numbers);


				if($isComparative && $comp_basis){
					$labellayer = $d->addBarLayer($data, $perlchartdir::Transparent);
					$labellayer->setBorderColor($perlchartdir::Transparent);
					# $labellayer->setAggregateLabelFormat("{value|1}%");
					#  $labellayer->setAggregateLabelStyle("arial.ttf", 7) ;

					$markLayer = $d->addBoxWhiskerLayer(undef, undef, undef, undef, $markdata, -1, 0x333333);
					$markLayer->setLineWidth(2);
					#  $markLayer->setDataGap(0.1);
					# Add the legend key for the mark line
					$legendBox->addKey("Comparative Group", 0x333333, 2);

					$layer = $d->addBarLayer3($data, $five_colors);$layer->setBarGap($bargap);
					$layer->setBorderColor(0x000033);

					}
				else	{
					$layer = $d->addBarLayer3($data, $five_colors, $labels);  $layer->setBarGap($bargap);
					$layer->setBorderColor(0x000033);
					#  $layer->setAggregateLabelFormat("{value|1}%");
					# $layer->setAggregateLabelStyle("arial.ttf", 7) ;
					}
				}
			$d->getDrawArea()->setPaletteMode($perlchartdir::ForcePalette);

			if( !$d->makeChart($o_file) )
				{
					copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
				}
			else	{
					$empty_chart{print_risklevels} = 0;
				}
			}
		else	{
				copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
			}

		}

#3 Age Groups
	if ($input->{'pgraphs'} eq 'all' || $input->{'print_agegroups'} == 1)
		{
		++$graph_cnt;
		print $graph_cnt.". Age groups<br>" unless $silent;
		####  Age Range by sex
		my $o_file = $GGR_PAGE_DIR . $PARMS{'files_prefix'} . "_ggr_age.png";
		my $comp_age_basis = ($COMPPARMS{'m_lt_19'}+$COMPPARMS{'m_20_29'}+$COMPPARMS{'m_30_39'}+$COMPPARMS{'m_40_49'}+$COMPPARMS{'m_50_59'}+$COMPPARMS{'m_60'}+$COMPPARMS{'f_lt_19'}+$COMPPARMS{'f_20_29'}+$COMPPARMS{'f_30_39'}+$COMPPARMS{'f_40_49'}+$COMPPARMS{'f_50_59'}+$COMPPARMS{'f_60'});

		if(my $age_basis = ($PARMS{'m_lt_19'}+$PARMS{'m_20_29'}+$PARMS{'m_30_39'}+$PARMS{'m_40_49'}+$PARMS{'m_50_59'}+$PARMS{'m_60'}+$PARMS{'f_lt_19'}+$PARMS{'f_20_29'}+$PARMS{'f_30_39'}+$PARMS{'f_40_49'}+$PARMS{'f_50_59'}+$PARMS{'f_60'}))
			{

			my $legendBox;
			my $labellayer;
			my $markLayer;
			my $layer;
			my $comp_male_data;
			my $comp_female_data;

			my $male_data = [(int($PARMS{'m_lt_19'}/$age_basis*100)), (int($PARMS{'m_20_29'}/$age_basis*100)), (int($PARMS{'m_30_39'}/$age_basis*100)), (int($PARMS{'m_40_49'}/$age_basis*100)), (int($PARMS{'m_50_59'}/$age_basis*100)), (int($PARMS{'m_60'}/$age_basis*100))];
			my $female_data = [(int($PARMS{'f_lt_19'}/$age_basis*100)), (int($PARMS{'f_20_29'}/$age_basis*100)), (int($PARMS{'f_30_39'}/$age_basis*100)), (int($PARMS{'f_40_49'}/$age_basis*100)), (int($PARMS{'f_50_59'}/$age_basis*100)), (int($PARMS{'f_60'}/$age_basis*100))];
			if($isComparative && $comp_age_basis){
				$comp_male_data = [(int($COMPPARMS{'m_lt_19'}/$comp_age_basis*100)), (int($COMPPARMS{'m_20_29'}/$comp_age_basis*100)), (int($COMPPARMS{'m_30_39'}/$comp_age_basis*100)), (int($COMPPARMS{'m_40_49'}/$comp_age_basis*100)), (int($COMPPARMS{'m_50_59'}/$comp_age_basis*100)), (int($COMPPARMS{'m_60'}/$comp_age_basis*100))];
				$comp_female_data = [(int($COMPPARMS{'f_lt_19'}/$comp_age_basis*100)), (int($COMPPARMS{'f_20_29'}/$comp_age_basis*100)), (int($COMPPARMS{'f_30_39'}/$comp_age_basis*100)), (int($COMPPARMS{'f_40_49'}/$comp_age_basis*100)), (int($COMPPARMS{'f_50_59'}/$comp_age_basis*100)), (int($COMPPARMS{'f_60'}/$comp_age_basis*100))];
				}
			my $labels = ["<19",  "20-29", "30-39", "40-49", "50-59", "60+"];

			my $c = new XYChart(250, $bar_charthigh, $perlchartdir::Transparent);
			my $c1 = new XYChart(250, $bar_charthigh, $perlchartdir::Transparent);

			$c->setPlotArea(50, 0, 180, 205, $perlchartdir::Transparent, -1, $perlchartdir::Transparent, 0xe0e0e0);

			$c1->setPlotArea(50, 0, 180, 205, $perlchartdir::Transparent, -1, $perlchartdir::Transparent, 0xe0e0e0);

			# Swap the axis so that the bars are drawn horizontally
			$c->swapXY(1);
			$c1->swapXY(1);
			$c1->yAxis()->setReverse();

			$c->addText(248, 0, "Female", "arial.ttf", 11, 0xcfa9cf)->setAlignment($perlchartdir::TopRight);
			$c1->addText(20, 0, "Male", "arial.ttf", 11, 0x9bb1be);

			# $textbox->setFontStyle("arial.ttf");
			# $textbox->setFontSize(7);
			$c->yAxis()->setLabelFormat("{value}%");
			$c1->yAxis()->setLabelFormat("{value}%");

			# Set the y axis label font to Arial Bold
			$c->yAxis()->setLabelStyle("arial.ttf");
			$c1->yAxis()->setLabelStyle("arial.ttf");

			my $tb = $c->xAxis()->setLabels($labels);
			$tb->setSize(60, 0);
			$tb->setAlignment($perlchartdir::Center);

			# Set the label font to Arial Bold
			$tb->setFontStyle("arial.ttf");

			# Disable ticks on the x-axis by setting the tick length to 0
			$c->xAxis()->setTickLength(0);
			$c1->xAxis()->setTickLength(0);
			$c->xAxis()->setColors($perlchartdir::Transparent);

			if($isComparative && $comp_age_basis){
				$markLayer = $c->addBoxWhiskerLayer(undef, undef, undef, undef, $comp_female_data, -1, 0x333333);
				$markLayer->setLineWidth(2);
				$labellayer = $c->addBarLayer($data, $perlchartdir::Transparent);   $labellayer->setBarGap($bargap);
				$labellayer->setBorderColor($perlchartdir::Transparent);
				}

			my $femalelayer = $c->addBarLayer2($perlchartdir::Stack);
			$femalelayer->addDataSet($female_data, 0xcfa9cf, "Females");
			$femalelayer->setBorderColor(0xcfa9cf);
			$c->addLineLayer($male_data, $perlchartdir::Transparent);

			if($isComparative && $comp_age_basis){
				$mmarkLayer = $c1->addBoxWhiskerLayer(undef, undef, undef, undef, $comp_male_data, -1, 0x333333);
				$mmarkLayer->setLineWidth(2);
				$mlabellayer = $c1->addBarLayer($data, $perlchartdir::Transparent);   $mlabellayer->setBarGap($bargap);
				$mlabellayer->setBorderColor($perlchartdir::Transparent);
				}

			my $malelayer = $c1->addBarLayer2($perlchartdir::Stack);
			$malelayer->addDataSet($male_data, 0x9bb1be, "Males");
			$malelayer->setBorderColor(0x9bb1be);
			$c1->addLineLayer($female_data, $perlchartdir::Transparent);

			# Create a MultiChart object of size 590 x 320 pixels.
			my $m = new MultiChart(530, 290, 0xffffff);

			# Add a title to the chart using Arial Bold Italic font
			my $title = $m->addTitle("Age groups", "arial.ttf");

			if($isComparative && $comp_age_basis){
				$legendBox = $m->addLegend($m->getWidth() / 2, $title->getHeight()-12, "arial.ttf", 8);
				$legendBox->setBackground($perlchartdir::Transparent, $perlchartdir::Transparent);
				$legendBox->setAlignment($perlchartdir::TopCenter);
				$legendBox->setLineStyleKey();
				$legendBox->addKey("Comparative Group", 0x333333, 2);
				}
			# Add another title at the bottom using Arial Bold Italic font
			$m->addTitle2($perlchartdir::Bottom, "Percentage of Participants", "arial.ttf", 10);

			# Put the left chart at (0, 35)
			$m->addChart(0, 35, $c1);

			# Put the right chart at (270, 35)
			$m->addChart(235, 35, $c);


			if( !$m->makeChart($o_file) )
				{
					copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
				}
			else	{
					$empty_chart{print_agegroups} = 0;
				}
			}
		else	{
				copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
			}

		}
#4 Total Assessments
	if ($input->{'pgraphs'} eq 'all' || $input->{'print_totalassessments'} == 1)
		{
		++$graph_cnt;
 		print "$graph_cnt. Total assessments<br>" unless $silent;
		#### Total Assessments Taken  #######
		my $o_file = $GGR_PAGE_DIR . $PARMS{'files_prefix'} . "_ggr_ta.png";

			my @a_data;
			my @c_data;
			my @comp_assessment_count=();
			my $comp_a_basis;
			foreach (@$assessments_ref){ push @a_data, $assessment_names_short{$_}; }
			if($isComparative){
				foreach (@$assessments_ref)
					{
					my $t = $_ . '_cnt';
					#print "$assessment_names{$_} = $COMPPARMS{$t}<br>";
					push (@comp_assessment_count, $COMPPARMS{$t});
					$comp_a_basis += $COMPPARMS{$t};
					}

					foreach (@$assessments_ref){ push @c_data, $assessment_names_short{$_}; }
				}

			my $data = \@assessment_count;
			my $markdata = \@comp_assessment_count if ($isComparative);

			my $labels = \@a_data;

			#my $label_count = @a_data;

			my $c = new XYChart($bar_chartwide, $bar_charthigh, 0xffffff);

			$c->setPlotArea(90, 50, 255, 180, $perlchartdir::Transparent, -1, $perlchartdir::Transparent, 0xe0e0e0);

			my $title = $c->addTitle2(8, "Assessments", "arial.ttf", 12);

			my $labellayer;
			my $legendbox;
			my $marklayer;
			my $layer;
			
			if($isComparative && $comp_a_basis){
					$legendBox = $c->addLegend($c->getWidth() / 2, $title->getHeight()-7, "arial.ttf", 8);
					$legendBox->setBackground($perlchartdir::Transparent, $perlchartdir::Transparent);
					$legendBox->setAlignment($perlchartdir::TopCenter);
					$legendBox->setLineStyleKey();
				}


#			my $textbox = $c->yAxis()->setTitle("Number Taken");
			# $textbox->setFontStyle("arial.ttf");
			# $textbox->setFontSize(7);
			$c->yAxis()->setLabelFormat("{value}");

			$c->xAxis()->setLabels($labels);
 			#$c->xAxis()->setLabelStyle("arialbd.ttf", 7, 0x000000, 45) if ($label_count > 3);
 			#$c->xAxis()->setLabelStyle("arial.ttf", 7) if ($label_count <= 3);
			$c->xAxis()->setTickLength(1);

				# Convert the labels on the x-axis to a CDMLTable
				my $table = $c->xAxis()->makeLabelTable();
				# Set the default top/bottom margins of the cells to 3 pixels
				$table->getStyle()->setMargin2(0, 0, 3, 3);
				# Use Arial Bold as the font for the first row
				$table->getRowStyle(0)->setFontStyle("arial.ttf");
				$table->getRowStyle(0)->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent);
				$table->appendRow()->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent);
				$table->appendRow()->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent);
				for(my $i = 0; $i < scalar(@$data); ++$i) {
					$table->setText($i, 2, $data->[$i]);
					}
				$table->insertCol(0)->setMargin2(5, 5, 3, 3);
				$table->setText(0, 0, "Assessment");
				$table->setText(0, 2, "# of Participants");

			if($isComparative && $comp_a_basis){
				$labellayer = $c->addBarLayer($data, $perlchartdir::Transparent);
				$labellayer->setBarGap($bargap);			
				$labellayer->setBorderColor($perlchartdir::Transparent);

				$markLayer = $c->addBoxWhiskerLayer(undef, undef, undef, undef, $markdata, -1, 0x333333);
				$markLayer->setLineWidth(2);

				$layer = $c->addBarLayer3($data, $five_colors, $labels);$layer->setBarGap($bargap);			
				$layer->setLegendOrder($perlchartdir::NoLegend);
				$layer->setBorderColor(0x000033);
				
				$legendBox->addKey("Comparitive Group",0x333333, 2);
				}
			else	{
				$layer = $c->addBarLayer3($data, $five_colors, $labels);$layer->setBarGap($bargap);			
				$layer->setBorderColor(0x000033);
				}

			$c->getDrawArea()->setPaletteMode($perlchartdir::ForcePalette);

			if( !$c->makeChart($o_file) )
			{
				copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
			}
			else	{
					$empty_chart{print_totalassessments} = 0;
				}
		}
#5 Preventable Diseases
	if (($input->{'pgraphs'} eq 'all' || $input->{'print_preventable'} == 1) &&
		( $assessments_chk{GHA} || $assessments_chk{HRA} || $assessments_chk{OHA} ))
		{
		++$graph_cnt;
 		print "$graph_cnt. Preventable deaths <br>" unless $silent;
		##### Preventable deaths by disease
		my $o_file = $GGR_PAGE_DIR . $PARMS{'files_prefix'} . "_ggr_disease.png";
		my $condition_count = $GROUP{'Throat Cancer'} + $GROUP{'Flu/Pneumonia'} + $GROUP{'Liver Cirrhosis'} + $GROUP{'Lung Cancer'} + $GROUP{'Kidney Failure'} + $GROUP{'Esophageal Cancer'} + $GROUP{'Pancreatic Cancer'} + $GROUP{'Emphysema'} + $GROUP{'Laryngeal Cancer'} + $GROUP{'Heart Attack'} + $GROUP{'Breast Cancer'} + $GROUP{'Diabetes Mellitus'} + $GROUP{'Motor Vehicle'} + $GROUP{'Cervical Cancer'} + $GROUP{'Stroke'} + $GROUP{'Mouth Cancer'} + $GROUP{'Bladder Cancer'} + $GROUP{'Peptic Ulcer'};
		my $comp_condition_count = $COMPGROUP{'Throat Cancer'} + $COMPGROUP{'Flu/Pneumonia'} + $COMPGROUP{'Liver Cirrhosis'} + $COMPGROUP{'Lung Cancer'} + $COMPGROUP{'Kidney Failure'} + $COMPGROUP{'Esophageal Cancer'} + $COMPGROUP{'Pancreatic Cancer'} + $COMPGROUP{'Emphysema'} + $COMPGROUP{'Laryngeal Cancer'} + $COMPGROUP{'Heart Attack'} + $COMPGROUP{'Breast Cancer'} + $COMPGROUP{'Diabetes Mellitus'} + $COMPGROUP{'Motor Vehicle'} + $COMPGROUP{'Cervical Cancer'} + $COMPGROUP{'Stroke'} + $COMPGROUP{'Mouth Cancer'} + $COMPGROUP{'Bladder Cancer'} + $COMPGROUP{'Peptic Ulcer'};

		my $pie_count = (int($GROUP{'Throat Cancer'}/$condition_count * 100)) + (int($GROUP{'Flu/Pneumonia'}/$condition_count * 100)) + (int($GROUP{'Liver Cirrhosis'}/$condition_count * 100)) + (int($GROUP{'Lung Cancer'}/$condition_count * 100)) + (int($GROUP{'Kidney Failure'}/$condition_count * 100)) + (int($GROUP{'Esophageal Cancer'}/$condition_count * 100)) + (int($GROUP{'Pancreatic Cancer'}/$condition_count * 100)) + (int($GROUP{'Emphysema'}/$condition_count * 100)) + (int($GROUP{'Laryngeal Cancer'}/$condition_count * 100)) + (int($GROUP{'Heart Attack'}/$condition_count * 100)) + (int($GROUP{'Breast Cancer'}/$condition_count * 100)) + (int($GROUP{'Diabetes Mellitus'}/$condition_count * 100)) + (int($GROUP{'Motor Vehicle'}/$condition_count * 100)) + (int($GROUP{'Cervical Cancer'}/$condition_count * 100)) + (int($GROUP{'Stroke'}/$condition_count * 100)) + (int($GROUP{'Mouth Cancer'}/$condition_count * 100)) + (int($GROUP{'Bladder Cancer'}/$condition_count * 100)) + (int($GROUP{'Peptic Ulcer'}/$condition_count * 100)) if( $condition_count );
		my $comp_pie_count = (int($COMPGROUP{'Throat Cancer'}/$comp_condition_count * 100)) + (int($COMPGROUP{'Flu/Pneumonia'}/$comp_condition_count * 100)) + (int($COMPGROUP{'Liver Cirrhosis'}/$comp_condition_count * 100)) + (int($COMPGROUP{'Lung Cancer'}/$comp_condition_count * 100)) + (int($COMPGROUP{'Kidney Failure'}/$comp_condition_count * 100)) + (int($COMPGROUP{'Esophageal Cancer'}/$comp_condition_count * 100)) + (int($COMPGROUP{'Pancreatic Cancer'}/$comp_condition_count * 100)) + (int($COMPGROUP{'Emphysema'}/$comp_condition_count * 100)) + (int($COMPGROUP{'Laryngeal Cancer'}/$comp_condition_count * 100)) + (int($COMPGROUP{'Heart Attack'}/$comp_condition_count * 100)) + (int($COMPGROUP{'Breast Cancer'}/$comp_condition_count * 100)) + (int($COMPGROUP{'Diabetes Mellitus'}/$comp_condition_count * 100)) + (int($COMPGROUP{'Motor Vehicle'}/$comp_condition_count * 100)) + (int($COMPGROUP{'Cervical Cancer'}/$comp_condition_count * 100)) + (int($COMPGROUP{'Stroke'}/$comp_condition_count * 100)) + (int($COMPGROUP{'Mouth Cancer'}/$comp_condition_count * 100)) + (int($COMPGROUP{'Bladder Cancer'}/$comp_condition_count * 100)) + (int($COMPGROUP{'Peptic Ulcer'}/$comp_condition_count * 100)) if( $comp_condition_count );

		if( $condition_count && $pie_count)
			{
			# The labels for the pie chart
			my $labels_tmp = ['Throat Cancer','Flu/Pneumonia','Liver Cirrhosis','Lung Cancer','Kidney Failure','Esophageal Cancer','Pancreatic Cancer','Emphysema','Laryngeal Cancer','Heart Attack','Diabetes Mellitus','Breast Cancer','Motor Vehicle','Cervical Cancer','Stroke','Mouth Cancer','Bladder Cancer','Peptic Ulcer'];

			# The data for the pie chart
			# The data for the pie chart
			my %data_hash;
			my @data_list;
			my @labels_list;
			# The data for the pie chart
			my @data_list;
			my @comp_data_list;
			my @labels_list;
			my $data;
			my $comp_data;
			my $labels;
			if($bars_preferred){
				foreach (@$labels_tmp) {
					$data_hash{primary}{$_} = (int($GROUP{$_}/$condition_count*100));
					$data_hash{comp}{$_} = (int($COMPGROUP{$_}/$comp_condition_count*100)) if ($isComparative && $comp_condition_count);
					}
				foreach my $label (sort { $data_hash{primary}{$a} <=> $data_hash{primary}{$b} } keys %{$data_hash{primary}} ) {
					if ( $data_hash{primary}{$label} ) {
						push @data_list, $data_hash{primary}{$label};
						push @comp_data_list, $data_hash{comp}{$label} if ($isComparative && $comp_condition_count);
						push @labels_list, $label;
						}
					}
				$data = \@data_list;
				$comp_data = \@comp_data_list if $isComparative;
				$labels = \@labels_list;
				}
			else	{
				foreach (@$labels_tmp) { $data_hash{$_} = (int($GROUP{$_}/$condition_count * 100)); }
				foreach my $label (sort { $data_hash{$a} <=> $data_hash{$b} } keys %data_hash) {
					if ( $data_hash{$label} ) {
						push @data_list, $data_hash{$label};
						push @labels_list, $label;
						}
					}
				my $data = \@data_list;
				my $labels = \@labels_list;

	#			my $data = [(int($GROUP{'Throat Cancer'}/$condition_count * 100)),(int($GROUP{'Flu/Pneumonia'}/$condition_count * 100)),(int($GROUP{'Liver Cirrhosis'}/$condition_count * 100)),(int($GROUP{'Lung Cancer'}/$condition_count * 100)),(int($GROUP{'Kidney Failure'}/$condition_count * 100)),(int($GROUP{'Esophageal Cancer'}/$condition_count * 100)),(int($GROUP{'Pancreatic Cancer'}/$condition_count * 100)),(int($GROUP{'Uterine Cancer'}/$condition_count * 100)),(int($GROUP{'Emphysema'}/$condition_count * 100)),(int($GROUP{'Laryngeal Cancer'}/$condition_count * 100)),(int($GROUP{'Heart Attack'}/$condition_count * 100)),(int($GROUP{'Diabetes Mellitus'}/$condition_count * 100)),(int($GROUP{'Breast Cancer'}/$condition_count * 100)),(int($GROUP{'Motor Vehicle'}/$condition_count * 100)),(int($GROUP{'Cervical Cancer'}/$condition_count * 100)),(int($GROUP{'Stroke'}/$condition_count * 100)),(int($GROUP{'Mouth Cancer'}/$condition_count * 100)),(int($GROUP{'Bladder Cancer'}/$condition_count * 100)),(int($GROUP{'Peptic Ulcer'}/$condition_count * 100))];
				}	
			unless ($bars_preferred){
				# Create a PieChart object
				my $c = new PieChart($pie_chartwide, $pie_charthigh);

				# Set the center of the pie at (x, y) and the radius
				$c->setPieSize($pie_centerx_small, $pie_centery_small, $pie_size_small);

				$c->addText($pie_text_right, $pie_text_top, "<*block,linespacing=.7, halign=right*>Preventable Deaths\nby Disease<*/*>", "arial.ttf", 9, 0x000000,9);

				#$c->addTitle("Custom Colors");
				# set the LineColor to light gray
				$c->setColor($perlchartdir::LineColor, 0xc0c0c0);
				# use given color array as the data colors (sector colors)
				$c->setColors2($perlchartdir::DataColor, $fourteen_colors);
				$c->setBgImage($pie_background, 7);

	#			$c->addLegend($pie_legendx_small, $pie_legendy_small);
	#			$c->setLabelLayout($perlchartdir::SideLayout);

				$c->setStartAngle(15);
				$c->setLabelStyle("arial.ttf", 7);

				# Set the pie data and the pie labels
				$c->getDrawArea()->setPaletteMode($perlchartdir::ForcePalette);

				#set data to pie chart as usual
				$c->setData($data, $labels);

				my $sum = 0;
				foreach (@$data) {  $sum += $_; }
				my $cutoff = 0;
				for (my $i = 0; $i < scalar(@$data); ++$i) {
					     $cutoff += $$data[$i]/$sum;
					     $c->sector($i)->setLabelStyle("arial.ttf", 7);
					     if ($$data[$i]/$sum < 0.07 || $cutoff < .52) {
						 $c->sector($i)->setLabelLayout($perlchartdir::SideLayout);
						 $c->sector($i)->setJoinLine(0x000000);
						 $c->sector($i)->setLabelFormat("{label} - {percent|1}%");
						 }
					     else {
						 $c->sector($i)->setLabelLayout(1,-40);
						 $c->sector($i)->setLabelFormat("{label}<*br*>{percent|1}%");
						 }

					}
				}
			else	{
				# create the bar chart
				$d = new XYChart($wbar_chartwide, $wbar_charthigh, 0xffffff);

				$d->setPlotArea(100, 50, 550, 210, $perlchartdir::Transparent, -1, $perlchartdir::Transparent, 0xe0e0e0);

				my $title = $d->addTitle2(8, "<*block,linespacing=.7, halign=right*>Preventable Deaths\nby Disease<*/*>", "arial.ttf", 12);

				if($isComparative && $comp_albasis){
					$legendBox = $d->addLegend($d->getWidth() / 2, $title->getHeight()-7, "arial.ttf", 8);
					$legendBox->setBackground($perlchartdir::Transparent, $perlchartdir::Transparent);
					$legendBox->setAlignment($perlchartdir::TopCenter);
					$legendBox->setLineStyleKey();
					}

				$d->swapXY(1);


#				$textbox = $d->yAxis()->setTitle("% of Participants");
				# $textbox->setFontStyle("arial.ttf");
				# $textbox->setFontSize(7);
				$d->yAxis()->setLabelFormat("{value}%");

				$d->xAxis()->setLabels($labels);
				$d->xAxis()->setTickLength(0);
				$d->yAxis()->setLinearScale(0,100,20);


				if($isComparative && $comp_condition_count){
					$labellayer = $d->addBarLayer($data, $perlchartdir::Transparent);
					$labellayer->setBorderColor($perlchartdir::Transparent);
					# $labellayer->setAggregateLabelFormat("{value|1}%");
					#  $labellayer->setAggregateLabelStyle("arial.ttf", 7) ;

					$markLayer = $d->addBoxWhiskerLayer(undef, undef, undef, undef, $comp_data, -1, 0x333333);
					$markLayer->setLineWidth(2);
#					$markLayer->setDataGap(0.4);
					# Add the legend key for the mark line
#					$legendBox->addKey("Comparative Group", 0x333333, 2);

					$layer = $d->addBarLayer3($data, $twelve_colors);$layer->setBarGap($bargap);
					$layer->setBorderColor(0x000033);
					}
				else	{
					$layer = $d->addBarLayer3($data, $twelve_colors, $labels);
					$layer->setBarGap($bargap);
					$layer->setBorderColor(0x000033);
					$layer->setAggregateLabelFormat("{value|1}%");
					$layer->setAggregateLabelStyle("arial.ttf", 7) ;
					}
				}

			$d->getDrawArea()->setPaletteMode($perlchartdir::ForcePalette);
			
			if( !$d->makeChart($o_file) )
				{
					copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
				}
			else	{
					$empty_chart{print_preventable} = 0;
				}
			}
		else	{
				copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
			}

		}
#6 Group Risk Factors
	if (($input->{'pgraphs'} eq 'all' || $input->{'print_riskfactors'} == 1) &&
		($assessments_chk{GHA} || $assessments_chk{HRA} || $assessments_chk{OHA} ))
		{
		++$graph_cnt;
 		print "$graph_cnt. Risk factors<br>" unless $silent;
		####  Risk Factors
		my $o_file = $GGR_PAGE_DIR . $PARMS{'files_prefix'} . "_ggr_factors.png";
		
		my $be_basis1 = $PARMS{'exer_none'}+$PARMS{'sm_still'}+$PARMS{'HDL_low'}+$PARMS{'male_prostate_bad'}+$PARMS{'chol_high'}+$PARMS{'alc_high'}+$PARMS{'bp_high'}+$PARMS{'sb_speed'}+$PARMS{'sb_some'}+$PARMS{'sb_never'}+$PARMS{'mammo_bad'}+$PARMS{'pap_bad'}+$PARMS{'wt_obese'};
		my $comp_be_basis1 = $COMPPARMS{'exer_none'}+$COMPPARMS{'sm_still'}+$COMPPARMS{'HDL_low'}+$COMPPARMS{'male_prostate_bad'}+$COMPPARMS{'chol_high'}+$COMPPARMS{'alc_high'}+$COMPPARMS{'bp_high'}+$COMPPARMS{'sb_speed'}+$COMPPARMS{'sb_some'}+$COMPPARMS{'sb_never'}+$COMPPARMS{'mammo_bad'}+$COMPPARMS{'pap_bad'}+$COMPPARMS{'wt_obese'};
		my $be_basis = $PARMS{'cnt'};
		my $comp_be_basis = $COMPPARMS{'cnt'};
		if ($be_basis)
			{

			# The data for the chart
			$PARMS{'modifiable_seat_belt'} = $PARMS{'sb_some'}+$PARMS{'sb_never'};
			$COMPPARMS{'modifiable_seat_belt'} = $COMPPARMS{'sb_some'}+$COMPPARMS{'sb_never'};
			# The labels for the chart
			my %labels_tmp = (
					'exer_none' =>  'Lack of Exercise',
					'sm_still' =>  'Smoking',
					'HDL_low' =>  'Low HDL',
					'chol_high' =>  'High Cholesterol',
					'alc_high' =>  'Alcohol Use',
					'bp_high' =>  'High Blood Pressure',
					'sb_speed' =>  'Speeding',
					'modifiable_seat_belt' =>  'Seat Belt Use',
					'mammo_bad' =>  'Mammograms',
					'pap_bad' =>  'Pelvic Exams',
					'male_prostate_bad' => 'Prostate Exams',
					'wt_obese' =>  'Weight'
					);

			# The data for the chart
			my %data_hash;
			my @data_list;
			my @comp_data_list;
			my @labels_list;
			my $data;
			my $comp_data;
			my $labels;
			foreach (keys %labels_tmp) {
				$data_hash{primary}{$labels_tmp{$_}} = (int($PARMS{$_}/$be_basis*100));
				$data_hash{comp}{$labels_tmp{$_}} = (int($COMPPARMS{$_}/$comp_be_basis*100)) if ($isComparative && $comp_be_basis);
				}
			foreach my $label (sort { $data_hash{primary}{$a} <=> $data_hash{primary}{$b} } keys %{$data_hash{primary}} ) {
				if ( $data_hash{primary}{$label} ) {
					push @data_list, $data_hash{primary}{$label};
					push @comp_data_list, $data_hash{comp}{$label} if ($isComparative && $comp_be_basis);
					push @labels_list, $label;
					}
				}
			$data = \@data_list;
			$comp_data = \@comp_data_list if $isComparative;
			$labels = \@labels_list;

			my $d;
			my $legendBox;
			my $textbox;
			my $labellayer;
			my $markLayer;
			my $layer;
				# create the bar chart
				$d = new XYChart($wbar_chartwide, $wbar_charthigh, 0xffffff);

				$d->setPlotArea(100, 50, 550, 210, $perlchartdir::Transparent, -1, $perlchartdir::Transparent, 0xe0e0e0);

				my $title = $d->addTitle2(8, "Modifiable behaviors", "arial.ttf", 12);

				if($isComparative && $comp_be_basis){
					$legendBox = $d->addLegend($d->getWidth() / 2, $title->getHeight()-7, "arial.ttf", 8);
					$legendBox->setBackground($perlchartdir::Transparent, $perlchartdir::Transparent);
					$legendBox->setAlignment($perlchartdir::TopCenter);
					$legendBox->setLineStyleKey();
					}

				$d->swapXY(1);


				$d->yAxis()->setLabelFormat("{value}%");

				$d->xAxis()->setLabels($labels);
				$d->xAxis()->setTickLength(0);
				$d->yAxis()->setLinearScale(0,100,20);


				if($isComparative && $comp_be_basis){
					$labellayer = $d->addBarLayer($data, $perlchartdir::Transparent);
					$labellayer->setBorderColor($perlchartdir::Transparent);

					$markLayer = $d->addBoxWhiskerLayer(undef, undef, undef, undef, $comp_data, -1, 0x333333);
					$markLayer->setLineWidth(2);
					# Add the legend key for the mark line
					$legendBox->addKey("Comparative Group", 0x333333, 2);

					$layer = $d->addBarLayer3($data, $twelve_colors);$layer->setBarGap($bargap);
					$layer->setBorderColor(0x000033);
					}
				else	{
					$layer = $d->addBarLayer3($data, $twelve_colors, $labels);
					$layer->setBarGap($bargap);
					$layer->setBorderColor(0x000033);
					$layer->setAggregateLabelFormat("{value|1}%");
					$layer->setAggregateLabelStyle("arial.ttf", 7) ;
					}

			$d->getDrawArea()->setPaletteMode($perlchartdir::ForcePalette);

			if( !$d->makeChart($o_file) )
				{
					copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
				}
			else	{
				$empty_chart{print_riskfactors} = 0;
				}
			}
		else	{
				copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
			}

		}
#7  Smoking
	if (($input->{'pgraphs'} eq 'all' || $input->{'print_smoking'} == 1) &&
		($assessments_chk{GHA} || $assessments_chk{HRA} || $assessments_chk{CRC} || $assessments_chk{OHA} ))
		{
		++$graph_cnt;
 		print "$graph_cnt. Smoking<br>" unless $silent;
		#### Smoking Habits
		my $o_file = $GGR_PAGE_DIR . $PARMS{'files_prefix'} . "_ggr_sm.png";

		my ($comp_sm_never, $comp_sm_quit, $comp_sm_still, $comp_sm_basis);
		$comp_sm_basis = $COMPPARMS{'sm_never'}+$COMPPARMS{'sm_quit'}+$COMPPARMS{'sm_still'};

		my ($sm_never, $sm_quit, $sm_still, $sm_basis);

		if( $sm_basis = ($PARMS{'sm_never'}+$PARMS{'sm_quit'}+$PARMS{'sm_still'}) )
			{
			$sm_never=sprintf("%.1f",($PARMS{'sm_never'}/$sm_basis*100));
			$sm_quit=sprintf("%.1f",($PARMS{'sm_quit'}/$sm_basis*100));
			$sm_still=sprintf("%.1f",($PARMS{'sm_still'}/$sm_basis*100));

			if ($sm_still > 26) 	{ $PARMS{smoke_msg} = 'Your group has smoking habits higher than the national average of 24% smokers.' }
			elsif ($sm_still < 22)	{ $PARMS{smoke_msg} = 'Your group has fewer smokers than the national average of 24% smokers.' }
			else			{ $PARMS{smoke_msg} = 'Your group has smoking habits about the sames as the national average of 24% smokers.' }

			if($isComparative && $comp_sm_basis){
				$comp_sm_never=sprintf("%.1f",($COMPPARMS{'sm_never'}/$comp_sm_basis*100));
				$comp_sm_quit=sprintf("%.1f",($COMPPARMS{'sm_quit'}/$comp_sm_basis*100));
				$comp_sm_still=sprintf("%.1f",($COMPPARMS{'sm_still'}/$comp_sm_basis*100));
				}
			my $numbers = [ $PARMS{'sm_never'},       $PARMS{'sm_quit'},   $PARMS{'sm_still'}];
			my $data = [ $sm_never,       $sm_quit,   $sm_still];
			my $markdata = [ $comp_sm_never,       $comp_sm_quit,   $comp_sm_still ] if $isComparative;

			my $labels = ["Non-smokers", "Ex-smokers", "Smokers"];

			my $c = new XYChart($bar_chartwide, $bar_charthigh, 0xffffff);

			$c->setPlotArea(90, 50, 255, 180, $perlchartdir::Transparent, -1, $perlchartdir::Transparent, 0xe0e0e0);

			my $title = $c->addTitle2(8, "Smoking status", "arial.ttf", 12);

			# my $textbox = $c->yAxis()->setTitle("% of Participants");
			# $textbox->setFontStyle("arial.ttf");
			# $textbox->setFontSize(7);
			$c->yAxis()->setLabelFormat("{value}%");

			$c->xAxis()->setLabels($labels);
			$c->xAxis()->setTickLength(1);
			$c->yAxis()->setLinearScale(0,100,20);

			# Convert the labels on the x-axis to a CDMLTable
			my $table = $c->xAxis()->makeLabelTable();
			# Set the default top/bottom margins of the cells to 3 pixels
			$table->getStyle()->setMargin2(0, 0, 3, 3);
			# Use Arial Bold as the font for the first row
			$table->getRowStyle(0)->setFontStyle("arial.ttf");
			$table->getRowStyle(0)->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent);
			$table->appendRow()->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent);
			$table->appendRow()->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent);
			for(my $i = 0; $i < scalar(@$data); ++$i) {
				$table->setText($i, 2, $data->[$i].'%');
				}
			$table->appendRow()->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent) if($show_numbers);
			for(my $i = 0; $i < scalar(@$numbers); ++$i) {
				$table->setText($i, 3, $numbers->[$i]) if($show_numbers);
				}
			$table->insertCol(0)->setMargin2(5, 5, 3, 3);
			$table->setText(0, 0, "Groups");
			$table->setText(0, 2, "% of Participants");
				$table->setText(0, 3, "# of Participants") if($show_numbers);

			my $legendBox;
			my $labellayer;
			my $markLayer;
			my $layer;
			if($isComparative && $comp_sm_basis){
					$legendBox = $c->addLegend($c->getWidth() / 2, $title->getHeight()-7, "arial.ttf", 8);
					$legendBox->setBackground($perlchartdir::Transparent, $perlchartdir::Transparent);
					$legendBox->setAlignment($perlchartdir::TopCenter);
					$legendBox->setLineStyleKey();
				}

			if($isComparative && $comp_sm_basis){
				$labellayer = $c->addBarLayer($data, $perlchartdir::Transparent);   $labellayer->setBarGap($bargap);
				$labellayer->setBorderColor($perlchartdir::Transparent);
				# $labellayer->setAggregateLabelFormat("{value|1}%");
				#  $labellayer->setAggregateLabelStyle("arial.ttf", 7) ;

				$markLayer = $c->addBoxWhiskerLayer(undef, undef, undef, undef, $markdata, -1, 0x333333);
				$markLayer->setLineWidth(2);
				#  $markLayer->setDataGap(0.1);
				# Add the legend key for the mark line
				$legendBox->addKey("Comparative Group", 0x333333, 2);

				$layer = $c->addBarLayer3($data, $five_colors);$layer->setBarGap($bargap);
				$layer->setBorderColor(0x000033);
				}
			else	{
				$layer = $c->addBarLayer3($data, $five_colors, $labels);  $layer->setBarGap($bargap);
				$layer->setBorderColor(0x000033);
				#  $layer->setAggregateLabelFormat("{value|1}%");
				# $layer->setAggregateLabelStyle("arial.ttf", 7) ;
				}

			$c->getDrawArea()->setPaletteMode($perlchartdir::ForcePalette);

			if( !$c->makeChart($o_file) )
				{
					copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
				}
			else	{
				$empty_chart{print_smoking} = 0;
				}
			}
			else {
				copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
			}

		}
#8 Alcohol Use
	if (($input->{'pgraphs'} eq 'all' || $input->{'print_alcohol'} == 1) &&
		($assessments_chk{GHA} || $assessments_chk{HRA} || $assessments_chk{OHA} )){
		++$graph_cnt;
 		print "$graph_cnt. Alcohol use<br>" unless $silent;
		#### Alcohol Habits
		my $o_file = $GGR_PAGE_DIR . $PARMS{'files_prefix'} . "_ggr_alc.png";

		my ($alc_good, $alc_over, $alc_obese, $alc_basis);
		my ($comp_alc_good, $comp_alc_over, $comp_alc_obese, $comp_alc_basis);
		$comp_alc_basis = $COMPPARMS{'alc_low'} + $COMPPARMS{'alc_medium'} + $COMPPARMS{'alc_high'};

		if($alc_basis = $PARMS{'alc_low'} + $PARMS{'alc_medium'} + $PARMS{'alc_high'})
			{
			$alc_good = sprintf("%.1f",($PARMS{'alc_low'}/$alc_basis*100));
			$alc_over = sprintf("%.1f",($PARMS{'alc_medium'}/$alc_basis*100));
			$alc_obese = sprintf("%.1f",($PARMS{'alc_high'}/$alc_basis*100));

			if ($alc_obese + $alc_over > 8 ) 	{ $PARMS{alcohol_msg} = 'This group has more moderate and heavy drinkers than the US average.' }
			else 					{ $PARMS{alcohol_msg} = 'This group has fewer moderate and heavy drinkers than the US average.' }

			if ($PARMS{'sb_drinkdrive'}) 	{ $PARMS{alcohol_msg} .= "  Of this group, $PARMS{'sb_drinkdrive'} participants out of $alc_basis reported either drinking and driving or riding with someone who had too much to drink in the last month." }

			if($isComparative && $comp_alc_basis){
				$comp_alc_good = sprintf("%.1f",($COMPPARMS{'alc_low'}/$comp_alc_basis*100));
				$comp_alc_over = sprintf("%.1f",($COMPPARMS{'alc_medium'}/$comp_alc_basis*100));
				$comp_alc_obese = sprintf("%.1f",($COMPPARMS{'alc_high'}/$comp_alc_basis*100));
				}

			my $numbers = [ $PARMS{'alc_low'}, $PARMS{'alc_medium'}, $PARMS{'alc_high'} ];
			my $data = [$alc_good ,            $alc_over ,     $alc_obese];
			my $markdata = [ $comp_alc_good ,  $comp_alc_over ,  $comp_alc_obese ] if $isComparative;

			my $labels = ["Low", "Moderate", "High"];

			my $c = new XYChart($bar_chartwide, $bar_charthigh, 0xffffff);

			$c->setPlotArea(90, 50, 255, 180, $perlchartdir::Transparent, -1, $perlchartdir::Transparent, 0xe0e0e0);

			my $title = $c->addTitle2(8, "Group Alcohol Use", "arial.ttf", 12);

			my $legendBox;
			my $labellayer;
			my $markLayer;
			my $layer;
			if($isComparative && $comp_alc_basis){
					$legendBox = $c->addLegend($c->getWidth() / 2, $title->getHeight()-7, "arial.ttf", 8);
					$legendBox->setBackground($perlchartdir::Transparent, $perlchartdir::Transparent);
					$legendBox->setAlignment($perlchartdir::TopCenter);
					$legendBox->setLineStyleKey();
				}


			# my $textbox = $c->yAxis()->setTitle("% of Participants");
			# $textbox->setFontStyle("arial.ttf");
			# $textbox->setFontSize(7);
			$c->yAxis()->setLabelFormat("{value}%");
			$c->yAxis()->setLinearScale(0,100,20);

			$c->xAxis()->setLabels($labels);
			$c->xAxis()->setTickLength(1);

				# Convert the labels on the x-axis to a CDMLTable
				my $table = $c->xAxis()->makeLabelTable();
				# Set the default top/bottom margins of the cells to 3 pixels
				$table->getStyle()->setMargin2(0, 0, 3, 3);
				# Use Arial Bold as the font for the first row
				$table->getRowStyle(0)->setFontStyle("arial.ttf");
				$table->getRowStyle(0)->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent);
				$table->appendRow()->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent);
				$table->appendRow()->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent);
				for(my $i = 0; $i < scalar(@$data); ++$i) {
					$table->setText($i, 2, $data->[$i].'%');
					}
				$table->appendRow()->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent) if($show_numbers);
				for(my $i = 0; $i < scalar(@$numbers); ++$i) {
					$table->setText($i, 3, $numbers->[$i]) if($show_numbers);
					}
				$table->insertCol(0)->setMargin2(5, 5, 3, 3);
				$table->setText(0, 0, "Alcohol Use");
				$table->setText(0, 2, "% of Participants");
				$table->setText(0, 3, "# of Participants") if($show_numbers);

			if($isComparative && $comp_alc_basis){
				$labellayer = $c->addBarLayer($data, $perlchartdir::Transparent);   $labellayer->setBarGap($bargap);
				$labellayer->setBorderColor(0x330000);
				# $labellayer->setAggregateLabelFormat("{value|1}%");
				#  $labellayer->setAggregateLabelStyle("arial.ttf", 7) ;

				$markLayer = $c->addBoxWhiskerLayer(undef, undef, undef, undef, $markdata, -1, 0x333333);
				$markLayer->setLineWidth(2);
				#  $markLayer->setDataGap(0.1);
				# Add the legend key for the mark line
				$legendBox->addKey("Comparative Group", 0x333333, 2);

				$layer = $c->addBarLayer3($data, $five_colors);$layer->setBarGap($bargap);
				$layer->setBorderColor(0x000033);
				}
			else	{
				$layer = $c->addBarLayer3($data, $five_colors, $labels);  $layer->setBarGap($bargap);
				$layer->setBorderColor(0x000033);
				#  $layer->setAggregateLabelFormat("{value|1}%");
				# $layer->setAggregateLabelStyle("arial.ttf", 7) ;
				}

			$c->getDrawArea()->setPaletteMode($perlchartdir::ForcePalette);

			if( !$c->makeChart($o_file) )
				{
					copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
				}
			else	{
					$empty_chart{print_alcohol} = 0;
				}
			}
			else {
				copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
			}

		}
#9 Weight Levels
	if (($input->{'pgraphs'} eq 'all' || $input->{'print_weight'} == 1) &&
		($assessments_chk{GHA} || $assessments_chk{HRA} ||
			$assessments_chk{CRC} || $assessments_chk{DRC} ||
			$assessments_chk{FIT} || $assessments_chk{OHA} ))
		{
		++$graph_cnt;
 		print "$graph_cnt. Weight status<br>" unless $silent;
		####  Weight Status
		my $o_file = $GGR_PAGE_DIR . $PARMS{'files_prefix'} . "_ggr_wt.png";

		my ($wt_good, $wt_under, $wt_over, $wt_obese, $wt_basis);
		my ($comp_wt_good, $comp_wt_under, $comp_wt_over, $comp_wt_obese, $comp_wt_basis);
		$comp_wt_basis = $COMPPARMS{'wt_under'} + $COMPPARMS{'wt_good'} + $COMPPARMS{'wt_over'} + $COMPPARMS{'wt_obese'} if $isComparative;

		if($wt_basis = $PARMS{'wt_under'} + $PARMS{'wt_good'} + $PARMS{'wt_over'} + $PARMS{'wt_obese'})
			{
			$wt_under = sprintf("%.1f",($PARMS{'wt_under'}/$wt_basis*100));
			$wt_good = sprintf("%.1f",($PARMS{'wt_good'}/$wt_basis*100));
			$wt_over = sprintf("%.1f",($PARMS{'wt_over'}/$wt_basis*100));
			$wt_obese = sprintf("%.1f",($PARMS{'wt_obese'}/$wt_basis*100));

			if( $wt_obese >= 20 ||
				$wt_obese + $wt_over >= 40 )	{  $PARMS{'wt_msg'} = "There is a large percentage of participants above their healthy weight."; }
			else					{  $PARMS{'wt_msg'} = "This group is doing a good job maintaining proper weight." }

			if($isComparative && $comp_wt_basis){
				$comp_wt_under = sprintf("%.1f",($COMPPARMS{'wt_under'}/$comp_wt_basis*100));
				$comp_wt_good = sprintf("%.1f",($COMPPARMS{'wt_good'}/$comp_wt_basis*100));
				$comp_wt_over = sprintf("%.1f",($COMPPARMS{'wt_over'}/$comp_wt_basis*100));
				$comp_wt_obese = sprintf("%.1f",($COMPPARMS{'wt_obese'}/$comp_wt_basis*100));
				}
			my $numbers = [ $PARMS{'wt_under'}, $PARMS{'wt_good'}, $PARMS{'wt_over'}, $PARMS{'wt_obese'}];
			my $data = [$wt_under, $wt_good , $wt_over , $wt_obese];
			my $markdata = [$comp_wt_under, $comp_wt_good , $comp_wt_over , $comp_wt_obese] if $isComparative;

			my $labels = ["Under\nWeight", "Healthy\nWeight", "Overweight", "Obese"];

			my $c = new XYChart($bar_chartwide, $bar_charthigh, 0xffffff);

			$c->setPlotArea(90, 50, 255, 180, $perlchartdir::Transparent, -1, $perlchartdir::Transparent, 0xe0e0e0);

			my $title = $c->addTitle2(8, "Weight levels", "arial.ttf", 12);

			my $legendBox;
			my $labellayer;
			my $markLayer;
			my $layer;
			if($isComparative && $comp_wt_basis){
					$legendBox = $c->addLegend($c->getWidth() / 2, $title->getHeight()-7, "arial.ttf", 8);
					$legendBox->setBackground($perlchartdir::Transparent, $perlchartdir::Transparent);
					$legendBox->setAlignment($perlchartdir::TopCenter);
					$legendBox->setLineStyleKey();
				}

			# my $textbox = $c->yAxis()->setTitle("% of Participants");
			# $textbox->setFontStyle("arial.ttf");
			# $textbox->setFontSize(7);
			$c->yAxis()->setLabelFormat("{value}%");
			$c->yAxis()->setLinearScale(0,100,20);

			$c->xAxis()->setLabels($labels);
			$c->xAxis()->setLabelStyle("arial.ttf", 7);
			$c->xAxis()->setTickLength(1);

				# Convert the labels on the x-axis to a CDMLTable
				my $table = $c->xAxis()->makeLabelTable();
				# Set the default top/bottom margins of the cells to 3 pixels
				$table->getStyle()->setMargin2(0, 0, 3, 3);
				# Use Arial Bold as the font for the first row
				$table->getRowStyle(0)->setFontStyle("arial.ttf");
				$table->getRowStyle(0)->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent);
				$table->appendRow()->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent);
				$table->appendRow()->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent);
				for(my $i = 0; $i < scalar(@$data); ++$i) {
					$table->setText($i, 2, $data->[$i].'%');
					}
				$table->appendRow()->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent) if($show_numbers);
				for(my $i = 0; $i < scalar(@$numbers); ++$i) {
					$table->setText($i, 3, $numbers->[$i]) if($show_numbers);
					}
				$table->insertCol(0)->setMargin2(5, 5, 3, 3);
				$table->setText(0, 0, "Levels");
				$table->setText(0, 2, "% of Participants");
				$table->setText(0, 3, "# of Participants") if($show_numbers);

			if($isComparative && $comp_wt_basis){
				$labellayer = $c->addBarLayer($data, $perlchartdir::Transparent);   $labellayer->setBarGap($bargap);
				$labellayer->setBorderColor($perlchartdir::Transparent);
				# $labellayer->setAggregateLabelFormat("{value|1}%");
				#  $labellayer->setAggregateLabelStyle("arial.ttf", 7) ;

				$markLayer = $c->addBoxWhiskerLayer(undef, undef, undef, undef, $markdata, -1, 0x333333);
				$markLayer->setLineWidth(2);
				#  $markLayer->setDataGap(0.1);
				# Add the legend key for the mark line
				$legendBox->addKey("Comparative Group", 0x333333, 2);

				$layer = $c->addBarLayer3($data, $five_colors);$layer->setBarGap($bargap);
				$layer->setBorderColor(0x000033);
				}
			else	{
				$layer = $c->addBarLayer3($data, $five_colors, $labels);  $layer->setBarGap($bargap);
				$layer->setBorderColor(0x000033);
				#  $layer->setAggregateLabelFormat("{value|1}%");
				# $layer->setAggregateLabelStyle("arial.ttf", 7) ;
				}

			$c->getDrawArea()->setPaletteMode($perlchartdir::ForcePalette);

			if( !$c->makeChart($o_file) )
				{
					copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
				}
			else	{
					$empty_chart{print_weight} = 0;
				}
			}
			else {
				copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
			}

		}
#10 Mammogram Data
	if (($input->{'pgraphs'} eq 'all' || $input->{'print_mammogram'} == 1) &&
		($assessments_chk{GHA} || $assessments_chk{HRA} || $assessments_chk{OHA} ))
		{
		++$graph_cnt;
 		print "$graph_cnt. Mammograms<br>" unless $silent;
		####  Mammogram
		my $o_file = $GGR_PAGE_DIR . $PARMS{'files_prefix'} . "_ggr_mammo.png";

		my ($mammo_good, $mammo_med, $mammo_bad, $mammo_basis);
		my ($comp_mammo_good, $comp_mammo_med, $comp_mammo_bad, $comp_mammo_basis);
		$comp_mammo_basis = $COMPPARMS{'mammo_good'} + $COMPPARMS{'mammo_med'} + $COMPPARMS{'mammo_bad'};

		if($mammo_basis = $PARMS{'mammo_good'} + $PARMS{'mammo_med'} + $PARMS{'mammo_bad'})
			{
			$mammo_good = sprintf("%.1f",($PARMS{'mammo_good'}/$mammo_basis*100));
			$mammo_med = sprintf("%.1f",($PARMS{'mammo_med'}/$mammo_basis*100));
			$mammo_bad = sprintf("%.1f",($PARMS{'mammo_bad'}/$mammo_basis*100));

			if ($mammo_bad + $mammo_med > 10)	{ $PARMS{mammo_msg} = "There are a high number of participants in your group that have not had a screening recently." }
			else					{ $PARMS{mammo_msg} = "This group is doing well in getting recommended screenings." }

			if($isComparative && $comp_mammo_basis){
				$comp_mammo_good = sprintf("%.1f",($COMPPARMS{'mammo_good'}/$comp_mammo_basis*100));
				$comp_mammo_med = sprintf("%.1f",($COMPPARMS{'mammo_med'}/$comp_mammo_basis*100));
				$comp_mammo_bad = sprintf("%.1f",($COMPPARMS{'mammo_bad'}/$comp_mammo_basis*100));
				}
			
			my $numbers = [ $PARMS{'mammo_good'}, $PARMS{'mammo_med'}, $PARMS{'mammo_bad'} ];
			my $data = [ $mammo_good ,       $mammo_med ,    $mammo_bad];
			my $markdata = [ $comp_mammo_good ,       $comp_mammo_med ,    $comp_mammo_bad ] if $isComparative;

			my $labels = ["1 year or less", "1 to 3 years", "Over 3 years"];

			my $c = new XYChart($bar_chartwide, $bar_charthigh, 0xffffff);

			$c->setPlotArea(90, 50, 255, 180, $perlchartdir::Transparent, -1, $perlchartdir::Transparent, 0xe0e0e0);

			my $title = $c->addTitle2(8, "Time since last mammogram", "arial.ttf", 12);

			my $legendBox;
			my $labellayer;
			my $markLayer;
			my $layer;
			if($isComparative && $comp_mammo_basis){
					$legendBox = $c->addLegend($c->getWidth() / 2, $title->getHeight()-7, "arial.ttf", 8);
					$legendBox->setBackground($perlchartdir::Transparent, $perlchartdir::Transparent);
					$legendBox->setAlignment($perlchartdir::TopCenter);
					$legendBox->setLineStyleKey();
				}

			# my $textbox = $c->yAxis()->setTitle("% of Participants");
			# $textbox->setFontStyle("arial.ttf");
			# $textbox->setFontSize(7);
			$c->yAxis()->setLabelFormat("{value}%");
			$c->yAxis()->setLinearScale(0,100,20);

			$c->xAxis()->setLabels($labels);
			$c->xAxis()->setTickLength(1);

				# Convert the labels on the x-axis to a CDMLTable
				my $table = $c->xAxis()->makeLabelTable();
				# Set the default top/bottom margins of the cells to 3 pixels
				$table->getStyle()->setMargin2(0, 0, 3, 3);
				# Use Arial Bold as the font for the first row
				$table->getRowStyle(0)->setFontStyle("arial.ttf");
				$table->getRowStyle(0)->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent);
				$table->appendRow()->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent);
				$table->appendRow()->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent);
				for(my $i = 0; $i < scalar(@$data); ++$i) {
					$table->setText($i, 2, $data->[$i].'%');
					}
				$table->appendRow()->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent) if($show_numbers);
				for(my $i = 0; $i < scalar(@$numbers); ++$i) {
					$table->setText($i, 3, $numbers->[$i]) if($show_numbers);
					}
				$table->insertCol(0)->setMargin2(5, 5, 3, 3);
				$table->setText(0, 0, "Last Exam");
				$table->setText(0, 2, "% of Participants");
				$table->setText(0, 3, "# of Participants") if($show_numbers);

			if($isComparative && $comp_mammo_basis){
				$labellayer = $c->addBarLayer($data, $perlchartdir::Transparent);   $labellayer->setBarGap($bargap);
				$labellayer->setBorderColor($perlchartdir::Transparent);
				# $labellayer->setAggregateLabelFormat("{value|1}%");
				#  $labellayer->setAggregateLabelStyle("arial.ttf", 7) ;

				$markLayer = $c->addBoxWhiskerLayer(undef, undef, undef, undef, $markdata, -1, 0x333333);
				$markLayer->setLineWidth(2);
				#  $markLayer->setDataGap(0.1);
				# Add the legend key for the mark line
				$legendBox->addKey("Comparative Group", 0x333333, 2);

				$layer = $c->addBarLayer3($data, $five_colors);$layer->setBarGap($bargap);
				$layer->setBorderColor(0x000033);
				}
			else	{
				$layer = $c->addBarLayer3($data, $five_colors, $labels);  $layer->setBarGap($bargap);
				$layer->setBorderColor(0x000033);
				#  $layer->setAggregateLabelFormat("{value|1}%");
				# $layer->setAggregateLabelStyle("arial.ttf", 7) ;
				}

			$c->getDrawArea()->setPaletteMode($perlchartdir::ForcePalette);

			if( !$c->makeChart($o_file) )
				{
					copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
				}
			else	{
				$empty_chart{print_mammogram} = 0;
				}
			}
			else {
				copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
			}

		}
#11 Pap Examinations
	if (($input->{'pgraphs'} eq 'all' || $input->{'print_pap'} == 1) &&
		($assessments_chk{GHA} || $assessments_chk{HRA} || $assessments_chk{OHA} ))
		{
		++$graph_cnt;
 		print "$graph_cnt. Pap exams<br>" unless $silent;
		#### Pap Exams
		my $o_file = $GGR_PAGE_DIR . $PARMS{'files_prefix'} . "_ggr_pap.png";

		my ($pap_good, $pap_med, $pap_bad, $pap_basis);
		my ($comp_pap_good, $comp_pap_med, $comp_pap_bad, $comp_pap_basis);
		$comp_pap_basis = $COMPPARMS{'pap_good'} + $COMPPARMS{'pap_med'} + $COMPPARMS{'pap_bad'};

		if ($pap_basis = $PARMS{'pap_good'} + $PARMS{'pap_med'} + $PARMS{'pap_bad'})
			{
			$pap_good = sprintf("%.1f",($PARMS{'pap_good'}/$pap_basis*100));
			$pap_med = sprintf("%.1f",($PARMS{'pap_med'}/$pap_basis*100));
			$pap_bad = sprintf("%.1f",($PARMS{'pap_bad'}/$pap_basis*100));

			if ($pap_bad + $pap_med > 10)	{ $PARMS{pap_msg} = "There are a high number of participants in your group that have not had a screening recently." }
			else				{ $PARMS{pap_msg} = "This group is doing well in getting recommended screenings." }

			if($isComparative && $comp_pap_basis){
				$comp_pap_good = sprintf("%.1f",($COMPPARMS{'pap_good'}/$comp_pap_basis*100));
				$comp_pap_med = sprintf("%.1f",($COMPPARMS{'pap_med'}/$comp_pap_basis*100));
				$comp_pap_bad = sprintf("%.1f",($COMPPARMS{'pap_bad'}/$comp_pap_basis*100));
				}

			my $numbers = [ $PARMS{'pap_good'}, $PARMS{'pap_med'}, $PARMS{'pap_bad'} ];
			my $data = [$pap_good ,         $pap_med ,       $pap_bad];
			my $markdata = [ $comp_pap_good ,  $comp_pap_med ,  $comp_pap_bad ] if $isComparative;

			my $labels = ["1 year or less", "1 to 3 years", "Over 3 years"];

			my $c = new XYChart($bar_chartwide, $bar_charthigh, 0xffffff);

			$c->setPlotArea(90, 50, 255, 180, $perlchartdir::Transparent, -1, $perlchartdir::Transparent, 0xe0e0e0);

			my $title = $c->addTitle2(8, "Time since last Pap", "arial.ttf", 12);

			my $legendBox;
			my $labellayer;
			my $markLayer;
			my $layer;
			if($isComparative && $comp_pap_basis){
					$legendBox = $c->addLegend($c->getWidth() / 2, $title->getHeight()-7, "arial.ttf", 8);
					$legendBox->setBackground($perlchartdir::Transparent, $perlchartdir::Transparent);
					$legendBox->setAlignment($perlchartdir::TopCenter);
					$legendBox->setLineStyleKey();
				}

			# my $textbox = $c->yAxis()->setTitle("% of Participants");
			# $textbox->setFontStyle("arial.ttf");
			# $textbox->setFontSize(7);
			$c->yAxis()->setLabelFormat("{value}%");
			$c->yAxis()->setLinearScale(0,100,20);

			$c->xAxis()->setLabels($labels);
			$c->xAxis()->setTickLength(1);

				# Convert the labels on the x-axis to a CDMLTable
				my $table = $c->xAxis()->makeLabelTable();
				# Set the default top/bottom margins of the cells to 3 pixels
				$table->getStyle()->setMargin2(0, 0, 3, 3);
				# Use Arial Bold as the font for the first row
				$table->getRowStyle(0)->setFontStyle("arial.ttf");
				$table->getRowStyle(0)->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent);
				$table->appendRow()->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent);
				$table->appendRow()->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent);
				for(my $i = 0; $i < scalar(@$data); ++$i) {
					$table->setText($i, 2, $data->[$i].'%');
					}
				$table->appendRow()->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent) if($show_numbers);
				for(my $i = 0; $i < scalar(@$numbers); ++$i) {
					$table->setText($i, 3, $numbers->[$i]) if($show_numbers);
					}
				$table->insertCol(0)->setMargin2(5, 5, 3, 3);
				$table->setText(0, 0, "Last Exam");
				$table->setText(0, 2, "% of Participants");
				$table->setText(0, 3, "# of Participants") if($show_numbers);

			if($isComparative && $comp_pap_basis){
				$labellayer = $c->addBarLayer($data, $perlchartdir::Transparent);   $labellayer->setBarGap($bargap);
				$labellayer->setBorderColor($perlchartdir::Transparent);
				# $labellayer->setAggregateLabelFormat("{value|1}%");
				#  $labellayer->setAggregateLabelStyle("arial.ttf", 7) ;

				$markLayer = $c->addBoxWhiskerLayer(undef, undef, undef, undef, $markdata, -1, 0x333333);
				$markLayer->setLineWidth(2);
				#  $markLayer->setDataGap(0.1);
				# Add the legend key for the mark line
				$legendBox->addKey("Comparative Group", 0x333333, 2);

				$layer = $c->addBarLayer3($data, $five_colors);$layer->setBarGap($bargap);
				$layer->setBorderColor(0x000033);
				}
			else	{
				$layer = $c->addBarLayer3($data, $five_colors, $labels);  $layer->setBarGap($bargap);
				$layer->setBorderColor(0x000033);
				#  $layer->setAggregateLabelFormat("{value|1}%");
				# $layer->setAggregateLabelStyle("arial.ttf", 7) ;
				}

			$c->getDrawArea()->setPaletteMode($perlchartdir::ForcePalette);

			if( !$c->makeChart($o_file) )
				{
					copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
				}
			else	{
				$empty_chart{print_pap} = 0;
				}
			}
			else {
				copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
			}

		}
#12  Breast Self Exams
	if (($input->{'pgraphs'} eq 'all' || $input->{'print_breast_self'} == 1) &&
		($assessments_chk{GHA} || $assessments_chk{HRA} || $assessments_chk{OHA} ))
		{
		++$graph_cnt;
 		print "$graph_cnt. Self breast exams<br>" unless $silent;
		#### breast self exam
		my $o_file = $GGR_PAGE_DIR . $PARMS{'files_prefix'} . "_ggr_breast_self.png";

		my ($self_breast_good, $self_breast_med, $self_breast_bad, $self_breast_basis);
		my ($comp_self_breast_good, $comp_self_breast_med, $comp_self_breast_bad, $comp_self_breast_basis);
		$comp_self_breast_basis = $COMPPARMS{'self_breast_good'} + $COMPPARMS{'self_breast_med'} + $COMPPARMS{'self_breast_bad'};

		if ($self_breast_basis = $PARMS{'self_breast_good'} + $PARMS{'self_breast_med'} + $PARMS{'self_breast_bad'})
			{
			$self_breast_good = sprintf("%.1f",($PARMS{'self_breast_good'}/$self_breast_basis*100));
			$self_breast_med = sprintf("%.1f",($PARMS{'self_breast_med'}/$self_breast_basis*100));
			$self_breast_bad = sprintf("%.1f",($PARMS{'self_breast_bad'}/$self_breast_basis*100));

			if ($self_breast_bad + $self_breast_med > 10)	{ $PARMS{self_breast_msg} = "There are a high number of participants in your group that have not been performing self exams as often as they should." }
			else				{ $PARMS{self_breast_msg} = "This group is doing well in following the guidelines recommended for self exam." }

			if($isComparative && $comp_self_breast_basis){
				$comp_self_breast_good = sprintf("%.1f",($COMPPARMS{'self_breast_good'}/$comp_self_breast_basis*100));
				$comp_self_breast_med = sprintf("%.1f",($COMPPARMS{'self_breast_med'}/$comp_self_breast_basis*100));
				$comp_self_breast_bad = sprintf("%.1f",($COMPPARMS{'self_breast_bad'}/$comp_self_breast_basis*100));
				}

			my $numbers = [ $PARMS{'self_breast_good'}, $PARMS{'self_breast_med'}, $PARMS{'self_breast_bad'} ];
			my $data = [$self_breast_good , $self_breast_med , $self_breast_bad] ;
			my $markdata = [$comp_self_breast_good , $comp_self_breast_med , $comp_self_breast_bad] if $isComparative;

			my $labels = ["monthly", "every few\nmonths", "rarely or\nnever"];

			my $c = new XYChart($bar_chartwide, $bar_charthigh, 0xffffff);

			$c->setPlotArea(90, 50, 255, 180, $perlchartdir::Transparent, -1, $perlchartdir::Transparent, 0xe0e0e0);

			my $title = $c->addTitle2(8, "Frequency of Self Breast Exam", "arial.ttf", 12);

			my $legendBox;
			my $labellayer;
			my $markLayer;
			my $layer;
			if($isComparative && $comp_self_breast_basis){
					$legendBox = $c->addLegend($c->getWidth() / 2, $title->getHeight()-7, "arial.ttf", 8);
					$legendBox->setBackground($perlchartdir::Transparent, $perlchartdir::Transparent);
					$legendBox->setAlignment($perlchartdir::TopCenter);
					$legendBox->setLineStyleKey();
				}

			# my $textbox = $c->yAxis()->setTitle("% of Participants");
			# $textbox->setFontStyle("arial.ttf");
			# $textbox->setFontSize(7);
			$c->yAxis()->setLabelFormat("{value}%");
			$c->yAxis()->setLinearScale(0,100,20);

			$c->xAxis()->setLabels($labels);
			$c->xAxis()->setTickLength(1);

				# Convert the labels on the x-axis to a CDMLTable
				my $table = $c->xAxis()->makeLabelTable();
				# Set the default top/bottom margins of the cells to 3 pixels
				$table->getStyle()->setMargin2(0, 0, 3, 3);
				# Use Arial Bold as the font for the first row
				$table->getRowStyle(0)->setFontStyle("arial.ttf");
				$table->getRowStyle(0)->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent);
				$table->appendRow()->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent);
				$table->appendRow()->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent);
				for(my $i = 0; $i < scalar(@$data); ++$i) {
					$table->setText($i, 2, $data->[$i].'%');
					}
				$table->appendRow()->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent) if($show_numbers);
				for(my $i = 0; $i < scalar(@$numbers); ++$i) {
					$table->setText($i, 3, $numbers->[$i]) if($show_numbers);
					}
				$table->insertCol(0)->setMargin2(5, 5, 3, 3);
				$table->setText(0, 0, "Frequency");
				$table->setText(0, 2, "% of Participants");
				$table->setText(0, 3, "# of Participants") if($show_numbers);

			if($isComparative && $comp_self_breast_basis){
				$labellayer = $c->addBarLayer($data, $perlchartdir::Transparent);   $labellayer->setBarGap($bargap);
				$labellayer->setBorderColor($perlchartdir::Transparent);
				# $labellayer->setAggregateLabelFormat("{value|1}%");
				#  $labellayer->setAggregateLabelStyle("arial.ttf", 7) ;

				$markLayer = $c->addBoxWhiskerLayer(undef, undef, undef, undef, $markdata, -1, 0x333333);
				$markLayer->setLineWidth(2);
				#  $markLayer->setDataGap(0.1);
				# Add the legend key for the mark line
				$legendBox->addKey("Comparative Group", 0x333333, 2);

				$layer = $c->addBarLayer3($data, $five_colors);$layer->setBarGap($bargap);
				$layer->setBorderColor(0x000033);
				}
			else	{
				$layer = $c->addBarLayer3($data, $five_colors, $labels);  $layer->setBarGap($bargap);
				$layer->setBorderColor(0x000033);
				#  $layer->setAggregateLabelFormat("{value|1}%");
				# $layer->setAggregateLabelStyle("arial.ttf", 7) ;
				}

			$c->getDrawArea()->setPaletteMode($perlchartdir::ForcePalette);

			if( !$c->makeChart($o_file) )
				{
					copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
				}
			else	{
				$empty_chart{print_breast_self} = 0;
				}
			}
			else {
				copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
			}

		}
#13 Prostate
	if (($input->{'pgraphs'} eq 'all' || $input->{'print_prostate'} == 1) &&
		($assessments_chk{GHA} || $assessments_chk{HRA} || $assessments_chk{OHA} ))
		{
		++$graph_cnt;
 		print "$graph_cnt. Prostate exams<br>" unless $silent;
		####  Male Prostate
		my $o_file = $GGR_PAGE_DIR . $PARMS{'files_prefix'} . "_ggr_prostate.png";

		my ($male_good, $male_med, $male_bad, $male_prostate_basis);
		my ($comp_male_good, $comp_male_med, $comp_male_bad, $comp_male_prostate_basis);
		$comp_male_prostate_basis = $COMPPARMS{'male_prostate_good'} + $COMPPARMS{'male_prostate_med'} + $COMPPARMS{'male_prostate_bad'};

		if ($male_prostate_basis = $PARMS{'male_prostate_good'} + $PARMS{'male_prostate_med'} + $PARMS{'male_prostate_bad'})
		{
			$male_good = sprintf("%.1f",($PARMS{'male_prostate_good'}/$male_prostate_basis*100));
			$male_med = sprintf("%.1f",($PARMS{'male_prostate_med'}/$male_prostate_basis*100));
			$male_bad = sprintf("%.1f",($PARMS{'male_prostate_bad'}/$male_prostate_basis*100));

			if ($male_bad + $male_med > 10)	{ $PARMS{male_msg} = "There are a high number of participants in your group that have not had a screening recently." }
			else				{ $PARMS{male_msg} = "This group is doing well in getting recommended screenings." }

			if($isComparative && $comp_male_prostate_basis){
				$comp_male_good = sprintf("%.1f",($COMPPARMS{'male_prostate_good'}/$comp_male_prostate_basis*100));
				$comp_male_med = sprintf("%.1f",($COMPPARMS{'male_prostate_med'}/$comp_male_prostate_basis*100));
				$comp_male_bad = sprintf("%.1f",($COMPPARMS{'male_prostate_bad'}/$comp_male_prostate_basis*100));
				}

			my $numbers = [ $PARMS{'male_prostate_good'}, $PARMS{'male_prostate_med'}, $PARMS{'male_prostate_bad'} ];
			my $data = [$male_good ,       $male_med ,    $male_bad];
			my $markdata = [ $comp_male_good , $comp_male_med , $comp_male_bad ] if $isComparative;

			my $labels = ["1 year or less", "1 to 3 years", "Over 3 years"];

			my $c = new XYChart($bar_chartwide, $bar_charthigh, 0xffffff);

			$c->setPlotArea(90, 50, 255, 180, $perlchartdir::Transparent, -1, $perlchartdir::Transparent, 0xe0e0e0);

			my $title = $c->addTitle2(8, "Time since last prostate exam", "arial.ttf", 12);

			my $legendBox;
			my $labellayer;
			my $markLayer;
			my $layer;
			if($isComparative && $comp_male_prostate_basis){
					$legendBox = $c->addLegend($c->getWidth() / 2, $title->getHeight()-7, "arial.ttf", 8);
					$legendBox->setBackground($perlchartdir::Transparent, $perlchartdir::Transparent);
					$legendBox->setAlignment($perlchartdir::TopCenter);
					$legendBox->setLineStyleKey();
				}

			# my $textbox = $c->yAxis()->setTitle("% of Participants");
			# $textbox->setFontStyle("arial.ttf");
			# $textbox->setFontSize(7);
			$c->yAxis()->setLabelFormat("{value}%");
			$c->yAxis()->setLinearScale(0,100,20);

			$c->xAxis()->setLabels($labels);
			$c->xAxis()->setTickLength(1);

				# Convert the labels on the x-axis to a CDMLTable
				my $table = $c->xAxis()->makeLabelTable();
				# Set the default top/bottom margins of the cells to 3 pixels
				$table->getStyle()->setMargin2(0, 0, 3, 3);
				# Use Arial Bold as the font for the first row
				$table->getRowStyle(0)->setFontStyle("arial.ttf");
				$table->getRowStyle(0)->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent);
				$table->appendRow()->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent);
				$table->appendRow()->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent);
				for(my $i = 0; $i < scalar(@$data); ++$i) {
					$table->setText($i, 2, $data->[$i].'%');
					}
				$table->appendRow()->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent) if($show_numbers);
				for(my $i = 0; $i < scalar(@$numbers); ++$i) {
					$table->setText($i, 3, $numbers->[$i]) if($show_numbers);
					}
				$table->insertCol(0)->setMargin2(5, 5, 3, 3);
				$table->setText(0, 0, "Last Exam");
				$table->setText(0, 2, "% of Participants");
				$table->setText(0, 3, "# of Participants") if($show_numbers);

			if($isComparative && $comp_male_prostate_basis){
				$labellayer = $c->addBarLayer($data, $perlchartdir::Transparent);   $labellayer->setBarGap($bargap);
				$labellayer->setBorderColor($perlchartdir::Transparent);
				# $labellayer->setAggregateLabelFormat("{value|1}%");
				#  $labellayer->setAggregateLabelStyle("arial.ttf", 7) ;

				$markLayer = $c->addBoxWhiskerLayer(undef, undef, undef, undef, $markdata, -1, 0x333333);
				$markLayer->setLineWidth(2);
				#  $markLayer->setDataGap(0.1);
				# Add the legend key for the mark line
				$legendBox->addKey("Comparative Group", 0x333333, 2);

				$layer = $c->addBarLayer3($data, $five_colors);$layer->setBarGap($bargap);
				$layer->setBorderColor(0x000033);
				}
			else	{
				$layer = $c->addBarLayer3($data, $five_colors, $labels);  $layer->setBarGap($bargap);
				$layer->setBorderColor(0x000033);
				#  $layer->setAggregateLabelFormat("{value|1}%");
				# $layer->setAggregateLabelStyle("arial.ttf", 7) ;
				}

			$c->getDrawArea()->setPaletteMode($perlchartdir::ForcePalette);

			if( !$c->makeChart($o_file) )
				{
					copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
				}
			else	{
				$empty_chart{print_prostate} = 0;
				}
			}
			else {
				copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
			}

		}
#13a Prostate for Men + 50
	if (($input->{'pgraphs'} eq 'all' || $input->{'print_prostate'} == 1) &&
		($assessments_chk{GHA} || $assessments_chk{HRA} || $assessments_chk{OHA} ))
		{
		++$graph_cnt;
 		print "$graph_cnt. Prostate exams<br>" unless $silent;
		####  Male Prostate
		my $o_file = $GGR_PAGE_DIR . $PARMS{'files_prefix'} . "_ggr_prostate50.png";

		my ($male_good, $male_med, $male_bad, $male_prostate_basis);
		my ($comp_male_good, $comp_male_med, $comp_male_bad, $comp_male_prostate_basis);
		$comp_male_prostate_basis = $COMPPARMS{'male_prostate50_good'} + $COMPPARMS{'male_prostate50_med'} + $COMPPARMS{'male_prostate50_bad'};

		if ($male_prostate_basis = $PARMS{'male_prostate50_good'} + $PARMS{'male_prostate50_med'} + $PARMS{'male_prostate50_bad'})
		{
			$male_good = sprintf("%.1f",($PARMS{'male_prostate50_good'}/$male_prostate_basis*100));
			$male_med = sprintf("%.1f",($PARMS{'male_prostate50_med'}/$male_prostate_basis*100));
			$male_bad = sprintf("%.1f",($PARMS{'male_prostate50_bad'}/$male_prostate_basis*100));

			if ($male_bad + $male_med > 10)	{ $PARMS{male_msg} = "There are a high number of participants in your group that have not had a screening recently." }
			else				{ $PARMS{male_msg} = "This group is doing well in getting recommended screenings." }

			if($isComparative && $comp_male_prostate_basis){
				$comp_male_good = sprintf("%.1f",($COMPPARMS{'male_prostate50_good'}/$comp_male_prostate_basis*100));
				$comp_male_med = sprintf("%.1f",($COMPPARMS{'male_prostate50_med'}/$comp_male_prostate_basis*100));
				$comp_male_bad = sprintf("%.1f",($COMPPARMS{'male_prostate50_bad'}/$comp_male_prostate_basis*100));
				}

			my $numbers = [ $PARMS{'male_prostate50_good'}, $PARMS{'male_prostate50_med'}, $PARMS{'male_prostate50_bad'} ];
			my $data = [$male_good ,       $male_med ,    $male_bad];
			my $markdata = [ $comp_male_good, $comp_male_med, $comp_male_bad ] if $isComparative;

			my $labels = ["1 year or less", "1 to 3 years", "Over 3 years"];

			my $c = new XYChart($bar_chartwide, $bar_charthigh, 0xffffff);

			$c->setPlotArea(90, 50, 255, 180, $perlchartdir::Transparent, -1, $perlchartdir::Transparent, 0xe0e0e0);

			my $title = $c->addTitle2(8, "Time since last prostate exam", "arial.ttf", 12);

			my $legendBox;
			my $labellayer;
			my $markLayer;
			my $layer;
			if($isComparative && $comp_male_prostate_basis){
					$legendBox = $c->addLegend($c->getWidth() / 2, $title->getHeight()-7, "arial.ttf", 8);
					$legendBox->setBackground($perlchartdir::Transparent, $perlchartdir::Transparent);
					$legendBox->setAlignment($perlchartdir::TopCenter);
					$legendBox->setLineStyleKey();
				}

			# my $textbox = $c->yAxis()->setTitle("% of Participants");
			# $textbox->setFontStyle("arial.ttf");
			# $textbox->setFontSize(7);
			$c->yAxis()->setLabelFormat("{value}%");
			$c->yAxis()->setLinearScale(0,100,20);

			$c->xAxis()->setLabels($labels);
			$c->xAxis()->setTickLength(1);

				# Convert the labels on the x-axis to a CDMLTable
				my $table = $c->xAxis()->makeLabelTable();
				# Set the default top/bottom margins of the cells to 3 pixels
				$table->getStyle()->setMargin2(0, 0, 3, 3);
				# Use Arial Bold as the font for the first row
				$table->getRowStyle(0)->setFontStyle("arial.ttf");
				$table->getRowStyle(0)->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent);
				$table->appendRow()->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent);
				$table->appendRow()->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent);
				for(my $i = 0; $i < scalar(@$data); ++$i) {
					$table->setText($i, 2, $data->[$i].'%');
					}
				$table->appendRow()->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent) if($show_numbers);
				for(my $i = 0; $i < scalar(@$numbers); ++$i) {
					$table->setText($i, 3, $numbers->[$i]) if($show_numbers);
					}
				$table->insertCol(0)->setMargin2(5, 5, 3, 3);
				$table->setText(0, 0, "Last Exam");
				$table->setText(0, 2, "% of Participants");
				$table->setText(0, 3, "# of Participants") if($show_numbers);

			if($isComparative && $comp_male_prostate_basis){
				$labellayer = $c->addBarLayer($data, $perlchartdir::Transparent);   $labellayer->setBarGap($bargap);
				$labellayer->setBorderColor($perlchartdir::Transparent);
				# $labellayer->setAggregateLabelFormat("{value|1}%");
				#  $labellayer->setAggregateLabelStyle("arial.ttf", 7) ;

				$markLayer = $c->addBoxWhiskerLayer(undef, undef, undef, undef, $markdata, -1, 0x333333);
				$markLayer->setLineWidth(2);
				#  $markLayer->setDataGap(0.1);
				# Add the legend key for the mark line
				$legendBox->addKey("Comparative Group", 0x333333, 2);

				$layer = $c->addBarLayer3($data, $five_colors);$layer->setBarGap($bargap);
				$layer->setBorderColor(0x000033);
				}
			else	{
				$layer = $c->addBarLayer3($data, $five_colors, $labels);  $layer->setBarGap($bargap);
				$layer->setBorderColor(0x000033);
				#  $layer->setAggregateLabelFormat("{value|1}%");
				# $layer->setAggregateLabelStyle("arial.ttf", 7) ;
				}

			$c->getDrawArea()->setPaletteMode($perlchartdir::ForcePalette);

			if( !$c->makeChart($o_file) )
				{
					copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
				}
			else	{
				$empty_chart{print_prostate} = 0;
				}
			}
			else {
				copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
			}

		}
#14  Exercise
	if (($input->{'pgraphs'} eq 'all' || $input->{'print_exercise'} == 1) &&
		($assessments_chk{GHA} || $assessments_chk{HRA} || $assessments_chk{CRC} || $assessments_chk{OHA} ))
		{
		++$graph_cnt;
 		print "$graph_cnt. Exercise habits<br>" unless $silent;
		#### Exercise Habits
		my $o_file = $GGR_PAGE_DIR . $PARMS{'files_prefix'} . "_ggr_exer.png";

		my ($exer_basis, $exer_good, $exer_some, $exer_none);
		my ($comp_exer_basis, $comp_exer_good, $comp_exer_some, $exer_none);
		$comp_exer_basis = $COMPPARMS{'exer_good'} + $COMPPARMS{'exer_some'} + $COMPPARMS{'exer_none'};

		if($exer_basis = $PARMS{'exer_good'} + $PARMS{'exer_some'} + $PARMS{'exer_none'})
			{
			$exer_good = sprintf("%.1f",($PARMS{'exer_good'}/$exer_basis*100));
			$exer_some = sprintf("%.1f",($PARMS{'exer_some'}/$exer_basis*100));
			$exer_none = sprintf("%.1f",($PARMS{'exer_none'}/$exer_basis*100));

			if($isComparative && $comp_exer_basis){
				$comp_exer_good = sprintf("%.1f",($COMPPARMS{'exer_good'}/$comp_exer_basis*100));
				$comp_exer_some = sprintf("%.1f",($COMPPARMS{'exer_some'}/$comp_exer_basis*100));
				$comp_exer_none = sprintf("%.1f",($COMPPARMS{'exer_none'}/$comp_exer_basis*100));
				}

			my $numbers = [ $PARMS{'exer_good'}, $PARMS{'exer_some'}, $PARMS{'exer_none'} ];
			my $data = [$exer_good ,$exer_some ,$exer_none];
			my $markdata = [ $comp_exer_good ,$comp_exer_some ,$comp_exer_none ] if $isComparative;

			my $labels = ["3+/week", "1-2/week", "Sedentary"];

			my $c = new XYChart($bar_chartwide, $bar_charthigh, 0xffffff);

			$c->setPlotArea(90, 50, 255, 180, $perlchartdir::Transparent, -1, $perlchartdir::Transparent, 0xe0e0e0);

			my $title = $c->addTitle2(8, "Exercise frequency", "arial.ttf", 12);

			my $legendBox;
			my $labellayer;
			my $markLayer;
			my $layer;
			if($isComparative && $comp_exer_basis){
					$legendBox = $c->addLegend($c->getWidth() / 2, $title->getHeight()-7, "arial.ttf", 8);
					$legendBox->setBackground($perlchartdir::Transparent, $perlchartdir::Transparent);
					$legendBox->setAlignment($perlchartdir::TopCenter);
					$legendBox->setLineStyleKey();
				}

			# my $textbox = $c->yAxis()->setTitle("% of Participants");
			# $textbox->setFontStyle("arial.ttf");
			# $textbox->setFontSize(7);
			$c->yAxis()->setLabelFormat("{value}%");
			$c->yAxis()->setLinearScale(0,100,20);

			$c->xAxis()->setLabels($labels);
			$c->xAxis()->setTickLength(1);

				# Convert the labels on the x-axis to a CDMLTable
				my $table = $c->xAxis()->makeLabelTable();
				# Set the default top/bottom margins of the cells to 3 pixels
				$table->getStyle()->setMargin2(0, 0, 3, 3);
				# Use Arial Bold as the font for the first row
				$table->getRowStyle(0)->setFontStyle("arial.ttf");
				$table->getRowStyle(0)->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent);
				$table->appendRow()->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent);
				$table->appendRow()->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent);
				for(my $i = 0; $i < scalar(@$data); ++$i) {
					$table->setText($i, 2, $data->[$i].'%');
					}
				$table->appendRow()->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent) if($show_numbers);
				for(my $i = 0; $i < scalar(@$numbers); ++$i) {
					$table->setText($i, 3, $numbers->[$i]) if($show_numbers);
					}
				$table->insertCol(0)->setMargin2(5, 5, 3, 3);
				$table->setText(0, 0, "Frequency");
				$table->setText(0, 2, "% of Participants");
				$table->setText(0, 3, "# of Participants") if($show_numbers);

			if($isComparative && $comp_exer_basis){
				$labellayer = $c->addBarLayer($data, $perlchartdir::Transparent);   $labellayer->setBarGap($bargap);
				$labellayer->setBorderColor($perlchartdir::Transparent);
				# $labellayer->setAggregateLabelFormat("{value|1}%");
				#  $labellayer->setAggregateLabelStyle("arial.ttf", 7) ;

				$markLayer = $c->addBoxWhiskerLayer(undef, undef, undef, undef, $markdata, -1, 0x333333);
				$markLayer->setLineWidth(2);
				#  $markLayer->setDataGap(0.1);
				# Add the legend key for the mark line
				$legendBox->addKey("Comparative Group", 0x333333, 2);

				$layer = $c->addBarLayer3($data, $five_colors);$layer->setBarGap($bargap);
				$layer->setBorderColor(0x000033);
				}
			else	{
				$layer = $c->addBarLayer3($data, $five_colors, $labels);  $layer->setBarGap($bargap);
				$layer->setBorderColor(0x000033);
				#  $layer->setAggregateLabelFormat("{value|1}%");
				# $layer->setAggregateLabelStyle("arial.ttf", 7) ;
				}

			$c->getDrawArea()->setPaletteMode($perlchartdir::ForcePalette);

			if( !$c->makeChart($o_file) )
				{
					copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
				}
			else	{
				$empty_chart{print_exercise} = 0;
				}
			}
			else {
				copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
			}

		}
#15 Seatbelts
	if (($input->{'pgraphs'} eq 'all' || $input->{'print_seatbelts'} == 1) &&
		($assessments_chk{GHA} || $assessments_chk{HRA} ))
		{
		++$graph_cnt;
 		print "$graph_cnt. Seat belt use<br>" unless $silent;
		#### Seat Belt Habits
		my $o_file = $GGR_PAGE_DIR . $PARMS{'files_prefix'} . "_ggr_sb.png";

		my ($sb_basis, $sb_never, $sb_some, $sb_seldom, $sb_usually, $sb_always);
		my ($comp_sb_basis, $comp_sb_never, $comp_sb_some, $comp_sb_seldom, $comp_sb_usually, $comp_sb_always);
		$comp_sb_basis = $COMPPARMS{'sb_never'} + $COMPPARMS{'sb_some'} + $COMPPARMS{'sb_seldom'} + $COMPPARMS{'sb_usually'} + $COMPPARMS{'sb_always'};

		if($sb_basis = $PARMS{'sb_never'} + $PARMS{'sb_some'} + $PARMS{'sb_seldom'} + $PARMS{'sb_usually'} + $PARMS{'sb_always'})
			{
			$sb_never = sprintf("%.1f",($PARMS{'sb_never'}/$sb_basis*100));
			$sb_some = sprintf("%.1f",($PARMS{'sb_some'}/$sb_basis*100));
			$sb_seldom = sprintf("%.1f",($PARMS{'sb_seldom'}/$sb_basis*100));
			$sb_usually = sprintf("%.1f",($PARMS{'sb_usually'}/$sb_basis*100));
			$sb_always = sprintf("%.1f",($PARMS{'sb_always'}/$sb_basis*100));

			if ($sb_usually + $sb_always >= 70)	{ $PARMS{sb_msg} = "This group of participants is doing very well in regards to seatbelt usage.  " }
			else					{ $PARMS{sb_msg} = "This group of participants needs to improve their seatbelt wearing habits.  " }

			if ($PARMS{'sb_drinkdrive'}) 		{ $PARMS{sb_msg} .= "Of this group, $PARMS{'sb_drinkdrive'} participants reported either drinking and driving or riding with someone who had too much to drink in the last month." }

			if($isComparative && $comp_sb_basis){
				$comp_sb_never = sprintf("%.1f",($COMPPARMS{'sb_never'}/$comp_sb_basis*100));
				$comp_sb_some = sprintf("%.1f",($COMPPARMS{'sb_some'}/$comp_sb_basis*100));
				$comp_sb_seldom = sprintf("%.1f",($COMPPARMS{'sb_seldom'}/$comp_sb_basis*100));
				$comp_sb_usually = sprintf("%.1f",($COMPPARMS{'sb_usually'}/$comp_sb_basis*100));
				$comp_sb_always = sprintf("%.1f",($COMPPARMS{'sb_always'}/$comp_sb_basis*100));
				}

			my $numbers = [ $PARMS{'sb_always'}, $PARMS{'sb_usually'}, $PARMS{'sb_some'}, $PARMS{'sb_seldom'}, $PARMS{'sb_never'} ];
			my $data = [ $sb_always ,$sb_usually ,$sb_some, $sb_seldom, $sb_never];
			my $markdata = [ $comp_sb_always ,$comp_sb_usually ,$comp_sb_some, $comp_sb_seldom, $comp_sb_never ] if $isComparative;

			my $labels = ["Always",    "81-99%",    "41-80%", "1-40%",    "Never"];

			my $c = new XYChart($bar_chartwide, $bar_charthigh, 0xffffff);

			$c->setPlotArea(90, 50, 255, 180, $perlchartdir::Transparent, -1, $perlchartdir::Transparent, 0xe0e0e0);

			my $title = $c->addTitle2(8, "% of trips seatbelts used", "arial.ttf", 12);

			my $legendBox;
			my $labellayer;
			my $markLayer;
			my $layer;
			if($isComparative && $comp_sb_basis){
					$legendBox = $c->addLegend($c->getWidth() / 2, $title->getHeight()-7, "arial.ttf", 8);
					$legendBox->setBackground($perlchartdir::Transparent, $perlchartdir::Transparent);
					$legendBox->setAlignment($perlchartdir::TopCenter);
					$legendBox->setLineStyleKey();
				}

			# my $textbox = $c->yAxis()->setTitle("% of Participants");
			# $textbox->setFontStyle("arial.ttf");
			# $textbox->setFontSize(7);
			$c->yAxis()->setLabelFormat("{value}%");
			$c->yAxis()->setLinearScale(0,100,20);

			$c->xAxis()->setLabels($labels);
			$c->xAxis()->setTickLength(1);

				# Convert the labels on the x-axis to a CDMLTable
				my $table = $c->xAxis()->makeLabelTable();
				# Set the default top/bottom margins of the cells to 3 pixels
				$table->getStyle()->setMargin2(0, 0, 3, 3);
				# Use Arial Bold as the font for the first row
				$table->getRowStyle(0)->setFontStyle("arial.ttf");
				$table->getRowStyle(0)->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent);
				$table->appendRow()->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent);
				$table->appendRow()->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent);
				for(my $i = 0; $i < scalar(@$data); ++$i) {
					$table->setText($i, 2, $data->[$i].'%');
					}
				$table->appendRow()->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent) if($show_numbers);
				for(my $i = 0; $i < scalar(@$numbers); ++$i) {
					$table->setText($i, 3, $numbers->[$i]) if($show_numbers);
					}
				$table->insertCol(0)->setMargin2(5, 5, 3, 3);
				$table->setText(0, 0, "Frequency");
				$table->setText(0, 2, "% of Participants");
				$table->setText(0, 3, "# of Participants") if($show_numbers);

			if($isComparative && $comp_sb_basis){
				$labellayer = $c->addBarLayer($data, $perlchartdir::Transparent);   $labellayer->setBarGap($bargap);
				$labellayer->setBorderColor($perlchartdir::Transparent);
				# $labellayer->setAggregateLabelFormat("{value|1}%");
				#  $labellayer->setAggregateLabelStyle("arial.ttf", 7) ;

				$markLayer = $c->addBoxWhiskerLayer(undef, undef, undef, undef, $markdata, -1, 0x333333);
				$markLayer->setLineWidth(2);
				#  $markLayer->setDataGap(0.1);
				# Add the legend key for the mark line
				$legendBox->addKey("Comparative Group", 0x333333, 2);

				$layer = $c->addBarLayer3($data, $five_colors);$layer->setBarGap($bargap);
				$layer->setBorderColor(0x000033);
				}
			else	{
				$layer = $c->addBarLayer3($data, $five_colors, $labels);  $layer->setBarGap($bargap);
				$layer->setBorderColor(0x000033);
				#  $layer->setAggregateLabelFormat("{value|1}%");
				# $layer->setAggregateLabelStyle("arial.ttf", 7) ;
				}

			$c->getDrawArea()->setPaletteMode($perlchartdir::ForcePalette);

			if( !$c->makeChart($o_file) )
				{
					copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
				}
			else	{
				$empty_chart{print_seatbelts} = 0;
				}
			}
			else {
				copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
			}

		}
#16 Cholesterol
	if (($input->{'pgraphs'} eq 'all' || $input->{'print_cholesterol'} == 1) &&
		($assessments_chk{GHA} || $assessments_chk{HRA} || $assessments_chk{CRC} || $assessments_chk{OHA} ))
		{
		++$graph_cnt;
 		print "$graph_cnt. Cholesterol<br>" unless $silent;
		##### Cholesterol Status
		my $o_file = $GGR_PAGE_DIR . $PARMS{'files_prefix'} . "_ggr_chol.png";

		my ($chol_basis, $chol_high, $chol_med, $chol_low, $chol_unknown);
		my ($comp_chol_basis, $comp_chol_high, $comp_chol_med, $comp_chol_low, $comp_chol_unknown);
		$comp_chol_basis = $COMPPARMS{'chol_high'} + $COMPPARMS{'chol_med'} + $COMPPARMS{'chol_low'} + $COMPPARMS{'chol_unknown'};

		if(($chol_basis = $PARMS{'chol_high'} + $PARMS{'chol_med'} + $PARMS{'chol_low'} + $PARMS{'chol_unknown'}) && $PARMS{'chol_high'} + $PARMS{'chol_med'} + $PARMS{'chol_low'} )
			{
			$chol_high = sprintf("%.1f",($PARMS{'chol_high'}/$chol_basis*100));
			$chol_med = sprintf("%.1f",($PARMS{'chol_med'}/$chol_basis*100));
			$chol_low = sprintf("%.1f",($PARMS{'chol_low'}/$chol_basis*100));
			$chol_unknown = sprintf("%.1f",($PARMS{'chol_unknown'}/$chol_basis*100));

			if ($chol_high > 21)	{ $PARMS{chol_msg} = "There are a high number of participants in your group with cholesterol higher than recommended." }
			else			{ $PARMS{chol_msg} = "This group is below the US average for high cholesterol." }

			if ($chol_unknown > 5 ) {$PARMS{chol_msg} .= "  Screening should be done for those in this group who do not know their cholesterol level."}

			my %chol_lab = (
				low	=> "Under\n" . CHOL_MARGINAL,
				med	=> CHOL_MARGINAL . "\nto\n" . CHOL_HIGH,
				high	=> "Over\n" . CHOL_HIGH
				);

			if($isComparative && $comp_chol_basis){
				$comp_chol_high = sprintf("%.1f",($COMPPARMS{'chol_high'}/$comp_chol_basis*100));
				$comp_chol_med = sprintf("%.1f",($COMPPARMS{'chol_med'}/$comp_chol_basis*100));
				$comp_chol_low = sprintf("%.1f",($COMPPARMS{'chol_low'}/$comp_chol_basis*100));
				$comp_chol_unknown = sprintf("%.1f",($COMPPARMS{'chol_unknown'}/$comp_chol_basis*100));
				}
			my $numbers = [ $PARMS{'chol_low'}, $PARMS{'chol_med'}, $PARMS{'chol_high'} ];
			push (@{$numbers},$PARMS{'chol_unknown'}) if ($PARMS{'chol_unknown'} > 0);
			my $data = [$chol_low ,$chol_med ,$chol_high ];
			push (@{$data}, $chol_unknown) if ($chol_unknown > 0);
			my $markdata = [ $comp_chol_low ,$comp_chol_med ,$comp_chol_high ] if $isComparative;
			push (@{$markdata}, $comp_chol_unknown) if (($comp_chol_unknown > 0 || $chol_unknown > 0) && $isComparative);
			
			my $labels = [$chol_lab{low}, $chol_lab{med}, $chol_lab{high} ];
			push (@{$labels},"unknown") if ( $chol_unknown > 0 || $comp_chol_unknown > 0 );

#			my $labels = [$chol_lab{low}, $chol_lab{med}, $chol_lab{high}, "unknown"];

			my $c = new XYChart($bar_chartwide, $bar_charthigh, 0xffffff);

			$c->setPlotArea(100, 50, 255, 180, $perlchartdir::Transparent, -1, $perlchartdir::Transparent, 0xe0e0e0);

			my $title = $c->addTitle2(8, "Cholesterol levels", "arial.ttf", 12);

			my $legendBox;
			my $labellayer;
			my $markLayer;
			my $layer;
			if($isComparative && $comp_chol_basis){
					$legendBox = $c->addLegend($c->getWidth() / 2, $title->getHeight()-7, "arial.ttf", 8);
					$legendBox->setBackground($perlchartdir::Transparent, $perlchartdir::Transparent);
					$legendBox->setAlignment($perlchartdir::TopCenter);
					$legendBox->setLineStyleKey();
				}

			# my $textbox = $c->yAxis()->setTitle("% of Participants");
			# $textbox->setFontStyle("arial.ttf");
			# $textbox->setFontSize(7);
			$c->yAxis()->setLabelFormat("{value}%");
			$c->yAxis()->setLinearScale(0,100,20);

			$c->xAxis()->setLabels($labels);
			$c->xAxis()->setLabelStyle("arial.ttf", 7);
			$c->xAxis()->setTickLength(1);

				# Convert the labels on the x-axis to a CDMLTable
				my $table = $c->xAxis()->makeLabelTable();
				# Set the default top/bottom margins of the cells to 3 pixels
				$table->getStyle()->setMargin2(0, 0, 3, 3);
				# Use Arial Bold as the font for the first row
				$table->getRowStyle(0)->setFontStyle("arial.ttf");
				$table->getRowStyle(0)->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent);
				$table->appendRow()->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent);
				$table->appendRow()->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent);
				
				for(my $i = 0; $i < scalar(@$data); ++$i) {
					$table->setText($i, 2, $data->[$i].'%');
					}
				$table->appendRow()->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent) if($show_numbers);
				for(my $i = 0; $i < scalar(@$numbers); ++$i) {
					$table->setText($i, 3, $numbers->[$i]) if($show_numbers);
					}
				$table->insertCol(0)->setMargin2(5, 5, 3, 3);
				$table->setText(0, 0, "Levels");
				$table->setText(0, 2, "% of Participants");
				$table->setText(0, 3, "# of Participants") if($show_numbers);

			if($isComparative && $comp_chol_basis){
				$labellayer = $c->addBarLayer($data, $perlchartdir::Transparent);   $labellayer->setBarGap($bargap);
				$labellayer->setBorderColor($perlchartdir::Transparent);
				# $labellayer->setAggregateLabelFormat("{value|1}%");
				#  $labellayer->setAggregateLabelStyle("arial.ttf", 7) ;

				$markLayer = $c->addBoxWhiskerLayer(undef, undef, undef, undef, $markdata, -1, 0x333333);
				$markLayer->setLineWidth(2);
				#  $markLayer->setDataGap(0.1);
				# Add the legend key for the mark line
				$legendBox->addKey("Comparative Group", 0x333333, 2);

				$layer = $c->addBarLayer3($data, $five_colors);$layer->setBarGap($bargap);
				$layer->setBorderColor(0x000033);
				}
			else	{
				$layer = $c->addBarLayer3($data, $five_colors, $labels);  $layer->setBarGap($bargap);
				$layer->setBorderColor(0x000033);
				#  $layer->setAggregateLabelFormat("{value|1}%");
				# $layer->setAggregateLabelStyle("arial.ttf", 7) ;
				}

			$c->getDrawArea()->setPaletteMode($perlchartdir::ForcePalette);

			if( !$c->makeChart($o_file) )
				{
					copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
				}
			else	{
				$empty_chart{print_cholesterol} = 0;
				}
			}
			else {
				copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
			}

		}
#17  Blood Pressure
	if (($input->{'pgraphs'} eq 'all' || $input->{'print_bloodpressure'} == 1) &&
		($assessments_chk{GHA} || $assessments_chk{HRA} || $assessments_chk{CRC} || $assessments_chk{OHA} ))
		{
		++$graph_cnt;
 		print "$graph_cnt. Blood pressures<br>" unless $silent;
		#### Blood Pressure
		my $o_file = $GGR_PAGE_DIR . $PARMS{'files_prefix'} . "_ggr_bp.png";

		my ($bp_basis, $bp_high, $bp_med, $bp_low, $bp_unknown);
		my ($comp_bp_basis, $comp_bp_high, $comp_bp_med, $comp_bp_low, $comp_bp_unknown);
		$comp_bp_basis = $COMPPARMS{'bp_high'} + $COMPPARMS{'bp_med'} + $COMPPARMS{'bp_low'} + $COMPPARMS{'bp_unknown'};

		if($bp_basis = $PARMS{'bp_high'} + $PARMS{'bp_med'} + $PARMS{'bp_low'} + $PARMS{'bp_unknown'})
			{
			$bp_high = sprintf("%.1f",($PARMS{'bp_high'}/$bp_basis*100));
			$bp_med = sprintf("%.1f",($PARMS{'bp_med'}/$bp_basis*100));
			$bp_low = sprintf("%.1f",($PARMS{'bp_low'}/$bp_basis*100));
			$bp_unknown = sprintf("%.1f",($PARMS{'bp_unknown'}/$bp_basis*100));

 			if ($bp_med + $bp_high > 28)	{ $PARMS{bp_msg} = "There are a high number of participants with blood pressure higher than recommended.";
 							  $PARMS{bp_msg} .= "  Of these, $PARMS{bp_meds} are on medication to reduce their blood pressure." if $PARMS{bp_meds} > 1}
 			else				{ $PARMS{bp_msg} = "This group is below the US average (28 percent) for high blood pressure." }

 			if ($PARMS{bp_no_meds} > 0)		{ $PARMS{bp_msg} .= "  $PARMS{bp_no_meds} individuals in this group have high blood pressure and are not taking medicine for it." }
 			if ($bp_unknown > 5 ) 		{ $PARMS{bp_msg} .= "  Screening should be done for those in this group that do not know their blood pressure." }

			my %bp_lab = (
				low	=> "Under\n" . BP_MARGINAL_SYSTOLIC . "/" . BP_MARGINAL_DIASTOLIC,
				med	=> BP_MARGINAL_SYSTOLIC . "/" . BP_MARGINAL_DIASTOLIC . "\nto\n" . BP_HIGH_SYSTOLIC . "/" . BP_HIGH_DIASTOLIC,
				high	=> "Over\n" . BP_HIGH_SYSTOLIC . "/" . BP_HIGH_DIASTOLIC
				);

			if($isComparative && $comp_bp_basis){
				$comp_bp_high = sprintf("%.1f",($COMPPARMS{'bp_high'}/$comp_bp_basis*100));
				$comp_bp_med = sprintf("%.1f",($COMPPARMS{'bp_med'}/$comp_bp_basis*100));
				$comp_bp_low = sprintf("%.1f",($COMPPARMS{'bp_low'}/$comp_bp_basis*100));
				$comp_bp_unknown = sprintf("%.1f",($COMPPARMS{'bp_unknown'}/$comp_bp_basis*100));
				}

			my $numbers = [ $PARMS{'bp_low'} ,$PARMS{'bp_med'} ,$PARMS{'bp_high'}];
			push (@{$numbers}, $PARMS{'bp_unknown'}) if( $PARMS{'bp_unknown'} > 0);
			my $data = [ $bp_low ,$bp_med ,$bp_high];
			push (@{$data}, $bp_unknown) if ($bp_unknown> 0);
			my $markdata = [ $comp_bp_low ,$comp_bp_med ,$comp_bp_high ] if $isComparative;
			push (@{$markdata}, $comp_bp_unknown) if (($comp_bp_unknown > 0 || $bp_unknown > 0) && $isComparative);

			my $labels = [$bp_lab{low}, $bp_lab{med}, $bp_lab{high} ];
			push (@{$labels},"unknown") if ( $bp_unknown > 0 || $comp_bp_unknown > 0 );

			my $c = new XYChart($bar_chartwide, $bar_charthigh, 0xffffff);

			$c->setPlotArea(90, 50, 255, 180, $perlchartdir::Transparent, -1, $perlchartdir::Transparent, 0xe0e0e0);

			my $title = $c->addTitle2(8, "Blood pressure ranges", "arial.ttf", 12);

			my $legendBox;
			my $labellayer;
			my $markLayer;
			my $layer;
			if($isComparative && $comp_bp_basis){
					$legendBox = $c->addLegend($c->getWidth() / 2, $title->getHeight()-7, "arial.ttf", 8);
					$legendBox->setBackground($perlchartdir::Transparent, $perlchartdir::Transparent);
					$legendBox->setAlignment($perlchartdir::TopCenter);
					$legendBox->setLineStyleKey();
				}

			# my $textbox = $c->yAxis()->setTitle("% of Participants");
			# $textbox->setFontStyle("arial.ttf");
			# $textbox->setFontSize(7);
			$c->yAxis()->setLabelFormat("{value}%");
			$c->yAxis()->setLinearScale(0,100,20);

			$c->xAxis()->setLabels($labels);
			$c->xAxis()->setLabelStyle("arial.ttf", 7);
			$c->xAxis()->setTickLength(1);

				# Convert the labels on the x-axis to a CDMLTable
				my $table = $c->xAxis()->makeLabelTable();
				# Set the default top/bottom margins of the cells to 3 pixels
				$table->getStyle()->setMargin2(0, 0, 3, 3);
				# Use Arial Bold as the font for the first row
				$table->getRowStyle(0)->setFontStyle("arial.ttf");
				$table->getRowStyle(0)->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent);
				$table->appendRow()->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent);
				$table->appendRow()->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent);
				for(my $i = 0; $i < scalar(@$data); ++$i) {
					$table->setText($i, 2, $data->[$i].'%');
					}
				$table->appendRow()->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent) if($show_numbers);
				for(my $i = 0; $i < scalar(@$numbers); ++$i) {
					$table->setText($i, 3, $numbers->[$i]) if($show_numbers);
					}
				$table->insertCol(0)->setMargin2(5, 5, 3, 3);
				$table->setText(0, 0, "Range");
				$table->setText(0, 2, "% of Participants");
				$table->setText(0, 3, "# of Participants") if($show_numbers);

			if($isComparative && $comp_bp_basis){
				$labellayer = $c->addBarLayer($data, $perlchartdir::Transparent);   $labellayer->setBarGap($bargap);
				$labellayer->setBorderColor($perlchartdir::Transparent);
				# $labellayer->setAggregateLabelFormat("{value|1}%");
				#  $labellayer->setAggregateLabelStyle("arial.ttf", 7) ;

				$markLayer = $c->addBoxWhiskerLayer(undef, undef, undef, undef, $markdata, -1, 0x333333);
				$markLayer->setLineWidth(2);
				#  $markLayer->setDataGap(0.1);
				# Add the legend key for the mark line
				$legendBox->addKey("Comparative Group", 0x333333, 2);

				$layer = $c->addBarLayer3($data, $five_colors);$layer->setBarGap($bargap);
				$layer->setBorderColor(0x000033);
				}
			else	{
				$layer = $c->addBarLayer3($data, $five_colors, $labels);  $layer->setBarGap($bargap);
				$layer->setBorderColor(0x000033);
				#  $layer->setAggregateLabelFormat("{value|1}%");
				# $layer->setAggregateLabelStyle("arial.ttf", 7) ;
				}

			$c->getDrawArea()->setPaletteMode($perlchartdir::ForcePalette);

			if( !$c->makeChart($o_file) )
				{
					copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
				}
			else	{
				$empty_chart{print_bloodpressure} = 0;
				}
			}
			else {
				copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
			}

		}
#18 Diabetes Risk
	if (($input->{'pgraphs'} eq 'all' || $input->{'print_diabetes'} == 1) &&
		($assessments_chk{DRC} || $manual_drc  ))
		{
		++$graph_cnt;
		carp "in diabetes risk - $PARMS{diabetes_low} + $PARMS{diabetes_med} + $PARMS{diabetes_high}";
 		print "$graph_cnt. Diabetes risk<br>" unless $silent;
		####  Diabetes Assessment Risk levels
		my $o_file = $GGR_PAGE_DIR . $PARMS{'files_prefix'} . "_ggr_diabrisks.png";

		my ($dlparm, $dmparm, $dhparm, $b16_basis);
		$b16_basis = $PARMS{diabetes_low} + $PARMS{diabetes_med} + $PARMS{diabetes_high};

		if ($b16_basis > 0)
			{
			$dlparm = sprintf("%.1f",($PARMS{diabetes_low}/$b16_basis * 100));
			$dmparm = sprintf("%.1f",($PARMS{diabetes_med}/$b16_basis * 100));
			$dhparm = sprintf("%.1f",($PARMS{diabetes_high}/$b16_basis * 100));

			# The labels for the pie chart
			my $labels_tmp = ["Low Risk", "Moderate Risk", "High Risk" ];
			my %data_hash;
			$data_hash{"High Risk"} = $dhparm;
			$data_hash{"Moderate Risk"} = $dmparm;
			$data_hash{"Low Risk"} = $dlparm;

			# The data for the pie chart
			my @data_list;
			my @labels_list;
			foreach my $label (sort { $data_hash{$a} <=> $data_hash{$b} } keys %data_hash) {
				if ( $data_hash{$label}  > .01) {
					push @data_list, $data_hash{$label};
					push @labels_list, $label;}
				}
			my $numbers = [ $PARMS{diabetes_low}, $PARMS{diabetes_med}, $PARMS{diabetes_high}];
			my $data = [ $dlparm ,$dmparm ,$dhparm];
			my $labels = ["Low Risk", "Moderate Risk", "High Risk" ];

			# create the bar chart
			$d = new XYChart($bar_chartwide, $bar_charthigh, 0xffffff);

			$d->setPlotArea(90, 50, 255, 180, $perlchartdir::Transparent, -1, $perlchartdir::Transparent, 0xe0e0e0);

			my $title = $d->addTitle2(8, "Diabetes risk levels", "arial.ttf", 12);

			if($isComparative && $comp_basis){
				$legendBox = $d->addLegend($d->getWidth() / 2, $title->getHeight()-7, "arial.ttf", 8);
				$legendBox->setBackground($perlchartdir::Transparent, $perlchartdir::Transparent);
				$legendBox->setAlignment($perlchartdir::TopCenter);
				$legendBox->setLineStyleKey();
				}


#				$textbox = $d->yAxis()->setTitle("% of Participants");
			# $textbox->setFontStyle("arial.ttf");
			# $textbox->setFontSize(7);
			$d->yAxis()->setLabelFormat("{value}%");

			$d->xAxis()->setLabels($labels);
			$d->xAxis()->setTickLength(0);
			$d->yAxis()->setLinearScale(0,100,20);

			# Convert the labels on the x-axis to a CDMLTable
			my $table = $d->xAxis()->makeLabelTable();
			# Set the default top/bottom margins of the cells to 3 pixels
			$table->getStyle()->setMargin2(0, 0, 3, 3);
			# Use Arial Bold as the font for the first row
			$table->getRowStyle(0)->setFontStyle("arial.ttf");
			$table->getRowStyle(0)->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent);
			$table->appendRow()->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent);
			$table->appendRow()->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent);
			for(my $i = 0; $i < scalar(@$data); ++$i) {
				$table->setText($i, 2, $data->[$i].'%');
				}
			$table->insertCol(0)->setMargin2(5, 5, 3, 3);
			$table->setText(0, 0, "Risk Level");
			$table->setText(0, 2, "% of Participants");
			$table->setText(0, 3, "# of Participants") if($show_numbers);


			if($isComparative && $comp_basis){
				$labellayer = $d->addBarLayer($data, $perlchartdir::Transparent);
				$labellayer->setBorderColor($perlchartdir::Transparent);
				# $labellayer->setAggregateLabelFormat("{value|1}%");
				#  $labellayer->setAggregateLabelStyle("arial.ttf", 7) ;

				$markLayer = $d->addBoxWhiskerLayer(undef, undef, undef, undef, $markdata, -1, 0x333333);
				$markLayer->setLineWidth(2);
				#  $markLayer->setDataGap(0.1);
				# Add the legend key for the mark line
				$legendBox->addKey("Comparative Group", 0x333333, 2);

				$layer = $d->addBarLayer3($data, $five_colors);$layer->setBarGap($bargap);
				$layer->setBorderColor(0x000033);

				}
			else	{
				$layer = $d->addBarLayer3($data, $five_colors, $labels);  $layer->setBarGap($bargap);
				$layer->setBorderColor(0x000033);
				#  $layer->setAggregateLabelFormat("{value|1}%");
				# $layer->setAggregateLabelStyle("arial.ttf", 7) ;
				}
			$d->getDrawArea()->setPaletteMode($perlchartdir::ForcePalette);

			if( !$d->makeChart($o_file) )
				{
					copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
				}
			else	{
					$empty_chart{print_diabetes} = 0;
				}
			}
		else	{
				copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
			}

		}
#19  Cardiac
	if (($input->{'pgraphs'} eq 'all' || $input->{'print_cardiac'} == 1) &&
		($assessments_chk{CRC} || $manual_crc ))
		{
		++$graph_cnt;
#		carp "in cardiac risk - $PARMS{cardiac_low} + $PARMS{cardiac_med} + $PARMS{cardiac_mod} + $PARMS{cardiac_high}";
 		print "$graph_cnt. Cardiac risk<br>" unless $silent;
		####  Cardiac Assessment Risk levels
		my $o_file = $GGR_PAGE_DIR . $PARMS{'files_prefix'} . "_ggr_cardrisks.png";

		my $comp_basis = $COMPPARMS{cardiac_low} + $COMPPARMS{cardiac_med} + $COMPPARMS{cardiac_mod} + $COMPPARMS{cardiac_high};

		my ($clparm, $cmedparm, $cmodparm, $chparm, $b17_basis);
		my ($compclparm, $compcmedparm, $compcmodparm, $compchparm);

		if ( $b17_basis = $PARMS{cardiac_low} + $PARMS{cardiac_med} + $PARMS{cardiac_mod} + $PARMS{cardiac_high} )
			{
			$clparm = sprintf("%.1f",($PARMS{cardiac_low}/$b17_basis * 100));
			$cmedparm = sprintf("%.1f",($PARMS{cardiac_med}/$b17_basis * 100));
			$cmodparm = sprintf("%.1f",($PARMS{cardiac_mod}/$b17_basis * 100));
			$chparm = sprintf("%.1f",($PARMS{cardiac_high}/$b17_basis * 100));

			if($isComparative && $comp_basis){
				$compclparm = sprintf("%.1f",($COMPPARMS{cardiac_low}/$comp_basis * 100));
				$compcmedparm = sprintf("%.1f",($COMPPARMS{cardiac_med}/$comp_basis * 100));
				$compcmodparm = sprintf("%.1f",($COMPPARMS{cardiac_mod}/$comp_basis * 100));
				$compchparm = sprintf("%.1f",($COMPPARMS{cardiac_high}/$comp_basis * 100));
				}

			# The labels for the pie chart
			my $labels_tmp = ["Low Risk", "Moderate Risk", "High Risk", "Very High Risk" ];
			my %data_hash;
			$data_hash{"Very High Risk"} = $chparm;
			$data_hash{"High Risk"} = $cmedparm;
			$data_hash{"Moderate Risk"} = $cmodparm;
			$data_hash{"Low Risk"} = $clparm;

			# The data for the pie chart
			my $numbers = [ $PARMS{cardiac_low}, $PARMS{cardiac_mod}, $PARMS{cardiac_med},  $PARMS{cardiac_high} ];
			my $data = [ $clparm, $cmodparm, $cmedparm, $chparm ];
			my $markdata = [ $compclparm, $compcmodparm, $compcmedparm, $compchparm ] if ($isComparative);
			my $labels = ["Low Risk", "Moderate Risk", "High Risk", "Very High Risk" ];

			# create the bar chart
			$d = new XYChart($bar_chartwide, $bar_charthigh, 0xffffff);

			$d->setPlotArea(90, 50, 255, 180, $perlchartdir::Transparent, -1, $perlchartdir::Transparent, 0xe0e0e0);

			my $title = $d->addTitle2(8, "Cardiac risk levels", "arial.ttf", 12);

			if($isComparative && $comp_basis){
				$legendBox = $d->addLegend($d->getWidth() / 2, $title->getHeight()-7, "arial.ttf", 8);
				$legendBox->setBackground($perlchartdir::Transparent, $perlchartdir::Transparent);
				$legendBox->setAlignment($perlchartdir::TopCenter);
				$legendBox->setLineStyleKey();
				}


#				$textbox = $d->yAxis()->setTitle("% of Participants");
			# $textbox->setFontStyle("arial.ttf");
			# $textbox->setFontSize(7);
			$d->yAxis()->setLabelFormat("{value}%");

			$d->xAxis()->setLabels($labels);
			$d->xAxis()->setTickLength(0);
			$d->yAxis()->setLinearScale(0,100,20);

			# Convert the labels on the x-axis to a CDMLTable
			my $table = $d->xAxis()->makeLabelTable();
			# Set the default top/bottom margins of the cells to 3 pixels
			$table->getStyle()->setMargin2(0, 0, 3, 3);
			# Use Arial Bold as the font for the first row
			$table->getRowStyle(0)->setFontStyle("arial.ttf");
			$table->getRowStyle(0)->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent);
			$table->appendRow()->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent);
			$table->appendRow()->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent);
			for(my $i = 0; $i < scalar(@$data); ++$i) {
				$table->setText($i, 2, $data->[$i].'%');
				}
			$table->appendRow()->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent) if($show_numbers);
			for(my $i = 0; $i < scalar(@$numbers); ++$i) {
				$table->setText($i, 3, $numbers->[$i]) if($show_numbers);
				}
			$table->insertCol(0)->setMargin2(5, 5, 3, 3);
			$table->setText(0, 0, "Risk Level");
			$table->setText(0, 2, "% of Participants");
			$table->setText(0, 3, "# of Participants") if($show_numbers);


			if($isComparative && $comp_basis){
				$labellayer = $d->addBarLayer($data, $perlchartdir::Transparent);
				$labellayer->setBorderColor($perlchartdir::Transparent);
				# $labellayer->setAggregateLabelFormat("{value|1}%");
				#  $labellayer->setAggregateLabelStyle("arial.ttf", 7) ;

				$markLayer = $d->addBoxWhiskerLayer(undef, undef, undef, undef, $markdata, -1, 0x333333);
				$markLayer->setLineWidth(2);
				#  $markLayer->setDataGap(0.1);
				# Add the legend key for the mark line
				$legendBox->addKey("Comparative Group", 0x333333, 2);

				$layer = $d->addBarLayer3($data, $five_colors);$layer->setBarGap($bargap);
				$layer->setBorderColor(0x000033);

				}
			else	{
				$layer = $d->addBarLayer3($data, $five_colors, $labels);  $layer->setBarGap($bargap);
				$layer->setBorderColor(0x000033);
				#  $layer->setAggregateLabelFormat("{value|1}%");
				# $layer->setAggregateLabelStyle("arial.ttf", 7) ;
				}
			$d->getDrawArea()->setPaletteMode($perlchartdir::ForcePalette);

			if( !$d->makeChart($o_file) )
				{
					copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
				}
			else	{
					$empty_chart{print_cardiac} = 0;
				}
			}
		else	{
				copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
			}

		}
#20 Fitness Assessment
	if (($input->{'pgraphs'} eq 'all' || $input->{'print_fitness'} == 1) &&
		($assessments_chk{FIT} ))
		{
		++$graph_cnt;
 		print "$graph_cnt. Fitness results<br>" unless $silent;
		####  Fitness assessment results
		my $o_file = $GGR_PAGE_DIR . $PARMS{'files_prefix'} . "_ggr_fit.png";

		if ( $PARMS{FIT_cnt} > 0 )
			{
			my $fit_step_basis = ($PARMS{'fit_step_low'}+$PARMS{'fit_step_med'}+$PARMS{'fit_step_high'});
			my $fit_sits_basis = ($PARMS{'fit_sits_low'}+$PARMS{'fit_sits_med'}+$PARMS{'fit_sits_high'});
			my $fit_push_basis = ($PARMS{'fit_push_low'}+$PARMS{'fit_push_med'}+$PARMS{'fit_push_high'});
			my $fit_flex_basis = ($PARMS{'fit_flex_low'}+$PARMS{'fit_flex_med'}+$PARMS{'fit_flex_high'});

			my $low_data = [(int($PARMS{'fit_step_low'}/$fit_step_basis*100)), (int($PARMS{'fit_sits_low'}/$fit_sits_basis*100)), (int($PARMS{'fit_push_low'}/$fit_push_basis*100)), (int($PARMS{'fit_flex_low'}/$fit_flex_basis*100))];
			my $medium_data = [(int($PARMS{'fit_step_med'}/$fit_step_basis*100)), (int($PARMS{'fit_sits_med'}/$fit_sits_basis*100)), (int($PARMS{'fit_push_med'}/$fit_push_basis*100)), (int($PARMS{'fit_flex_med'}/$fit_flex_basis*100))];
			my $high_data = [(int($PARMS{'fit_step_high'}/$fit_step_basis*100)), (int($PARMS{'fit_sits_high'}/$fit_sits_basis*100)), (int($PARMS{'fit_push_high'}/$fit_push_basis*100)), (int($PARMS{'fit_flex_high'}/$fit_flex_basis*100))];
			my $labels = ["Cardio\nPulse", "Strength\nSit ups", "Strength\nPush ups","Flexibility\nReach"];
			my @set_legend = (  'Low Fitness', 'Medium Fitness', 'High Fitness' );
			my $c = new XYChart($bar_chartwide, $bar_charthigh, 0xffffff);

			$c->setPlotArea(90, 70, 255, 180, $perlchartdir::Transparent, -1, $perlchartdir::Transparent, 0xe0e0e0);

#			$c->addLegend(288, 2, 1, "arial.ttf", 8)->setBackground($perlchartdir::Transparent);
 			$c->addLegend(90, 12, 0, "arial.ttf", 8)->setBackground($perlchartdir::Transparent);
#			$c->addLegend(298, 40, 1, "arial.ttf", 8)->setBackground($perlchartdir::Transparent, $perlchartdir::Transparent);

			my $title = $c->addTitle2(8, "Assessed areas", "arial.ttf", 12);

			my $textbox = $c->yAxis()->setTitle("% Participants");
			# $textbox->setFontStyle("arial.ttf");
			# $textbox->setFontSize(7);
			$c->yAxis()->setLabelFormat("{value}%");
			$c->yAxis()->setLinearScale(0,100,20);

			$c->xAxis()->setLabels($labels);
			$c->xAxis()->setTickLength(1);

			my $layer = $c->addBarLayer2($perlchartdir::Stack);
			$layer->addDataSet($low_data, 0xa1b69a, "Low\nFitness");
			$layer->addDataSet($medium_data, 0xe7cfa5, "Medium\nFitness");
			$layer->addDataSet($high_data, 0xcb8368, "High\nFitness");
			$layer->setBorderColor(0x000033);
			$layer->setDataLabelFormat("{value|1}%");
			$layer->setDataLabelStyle("arial.ttf", 7)->setAlignment($perlchartdir::Center);
			$layer->setLegend($perlchartdir::ReverseLegend);

			$c->getDrawArea()->setPaletteMode($perlchartdir::ForcePalette);

			if( !$c->makeChart($o_file) )
				{
					copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
				}
			else	{
				$empty_chart{print_fitness} = 0;
				}
			}
		else	{
				copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
			}

		}
#21 Well-being Assessment (old clients only)
	if (($input->{'pgraphs'} eq 'all' || $input->{'print_wellbeing'} == 1) &&
		($assessments_chk{GWB} ))
		{
		++$graph_cnt;
 		print "$graph_cnt. Well-being<br>" unless $silent;
		####  General Well-being assessment results
		my $o_file = $GGR_PAGE_DIR . $PARMS{'files_prefix'} . "_ggr_gwb.png";

		if ( $PARMS{GWB_cnt} > 0 )
			{
			my $gwb_stress_basis = ($PARMS{'gwb_stress_low'}+$PARMS{'gwb_stress_med'}+$PARMS{'gwb_stress_high'});
			my $gwb_depression_basis = ($PARMS{'gwb_depression_low'}+$PARMS{'gwb_depression_med'}+$PARMS{'gwb_depression_high'});
			my $gwb_health_basis = ($PARMS{'gwb_health_low'}+$PARMS{'gwb_health_med'}+$PARMS{'gwb_health_high'});
			my $gwb_control_basis = ($PARMS{'gwb_control_low'}+$PARMS{'gwb_control_med'}+$PARMS{'gwb_control_high'});
			my $gwb_being_basis = ($PARMS{'gwb_being_low'}+$PARMS{'gwb_being_med'}+$PARMS{'gwb_being_high'});
			my $gwb_vitality_basis = ($PARMS{'gwb_vitality_low'}+$PARMS{'gwb_vitality_med'}+$PARMS{'gwb_vitality_high'});

			my $low_data = [(int($PARMS{'gwb_stress_low'}/$gwb_stress_basis*100)), (int($PARMS{'gwb_depression_low'}/$gwb_depression_basis*100)), (int($PARMS{'gwb_control_high'}/$gwb_control_basis*100)), (int($PARMS{'gwb_being_high'}/$gwb_being_basis*100)), (int($PARMS{'gwb_vitality_high'}/$gwb_vitality_basis*100)), (int($PARMS{'gwb_health_high'}/$gwb_health_basis*100))];
			my $medium_data = [(int($PARMS{'gwb_stress_med'}/$gwb_stress_basis*100)), (int($PARMS{'gwb_depression_med'}/$gwb_depression_basis*100)), (int($PARMS{'gwb_control_med'}/$gwb_control_basis*100)), (int($PARMS{'gwb_being_med'}/$gwb_being_basis*100)), (int($PARMS{'gwb_vitality_med'}/$gwb_vitality_basis*100)), (int($PARMS{'gwb_health_med'}/$gwb_health_basis*100))];
			my $high_data = [(int($PARMS{'gwb_stress_high'}/$gwb_stress_basis*100)), (int($PARMS{'gwb_depression_high'}/$gwb_depression_basis*100)), (int($PARMS{'gwb_control_low'}/$gwb_control_basis*100)), (int($PARMS{'gwb_being_low'}/$gwb_being_basis*100)), (int($PARMS{'gwb_vitality_low'}/$gwb_vitality_basis*100)), (int($PARMS{'gwb_health_low'}/$gwb_health_basis*100))];
			my $labels = ["Stress",                                           "Depression",                                                     "Self Control",                                                "Well-being",                                    "Vitality",                                                 "Health"];
			my @set_legend = (  'Positive Attitude', 'Neutral Attitude' , 'Negative Attitude' );
			my $c = new XYChart($bar_chartwide, $bar_charthigh, 0xffffff);

			$c->setPlotArea(90, 70, 255, 180, $perlchartdir::Transparent, -1, $perlchartdir::Transparent, 0xe0e0e0);

#			$c->addLegend(288, 2, 1, "arial.ttf", 8)->setBackground($perlchartdir::Transparent);
			$c->addLegend(80, 2, 0, "arial.ttf", 8)->setBackground($perlchartdir::Transparent);
#			$c->addLegend(238, 22, 1, "arial.ttf", 8)->setBackground($perlchartdir::Transparent, $perlchartdir::Transparent);

			my $title = $c->addTitle2(8, "Assessed attitudes", "arial.ttf", 12);

			my $textbox = $c->yAxis()->setTitle("% Participants");
			# $textbox->setFontStyle("arial.ttf");
			# $textbox->setFontSize(7);
			$c->yAxis()->setLabelFormat("{value}%");
			$c->yAxis()->setLinearScale(0,100,20);

			$c->xAxis()->setLabels($labels);
			$c->xAxis()->setLabelStyle("arialbd.ttf", 7, 0x000000, 45);
			$c->xAxis()->setTickLength(1);

			my $layer = $c->addBarLayer2($perlchartdir::Stack);
			$layer->addDataSet($low_data, 0xa1b69a, "Positive\nAttitude");
			$layer->addDataSet($medium_data, 0xe7cfa5, "Neutral\nAttitude");
			$layer->addDataSet($high_data, 0xcb8368, "Negative\nAttitude");
			$layer->setBorderColor(0x000033);
			$layer->setDataLabelFormat("{value|1}%");
			$layer->setDataLabelStyle("arial.ttf", 7)->setAlignment($perlchartdir::Center);
			$layer->setLegend($perlchartdir::ReverseLegend);

			$c->getDrawArea()->setPaletteMode($perlchartdir::ForcePalette);

			if( !$c->makeChart($o_file) )
				{
					copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
				}
			else	{
				$empty_chart{print_wellbeing} = 0;
				}
			}
		else	{
				copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
			}

		}
#22 Well-being (GHA and HRA Assessments input only)
	if (($input->{'pgraphs'} eq 'all' || $input->{'print_wellbeing2'} == 1) &&
		($assessments_chk{GWB} || $assessments_chk{HRA}  || $assessments_chk{GHA} || $assessments_chk{OHA}))
		{
		++$graph_cnt;
 		print "$graph_cnt. Stress & depression<br>" unless $silent;
		####  General Well-being assessment results new HRA format
		my $o_file = $GGR_PAGE_DIR . $PARMS{'files_prefix'} . "_ggr1_gwb.png";
		my $gwb_stress_basis = ($PARMS{'gwb_stress_low'}+$PARMS{'gwb_stress_med'}+$PARMS{'gwb_stress_high'});
		my $gwb_depression_basis = ($PARMS{'gwb_depression_low'}+$PARMS{'gwb_depression_med'}+$PARMS{'gwb_depression_high'});

		if ( ($PARMS{HRA_cnt} > 0 || $PARMS{GWB_cnt} > 0 || $PARMS{GHA_cnt} > 0) && ($gwb_stress_basis > 0 && $gwb_depression_basis > 0))
			{
			my $gwb_stress_basis = ($PARMS{'gwb_stress_low'}+$PARMS{'gwb_stress_med'}+$PARMS{'gwb_stress_high'});
			my $gwb_depression_basis = ($PARMS{'gwb_depression_low'}+$PARMS{'gwb_depression_med'}+$PARMS{'gwb_depression_high'});


			my $low_data = [(int($PARMS{'gwb_stress_low'}/$gwb_stress_basis*100)), (int($PARMS{'gwb_depression_low'}/$gwb_depression_basis*100))];
			my $medium_data = [(int($PARMS{'gwb_stress_med'}/$gwb_stress_basis*100)), (int($PARMS{'gwb_depression_med'}/$gwb_depression_basis*100))];
			my $high_data = [(int($PARMS{'gwb_stress_high'}/$gwb_stress_basis*100)), (int($PARMS{'gwb_depression_high'}/$gwb_depression_basis*100))];
			my $labels = ["Stress", "Depression"];
			my @set_legend = (  'Positive Attitude', 'Neutral Attitude' , 'Negative Attitude' );
			my $c = new XYChart($bar_chartwide, $bar_charthigh, 0xffffff);

			$c->setPlotArea(50, 50, 185, 230, $perlchartdir::Transparent, -1, $perlchartdir::Transparent, 0xe0e0e0);

#			$c->addLegend(288, 2, 1, "arial.ttf", 8)->setBackground($perlchartdir::Transparent);
#			$c->addLegend(70, 2, 0, "arial.ttf", 8)->setBackground($perlchartdir::Transparent);
			$c->addLegend(238, 22, 1, "arial.ttf", 8)->setBackground($perlchartdir::Transparent, $perlchartdir::Transparent);

			my $title = $c->addTitle2(8, "Assessed attitudes", "arial.ttf", 12);

			my $textbox = $c->yAxis()->setTitle("% Participants");
			# $textbox->setFontStyle("arial.ttf");
			# $textbox->setFontSize(7);
			$c->yAxis()->setLabelFormat("{value}%");
			$c->yAxis()->setLinearScale(0,100,20);

			$c->xAxis()->setLabels($labels);
			$c->xAxis()->setTickLength(1);

			my $layer = $c->addBarLayer2($perlchartdir::Stack);
			$layer->addDataSet($low_data, 0xa1b69a, "Positive\nAttitude");
			$layer->addDataSet($medium_data, 0xe7cfa5, "Neutral\nAttitude");
			$layer->addDataSet($high_data, 0xcb8368, "Negative\nAttitude");
			$layer->setBorderColor(0x000033);
			$layer->setDataLabelFormat("{value|1}%");
			$layer->setDataLabelStyle("arial.ttf", 7)->setAlignment($perlchartdir::Center);
			$layer->setLegend($perlchartdir::ReverseLegend);

			$c->getDrawArea()->setPaletteMode($perlchartdir::ForcePalette);

			if( !$c->makeChart($o_file) )
				{
					copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
				}
			else	{
				$empty_chart{print_wellbeing2} = 0;
				}
			}
		else	{
				copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
			}

		}
#23 Self Reported Conditions
	if (($input->{'pgraphs'} eq 'all' || $input->{'print_selfreported'} == 1 || $input->{'print_srdisease'} == 1) )
#		&& 	( ($assessments_chk{GHA} &&  $PARMS{GHA_cnt} )  || ( $assessments_chk{HRA}  &&  $PARMS{HRA_cnt} )  || ( $assessments_chk{OHA}  &&  $PARMS{OHA_cnt} )))
		{
		++$graph_cnt;
 		print "$graph_cnt. Self reported conditions<br>" unless $silent;
		####  Self Reported disease
		my $o_file = $GGR_PAGE_DIR . $PARMS{'files_prefix'} . "_ggr_srd.png";

		my @dis_list = ( 'my_cancer', 'my_diabetes', 'my_heart', 'my_hrtdisease', 'my_bp', 'my_chol', 'my_stroke' );
		my $disease_max = 10;
		my %diseases;
		my %comp_diseases;
		my $xcnt = $PARMS{HRA_cnt}+$PARMS{GHA_cnt}+$PARMS{OHA_cnt};
		my $xcnt1 = $COMPPARMS{HRA_cnt}+$COMPPARMS{GHA_cnt}+$COMPPARMS{OHA_cnt};


		if($xcnt > 0)
			{
			foreach (@dis_list) {
				$diseases{$_} = (int($PARMS{$_}/$xcnt*100));
				$comp_diseases{$_} = (int($COMPPARMS{$_}/$xcnt1*100)) if ($isComparative && $xcnt1);
				}
			my @g1;
			my @g2;
			my @g3;
			if($PARMS{'my_cancer'}){ push(@g1, 'Cancer'); push(@g2, $diseases{'my_cancer'}); push(@g3, $comp_diseases{'my_cancer'}) if $isComparative;}
			if($PARMS{'my_copd'}){ push(@g1, 'COPD'); push(@g2, $diseases{'my_copd'}); push(@g3, $comp_diseases{'my_copd'}) if $isComparative;}
			if($PARMS{'my_diabetes'}){ push(@g1, "Diabetes"); push(@g2, $diseases{'my_diabetes'}); push(@g3, $comp_diseases{'my_diabetes'}) if $isComparative;}
			if($PARMS{'my_heart'}){ push(@g1, "Heart attack"); push(@g2, $diseases{'my_heart'}); push(@g3, $comp_diseases{'my_heart'}) if $isComparative;}
			if($PARMS{'my_hrtdisease'}){ push(@g1, "Heart disease"); push(@g2, $diseases{'my_hrtdisease'}); push(@g3, $comp_diseases{'my_hrtdisease'}) if $isComparative;}
			if($PARMS{'my_bp'}){ push(@g1, "High BP"); push(@g2, $diseases{'my_bp'}); push(@g3, $comp_diseases{'my_bp'}) if $isComparative;}
			if($PARMS{'my_chol'}){ push(@g1, "High cholesterol"); push(@g2, $diseases{'my_chol'}); push(@g3, $comp_diseases{'my_chol'}) if $isComparative;}
			if($PARMS{'my_ibs'}){ push(@g1, 'IBS'); push(@g2, $diseases{'my_ibs'}); push(@g3, $comp_diseases{'my_ibs'}) if $isComparative;}
			if($PARMS{'my_stroke'}){ push(@g1, "Stroke"); push(@g2, $diseases{'my_stroke'}); push(@g3, $comp_diseases{'my_stroke'}) if $isComparative;}
			my $markdata = \@g3;
			my $data = \@g2;
			my $labels = \@g1;
			my $c = new XYChart($wbar_chartwide, $wbar_charthigh, 0xffffff);

			$c->setPlotArea(90, 50, 255, 180, $perlchartdir::Transparent, -1, $perlchartdir::Transparent, 0xe0e0e0);

			my $title = $c->addTitle2(8, "Disease", "arial.ttf", 12);

			my $legendBox;
			my $labellayer;
			my $markLayer;
			my $layer;
			if($isComparative && $xcnt1){
					$legendBox = $c->addLegend($c->getWidth() / 2, $title->getHeight()-7, "arial.ttf", 8);
					$legendBox->setBackground($perlchartdir::Transparent, $perlchartdir::Transparent);
					$legendBox->setAlignment($perlchartdir::TopCenter);
					$legendBox->setLineStyleKey();
				}

			# my $textbox = $c->yAxis()->setTitle("% of Participants");
			# $textbox->setFontStyle("arial.ttf");
			# $textbox->setFontSize(7);
			$c->yAxis()->setLabelFormat("{value}%");
			$c->yAxis()->setLinearScale(0,100,20);

			$c->xAxis()->setLabels($labels);
			$c->xAxis()->setLabelStyle("arialbd.ttf", 7, 0x000000, 45);
			$c->xAxis()->setTickLength(1);

				# Convert the labels on the x-axis to a CDMLTable
				my $table = $c->xAxis()->makeLabelTable();
				# Set the default top/bottom margins of the cells to 3 pixels
				$table->getStyle()->setMargin2(0, 0, 3, 3);
				# Use Arial Bold as the font for the first row
				$table->getRowStyle(0)->setFontStyle("arial.ttf");
				$table->getRowStyle(0)->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent);
				$table->appendRow()->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent);
				$table->appendRow()->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent);
				for(my $i = 0; $i < scalar(@$data); ++$i) {
					$table->setText($i, 2, $data->[$i].'%');
					}
				$table->insertCol(0)->setMargin2(5, 5, 3, 3);
				$table->setText(0, 0, "Conditions");
				$table->setText(0, 2, "% of Participants");
				$table->setText(0, 3, "# of Participants") if($show_numbers);

			if($isComparative && $xcnt1){
				$labellayer = $c->addBarLayer($data, $perlchartdir::Transparent);   $labellayer->setBarGap($bargap);
				$labellayer->setBorderColor($perlchartdir::Transparent);
				# $labellayer->setAggregateLabelFormat("{value|1}%");
				#  $labellayer->setAggregateLabelStyle("arial.ttf", 7) ;

				$markLayer = $c->addBoxWhiskerLayer(undef, undef, undef, undef, $markdata, -1, 0x333333);
				$markLayer->setLineWidth(2);
				#  $markLayer->setDataGap(0.1);
				# Add the legend key for the mark line
				$legendBox->addKey("Comparative Group", 0x333333, 2);

				$layer = $c->addBarLayer3($data, $ten_colors);$layer->setBarGap($bargap);
				$layer->setBorderColor(0x000033);
				}
			else	{
				$layer = $c->addBarLayer3($data, $ten_colors, $labels);
				$layer->setBorderColor(0x000033);
				#  $layer->setAggregateLabelFormat("{value|1}%");
				# $layer->setAggregateLabelStyle("arial.ttf", 7) ;
				}

			$c->getDrawArea()->setPaletteMode($perlchartdir::ForcePalette);

			if( !$c->makeChart($o_file) )
				{
					copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
				}
			else	{
				$empty_chart{print_selfreported} = 0;
				}
			}
			else {
				copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
			}

		}
#24  Self Reported Family History
	if (($input->{'pgraphs'} eq 'all' || $input->{'print_familyhistory'} == 1 || $input->{'print_srfam'} == 1)  )
#		( $assessments_chk{HRA} ) && ( $PARMS{HRA_cnt} ))
		{
		++$graph_cnt;
 		print "$graph_cnt. Family history<br>" unless $silent;
		####  Self Reported family history
		my $o_file = $GGR_PAGE_DIR . $PARMS{'files_prefix'} . "_ggr_srfh.png";

		my @dis_list = ( 'fh_cancer', 'fh_diabetes', 'fh_heart', 'fh_hrtdisease', 'fh_bp', 'fh_chol', 'fh_stroke', 'fh_copd', 'fh_ibs' );
		my $disease_max = 10;
		my %diseases;
		my %comp_diseases;

		foreach (@dis_list) {
			$diseases{$_} = (int($PARMS{$_}/($PARMS{user_count})*100)) if $PARMS{$_};
			$comp_diseases{$_} = (int($COMPPARMS{$_}/$COMPPARMS{user_count}*100)) if ($isComparative && $COMPPARMS{user_count});
			}


		if(($PARMS{HRA_cnt} > 0 || $PARMS{GHA_cnt} > 0  || $PARMS{DRC_cnt} > 0  || $PARMS{CRC_cnt} > 0  || $PARMS{OHA_cnt} > 0 ) && ( $PARMS{'fh_cancer'} || $PARMS{'fh_diabetes'} || $PARMS{'fh_heart'} || $PARMS{'fh_hrtdisease'} || $PARMS{'fh_bp'} || $PARMS{'fh_chol'} || $PARMS{'fh_stroke'}))
			{
			my $markdata;
			my $data;
			my $labels;
			my @g1;
			my @g2;
			my @g3;
			if($PARMS{'fh_cancer'}){ push(@g1, 'Cancer'); push(@g2, $diseases{'fh_cancer'}); push(@g3, $comp_diseases{'fh_cancer'}) if $isComparative;}
			if($PARMS{'fh_copd'}){ push(@g1, 'COPD'); push(@g2, $diseases{'fh_copd'}); push(@g3, $comp_diseases{'fh_copd'}) if $isComparative;}
			if($PARMS{'fh_diabetes'}){ push(@g1, "Diabetes"); push(@g2, $diseases{'fh_diabetes'}); push(@g3, $comp_diseases{'fh_diabetes'}) if $isComparative;}
			if($PARMS{'fh_heart'}){ push(@g1, "Heart attack"); push(@g2, $diseases{'fh_heart'}); push(@g3, $comp_diseases{'fh_heart'}) if $isComparative;}
			if($PARMS{'fh_hrtdisease'}){ push(@g1, "Heart disease"); push(@g2, $diseases{'fh_hrtdisease'}); push(@g3, $comp_diseases{'fh_hrtdisease'}) if $isComparative;}
			if($PARMS{'fh_bp'}){ push(@g1, "High BP"); push(@g2, $diseases{'fh_bp'}); push(@g3, $comp_diseases{'fh_bp'}) if $isComparative;}
			if($PARMS{'fh_chol'}){ push(@g1, "High cholesterol"); push(@g2, $diseases{'fh_chol'}); push(@g3, $comp_diseases{'fh_chol'}) if $isComparative;}
			if($PARMS{'fh_ibs'}){ push(@g1, 'IBS'); push(@g2, $diseases{'fh_ibs'}); push(@g3, $comp_diseases{'fh_ibs'}) if $isComparative;}
			if($PARMS{'fh_stroke'}){ push(@g1, "Stroke"); push(@g2, $diseases{'fh_stroke'}); push(@g3, $comp_diseases{'fh_stroke'}) if $isComparative;}
			$markdata = \@g3;
			$data = \@g2;
			$labels = \@g1;

			my $c = new XYChart($wbar_chartwide, $wbar_charthigh, 0xffffff);

			$c->setPlotArea(90, 50, 255, 180, $perlchartdir::Transparent, -1, $perlchartdir::Transparent, 0xe0e0e0);

			my $title = $c->addTitle2(8, "Disease", "arial.ttf", 12);

			my $legendBox;
			my $labellayer;
			my $markLayer;
			my $layer;
			if($isComparative && $COMPPARMS{user_count}){
					$legendBox = $c->addLegend($c->getWidth() / 2, $title->getHeight()-7, "arial.ttf", 8);
					$legendBox->setBackground($perlchartdir::Transparent, $perlchartdir::Transparent);
					$legendBox->setAlignment($perlchartdir::TopCenter);
					$legendBox->setLineStyleKey();
				}

			# my $textbox = $c->yAxis()->setTitle("% of Participants");
			# $textbox->setFontStyle("arial.ttf");
			# $textbox->setFontSize(7);
			$c->yAxis()->setLabelFormat("{value}%");
			$c->yAxis()->setLinearScale(0,100,20);

			$c->xAxis()->setLabels($labels);
			$c->xAxis()->setLabelStyle("arialbd.ttf", 7, 0x000000, 45);
			$c->xAxis()->setTickLength(1);

				# Convert the labels on the x-axis to a CDMLTable
				my $table = $c->xAxis()->makeLabelTable();
				# Set the default top/bottom margins of the cells to 3 pixels
				$table->getStyle()->setMargin2(0, 0, 3, 3);
				# Use Arial Bold as the font for the first row
				$table->getRowStyle(0)->setFontStyle("arial.ttf");
				$table->getRowStyle(0)->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent);
				$table->appendRow()->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent);
				$table->appendRow()->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent);
				for(my $i = 0; $i < scalar(@$data); ++$i) {
					$table->setText($i, 2, $data->[$i].'%');
					}
				$table->insertCol(0)->setMargin2(5, 5, 3, 3);
				$table->setText(0, 0, "Conditions");
				$table->setText(0, 2, "% of Participants");
				$table->setText(0, 3, "# of Participants") if($show_numbers);

			if($isComparative && $COMPPARMS{user_count}){
				$labellayer = $c->addBarLayer($data, $perlchartdir::Transparent);   $labellayer->setBarGap($bargap);
				$labellayer->setBorderColor($perlchartdir::Transparent);
				# $labellayer->setAggregateLabelFormat("{value|1}%");
				#  $labellayer->setAggregateLabelStyle("arial.ttf", 7) ;

				$markLayer = $c->addBoxWhiskerLayer(undef, undef, undef, undef, $markdata, -1, 0x333333);
				$markLayer->setLineWidth(2);
				#  $markLayer->setDataGap(0.1);
				# Add the legend key for the mark line
				$legendBox->addKey("Comparative Group", 0x333333, 2);

				$layer = $c->addBarLayer3($data, $ten_colors);$layer->setBarGap($bargap);
				$layer->setBorderColor(0x000033);
				}
			else	{
				$layer = $c->addBarLayer3($data, $ten_colors, $labels);
				$layer->setBorderColor(0x000033);
				#  $layer->setAggregateLabelFormat("{value|1}%");
				# $layer->setAggregateLabelStyle("arial.ttf", 7) ;
				}

			$c->getDrawArea()->setPaletteMode($perlchartdir::ForcePalette);

			if( !$c->makeChart($o_file) )
				{
					copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
				}
			else	{
				$empty_chart{print_familyhistory} = 0;
				}
			}
			else {
				copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
			}

		}
#25 Glucose
	if (($input->{'pgraphs'} eq 'all' || $input->{'print_glucose'} == 1 || 2 == 1) &&
		($assessments_chk{GHA} || $assessments_chk{HRA} || $assessments_chk{OHA} || $assessments_chk{CRC} ))
	{
		++$graph_cnt;
 		print "$graph_cnt. Glucose<br>" unless $silent;
		##### Glucose Status
		my $o_file = $GGR_PAGE_DIR . $PARMS{'files_prefix'} . "_ggr_gluc.png";

		my ($gluc_basis, $gluc_high, $gluc_good, $gluc_med, $gluc_low, $gluc_unknown);
		my ($comp_gluc_basis, $comp_gluc_high, $comp_gluc_good, $comp_gluc_med, $comp_gluc_low, $comp_gluc_unknown);
		$comp_gluc_basis = $COMPPARMS{'GLUCOSE_high'} + $COMPPARMS{'GLUCOSE_good'} + $COMPPARMS{'GLUCOSE_med'} + $COMPPARMS{'GLUCOSE_low'} + $COMPPARMS{'GLUCOSE_unknown'};

		if(($gluc_basis = $PARMS{'GLUCOSE_high'} + $PARMS{'GLUCOSE_good'} + $PARMS{'GLUCOSE_med'} + $PARMS{'GLUCOSE_low'} + $PARMS{'GLUCOSE_unknown'}) && $PARMS{'GLUCOSE_high'} + $PARMS{'GLUCOSE_good'} + $PARMS{'GLUCOSE_med'} + $PARMS{'GLUCOSE_low'})
		{
			$gluc_high = sprintf("%.1f",($PARMS{'GLUCOSE_high'}/$gluc_basis*100));
			$gluc_good = sprintf("%.1f",($PARMS{'GLUCOSE_good'}/$gluc_basis*100));
			$gluc_med = sprintf("%.1f",($PARMS{'GLUCOSE_med'}/$gluc_basis*100));
			$gluc_low = sprintf("%.1f",($PARMS{'GLUCOSE_low'}/$gluc_basis*100));
			$gluc_unknown = sprintf("%.1f",($PARMS{'GLUCOSE_unknown'}/$gluc_basis*100));

			my %gluc_lab = (
				low	=> "Under\n" . GLUCOSE_LOW_MALE. " for males\n".GLUCOSE_LOW_FEMALE. " for females",
				good	=> "Above low\nand up to\n" . GLUCOSE_MARGINAL,
				med	=> "Above ".GLUCOSE_MARGINAL."\nand up\nto " . GLUCOSE_HIGH,
				high	=> "Over " . GLUCOSE_HIGH
				);

			if($isComparative && $comp_gluc_basis){
				$comp_gluc_high = sprintf("%.1f",($COMPPARMS{'GLUCOSE_high'}/$comp_gluc_basis*100));
				$comp_gluc_good = sprintf("%.1f",($COMPPARMS{'GLUCOSE_good'}/$comp_gluc_basis*100));
				$comp_gluc_med = sprintf("%.1f",($COMPPARMS{'GLUCOSE_med'}/$comp_gluc_basis*100));
				$comp_gluc_low = sprintf("%.1f",($COMPPARMS{'GLUCOSE_low'}/$comp_gluc_basis*100));
				$comp_gluc_unknown = sprintf("%.1f",($COMPPARMS{'GLUCOSE_unknown'}/$comp_gluc_basis*100));
				}

			my $markdata = [$comp_gluc_low ,$comp_gluc_good ,$comp_gluc_med ,$comp_gluc_high, $comp_gluc_unknown] if $isComparative;
			my $numbers = [$PARMS{'GLUCOSE_low'} , $PARMS{'GLUCOSE_good'}, $PARMS{'GLUCOSE_med'} , $PARMS{'GLUCOSE_high'}];
			push (@{$numbers}, $PARMS{'GLUCOSE_unknown'} ) if ($PARMS{'GLUCOSE_unknown'} > 0  || ($COMPPARMS{'GLUCOSE_unknown'} > 0 && $isComparative));
			my $data = [$gluc_low ,$gluc_good ,$gluc_med ,$gluc_high ];
			push (@{$data}, $gluc_unknown ) if ($gluc_unknown > 0  || ($comp_gluc_unknown > 0 && $isComparative));

			my $labels = [$gluc_lab{low}, $gluc_lab{good}, $gluc_lab{med}, $gluc_lab{high}];
			push (@{$labels},  "unknown" ) if ($gluc_unknown > 0  || ($comp_gluc_unknown > 0 && $isComparative));

			my $c = new XYChart($bar_chartwide, $bar_charthigh, 0xffffff);

			$c->setPlotArea(90, 50, 255, 165, $perlchartdir::Transparent, -1, $perlchartdir::Transparent, 0xe0e0e0);

			my $title = $c->addTitle2(8, "Glucose levels", "arial.ttf", 12);

			my $legendBox;
			my $labellayer;
			my $markLayer;
			my $layer;
			if($isComparative && $comp_gluc_basis){
					$legendBox = $c->addLegend($c->getWidth() / 2, $title->getHeight()-7, "arial.ttf", 8);
					$legendBox->setBackground($perlchartdir::Transparent, $perlchartdir::Transparent);
					$legendBox->setAlignment($perlchartdir::TopCenter);
					$legendBox->setLineStyleKey();
				}

			# my $textbox = $c->yAxis()->setTitle("% of Participants");
			# $textbox->setFontStyle("arial.ttf");
			# $textbox->setFontSize(7);
			$c->yAxis()->setLabelFormat("{value}%");
			$c->yAxis()->setLinearScale(0,100,20);

			$c->xAxis()->setLabels($labels);
			$c->xAxis()->setLabelStyle("arial.ttf", 7);
			$c->xAxis()->setTickLength(1);

				# Convert the labels on the x-axis to a CDMLTable
				my $table = $c->xAxis()->makeLabelTable();
				# Set the default top/bottom margins of the cells to 3 pixels
				$table->getStyle()->setMargin2(0, 0, 3, 3);
				# Use Arial Bold as the font for the first row
				$table->getRowStyle(0)->setFontStyle("arial.ttf");
				$table->getRowStyle(0)->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent);
				$table->appendRow()->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent);
				$table->appendRow()->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent);
				for(my $i = 0; $i < scalar(@$data); ++$i) {
					$table->setText($i, 2, $data->[$i].'%');
					}
				$table->appendRow()->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent) if($show_numbers);
				for(my $i = 0; $i < scalar(@$numbers); ++$i) {
					$table->setText($i, 3, $numbers->[$i]) if($show_numbers);
					}
				$table->insertCol(0)->setMargin2(5, 5, 3, 3);
				$table->setText(0, 0, "Levels");
				$table->setText(0, 2, "% of Participants");
				$table->setText(0, 3, "# of Participants") if($show_numbers);

			if($isComparative && $comp_gluc_basis){
				$labellayer = $c->addBarLayer($data, $perlchartdir::Transparent);   $labellayer->setBarGap($bargap);
				$labellayer->setBorderColor($perlchartdir::Transparent);
				# $labellayer->setAggregateLabelFormat("{value|1}%");
				#  $labellayer->setAggregateLabelStyle("arial.ttf", 7) ;

				$markLayer = $c->addBoxWhiskerLayer(undef, undef, undef, undef, $markdata, -1, 0x333333);
				$markLayer->setLineWidth(2);
				#  $markLayer->setDataGap(0.1);
				# Add the legend key for the mark line
				$legendBox->addKey("Comparative Group", 0x333333, 2);

				$layer = $c->addBarLayer3($data, $five_colors);$layer->setBarGap($bargap);
				$layer->setBorderColor(0x000033);
				}
			else	{
				$layer = $c->addBarLayer3($data, $five_colors, $labels);  $layer->setBarGap($bargap);
				$layer->setBorderColor(0x000033);
				#  $layer->setAggregateLabelFormat("{value|1}%");
				# $layer->setAggregateLabelStyle("arial.ttf", 7) ;
				}

			$c->getDrawArea()->setPaletteMode($perlchartdir::ForcePalette);

				if( !$c->makeChart($o_file) )
				{
					copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
				}
			else	{
				$empty_chart{print_glucose} = 0;
				}
		}
		else {
				copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
		}

	}
#26 LDL Levels
	if (($input->{'pgraphs'} eq 'all' || $input->{'print_ldl'} == 1) &&
		($assessments_chk{GHA} || $assessments_chk{HRA} || $assessments_chk{OHA} || $assessments_chk{CRC} ))
	{
		++$graph_cnt;
 		print "$graph_cnt. LDL<br>" unless $silent;
		##### Ldl Status
		my $o_file = $GGR_PAGE_DIR . $PARMS{'files_prefix'} . "_ggr_ldl.png";

		my ($ldl_basis, $ldl_high, $ldl_med, $ldl_low, $ldl_unknown);
		my ($comp_ldl_basis, $comp_ldl_high, $comp_ldl_med, $comp_ldl_low, $comp_ldl_unknown);
		$comp_ldl_basis = $COMPPARMS{'LDL_high'} + $COMPPARMS{'LDL_med'} + $COMPPARMS{'LDL_low'} + $COMPPARMS{'LDL_unknown'};

		if(($ldl_basis = $PARMS{'LDL_high'} + $PARMS{'LDL_med'} + $PARMS{'LDL_low'} + $PARMS{'LDL_unknown'}) && $PARMS{'LDL_high'} + $PARMS{'LDL_med'} + $PARMS{'LDL_low'})
		{
			$ldl_high = sprintf("%.1f",($PARMS{'LDL_high'}/$ldl_basis*100));
			$ldl_med = sprintf("%.1f",($PARMS{'LDL_med'}/$ldl_basis*100));
			$ldl_low = sprintf("%.1f",($PARMS{'LDL_low'}/$ldl_basis*100));
			$ldl_unknown = sprintf("%.1f",($PARMS{'LDL_unknown'}/$ldl_basis*100));


			my %ldl_lab = (
				low	=> "Under\n" . LDL_MARGINAL,
				med	=> LDL_MARGINAL . "\nto\n" . LDL_HIGH,
				high	=> "Over\n" . LDL_HIGH
				);

			if($isComparative && $comp_ldl_basis){
				$comp_ldl_high = sprintf("%.1f",($COMPPARMS{'LDL_high'}/$comp_ldl_basis*100));
				$comp_ldl_med = sprintf("%.1f",($COMPPARMS{'LDL_med'}/$comp_ldl_basis*100));
				$comp_ldl_low = sprintf("%.1f",($COMPPARMS{'LDL_low'}/$comp_ldl_basis*100));
				$comp_ldl_unknown = sprintf("%.1f",($COMPPARMS{'LDL_unknown'}/$comp_ldl_basis*100));
				}

			my $numbers = [$PARMS{'LDL_low'} ,$PARMS{'LDL_med'} ,$PARMS{'LDL_high'} ];
			push (@{$numbers}, $PARMS{'LDL_unknown'}) if ($PARMS{'LDL_unknown'} > 0 || ($COMPPARMS{'LDL_unknown'} > 0 && $isComparative));
			my $data = [$ldl_low ,$ldl_med ,$ldl_high ];
			push (@{$data}, $ldl_unknown) if ($ldl_unknown > 0 || ($COMPPARMS{'LDL_unknown'} > 0 && $isComparative));
			my $markdata = [$comp_ldl_low ,$comp_ldl_med ,$comp_ldl_high, $comp_ldl_unknown] if $isComparative;

			my $labels = [$ldl_lab{low}, $ldl_lab{med}, $ldl_lab{high} ];
			push (@{$labels}, "unknown") if ($ldl_unknown > 0 || ($COMPPARMS{'LDL_unknown'} > 0 && $isComparative));

			my $c = new XYChart($bar_chartwide, $bar_charthigh, 0xffffff);

			$c->setPlotArea(90, 50, 255, 180, $perlchartdir::Transparent, -1, $perlchartdir::Transparent, 0xe0e0e0);

			my $title = $c->addTitle2(8, "LDL levels", "arial.ttf", 12);

			my $legendBox;
			my $labellayer;
			my $markLayer;
			my $layer;
			if($isComparative && $comp_ldl_basis){
					$legendBox = $c->addLegend($c->getWidth() / 2, $title->getHeight()-7, "arial.ttf", 8);
					$legendBox->setBackground($perlchartdir::Transparent, $perlchartdir::Transparent);
					$legendBox->setAlignment($perlchartdir::TopCenter);
					$legendBox->setLineStyleKey();
				}

			# my $textbox = $c->yAxis()->setTitle("% of Participants");
			# $textbox->setFontStyle("arial.ttf");
			# $textbox->setFontSize(7);
			$c->yAxis()->setLabelFormat("{value}%");
			$c->yAxis()->setLinearScale(0,100,20);

			$c->xAxis()->setLabels($labels);
			$c->xAxis()->setLabelStyle("arial.ttf", 7);
			$c->xAxis()->setTickLength(1);

				# Convert the labels on the x-axis to a CDMLTable
				my $table = $c->xAxis()->makeLabelTable();
				# Set the default top/bottom margins of the cells to 3 pixels
				$table->getStyle()->setMargin2(0, 0, 3, 3);
				# Use Arial Bold as the font for the first row
				$table->getRowStyle(0)->setFontStyle("arial.ttf");
				$table->getRowStyle(0)->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent);
				$table->appendRow()->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent);
				$table->appendRow()->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent);
				for(my $i = 0; $i < scalar(@$data); ++$i) {
					$table->setText($i, 2, $data->[$i].'%');
					}
				$table->appendRow()->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent) if($show_numbers);
				for(my $i = 0; $i < scalar(@$numbers); ++$i) {
					$table->setText($i, 3, $numbers->[$i]) if($show_numbers);
					}
				$table->insertCol(0)->setMargin2(5, 5, 3, 3);
				$table->setText(0, 0, "Levels");
				$table->setText(0, 2, "% of Participants");
				$table->setText(0, 3, "# of Participants") if($show_numbers);

			if($isComparative && $comp_ldl_basis){
				$labellayer = $c->addBarLayer($data, $perlchartdir::Transparent);   $labellayer->setBarGap($bargap);
				$labellayer->setBorderColor($perlchartdir::Transparent);
				# $labellayer->setAggregateLabelFormat("{value|1}%");
				#  $labellayer->setAggregateLabelStyle("arial.ttf", 7) ;

				$markLayer = $c->addBoxWhiskerLayer(undef, undef, undef, undef, $markdata, -1, 0x333333);
				$markLayer->setLineWidth(2);
				#  $markLayer->setDataGap(0.1);
				# Add the legend key for the mark line
				$legendBox->addKey("Comparative Group", 0x333333, 2);

				$layer = $c->addBarLayer3($data, $five_colors);$layer->setBarGap($bargap);
				$layer->setBorderColor(0x000033);
				}
			else	{
				$layer = $c->addBarLayer3($data, $five_colors, $labels);  $layer->setBarGap($bargap);
				$layer->setBorderColor(0x000033);
				#  $layer->setAggregateLabelFormat("{value|1}%");
				# $layer->setAggregateLabelStyle("arial.ttf", 7) ;
				}

			$c->getDrawArea()->setPaletteMode($perlchartdir::ForcePalette);

				if( !$c->makeChart($o_file) )
				{
					copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
				}
			else	{
				$empty_chart{print_ldl} = 0;
				}
		}
		else {
				copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
		}

	}
#27  Triglycerides
	if (($input->{'pgraphs'} eq 'all' || $input->{'print_triglycerides'} == 1) &&($assessments_chk{GHA} || $assessments_chk{HRA} || $assessments_chk{CRC} || $assessments_chk{OHA} ))
	{
		++$graph_cnt;
 		print "$graph_cnt. Triglycerides<br>" unless $silent;
		my $o_file = $GGR_PAGE_DIR . $PARMS{'files_prefix'} . "_ggr_trig.png";

		my ($tri_basis, $tri_above500, $tri_200_499, $tri_150_199, $tri_below150, $tri_unknown);
		my ($comp_tri_basis, $comp_tri_above500, $comp_tri_200_499, $comp_tri_150_199, $comp_tri_below150, $comp_tri_unknown);
		$comp_tri_basis = $COMPPARMS{'TRI_above500'} + $COMPPARMS{'TRI_200_499'} + $COMPPARMS{'TRI_150_199'} + $COMPPARMS{'TRI_below150'} + $COMPPARMS{'TRI_unknown'};

		if(($tri_basis = $PARMS{'TRI_above500'} + $PARMS{'TRI_200_499'} + $PARMS{'TRI_150_199'} + $PARMS{'TRI_below150'} + $PARMS{'TRI_unknown'}) && $PARMS{'TRI_above500'} + $PARMS{'TRI_200_499'} + $PARMS{'TRI_150_199'} + $PARMS{'TRI_below150'})
		{
			$tri_above500 = sprintf("%.1f",($PARMS{'TRI_above500'}/$tri_basis*100));
			$tri_200_499 = sprintf("%.1f",($PARMS{'TRI_200_499'}/$tri_basis*100));
			$tri_150_199 = sprintf("%.1f",($PARMS{'TRI_150_199'}/$tri_basis*100));
			$tri_below150 = sprintf("%.1f",($PARMS{'TRI_below150'}/$tri_basis*100));
			$tri_unknown = sprintf("%.1f",($PARMS{'TRI_unknown'}/$tri_basis*100));


			if($isComparative && $comp_tri_basis){
				$comp_tri_above500 = sprintf("%.1f",($COMPPARMS{'TRI_above500'}/$comp_tri_basis*100));
				$comp_tri_200_499 = sprintf("%.1f",($COMPPARMS{'TRI_200_499'}/$comp_tri_basis*100));
				$comp_tri_150_199 = sprintf("%.1f",($COMPPARMS{'TRI_150_199'}/$comp_tri_basis*100));
				$comp_tri_below150 = sprintf("%.1f",($COMPPARMS{'TRI_below150'}/$comp_tri_basis*100));
				$comp_tri_unknown = sprintf("%.1f",($COMPPARMS{'TRI_unknown'}/$comp_tri_basis*100));
				}

			my $markdata = [$comp_tri_below150, $comp_tri_150_199, $comp_tri_200_499, $comp_tri_above500, $comp_tri_unknown] if $isComparative;
			my $numbers = [ $PARMS{'TRI_below150'}, $PARMS{'TRI_150_199'}, $PARMS{'TRI_200_499'}, $PARMS{'TRI_above500'} ];
			push (@{$numbers},$PARMS{'TRI_unknown'}) if ($PARMS{'TRI_unknown'} > 0 || ($COMPPARMS{'TRI_unknown'} > 0 && $isComparative));
			my $data = [$tri_below150, $tri_150_199, $tri_200_499, $tri_above500];
			push (@{$data}, $tri_unknown) if ($tri_unknown > 0 || ($COMPPARMS{'TRI_unknown'} > 0 && $isComparative));

			my $labels = ["below\n150", "150\nto\n199", "200\nto\n499", "above\n500"];
			push(@{$labels}, "unknown") if ($tri_unknown > 0 || ($COMPPARMS{'TRI_unknown'} > 0 && $isComparative));

			my $c = new XYChart($bar_chartwide, $bar_charthigh, 0xffffff);

			$c->setPlotArea(90, 50, 255, 180, $perlchartdir::Transparent, -1, $perlchartdir::Transparent, 0xe0e0e0);

			my $title = $c->addTitle2(8, "Triglycerides levels", "arial.ttf", 12);

			my $legendBox;
			my $labellayer;
			my $markLayer;
			my $layer;
			if($isComparative && $comp_tri_basis){
					$legendBox = $c->addLegend($c->getWidth() / 2, $title->getHeight()-7, "arial.ttf", 8);
					$legendBox->setBackground($perlchartdir::Transparent, $perlchartdir::Transparent);
					$legendBox->setAlignment($perlchartdir::TopCenter);
					$legendBox->setLineStyleKey();
				}

			# my $textbox = $c->yAxis()->setTitle("% of Participants");
			# $textbox->setFontStyle("arial.ttf");
			# $textbox->setFontSize(7);
			$c->yAxis()->setLabelFormat("{value}%");
			$c->yAxis()->setLinearScale(0,100,20);

			$c->xAxis()->setLabels($labels);
			$c->xAxis()->setLabelStyle("arial.ttf", 7);
			$c->xAxis()->setTickLength(1);

				# Convert the labels on the x-axis to a CDMLTable
				my $table = $c->xAxis()->makeLabelTable();
				# Set the default top/bottom margins of the cells to 3 pixels
				$table->getStyle()->setMargin2(0, 0, 3, 3);
				# Use Arial Bold as the font for the first row
				$table->getRowStyle(0)->setFontStyle("arial.ttf");
				$table->getRowStyle(0)->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent);
				$table->appendRow()->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent);
				$table->appendRow()->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent);
				for(my $i = 0; $i < scalar(@$data); ++$i) {
					$table->setText($i, 2, $data->[$i].'%');
					}
				$table->appendRow()->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent) if($show_numbers);
				for(my $i = 0; $i < scalar(@$numbers); ++$i) {
					$table->setText($i, 3, $numbers->[$i]) if($show_numbers);
					}
				$table->insertCol(0)->setMargin2(5, 5, 3, 3);
				$table->setText(0, 0, "Levels");
				$table->setText(0, 2, "% of Participants");
				$table->setText(0, 3, "# of Participants") if($show_numbers);

			if($isComparative && $comp_tri_basis){
				$labellayer = $c->addBarLayer($data, $perlchartdir::Transparent);   $labellayer->setBarGap($bargap);
				$labellayer->setBorderColor($perlchartdir::Transparent);
				# $labellayer->setAggregateLabelFormat("{value|1}%");
				#  $labellayer->setAggregateLabelStyle("arial.ttf", 7) ;

				$markLayer = $c->addBoxWhiskerLayer(undef, undef, undef, undef, $markdata, -1, 0x333333);
				$markLayer->setLineWidth(2);
				#  $markLayer->setDataGap(0.1);
				# Add the legend key for the mark line
				$legendBox->addKey("Comparative Group", 0x333333, 2);

				$layer = $c->addBarLayer3($data, $five_colors);$layer->setBarGap($bargap);
				$layer->setBorderColor(0x000033);
				}
			else	{
				$layer = $c->addBarLayer3($data, $five_colors, $labels);  $layer->setBarGap($bargap);
				$layer->setBorderColor(0x000033);
				#  $layer->setAggregateLabelFormat("{value|1}%");
				# $layer->setAggregateLabelStyle("arial.ttf", 7) ;
				}

			$c->getDrawArea()->setPaletteMode($perlchartdir::ForcePalette);

				if( !$c->makeChart($o_file) )
				{
					copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
				}
			else	{
				$empty_chart{print_triglycerides} = 0;
				}
		}
		else {
				copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
		}

	}
#28 Days Missed
	if (($input->{'pgraphs'} eq 'all' || $input->{'print_days_missed'} == 1) &&($assessments_chk{GHA} || $assessments_chk{HRA} || $assessments_chk{CRC} || $assessments_chk{OHA} ))
	{
		++$graph_cnt;
 		print "$graph_cnt. Days missed<br>" unless $silent;
		##### Days_missed Status
		my $o_file = $GGR_PAGE_DIR . $PARMS{'files_prefix'} . "_ggr_days.png";

		my ($days_missed_basis, $days_missed_none, $days_missed_1to5, $days_missed_6to10, $days_missed_10plus, $days_missed_not_apply);
		my ($comp_days_missed_basis, $comp_days_missed_none, $comp_days_missed_1to5, $comp_days_missed_6to10, $comp_days_missed_10plus, $comp_days_missed_not_apply);
		$comp_days_missed_basis = $COMPPARMS{'days_missed_none'} + $COMPPARMS{'days_missed_1to5'} + $COMPPARMS{'days_missed_6to10'} + $COMPPARMS{'days_missed_10plus'} + $COMPPARMS{'days_missed_not_apply'};

		if($days_missed_basis = $PARMS{'days_missed_none'} + $PARMS{'days_missed_1to5'} + $PARMS{'days_missed_6to10'} + $PARMS{'days_missed_10plus'} + $PARMS{'days_missed_not_apply'})
		{
			$days_missed_none = sprintf("%.1f",($PARMS{'days_missed_none'}/$days_missed_basis*100));
			$days_missed_1to5 = sprintf("%.1f",($PARMS{'days_missed_1to5'}/$days_missed_basis*100));
			$days_missed_6to10 = sprintf("%.1f",($PARMS{'days_missed_6to10'}/$days_missed_basis*100));
			$days_missed_10plus = sprintf("%.1f",($PARMS{'days_missed_10plus'}/$days_missed_basis*100));
			$days_missed_not_apply = sprintf("%.1f",($PARMS{'days_missed_not_apply'}/$days_missed_basis*100));


			if($isComparative && $comp_days_missed_basis){
				$comp_days_missed_none = sprintf("%.1f",($COMPPARMS{'days_missed_none'}/$comp_days_missed_basis*100));
				$comp_days_missed_1to5 = sprintf("%.1f",($COMPPARMS{'days_missed_1to5'}/$comp_days_missed_basis*100));
				$comp_days_missed_6to10 = sprintf("%.1f",($COMPPARMS{'days_missed_6to10'}/$comp_days_missed_basis*100));
				$comp_days_missed_10plus = sprintf("%.1f",($COMPPARMS{'days_missed_10plus'}/$comp_days_missed_basis*100));
				$comp_days_missed_not_apply = sprintf("%.1f",($COMPPARMS{'days_missed_not_apply'}/$comp_days_missed_basis*100));
				}

			my $markdata = [$comp_days_missed_none, $comp_days_missed_1to5, $comp_days_missed_6to10, $comp_days_missed_10plus, $comp_days_missed_not_apply] if $isComparative;
			my $numbers = [ $PARMS{'days_missed_none'}, $PARMS{'days_missed_1to5'}, $PARMS{'days_missed_6to10'}, $PARMS{'days_missed_10plus'}, $PARMS{'days_missed_not_apply'} ];
			my $data = [$days_missed_none, $days_missed_1to5, $days_missed_6to10, $days_missed_10plus, $days_missed_not_apply];

			my $labels = ['None', '1-5\ndays', '6-10\ndays', '10 days\nor more', 'Did not\napply'];

			my $c = new XYChart($bar_chartwide, $bar_charthigh, 0xffffff);

			$c->setPlotArea(90, 50, 255, 180, $perlchartdir::Transparent, -1, $perlchartdir::Transparent, 0xe0e0e0);

			my $title = $c->addTitle2(8, "Days missed", "arial.ttf", 12);

			my $legendBox;
			my $labellayer;
			my $markLayer;
			my $layer;
			if($isComparative && $comp_days_missed_basis){
					$legendBox = $c->addLegend($c->getWidth() / 2, $title->getHeight()-7, "arial.ttf", 8);
					$legendBox->setBackground($perlchartdir::Transparent, $perlchartdir::Transparent);
					$legendBox->setAlignment($perlchartdir::TopCenter);
					$legendBox->setLineStyleKey();
				}

			# my $textbox = $c->yAxis()->setTitle("% of Participants");
			# $textbox->setFontStyle("arial.ttf");
			# $textbox->setFontSize(7);
			$c->yAxis()->setLabelFormat("{value}%");
			$c->yAxis()->setLinearScale(0,100,20);

			$c->xAxis()->setLabels($labels);
			$c->xAxis()->setLabelStyle("arial.ttf", 7);
			$c->xAxis()->setTickLength(1);

				# Convert the labels on the x-axis to a CDMLTable
				my $table = $c->xAxis()->makeLabelTable();
				# Set the default top/bottom margins of the cells to 3 pixels
				$table->getStyle()->setMargin2(0, 0, 3, 3);
				# Use Arial Bold as the font for the first row
				$table->getRowStyle(0)->setFontStyle("arial.ttf");
				$table->getRowStyle(0)->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent);
				$table->appendRow()->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent);
				$table->appendRow()->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent);
				for(my $i = 0; $i < scalar(@$data); ++$i) {
					$table->setText($i, 2, $data->[$i].'%');
					}
				$table->appendRow()->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent) if($show_numbers);
				for(my $i = 0; $i < scalar(@$numbers); ++$i) {
					$table->setText($i, 3, $numbers->[$i]) if($show_numbers);
					}
				$table->insertCol(0)->setMargin2(5, 5, 3, 3);
				$table->setText(0, 0, "Days Missed");
				$table->setText(0, 2, "% of Participants");
				$table->setText(0, 3, "# of Participants") if($show_numbers);

			if($isComparative && $comp_days_missed_basis){
				$labellayer = $c->addBarLayer($data, $perlchartdir::Transparent);   $labellayer->setBarGap($bargap);
				$labellayer->setBorderColor($perlchartdir::Transparent);
				# $labellayer->setAggregateLabelFormat("{value|1}%");
				#  $labellayer->setAggregateLabelStyle("arial.ttf", 7) ;

				$markLayer = $c->addBoxWhiskerLayer(undef, undef, undef, undef, $markdata, -1, 0x333333);
				$markLayer->setLineWidth(2);
				#  $markLayer->setDataGap(0.1);
				# Add the legend key for the mark line
				$legendBox->addKey("Comparative Group", 0x333333, 2);

				$layer = $c->addBarLayer3($data, $five_colors);$layer->setBarGap($bargap);
				$layer->setBorderColor(0x000033);
				}
			else	{
				$layer = $c->addBarLayer3($data, $five_colors, $labels);  $layer->setBarGap($bargap);
				$layer->setBorderColor(0x000033);
				#  $layer->setAggregateLabelFormat("{value|1}%");
				# $layer->setAggregateLabelStyle("arial.ttf", 7) ;
				}

			$c->getDrawArea()->setPaletteMode($perlchartdir::ForcePalette);

				if( !$c->makeChart($o_file) )
				{
					copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
				}
			else	{
				$empty_chart{print_days_missed} = 0;
				}
		}
		else {
				copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
		}

	}
#29  Colon Exam
	if (($input->{'pgraphs'} eq 'all' || $input->{'print_colon_exam'} == 1) &&($assessments_chk{GHA} || $assessments_chk{HRA} || $assessments_chk{CRC} || $assessments_chk{OHA} ))
	{
		++$graph_cnt;
 		print "$graph_cnt. Colon exam<br>" unless $silent;
		##### Colon Exam
		my $o_file = $GGR_PAGE_DIR . $PARMS{'files_prefix'} . "_ggr_colon.png";

		my ($colon_basis, $colonoscopy_good, $colonoscopy_med, $colonoscopy_bad);
		my ($comp_colon_basis, $colonoscopy_good, $comp_colonoscopy_med, $comp_colonoscopy_bad);
		$comp_colon_basis = $COMPPARMS{'colonoscopy_good'} + $COMPPARMS{'colonoscopy_med'} + $COMPPARMS{'colonoscopy_bad'};

		if($colon_basis = $PARMS{'colonoscopy_good'} + $PARMS{'colonoscopy_med'} + $PARMS{'colonoscopy_bad'})
		{
			$colonoscopy_good = sprintf("%.1f",($PARMS{'colonoscopy_good'}/$colon_basis*100));
			$colonoscopy_med = sprintf("%.1f",($PARMS{'colonoscopy_med'}/$colon_basis*100));
			$colonoscopy_bad = sprintf("%.1f",($PARMS{'colonoscopy_bad'}/$colon_basis*100));

			if($isComparative && $comp_colon_basis){
				$comp_colonoscopy_good = sprintf("%.1f",($COMPPARMS{'colonoscopy_good'}/$comp_colon_basis*100));
				$comp_colonoscopy_med = sprintf("%.1f",($COMPPARMS{'colonoscopy_med'}/$comp_colon_basis*100));
				$comp_colonoscopy_bad = sprintf("%.1f",($COMPPARMS{'colonoscopy_bad'}/$comp_colon_basis*100));
				}

			my $markdata = [$comp_colonoscopy_good, $comp_colonoscopy_med, $comp_colonoscopy_bad] if $isComparative;
			my $numbers = [ $PARMS{'colonoscopy_good'}, $PARMS{'colonoscopy_med'}, $PARMS{'colonoscopy_bad'} ];
			my $data = [$colonoscopy_good, $colonoscopy_med, $colonoscopy_bad];

			my $labels = ["1 year\nor less", "1 to 3\nyears", "Over 3\nyears"];

			my $c = new XYChart($bar_chartwide, $bar_charthigh, 0xffffff);

			$c->setPlotArea(90, 50, 255, 180, $perlchartdir::Transparent, -1, $perlchartdir::Transparent, 0xe0e0e0);

			my $title = $c->addTitle2(8, "Time since last colon exam", "arial.ttf", 12);

			my $legendBox;
			my $labellayer;
			my $markLayer;
			my $layer;
			if($isComparative && $comp_colon_basis){
					$legendBox = $c->addLegend($c->getWidth() / 2, $title->getHeight()-7, "arial.ttf", 8);
					$legendBox->setBackground($perlchartdir::Transparent, $perlchartdir::Transparent);
					$legendBox->setAlignment($perlchartdir::TopCenter);
					$legendBox->setLineStyleKey();
				}

			# my $textbox = $c->yAxis()->setTitle("% of Participants");
			# $textbox->setFontStyle("arial.ttf");
			# $textbox->setFontSize(7);
			$c->yAxis()->setLabelFormat("{value}%");
			$c->yAxis()->setLinearScale(0,100,20);

			$c->xAxis()->setLabels($labels);
			$c->xAxis()->setLabelStyle("arial.ttf", 7);
			$c->xAxis()->setTickLength(1);

				# Convert the labels on the x-axis to a CDMLTable
				my $table = $c->xAxis()->makeLabelTable();
				# Set the default top/bottom margins of the cells to 3 pixels
				$table->getStyle()->setMargin2(0, 0, 3, 3);
				# Use Arial Bold as the font for the first row
				$table->getRowStyle(0)->setFontStyle("arial.ttf");
				$table->getRowStyle(0)->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent);
				$table->appendRow()->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent);
				$table->appendRow()->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent);
				for(my $i = 0; $i < scalar(@$data); ++$i) {
					$table->setText($i, 2, $data->[$i].'%');
					}
				$table->appendRow()->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent) if($show_numbers);
				for(my $i = 0; $i < scalar(@$numbers); ++$i) {
					$table->setText($i, 3, $numbers->[$i]) if($show_numbers);
					}
				$table->insertCol(0)->setMargin2(5, 5, 3, 3);
				$table->setText(0, 0, "Last Exam");
				$table->setText(0, 2, "% of Participants");
				$table->setText(0, 3, "# of Participants") if($show_numbers);

			if($isComparative && $comp_colon_basis){
				$labellayer = $c->addBarLayer($data, $perlchartdir::Transparent);   $labellayer->setBarGap($bargap);
				$labellayer->setBorderColor($perlchartdir::Transparent);
				# $labellayer->setAggregateLabelFormat("{value|1}%");
				#  $labellayer->setAggregateLabelStyle("arial.ttf", 7) ;

				$markLayer = $c->addBoxWhiskerLayer(undef, undef, undef, undef, $markdata, -1, 0x333333);
				$markLayer->setLineWidth(2);
				#  $markLayer->setDataGap(0.1);
				# Add the legend key for the mark line
				$legendBox->addKey("Comparative Group", 0x333333, 2);

				$layer = $c->addBarLayer3($data, $five_colors);$layer->setBarGap($bargap);
				$layer->setBorderColor(0x000033);
				}
			else	{
				$layer = $c->addBarLayer3($data, $five_colors, $labels);  $layer->setBarGap($bargap);
				$layer->setBorderColor(0x000033);
				#  $layer->setAggregateLabelFormat("{value|1}%");
				# $layer->setAggregateLabelStyle("arial.ttf", 7) ;
				}

			$c->getDrawArea()->setPaletteMode($perlchartdir::ForcePalette);

				if( !$c->makeChart($o_file) )
				{
					copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
				}
			else	{
				$empty_chart{print_colon_exam} = 0;
				}
		}
		else {
				copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
		}

	}
#30 HGa1C - Hemoglobin
	if (($input->{'pgraphs'} eq 'all' || $input->{'print_hga1c'} == 1) &&
		($assessments_chk{GHA} || $assessments_chk{HRA} || $assessments_chk{CRC} || $assessments_chk{OHA} ))
	{
		++$graph_cnt;
 		print "$graph_cnt. HgA1c<br>" unless $silent;
		##### HgA1c Status
		my $o_file = $GGR_PAGE_DIR . $PARMS{'files_prefix'} . "_ggr_hga1c.png";

		my ($hga1c_basis, $hga1c_high, $hga1c_med, $hga1c_low, $hga1c_unknown);
		my ($comp_hga1c_basis, $comp_hga1c_high, $comp_hga1c_med, $comp_hga1c_low, $comp_hga1c_unknown);
		$comp_hga1c_basis = $COMPPARMS{'hga1c_high'} + $COMPPARMS{'hga1c_med'} + $COMPPARMS{'hga1c_low'} + $COMPPARMS{'hga1c_unknown'};

		if(($hga1c_basis = $PARMS{'hga1c_high'} + $PARMS{'hga1c_med'} + $PARMS{'hga1c_low'} + $PARMS{'hga1c_unknown'}) &&  $PARMS{'hga1c_high'} + $PARMS{'hga1c_med'} + $PARMS{'hga1c_low'} )
		{
			$hga1c_high = sprintf("%.1f",($PARMS{'hga1c_high'}/$hga1c_basis*100));
			$hga1c_med = sprintf("%.1f",($PARMS{'hga1c_med'}/$hga1c_basis*100));
			$hga1c_low = sprintf("%.1f",($PARMS{'hga1c_low'}/$hga1c_basis*100));
			$hga1c_unknown = sprintf("%.1f",($PARMS{'hga1c_unknown'}/$hga1c_basis*100));

			my %hga1c_lab = (
				low	=> "Under\n" . HGA1C_MARGINAL,
				med	=> HGA1C_MARGINAL . "\nto\n" . HGA1C_HIGH,
				high	=> "Over\n" . HGA1C_HIGH
				);

			if($isComparative && $comp_hga1c_basis){
				$comp_hga1c_high = sprintf("%.1f",($COMPPARMS{'hga1c_high'}/$comp_hga1c_basis*100));
				$comp_hga1c_med = sprintf("%.1f",($COMPPARMS{'hga1c_med'}/$comp_hga1c_basis*100));
				$comp_hga1c_low = sprintf("%.1f",($COMPPARMS{'hga1c_low'}/$comp_hga1c_basis*100));
				$comp_hga1c_unknown = sprintf("%.1f",($COMPPARMS{'hga1c_unknown'}/$comp_hga1c_basis*100));
				}

			my $markdata = [$comp_hga1c_low ,$comp_hga1c_med ,$comp_hga1c_high, $comp_hga1c_unknown] if $isComparative;
			my $numbers = [ $PARMS{'hga1c_low'}, $PARMS{'hga1c_med'}, $PARMS{'hga1c_high'} ];
			push (@{$numbers}, $PARMS{'hga1c_unknown'}) if ( $PARMS{'hga1c_unknown'} > 0 || ($COMPPARMS{'hga1c_unknown'} > 0 &&  $isComparative));
			my $data = [$hga1c_low ,$hga1c_med ,$hga1c_high ];
			push (@{$data}, $hga1c_unknown) if ($hga1c_unknown > 0 || ($COMPPARMS{'hga1c_unknown'} > 0 &&  $isComparative));

			my $labels = [$hga1c_lab{low}, $hga1c_lab{med}, $hga1c_lab{high} ];
			push (@{$labels}, "unknown") if ($hga1c_unknown > 0 || ($COMPPARMS{'hga1c_unknown'} > 0 &&  $isComparative));

			my $c = new XYChart($bar_chartwide, $bar_charthigh, 0xffffff);

			$c->setPlotArea(90, 50, 255, 180, $perlchartdir::Transparent, -1, $perlchartdir::Transparent, 0xe0e0e0);

			my $title = $c->addTitle2(8, "Hemoglobin A1c levels", "arial.ttf", 12);

			my $legendBox;
			my $labellayer;
			my $markLayer;
			my $layer;
			if($isComparative && $comp_hga1c_basis){
					$legendBox = $c->addLegend($c->getWidth() / 2, $title->getHeight()-7, "arial.ttf", 8);
					$legendBox->setBackground($perlchartdir::Transparent, $perlchartdir::Transparent);
					$legendBox->setAlignment($perlchartdir::TopCenter);
					$legendBox->setLineStyleKey();
				}

			# my $textbox = $c->yAxis()->setTitle("% of Participants");
			# $textbox->setFontStyle("arial.ttf");
			# $textbox->setFontSize(7);
			$c->yAxis()->setLabelFormat("{value}%");
			$c->yAxis()->setLinearScale(0,100,20);

			$c->xAxis()->setLabels($labels);
			$c->xAxis()->setLabelStyle("arial.ttf", 7);
			$c->xAxis()->setTickLength(1);

				# Convert the labels on the x-axis to a CDMLTable
				my $table = $c->xAxis()->makeLabelTable();
				# Set the default top/bottom margins of the cells to 3 pixels
				$table->getStyle()->setMargin2(0, 0, 3, 3);
				# Use Arial Bold as the font for the first row
				$table->getRowStyle(0)->setFontStyle("arial.ttf");
				$table->getRowStyle(0)->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent);
				$table->appendRow()->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent);
				$table->appendRow()->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent);
				for(my $i = 0; $i < scalar(@$data); ++$i) {
					$table->setText($i, 2, $data->[$i].'%');
					}
				$table->appendRow()->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent) if($show_numbers);
				for(my $i = 0; $i < scalar(@$numbers); ++$i) {
					$table->setText($i, 3, $numbers->[$i]) if($show_numbers);
					}
				$table->insertCol(0)->setMargin2(5, 5, 3, 3);
				$table->setText(0, 0, "Levels");
				$table->setText(0, 2, "% of Participants");
				$table->setText(0, 3, "# of Participants") if($show_numbers);

			if($isComparative && $comp_hga1c_basis){
				$labellayer = $c->addBarLayer($data, $perlchartdir::Transparent);   $labellayer->setBarGap($bargap);
				$labellayer->setBorderColor($perlchartdir::Transparent);
				# $labellayer->setAggregateLabelFormat("{value|1}%");
				#  $labellayer->setAggregateLabelStyle("arial.ttf", 7) ;

				$markLayer = $c->addBoxWhiskerLayer(undef, undef, undef, undef, $markdata, -1, 0x333333);
				$markLayer->setLineWidth(2);
				#  $markLayer->setDataGap(0.1);
				# Add the legend key for the mark line
				$legendBox->addKey("Comparative Group", 0x333333, 2);

				$layer = $c->addBarLayer3($data, $five_colors);$layer->setBarGap($bargap);
				$layer->setBorderColor(0x000033);
				}
			else	{
				$layer = $c->addBarLayer3($data, $five_colors, $labels);  $layer->setBarGap($bargap);
				$layer->setBorderColor(0x000033);
				#  $layer->setAggregateLabelFormat("{value|1}%");
				# $layer->setAggregateLabelStyle("arial.ttf", 7) ;
				}

			$c->getDrawArea()->setPaletteMode($perlchartdir::ForcePalette);

				if( !$c->makeChart($o_file) )
				{
					copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
				}
			else	{
				$empty_chart{print_hga1c} = 0;
				}
		}
		else {
				copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
		}

	}
#31 General Exam
	if (($input->{'pgraphs'} eq 'all' || $input->{'print_general_exam'} == 1) &&($assessments_chk{GHA} || $assessments_chk{HRA} || $assessments_chk{CRC} || $assessments_chk{OHA} ))
	{
		++$graph_cnt;
 		print "$graph_cnt. General exam<br>" unless $silent;
		##### Ldl Status
		my $o_file = $GGR_PAGE_DIR . $PARMS{'files_prefix'} . "_ggr_general.png";

		my ($gen_basis, $gen_exam_under2, $gen_exam_2to5, $gen_exam_5plus, $gen_exam_never);
		my ($comp_gen_basis, $comp_gen_exam_under2, $comp_gen_exam_2to5, $comp_gen_exam_5plus, $comp_gen_exam_never);
		$comp_gen_basis = $COMPPARMS{'gen_exam_under2'} + $COMPPARMS{'gen_exam_2to5'} + $COMPPARMS{'gen_exam_5plus'} + $COMPPARMS{'gen_exam_never'};

		if($gen_basis = $PARMS{'gen_exam_under2'} + $PARMS{'gen_exam_2to5'} + $PARMS{'gen_exam_5plus'} + $PARMS{'gen_exam_never'})
		{
			$gen_exam_under2 = sprintf("%.1f",($PARMS{'gen_exam_under2'}/$gen_basis*100));
			$gen_exam_2to5 = sprintf("%.1f",($PARMS{'gen_exam_2to5'}/$gen_basis*100));
			$gen_exam_5plus = sprintf("%.1f",($PARMS{'gen_exam_5plus'}/$gen_basis*100));
			$gen_exam_never = sprintf("%.1f",($PARMS{'gen_exam_never'}/$gen_basis*100));

			if($isComparative && $comp_gen_basis){
				$comp_gen_exam_under2 = sprintf("%.1f",($COMPPARMS{'gen_exam_under2'}/$comp_gen_basis*100));
				$comp_gen_exam_2to5 = sprintf("%.1f",($COMPPARMS{'gen_exam_2to5'}/$comp_gen_basis*100));
				$comp_gen_exam_5plus = sprintf("%.1f",($COMPPARMS{'gen_exam_5plus'}/$comp_gen_basis*100));
				$comp_gen_exam_never = sprintf("%.1f",($COMPPARMS{'gen_exam_never'}/$comp_gen_basis*100));
				}

			my $markdata = [$comp_gen_exam_under2, $comp_gen_exam_2to5, $comp_gen_exam_5plus, $comp_gen_exam_never] if $isComparative;
			my $numbers = [ $PARMS{'gen_exam_under2'}, $PARMS{'gen_exam_2to5'}, $PARMS{'gen_exam_5plus'}, $PARMS{'gen_exam_never'} ];
			my $data = [$gen_exam_under2, $gen_exam_2to5, $gen_exam_5plus, $gen_exam_never];

			my $labels = ["2 years\nor less", "2 to 5\nyears", "Over 5\n years", "Never"];

			my $c = new XYChart($bar_chartwide, $bar_charthigh, 0xffffff);

			$c->setPlotArea(90, 50, 255, 180, $perlchartdir::Transparent, -1, $perlchartdir::Transparent, 0xe0e0e0);

			my $title = $c->addTitle2(8, "Time since last general exam", "arial.ttf", 12);

			my $legendBox;
			my $labellayer;
			my $markLayer;
			my $layer;
			if($isComparative && $comp_gen_basis){
					$legendBox = $c->addLegend($c->getWidth() / 2, $title->getHeight()-7, "arial.ttf", 8);
					$legendBox->setBackground($perlchartdir::Transparent, $perlchartdir::Transparent);
					$legendBox->setAlignment($perlchartdir::TopCenter);
					$legendBox->setLineStyleKey();
				}

			# my $textbox = $c->yAxis()->setTitle("% of Participants");
			# $textbox->setFontStyle("arial.ttf");
			# $textbox->setFontSize(7);
			$c->yAxis()->setLabelFormat("{value}%");
			$c->yAxis()->setLinearScale(0,100,20);

			$c->xAxis()->setLabels($labels);
			$c->xAxis()->setLabelStyle("arial.ttf", 7);
			$c->xAxis()->setTickLength(1);

				# Convert the labels on the x-axis to a CDMLTable
				my $table = $c->xAxis()->makeLabelTable();
				# Set the default top/bottom margins of the cells to 3 pixels
				$table->getStyle()->setMargin2(0, 0, 3, 3);
				# Use Arial Bold as the font for the first row
				$table->getRowStyle(0)->setFontStyle("arial.ttf");
				$table->getRowStyle(0)->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent);
				$table->appendRow()->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent);
				$table->appendRow()->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent);
				for(my $i = 0; $i < scalar(@$data); ++$i) {
					$table->setText($i, 2, $data->[$i].'%');
					}
				$table->appendRow()->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent) if($show_numbers);
				for(my $i = 0; $i < scalar(@$numbers); ++$i) {
					$table->setText($i, 3, $numbers->[$i]) if($show_numbers);
					}
				$table->insertCol(0)->setMargin2(5, 5, 3, 3);
				$table->setText(0, 0, "Last Exam");
				$table->setText(0, 2, "% of Participants");
				$table->setText(0, 3, "# of Participants") if($show_numbers);

			if($isComparative && $comp_gen_basis){
				$labellayer = $c->addBarLayer($data, $perlchartdir::Transparent);   $labellayer->setBarGap($bargap);
				$labellayer->setBorderColor($perlchartdir::Transparent);
				# $labellayer->setAggregateLabelFormat("{value|1}%");
				#  $labellayer->setAggregateLabelStyle("arial.ttf", 7) ;

				$markLayer = $c->addBoxWhiskerLayer(undef, undef, undef, undef, $markdata, -1, 0x333333);
				$markLayer->setLineWidth(2);
				#  $markLayer->setDataGap(0.1);
				# Add the legend key for the mark line
				$legendBox->addKey("Comparative Group", 0x333333, 2);

				$layer = $c->addBarLayer3($data, $five_colors);$layer->setBarGap($bargap);
				$layer->setBorderColor(0x000033);
				}
			else	{
				$layer = $c->addBarLayer3($data, $five_colors, $labels);  $layer->setBarGap($bargap);
				$layer->setBorderColor(0x000033);
				#  $layer->setAggregateLabelFormat("{value|1}%");
				# $layer->setAggregateLabelStyle("arial.ttf", 7) ;
				}

			$c->getDrawArea()->setPaletteMode($perlchartdir::ForcePalette);

				if( !$c->makeChart($o_file) )
				{
					copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
				}
			else	{
				$empty_chart{print_general_exam} = 0;
				}
		}
		else {
				copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
		}

	}
 #32 HDL Levels
 	if (($input->{'pgraphs'} eq 'all' || $input->{'print_hdl'} == 1) &&
 		($assessments_chk{GHA} || $assessments_chk{HRA} || $assessments_chk{CRC} || $assessments_chk{OHA} ))
 	{
 		++$graph_cnt;
 		print $graph_cnt.". HDL<br>" unless $silent;
 		##### hdl Status
 		my $o_file = $GGR_PAGE_DIR . $PARMS{'files_prefix'} . "_ggr_hdl.png";

 		my ($hdl_basis, $hdl_high, $hdl_low, $hdl_unknown);
 		my ($comp_hdl_basis, $comp_hdl_high, $comp_hdl_low, $comp_hdl_unknown);
 		$comp_hdl_basis = $COMPPARMS{'HDL_high'} + $COMPPARMS{'HDL_low'} + $COMPPARMS{'HDL_unknown'};

 		if(($hdl_basis = $PARMS{'HDL_high'} + $PARMS{'HDL_low'} + $PARMS{'HDL_unknown'}) && $PARMS{'HDL_high'} + $PARMS{'HDL_low'})
 		{
 			$hdl_high = sprintf("%.1f",($PARMS{'HDL_high'}/$hdl_basis*100));
 			$hdl_low = sprintf("%.1f",($PARMS{'HDL_low'}/$hdl_basis*100));
 			$hdl_unknown = sprintf("%.1f",($PARMS{'HDL_unknown'}/$hdl_basis*100));


 			my %hdl_lab = (
 				low	=> "Under\nrecommended\nlevel",
 				high	=> "At or above\nrecommended\nlevel"
 				);

			if($isComparative && $comp_hdl_basis){
				$comp_hdl_high = sprintf("%.1f",($COMPPARMS{'HDL_high'}/$comp_hdl_basis*100));
				$comp_hdl_low = sprintf("%.1f",($COMPPARMS{'HDL_low'}/$comp_hdl_basis*100));
				$comp_hdl_unknown = sprintf("%.1f",($COMPPARMS{'HDL_unknown'}/$comp_hdl_basis*100));
				}

			my $markdata = [$comp_hdl_low ,$comp_hdl_high, $comp_hdl_unknown] if $isComparative;
			my $numbers = [$PARMS{'HDL_low'} , $PARMS{'HDL_high'} ];
			push (@{$numbers}, $PARMS{'HDL_unknown'}) if ($PARMS{'HDL_unknown'} > 0 || ($COMPPARMS{'HDL_unknown'} > 0 && $isComparative));
 			my $data = [$hdl_low ,$hdl_high ];
 			push (@{$data}, $hdl_unknown) if ($hdl_unknown > 0 || ($COMPPARMS{'HDL_unknown'} > 0 && $isComparative));

 			my $labels = [$hdl_lab{low}, $hdl_lab{high} ];
 			push(@{$labels},"unknown") if ($hdl_unknown > 0 || ($COMPPARMS{'HDL_unknown'} > 0 && $isComparative));

 			my $c = new XYChart($bar_chartwide, $bar_charthigh, 0xffffff);

 			$c->setPlotArea(90, 50, 255, 180, $perlchartdir::Transparent, -1, $perlchartdir::Transparent, 0xe0e0e0);

 			my $title = $c->addTitle2(8, "HDL levels", "arial.ttf", 12);

 			my $legendBox;
 			my $labellayer;
 			my $markLayer;
 			my $layer;
 			if($isComparative && $comp_hdl_basis){
				$legendBox = $c->addLegend($c->getWidth() / 2, $title->getHeight()-7, "arial.ttf", 8);
 				$legendBox->setBackground($perlchartdir::Transparent, $perlchartdir::Transparent);
 				$legendBox->setAlignment($perlchartdir::TopCenter);
 				$legendBox->setLineStyleKey();
 				}

 			# my $textbox = $c->yAxis()->setTitle("% of Participants");
 			# $textbox->setFontStyle("arial.ttf");
 			# $textbox->setFontSize(7);
 			$c->yAxis()->setLabelFormat("{value}%");
 			$c->yAxis()->setLinearScale(0,100,20);

 			$c->xAxis()->setLabels($labels);
 			$c->xAxis()->setLabelStyle("arial.ttf", 7);
 			$c->xAxis()->setTickLength(1);

				# Convert the labels on the x-axis to a CDMLTable
				my $table = $c->xAxis()->makeLabelTable();
				# Set the default top/bottom margins of the cells to 3 pixels
				$table->getStyle()->setMargin2(0, 0, 3, 3);
				# Use Arial Bold as the font for the first row
				$table->getRowStyle(0)->setFontStyle("arial.ttf");
				$table->getRowStyle(0)->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent);
				$table->appendRow()->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent);
				$table->appendRow()->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent);
				for(my $i = 0; $i < scalar(@$data); ++$i) {
					$table->setText($i, 2, $data->[$i].'%');
					}
				$table->appendRow()->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent) if($show_numbers);
				for(my $i = 0; $i < scalar(@$numbers); ++$i) {
					$table->setText($i, 3, $numbers->[$i]) if($show_numbers);
					}
				$table->insertCol(0)->setMargin2(5, 5, 3, 3);
				$table->setText(0, 0, "Levels");
				$table->setText(0, 2, "% of Participants");
				$table->setText(0, 3, "# of Participants") if($show_numbers);

			if($isComparative && $comp_hdl_basis){
				$labellayer = $c->addBarLayer($data, $perlchartdir::Transparent);   $labellayer->setBarGap($bargap);
				$labellayer->setBorderColor($perlchartdir::Transparent);
				# $labellayer->setAggregateLabelFormat("{value|1}%");
				#  $labellayer->setAggregateLabelStyle("arial.ttf", 7) ;

				$markLayer = $c->addBoxWhiskerLayer(undef, undef, undef, undef, $markdata, -1, 0x333333);
				$markLayer->setLineWidth(2);
				#  $markLayer->setDataGap(0.1);
				# Add the legend key for the mark line
				$legendBox->addKey("Comparative Group", 0x333333, 2);

				$layer = $c->addBarLayer3($data, $five_colors);$layer->setBarGap($bargap);
				$layer->setBorderColor(0x000033);
				}
			else	{
				$layer = $c->addBarLayer3($data, $five_colors, $labels);  $layer->setBarGap($bargap);
				$layer->setBorderColor(0x000033);
				#  $layer->setAggregateLabelFormat("{value|1}%");
				# $layer->setAggregateLabelStyle("arial.ttf", 7) ;
				}

 			$c->getDrawArea()->setPaletteMode($perlchartdir::ForcePalette);

 				if( !$c->makeChart($o_file) )
 				{
 					copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
 				}
 			else	{
 				$empty_chart{print_hdl} = 0;
 				}
 		}
 		else {
 				copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
 		}

 	}
 #33 Flu Shot
 	if (($input->{'pgraphs'} eq 'all' || $input->{'print_flu'} == 1) &&
 		($assessments_chk{GHA} || $assessments_chk{HRA} || $assessments_chk{OHA}  ))
 	{
 		++$graph_cnt;
 		print $graph_cnt.". Flu Shots<br>" unless $silent;
 		##### flu shot Status
 		my $o_file = $GGR_PAGE_DIR . $PARMS{'files_prefix'} . "_ggr_flu.png";

 		my ($flu_basis, $flu_no, $flu_good, $flu_expired);
 		my ($comp_flu_basis, $comp_flu_no, $comp_flu_good, $comp_flu_expired);
 		$comp_flu_basis = $COMPPARMS{'flu_no'} + $COMPPARMS{'flu_old'} + $COMPPARMS{'flu_current'};

 		if($flu_basis = $PARMS{'flu_no'} + $PARMS{'flu_old'} + $PARMS{'flu_current'})
 		{
 			$flu_no = sprintf("%.1f",($PARMS{'flu_no'}/$flu_basis*100));
 			$flu_old = sprintf("%.1f",($PARMS{'flu_old'}/$flu_basis*100));
 			$flu_current = sprintf("%.1f",($PARMS{'flu_current'}/$flu_basis*100));


 			my %flu_lab = (
 				no	=> "No flu shot",
 				old	=> "More than 1 year ago",
 				current	=> "Within 1 year"
 				);

			if($isComparative && $comp_flu_basis){
				$comp_flu_no = sprintf("%.1f",($COMPPARMS{'flu_no'}/$comp_flu_basis*100));
				$comp_flu_old = sprintf("%.1f",($COMPPARMS{'flu_old'}/$comp_flu_basis*100));
				$comp_flu_current = sprintf("%.1f",($COMPPARMS{'flu_current'}/$comp_flu_basis*100));
				}

			my $markdata = [$comp_flu_current,$comp_flu_old, $comp_flu_no ] if $isComparative;
			my $numbers = [$PARMS{'flu_current'}, $PARMS{'flu_old'}, $PARMS{'flu_no'} ];
 			my $data = [$flu_current, $flu_old, $flu_no  ];

 			my $labels = [$flu_lab{current}, $flu_lab{old}, $flu_lab{no} ];

 			my $c = new XYChart($bar_chartwide, $bar_charthigh, 0xffffff);

 			$c->setPlotArea(90, 50, 255, 180, $perlchartdir::Transparent, -1, $perlchartdir::Transparent, 0xe0e0e0);

 			my $title = $c->addTitle2(8, "Flu Shots", "arial.ttf", 12);

 			my $legendBox;
 			my $labellayer;
 			my $markLayer;
 			my $layer;
 			if($isComparative && $comp_hdl_basis){
				$legendBox = $c->addLegend($c->getWidth() / 2, $title->getHeight()-7, "arial.ttf", 8);
 				$legendBox->setBackground($perlchartdir::Transparent, $perlchartdir::Transparent);
 				$legendBox->setAlignment($perlchartdir::TopCenter);
 				$legendBox->setLineStyleKey();
 				}

 			# my $textbox = $c->yAxis()->setTitle("% of Participants");
 			# $textbox->setFontStyle("arial.ttf");
 			# $textbox->setFontSize(7);
 			$c->yAxis()->setLabelFormat("{value}%");
 			$c->yAxis()->setLinearScale(0,100,20);

 			$c->xAxis()->setLabels($labels);
 			$c->xAxis()->setLabelStyle("arial.ttf", 7);
 			$c->xAxis()->setTickLength(1);

				# Convert the labels on the x-axis to a CDMLTable
				my $table = $c->xAxis()->makeLabelTable();
				# Set the default top/bottom margins of the cells to 3 pixels
				$table->getStyle()->setMargin2(0, 0, 3, 3);
				# Use Arial Bold as the font for the first row
				$table->getRowStyle(0)->setFontStyle("arial.ttf");
				$table->getRowStyle(0)->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent);
				$table->appendRow()->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent);
				$table->appendRow()->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent);
				for(my $i = 0; $i < scalar(@$data); ++$i) {
					$table->setText($i, 2, $data->[$i].'%');
					}
				$table->appendRow()->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent) if($show_numbers);
				for(my $i = 0; $i < scalar(@$numbers); ++$i) {
					$table->setText($i, 3, $numbers->[$i]) if($show_numbers);
					}
				$table->insertCol(0)->setMargin2(5, 5, 3, 3);
				$table->setText(0, 0, "Levels");
				$table->setText(0, 2, "% of Participants");
				$table->setText(0, 3, "# of Participants") if($show_numbers);

			if($isComparative && $comp_flu_basis){
				$labellayer = $c->addBarLayer($data, $perlchartdir::Transparent);   $labellayer->setBarGap($bargap);
				$labellayer->setBorderColor($perlchartdir::Transparent);
				# $labellayer->setAggregateLabelFormat("{value|1}%");
				#  $labellayer->setAggregateLabelStyle("arial.ttf", 7) ;

				$markLayer = $c->addBoxWhiskerLayer(undef, undef, undef, undef, $markdata, -1, 0x333333);
				$markLayer->setLineWidth(2);
				#  $markLayer->setDataGap(0.1);
				# Add the legend key for the mark line
				$legendBox->addKey("Comparative Group", 0x333333, 2);

				$layer = $c->addBarLayer3($data, $five_colors);$layer->setBarGap($bargap);
				$layer->setBorderColor(0x000033);
				}
			else	{
				$layer = $c->addBarLayer3($data, $five_colors, $labels);  $layer->setBarGap($bargap);
				$layer->setBorderColor(0x000033);
				#  $layer->setAggregateLabelFormat("{value|1}%");
				# $layer->setAggregateLabelStyle("arial.ttf", 7) ;
				}

 			$c->getDrawArea()->setPaletteMode($perlchartdir::ForcePalette);

 				if( !$c->makeChart($o_file) )
 				{
 					copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
 				}
 			else	{
 				$empty_chart{print_flu} = 0;
 				}
 		}
 		else {
 				copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
 		}

 	}
 #34 Waist
 	if (($input->{'pgraphs'} eq 'all' || $input->{'print_waist'} == 1) &&
 		( $PARMS{'waist_count'} ))
 	{
 		++$graph_cnt;
 		print $graph_cnt.". Waist Measure<br>" unless $silent;
 		##### Waist Measure Status
 		my $o_file = $GGR_PAGE_DIR . $PARMS{'files_prefix'} . "_ggr_waist.png";

 		my ($waist_basis, $waist_high, $waist_ok);
 		my ($comp_waist_basis, $comp_waist_high, $comp_waist_ok);
 		$comp_waist_basis = $COMPPARMS{'waist_high'} + $COMPPARMS{'waist_ok'} ;

 		if($waist_basis = $PARMS{'waist_high'} + $PARMS{'waist_ok'})
 		{
 			$waist_high = sprintf("%.1f",($PARMS{'waist_high'}/$waist_basis*100));
 			$waist_ok = sprintf("%.1f",($PARMS{'waist_ok'}/$waist_basis*100));


 			my %waist_lab = (
 				high	=> "Waist above 35 inches for women and 40 inches for men",
 				ok	=> "Waist below high ranges",
 				);

			if($isComparative && $comp_waist_basis){
				$comp_waist_high = sprintf("%.1f",($COMPPARMS{'waist_high'}/$comp_waist_basis*100));
				$comp_waist_ok = sprintf("%.1f",($COMPPARMS{'waist_ok'}/$comp_waist_basis*100));
				}

			my $markdata = [$comp_waist_ok, $comp_waist_high] if $isComparative;
			my $numbers = [$PARMS{'waist_ok'}, $PARMS{'waist_high'}  ];
 			my $data = [ $waist_ok,  $waist_high ];

 			my $labels = [$waist_lab{ok}, $waist_lab{high}  ];

 			my $c = new XYChart($bar_chartwide, $bar_charthigh, 0xffffff);

 			$c->setPlotArea(90, 50, 255, 180, $perlchartdir::Transparent, -1, $perlchartdir::Transparent, 0xe0e0e0);

 			my $title = $c->addTitle2(8, "Waist Measurement", "arial.ttf", 12);

 			my $legendBox;
 			my $labellayer;
 			my $markLayer;
 			my $layer;
 			if($isComparative && $comp_hdl_basis){
				$legendBox = $c->addLegend($c->getWidth() / 2, $title->getHeight()-7, "arial.ttf", 8);
 				$legendBox->setBackground($perlchartdir::Transparent, $perlchartdir::Transparent);
 				$legendBox->setAlignment($perlchartdir::TopCenter);
 				$legendBox->setLineStyleKey();
 				}

 			# my $textbox = $c->yAxis()->setTitle("% of Participants");
 			# $textbox->setFontStyle("arial.ttf");
 			# $textbox->setFontSize(7);
 			$c->yAxis()->setLabelFormat("{value}%");
 			$c->yAxis()->setLinearScale(0,100,20);

 			$c->xAxis()->setLabels($labels);
 			$c->xAxis()->setLabelStyle("arial.ttf", 7);
 			$c->xAxis()->setTickLength(1);

				# Convert the labels on the x-axis to a CDMLTable
				my $table = $c->xAxis()->makeLabelTable();
				# Set the default top/bottom margins of the cells to 3 pixels
				$table->getStyle()->setMargin2(0, 0, 3, 3);
				# Use Arial Bold as the font for the first row
				$table->getRowStyle(0)->setFontStyle("arial.ttf");
				$table->getRowStyle(0)->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent);
				$table->appendRow()->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent);
				$table->appendRow()->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent);
				for(my $i = 0; $i < scalar(@$data); ++$i) {
					$table->setText($i, 2, $data->[$i].'%');
					}
				$table->appendRow()->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent) if($show_numbers);
				for(my $i = 0; $i < scalar(@$numbers); ++$i) {
					$table->setText($i, 3, $numbers->[$i]) if($show_numbers);
					}
				$table->insertCol(0)->setMargin2(5, 5, 3, 3);
				$table->setText(0, 0, "Levels");
				$table->setText(0, 2, "% of Participants");
				$table->setText(0, 3, "# of Participants") if($show_numbers);

			if($isComparative && $comp_waist_basis){
				$labellayer = $c->addBarLayer($data, $perlchartdir::Transparent);   $labellayer->setBarGap($bargap);
				$labellayer->setBorderColor($perlchartdir::Transparent);
				# $labellayer->setAggregateLabelFormat("{value|1}%");
				#  $labellayer->setAggregateLabelStyle("arial.ttf", 7) ;

				$markLayer = $c->addBoxWhiskerLayer(undef, undef, undef, undef, $markdata, -1, 0x333333);
				$markLayer->setLineWidth(2);
				#  $markLayer->setDataGap(0.1);
				# Add the legend key for the mark line
				$legendBox->addKey("Comparative Group", 0x333333, 2);

				$layer = $c->addBarLayer3($data, $five_colors);$layer->setBarGap($bargap);
				$layer->setBorderColor(0x000033);
				}
			else	{
				$layer = $c->addBarLayer3($data, $five_colors, $labels);  $layer->setBarGap($bargap);
				$layer->setBorderColor(0x000033);
				#  $layer->setAggregateLabelFormat("{value|1}%");
				# $layer->setAggregateLabelStyle("arial.ttf", 7) ;
				}

 			$c->getDrawArea()->setPaletteMode($perlchartdir::ForcePalette);

 				if( !$c->makeChart($o_file) )
 				{
 					copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
 				}
 			else	{
 				$empty_chart{print_waist} = 0;
 				}
 		}
 		else {
 				copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
 		}

 	}
 #35 Diet
 	if (($input->{'pgraphs'} eq 'all' || $input->{'print_diet'} == 1) &&
 		($assessments_chk{GHA} || $assessments_chk{HRA} || $assessments_chk{OHA}  || $assessments_chk{CRC}  ))
 	{
 		++$graph_cnt;
 		print $graph_cnt.". Diet<br>" unless $silent;
 		##### Diet Status
 		my $o_file = $GGR_PAGE_DIR . $PARMS{'files_prefix'} . "_ggr_diet.png";

 		my ($diet_fiber_basis, $diet_fat_basis, $diet_fiber_good, $diet_fat_good, $diet_fiber_bad, $diet_fat_bad);
 		my ($comp_diet_fiber_basis, $comp_diet_fat_basis,  $comp_diet_fiber_good, $comp_diet_fat_good, $comp_diet_fiber_bad, $comp_diet_fat_bad);
 		$comp_diet_fiber_basis = $COMPPARMS{'diet_fiber_good'} +  + $COMPPARMS{'diet_fiber_bad'};
 		$comp_diet_fat_basis = $COMPPARMS{'diet_fat_good'} + $COMPPARMS{'diet_fat_bad'};
 		$diet_fiber_basis = $PARMS{'diet_fiber_good'} + $PARMS{'diet_fiber_bad'};
 		$diet_fat_basis = $PARMS{'diet_fat_good'} + $PARMS{'diet_fat_bad'};

 		if($diet_fiber_basis || $diet_fat_basis)
 		{
 			$diet_fiber_good = sprintf("%.1f",($PARMS{'diet_fiber_good'}/$diet_fiber_basis*100));
 			$diet_fiber_bad = sprintf("%.1f",($PARMS{'diet_fiber_bad'}/$diet_fiber_basis*100));
 			$diet_fat_good = sprintf("%.1f",($PARMS{'diet_fat_good'}/$diet_fat_basis*100));
 			$diet_fat_bad = sprintf("%.1f",($PARMS{'diet_fat_bad'}/$diet_fat_basis*100));


 			my %diet_lab = (
 				fiber_good	=> "Fiber in Diet",
 				fiber_bad	=> "Low or No Fiber in Diet",
 				fat_good	=> "Diet Low in Fat",
 				fat_bad		=> "Diet High in Fat"
 				);

			if($isComparative && $comp_diet_basis){
				$comp_diet_fiber_good = sprintf("%.1f",($COMPPARMS{'diet_fiber_good'}/$comp_diet_fiber_basis*100));
				$comp_diet_fiber_bad = sprintf("%.1f",($COMPPARMS{'diet_fiber_bad'}/$comp_diet_fiber_basis*100));
				$comp_diet_fat_good = sprintf("%.1f",($COMPPARMS{'diet_fat_good'}/$comp_diet_fat_basis*100));
				$comp_diet_fat_bad = sprintf("%.1f",($COMPPARMS{'diet_fat_bad'}/$comp_diet_fat_basis*100));
				}

			my $markdata = [$comp_diet_fiber_good,$comp_diet_fiber_bad,  $comp_diet_fat_good, $comp_diet_fat_bad ] if $isComparative;
			my $numbers = [$PARMS{'diet_fiber_good'}, $PARMS{'diet_fiber_bad'}, $PARMS{'diet_fat_good'}, $PARMS{'diet_fat_bad'} ];
 			my $data = [$diet_fiber_good, $diet_fiber_bad, $diet_fat_good, $diet_fat_bad  ];

 			my $labels = [$diet_lab{fiber_good}, $diet_lab{fiber_bad}, $diet_lab{fat_good}, $diet_lab{fat_bad} ];

 			my $c = new XYChart($bar_chartwide, $bar_charthigh, 0xffffff);

 			$c->setPlotArea(90, 50, 255, 180, $perlchartdir::Transparent, -1, $perlchartdir::Transparent, 0xe0e0e0);

 			my $title = $c->addTitle2(8, "Dietary Habits", "arial.ttf", 12);

 			my $legendBox;
 			my $labellayer;
 			my $markLayer;
 			my $layer;
 			if($isComparative && $comp_hdl_basis){
				$legendBox = $c->addLegend($c->getWidth() / 2, $title->getHeight()-7, "arial.ttf", 8);
 				$legendBox->setBackground($perlchartdir::Transparent, $perlchartdir::Transparent);
 				$legendBox->setAlignment($perlchartdir::TopCenter);
 				$legendBox->setLineStyleKey();
 				}

 			# my $textbox = $c->yAxis()->setTitle("% of Participants");
 			# $textbox->setFontStyle("arial.ttf");
 			# $textbox->setFontSize(7);
 			$c->yAxis()->setLabelFormat("{value}%");
 			$c->yAxis()->setLinearScale(0,100,20);

 			$c->xAxis()->setLabels($labels);
 			$c->xAxis()->setLabelStyle("arial.ttf", 7);
 			$c->xAxis()->setTickLength(1);

				# Convert the labels on the x-axis to a CDMLTable
				my $table = $c->xAxis()->makeLabelTable();
				# Set the default top/bottom margins of the cells to 3 pixels
				$table->getStyle()->setMargin2(0, 0, 3, 3);
				# Use Arial Bold as the font for the first row
				$table->getRowStyle(0)->setFontStyle("arial.ttf");
				$table->getRowStyle(0)->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent);
				$table->appendRow()->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent);
				$table->appendRow()->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent);
				for(my $i = 0; $i < scalar(@$data); ++$i) {
					$table->setText($i, 2, $data->[$i].'%');
					}
				$table->appendRow()->setBackground($perlchartdir::Transparent,$perlchartdir::Transparent) if($show_numbers);
				for(my $i = 0; $i < scalar(@$numbers); ++$i) {
					$table->setText($i, 3, $numbers->[$i]) if($show_numbers);
					}
				$table->insertCol(0)->setMargin2(5, 5, 3, 3);
				$table->setText(0, 0, "Levels");
				$table->setText(0, 2, "% of Participants");
				$table->setText(0, 3, "# of Participants") if($show_numbers);

			if($isComparative && $comp_flu_basis){
				$labellayer = $c->addBarLayer($data, $perlchartdir::Transparent);   $labellayer->setBarGap($bargap);
				$labellayer->setBorderColor($perlchartdir::Transparent);
				# $labellayer->setAggregateLabelFormat("{value|1}%");
				#  $labellayer->setAggregateLabelStyle("arial.ttf", 7) ;

				$markLayer = $c->addBoxWhiskerLayer(undef, undef, undef, undef, $markdata, -1, 0x333333);
				$markLayer->setLineWidth(2);
				#  $markLayer->setDataGap(0.1);
				# Add the legend key for the mark line
				$legendBox->addKey("Comparative Group", 0x333333, 2);

				$layer = $c->addBarLayer3($data, $five_colors);$layer->setBarGap($bargap);
				$layer->setBorderColor(0x000033);
				}
			else	{
				$layer = $c->addBarLayer3($data, $five_colors, $labels);  $layer->setBarGap($bargap);
				$layer->setBorderColor(0x000033);
				#  $layer->setAggregateLabelFormat("{value|1}%");
				# $layer->setAggregateLabelStyle("arial.ttf", 7) ;
				}

 			$c->getDrawArea()->setPaletteMode($perlchartdir::ForcePalette);

 				if( !$c->makeChart($o_file) )
 				{
 					copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
 				}
 			else	{
 				$empty_chart{print_diet} = 0;
 				}
 		}
 		else {
 				copy ($blank_data, $o_file) or die "$! - $blank_data to $o_file copy error";
 		}

 	}
	$PARMS{empty_chart} = \%empty_chart;
	return \%PARMS;

}
sub prepare_hashes_arg_pdf
{
	my ( $input, $GGR_PAGE_DIR, $assessments_ref, $assessment_count_ref, $PARMS_ref, $GROUP_ref, $hra_cnt ) = @_;

	my @assessment_count = @$assessment_count_ref;
	my %PARMS = %{$PARMS_ref};
	my %GROUP = %{$GROUP_ref};

	my %OUTPUT_DATA = ();
	my @sheet_list;

	print $graph_cnt.". ";

	my $graph_cnt = 0;

	if ($input->{'pgraphs'} eq 'all' || $input->{'print_achievable'} == 1)
		{
		++$graph_cnt;
		print $graph_cnt.". ";
		### Achievable Group levels
		my $o_file = "Achievable Group Risk";
		push @sheet_list, $o_file;

		my ($alparm, $amparm, $ahparm, $avparm, $albasis);
		$albasis = $PARMS{'ach_low'} + $PARMS{'ach_moderate'} + $PARMS{'ach_medium'} + $PARMS{'ach_high'};
		if( $albasis )
			{
			$alparm = sprintf("%.1f",($PARMS{'ach_low'}/$albasis * 100));
			$amparm = sprintf("%.1f",($PARMS{'ach_moderate'}/$albasis * 100));
			$ahparm = sprintf("%.1f",($PARMS{'ach_medium'}/$albasis * 100));
			$avparm = sprintf("%.1f",($PARMS{'ach_high'}/$albasis * 100));


			my @g_data = (
				["Low Risk", "Moderate Risk", "High Risk", "Very High"],
				[ $alparm, $amparm, $ahparm, $avparm]
				);
			my $j=0;
			foreach (@{$g_data[0]}) { $OUTPUT_DATA{$o_file}{computed}{$_}= $g_data[1][$j]; ++$j; }
			$OUTPUT_DATA{$o_file}{label} = 'Participants achievable risk levels';
			$OUTPUT_DATA{$o_file}{label_x} = 'Risk Levels';
			$OUTPUT_DATA{$o_file}{label_y} = '% Participants';
			$OUTPUT_DATA{$o_file}{raw}{total} = $albasis;
			$OUTPUT_DATA{$o_file}{raw}{'low risk'} = $PARMS{'ach_low'};
			$OUTPUT_DATA{$o_file}{raw}{'moderate risk'} = $PARMS{'ach_moderate'};
			$OUTPUT_DATA{$o_file}{raw}{'high risk'} = $PARMS{'ach_medium'};
			$OUTPUT_DATA{$o_file}{raw}{'very high risk'} = $PARMS{'ach_high'};
			$OUTPUT_DATA{$o_file}{title} = 'Achievable Group Risk';
			$OUTPUT_DATA{$o_file}{g_data} = [ @g_data ];
			$OUTPUT_DATA{$o_file}{x_data} = [  ];
			}

		}
	if ($input->{'pgraphs'} eq 'all' || $input->{'print_agegroups'} == 1)
		{
		++$graph_cnt;
		print $graph_cnt.". ";
		####  Age Range by sex
		my $o_file = 'Gender by Age Group';
		push @sheet_list, $o_file;

		if(my $age_basis = ($PARMS{'m_lt_19'}+$PARMS{'m_20_29'}+$PARMS{'m_30_39'}+$PARMS{'m_40_49'}+$PARMS{'m_50_59'}+$PARMS{'m_60'}+$PARMS{'f_lt_19'}+$PARMS{'f_20_29'}+$PARMS{'f_30_39'}+$PARMS{'f_40_49'}+$PARMS{'f_50_59'}+$PARMS{'f_60'}))
			{
			my @g_data = (
				    ["under 19",                                           "20-29",                                 "30-39",                            "40-49",                                          "50-59",                          "60+"],
				    [(int($PARMS{'m_lt_19'}/$age_basis*100)), (int($PARMS{'m_20_29'}/$age_basis*100)), (int($PARMS{'m_30_39'}/$age_basis*100)), (int($PARMS{'m_40_49'}/$age_basis*100)), (int($PARMS{'m_50_59'}/$age_basis*100)), (int($PARMS{'m_60'}/$age_basis*100))],
				    [(int($PARMS{'f_lt_19'}/$age_basis*100)), (int($PARMS{'f_20_29'}/$age_basis*100)), (int($PARMS{'f_30_39'}/$age_basis*100)), (int($PARMS{'f_40_49'}/$age_basis*100)), (int($PARMS{'f_50_59'}/$age_basis*100)), (int($PARMS{'f_60'}/$age_basis*100))]
			  	);
			my @x_data = (
				    ["under 19",                                           "20-29",                                 "30-39",                            "40-49",                                          "50-59",                          "60+"],
				    [$PARMS{'m_lt_19'}, $PARMS{'m_20_29'}, $PARMS{'m_30_39'}, $PARMS{'m_40_49'}, $PARMS{'m_50_59'}, $PARMS{'m_60'}],
				    [$PARMS{'f_lt_19'}, $PARMS{'f_20_29'}, $PARMS{'f_30_39'}, $PARMS{'f_40_49'}, $PARMS{'f_50_59'}, $PARMS{'f_60'}]
			  	);
			my $j=0;
			foreach (@{$g_data[0]}) { $OUTPUT_DATA{$o_file}{computed}{key}{Males}{$_}= $g_data[1][$j]; $OUTPUT_DATA{$o_file}{computed}{key}{Females}{$_}= $g_data[2][$j]; ++$j; }
			my $j=0;
			foreach (@{$x_data[0]}) { $OUTPUT_DATA{$o_file}{raw}{key}{Males}{$_}= $x_data[1][$j]; $OUTPUT_DATA{$o_file}{raw}{key}{Females}{$_}= $x_data[2][$j]; ++$j; }
			$OUTPUT_DATA{$o_file}{label_x} = 'Age groups';
			$OUTPUT_DATA{$o_file}{label_y} = '% Participants';
			my @subtitle = ( 'Male', 'Female');
			$OUTPUT_DATA{$o_file}{label_y_sub} = [ @subtitle ];
			$OUTPUT_DATA{$o_file}{raw}{key}{total} = $age_basis;
			$OUTPUT_DATA{$o_file}{title} = 'Gender by Age Group';
			$OUTPUT_DATA{$o_file}{g_data} = [ @g_data ];
			$OUTPUT_DATA{$o_file}{x_data} = [ @x_data ];
			}

		}
	if ($input->{'pgraphs'} eq 'all' || $input->{'print_totalassessments'} == 1)
		{
		++$graph_cnt;
		print $graph_cnt.". ";
		#### Total Assessments Taken  #######
		my $o_file = 'Number of Assessments Taken';
		push @sheet_list, $o_file;

		my @g_data=(
			$assessments_ref, \@assessment_count
			);

			my $j=0;
			foreach (@{$g_data[0]}) { $OUTPUT_DATA{$o_file}{computed}{$_}= $g_data[1][$j]; $OUTPUT_DATA{$o_file}{raw}{$_}= $g_data[1][$j]; ++$j; }
			$OUTPUT_DATA{$o_file}{raw}{total}=  $hra_cnt;
			$OUTPUT_DATA{$o_file}{title} = 'Number of Assessments Taken';
			$OUTPUT_DATA{$o_file}{label_x} = 'Assessments';
			$OUTPUT_DATA{$o_file}{label_y} = 'Number taken';
			$OUTPUT_DATA{$o_file}{g_data} = [ @g_data ];
			$OUTPUT_DATA{$o_file}{x_data} = [  ];
		}

	if ($input->{'pgraphs'} eq 'all' || $input->{'print_preventable'} == 1)
		{
		++$graph_cnt;
		print $graph_cnt.". ";
		##### Preventable deaths by disease
		my $o_file = 'Preventable Deaths by Disease';
		push @sheet_list, $o_file;

		if( $hra_cnt )
			{
			my @g_data=(
				['Throat Cancer',                                   'Flu/Pneumonia',                                    'Liver',                                        'Lung Cancer',                                     'Kidney Failure',                                 'Esophageal Cancer',                            'Pancreatic Cancer',                                       'Uterine Cancer',                                   'Emphysema',                           'Laryngeal Cancer',                                           'Heart Attack',                               'Breast Cancer',                                      'Diabetes Mellitus',                              'Motor Vehicle',                                     'Cervical Cancer',                                    'Stroke',                                'Mouth Cancer',                                 'Bladder Cancer',                                   'Peptic Ulcer'],
				[(int($GROUP{'Throat Cancer'}/$hra_cnt * 100)),(int($GROUP{'Flu/Pneumonia'}/$hra_cnt * 100)),(int($GROUP{'Liver Cirrhosis'}/$hra_cnt * 100)),(int($GROUP{'Lung Cancer'}/$hra_cnt * 100)),(int($GROUP{'Kidney Failure'}/$hra_cnt * 100)),(int($GROUP{'Esophageal Cancer'}/$hra_cnt * 100)),(int($GROUP{'Pancreatic Cancer'}/$hra_cnt * 100)),(int($GROUP{'Uterine Cancer'}/$hra_cnt * 100)),(int($GROUP{'Emphysema'}/$hra_cnt * 100)),(int($GROUP{'Laryngeal Cancer'}/$hra_cnt * 100)),(int($GROUP{'Heart Attack'}/$hra_cnt * 100)),(int($GROUP{'Breast Cancer'}/$hra_cnt * 100)),(int($GROUP{'Diabetes Mellitus'}/$hra_cnt * 100)),(int($GROUP{'Motor Vehicle'}/$hra_cnt * 100)),(int($GROUP{'Cervical Cancer'}/$hra_cnt * 100)),(int($GROUP{'Stroke'}/$hra_cnt * 100)),(int($GROUP{'Mouth Cancer'}/$hra_cnt * 100)),(int($GROUP{'Bladder Cancer'}/$hra_cnt * 100)),(int($GROUP{'Peptic Ulcer'}/$hra_cnt * 100))]
				);
			my @x_data=(
				['Throat Cancer',                                   'Flu/Pneumonia',                                    'Liver',                                        'Lung Cancer',                                     'Kidney Failure',                                 'Esophageal Cancer',                            'Pancreatic Cancer',                                       'Uterine Cancer',                                   'Emphysema',                           'Laryngeal Cancer',                                           'Heart Attack',                               'Breast Cancer',                                      'Diabetes Mellitus',                              'Motor Vehicle',                                     'Cervical Cancer',                                    'Stroke',                                'Mouth Cancer',                                 'Bladder Cancer',                                   'Peptic Ulcer'],
				[$GROUP{'Throat Cancer'} , $GROUP{'Flu/Pneumonia'} , $GROUP{'Liver Cirrhosis'} , $GROUP{'Lung Cancer'} , $GROUP{'Kidney Failure'} , $GROUP{'Esophageal Cancer'} , $GROUP{'Pancreatic Cancer'} , $GROUP{'Uterine Cancer'} , $GROUP{'Emphysema'} , $GROUP{'Laryngeal Cancer'} , $GROUP{'Heart Attack'} , $GROUP{'Breast Cancer'} , $GROUP{'Diabetes Mellitus'} , $GROUP{'Motor Vehicle'} , $GROUP{'Cervical Cancer'} , $GROUP{'Stroke'} , $GROUP{'Mouth Cancer'} , $GROUP{'Bladder Cancer'} , $GROUP{'Peptic Ulcer'}]
				);
			my $j=0;
			foreach (@{$g_data[0]}) { $OUTPUT_DATA{$o_file}{computed}{$_}= $g_data[1][$j]; ++$j; }
			$j=0;
			foreach (@{$x_data[0]}) { $OUTPUT_DATA{$o_file}{raw}{$_}= $x_data[1][$j]; ++$j; }
			$OUTPUT_DATA{$o_file}{raw}{total}=  $hra_cnt;
			$OUTPUT_DATA{$o_file}{title} = 'Preventable Deaths by Disease';
			$OUTPUT_DATA{$o_file}{label} = 'Elevated risk within group';
			$OUTPUT_DATA{$o_file}{label_x} = 'Disease';
			$OUTPUT_DATA{$o_file}{label_y} = 'Participants with high risk';
			$OUTPUT_DATA{$o_file}{g_data} = [ @g_data ];
			$OUTPUT_DATA{$o_file}{x_data} = [ @x_data ];
			}

		}
	if ($input->{'pgraphs'} eq 'all' || $input->{'print_riskfactors'} == 1)
		{
		++$graph_cnt;
		print $graph_cnt.". ";
		####  Risk Factors
		my $o_file = "Group Contributing Risk Factors";
		push @sheet_list, $o_file;

		if (my $be_basis = $PARMS{'exer_none'}+$PARMS{'sm_still'}+$PARMS{'HDL_low'}+$PARMS{'chol_high'}+$PARMS{'alc_high'}+$PARMS{'bp_high'}+$PARMS{'sb_speed'}+$PARMS{'sb_some'}+$PARMS{'sb_never'}+$PARMS{'mammo_bad'}+$PARMS{'pap_bad'}+$PARMS{'wt_obese'})
			{
			my @g_data = (
				['Lack of Exercise',                               'Smoking',                           'Low HDL',                                      'High Cholesterol',               'Alcohol Use',                     'High Blood Pressure',                      'Speeding',                                'Seat Belt Use',                                   'Mammograms',                              'Pelvic Exams',                       'Weight'],
				[(int($PARMS{'exer_none'}/$be_basis*100)),(int($PARMS{'sm_still'}/$be_basis*100)),(int($PARMS{'HDL_low'}/$be_basis*100)),(int($PARMS{'chol_high'}/$be_basis*100)),(int($PARMS{'alc_high'}/$be_basis*100)),(int($PARMS{'bp_high'}/$be_basis*100)),(int($PARMS{'sb_speed'}/$be_basis*100)),(int(($PARMS{'sb_some'}+$PARMS{'sb_never'})/$be_basis*100)),(int($PARMS{'mammo_bad'}/$be_basis*100)),(int($PARMS{'pap_bad'}/$be_basis*100)),(int($PARMS{'wt_obese'}/$be_basis*100))]
				);
			my @x_data = (
				['Lack of Exercise', 'Smoking', 'Low HDL', 'High Cholesterol', 'Alcohol Use', 'High Blood Pressure', 'Speeding', 'Seat Belt Use', 'Mammograms', 'Pelvic Exams', 'Weight'],
				[$PARMS{'exer_none'},$PARMS{'sm_still'},$PARMS{'HDL_low'},$PARMS{'chol_high'},$PARMS{'alc_high'},$PARMS{'bp_high'},$PARMS{'sb_speed'},(int($PARMS{'sb_some'}+$PARMS{'sb_never'})),$PARMS{'mammo_bad'},$PARMS{'pap_bad'},$PARMS{'wt_obese'}]
				);

			my $j=0;
			foreach (@{$g_data[0]}) { $OUTPUT_DATA{$o_file}{computed}{$_}= $g_data[1][$j]; ++$j; }
			$j=0;
			foreach (@{$x_data[0]}) { $OUTPUT_DATA{$o_file}{raw}{$_}= $x_data[1][$j]; ++$j; }
			$OUTPUT_DATA{$o_file}{raw}{total}=  $be_basis;
			$OUTPUT_DATA{$o_file}{title} = 'Group Contributing Risk Factors';
			$OUTPUT_DATA{$o_file}{label} = 'Modifiable behaviors';
			$OUTPUT_DATA{$o_file}{label_x} = 'Condition';
			$OUTPUT_DATA{$o_file}{label_y} = '% Participants with condition';
			$OUTPUT_DATA{$o_file}{g_data} = [ @g_data ];
			$OUTPUT_DATA{$o_file}{x_data} = [ @x_data ];
			}

		}
	if ($input->{'pgraphs'} eq 'all' || $input->{'print_risklevels'} == 1)
		{
		++$graph_cnt;
		print $graph_cnt.". ";
		my $o_file = 'Group Health Risk';
		push @sheet_list, $o_file;

		my ($lparm, $mparm, $hparm, $vparm, $b4_basis);
		$b4_basis = $PARMS{'low'} + $PARMS{'moderate'} + $PARMS{'medium'} + $PARMS{'high'};
		if( $b4_basis )
			{
			$lparm = (int($PARMS{'low'}/$b4_basis * 100));
			$mparm = (int($PARMS{'moderate'}/$b4_basis * 100));
			$hparm = (int($PARMS{'medium'}/$b4_basis * 100));
			$vparm = (int($PARMS{'high'}/$b4_basis * 100));

			if ($hparm > 33 || $vparm > 33 || $vparm+$hparm > 50)
				{
				$OUTPUT_DATA{$o_file}{message}{level}=  'above target';
				}
			else
				{
				$OUTPUT_DATA{$o_file}{message}{level}=  'at target';
				}

			my @g_data = (
				["Low Risk", "Moderate Risk", "High Risk", "Very High Risk"],
				[$lparm,$mparm,$hparm,$vparm]
				);
			my @x_data = (
				["Low Risk", "Moderate Risk", "High Risk", "Very High Risk"],
				[$PARMS{'low'},$PARMS{'moderate'},$PARMS{'medium'},$PARMS{'high'}]
				);

			my $j=0;
			foreach (@{$g_data[0]}) { $OUTPUT_DATA{$o_file}{computed}{$_}= $g_data[1][$j]; ++$j; }
			$j=0;
			foreach (@{$x_data[0]}) { $OUTPUT_DATA{$o_file}{raw}{$_}= $x_data[1][$j]; ++$j; }
			$OUTPUT_DATA{$o_file}{raw}{total}=  $b4_basis;
			$OUTPUT_DATA{$o_file}{title} = 'Group Health Risk';
			$OUTPUT_DATA{$o_file}{label} = 'Current health risk levels';
			$OUTPUT_DATA{$o_file}{label_x} = 'Risk Level';
			$OUTPUT_DATA{$o_file}{label_y} = '% Participants';
			$OUTPUT_DATA{$o_file}{g_data} = [ @g_data ];
			$OUTPUT_DATA{$o_file}{x_data} = [ @x_data ];
			}

		}

	if ($input->{'pgraphs'} eq 'all' || $input->{'print_smoking'} == 1){
		++$graph_cnt;
		print $graph_cnt.". ";
		#### Smoking Habits
		my $o_file = 'Group Smoking Habits';
		push @sheet_list, $o_file;

		my ($sm_never, $sm_quit, $sm_still, $sm_basis);

		if($sm_basis= ($PARMS{'sm_never'}+$PARMS{'sm_quit'}+$PARMS{'sm_still'}))
			{
			$sm_never=sprintf("%.2f",($PARMS{'sm_never'}/$sm_basis*100));
			$sm_quit=sprintf("%.2f",($PARMS{'sm_quit'}/$sm_basis*100));
			$sm_still=sprintf("%.2f",($PARMS{'sm_still'}/$sm_basis*100));

			if ($sm_still > 26) 	{ $OUTPUT_DATA{$o_file}{message}{level}=  'above target';}
			elsif ($sm_still < 22)	{ $OUTPUT_DATA{$o_file}{message}{level}=  'below target';}
			else			{ $OUTPUT_DATA{$o_file}{message}{level}=  'at target';}

			my @g_data=(
				["Non-smokers", "Ex-smokers", "Smokers"],
				[ $sm_never,       $sm_quit,   $sm_still]
				);
			my @x_data=(
				["Non-smokers", "Ex-smokers", "Smokers"],
				[ $PARMS{'sm_never'},$PARMS{'sm_quit'},$PARMS{'sm_still'}]
				);

			my $j=0;
			foreach (@{$g_data[0]}) { $OUTPUT_DATA{$o_file}{computed}{$_}= $g_data[1][$j]; ++$j; }
			my $j=0;
			foreach (@{$x_data[0]}) { $OUTPUT_DATA{$o_file}{raw}{$_}= $x_data[1][$j]; ++$j; }
			$OUTPUT_DATA{$o_file}{label_x} = 'Smoking status';
			$OUTPUT_DATA{$o_file}{label_y} = '% of Participants';
			$OUTPUT_DATA{$o_file}{raw}{total} = $sm_basis;
			$OUTPUT_DATA{$o_file}{raw}{target_high} = 26;
			$OUTPUT_DATA{$o_file}{raw}{target_low} = 22;
			$OUTPUT_DATA{$o_file}{title} = 'Group Smoking Habits';
			$OUTPUT_DATA{$o_file}{g_data} = [ @g_data ];
			$OUTPUT_DATA{$o_file}{x_data} = [ @x_data ];
			}

		}

	if ($input->{'pgraphs'} eq 'all' || $input->{'print_alcohol'} == 1){
		++$graph_cnt;
		print $graph_cnt.". ";
		#### Alcohol Habits
		my $o_file = 'Drinks in a Week';
		push @sheet_list, $o_file;

		my ($alc_good, $alc_over, $alc_obese, $alc_basis);

		if($alc_basis = $PARMS{'alc_low'} + $PARMS{'alc_medium'} + $PARMS{'alc_high'})
			{
			$alc_good = sprintf("%.2f",($PARMS{'alc_low'}/$alc_basis*100));
			$alc_over = sprintf("%.2f",($PARMS{'alc_medium'}/$alc_basis*100));
			$alc_obese = sprintf("%.2f",($PARMS{'alc_high'}/$alc_basis*100));

			if ($alc_obese + $alc_over > 8 ) 	{ $OUTPUT_DATA{$o_file}{message}{level}=  'above target'; }
			else 					{ $OUTPUT_DATA{$o_file}{message}{level}=  'at target'; }

			if ($PARMS{'sb_drinkdrive'}) 	{ $OUTPUT_DATA{$o_file}{raw}{'Drink and Drive'}=  $PARMS{'sb_drinkdrive'}; }

			my @g_data = (
				["Low", "Moderate", "High"],
				[$alc_good ,            $alc_over ,     $alc_obese]
				);
			my @x_data = (
				["Low", "Moderate", "High"],
				[$PARMS{'alc_low'} ,$PARMS{'alc_medium'} , $PARMS{'alc_high'}]
				);

			my $j=0;
			foreach (@{$g_data[0]}) { $OUTPUT_DATA{$o_file}{computed}{$_}= $g_data[1][$j]; ++$j; }
			my $j=0;
			foreach (@{$x_data[0]}) { $OUTPUT_DATA{$o_file}{raw}{$_}= $x_data[1][$j]; ++$j; }
			$OUTPUT_DATA{$o_file}{label_x} = 'Group Alcohol Use';
			$OUTPUT_DATA{$o_file}{label_y} = '% of Participants';
			$OUTPUT_DATA{$o_file}{raw}{total} = $alc_basis;
			$OUTPUT_DATA{$o_file}{raw}{target_high} = 8;
			$OUTPUT_DATA{$o_file}{raw}{target_low} = 0;
			$OUTPUT_DATA{$o_file}{title} = 'Drinks in a Week';
			$OUTPUT_DATA{$o_file}{g_data} = [ @g_data ];
			$OUTPUT_DATA{$o_file}{x_data} = [ @x_data ];
			}

		}
	if ($input->{'pgraphs'} eq 'all' || $input->{'print_weight'} == 1)
		{
		++$graph_cnt;
		print $graph_cnt.". ";
		####  Weight Status
		my $o_file = 'Group Weight';
		push @sheet_list, $o_file;

		my ($wt_good, $wt_under, $wt_over, $wt_obese, $wt_basis);

		if($wt_basis = $PARMS{'wt_under'} + $PARMS{'wt_good'} + $PARMS{'wt_over'} + $PARMS{'wt_obese'})
			{
			$wt_under = sprintf("%.2f",($PARMS{'wt_under'}/$wt_basis*100));
			$wt_good = sprintf("%.2f",($PARMS{'wt_good'}/$wt_basis*100));
			$wt_over = sprintf("%.2f",($PARMS{'wt_over'}/$wt_basis*100));
			$wt_obese = sprintf("%.2f",($PARMS{'wt_obese'}/$wt_basis*100));

			if( $wt_obese >= 20 ||
				$wt_obese + $wt_over >= 40 )	{  $OUTPUT_DATA{$o_file}{message}{level}=  'above target'; }
			else					{  $OUTPUT_DATA{$o_file}{message}{level}=  'on target'; }

			my @g_data = (
				["Under Weight", "Healthy Weight", "Overweight", "Obese"],
				[$wt_under,         $wt_good ,     $wt_over ,   $wt_obese]
				);
			my @x_data = (
				["Under Weight", "Healthy Weight", "Overweight", "Obese"],
				[$PARMS{'wt_under'},$PARMS{'wt_good'} , $PARMS{'wt_over'} , $PARMS{'wt_obese'}]
				);
			my $j=0;
			foreach (@{$g_data[0]}) { $OUTPUT_DATA{$o_file}{computed}{$_}= $g_data[1][$j]; ++$j; }
			my $j=0;
			foreach (@{$x_data[0]}) { $OUTPUT_DATA{$o_file}{raw}{$_}= $x_data[1][$j]; ++$j; }
			$OUTPUT_DATA{$o_file}{label_x} = 'Weight classification';
			$OUTPUT_DATA{$o_file}{label_y} = '% of Participants';
			$OUTPUT_DATA{$o_file}{raw}{total} = $wt_basis;
			$OUTPUT_DATA{$o_file}{raw}{target_high} = 20;
			$OUTPUT_DATA{$o_file}{raw}{target_low} = 0;
			$OUTPUT_DATA{$o_file}{title} = 'Group Weight';
			$OUTPUT_DATA{$o_file}{g_data} = [ @g_data ];
			$OUTPUT_DATA{$o_file}{x_data} = [ @x_data ];
			}

		}
	if ($input->{'pgraphs'} eq 'all' || $input->{'print_mammogram'} == 1)
		{
		++$graph_cnt;
		print $graph_cnt.". ";
		####  Mammogram
		my $o_file = 'Group Mammogram (females 40 and older)';
		push @sheet_list, $o_file;

		my ($mammo_good, $mammo_med, $mammo_bad, $mammo_basis);

		if($mammo_basis = $PARMS{'mammo_good'} + $PARMS{'mammo_med'} + $PARMS{'mammo_bad'})
			{
			$mammo_good = sprintf("%.2f",($PARMS{'mammo_good'}/$mammo_basis*100));
			$mammo_med = sprintf("%.2f",($PARMS{'mammo_med'}/$mammo_basis*100));
			$mammo_bad = sprintf("%.2f",($PARMS{'mammo_bad'}/$mammo_basis*100));

			if ($mammo_bad + $mammo_med > 10)	{ $OUTPUT_DATA{$o_file}{message}{level}=  'above target'; }
			else					{ $OUTPUT_DATA{$o_file}{message}{level}=  'at target';    }

			my @g_data = (
				["1 year or less", "1 to 3 years", "Over 3 years"],
				[$mammo_good ,       $mammo_med ,    $mammo_bad]
				);
			my @x_data = (
				["1 year or less", "1 to 3 years", "Over 3 years"],
				[$PARMS{'mammo_good'} ,$PARMS{'mammo_med'}, $PARMS{'mammo_bad'}]
				);
			my $j=0;
			foreach (@{$g_data[0]}) { $OUTPUT_DATA{$o_file}{computed}{$_}= $g_data[1][$j]; ++$j; }
			my $j=0;
			foreach (@{$x_data[0]}) { $OUTPUT_DATA{$o_file}{raw}{$_}= $x_data[1][$j]; ++$j; }
			$OUTPUT_DATA{$o_file}{label_x} = 'Time since last mammogram';
			$OUTPUT_DATA{$o_file}{label_y} = '% of Participants';
			$OUTPUT_DATA{$o_file}{raw}{total} = $mammo_basis;
			$OUTPUT_DATA{$o_file}{raw}{target_high} = 10;
			$OUTPUT_DATA{$o_file}{raw}{target_low} = 0;
			$OUTPUT_DATA{$o_file}{title} = 'Group Mammogram (females 40 and older)';
			$OUTPUT_DATA{$o_file}{g_data} = [ @g_data ];
			$OUTPUT_DATA{$o_file}{x_data} = [ @x_data ];
			}

		}

	if ($input->{'pgraphs'} eq 'all' || $input->{'print_pap'} == 1)
		{
		++$graph_cnt;
		print $graph_cnt.". ";
		#### Pap Exams
		my $o_file = 'Group Pap Smear (all females)';
		push @sheet_list, $o_file;

		my ($pap_good, $pap_med, $pap_bad, $pap_basis);

		if ($pap_basis = $PARMS{'pap_good'} + $PARMS{'pap_med'} + $PARMS{'pap_bad'})
			{
			$pap_good = sprintf("%.2f",($PARMS{'pap_good'}/$pap_basis*100));
			$pap_med = sprintf("%.2f",($PARMS{'pap_med'}/$pap_basis*100));
			$pap_bad = sprintf("%.2f",($PARMS{'pap_bad'}/$pap_basis*100));

			if ($pap_bad + $pap_med > 10)	{ $OUTPUT_DATA{$o_file}{message}{level}=  'above target'; }
			else				{ $OUTPUT_DATA{$o_file}{message}{level}=  'at target';   }

			my @g_data = (
				["1 year or less", "1 to 3 years", "Over 3 years"],
				[$pap_good ,         $pap_med ,       $pap_bad]
				);
			my @x_data = (
				["1 year or less", "1 to 3 years", "Over 3 years"],
				[$PARMS{'pap_good'} ,$PARMS{'pap_med'} ,$PARMS{'pap_bad'}]
				);
			my $j=0;
			foreach (@{$g_data[0]}) { $OUTPUT_DATA{$o_file}{computed}{$_}= $g_data[1][$j]; ++$j; }
			my $j=0;
			foreach (@{$x_data[0]}) { $OUTPUT_DATA{$o_file}{raw}{$_}= $x_data[1][$j]; ++$j; }
			$OUTPUT_DATA{$o_file}{label_x} = 'Time since last Pap';
			$OUTPUT_DATA{$o_file}{label_y} = '% of Participants';
			$OUTPUT_DATA{$o_file}{raw}{total} = $pap_basis;
			$OUTPUT_DATA{$o_file}{raw}{target_high} = 10;
			$OUTPUT_DATA{$o_file}{raw}{target_low} = 0;
			$OUTPUT_DATA{$o_file}{title} = 'Group Pap Smear (all females)';
			$OUTPUT_DATA{$o_file}{g_data} = [ @g_data ];
			$OUTPUT_DATA{$o_file}{x_data} = [ @x_data ];
			}

		}

	if ($input->{'pgraphs'} eq 'all' || $input->{'print_breast_self'} == 1)
		{
		++$graph_cnt;
		print $graph_cnt.". ";
		#### breast self exam
		my $o_file = 'Self Breast Exam (all females)';
		push @sheet_list, $o_file;

		my ($self_breast_good, $self_breast_med, $self_breast_bad, $self_breast_basis);

		if ($self_breast_basis = $PARMS{'self_breast_good'} + $PARMS{'self_breast_med'} + $PARMS{'self_breast_bad'})
			{
			$self_breast_good = sprintf("%.2f",($PARMS{'self_breast_good'}/$self_breast_basis*100));
			$self_breast_med = sprintf("%.2f",($PARMS{'self_breast_med'}/$self_breast_basis*100));
			$self_breast_bad = sprintf("%.2f",($PARMS{'self_breast_bad'}/$self_breast_basis*100));

			if ($self_breast_bad + $self_breast_med > 10)	{ $OUTPUT_DATA{$o_file}{message}{level}=  'above target'; }
			else						{ $OUTPUT_DATA{$o_file}{message}{level}=  'at target';   }

			my @g_data = (
				["monthly", "every few months", "rarely or never"],
				[$self_breast_good ,         $self_breast_med ,       $self_breast_bad]
				);
			my @x_data = (
				["monthly", "every few months", "rarely or never"],
				[$PARMS{'self_breast_good'} , $PARMS{'self_breast_med'}, $PARMS{'self_breast_bad'}]
				);
			my $j=0;
			foreach (@{$g_data[0]}) { $OUTPUT_DATA{$o_file}{computed}{$_}= $g_data[1][$j]; ++$j; }
			my $j=0;
			foreach (@{$x_data[0]}) { $OUTPUT_DATA{$o_file}{raw}{$_}= $x_data[1][$j]; ++$j; }
			$OUTPUT_DATA{$o_file}{label_x} = 'Frequency of Self Breast Exam';
			$OUTPUT_DATA{$o_file}{label_y} = '% of Participants';
			$OUTPUT_DATA{$o_file}{raw}{total} = $self_breast_basis;
			$OUTPUT_DATA{$o_file}{raw}{target_high} = 10;
			$OUTPUT_DATA{$o_file}{raw}{target_low} = 0;
			$OUTPUT_DATA{$o_file}{title} = 'Self Breast Exam (all females)';
			$OUTPUT_DATA{$o_file}{g_data} = [ @g_data ];
			$OUTPUT_DATA{$o_file}{x_data} = [ @x_data ];
			}

		}

	if ($input->{'pgraphs'} eq 'all' || $input->{'print_prostate'} == 1)
		{
		++$graph_cnt;
		print $graph_cnt.". ";
		####  Male Prostate
		my $o_file = 'Group Prostate Exams (males 40 and older)';
		push @sheet_list, $o_file;

		my ($male_good, $male_med, $male_bad, $male_prostate_basis);

		if ($male_prostate_basis = $PARMS{'male_prostate_good'} + $PARMS{'male_prostate_med'} + $PARMS{'male_prostate_bad'})
			{
			$male_good = sprintf("%.2f",($PARMS{'male_prostate_good'}/$male_prostate_basis*100));
			$male_med = sprintf("%.2f",($PARMS{'male_prostate_med'}/$male_prostate_basis*100));
			$male_bad = sprintf("%.2f",($PARMS{'male_prostate_bad'}/$male_prostate_basis*100));

			if ($male_bad + $male_med > 10)	{ $OUTPUT_DATA{$o_file}{message}{level}=  'above target'; }
			else				{ $OUTPUT_DATA{$o_file}{message}{level}=  'at target';   }

			my @g_data = (
				["1 year or less", "1 to 3 years", "Over 3 years"],
				[$male_good ,       $male_med ,    $male_bad]
				);
			my @x_data = (
				["1 year or less", "1 to 3 years", "Over 3 years"],
				[$PARMS{'male_prostate_good'} ,$PARMS{'male_prostate_med'},$PARMS{'male_prostate_bad'}]
				);
			my $j=0;
			foreach (@{$g_data[0]}) { $OUTPUT_DATA{$o_file}{computed}{$_}= $g_data[1][$j]; ++$j; }
			my $j=0;
			foreach (@{$x_data[0]}) { $OUTPUT_DATA{$o_file}{raw}{$_}= $x_data[1][$j]; ++$j; }
			$OUTPUT_DATA{$o_file}{label_x} = 'Time since last prostate exam';
			$OUTPUT_DATA{$o_file}{label_y} = '% of Participants';
			$OUTPUT_DATA{$o_file}{raw}{total} = $male_prostate_basis;
			$OUTPUT_DATA{$o_file}{raw}{target_high} = 10;
			$OUTPUT_DATA{$o_file}{raw}{target_low} = 0;
			$OUTPUT_DATA{$o_file}{title} = 'Group Prostate Exams (males 40 and older)';
			$OUTPUT_DATA{$o_file}{g_data} = [ @g_data ];
			$OUTPUT_DATA{$o_file}{x_data} = [ @x_data ];
			}

		}

	if ($input->{'pgraphs'} eq 'all' || $input->{'print_exercise'} == 1)
		{
		++$graph_cnt;
		print $graph_cnt.". ";
		#### Exercise Habits
		my $o_file = 'Group Exercise Habits';
		push @sheet_list, $o_file;

		my ($exer_basis, $exer_good, $exer_some, $exer_none);

		if($exer_basis = $PARMS{'exer_good'} + $PARMS{'exer_some'} + $PARMS{'exer_none'})
			{
			$exer_good = sprintf("%.2f",($PARMS{'exer_good'}/$exer_basis*100));
			$exer_some = sprintf("%.2f",($PARMS{'exer_some'}/$exer_basis*100));
			$exer_none = sprintf("%.2f",($PARMS{'exer_none'}/$exer_basis*100));

			my @g_data = (
				["3+/week", "1-2/week", "Sedentary"],
				[$exer_good ,$exer_some ,$exer_none]
				);
			my @x_data = (
				["3+/week", "1-2/week", "Sedentary"],
				[$PARMS{'exer_good'} ,$PARMS{'exer_some'},$PARMS{'exer_none'}]
				);
			my $j=0;
			foreach (@{$g_data[0]}) { $OUTPUT_DATA{$o_file}{computed}{$_}= $g_data[1][$j]; ++$j; }
			my $j=0;
			foreach (@{$x_data[0]}) { $OUTPUT_DATA{$o_file}{raw}{$_}= $x_data[1][$j]; ++$j; }
			$OUTPUT_DATA{$o_file}{label_x} = 'Exercise frequency';
			$OUTPUT_DATA{$o_file}{label_y} = '% of Participants';
			$OUTPUT_DATA{$o_file}{raw}{total} = $exer_basis;
			$OUTPUT_DATA{$o_file}{title} = 'Group Exercise Habits';
			$OUTPUT_DATA{$o_file}{g_data} = [ @g_data ];
			$OUTPUT_DATA{$o_file}{x_data} = [ @x_data ];
			}
		}

	if ($input->{'pgraphs'} eq 'all' || $input->{'print_seatbelts'} == 1)
		{
		++$graph_cnt;
		print $graph_cnt.". ";
		#### Seat Belt Habits
		my $o_file = 'Group Seatbelt Use';
		push @sheet_list, $o_file;

		my ($sb_basis, $sb_never, $sb_some, $sb_seldom, $sb_usually, $sb_always);

		if($sb_basis = $PARMS{'sb_never'} + $PARMS{'sb_some'} + $PARMS{'sb_seldom'} + $PARMS{'sb_usually'} + $PARMS{'sb_always'})
			{
			$sb_never = sprintf("%.2f",($PARMS{'sb_never'}/$sb_basis*100));
			$sb_some = sprintf("%.2f",($PARMS{'sb_some'}/$sb_basis*100));
			$sb_seldom = sprintf("%.2f",($PARMS{'sb_seldom'}/$sb_basis*100));
			$sb_usually = sprintf("%.2f",($PARMS{'sb_usually'}/$sb_basis*100));
			$sb_always = sprintf("%.2f",($PARMS{'sb_always'}/$sb_basis*100));

			if ($sb_usually + $sb_always >= 70)	{ $OUTPUT_DATA{$o_file}{message}{level}=  'at target'; }
			else					{ $OUTPUT_DATA{$o_file}{message}{level}=  'below target';   }

			my @g_data = (
				["Always",    "81-99%",    "41-80%", "1-40%",    "Never"],
				[$sb_always ,$sb_usually ,$sb_some, $sb_seldom, $sb_never]
				);
			my @x_data = (
				["Always",    "81-99%",    "41-80%", "1-40%",    "Never"],
				[$PARMS{'sb_always'} ,$PARMS{'sb_usually'} ,$PARMS{'sb_some'}, $PARMS{'sb_seldom'}, $PARMS{'sb_never'}]
				);
			my $j=0;
			foreach (@{$g_data[0]}) { $OUTPUT_DATA{$o_file}{computed}{$_}= $g_data[1][$j]; ++$j; }
			my $j=0;
			foreach (@{$x_data[0]}) { $OUTPUT_DATA{$o_file}{raw}{$_}= $x_data[1][$j]; ++$j; }
			$OUTPUT_DATA{$o_file}{label_x} = '% of trips seatbelts used';
			$OUTPUT_DATA{$o_file}{label_y} = '% of Participants';
			$OUTPUT_DATA{$o_file}{raw}{total} = $sb_basis;
			$OUTPUT_DATA{$o_file}{raw}{target_high} = 100;
			$OUTPUT_DATA{$o_file}{raw}{target_low} = 70;
			$OUTPUT_DATA{$o_file}{title} = 'Group Seatbelt Use';
			$OUTPUT_DATA{$o_file}{g_data} = [ @g_data ];
			$OUTPUT_DATA{$o_file}{x_data} = [ @x_data ];
			}

		}

	if ($input->{'pgraphs'} eq 'all' || $input->{'print_cholesterol'} == 1)
		{
		++$graph_cnt;
		print $graph_cnt.". ";
		##### Cholesterol Status
		my $o_file = 'Group Cholesterol';
		push @sheet_list, $o_file;

		my ($chol_basis, $chol_high, $chol_med, $chol_low, $chol_unknown);

		if($chol_basis = $PARMS{'chol_high'} + $PARMS{'chol_med'} + $PARMS{'chol_low'} + $PARMS{'chol_unknown'})
			{
			$chol_high = sprintf("%.2f",($PARMS{'chol_high'}/$chol_basis*100));
			$chol_med = sprintf("%.2f",($PARMS{'chol_med'}/$chol_basis*100));
			$chol_low = sprintf("%.2f",($PARMS{'chol_low'}/$chol_basis*100));
			$chol_unknown = sprintf("%.2f",($PARMS{'chol_unknown'}/$chol_basis*100));

			if ($chol_high > 21)	{ $OUTPUT_DATA{$o_file}{message}{level}=  'above target'; }
			else			{ $OUTPUT_DATA{$o_file}{message}{level}=  'at target';   }

			my %chol_lab = (
				low	=> "Under " . CHOL_MARGINAL,
				med	=> CHOL_MARGINAL . " to " . CHOL_HIGH,
				high	=> "Over " . CHOL_HIGH
				);

			my @g_data = (
				[$chol_lab{low}, $chol_lab{med}, $chol_lab{high}, "unknown"],
				[$chol_low ,$chol_med ,$chol_high, $chol_unknown]
				);
			my @x_data = (
				[$chol_lab{low}, $chol_lab{med}, $chol_lab{high}, "unknown"],
				[$PARMS{'chol_low'} ,$PARMS{'chol_med'} ,$PARMS{'chol_high'}, $PARMS{'chol_unknown'}]
				);
			my $j=0;
			foreach (@{$g_data[0]}) { $OUTPUT_DATA{$o_file}{computed}{$_}= $g_data[1][$j]; ++$j; }
			my $j=0;
			foreach (@{$x_data[0]}) { $OUTPUT_DATA{$o_file}{raw}{$_}= $x_data[1][$j]; ++$j; }
			$OUTPUT_DATA{$o_file}{label_x} = 'Cholesterol levels';
			$OUTPUT_DATA{$o_file}{label_y} = '% of Participants';
			$OUTPUT_DATA{$o_file}{raw}{total} = $chol_basis;
			$OUTPUT_DATA{$o_file}{raw}{target_high} = 21;
			$OUTPUT_DATA{$o_file}{raw}{target_low} = 0;
			$OUTPUT_DATA{$o_file}{title} = 'Group Cholesterol';
			$OUTPUT_DATA{$o_file}{g_data} = [ @g_data ];
			$OUTPUT_DATA{$o_file}{x_data} = [ @x_data ];
			}

		}

	if ($input->{'pgraphs'} eq 'all' || $input->{'print_bloodpressure'} == 1)
		{
		++$graph_cnt;
		print $graph_cnt.". ";
		#### Blood Pressure
		my $o_file = 'Group Blood Pressure';
		push @sheet_list, $o_file;

		my ($bp_basis, $bp_high, $bp_med, $bp_low, $bp_unknown);

		if($bp_basis = $PARMS{'bp_high'} + $PARMS{'bp_med'} + $PARMS{'bp_low'} + $PARMS{'bp_unknown'})
			{
			$bp_high = sprintf("%.2f",($PARMS{'bp_high'}/$bp_basis*100));
			$bp_med = sprintf("%.2f",($PARMS{'bp_med'}/$bp_basis*100));
			$bp_low = sprintf("%.2f",($PARMS{'bp_low'}/$bp_basis*100));
			$bp_unknown = sprintf("%.2f",($PARMS{'bp_unknown'}/$bp_basis*100));

			if ($bp_med + $bp_high > 28)	{ $OUTPUT_DATA{$o_file}{message}{level}=  'above target'; }
			else				{ $OUTPUT_DATA{$o_file}{message}{level}=  'at target';   }

			my %bp_lab = (
				low	=> "Under " . BP_MARGINAL_SYSTOLIC . "/" . BP_MARGINAL_DIASTOLIC,
				med	=> BP_MARGINAL_SYSTOLIC . "/" . BP_MARGINAL_DIASTOLIC . " to " . BP_HIGH_SYSTOLIC . "/" . BP_HIGH_DIASTOLIC,
				high	=> "Over " . BP_HIGH_SYSTOLIC . "/" . BP_HIGH_DIASTOLIC
				);

			my @g_data = (
				[$bp_lab{low}, $bp_lab{med}, $bp_lab{high}, "unknown"],
				[$bp_low ,$bp_med ,$bp_high, $bp_unknown]
				);
			my @x_data = (
				[$bp_lab{low}, $bp_lab{med}, $bp_lab{high}, "unknown", "bp high, on medication", "bp high, not on medication"],
				[$PARMS{'bp_low'} ,$PARMS{'bp_med'} ,$PARMS{'bp_high'}, $PARMS{'bp_unknown'}, $PARMS->{'bp_meds'}, $PARMS->{'bp_no_meds'}]
				);
			my $j=0;
			foreach (@{$g_data[0]}) { $OUTPUT_DATA{$o_file}{computed}{$_}= $g_data[1][$j]; ++$j; }
			my $j=0;
			foreach (@{$x_data[0]}) { $OUTPUT_DATA{$o_file}{raw}{$_}= $x_data[1][$j]; ++$j; }
			$OUTPUT_DATA{$o_file}{label_x} = 'Blood pressure levels';
			$OUTPUT_DATA{$o_file}{label_y} = '% of Participants';
			$OUTPUT_DATA{$o_file}{raw}{total} = $bp_basis;
			$OUTPUT_DATA{$o_file}{raw}{target_high} = 28;
			$OUTPUT_DATA{$o_file}{raw}{target_low} = 0;
			$OUTPUT_DATA{$o_file}{title} = 'Group Blood Pressure';
			$OUTPUT_DATA{$o_file}{g_data} = [ @g_data ];
			$OUTPUT_DATA{$o_file}{x_data} = [ @x_data ];
			}

		}

	if ($input->{'pgraphs'} eq 'all' || $input->{'print_diabetes'} == 1){
		++$graph_cnt;
		print $graph_cnt.". ";
		####  Diabetes Assessment Risk levels
		my $o_file = 'Diabetes Assessment Results';
		push @sheet_list, $o_file;

		my ($dlparm, $dmparm, $dhparm, $diab_basis);

		$diab_basis = $PARMS{diabetes_low} + $PARMS{diabetes_med} + $PARMS{diabetes_high};

		if ( $b16_basis )
			{
			$dlparm = sprintf("%.2f",($PARMS{diabetes_low}/$diab_basis * 100));
			$dmparm = sprintf("%.2f",($PARMS{diabetes_med}/$diab_basis * 100));
			$dhparm = sprintf("%.2f",($PARMS{diabetes_high}/$diab_basis * 100));

			my @g_data = (
				["Low Risk - $dlparm%", "Moderate Risk - $dmparm%", "High Risk - $dhparm%"],
				[$dlparm,                  $dmparm,                       $dhparm]
				);
			my @x_data = (
				["Low Risk", "Moderate Risk", "High Risk"],
				[$PARMS{diabetes_low},$PARMS{diabetes_med}, $PARMS{diabetes_high}]
				);

			my $j=0;
			foreach (@{$g_data[0]}) { $OUTPUT_DATA{$o_file}{computed}{$_}= $g_data[1][$j]; ++$j; }
			my $j=0;
			foreach (@{$x_data[0]}) { $OUTPUT_DATA{$o_file}{raw}{$_}= $x_data[1][$j]; ++$j; }
			$OUTPUT_DATA{$o_file}{label} = 'Group Risk Levels';
			$OUTPUT_DATA{$o_file}{raw}{total} = $diab_basis;
			$OUTPUT_DATA{$o_file}{title} = 'Diabetes Assessment Results';
			$OUTPUT_DATA{$o_file}{g_data} = [ @g_data ];
			$OUTPUT_DATA{$o_file}{x_data} = [ @x_data ];
			}

		}

	if ($input->{'pgraphs'} eq 'all' || $input->{'print_cardiac'} == 1)
		{
		++$graph_cnt;
		print $graph_cnt.". ";
		####  Cardiac Assessment Risk levels
		my $o_file = 'Cardiac Assessment Results';
		push @sheet_list, $o_file;

		my ($clparm, $cmedparm, $cmodparm, $chparm, $b17_basis);

		$b17_basis = $PARMS{cardiac_low} + $PARMS{cardiac_med} + $PARMS{cardiac_mod} + $PARMS{cardiac_high};

		if ( $PARMS{CRC_cnt} > 0 )
			{
			$clparm = sprintf("%.2f",($PARMS{cardiac_low}/$b17_basis * 100));
			$cmedparm = sprintf("%.2f",($PARMS{cardiac_med}/$b17_basis * 100));
			$cmodparm = sprintf("%.2f",($PARMS{cardiac_mod}/$b17_basis * 100));
			$chparm = sprintf("%.2f",($PARMS{cardiac_high}/$b17_basis * 100));

 			my $start_angle = 0;
 			$start_angle = -85 if ($clparm > 1);

			my @g_data = (
				["Low Risk - $clparm%", "Moderate Risk - $cmodparm%", "High Risk - $cmedparm%", "Very High Risk - $chparm%"],
				[$clparm,$cmodparm,$cmedparm,$chparm]
				);
			my @x_data = (
				["Low Risk", "Moderate Risk", "High Risk", "Very High Risk"],
				[$PARMS{cardiac_low},$PARMS{cardiac_mod},$PARMS{cardiac_med},$PARMS{cardiac_high}]
				);

			my $j=0;
			foreach (@{$g_data[0]}) { $OUTPUT_DATA{$o_file}{computed}{$_}= $g_data[1][$j]; ++$j; }
			my $j=0;
			foreach (@{$x_data[0]}) { $OUTPUT_DATA{$o_file}{raw}{$_}= $x_data[1][$j]; ++$j; }
			$OUTPUT_DATA{$o_file}{label} = 'Group Risk Levels';
			$OUTPUT_DATA{$o_file}{raw}{total} = $b17_basis;
			$OUTPUT_DATA{$o_file}{title} = 'Cardiac Assessment Results';
			$OUTPUT_DATA{$o_file}{g_data} = [ @g_data ];
			$OUTPUT_DATA{$o_file}{x_data} = [ @x_data ];
			}

		}

	if ($input->{'pgraphs'} eq 'all' || $input->{'print_fitness'} == 1)
		{
		++$graph_cnt;
		print $graph_cnt.". ";
		####  Fitness assessment results
		my $o_file = 'Fitness Assessment Results';
		push @sheet_list, $o_file;

		if ( $PARMS{FIT_cnt} > 0 )
			{
			my $fit_step_basis = ($PARMS{'fit_step_low'}+$PARMS{'fit_step_med'}+$PARMS{'fit_step_high'});
			my $fit_sits_basis = ($PARMS{'fit_sits_low'}+$PARMS{'fit_sits_med'}+$PARMS{'fit_sits_high'});
			my $fit_push_basis = ($PARMS{'fit_push_low'}+$PARMS{'fit_push_med'}+$PARMS{'fit_push_high'});
			my $fit_flex_basis = ($PARMS{'fit_flex_low'}+$PARMS{'fit_flex_med'}+$PARMS{'fit_flex_high'});


			my @g_data = (
			    ["Pulse",                                           "Sit-ups",                                 "Push-ups",                            "Flexibility"],
			    [(int($PARMS{'fit_step_low'}/$fit_step_basis*100)), (int($PARMS{'fit_sits_low'}/$fit_sits_basis*100)), (int($PARMS{'fit_push_low'}/$fit_push_basis*100)), (int($PARMS{'fit_flex_low'}/$fit_flex_basis*100))],
			    [(int($PARMS{'fit_step_med'}/$fit_step_basis*100)), (int($PARMS{'fit_sits_med'}/$fit_sits_basis*100)), (int($PARMS{'fit_push_med'}/$fit_push_basis*100)), (int($PARMS{'fit_flex_med'}/$fit_flex_basis*100))],
			    [(int($PARMS{'fit_step_high'}/$fit_step_basis*100)), (int($PARMS{'fit_sits_high'}/$fit_sits_basis*100)), (int($PARMS{'fit_push_high'}/$fit_push_basis*100)), (int($PARMS{'fit_flex_high'}/$fit_flex_basis*100))]
			  );
			my @x_data = (
			    ["Pulse",                      "Sit-ups",              "Push-ups",                 "Flexibility"],
			    [$PARMS{'fit_step_low'} , $PARMS{'fit_sits_low'} , $PARMS{'fit_push_low'} , $PARMS{'fit_flex_low'} ],
			    [$PARMS{'fit_step_med'} , $PARMS{'fit_sits_med'} , $PARMS{'fit_push_med'} , $PARMS{'fit_flex_med'} ],
			    [$PARMS{'fit_step_high'}, $PARMS{'fit_sits_high'}, $PARMS{'fit_push_high'}, $PARMS{'fit_flex_high'}]
			  );
			my $j=0;
			foreach (@{$g_data[0]}) { $OUTPUT_DATA{$o_file}{computed}{key}{$_}{'Low Fitness'}= $g_data[1][$j];$OUTPUT_DATA{$o_file}{computed}{key}{$_}{'Medium Fitness'}= $g_data[2][$j];$OUTPUT_DATA{$o_file}{computed}{key}{$_}{'High Fitness'}= $g_data[3][$j]; ++$j; }
			my $j=0;
			foreach (@{$x_data[0]}) { $OUTPUT_DATA{$o_file}{raw}{key}{$_}{'Low Fitness'}= $x_data[1][$j];$OUTPUT_DATA{$o_file}{raw}{key}{$_}{'Medium Fitness'}= $x_data[2][$j];$OUTPUT_DATA{$o_file}{raw}{key}{$_}{'High Fitness'}= $x_data[3][$j]; ++$j; }
			$OUTPUT_DATA{$o_file}{label_x} = 'Fitness Levels';
			$OUTPUT_DATA{$o_file}{label_y} = '% of Participants';
			$OUTPUT_DATA{$o_file}{raw}{key}{"Pulse"}{total} = 		$fit_step_basis;
			$OUTPUT_DATA{$o_file}{raw}{key}{"Sit-ups"}{total} = 		$fit_sits_basis;
			$OUTPUT_DATA{$o_file}{raw}{key}{"Push-ups"}{total} = 	$fit_push_basis;
			$OUTPUT_DATA{$o_file}{raw}{key}{"Flexibility"}{total} = 	$fit_flex_basis;
			$OUTPUT_DATA{$o_file}{title} = 'Fitness Assessment Results';
			my @subtitle = ( 'Low', 'Medium', 'High');
			$OUTPUT_DATA{$o_file}{label_y_sub} = [ @subtitle ];
			$OUTPUT_DATA{$o_file}{g_data} = [ @g_data ];
			$OUTPUT_DATA{$o_file}{x_data} = [ @x_data ];
			}

		}

	if ($input->{'pgraphs'} eq 'all' || $input->{'print_wellbeing'} == 1)
		{
		++$graph_cnt;
		print $graph_cnt.". ";
		####  General Well-being assessment results
		my $o_file = 'General Well-being Assessment Results';
		push @sheet_list, $o_file;

		if ( $PARMS{GWB_cnt} > 0 )
			{
			my $gwb_stress_basis 		= ($PARMS{'gwb_stress_low'}+$PARMS{'gwb_stress_med'}+$PARMS{'gwb_stress_high'});
			my $gwb_depression_basis 	= ($PARMS{'gwb_depression_low'}+$PARMS{'gwb_depression_med'}+$PARMS{'gwb_depression_high'});
			my $gwb_health_basis 		= ($PARMS{'gwb_health_low'}+$PARMS{'gwb_health_med'}+$PARMS{'gwb_health_high'});
			my $gwb_control_basis 		= ($PARMS{'gwb_control_low'}+$PARMS{'gwb_control_med'}+$PARMS{'gwb_control_high'});
			my $gwb_being_basis 		= ($PARMS{'gwb_being_low'}+$PARMS{'gwb_being_med'}+$PARMS{'gwb_being_high'});
			my $gwb_vitality_basis 		= ($PARMS{'gwb_vitality_low'}+$PARMS{'gwb_vitality_med'}+$PARMS{'gwb_vitality_high'});


			my @g_data = (
			    ["Stress",                                           "Depression",                                                     "Self-Control",                                                "Well-being",                                    "Vitality",                                                 "Health"],
			    [(int($PARMS{'gwb_stress_low'}/$gwb_stress_basis*100)), (int($PARMS{'gwb_depression_low'}/$gwb_depression_basis*100)), (int($PARMS{'gwb_control_high'}/$gwb_control_basis*100)), (int($PARMS{'gwb_being_high'}/$gwb_being_basis*100)), (int($PARMS{'gwb_vitality_high'}/$gwb_vitality_basis*100)), (int($PARMS{'gwb_health_high'}/$gwb_health_basis*100))],
			    [(int($PARMS{'gwb_stress_med'}/$gwb_stress_basis*100)), (int($PARMS{'gwb_depression_med'}/$gwb_depression_basis*100)), (int($PARMS{'gwb_control_med'}/$gwb_control_basis*100)), (int($PARMS{'gwb_being_med'}/$gwb_being_basis*100)), (int($PARMS{'gwb_vitality_med'}/$gwb_vitality_basis*100)), (int($PARMS{'gwb_health_med'}/$gwb_health_basis*100))],
			    [(int($PARMS{'gwb_stress_high'}/$gwb_stress_basis*100)), (int($PARMS{'gwb_depression_high'}/$gwb_depression_basis*100)), (int($PARMS{'gwb_control_low'}/$gwb_control_basis*100)), (int($PARMS{'gwb_being_low'}/$gwb_being_basis*100)), (int($PARMS{'gwb_vitality_low'}/$gwb_vitality_basis*100)), (int($PARMS{'gwb_health_low'}/$gwb_health_basis*100))]
			  );
			my @x_data = (
			    ["Stress", "Depression", "Self-Control","Well-being","Vitality","Health"],
			    [$PARMS{'gwb_stress_low'} , $PARMS{'gwb_depression_low'} , $PARMS{'gwb_control_high'}, $PARMS{'gwb_being_high'}, $PARMS{'gwb_vitality_high'}, $PARMS{'gwb_health_high'}],
			    [$PARMS{'gwb_stress_med'} , $PARMS{'gwb_depression_med'} , $PARMS{'gwb_control_med'} , $PARMS{'gwb_being_med'} , $PARMS{'gwb_vitality_med'} , $PARMS{'gwb_health_med'} ],
			    [$PARMS{'gwb_stress_high'}, $PARMS{'gwb_depression_high'}, $PARMS{'gwb_control_low'} , $PARMS{'gwb_being_low'} , $PARMS{'gwb_vitality_low'} , $PARMS{'gwb_health_low'} ]
			  );
			my $j=0;
			foreach (@{$g_data[0]}) { $OUTPUT_DATA{$o_file}{computed}{key}{$_}{'Good'}= $g_data[1][$j];$OUTPUT_DATA{$o_file}{computed}{key}{$_}{'Medium'}= $g_data[2][$j];$OUTPUT_DATA{$o_file}{computed}{key}{$_}{'Poor'}= $g_data[3][$j]; ++$j; }
			my $j=0;
			foreach (@{$x_data[0]}) { $OUTPUT_DATA{$o_file}{raw}{key}{$_}{'Good'}= $x_data[1][$j];$OUTPUT_DATA{$o_file}{raw}{key}{$_}{'Medium'}= $x_data[2][$j];$OUTPUT_DATA{$o_file}{raw}{key}{$_}{'Poor'}= $x_data[3][$j]; ++$j; }
			$OUTPUT_DATA{$o_file}{label_x} = 'Participant Perceptions';
			$OUTPUT_DATA{$o_file}{label_y} = '% of Participants';
			$OUTPUT_DATA{$o_file}{raw}{key}{"Stress"}{total} = 	$gwb_stress_basis ;
			$OUTPUT_DATA{$o_file}{raw}{key}{"Depression"}{total} = $gwb_depression_basis;
			$OUTPUT_DATA{$o_file}{raw}{key}{"Health"}{total} = 	$gwb_health_basis ;
			$OUTPUT_DATA{$o_file}{raw}{key}{"Self-Control"}{total} = $gwb_control_basis ;
			$OUTPUT_DATA{$o_file}{raw}{key}{"Well-being"}{total} = $gwb_being_basis ;
			$OUTPUT_DATA{$o_file}{raw}{key}{"Vitality"}{total} = $gwb_vitality_basis ;
			$OUTPUT_DATA{$o_file}{title} = 'General Well-being Assessment Results';
			my @subtitle = ( 'Low', 'Medium', 'High');
			$OUTPUT_DATA{$o_file}{label_y_sub} = [ @subtitle ];
			$OUTPUT_DATA{$o_file}{g_data} = [ @g_data ];
			$OUTPUT_DATA{$o_file}{x_data} = [ @x_data ];
			}

		}

	if ($input->{'pgraphs'} eq 'all' || $input->{'print_wellbeing2'} == 1)
		{
		++$graph_cnt;
		print $graph_cnt.". ";
		####  General Well-being assessment results new HRA format
		my $o_file = 'Stress and Depression Results from General Health Assessment';
		push @sheet_list, $o_file;

		if ( $PARMS{HRA_cnt} > 0 || $PARMS{GWB_cnt} > 0)
			{
			my $gwb_stress_basis = ($PARMS{'gwb_stress_low'}+$PARMS{'gwb_stress_med'}+$PARMS{'gwb_stress_high'});
			my $gwb_depression_basis = ($PARMS{'gwb_depression_low'}+$PARMS{'gwb_depression_med'}+$PARMS{'gwb_depression_high'});


			my @g_data = (
			    ["Stress",  "Depression"],
			    [(int($PARMS{'gwb_stress_low'}/$gwb_stress_basis*100)), (int($PARMS{'gwb_depression_low'}/$gwb_depression_basis*100))],
			    [(int($PARMS{'gwb_stress_med'}/$gwb_stress_basis*100)), (int($PARMS{'gwb_depression_med'}/$gwb_depression_basis*100))],
			    [(int($PARMS{'gwb_stress_high'}/$gwb_stress_basis*100)), (int($PARMS{'gwb_depression_high'}/$gwb_depression_basis*100))]
			  );
			my @x_data = (
			    ["Stress",                   "Depression"],
			    [$PARMS{'gwb_stress_low'} , $PARMS{'gwb_depression_low'} ],
			    [$PARMS{'gwb_stress_med'} , $PARMS{'gwb_depression_med'} ],
			    [$PARMS{'gwb_stress_high'}, $PARMS{'gwb_depression_high'}]
			  );
			my @set_legend = ( 'Good', 'Medium', 'Poor' );
			my $j=0;
			foreach (@{$g_data[0]}) { $OUTPUT_DATA{$o_file}{computed}{key}{$_}{'Good'}= $g_data[1][$j];$OUTPUT_DATA{$o_file}{computed}{key}{$_}{'Medium'}= $g_data[2][$j];$OUTPUT_DATA{$o_file}{computed}{key}{$_}{'Poor'}= $g_data[3][$j]; ++$j; }
			my $j=0;
			foreach (@{$x_data[0]}) { $OUTPUT_DATA{$o_file}{raw}{key}{$_}{'Good'}= $x_data[1][$j];$OUTPUT_DATA{$o_file}{raw}{key}{$_}{'Medium'}= $x_data[2][$j];$OUTPUT_DATA{$o_file}{raw}{key}{$_}{'Poor'}= $x_data[3][$j]; ++$j; }
			$OUTPUT_DATA{$o_file}{label_x} = 'Participant Perceptions';
			$OUTPUT_DATA{$o_file}{label_y} = '% of Participants';
			$OUTPUT_DATA{$o_file}{raw}{key}{"Stress"}{total} = 	$gwb_stress_basis ;
			$OUTPUT_DATA{$o_file}{raw}{key}{"Depression"}{total} = $gwb_depression_basis;
			$OUTPUT_DATA{$o_file}{title} = 'Stress & Depression Results';
			my @subtitle = ( 'Low', 'Medium', 'High');
			$OUTPUT_DATA{$o_file}{label_y_sub} = [ @subtitle ];
			$OUTPUT_DATA{$o_file}{g_data} = [ @g_data ];
			$OUTPUT_DATA{$o_file}{x_data} = [ @x_data];
			}

		}

	if ($input->{'pgraphs'} eq 'all' || $input->{'print_selfreported'} == 1 || $input->{'print_srdisease'} == 1)
		{
		++$graph_cnt;
		print $graph_cnt.". ";
		####  Self Reported disease
		my $o_file = 'Personal Conditions';
		push @sheet_list, $o_file;

		my $disease_max = $hra_cnt *.8;

		$disease_max = 10 if $disease_max < 10;

		if($PARMS{HRA_cnt} > 0)
			{
			my @g_data = (
			    ["Cancer",            "Diabetes",            "Heart attack",     "Heart disease",         "High BP",       "High cholesterol","Stroke"],
			    [$PARMS{'my_cancer'}, $PARMS{'my_diabetes'}, $PARMS{'my_heart'}, $PARMS{'my_hrtdisease'}, $PARMS{'my_bp'}, $PARMS{'my_chol'}, $PARMS{'my_stroke'}],
			  );
			my $j=0;
			foreach (@{$g_data[0]}) { $OUTPUT_DATA{$o_file}{computed}{$_}= $g_data[1][$j]; ++$j; }
			my $j=0;
			foreach (@{$g_data[0]}) { $OUTPUT_DATA{$o_file}{raw}{$_}= $g_data[1][$j]; ++$j; }
			$OUTPUT_DATA{$o_file}{label_x} = 'Disease';
			$OUTPUT_DATA{$o_file}{label_y} = 'Participants';
			$OUTPUT_DATA{$o_file}{title} = 'Personal Conditions';
			$OUTPUT_DATA{$o_file}{g_data} = [ @g_data ];
			$OUTPUT_DATA{$o_file}{x_data} = [];
			}

		}

	if ($input->{'pgraphs'} eq 'all' || $input->{'print_familyhistory'} == 1 || $input->{'print_srfam'} == 1)
		{
		++$graph_cnt;
		print $graph_cnt.". ";
		####  Self Reported family history
		my $o_file = 'Family History Conditions';
		push @sheet_list, $o_file;

		my $disease_max = $hra_cnt *.8;

		$disease_max = 10 if $disease_max < 10;

		if($PARMS{HRA_cnt} > 0 || $PARMS{'fh_cancer'} || $PARMS{'fh_diabetes'} || $PARMS{'fh_heart'} || $PARMS{'fh_hrtdisease'} || $PARMS{'fh_bp'} || $PARMS{'fh_chol'} || $PARMS{'fh_stroke'})
			{
			my @g1;
			my @g2;
			if($PARMS{'fh_cancer'}){ push(@g1, 'Cancer'); push(@g2, $PARMS{'fh_cancer'}); }
			if($PARMS{'fh_copd'}){ push(@g1, 'COPD'); push(@g2, $PARMS{'fh_copd'}); }
			if($PARMS{'fh_diabetes'}){ push(@g1, "Diabetes"); push(@g2, $PARMS{'fh_diabetes'}); }
			if($PARMS{'fh_heart'}){ push(@g1, "Heart attack"); push(@g2, $PARMS{'fh_heart'}); }
			if($PARMS{'fh_hrtdisease'}){ push(@g1, "Heart disease"); push(@g2, $PARMS{'fh_hrtdisease'}); }
			if($PARMS{'fh_bp'}){ push(@g1, "High BP"); push(@g2, $PARMS{'fh_bp'}); }
			if($PARMS{'fh_chol'}){ push(@g1, "High cholesterol"); push(@g2, $PARMS{'fh_chol'}); }
			if($PARMS{'fh_ibs'}){ push(@g1, 'IBS'); push(@g2, $PARMS{'fh_ibs'}); }
			if($PARMS{'fh_stroke'}){ push(@g1, "Stroke"); push(@g2, $PARMS{'fh_stroke'}); }
			my @g_data = (@g1,@g2);

#			my @g_data = (
#			    ["Cancer",            "Diabetes",            "Heart attack",     "Heart disease",         "High BP",       "High cholesterol","Stroke"],
#			    [$PARMS{'fh_cancer'}, $PARMS{'fh_diabetes'}, $PARMS{'fh_heart'}, $PARMS{'fh_hrtdisease'}, $PARMS{'fh_bp'}, $PARMS{'fh_chol'}, $PARMS{'fh_stroke'}],
#			  );
			my $j=0;
			foreach (@{$g_data[0]}) { $OUTPUT_DATA{$o_file}{computed}{$_}= $g_data[1][$j]; ++$j; }
			my $j=0;
			foreach (@{$g_data[0]}) { $OUTPUT_DATA{$o_file}{raw}{$_}= $g_data[1][$j]; ++$j; }
			$OUTPUT_DATA{$o_file}{label_x} = 'Disease';
			$OUTPUT_DATA{$o_file}{label_y} = 'Participants';
			$OUTPUT_DATA{$o_file}{title} = 'Family History Conditions';
			$OUTPUT_DATA{$o_file}{g_data} = [ @g_data ];
			$OUTPUT_DATA{$o_file}{x_data} = [];
			}

		}
	if ($input->{'pgraphs'} eq 'all' || $input->{'print_glucose'} == 1)
	{
		++$graph_cnt;
		print $graph_cnt.". ";
		####  Glucose
		my $o_file = 'Group Glucose';
		push @sheet_list, $o_file;

		my ($gluc_basis, $gluc_high, $gluc_med, $gluc_low, $gluc_unknown);

		if($gluc_basis = $PARMS{'GLUCOSE_high'} + $PARMS{'GLUCOSE_good'} + $PARMS{'GLUCOSE_med'} + $PARMS{'GLUCOSE_low'} + $PARMS{'GLUCOSE_unknown'})
		{
			$gluc_high = sprintf("%.2f",($PARMS{'GLUCOSE_high'}/$gluc_basis*100));
			$gluc_good = sprintf("%.2f",($PARMS{'GLUCOSE_good'}/$gluc_basis*100));
			$gluc_med = sprintf("%.2f",($PARMS{'GLUCOSE_med'}/$gluc_basis*100));
			$gluc_low = sprintf("%.2f",($PARMS{'GLUCOSE_low'}/$gluc_basis*100));
			$gluc_unknown = sprintf("%.2f",($PARMS{'GLUCOSE_unknown'}/$gluc_basis*100));

			my %gluc_lab = (
				low	=> "Under " . GLUCOSE_LOW_MALE. " for males ".GLUCOSE_LOW_FEMALE. " for females",
				good	=> "Above low and up to " . GLUCOSE_MARGINAL,
				med	=> "Above ".GLUCOSE_MARGINAL." and up to " . GLUCOSE_HIGH,
				high	=> "Over " . GLUCOSE_HIGH
				);

			my @g_data = (
				[$gluc_lab{low}, $gluc_lab{good}, $gluc_lab{med}, $gluc_lab{high}, "unknown"],
				[$gluc_low, $gluc_good, $gluc_med, $gluc_high, $gluc_unknown]
				);
			my @x_data = (
				[$gluc_lab{low}, $gluc_lab{good}, $gluc_lab{med}, $gluc_lab{high}, "unknown"],
				[$PARMS{'GLUCOSE_low'} ,$PARMS{'GLUCOSE_good'}, $PARMS{'GLUCOSE_med'} ,$PARMS{'GLUCOSE_high'}, $PARMS{'GLUCOSE_unknown'}]
				);
			my $j=0;
			foreach (@{$g_data[0]}) { $OUTPUT_DATA{$o_file}{computed}{$_}= $g_data[1][$j]; ++$j; }
			my $j=0;
			foreach (@{$x_data[0]}) { $OUTPUT_DATA{$o_file}{raw}{$_}= $x_data[1][$j]; ++$j; }
			$OUTPUT_DATA{$o_file}{label_x} = 'Glucose levels';
			$OUTPUT_DATA{$o_file}{label_y} = '% of Participants';
			$OUTPUT_DATA{$o_file}{raw}{total} = $gluc_basis;
			# $OUTPUT_DATA{$o_file}{raw}{target_high} = 21;
			# $OUTPUT_DATA{$o_file}{raw}{target_low} = 0;
			$OUTPUT_DATA{$o_file}{title} = 'Group Glucose';
			$OUTPUT_DATA{$o_file}{g_data} = [ @g_data ];
			$OUTPUT_DATA{$o_file}{x_data} = [ @x_data ];

		}
	}

	if ($input->{'pgraphs'} eq 'all' || $input->{'print_ldl'} == 1)
	{
		++$graph_cnt;
		print $graph_cnt.". ";
		####  Ldl
		my $o_file = 'Group Ldl';
		push @sheet_list, $o_file;

		my ($ldl_basis, $ldl_high, $ldl_med, $ldl_low, $ldl_unknown);

		if($ldl_basis = $PARMS{'LDL_high'} + $PARMS{'LDL_med'} + $PARMS{'LDL_low'} + $PARMS{'LDL_unknown'})
		{
			$ldl_high = sprintf("%.2f",($PARMS{'LDL_high'}/$ldl_basis*100));
			$ldl_med = sprintf("%.2f",($PARMS{'LDL_med'}/$ldl_basis*100));
			$ldl_low = sprintf("%.2f",($PARMS{'LDL_low'}/$ldl_basis*100));
			$ldl_unknown = sprintf("%.2f",($PARMS{'LDL_unknown'}/$ldl_basis*100));

			my %ldl_lab = (
				low	=> "Under " . LDL_MARGINAL,
				med	=> LDL_MARGINAL . " to " . LDL_HIGH,
				high	=> "Over " . LDL_HIGH
				);

			my @g_data = (
				[$ldl_lab{low}, $ldl_lab{med}, $ldl_lab{high}, "unknown"],
				[$ldl_low, $ldl_med, $ldl_high, $ldl_unknown]
				);
			my @x_data = (
				[$ldl_lab{low}, $ldl_lab{med}, $ldl_lab{high}, "unknown"],
				[$PARMS{'LDL_low'} ,$PARMS{'LDL_med'} ,$PARMS{'LDL_high'}, $PARMS{'LDL_unknown'}]
				);
			my $j=0;
			foreach (@{$g_data[0]}) { $OUTPUT_DATA{$o_file}{computed}{$_}= $g_data[1][$j]; ++$j; }
			my $j=0;
			foreach (@{$x_data[0]}) { $OUTPUT_DATA{$o_file}{raw}{$_}= $x_data[1][$j]; ++$j; }
			$OUTPUT_DATA{$o_file}{label_x} = 'Ldl levels';
			$OUTPUT_DATA{$o_file}{label_y} = '% of Participants';
			$OUTPUT_DATA{$o_file}{raw}{total} = $ldl_basis;
			$OUTPUT_DATA{$o_file}{title} = 'Group Ldl';
			$OUTPUT_DATA{$o_file}{g_data} = [ @g_data ];
			$OUTPUT_DATA{$o_file}{x_data} = [ @x_data ];

		}
	}

	if ($input->{'pgraphs'} eq 'all' || $input->{'print_hdl'} == 1)
	{
		++$graph_cnt;
		print $graph_cnt.". ";
		####  hdl
		my $o_file = 'Group HDL';
		push @sheet_list, $o_file;

		my ($hdl_basis, $hdl_high, $hdl_low, $hdl_unknown);

		if($hdl_basis = $PARMS{'HDL_high'} + $PARMS{'HDL_low'} + $PARMS{'HDL_unknown'})
		{
			$hdl_high = sprintf("%.2f",($PARMS{'HDL_high'}/$hdl_basis*100));
			$hdl_low = sprintf("%.2f",($PARMS{'HDL_low'}/$hdl_basis*100));
			$hdl_unknown = sprintf("%.2f",($PARMS{'HDL_unknown'}/$hdl_basis*100));

			my %hdl_lab = (
				low	=> "Under " . HDL_HIGH,
				high	=> "Over " . HDL_HIGH
				);

			my @g_data = (
				[$hdl_lab{low}, $hdl_lab{high}, "unknown"],
				[$hdl_low, $hdl_high, $hdl_unknown]
				);
			my @x_data = (
				[$hdl_lab{low}, $hdl_lab{high}, "unknown"],
				[$PARMS{'HDL_low'}, $PARMS{'HDL_high'}, $PARMS{'HDL_unknown'}]
				);
			my $j=0;
			foreach (@{$g_data[0]}) { $OUTPUT_DATA{$o_file}{computed}{$_}= $g_data[1][$j]; ++$j; }
			my $j=0;
			foreach (@{$x_data[0]}) { $OUTPUT_DATA{$o_file}{raw}{$_}= $x_data[1][$j]; ++$j; }
			$OUTPUT_DATA{$o_file}{label_x} = 'HDL levels';
			$OUTPUT_DATA{$o_file}{label_y} = '% of Participants';
			$OUTPUT_DATA{$o_file}{raw}{total} = $hdl_basis;
			$OUTPUT_DATA{$o_file}{title} = 'Group HDL';
			$OUTPUT_DATA{$o_file}{g_data} = [ @g_data ];
			$OUTPUT_DATA{$o_file}{x_data} = [ @x_data ];

		}
	}
	if ($input->{'pgraphs'} eq 'all' || $input->{'print_triglycerides'} == 1)
	{
		++$graph_cnt;
		print $graph_cnt.". ";
		####  Triglycerides
		my $o_file = 'Group Triglycerides';
		push @sheet_list, $o_file;

		my ($tri_basis, $tri_above500, $tri_200_499, $tri_150_199, $tri_below150, $tri_unknown);

		if($tri_basis = $PARMS{'TRI_above500'} + $PARMS{'TRI_200_499'} + $PARMS{'TRI_150_199'} + $PARMS{'TRI_below150'} + $PARMS{'TRI_unknown'})
		{
			$tri_above500 = sprintf("%.2f",($PARMS{'TRI_above500'}/$tri_basis*100));
			$tri_200_499 = sprintf("%.2f",($PARMS{'TRI_200_499'}/$tri_basis*100));
			$tri_150_199 = sprintf("%.2f",($PARMS{'TRI_150_199'}/$tri_basis*100));
			$tri_below150 = sprintf("%.2f",($PARMS{'TRI_below150'}/$tri_basis*100));
			$tri_unknown = sprintf("%.2f",($PARMS{'TRI_unknown'}/$tri_basis*100));

			my @g_data = (
				['below 150', '150 - 199', '200 - 499', 'above 500', 'unknown'],
				[$tri_below150, $tri_150_199, $tri_200_499, $tri_above500, $tri_unknown]
				);
			my @x_data = (
				['below 150', '150 - 199', '200 - 499', 'above 500', 'unknown'],
				[$PARMS{'TRI_below150'} ,$PARMS{'TRI_150_199'} ,$PARMS{'TRI_200_499'}, $PARMS{'TRI_above500'}, $PARMS{'TRI_unknown'}]
				);
			my $j=0;
			foreach (@{$g_data[0]}) { $OUTPUT_DATA{$o_file}{computed}{$_}= $g_data[1][$j]; ++$j; }
			my $j=0;
			foreach (@{$x_data[0]}) { $OUTPUT_DATA{$o_file}{raw}{$_}= $x_data[1][$j]; ++$j; }
			$OUTPUT_DATA{$o_file}{label_x} = 'Triglycerides levels';
			$OUTPUT_DATA{$o_file}{label_y} = '% of Participants';
			$OUTPUT_DATA{$o_file}{raw}{total} = $tri_basis;
			$OUTPUT_DATA{$o_file}{title} = 'Group Triglycerides';
			$OUTPUT_DATA{$o_file}{g_data} = [ @g_data ];
			$OUTPUT_DATA{$o_file}{x_data} = [ @x_data ];

		}
	}

	if ($input->{'pgraphs'} eq 'all' || $input->{'print_days_missed'} == 1)
	{
		++$graph_cnt;
		print $graph_cnt.". ";
		####  days_missed
		my $o_file = 'Days missed';
		push @sheet_list, $o_file;

		my ($days_missed_basis, $days_missed_none, $days_missed_1to5, $days_missed_6to10, $days_missed_10plus, $days_missed_not_apply);

		if($days_missed_basis = $PARMS{'days_missed_none'} + $PARMS{'days_missed_1to5'} + $PARMS{'days_missed_6to10'} + $PARMS{'days_missed_10plus'} + $PARMS{'days_missed_not_apply'})
		{
			$days_missed_none = sprintf("%.2f",($PARMS{'days_missed_none'}/$days_missed_basis*100));
			$days_missed_1to5 = sprintf("%.2f",($PARMS{'days_missed_1to5'}/$days_missed_basis*100));
			$days_missed_6to10 = sprintf("%.2f",($PARMS{'days_missed_6to10'}/$days_missed_basis*100));
			$days_missed_10plus = sprintf("%.2f",($PARMS{'days_missed_10plus'}/$days_missed_basis*100));
			$days_missed_not_apply = sprintf("%.2f",($PARMS{'days_missed_not_apply'}/$days_missed_basis*100));


			my @g_data = (
				['None', '1-5 days', '6-10 days', '10 days or more', 'Does not apply'],
				[$days_missed_none, $days_missed_1to5, $days_missed_6to10, $days_missed_10plus, $days_missed_not_apply]
				);
			my @x_data = (
				['None', '1-5 days', '6-10 days', '10 days or more', 'Does not apply'],
				[$PARMS{'days_missed_none'} ,$PARMS{'days_missed_1to5'} ,$PARMS{'days_missed_6to10'}, $PARMS{'days_missed_10plus'}, $PARMS{'days_missed_not_apply'}]
				);
			my $j=0;
			foreach (@{$g_data[0]}) { $OUTPUT_DATA{$o_file}{computed}{$_}= $g_data[1][$j]; ++$j; }
			my $j=0;
			foreach (@{$x_data[0]}) { $OUTPUT_DATA{$o_file}{raw}{$_}= $x_data[1][$j]; ++$j; }
			$OUTPUT_DATA{$o_file}{label_x} = 'Days missed';
			$OUTPUT_DATA{$o_file}{label_y} = '% of Participants';
			$OUTPUT_DATA{$o_file}{raw}{total} = $days_missed_basis;
			$OUTPUT_DATA{$o_file}{title} = 'Days missed';
			$OUTPUT_DATA{$o_file}{g_data} = [ @g_data ];
			$OUTPUT_DATA{$o_file}{x_data} = [ @x_data ];

		}
	}

	if ($input->{'pgraphs'} eq 'all' || $input->{'print_colon_exam'} == 1)
	{
		++$graph_cnt;
		print $graph_cnt.". ";
		####  colon_exam
		my $o_file = 'Colon exam';
		push @sheet_list, $o_file;

		my ($colon_basis, $colonoscopy_good, $colonoscopy_med, $colonoscopy_bad);

		if($colon_basis = $PARMS{'colonoscopy_good'} + $PARMS{'colonoscopy_med'} + $PARMS{'colonoscopy_bad'})
		{
			$colonoscopy_good = sprintf("%.2f",($PARMS{'colonoscopy_good'}/$colon_basis*100));
			$colonoscopy_med = sprintf("%.2f",($PARMS{'colonoscopy_med'}/$colon_basis*100));
			$colonoscopy_bad = sprintf("%.2f",($PARMS{'colonoscopy_bad'}/$colon_basis*100));

			my @g_data = (
				["1 year or less", "1 to 3 years", "Over 3 years"],
				[$colonoscopy_good, $colonoscopy_med, $colonoscopy_bad]
				);
			my @x_data = (
				["1 year or less", "1 to 3 years", "Over 3 years"],
				[$PARMS{'colonoscopy_good'} ,$PARMS{'colonoscopy_med'} ,$PARMS{'colonoscopy_bad'}]
				);
			my $j=0;
			foreach (@{$g_data[0]}) { $OUTPUT_DATA{$o_file}{computed}{$_}= $g_data[1][$j]; ++$j; }
			my $j=0;
			foreach (@{$x_data[0]}) { $OUTPUT_DATA{$o_file}{raw}{$_}= $x_data[1][$j]; ++$j; }
			$OUTPUT_DATA{$o_file}{label_x} = 'Time since last colon exam';
			$OUTPUT_DATA{$o_file}{label_y} = '% of Participants';
			$OUTPUT_DATA{$o_file}{raw}{total} = $colon_basis;
			$OUTPUT_DATA{$o_file}{title} = 'Colon exam';
			$OUTPUT_DATA{$o_file}{g_data} = [ @g_data ];
			$OUTPUT_DATA{$o_file}{x_data} = [ @x_data ];

		}
	}

	if ($input->{'pgraphs'} eq 'all' || $input->{'print_general_exam'} == 1)
	{
		++$graph_cnt;
		print $graph_cnt.". ";
		####  general_exam
		my $o_file = 'General exam';
		push @sheet_list, $o_file;

		my ($gen_basis, $gen_exam_under2, $gen_exam_2to5, $gen_exam_5plus, $gen_exam_never);

		if($gen_basis = $PARMS{'gen_exam_under2'} + $PARMS{'gen_exam_2to5'} + $PARMS{'gen_exam_5plus'} + $PARMS{'gen_exam_never'})
		{
			$gen_exam_under2 = sprintf("%.2f",($PARMS{'gen_exam_under2'}/$gen_basis*100));
			$gen_exam_2to5 = sprintf("%.2f",($PARMS{'gen_exam_2to5'}/$gen_basis*100));
			$gen_exam_5plus = sprintf("%.2f",($PARMS{'gen_exam_5plus'}/$gen_basis*100));
			$gen_exam_never = sprintf("%.2f",($PARMS{'gen_exam_never'}/$gen_basis*100));

			my @g_data = (
				["2 years or less", "2 to 5 years", "Over 5 years", "Never"],
				[$gen_exam_under2, $gen_exam_2to5, $gen_exam_5plus, $gen_exam_never]
				);
			my @x_data = (
				["2 years or less", "2 to 5 years", "Over 5 years", "Never"],
				[$PARMS{'gen_exam_under2'} ,$PARMS{'gen_exam_2to5'} ,$PARMS{'gen_exam_5plus'}, $PARMS{'gen_exam_never'}]
				);
			my $j=0;
			foreach (@{$g_data[0]}) { $OUTPUT_DATA{$o_file}{computed}{$_}= $g_data[1][$j]; ++$j; }
			my $j=0;
			foreach (@{$x_data[0]}) { $OUTPUT_DATA{$o_file}{raw}{$_}= $x_data[1][$j]; ++$j; }
			$OUTPUT_DATA{$o_file}{label_x} = 'Time since last general exam';
			$OUTPUT_DATA{$o_file}{label_y} = '% of Participants';
			$OUTPUT_DATA{$o_file}{raw}{total} = $gen_basis;
			$OUTPUT_DATA{$o_file}{title} = 'General exam';
			$OUTPUT_DATA{$o_file}{g_data} = [ @g_data ];
			$OUTPUT_DATA{$o_file}{x_data} = [ @x_data ];

		}
	}

	if ($input->{'pgraphs'} eq 'all' || $input->{'print_hga1c'} == 1)
	{
		++$graph_cnt;
		print $graph_cnt.". ";
		####  HgA1c
		my $o_file = 'HgA1c';
		push @sheet_list, $o_file;

		my ($hga1c_basis, $hga1c_high, $hga1c_med, $hga1c_low, $hga1c_unknown);

		if($hga1c_basis = $PARMS{'hga1c_high'} + $PARMS{'hga1c_med'} + $PARMS{'hga1c_low'} + $PARMS{'hga1c_unknown'})
		{
			$hga1c_high = sprintf("%.2f",($PARMS{'hga1c_high'}/$hga1c_basis*100));
			$hga1c_med = sprintf("%.2f",($PARMS{'hga1c_med'}/$hga1c_basis*100));
			$hga1c_low = sprintf("%.2f",($PARMS{'hga1c_low'}/$hga1c_basis*100));
			$hga1c_unknown = sprintf("%.2f",($PARMS{'hga1c_unknown'}/$hga1c_basis*100));

			my %hga1c_lab = (
				low	=> "Under " . HGA1C_MARGINAL,
				med	=> HGA1C_MARGINAL . " to " . HGA1C_HIGH,
				high	=> "Over " . HGA1C_HIGH
				);

			my @g_data = (
				[$hga1c_lab{low}, $hga1c_lab{med},$hga1c_lab{high}, "Unknown"],
				[$hga1c_low, $hga1c_med, $hga1c_high, $hga1c_unknown]
				);
			my @x_data = (
				[$hga1c_lab{low}, $hga1c_lab{med},$hga1c_lab{high}, "Unknown"],
				[$PARMS{'hga1c_low'}, $PARMS{'hga1c_med'}, $PARMS{'hga1c_high'}, $PARMS{'hga1c_unknown'}]
				);
			my $j=0;
			foreach (@{$g_data[0]}) { $OUTPUT_DATA{$o_file}{computed}{$_}= $g_data[1][$j]; ++$j; }
			my $j=0;
			foreach (@{$x_data[0]}) { $OUTPUT_DATA{$o_file}{raw}{$_}= $x_data[1][$j]; ++$j; }
			$OUTPUT_DATA{$o_file}{label_x} = 'Hemoglobin A1c levels';
			$OUTPUT_DATA{$o_file}{label_y} = '% of Participants';
			$OUTPUT_DATA{$o_file}{raw}{total} = $hga1c_basis;
			$OUTPUT_DATA{$o_file}{title} = 'HgA1c';
			$OUTPUT_DATA{$o_file}{g_data} = [ @g_data ];
			$OUTPUT_DATA{$o_file}{x_data} = [ @x_data ];

		}
	}

	if ($input->{'pgraphs'} eq 'all' || $input->{'print_diet'} == 1)
	{
		++$graph_cnt;
		print $graph_cnt.". ";
		####  FIBER
		my $o_file = 'Group Fiber';
		push @sheet_list, $o_file;

		my ($fiber_basis, $diet_fiber_good, $diet_fiber_bad);

		if($fiber_basis = $PARMS{'diet_fiber_good'} + $PARMS{'diet_fiber_bad'})
		{
			$diet_fiber_good = sprintf("%.2f",($PARMS{'diet_fiber_good'}/$fiber_basis*100));
			$diet_fiber_bad = sprintf("%.2f",($PARMS{'diet_fiber_bad'}/$fiber_basis*100));

			my %fiber_lab = (
				bad	=> "Low or No Fiber in Diet",
				good	=> "Fiber in Diet"
				);

			my @g_data = (
				[$fiber_lab{good}, $fiber_lab{bad}],
				[$diet_fiber_good, $diet_fiber_bad]
				);
			my @x_data = (
				[$fiber_lab{good}, $fiber_lab{bad}],
				[$PARMS{'diet_fiber_good'}, $PARMS{'diet_fiber_bad'}]
				);
			my $j=0;
			foreach (@{$g_data[0]}) { $OUTPUT_DATA{$o_file}{computed}{$_}= $g_data[1][$j]; ++$j; }
			my $j=0;
			foreach (@{$x_data[0]}) { $OUTPUT_DATA{$o_file}{raw}{$_}= $x_data[1][$j]; ++$j; }
			$OUTPUT_DATA{$o_file}{label_x} = 'Fiber in diet';
			$OUTPUT_DATA{$o_file}{label_y} = '% of Participants';
			$OUTPUT_DATA{$o_file}{raw}{total} = $fiber_basis;
			$OUTPUT_DATA{$o_file}{title} = 'Group Fiber';
			$OUTPUT_DATA{$o_file}{g_data} = [ @g_data ];
			$OUTPUT_DATA{$o_file}{x_data} = [ @x_data ];

		}
	}

	if ($input->{'pgraphs'} eq 'all' || $input->{'print_diet'} == 1)
	{
		++$graph_cnt;
		print $graph_cnt.". ";
		####  FAT
		my $o_file = 'Group Fat';
		push @sheet_list, $o_file;

		my ($fat_basis, $diet_fat_good, $diet_fat_bad);

		if($fat_basis = $PARMS{'diet_fat_good'} + $PARMS{'diet_fat_bad'})
		{
			$diet_fat_good = sprintf("%.2f",($PARMS{'diet_fat_good'}/$fat_basis*100));
			$diet_fat_bad = sprintf("%.2f",($PARMS{'diet_fat_bad'}/$fat_basis*100));

			my %fat_lab = (
				good	=> "Low or No Fat in Diet",
				bad	=> "Fat in Diet"
				);

			my @g_data = (
				[$fat_lab{good}, $fat_lab{bad}],
				[$diet_fat_good, $diet_fat_bad]
				);
			my @x_data = (
				[$fat_lab{good}, $fat_lab{bad}],
				[$PARMS{'diet_fat_good'}, $PARMS{'diet_fat_bad'}]
				);
			my $j=0;
			foreach (@{$g_data[0]}) { $OUTPUT_DATA{$o_file}{computed}{$_}= $g_data[1][$j]; ++$j; }
			my $j=0;
			foreach (@{$x_data[0]}) { $OUTPUT_DATA{$o_file}{raw}{$_}= $x_data[1][$j]; ++$j; }
			$OUTPUT_DATA{$o_file}{label_x} = 'Fat in diet';
			$OUTPUT_DATA{$o_file}{label_y} = '% of Participants';
			$OUTPUT_DATA{$o_file}{raw}{total} = $fat_basis;
			$OUTPUT_DATA{$o_file}{title} = 'Group Fat';
			$OUTPUT_DATA{$o_file}{g_data} = [ @g_data ];
			$OUTPUT_DATA{$o_file}{x_data} = [ @x_data ];

		}
	}

	if ($input->{'pgraphs'} eq 'all' || $input->{'print_waist'} == 1)
	{
		++$graph_cnt;
		print $graph_cnt.". ";
		####  FAT
		my $o_file = 'Group Waist Measurements';
		push @sheet_list, $o_file;

		my ($waist_basis, $waist_high, $waist_ok);

		if($waist_basis = $PARMS{'waist_high'} + $PARMS{'waist_ok'})
		{
			$waist_high = sprintf("%.2f",($PARMS{'waist_high'}/$waist_basis*100));
			$waist_ok = sprintf("%.2f",($PARMS{'waist_ok'}/$waist_basis*100));

			my %waist_lab = (
				high	=> "Waist above 35 inches for women and 40 inches for men",
				ok	=> "Waist below high ranges"
				);

			my @g_data = (
				[$waist_lab{high}, $waist_lab{ok}],
				[$waist_high, $waist_ok]
				);
			my @x_data = (
				[$waist_lab{high}, $waist_lab{ok}],
				[$PARMS{'waist_high'}, $PARMS{'waist_ok'}]
				);
			my $j=0;
			foreach (@{$g_data[0]}) { $OUTPUT_DATA{$o_file}{computed}{$_}= $g_data[1][$j]; ++$j; }
			my $j=0;
			foreach (@{$x_data[0]}) { $OUTPUT_DATA{$o_file}{raw}{$_}= $x_data[1][$j]; ++$j; }
			$OUTPUT_DATA{$o_file}{label_x} = 'Waist Measures';
			$OUTPUT_DATA{$o_file}{label_y} = '% of Participants';
			$OUTPUT_DATA{$o_file}{raw}{total} = $waist_basis;
			$OUTPUT_DATA{$o_file}{title} = 'Group Waist Measures';
			$OUTPUT_DATA{$o_file}{g_data} = [ @g_data ];
			$OUTPUT_DATA{$o_file}{x_data} = [ @x_data ];

		}
	}
	if(lc($input->{'rpt_format'}) eq 'xls'){
		my %cell_locations = ( 	title 		=> 'A2',
					raw_title	=> 'A25',
					g_data 		=> 'B5',
					label_y 	=> 'C3',
					label_y_sub 	=> 'C4',
					label_x 	=> 'B4',
					x_data 		=> 'B26');
		my $workbook_ref;
		my %converted_user;
		my %stuff = (
			report_name => 'Aggregate Spreadsheet',
			file_name => $PARMS{'file_name'},
			);

		foreach my $sheet (@sheet_list){
			my %cell_values = (	title 		=> $OUTPUT_DATA{$sheet}{title},
						raw_title 	=> 'Raw numbers used to compute %',
						sheetname 	=> substr($sheet,0,30),
						label_x		=> $OUTPUT_DATA{$sheet}{label_x},
						label_y		=> $OUTPUT_DATA{$sheet}{label_y},
						label_y_sub	=> $OUTPUT_DATA{$sheet}{label_y_sub},
						g_data		=> $OUTPUT_DATA{$sheet}{g_data},
						x_data		=> $OUTPUT_DATA{$sheet}{x_data});
			$workbook_ref = HealthStatus::Report::xls_basic_sheet($config, \%converted_user, $workbook_ref, \%stuff, \%cell_locations, \%cell_values);
			}
		}

	return \%OUTPUT_DATA;

}

sub bargraph
	{
	my ( $g_hash, $gdata, $legend, $o_file, $font_dir) = @_;

	my $legend_count = @$legend;

	my $bar_graph = GD::Graph::bars->new(450, 220);

	$bar_graph->set( %$g_hash ) or die $bar_graph->error;
	if($legend_count) { $bar_graph->set_legend( @$legend ) or die $bar_graph->error; }

	$bar_graph->set_title_font($font_dir . "arial.ttf", 14);
	$bar_graph->set_x_label_font($font_dir . "arial.ttf", 10);
	$bar_graph->set_y_label_font($font_dir . "arial.ttf", 10);
	$bar_graph->set_x_axis_font($font_dir . "arial.ttf", 6);
	$bar_graph->set_y_axis_font($font_dir . "arial.ttf", 8);
	$bar_graph->set_legend_font($font_dir . "arial.ttf", 9);

	$gd_graph = $bar_graph->plot($gdata) or die $bar_graph->error;

	if ( $gd_graph ) {
		open(IMG, ">$o_file") or die "$! - $o_file";
		binmode IMG;
		print IMG $gd_graph->png or die "$! - $o_file";
		close IMG;
		return 1;
		}
	else	{
		return 0;
		}
	}

sub mixed_graph
	{
	my ( $g_hash, $gdata, $legend, $o_file, $font_dir) = @_;

	my $legend_count = @$legend;

	my $mixed_graph = GD::Graph::mixed->new(450, 220);

	$mixed_graph->set( %$g_hash) or die $mixed_graph->error;
	if ($legend_count) { $mixed_graph->set_legend( @$legend ) or die $mixed_graph->error; }

	$mixed_graph->set_title_font($font_dir . "arial.ttf", 14);
	$mixed_graph->set_x_label_font($font_dir . "arial.ttf", 10);
	$mixed_graph->set_y_label_font($font_dir . "arial.ttf", 10);
	$mixed_graph->set_x_axis_font($font_dir . "arial.ttf", 8);
	$mixed_graph->set_y_axis_font($font_dir . "arial.ttf", 8);
	$mixed_graph->set_legend_font($font_dir . "arial.ttf", 9);

	$gd_graph = $mixed_graph->plot($gdata) or die $mixed_graph->error;
	if ( $gd_graph )
		{
		open(IMG, ">$o_file") or die "$! - $o_file";
		binmode IMG;
		print IMG $gd_graph->png or die "$! - $o_file";
		close IMG;
		return 1;
		}
	else	{
		return 0;
		}
	}

sub pie_graph
	{
	my ( $g_hash, $gdata, $legend, $o_file, $font_dir) = @_;

	my $pie_graph = GD::Graph::pie->new(320,320);

	$pie_graph->set( %$g_hash ) or die $pie_graph->error;

	$pie_graph->set_title_font($font_dir . "arial.ttf", 14);
	$pie_graph->set_value_font($font_dir . "arial.ttf", 8);
	$pie_graph->set_label_font($font_dir . "arial.ttf", 8);

	$gd_graph = $pie_graph->plot($gdata) or die $pie_graph->error;
	if ( $gd_graph )
		{
		open(IMG, ">$o_file") or die "$! - $o_file";
		binmode IMG;
		print IMG $gd_graph->png or die "$! - $o_file";
		close IMG;
		return 1;
		}
	else	{
		return 0;
		}
	}


1;