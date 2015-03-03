#!/usr/bin/perl
# $
# $	(Mail select version 3.8)
# $
# $     Mail Select was first made for myself because I was interested in sending binary
# $     files via sendmail, this if you have been a regular visitor to my site was not actually
# $     completed until 2.8.  Now I have made a sendmail program for windows and windows NT
# $     my mail select program can be used by the win32 sector. (N/A Yet)
# $
# $	This code is distributed in the hope that is will be useful but WITHOUT ANY
# $	WARRANTY. ALL WARRANTIES, EXPRESS OR IMPLIED ARE HEREBY DISCLAMED. This includes
# $	but isn't limited to warranties of MERCHANTABILITY or FITNESS FOR A PARTICULAR
# $	PURPOSE.  The RESELLING of this code is STRICTLY PROHIBITED.
# $
# $     $Revision: 3.8
# $     $Author: Paul Williams
# $     $Email: paul@rainbow.nwnet.co.uk
# $     $URL: http://www.cougasoft.org/
# $     $Created: 17/11/1996 16:07
# $     $Last Modified: 01/04/2000 18:16
# $
# $	Copyright 1996, 1997, 1998, 1999 Cougasoft.  All rights reserved.
# $


use Mail::Sendmail;
use MIME::QuotedPrint;
use MIME::Base64;
use MIME::Types;
use CGI;
use CGI::Carp;
use Email::Valid;
use DBI;


	# $ Every time the script is loading I do a couple of error checks to make sure
	# $ that everything is running well before anything happend (like the data file is
	# $ present and the email program is there). If you know everything works you can
	# $ set \$SPEED to a positive value.
	my $SPEED = 0;

