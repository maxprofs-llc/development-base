#!/usr/local/bin/perl

use strict;

$| = 1;
#BEGIN{($_=$0)=~s![\\/][^\\/]+$!!;push@INC,$_}

use File::Basename        qw( dirname );
use File::Spec::Functions qw( rel2abs );

use lib dirname(rel2abs($0)),'.','/usr/local/www/vhosts/managed2/modules/pdf', '/usr/local/www/vhosts/managed2/modules';

use vars qw( $Debug $production $cook $config_file);

if (!do('common.inc')) {
   my $error = $@ ? $@
             : $! ? $!
             : 'did not return a true value';
   die("Unable to load common stuff: $error\n");
}

use CGI qw(-no_xhtml -debug);
use Time::localtime;
use Date::Calc qw(:all);

use HealthStatus::Config;
use HealthStatus;
use HealthStatus::User;
use HealthStatus::Constants;
use HealthStatus::Database;
use Data::Dumper;
use Spreadsheet::ParseExcel;
my $config = getConfig();
my $dbcfg = $config->{db};

print "Content-type: text/plain\n\n";

require $config->db_config_file;

my $db = HealthStatus::Database->new( $config );

my $excel = new Spreadsheet::ParseExcel;

my $book = $excel->parse('/usr/local/www/vhosts/managed2/base/data/efr_biometrics.xls') || die "cant open";
my $worksheet = $book->worksheet(0);

my ( $row_min, $row_max ) = $worksheet->row_range();
my ( $col_min, $col_max ) = $worksheet->col_range();


my $data = [];

open OUTFILE, '>myoutfile.txt';
for (my $row=$row_min+2;$row<=$row_max;$row++) #row_max
{
    my $urow ={};
    $urow->{'OrgName'} = $worksheet->get_cell($row, 0)->value();
    $urow->{'EmployeeCase'} = $worksheet->get_cell($row, 1)->value();
    $urow->{'Sex'} = $worksheet->get_cell($row, 2)->value();
    $urow->{'db_sortdate'} = $worksheet->get_cell($row, 3)->value();
    $urow->{'fasted'} = $worksheet->get_cell($row, 4)->value();
    $urow->{'height'} = $worksheet->get_cell($row, 5)->value();
    $urow->{'weight'} = $worksheet->get_cell($row, 7)->value();
    $urow->{'waist'} = $worksheet->get_cell($row, 8)->value();
    $urow->{'bp_sys'} = $worksheet->get_cell($row, 9)->value();
    $urow->{'bp_dias'} = $worksheet->get_cell($row, 10)->value();
    $urow->{'bodyfat'} = $worksheet->get_cell($row, 12)->value();
    $urow->{'cholesterol'} = $worksheet->get_cell($row, 14)->value();
    $urow->{'hdl'} = $worksheet->get_cell($row, 15)->value() if($worksheet->get_cell($row, 15));
    $urow->{'ldl'} = $worksheet->get_cell($row, 16)->value() if($worksheet->get_cell($row, 16));
    $urow->{'triglycerides'} = $worksheet->get_cell($row, 17)->value();
    $urow->{'glucose'} = $worksheet->get_cell($row, 19)->value();
    
    trim_ws_and_alphas(values %$urow);
    
    my %hash;
    
    print "Row: $row $urow->{'EmployeeCase'} \n";
    my $user = bless {}, 'HealthStatus::User';

    $user->db_number($urow->{'EmployeeCase'});
    $user->site($urow->{'OrgName'});
    $user->sex($urow->{'Sex'});
    $user->fasted($urow->{'fasted'});
    $user->waist($urow->{'waist'});
    $user->bp_sys($urow->{'bp_sys'});
    $user->bp_dias($urow->{'bp_dias'});
    $user->cholesterol($urow->{'cholesterol'});
    $user->triglycerides($urow->{'triglycerides'});
    $user->glucose($urow->{'glucose'});
    $user->hdl($urow->{'hdl'});
    $user->ldl($urow->{'ldl'});
    $user->client7($urow->{'EmployeeCase'});
    $user->client6('waiting');
    $user->client5($urow->{'db_sortdate'});
    $hash{weight}=$urow->{'weight'};
    $hash{height}=$urow->{'height'};
    $hash{bodyfat}=$urow->{'bodyfat'};
    $user->add(\%hash);
    
    my $status2 = $db->save_users_assessment($user,'BIO' );
    print $status2 ." - user weight:".$user->weight." spreadsheet: ".$urow->{'weight'}." - user height:".$user->height." spreadsheet: ".$urow->{'height'}." \n";

    #print Dumper($user) . "\n\n";

}
close OUTFILE;

sub trim_ws_and_alphas {
    for (@_)
    {
        s/^[\s\t\n]*//; s/[\s\t\n]*$//; s/\s+\w$//; s/<>//g;
    }
}

