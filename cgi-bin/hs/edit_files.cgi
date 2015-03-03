#!/usr/local/bin/perl
use strict;

use File::Basename        qw( dirname );
use File::Spec::Functions qw( rel2abs );

use lib dirname(rel2abs($0)),'.','/usr/local/www/vhosts/managed2/modules/pdf', '/usr/local/www/vhosts/managed2/modules';
if (!do('common.inc')) {
   my $error = $@ ? $@
             : $! ? $!
             : 'did not return a true value';
   die("Unable to load common stuff: $error\n");
}
use vars qw( $Debug );
use Text::Template;
use Data::Dumper;
use Mail::Sendmail;

my $input = new CGI();
my $config = getConfig($input->param('extracfg'));

my %input = $input->Vars();
my ($data, $got_it, $assessment, $health, $page, $template, $template_name);
my ($attaboy, $bday, $results, $output);

my %hash = map { $_, $input->param($_) } $input->param();
my %config = map { $_, $config->$_ } $config->directives;

$hash{config} = \%config;
$input{config} = $config->as_hash();
# authenticate_user redirects the user if they is not allowed to
# view this page
my $user = authenticateUser("admin", $input, $config) or die "You should never see this message.";
############################################################################
### Comment out the following line before going into production ############
$Debug = $input->param("HS_Debug") || $ENV{HS_DEBUG} || 0;
#### only uncomment if you need to debug the input scripts      ############
############################################################################

$| = 1;

if ($Debug) {
	print "Content-type: text/plain\n\n";
	print "Modules Versions:\nHealthStatus - $HealthStatus::VERSION\nHealthStatus::Authenticate - $HealthStatus::Authenticate::VERSION\nHealthStatus::Database - $HealthStatus::Database::VERSION\n";
	print "HealthStatus::Config - $HealthStatus::Config::VERSION\nHealthStatus::User - $HealthStatus::User::VERSION\n\n";
	$config->pretty_print;
}

print $input->param('preview') . " = preview\n" if $Debug;
print $input->param('edit') . "\n" if $Debug;
print $input->param('save') . "\n" if $Debug;

if($input->param('save') eq 'email'){
	my $efile = $config->template_directory . $config->attaboy_text;
	my $etext = $input->param('attaboy_text');
	$etext =~ s/<p>/\n\n/g;
	$etext =~ s/<\/p>//g;
	print $efile . "\n" if $Debug;
	open AB, ">$efile";
	print AB $etext;
	close AB;
	my $bfile = $config->template_directory . $config->bday_text;
	my $btext = $input->param('bday_text');
	$btext =~ s/<p>/\n\n/g;
	$btext =~ s/<\/p>//g;
	print $bfile . "\n" if $Debug;
	open BD, ">$bfile";
	print BD $btext;
	close BD;

	print $input->redirect (-uri => $config->admin_path );
	exit;
	}