my %mime =
(
       #-------------------------------------<TEXT>-----
       'HTML',		"text/html",
       'HTM',		"text/html",
       'STM',		"text/html",
       'SHTML',		"text/html",
       'TXT',		"text/plain",
       'PREF',		"text/plain",
       'AIS',		"text/plain",
       'RTX',		"text/richtext",
       'TSV',		"text/tab-separated-values",
       'NFO',		"text/warez-info",
       'ETX',		"text/x-setext",
       'SGML',		"text/x-sgml",
       'SGM',		"text/x-sgml",
       'TALK',		"text/x-speech",
       'CGI',		"text/plain",    #  we want these two as text files
       'PL',		"text/plain",    #  and not application/x-httpd-cgi
       #-------------------------------------<IMAGE>----
       'COD',           "image/cis-cod",
       'FID',           "image/fif",
       'GIF',           "image/gif",
       'ICO',           "image/ico",
       'IEF',           "image/ief",
       'JPEG',          "image/jpeg",
       'JPG',           "image/jpeg",
       'JPE',           "image/jpeg",
       'PNG',           "image/png",
       'TIF',           "image/tiff",
       'TIFF',          "image/tiff",
       'MCF',		"image/vasa",
       'RAS',		"image/x-cmu-raster",
       'CMX',		"image/x-cmx",
       'PCD',		"image/x-photo-cd",
       'PNM',		"image/x-portable-anymap",
       'PBM',		"image/x-portable-bitmap",
       'PGM',		"image/x-portable-graymap",
       'PPM',		"image/x-portable-pixmap",
       'RGB',		"image/x-rgb",
       'XBM',		"image/x-xbitmap",
       'XPM',		"image/x-xpixmap",
       'XWD',		"image/x-xwindowdump",
       #-------------------------------------<APPS>-----
       'EXE',		"application/octet-stream",
       'BIN',		"application/octet-stream",
       'DMS',		"application/octet-stream",
       'LHA',		"application/octet-stream",
       'CLASS',		"application/octet-stream",
       'DLL',		"application/octet-stream",
       'AAM',		"application/x-authorware-map",
       'AAS',		"application/x-authorware-seg",
       'AAB',		"application/x-authorware-bin",
       'VMD',		"application/vocaltec-media-desc",
       'VMF',		"application/vocaltec-media-file",
       'ASD',		"application/astound",
       'ASN',		"application/astound",
       'DWG',		"application/autocad",
       'DSP',		"application/dsptype",
       'DFX',		"application/dsptype",
       'EVY',		"application/envoy",
       'SPL',		"application/futuresplash",
       'IMD',		"application/immedia",
       'HQX',		"application/mac-binhex40",
       'CPT',		"application/mac-compactpro",
       'DOC',		"application/msword",
       'ODA',		"application/oda",
       'PDF',		"application/pdf",
       'AI',		"application/postscript",
       'EPS',		"application/postscript",
       'PS',		"application/postscript",
       'PPT',		"application/powerpoint",
       'RTF',		"application/rtf",
       'APM',		"application/studiom",
       'XAR',		"application/vnd.xara",
       'ANO',		"application/x-annotator",
       'ASP',		"application/x-asap",
       'CHAT',		"application/x-chat",
       'BCPIO',		"application/x-bcpio",
       'VCD',		"application/x-cdlink",
       'TGZ',		"application/x-compressed",
       'Z',		"application/x-compress",
       'CPIO',		"application/x-cpio",
       'PUZ',		"application/x-crossword",
       'CSH',		"application/x-csh",
       'DCR',		"application/x-director",
       'DIR',		"application/x-director",
       'DXR',		"application/x-director",
       'FGD',		"application/x-director",
       'DVI',		"application/x-dvi",
       'LIC',		"application/x-enterlicense",
       'EPB',		"application/x-epublisher",
       'FAXMGR',	"application/x-fax-manager",
       'FAXMGRJOB',	"application/x-fax-manager-job",
       'FM',		"application/x-framemaker",
       'FRAME',		"application/x-framemaker",
       'FRM',		"application/x-framemaker",
       'MAKER',		"application/x-framemaker",
       'GTAR',		"application/x-gtar",
       'GZ',		"application/x-gzip",
       'HDF',		"application/x-hdf",
       'INS',		"application/x-insight",
       'INSIGHT',	"application/x-insight",
       'INST',		"application/x-install",
       'IV',		"application/x-inventor",
       'JS',		"application/x-javascript",
       'SKP',		"application/x-koan",
       'SKD',		"application/x-koan",
       'SKT',		"application/x-koan",
       'SKM',		"application/x-koan",
       'LATEX',		"application/x-latex",
       'LICMGR',	"application/x-licensemgr",
       'MAIL',		"application/x-mailfolder",
       'MIF',		"application/x-mailfolder",
       'NC',		"application/x-netcdf",
       'CDF',		"application/x-netcdf",
       'SDS',		"application/x-onlive",
       'SGI-LPR',	"application/x-sgi-lpr",
       'SH',		"application/x-sh",
       'SHAR',		"application/x-shar",
       'SWF',		"application/x-shockwave-flash",
       'SPRITE',	"application/x-sprite",
       'SPR',		"application/x-sprite",
       'SIT',		"application/x-stuffit",
       'SV4CPIO',	"application/x-sv4cpio",
       'SV4CRC',	"application/x-sv4crc",
       'TAR',		"application/x-tar",
       'TARDIST',	"application/x-tardist",
       'TCL',		"application/x-tcl",
       'TEX',		"application/x-tex",
       'TEXINFO',	"application/x-texinfo",
       'TEXI',		"application/x-texinfo",
       'T',		"application/x-troff",
       'TR',		"application/x-troff",
       'TROFF',		"application/x-troff",
       'MAN',		"application/x-troff-man",
       'ME',		"application/x-troff-me",
       'MS',		"application/x-troff-ms",
       'TVM',		"application/x-tvml",
       'TVM',		"application/x-tvml",
       'USTAR',		"application/x-ustar",
       'SRC',		"application/x-wais-source",
       'WKZ',		"application/x-wingz",
       'ZIP',		"application/x-zip-compressed",
       'ZTARDIST',	"application/x-ztardist",
       #-------------------------------------<AUDIO>----
       'AU',		"audio/basic",
       'SND',		"audio/basic",
       'ES',		"audio/echospeech",
       'MID',		"audio/midi",
       'KAR',		"audio/midi",
       'MPGA',		"audio/mpeg",
       'MP2',		"audio/mpeg",
       'TSI',		"audio/tsplayer",
       'VOX',		"audio/voxware",
       'AIF',		"audio/x-aiff",
       'AIFC',		"audio/x-aiff",
       'AIFF',		"audio/x-aiff",
       'MID',		"audio/x-midi",
       'MP3',		"audio/x-mpeg",
       'MP2A',		"audio/x-mpeg2",
       'MPA2',		"audio/x-mpeg2",
       'M3U',		"audio/x-mpegurl",
       'MP3URL',	"audio/x-mpegurl",
       'PAT',		"audio/x-pat",
       'RAM',		"audio/x-pn-realaudio",
       'RPM',		"audio/x-pn-realaudio-plugin",
       'RA',		"audio/x-realaudio",
       'SBK',		"audio/x-sbk",
       'STR',		"audio/x-str",
       'WAV',		"audio/x-wav",
       #-------------------------------------<VIDEO>----
       'MPEG',		"video/mpeg",
       'MPG',		"video/mpeg",
       'MPE',		"video/mpeg",
       'QT',		"video/quicktime",
       'MOV',		"video/quicktime",
       'VIV',		"video/vivo",
       'VIVO',		"video/vivo",
       'MPS',		"video/x-mpeg-system",
       'SYS',		"video/x-mpeg-system",
       'MP2V',		"video/x-mpeg2",
       'MPV2',		"video/x-mpeg2",
       'AVI',		"video/x-msvideo",
       'MV',		"video/x-sgi-movie",
       'MOVIE',		"video/x-sgi-movie",
       #-------------------------------------<EXTRA>----
       'PDB',		"chemical/x-pdb",
       'XYZ',		"chemical/x-pdb",
       'CHM',		"chemical/x-cs-chemdraw",
       'SMI',		"chemical/x-daylight-smiles",
       'SKC',		"chemical/x-mdl-isis",
       'MOL',		"chemical/x-mdl-molfile",
       'RXN',		"chemical/x-mdl-rxn",
       'SMD',		"chemical/x-smd",
       'ACC',		"chemical/x-synopsys-accord",
       'ICE',		"x-conference/x-cooltalk",
       'SVR',		"x-world/x-svr",
       'WRL',		"x-world/x-vrml",
       'VRML',		"x-world/x-vrml",
       'VRJ',		"x-world/x-vrt",
       'VRJT',		"x-world/x-vrt",
);