elsif($input->param('preview')){
	my $datfile 	= $config->template_directory;
	my $assessment 	= $input->param('assessment');
	my $dumpfile 	= $config->authenticate_dir;
	my $user1 		= HealthStatus::User->new( \%hash );
	my $etext 		= $input->param(lc($assessment).'_text');
	my $variable_file;
	my $result_msg;
	my $assessment_msg;
	$user1->db_id( '1' );

	
	if ($assessment eq 'CRC'){
		$variable_file 	= "crc_variables.tmpl";
		$dumpfile 		.= "/CRC_dump_of_1.user";
		$result_msg		= "Your Personalized Cardiac Risk Results";
		$assessment_msg = "Cardiac Risk Assessment";
		}
	elsif ($assessment eq 'DRC'){
		$variable_file 	= "drc_variables.tmpl";
		$dumpfile 		.= "/DRC_dump_of_1.user";
		$result_msg		= "Your Personalized Diabetes Risk Results";
		$assessment_msg = "Diabetes Assessment";
		}
	elsif ($assessment eq 'FIT'){
		$variable_file 	= "fit_variables.tmpl";
		$dumpfile 		.= "/FIT_dump_of_1.user";
		$result_msg		= "Your Personalized Fitness Assessment";
		$assessment_msg = "Fitness Assessment";
		}
	elsif ($assessment eq 'GWB'){
		$variable_file 	= "gwb_variables.tmpl";
		$dumpfile 		.= "/GWB_dump_of_1.user";
		$result_msg		= "Your Personalized General Well-being Assessment";
		$assessment_msg = "General Well-Being";
		}
	elsif ($assessment eq 'HRA'){
		$variable_file 	= "hra_variables.tmpl";
		$dumpfile 		.= "/HRA_dump_of_1.user";
		$result_msg		= "Your Personalized General Health Assessment";
		$assessment_msg = "General Health Assessment";
		}
	elsif ($assessment eq 'GHA'){
		$variable_file 	= "gha_variables.tmpl";
		$dumpfile 		.= "/GHA_dump_of_1.user";
		$result_msg		= "Your Personalized Health Risk Assessment";
		$assessment_msg = "Health Risk Assessment";
		}
	if (!(-e "$dumpfile")) {
		error( "$dumpfile does not exist, please contact HealthStatus.com - 317.823.2687" );
		exit 1;
		}
	$user1 = do $dumpfile;
	bless($user1, "HealthStatus::User");
	$user1->{config} = $config;
	my $config_file = $config->conf_config_dir."/healthstatus.conf";
	my $health = HealthStatus->new(
		{
		assessment => $assessment,
		user       => $user1,
		config     => $config_file,
		}
		);
	$user1->set_non_standard;
	$health->assess( $user1 );
	$user1->pretty_print if $Debug;
	foreach my $key ( keys %$user1 )
		{
		$input{$key} = $user1->{$key};
		$input->param("$key","$user1->{$key}");
		}
	$input{config} 			= $config->as_hash();
	$input{edit_preview} 	= 1;
	$input{assessment} 		= $assessment;
	$etext =~ s/\{\$date\}/\$date/g;
	$input{etext} 			= $etext;
	$input{variable_file} 	= $variable_file;
	$input{result_msg} 		= $result_msg;
	$input{assessment_msg} 	= $assessment_msg;
	$datfile 				.= 'covers_letter_preview.tmpl';
	my $mime = $health->mime(  lc $input->param('output_format') );
	my $data;
	if($input->param('output_format') eq 'PDF') {
		my $template = 	$health->template('pdf','covers_letter_pdf_preview.tmpl');
		$data = $health->pdf( $template, \%input );
	} else {
		$data = Text::Template::fill_in_file( $datfile, HASH => \%input );
	}
	print $input->header($mime), $data;
	exit;
	}
elsif($input->param('save') eq 'letter'){
	my $crcfile = $config->template_directory;
	$crcfile .= $config->crc_cover_letter_html || "/crc_cover_letter_html.tmpl";
	my $etext = $input->param('crc_text');
	$etext =~ s/\n\n/<\/p>\n<p>/g;
	print $crcfile . "\n" if $Debug;
	open AB, ">$crcfile";
	print AB $etext;
	close AB;

	my $drcfile = $config->template_directory;
	$drcfile .= $config->drc_cover_letter_html || "/drc_cover_letter_html.tmpl";
	my $etext = $input->param('drc_text');
	$etext =~ s/\n\n/<\/p>\n<p>/g;
	print $drcfile . "\n" if $Debug;
	open AB, ">$drcfile";
	print AB $etext;
	close AB;

	my $fitfile = $config->template_directory;
	$fitfile .= $config->fit_cover_letter_html || "/fit_cover_letter_html.tmpl";
	my $etext = $input->param('fit_text');
	$etext =~ s/\n\n/<\/p>\n<p>/g;
	print $fitfile . "\n" if $Debug;
	open AB, ">$fitfile";
	print AB $etext;
	close AB;

	my $ghafile = $config->template_directory;
	$ghafile .= $config->gha_cover_letter_html || "/gha_cover_letter_html.tmpl";
	my $etext = $input->param('gha_text');
	$etext =~ s/\n\n/<\/p>\n<p>/g;
	print $ghafile . "\n" if $Debug;
	open AB, ">$ghafile";
	print AB $etext;
	close AB;

	my $gwbfile = $config->template_directory;
	$gwbfile .= $config->gwb_cover_letter_html || "/gwb_cover_letter_html.tmpl";
	my $etext = $input->param('gwb_text');
	$etext =~ s/\n\n/<\/p>\n<p>/g;
	print $gwbfile . "\n" if $Debug;
	open AB, ">$gwbfile";
	print AB $etext;
	close AB;

	my $hrafile = $config->template_directory;
	$hrafile .= $config->hra_cover_letter_html || "/hra_cover_letter_html.tmpl";
	my $etext = $input->param('hra_text');
	$etext =~ s/\n\n/<\/p>\n<p>/g;
	print $hrafile . "\n" if $Debug;
	open AB, ">$hrafile";
	print AB $etext;
	close AB;

	print $input->redirect (-uri => $config->admin_path );
	exit;
	}