#
# $--------------------------------------------------------------------------------------------
#
#  M  A  I  N     P  R  O  G  R  A  M
#
# $--------------------------------------------------------------------------------------------
#

	# $ I have changed from using do to my own preference subroutine, it calls all the
        # $ data in as keys and data then places them in a %PREF hash.
        unless ( (my $pref = &preferences("data/ms-pref.pref", 28) ) == 1
		or (my $pref2 = &preferences("ms-pref.pref", 28) ) == 1)
	{
       		print "Content-type: text/plain\n\n";
        	print "Error initiating preference file(s);\n\n";
        	print "$pref\n$pref2\n";
        	exit;
	}

#
# $--------------------------------------------------------------------------------------------
#
#  S  O  R  T    F  O  R  M    I  N  P  U  T
#
# $--------------------------------------------------------------------------------------------
#

	my (@files, @problem, %INPUT, %PREF);		# Declare global variables

my $input = new CGI();
my %INPUT = $input->Vars();

push @files, $input->param('files1') if $input->param('files1');
push @files, $input->param('files2') if $input->param('files2');
# Handle demonstration option in the form 
push @files, $input->param('demo') if $input->param('demo');

        # $ Only try to read input on STDIN if we have a CONTENT_LENGTH
#        if ($ENV{'CONTENT_LENGTH'})
#  	{
#		my (@pairs, $pair, $input, $name, $value);

#		read(STDIN, $input, $ENV{'CONTENT_LENGTH'});

#			@pairs = split(/&/, $input);

#                                foreach $pair (@pairs) {
#                                ($name, $value) = split(/=/, $pair);

#                                $value =~ tr/+/ /;
#                                $value =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;

#                        $INPUT{$name} = $value;

#			push @files, $value if $name eq 'files';
# 		}
#  	}

#
# $--------------------------------------------------------------------------------------------
#
#  A  C  T  I  O  N    =    M  A  I  L    I  T
#
# $--------------------------------------------------------------------------------------------
#

		&missing('NAME')  unless $INPUT{'name'};
		&missing('EMAIL') unless $INPUT{'email'};
		&missing('FILE')  unless $files[0];
carp "Mailcheck";
		&mailcheck($INPUT{'email'});#, &send_mail(), &addlog();
carp "back Mailcheck";
		&send_mail();
carp "back send_mail";
		&addlog();
carp "back addlog";
		&notify('500 Internal Server Error', "The following files weren't downloaded due to an error<BR>[@problem]<BR>", 2) if @problem;
		my $city = $INPUT{'CITY'} if $INPUT{'CITY'};
		my $STATE = $INPUT{'STATE'} if $INPUT{'STATE'};
		my $ZIP = $INPUT{'ZIP'} if $INPUT{'ZIP'};
		my $GEO = $INPUT{'GEO'} if $INPUT{'GEO'};
		my $physician = $INPUT{'physician'} if $INPUT{'physician'};
		my $IP = $INPUT{'IP'} if $INPUT{'IP'};
		my $results1;
		my $results = "E-Book was requested by:\n     $INPUT{'name'}";
		$results .= " from" if($city || $STATE || $ZIP || $GEO);
		if ($city){			
			$results .= ", $city";
			$results1 .= "|| $city";
		}
		if ($STATE){
			$results .= ", $STATE";
			$results1 .= "|| $STATE";
		}
		if ($ZIP){
			$results .= ", $ZIP";
			$results1 .= "|| $ZIP";
		}
		if ($GEO){
			$results .= ", $GEO";
			$results1 .= "|| $GEO";
		}
		if ($physician){
			$results .= ", $physician";
			$results1 .= "|| $physician";
		}
		if ($IP){			
			$results1 .= "|| $IP";
		}
		$results .= " requested:\n     $files[0]\n$physician\n     From: $ENV{'HTTP_REFERER'}\n     they can be contacted at: $INPUT{'email'}\n\n";		
		
		$results .= "\n$INPUT{'name'} ";
		$results .= $results1;
		$results .= "|| $INPUT{'email'} || ".&date;
		
		# send the email to the administrator
		%mail = ( 
			  To => 'gwhite@healthstatus.com',			  
			  From    => 'info@healthstatus.com',
			  Subject => "Information request from HealthStatus.com",
			  Message => $results,
			  smtp => 'local-mail.healthstatus.com'

			);
		sendmail(%mail) or die &error("Mail program error - $Mail::Sendmail::error", "Error", ".net request - sendmail 01");
		&insert_db();
        	if ($PREF{'REDIRECT'})
         	{
         		print "Location: $PREF{'REDIRECT'}\n\n";
				exit 0;
         	}

		&notify('Success !', "File(s) have been successfully sent", 2);
		
		exit;