elsif($input->param('revert_back') eq 'letter'){
	my $crcfile = $config->template_directory;
	$crcfile .= $config->crc_cover_letter_html || "/crc_cover_letter_html.tmpl";
	my $crc_defaultfile = $config->template_directory."/crc_default_cover_letter.tmpl";
	my $crc_cover_letter;
	open FILE, $crc_defaultfile;
	while( <FILE> ) {
		$crc_cover_letter .= $_;
	}
	close FILE;
	print $crcfile . "\n" if $Debug;
	open AB, ">$crcfile";
	print AB $crc_cover_letter;
	close AB;

	my $drcfile = $config->template_directory;
	$drcfile .= $config->drc_cover_letter_html || "/drc_cover_letter_html.tmpl";
	my $drc_defaultfile = $config->template_directory."/drc_default_cover_letter.tmpl";
	my $drc_cover_letter;
	open FILE, $drc_defaultfile;
	while( <FILE> ) {
		$drc_cover_letter .= $_;
	}
	close FILE;
	print $drcfile . "\n" if $Debug;
	open AB, ">$drcfile";
	print AB $drc_cover_letter;
	close AB;

	my $fitfile = $config->template_directory;
	$fitfile .= $config->fit_cover_letter_html || "/fit_cover_letter_html.tmpl";
	my $fit_defaultfile = $config->template_directory."/fit_default_cover_letter.tmpl";
	my $fit_cover_letter;
	open FILE, $fit_defaultfile;
	while( <FILE> ) {
		$fit_cover_letter .= $_;
	}
	close FILE;

	print $fitfile . "\n" if $Debug;
	open AB, ">$fitfile";
	print AB $fit_cover_letter;
	close AB;

	my $ghafile = $config->template_directory;
	$ghafile .= $config->gha_cover_letter_html || "/gha_cover_letter_html.tmpl";
	my $gha_defaultfile = $config->template_directory."/gha_default_cover_letter.tmpl";
	my $gha_cover_letter;
	open FILE, $gha_defaultfile;
	while( <FILE> ) {
		$gha_cover_letter .= $_;
	}
	close FILE;
	print $ghafile . "\n" if $Debug;
	open AB, ">$ghafile";
	print AB $gha_cover_letter;
	close AB;

	my $gwbfile = $config->template_directory;
	$gwbfile .= $config->gwb_cover_letter_html || "/gwb_cover_letter_html.tmpl";
	my $gwb_defaultfile = $config->template_directory."/gwb_default_cover_letter.tmpl";
	my $gwb_cover_letter;
	open FILE, $gwb_defaultfile;
	while( <FILE> ) {
		$gwb_cover_letter .= $_;
	}
	close FILE;
	print $gwbfile . "\n" if $Debug;
	open AB, ">$gwbfile";
	print AB $gwb_cover_letter;
	close AB;

	my $hrafile = $config->template_directory;
	$hrafile .= $config->hra_cover_letter_html || "/hra_cover_letter_html.tmpl";
	my $hra_defaultfile = $config->template_directory."/hra_default_cover_letter.tmpl";
	my $hra_cover_letter;
	open FILE, $hra_defaultfile;
	while( <FILE> ) {
		$hra_cover_letter .= $_;
	}
	close FILE;
	print $hrafile . "\n" if $Debug;
	open AB, ">$hrafile";
	print AB $hra_cover_letter;
	close AB;

	print $input->redirect (-uri => $config->admin_path );
	exit;
	}
elsif($input->param('revert_back') eq 'email'){
	my $efile = $config->template_directory . $config->attaboy_text;
	my $default_attaboyfile = $config->template_directory."/attaboy_default.tmpl";
	my $default_attaboy;
	open FILE, $default_attaboyfile;
	while( <FILE> ) {
		$default_attaboy .= $_;
	}
	print $efile . "\n" if $Debug;
	open AB, ">$efile";
	print AB $default_attaboy;
	close AB;
	my $bfile = $config->template_directory . $config->bday_text;
	my $default_bdayfile = $config->template_directory."/bday_default.tmpl";
	my $default_bday;
	open FILE, $default_bdayfile;
	while( <FILE> ) {
		$default_bday .= $_;
	}
	print $bfile . "\n" if $Debug;
	open BD, ">$bfile";
	print BD $default_bday;
	close BD;

	print $input->redirect (-uri => $config->admin_path );
	exit;
	}
elsif($input->param('edit') eq 'email'){
	my $dumpfile 	= $config->authenticate_dir."/CRC_dump_of_1.user";;
	my $user1 		= HealthStatus::User->new( \%hash );
	$user1->db_id( '1' );
	if (!(-e "$dumpfile")) {
		error( "$dumpfile does not exist, please contact HealthStatus.com - 317.823.2687" );
		exit 1;
		}
	$user1 = do $dumpfile;
	bless($user1, "HealthStatus::User");
	$user1->{config} = $config;
	my $config_file = $config->conf_config_dir."/healthstatus.conf";
	my $health = HealthStatus->new(
		{
		assessment => "CRC",
		user       => $user1,
		config     => $config_file,
		}
		);
	$user1->set_non_standard;
	$health->assess( $user1 );
	$user1->pretty_print if $Debug;
	foreach my $key ( keys %$user1 )
		{
		$input{$key} = $user1->{$key};
		$input->param("$key","$user1->{$key}");
		}
	$input{config} 			= $config->as_hash();
	
	my $efile = $config->template_directory . $config->attaboy_text;
	print $efile . "\n" if $Debug;
	open AB, $efile;
	my @attaboy_email =  <AB>;
	close AB;
	foreach(@attaboy_email){$input{attaboy_email} .= $_ . ' ';}
	$input{attaboy_email} =~ s/\n\s*\n/<p>/g;
	my $bfile = $config->template_directory .$config->bday_text;
	print $bfile . "\n" if $Debug;
	open BD, $bfile;
	my @bday_email = <BD>;
	close BD;
	foreach (@bday_email){ $input{bday_email} .= $_ . ' ';}
	$input{bday_email} =~ s/\n\s*\n/<p>/g;
	$template = $config->template_directory . 'edit_email.tmpl';
	print $template . "\n" if $Debug;
	$output = Text::Template::fill_in_file( $template , HASH => \%input );
		error( $Text::Template::ERROR, 'Template file error ' . $template )
		if $Text::Template::ERROR;

	}
elsif($input->param('send_email')){
	my $message ;
	my $subject;
		$message  = $input->param('email_text');
		$message =~ s/<p>/\n\n/g;
	if($input->param('flag') eq 'bday'){
		$subject = $config->bday_subject  ; 
	} else {
		$subject = $config->attaboy_subject  ; 
	}
	
	my %mail = ( To      => $input->param('email'),
	    From    => $config->email_from,
	    Subject => $subject,
	    Message => $message,
	    smtp    =>  $config->email_smtp
	   );

	sendmail(%mail) or die $Mail::Sendmail::error;
	print $input->redirect (-uri => $config->admin_path );
	exit;
	}