#
# $--------------------------------------------------------------------------------------------
#
#  A  C  T  I  O  N    =    E  L  S  E
#
# $--------------------------------------------------------------------------------------------
#

#	else
#  	{
        &status() unless $SPEED;
		my (@CHECKED, @allfiles);

		opendir FILES, $PREF{'FILEBASE'} or &notify('500 Internal Server Error', "I was not able to open the download directory<BR>chmod the dir to www readable (755).<BR><BR>If this is not admin, please let him/her<BR> know about this problem.", 0);
           		@allfiles = sort grep(!/^\.\.?$/,readdir FILES);
		closedir FILES;

        	if ($ENV{'QUERY_STRING'} eq 'action=random')
         	{
               		$CHECKED[rand($#allfiles + 1)] = 'CHECKED';
         	}

		&top_html("Download...", 1);
	   	print "<FORM METHOD='POST' ACTION='$ENV{'SCRIPT_NAME'}?action=mail-it'>\n" .
	      	   "\n" .
	       	   "<CENTER><TABLE BGCOLOR='$PREF{'RESHADE'}'>\n";

        	   for (my $i = 0; $i <= $#allfiles; $i++)
         	   {
			print "<TR>\n";
                	print "<TD><INPUT type=checkbox NAME='files' value='$allfiles[$i]' $CHECKED[$i]><FONT size='-1'>$allfiles[$i]</FONT></TD>\n";
                	$i++;
                	print "<TD><INPUT type=checkbox NAME='files' value='$allfiles[$i]' $CHECKED[$i]><FONT size='-1'>$allfiles[$i]</FONT></TD>\n" if $allfiles[$i];
                	print "<TD><FONT size='-1'>&nbsp;</FONT></TD>\n" unless $allfiles[$i];
			print "</TR>\n";
         	   }

           	print "</TABLE></CENTER><BR><BR>\n\n" .
		   "<CENTER><TABLE BGCOLOR='$PREF{'TBCOLOR'}'><TR ALIGN=RIGHT>\n" .
	      	   "<TD><TT>&nbsp;Name&nbsp; </FONT></TT>\n" .
	      	   "<TD><INPUT type=text size=30 name='name'></TD>\n" .
	      	   "</TR>\n" .
	      	   "<TR ALIGN=RIGHT>\n" .
	      	   "<TD><TT>&nbsp;E-mail&nbsp; </FONT></TT>\n" .
	      	   "<TD><INPUT type=text size=30 name='email'></TD>\n" .
	      	   "</TR>\n" .
	      	   "<TR ALIGN=RIGHT BGCOLOR='$PREF{'BGCOLOR'}'><TD></TD>\n" .
	      	   "<TD><FONT SIZE=-1><INPUT type=submit value='d o w n l o a d'></FONT></TD>\n" .
	      	   "</TR>\n" .
	      	   "<TR><TD></TD>\n" .
	      	   "<TD></FORM></TD></TR>\n";
	   	print "</TABLE></CENTER>\n";
		&bottom(1);
#  }

#
# $--------------------------------------------------------------------------------------------
#
#  S  U  B  R  O  T  I  N  E  S
#
# $--------------------------------------------------------------------------------------------
#

	sub top_html
   	{
		my ($title, $more) = @_;

		print "Content-type: text/html\n\n" .
                # $ Please don't change this, people also seem to like to alter this which is
                # $ also a little dis-heartening, especially as its hidden inside the html output
		    "<!-- © Copyright 1998 Cougasoft [paul\@rainbow.nwnet.co.uk] -->\n" .
	    	    "<HTML>\n" .
	    	    "<HEAD>\n" .
	    	    "	 <TITLE>Mail Select - $title</TITLE>\n" .
	    	    "</HEAD>\n" .
	    	    "<BODY TEXT='$PREF{'BODYTEXT'}' BGCOLOR='$PREF{'BGCOLOR'}' LINK='$PREF{'LINK'}' VLINK='$PREF{'VLINK'}' ALINK='$PREF{'ALINK'}' BACKGROUND='$PREF{'BACKGROUND'}'>\n\n";
		print "<CENTER><IMG SRC='$PREF{'GIF'}'></CENTER>\n\n";

		print "<CENTER><FONT SIZE=-1>[<A HREF='$PREF{'HOME'}'>Home</A>] - [<A HREF='$ENV{'SCRIPT_NAME'}?action=random'>Random download</A>] </FONT></CENTER><BR>" if $more;
   	}

#
# $--------------------------------------------------------------------------------------------
#
#  S  U  B  -  A  D  D    L  I  N  K
#
# $--------------------------------------------------------------------------------------------
#

        # $ Add the download to the logfile, this isn't a statistical addition to my mail
        # $ select program but just a rough user download (with the email address it was
        # $ sent to.

	sub addlog
  	{
     		my ($init, $date) = (0, &date);
     		$PREF{'MAXIMUM'} -= 1;

		open(LINK, "$PREF{'DATA'}");
			my @link = <LINK>;
		close(LINK);

		open(FILE, ">$PREF{'DATA'}") || &notify("500 Internal Server Error", "I was not able to write to the \$data file<BR>chmod it to 666 and try again<BR><BR>If this is not admin, please let him/her<BR> know about this problem.", 0);
             		print FILE "$INPUT{'name'}||$INPUT{'email'}||$date||@files||" . time . "||\n";
	     		while ($init != $PREF{'MAXIMUM'}) {
	     		print FILE "$link[$init]";
	     		$init++;
	     		}
		close(FILE);
  	}

#
# $--------------------------------------------------------------------------------------------
#
#  S  U  B  -  S  E  N  D    M  A  I  L
#
# $--------------------------------------------------------------------------------------------
#

	sub send_mail
  	{
        	my @boundaryv = (0..9, 'A'..'F');
    		$PREF{'FOOTER'} =~ s/\\n/\n/g;
		$| = 1;

    		foreach my $file (@files)
     		{	next if $file eq "I want a demo";	
        		do { push @problem, "$file"; carp "problem at line 462- $PREF{'FILEBASE'}/$file"; next; } if !-r "$PREF{'FILEBASE'}/$file"; # checks the existence and readability
        		my ($boundary, $ext) = (undef, undef);

        		#--------------------------------------------------- Obtain content-type of file
#			($ext) = $file =~ m,\.([^\.]*)$,;
#	 		$ext =~ tr,a-z,A-Z,;
#         		my $fext = $mime{$ext};
			
			my $types = MIME::Types->new;
			my $mime = $types->mimeTypeOf($file);


        		#--------------------------------------------------- Generate multipart boundary
  			srand(time ^ $$);

  			for (my $i = 0; $i++ < 24;)
  	 		{
  	       			$boundary .= $boundaryv[rand(@boundaryv)];
  	 		}

        		#--------------------------------------------------- Send attatchments etc...

			# send the email to the administrator
			%mail = ( To => $INPUT{'email'},
				  From    => 'info@healthstatus.com',
				  Subject => "Information requested from HealthStatus",
				  Message => $results,
				  smtp => 'local-mail.healthstatus.com'
				);

			my $boundary = "====" . time() . "====";
			$mail{'content-type'} = "multipart/mixed; boundary=\"$boundary\"";

			my $message = encode_qp( "The information you requested." );
			$message = encode_qp ("\n$PREF{FOOTER}\n") if ($PREF{'FOOTER'});

			open (F, "$PREF{'FILEBASE'}/$file") or die "Cannot read $file: $!";
			binmode F; undef $/;
			$mail{body} = encode_base64(<F>);
			close F;

			$boundary = '--'.$boundary;
	$mail{body} = <<END_OF_BODY;
$boundary
Content-Type: text/plain; charset="iso-8859-1"
Content-Transfer-Encoding: quoted-printable

$message
$boundary
Content-Type: application/octet-stream; name="$file"
Content-Transfer-Encoding: base64
Content-Disposition: attachment; filename="$file"

$mail{body}
$boundary--
END_OF_BODY


			sendmail(%mail) or die &error("Mail program error - $Mail::Sendmail::error", "Error", ".net request - sendmail 01");
     		}
  	}




# $--------------------------------------------------------------------------------------------
	sub send_mail_old
  	{
        	my @boundaryv = (0..9, 'A'..'F');
    		$PREF{'FOOTER'} =~ s/\\n/\n/g;
		$| = 1;

    		foreach my $file (@files)
     		{
        		do { push @problem, "$file"; next; } if !-r "$PREF{'FILEBASE'}/$file"; # checks the existence and readability
        		my ($boundary, $ext) = (undef, undef);

        		#--------------------------------------------------- Obtain content-type of file
			($ext) = $file =~ m,\.([^\.]*)$,;
	 		$ext =~ tr,a-z,A-Z,;
         		my $fext = $mime{$ext};

        		#--------------------------------------------------- Generate multipart boundary
  			srand(time ^ $$);

  			for (my $i = 0; $i++ < 24;)
  	 		{
  	       			$boundary .= $boundaryv[rand(@boundaryv)];
  	 		}

        		#--------------------------------------------------- Send attatchments etc...
        		my $date = &date();
        		open MAIL, "| $PREF{'MAILPGRM'} -t" or &notify("500 Internal Server Error", "I was not able to open the mail program<BR>contact the server's technical administrator.<BR><BR>If this is not admin, please let him/her<BR> know about this problem.", 0);
				print MAIL "To: $INPUT{'name'} <$INPUT{'email'}>\n";
           			print MAIL "From: $PREF{'YOURNAME'} <$PREF{'YOUREMAIL'}>\n";
           			print MAIL "Date: $date\n";
  	   			print MAIL "Organization: $PREF{'ORG'}\n" if ($PREF{'ORG'});
           			print MAIL "X-Mailer: cStandalone 2.05 [en] (CS; I)\n";
           			print MAIL "MIME-Version: 1.0\n";
	   			print MAIL "Subject: HealthStatus.com File ($file)\n";
           			print MAIL "Content-Type: multipart/mixed; boundary=\"------------$boundary\"\n";
           			print MAIL "\n";
           			print MAIL "This is a multi-part message in MIME format.\n";

           			print MAIL "--------------$boundary\n";
	   			print MAIL "Content-Type: text/plain; charset=us-ascii\n";
	   			print MAIL "Content-Transfer-Encoding: 7bit\n\n";
           			print MAIL "Attatchment: $file\n";
	   			print MAIL "\n\n$PREF{FOOTER}\n" if ($PREF{'FOOTER'});

	   			if ($fext && $fext !~ /^text/)
            			{
                			print MAIL "--------------$boundary\n";
					print MAIL "Content-Type: $fext; name=\"$file\"\n";
					print MAIL "Content-Transfer-Encoding: base64\n";
                			print MAIL "Content-Disposition: inline; filename=\"$file\"\n\n";

           				my $buf; $/=0;
                        		open INPUT, "$PREF{'FILEBASE'}/$file"; # should be readable, we checked above [-r]
   					binmode INPUT if ($^O eq 'NT' or $^O eq 'MSWin32');
   					while(read(INPUT, $buf, 60*57))
					{
         					print MAIL &encode_base64($buf);
    			 		}
	   				close INPUT;

                			print MAIL "\n--------------$boundary--\n";
            			}
           			else
            			{
                			print MAIL "--------------$boundary\n";
					print MAIL "Content-Type: $fext; charset=us-ascii; name=\"$file\"\n";
					print MAIL "Content-Transfer-Encoding: 7bit\n";
                			print MAIL "Content-Disposition: inline; filename=\"$file\"\n\n";

           				open INPUT, "$PREF{'FILEBASE'}/$file"; # should be readable, we checked above [-r]
	    	  	 		print MAIL while (<INPUT>);
					close INPUT;

                			print MAIL "\n--------------$boundary--\n";
            			}

           			print MAIL "\n";
			close MAIL;
     		}
  	}

#
# $--------------------------------------------------------------------------------------------
#
#  S  U  B  -  M  A  I  L  C  H  E  C  K
#
# $--------------------------------------------------------------------------------------------
#

        # $ Checks the argument $_[0] for correct email syntax, this little regexp
        # $ doesn't actually check everything but i think its good enough for now ;)

	sub mailcheck
	{
	my $eaddress = shift;
#     		if  (($_[0] =~ /[,|\/\\]|(@.*@)|(\.\.)|(\.$)/)
#         		|| ($_[0] !~/^[\w\-\.]+[\%\+]?[\w\-\.]*\@[0-9a-zA-Z\-]+\.[0-9a-zA-Z\-\.]+$/))
#                {
#                        &notify("E-mail address problem !", "There is a problem with your e-mail !", 1);
#     		}
		my $address = Email::Valid->address($eaddress);
     		&notify("E-mail address problem !", "There is a problem with your e-mail !", 1) unless $address;
  	}

#
# $--------------------------------------------------------------------------------------------
#
#  S  U  B  -  E  N  C  O  D  E    B  A  S  E  6  4
#
# $--------------------------------------------------------------------------------------------
#

 	sub encode_base64 #($)
  	{
    		my ($res, $eol, $padding) = ("", "\n", undef);

    		while (($_[0] =~ /(.{1,45})/gs))
     		{
	 		$res .= substr(pack('u', $1), 1);
	 		chop $res;
     		}

    		$res =~ tr#` -_#AA-Za-z0-9+/#;               		# ` help emacs
    		$padding = (3 - length($_[0]) % 3) % 3;   		# fix padding at the end

    		$res =~ s#.{$padding}$#'=' x $padding#e if $padding;    # pad eoedv data with ='s
    		$res =~ s#(.{1,76})#$1$eol#g if (length $eol);          # lines of at least 76 characters

    		return $res;
  	}

#
# $--------------------------------------------------------------------------------------------
#
#  S  U  B  -  D  A  T  E
#
# $--------------------------------------------------------------------------------------------
#

	# Date, no longer returns global \$date variable.
	#
	# This is my new date subroutine, looks a complete mess I know, nothing I can
	# do about it but it does the job (and does it very well I think :)  Wouldn't
	# suggest altering it unless you really know what your doing.
	sub date
	{
		my @days = qw(Sunday Monday Tuesday Wednesday Thursday Friday Saturday);
		my @months = qw(January February March April May June July August September October November December);

		# $ '$_[0]' is read only so we must copy the contents to a new variable and
		# $ then we can make our modifications, if there are no substitutions I assume
		# $ there is either no argument or some kind of problem with the string.
		my ($date, $timevar, %D) = (shift, shift, undef);

		($D{sec}, $D{min}, $D{hour}, $D{mday}, $D{mon}, $D{year}, $D{wday}, $D{yday}) = localtime($timevar?$timevar:time);

		$D{sec}		= "0$D{sec}" if ($D{sec} < 10);
		$D{min}		= "0$D{min}" if ($D{min} < 10);
		$D{hour}	= "0$D{hour}" if ($D{hour} < 10);
		$D{year}	= $D{year}+1900;

		# $ Now I need to add a few extra variables to the %DATE hash, namely the
		# $ literal day, month and wether the time is AM or PM.
		$D{day}		= sprintf "%." . (($D{wday} == 2 or $D{wday}==4)?4:3) . 's', $days[$D{wday}];
		$D{month}	= sprintf "%." . ($D{mon} == 9?4:3) . 's', $months[$D{mon}];
		$D{lday}	= $days[$D{wday}];
		$D{lmonth}	= $months[$D{mon}];

		$D{'24hour'}	= $D{hour};
		$D{ampm}	= $D{hour} >= 12 ? 'PM' : 'AM';


		return ($date =~ s/\[([^\]]*)\]/$D{$1}/g) ? $date
			: "$D{'month'} $D{'mday'}, $D{'year'} - $D{'hour'}:$D{'min'}:$D{'sec'}";
	}

#
# $--------------------------------------------------------------------------------------------
#
#  S  U  B  -  S  T  A  T  U  S  ( C  H  E  C  K )
#
# $--------------------------------------------------------------------------------------------
#

 	# $ Check the status of the user, if the data file can't be found we let
        # $ the user know, this is part of my error checking coding, I try to make
        # $ it as easy as possible to catch errors with all of my scripts

	sub status
        {
		my ($datafile, $filebase, $mailprog);

		unless (-e "$PREF{'DATA'}" && -d "$PREF{'FILEBASE'}" && -e "$PREF{'MAILPGRM'}")
	 	{
	    		$datafile = "Log Data File" if (!-e "$PREF{'DATA'}");
	    		$filebase = "Download File Base" if (!-d "$PREF{'FILEBASE'}");
	    		$mailprog = "Mail Program [Sendmail]" if (!-e "$PREF{'MAILPGRM'}");

	    		&top_html("Problema !", 0);
                		print "<BR><CENTER><TABLE CELLSPACING=0 CELLPADDING=9 >\n" .
                        		"<TR><TD BGCOLOR='$PREF{'TBCOLOR'}'><FONT SIZE=-1>\n" .
                        		"<DT><I>Currently -</I></DT>\n" .
                        		"<DD>$datafile</DD>\n<DD>$filebase</DD>\n<DD>$mailprog</DD>\n" .
                        		"<DT><I>Can not be found.</I></DT><DD>Please update location(s) in <A HREF='cl-admin.cgi'>Administration</A>.</DD>\n" .
                        		"</FONT></TD>" .
                        		"</TR>";
                		print "</TABLE></CENTER>\n\n";
            		&bottom(1);
         	}
         }

#
# $--------------------------------------------------------------------------------------------
#
#  S  U  B  -  N  F  R  A  M  E
#
# $--------------------------------------------------------------------------------------------
#

 	# $ notifying frame - just a simple subroutine that prints out a table with
        # $ the first argument you pass it embedded in it, saves me a lot of time !

	sub nframe
         {
               	print "<BR><CENTER><TABLE CELLSPACING=0 CELLPADDING=9 >\n" .
                      " <TR>\n<TD ALIGN=CENTER BGCOLOR='$PREF{'TBCOLOR'}'><TT>\n" .
                      " $_[0]</TT></TD>\n </TR>\n";
               	print "</TABLE></CENTER>\n\n";
         }

#
# $--------------------------------------------------------------------------------------------
#
#  S  U  B  -  M  I  S  S  I  N  G
#
# $--------------------------------------------------------------------------------------------
#

 	# $ subroutine I call when a variable is missing, in the future, I might
        # $ include this in the parsing function above which would save xxx time and
        # $ also let people change my scripts more successfully ?

	sub missing
        {
               	&top_html("Missing Field");
               	&nframe("Missing Field [$_[0]]<BR> Return to the " .
                   "<a href='$ENV{'HTTP_REFERER'}'> F O R M</a> and try again.");
               	&bottom(1);
        }

#
# $--------------------------------------------------------------------------------------------
#
#  S  U  B  -  N  O  T  I  F   Y
#
# $--------------------------------------------------------------------------------------------
#

 	# $ there are 3 arguments passed to this function, 1=TITLE, 2=DISPLAY_TEXT, 3=ADDITIONAL
        # $ the title is self explanatory, the display text is just the text you would like to
        # $ display to the user and the additional is which additional text to add to the nframe

	sub notify
        {
               	my ($title, $info, $more, $extra) = (shift, shift, shift, undef);

               	$extra = qq!<BR>Return to the <a href="$ENV{'HTTP_REFERER'}"> F O R M</a> and try again.! if $more == 1;
               	$extra = qq!<BR>Return to my <A HREF="$PREF{'HOME'}">S  I  T  E</A> and surf on.! if $more == 2;

               	&top_html("$title");
               	&nframe("<TT>$info $extra</TT>");
               	&bottom(1);
        }

#
# $--------------------------------------------------------------------------------------------
#
#  S  U  B  -  B  O  T  T  O  M
#
# $--------------------------------------------------------------------------------------------
#

 	# $ hmmmmm ? what does this do I hear you all cry, well I just don't know, I wrote
        # $ it a long time ago and took me about an hour but I don't know what its for ?!?!
        # $ [please note I was being sarcastic, no more emails about what it does] ;)

	sub bottom
        {
               	print "</BODY>\n";
               	print "</HTML>\n";
               	exit 0 if $_[0];
        }

#
# $--------------------------------------------------------------------------------------------
#
#  S  U  B  -  P  R  E  F  E  R  E  N  C  E  S
#
# $--------------------------------------------------------------------------------------------
#

	sub preferences
	{
        	my ($no, $prefno);

        	open(PREF, $_[0]) || return "$_[0]: Preference file can not be found";
  		for ($no = 1; (<PREF>); $no++)
                {
                        if (/^#|^;/)
                        {
                                $PREF{'__COMMENTS__'} .= $_ if (!$prefno);
                        }
                        elsif (/^(\w+)\s*=\s?(.*)$/)
                        {
                                $PREF{$1} = $2;
                                $prefno++;
                        }
                        else
                        {
                                return "$_[0]:Line $no: incorrect preference structure.";
                        }
                }
                close(PREF);

                return ($_[1] == $prefno) ? 1 : "$_[0]: Incorrect number of preferences.";
	}

#
# $--------------------------------------------------------------------------------------------
#  ===========================================================================================
# $--------------------------------------------------------------------------------------------
#


#$--------------------------------------------------------------------------------------------
#
#  S  U  B  -  INSERT DATABASE VALUES
#
# $--------------------------------------------------------------------------------------------
#

	sub insert_db
	{
        # connect to MySQL database
		my %attr = (PrintError=>0,RaiseError=>1 );
		my $dbh = DBI->connect($PREF{'DB_CONNECT'}, $PREF{'DB_USER'}, $PREF{'DB_PASS'}, \%attr);
		# set the value of SQL query
		$insert_query = "insert into hs_mailselect (mailselect_name, mailselect_company, mailselect_phone, mailselect_email, mailselect_organization, mailselect_organization_size, mailselect_efile,mailselect_frompage) 
			values (?, ?, ?, ?, ?, ?, ?, ?) ";
		# prepare your statement for connecting to the database
		$statement = $dbh->prepare($insert_query);
		# execute your SQL statement
		$statement->execute($INPUT{'name'}, $INPUT{'company'}, $INPUT{'phone'}, $INPUT{'email'}, $INPUT{'desc'}, $INPUT{'size'}, $files[0], $ENV{'HTTP_REFERER'});	
		          
	}

#
# $--------------------------------------------------------------------------------------------
#  ===========================================================================================
# $--------------------------------------------------------------------------------------------
#