elsif($input->param('edit') eq 'letter'){
	my $crcfile = $config->template_directory;
	$crcfile .= $config->crc_cover_letter_html || "/crc_cover_letter_html.tmpl";
	print $crcfile . "\n" if $Debug;
	open AB, $crcfile;
	my @crc_cover =  <AB>;
	close AB;
	foreach(@crc_cover){$input{crc_cover} .= $_ . ' ';}
	$input{crc_cover} =~ s/\n\s*\n/<p>/g;

	my $drcfile = $config->template_directory;
	$drcfile .= $config->drc_cover_letter_html || "/drc_cover_letter_html.tmpl";
	print $drcfile . "\n" if $Debug;
	open AB, $drcfile;
	my @drc_cover =  <AB>;
	close AB;
	foreach(@drc_cover){$input{drc_cover} .= $_ . ' ';}
	$input{drc_cover} =~ s/\n\s*\n/<p>/g;

	my $fitfile = $config->template_directory;
	$fitfile .= $config->fit_cover_letter_html || "/fit_cover_letter_html.tmpl";
	print $fitfile . "\n" if $Debug;
	open AB, $fitfile;
	my @fit_cover =  <AB>;
	close AB;
	foreach(@fit_cover){$input{fit_cover} .= $_ . ' ';}
	$input{fit_cover} =~ s/\n\s*\n/<p>/g;

	my $ghafile = $config->template_directory;
	$ghafile .= $config->gha_cover_letter_html || "/gha_cover_letter_html.tmpl";
	print $ghafile . "\n" if $Debug;
	open AB, $ghafile;
	my @gha_cover =  <AB>;
	close AB;
	foreach(@gha_cover){$input{gha_cover} .= $_ . ' ';}
	$input{gha_cover} =~ s/\n\s*\n/<p>/g;

	my $gwbfile = $config->template_directory;
	$gwbfile .= $config->gwb_cover_letter_html || "/gwb_cover_letter_html.tmpl";
	print $gwbfile . "\n" if $Debug;
	open AB, $gwbfile;
	my @gwb_cover =  <AB>;
	close AB;
	foreach(@gwb_cover){$input{gwb_cover} .= $_ . ' ';}
	$input{gwb_cover} =~ s/\n\s*\n/<p>/g;

	my $hrafile = $config->template_directory;
	$hrafile .= $config->hra_cover_letter_html || "/hra_cover_letter_html.tmpl";
	print $hrafile . "\n" if $Debug;
	open AB, $hrafile;
	my @hra_cover =  <AB>;
	close AB;
	foreach(@hra_cover){$input{hra_cover} .= $_ . ' ';}
	$input{hra_cover} =~ s/\n\s*\n/<p>/g;

	$template = $config->template_directory . 'edit_covers.tmpl';
	print $template . "\n" if $Debug;
	$output = Text::Template::fill_in_file( $template , HASH => \%input );
		error( $Text::Template::ERROR, 'Template file error ' . $template )
		if $Text::Template::ERROR;
	}
elsif($input->param('edit') eq 'links'){
	}

if ($config->html_use_ssi){
	require CGI::SSI;
	my $ssi = CGI::SSI->new();
	$results = $ssi->process($output);
	}
else 	{ $results = $output }

#output the next template
if( exists $input{cookie} ){
	my $cookie = $input{cookie};
	print $input->header( -cookie=> $cookie ), $results;
	}
else	{
	print $input->header(), $results;
	}

=head1 BUGS

* none that i've found so far.

=head1 TO DO

* nothing yet

=head1 AUTHOR

Greg White <gwhite@healthstatus.com>

=head1 COPYRIGHT

Copyright 2001-2008, HealthStatus.com

=cut

1;