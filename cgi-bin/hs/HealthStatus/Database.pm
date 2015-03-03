# $Id: Database.pm,v 1.3 2010/06/25 17:18:50 code4hs Exp $

package HealthStatus::Database;

use DBI;
use DBIx::Sequence;
use HealthStatus;
use HealthStatus::Constants;
use HealthStatus::Config;
use HealthStatus::User;
use HealthStatus::Authenticate;
use Carp;
use strict;
use Data::Dumper;
use base qw(HealthStatus);

require Exporter;

use vars qw( $VERSION @ISA   %setup_tables %field_info %Tables %Fields %ORACLE_CVRT %POSTGRES_CVRT @Encrypt);

( $VERSION ) = q$Revision: 1.3 $ =~ m/ (\d+ \. \d+) /gx;

@ISA          =  qw( Exporter );


=head1 NAME

HealthStatus::Database

=head1 SYNOPSIS

        HealthStatus::Database->new( $dsn );

=head1 DESCRIPTION

C<HealthStatus::Database> subclasses DBI, so all of the C<DBI> methods and techniques are available.  This subclass adds some queries special to HealthStatus.

=head1 METHODS

=over 4

=item HealthStatus::Database->connect( $dsn )

  $db  =  HealthStatus::Database->new( $DBI_driver, $database, $hostname, $port, $user, $password );

  $db  =  HealthStatus::Database->new( );

  $db->debug_on( \*DEBUG_OUTPUT_HANDLE );
  $db->debug_off( );

  @query_results = $db->get_users_assessments_taken( $user, $config, @assessments );
  $count = $db->count_users( $user, $config, @assessments, $stipulations );
  $db->get_users_assessment( $user, $config, $assessment, $record_number);
  $db->get_users_pt_data ($user, $config );
  $db->save_users_assessment( $user, $config, $assessment );


  @query_results  =  $db->select( \@desired_fields, \@desired_tables, $stipulations, $hash_or_not );
  @query_results  =  $db->select( \@desired_fields, $desired_table, $stipulations, $hash_or_not );
  [..etc..]

  @query_results  =  $db->select_all( \@desired_tables, $stipulations, $hash_or_not );

  $db->select_incrementally( \@desired_fields, \@desired_tables, $stipulations );
  $db->select_all_incrementally( \@desired_tables, $stipulations );

  $next_row_ref  =  $db->get_next_row( $hash_or_not );

  $number_of_rows  =  $db->count( $desired_table, $stipulations );

  $a_single_value  =  $db->select_one_value( $desired_field, $desired_table, $stipulations );

  @scalar_query_results  =  $db->select_one_column( $desired_field, \@desired_tables, $stipulations );

  $single_row_ref  =  $db->select_one_row( \@desired_fields, \@desired_tables, $stipulations, $hash_or_not );

  $db->delete( $desired_table, $stipulations );
  $db->delete_all( $desired_table );

  $db->insert( $desired_table, \%new_data );
  $insert_id  =  $db->insert( $desired_table, \%new_data );  # MySQL only!!
  $db->update( $desired_table, \%new_data, $stipulations );

  $db->use_db( "another_database" );

  $db->execute_sql( $some_raw_sql );

  #  Oracle users may find this one handy..
  $db->force_lowercase_fields( );

  #  this is just a wrapper around the corresponding DBI function
  $db->func( @func_arguments, $func_name );

  $db->disconnect( );

  $db->finish( );


This C<connect> function overrides C<DBI>'s connect function and reblesses the C<DBI> object into C<HealthStatus::Database>.

=cut

sub new { 
        # To check whether maintenance file exist
        my $utility_dir = '/usr/local/www/vhosts/';
		opendir(DH, "$utility_dir") || die "Can't opedir $utility_dir: $!\n";
		my @list = readdir(DH);
		
		closedir(DH);
		my $form = '/usr/local/www/vhosts/error.html';
		foreach my $file(@list){		
			my %hash;
			if ($file eq '.' || $file eq '..') {
	           next;
		    }elsif ($file eq 'error.html' ) { 				  
				  HealthStatus::fill_and_send( $form, \%hash);
				  exit;
			}
		}
		# check ends here
        my $class  =  shift;
        my ( $self );

        $self   =  { };

        if ( @_ ) {
                my ( $config ) = @_;

                return unless ref $config eq 'HealthStatus::Config';

                $self->{'data_source'}  =  $config->db_connect;
                $self->{'user'}         =  $config->db_user;
                $self->{'password'}     =  $config->db_pass;
                $self->{'driver'}       =  $config->db_driver;
                $self->{'database'}     =  $config->db_database;
                $self->{'hostname'}     =  $config->db_hostname;
                $self->{'port'}         =  $config->db_port;
                $self->{'force_lowercase'}  =  0;
                $self->{'config'}	=  $config;
                $self->{'debug_handle'}  =  \*STDERR;
                $self->{'os'} = $^O;

		require $config->db_config_file;

                return if lc($config->db_driver) eq 'debug';

		$ENV{ORACLE_HOME} = $config->db_oracle_home if ( lc($config->db_driver) eq 'oracle' );

                $self->{'db'}  =  DBI->connect( $self->{'data_source'},
                                                $self->{'user'}, $self->{'password'} );
                if ( ! $self->{'db'} ) {
			#die "Could not open database $self->{'data_source'}, $self->{'user'}!\n\n";
			error("Could not open database: $self->{'data_source'}!", '',
                        __LINE__, __FILE__, 
			$self->{config}->{config_data}->{conf_install_site},
			$self->{config}->{config_data}->{error_system},
               		$self->{config}->{config_data}->{email_from},
                	$self->{config}->{config_data}->{error_subject},
                	$self->{config}->{config_data}->{email_smtp} ); 
				
                }
	        $self->{'sequence'} = new DBIx::Sequence({ dbh => $self->{'db'} });

        }

        bless( $self, $class );
}


sub new_extra {
	my $class  =  shift;
	my ( $self );

	$self   =  { };

	if ( @_ ) {
		my ( $connect, $user, $password, $driver, $config ) = @_;

		$self->{'db'}  =  DBI->connect( $connect, $user, $password );

		if ( ! $self->{'db'} ) {
			#die "Could not open extra database $connect!\n\n";
			error("Could not open extra database $connect!", '',
                        __LINE__, __FILE__, 
			$self->{config}->{config_data}->{conf_install_site},
			$self->{config}->{config_data}->{error_system},
               		$self->{config}->{config_data}->{email_from},
                	$self->{config}->{config_data}->{error_subject},
                	$self->{config}->{config_data}->{email_smtp} ); 
		}
		$self->{'driver'}    =  $driver;
		$self->{'user'}      =  $user;
		$self->{'password'}  =  $password;
		$self->{'force_lowercase'}  =  0;
                $self->{'config'}    =  $config;
	}

	bless( $self, $class );
}

sub debug_on {        #   call it like this, e.g.:  $db->debug_on( \*STDERR );
        my $self          =  shift;
        my $debug_handle  =  shift;

        #   we check to see if it's valid before agreeing to use it
        if ( (ref($debug_handle) eq 'Fh')  ||  (ref($debug_handle) eq 'GLOB') ) {
                $self->{'debug'}         =  1;
                $self->{'debug_handle'}  =  $debug_handle;
        }
        else { print { $self->{'debug_handle'} }  "Database debug_on - bad file handle - passed in: $debug_handle\n"; }
}


sub debug_off {
        my $self  =  shift;

        $self->{'debug'}  =  0;
        undef( $self->{'debug_handle'} );
}

sub debug{return $_[0]->{debug};}

sub get_table_names
	{
        my $self = shift;
        my $assessments = shift;

        my %table_names;

        foreach (@$assessments){
        	$table_names{$_} = $Tables{$_};
        	}
        return (\%table_names);

	}
	
sub get_db_tables
	{   
        my $self = shift;
        my $config  = shift;            	
        
        my $dbh  =  DBI->connect($config->db_connect, $config->db_user, $config->db_pass );
        my %group_table;
        my @table = $dbh->tables();
    
       foreach (@table){ 
	   if ( lc($config->db_driver) eq 'oracle' ){
			my $usr = uc($config->db_user);
			s("$usr".")();
			s("SYS".")();
			s(")();
			}
	   if ( lc($config->db_driver) eq 'mssql' ){
			my $dbname = $config->db_database;
			my $usr = lc($config->db_user);
			s("$dbname"."$usr".")();
			s("$dbname"."dbo".")();
			s(")();
		  }
	   if ( lc($config->db_driver) eq 'postgres' ){
	        next if(/pg_catalog/);
	        next if(/information_/);
			s(public.)();
			s(")();
		 }
        if(lc($config->db_driver) eq 'mysql'){
              my $dbname = $config->db_database;
              s(`$dbname`.`)();
              s(`)();
         }      
	      $group_table{lc($_)} = 1; 
	 }
	         
        return (\%group_table);

}	
	
sub init_seq {
        my $self  =  shift;
        require $self->{'config'}->db_config_file;
        my @assessments_allowed = split /\s+/, $self->{'config'}->ggr_adv_tables;
	   foreach (@assessments_allowed){
        	$self->{'sequence'}->Bootstrap($Tables{$_},$Tables{$_},'xnum');
        	}
        $self->{'sequence'}->Bootstrap($Tables{REG},$Tables{REG},'unum');
}

sub finish {
        my $self  =  shift;

        return if lc($self->{'config'}->db_driver) eq 'debug';
        $self->{'statement'}->finish();
}


sub disconnect {
        my $self  =  shift;

        return if lc($self->{'config'}->db_driver) eq 'debug';
        $self->{'db'}->disconnect();
}

sub quote {
	my ($self, $str) = @_;
	return $$self{db}->quote($str);
}

sub force_lowercase_fields {
	my $self  =  shift;

	$self->{'force_lowercase'}  =  1;
}

sub normalcase_fields {
	my $self  =  shift;

	$self->{'force_lowercase'}  =  0;
}

sub select {
    my $self          =  shift;
    my $fields        =  shift;
    my $tables        =  shift;
    my $stipulations  =  shift;
    my $wants_a_hash  =  shift;
    my $limit 	      =  shift;
        my ( @fields, @tables );

        $self->__add_to_array( $fields, \@fields );
        $self->__add_to_array( $tables, \@tables );

    if ( ! defined($self->{'db'}) ) {
	    #die "There is not a valid DB handle from which to select data.\n";
		error("There is not a valid DB handle from which to select data.\n", '',
		__LINE__, __FILE__, 
		$self->{config}->{config_data}->{conf_install_site},
		$self->{config}->{config_data}->{error_system},
                $self->{config}->{config_data}->{email_from},
                $self->{config}->{config_data}->{error_subject},
                $self->{config}->{config_data}->{email_smtp} ) ;
    }

    local $"  =  ", ";
    $self->{'sql'}   =  "SELECT @fields FROM @tables ";
    $self->{'sql'}  .=  $stipulations  if  $stipulations;

    print { $self->{'debug_handle'} } "Database:select - $self->{'sql'}\n"  if  $self->{'debug'};

    $self->__sql_execute( $wants_a_hash, $limit );
}

sub select_one_value {
    my $self          =  shift;
        my $field         =  shift;
    my $tables        =  shift;
    my $stipulations  =  shift;
        my ( @tables );

        $self->__add_to_array( $tables, \@tables );

    local $"  =  ', ';
    $self->{'sql'}   =  "SELECT $field FROM @tables ";
    $self->{'sql'}  .=  $stipulations  if  $stipulations;

    print { $self->{'debug_handle'} } "Database:select_one_value - $self->{'sql'}\n"  if  $self->{'debug'};

    my @query_results  =  $self->__sql_execute();
    return $query_results[0]->[0];
}


sub select_one_row {
    my $self          =  shift;
    my $fields        =  shift;
    my $tables        =  shift;
    my $stipulations  =  shift;
    my $wants_a_hash  =  shift;
        my ( @fields, @tables );

        $self->__add_to_array( $fields, \@fields );
        $self->__add_to_array( $tables, \@tables );

    local $"  =  ", ";
    $self->{'sql'}   =  "SELECT @fields FROM @tables ";
    $self->{'sql'}  .=  $stipulations  if  $stipulations;
   
    print { $self->{'debug_handle'} } "Database:select_one_row - $self->{'sql'}\n"  if  $self->{'debug'};

    my @query_results  =  $self->__sql_execute( $wants_a_hash );
	
    return $query_results[0];
	
}

sub select_one_column {
    my $self          =  shift;
        my $field         =  shift;
        my $tables        =  shift;
        my $stipulations  =  shift;
        my ( @tables );

        $self->__add_to_array( $tables, \@tables );

    local $"  =  ", ";
    $self->{'sql'}   =  "SELECT $field FROM @tables ";
    $self->{'sql'}  .=  $stipulations  if  $stipulations;

    print { $self->{'debug_handle'} } "Database:select_one_column - $self->{'sql'}\n"  if  $self->{'debug'};

    my @query_results  =  $self->__sql_execute( 1 );   #  TODO:  find out why this didn't work with arrayrefs!!
        my ( $result_data, @array_of_scalars );
        $field  =~  s/^\s*distinct\s+(\S+)/$1/i;
        $field  =~  s/.*\.(.*)/$1/;
        foreach $result_data ( @query_results ) {
                push( @array_of_scalars, $result_data->{$field} );
        }
    return @array_of_scalars;
}

sub select_one_column_distinct {
    my $self          =  shift;
        my $field         =  shift;
        my $tables        =  shift;
        my $stipulations  =  shift;
        my ( @tables );

        $self->__add_to_array( $tables, \@tables );

    local $"  =  ", ";
    $self->{'sql'}   =  "SELECT DISTINCT $field FROM @tables ";
    $self->{'sql'}  .=  $stipulations  if  $stipulations;

    print { $self->{'debug_handle'} } "Database:select_one_column_distinct - $self->{'sql'}\n"  if  $self->{'debug'};

    my @query_results  =  $self->__sql_execute( 1 );   #  TODO:  find out why this didn't work with arrayrefs!!
        my ( $result_data, @array_of_scalars );
        $field  =~  s/^\s*distinct\s+(\S+)/$1/i;
        $field  =~  s/.*\.(.*)/$1/;
        foreach $result_data ( @query_results ) {
                push( @array_of_scalars, $result_data->{$field} );
        }
    return @array_of_scalars;
}


sub select_all {
    my $self          =  shift;
    my $tables        =  shift;
    my $stipulations  =  shift;
    my $wants_a_hash  =  shift;
        my ( @tables );

        $self->__add_to_array( $tables, \@tables );

    $self->select( [ "*" ], \@tables, $stipulations, $wants_a_hash ); }

sub select_incrementally {
        my $self          =  shift;
        my $fields        =  shift;
        my $tables        =  shift;
        my $stipulations  =  shift;
        my ( @fields, @tables );

        $self->__add_to_array( $fields, \@fields );
        $self->__add_to_array( $tables, \@tables );

    if ( ! defined($self->{'db'}) ) {
	    #die "There is not a valid DB handle from which to select data.\n";
		error("There is not a valid DB handle from which to select data.\n", '',
		__LINE__, __FILE__, 
		$self->{config}->{config_data}->{conf_install_site},
		$self->{config}->{config_data}->{error_system},
                $self->{config}->{config_data}->{email_from},
                $self->{config}->{config_data}->{error_subject},
                $self->{config}->{config_data}->{email_smtp} ) ;
    }

    local $"  =  ", ";
    $self->{'sql'}   =  "SELECT @fields FROM @tables ";
    $self->{'sql'}  .=  $stipulations  if  $stipulations;

    print { $self->{'debug_handle'} } "Database:select_incrementally - $self->{'sql'}\n"  if  $self->{'debug'};

    $self->{'statement'}  =  $self->{'db'}->prepare( $self->{'sql'} );
    if  ( ! defined $self->{'statement'} ) {
	    #die "Cannot prepare statement (error ".$self->{'db'}->err."): ".$self->{'db'}->errstr."\n";
		error("Cannot prepare statement: $self->{'db'}->{errstr} $self->{'sql'}", $self->{'db'}->err,
		__LINE__, __FILE__, 
		$self->{config}->{config_data}->{conf_install_site},
		$self->{config}->{config_data}->{error_system},
                $self->{config}->{config_data}->{email_from},
                $self->{config}->{config_data}->{error_subject},
                $self->{config}->{config_data}->{email_smtp} ) ;
    }
    $self->{'statement'}->execute();
    #   we now leave the $self->{'statement'} object "hanging open" for use by &get_next_row()
}

sub select_all_incrementally {
        my $self          =  shift;
        my $tables        =  shift;
        my $stipulations  =  shift;
        my ( @tables );

        $self->__add_to_array( $tables, \@tables );

    $self->select_incrementally( [ "*" ], \@tables, $stipulations ); }

sub get_next_row {
    my $self          =  shift;
    my $wants_a_hash  =  shift;

    if ( ! defined($self->{'db'}) ) {
	    #die "There is not a valid DB handle from which to select another row of results.\n";
		error("There is not a valid DB handle from which to select another row of results.", '',
		__LINE__, __FILE__, 
		$self->{config}->{config_data}->{conf_install_site},
		$self->{config}->{config_data}->{error_system},
                $self->{config}->{config_data}->{email_from},
                $self->{config}->{config_data}->{error_subject},
                $self->{config}->{config_data}->{email_smtp} ) ;
        }

    if ( $wants_a_hash ) {
                return $self->{'statement'}->fetchrow_hashref();
    }
        else {
                return $self->{'statement'}->fetchrow_arrayref();
    }   #   i personally have no use for fetchrow[_array]... ( does anybody? )
}


sub rows {
        my $self  =  shift;

        if ( $self->{'statement'} ) {
                return $self->{'statement'}->rows();
        }
        else {
                return 0;
        }
}


sub count {
    my $self          =  shift;
    my $tables        =  shift;
    my $stipulations  =  shift;
        my ( @tables );

        $self->__add_to_array( $tables, \@tables );

    if ( ! defined($self->{'db'}) ) {
	    #die "There is not a valid DB handle from which to select a count.\n";
		error("There is not a valid DB handle from which to select a count data.\n", '',
		__LINE__, __FILE__, 
		$self->{config}->{config_data}->{conf_install_site},
		$self->{config}->{config_data}->{error_system},
                $self->{config}->{config_data}->{email_from},
                $self->{config}->{config_data}->{error_subject},
                $self->{config}->{config_data}->{email_smtp} ) ;
        }

    local $"  =  ", ";
    $self->{'sql'}  =  "SELECT COUNT(*) FROM @tables $stipulations";

    print { $self->{'debug_handle'} } "Database: count - $self->{'sql'}\n"  if  $self->{'debug'};

    my @query_results  =  $self->__sql_execute();
    return $query_results[0]->[0];
}


sub insert {
    my $self            =  shift;
    my $table           =  shift;                #   send only one table
    my %new_data        =  %{ shift @_ };
    my @fields          =  keys( %new_data );       #   these are promised to be in the same order,
    my @values          =  values( %new_data );     #   according to the docs
    my @question_marks  =  ( "?" ) x @values;

    if ( ! defined($self->{'db'}) ) {
	    #die "There is not a valid DB handle into which to insert data.\n\n";
		error("There is not a valid DB handle into which to insert data.\n", '',
		__LINE__, __FILE__, 
		$self->{config}->{config_data}->{conf_install_site},
		$self->{config}->{config_data}->{error_system},
                $self->{config}->{config_data}->{email_from},
                $self->{config}->{config_data}->{error_subject},
                $self->{config}->{config_data}->{email_smtp} ) ;
    }

    local $"  =  ", ";
    $self->{'sql'} = "INSERT INTO $table ( @fields ) VALUES ( @question_marks )";

    print { $self->{'debug_handle'} } "Database:insert - sql: $self->{'sql'}\nvalues: @values\n"  if  $self->{'debug'};
	print STDERR $self->{'sql'};
    $self->__sql_execute( \@values );
        return $self->{'statement'}->{'mysql_insertid'}  if  ( $self->{'driver'} eq 'mysql' ); }


sub update {
    my $self            =  shift;
    my $table           =  shift;                #   send only one table
    my %new_data        =  %{ shift @_ };
    my $stipulations    =  shift;
    my @fields          =  keys( %new_data );       #   these are promised to be in the same order,
    my @values          =  values( %new_data );     #   according to the docs

    if ( ! defined($self->{'db'}) ) {
	    #die "There is not a valid DB handle to update.\n";
		error("There is not a valid DB handle to update.\n", '',
		__LINE__, __FILE__, 
		$self->{config}->{config_data}->{conf_install_site},
		$self->{config}->{config_data}->{error_system},
                $self->{config}->{config_data}->{email_from},
                $self->{config}->{config_data}->{error_subject},
                $self->{config}->{config_data}->{email_smtp} ) ;
    }

    $self->{'sql'} = "UPDATE $table SET ";
    foreach ( @fields ) {
                $self->{'sql'}  .=  "$_ = ?, ";
    }
    $self->{'sql'}   =~  s/\,\s$/ /;                           #   chop off the last comma
    $self->{'sql'}  .=   $stipulations  if  $stipulations;

    print { $self->{'debug_handle'} } "Database:update - sql: $self->{'sql'}\nvalues: @values\n"  if  $self->{'debug'};

    $self->__sql_execute( \@values );
}

sub delete {
    my $self          =  shift;
    my $table         =  shift;
    my $stipulations  =  shift;

    if ( ! defined($self->{'db'}) ) {
	    #die "There is not a valid DB handle from which to delete data.\n";
		error("There is not a valid DB handle from which to delete data.\n", '',
		__LINE__, __FILE__, 
		$self->{config}->{config_data}->{conf_install_site},
		$self->{config}->{config_data}->{error_system},
                $self->{config}->{config_data}->{email_from},
                $self->{config}->{config_data}->{error_subject},
                $self->{config}->{config_data}->{email_smtp} ) ;	        
        }

    $self->{'sql'}  =  "DELETE FROM $table $stipulations";

    print { $self->{'debug_handle'} } "Database:delete - $self->{'sql'}\n"  if  $self->{'debug'};

    $self->__sql_execute();
}


sub delete_all {
    my $self   =  shift;
    my $table  =  shift;

    if ( ! defined($self->{'db'}) ) {
	    #die "There is not a valid DB handle from which to delete data.\n";
		error("There is not a valid DB handle from which to delete data.\n", '',
		__LINE__, __FILE__, 
		$self->{config}->{config_data}->{conf_install_site},
		$self->{config}->{config_data}->{error_system},
                $self->{config}->{config_data}->{email_from},
                $self->{config}->{config_data}->{error_subject},
                $self->{config}->{config_data}->{email_smtp} ) ;
			
    }

    $self->{'sql'}  =  "DELETE FROM $table";
    print { $self->{'debug_handle'} } "Database:delete_all - $self->{'sql'}\n"  if  $self->{'debug'};

    $self->__sql_execute();
}


sub execute_sql {
        my $self          =  shift;
        $self->{'sql'}    =  shift;
		my $wants_a_hash  =  shift;

    my @caller = caller(1) if $self->{'debug'};
    print { $self->{'debug_handle'} } "Database:execute_sql - $self->{'sql'} called from $caller[0]::$caller[3] l.$caller[2]\n"  if  $self->{'debug'};

    $self->__sql_execute( $wants_a_hash );
        return $self->{'statement'}->{'mysql_insertid'}  if  ( $self->{'driver'} eq 'mysql' ); }

sub execute_sql_return {
        my $self          =  shift;
        $self->{'sql'}    =  shift;
    	my $wants_a_hash  =  shift;
        my $limit	  =  shift;
    	my @results;

    my @caller = caller(1) if $self->{'debug'};
    print { $self->{'debug_handle'} } "Database:execute_sql_return - $self->{'sql'} called from $caller[0]::$caller[3] l.$caller[2]\n"  if  $self->{'debug'};

    @results = $self->__sql_execute( $wants_a_hash, $limit );
	
    return @results;

    }

sub __sql_execute {
    my $self  =  shift;
        my ( @values, $wants_a_hash, $limit );

        if ( @_ > 2 ) {
                @values        =  @{ shift @_ };   #   the @values fill in the ?s
                $wants_a_hash  =  shift @_;
                $limit = shift @_;
        }
        else {
                if ( ref($_[0]) eq 'ARRAY' ) {
                        @values        =  @{ shift @_ };
                }
                else {
	                $wants_a_hash  =  shift @_;
  	              $limit = shift @_;
                }
        }

    print { $self->{'debug_handle'} } "Database:SQL Execute - $self->{'sql'}\n"  if  $self->{'debug'};

    $self->{'statement'}  =  $self->{'db'}->prepare( $self->{'sql'} );

    if ( ! defined $self->{'statement'}  ||  $DBI::err ) {
                #warn "Cannot prepare statement (error ".$self->{'db'}->err."): ".$self->{'db'}->errstr. " " . $self->{'sql'} . "\n";
                error("Cannot prepare statement: $self->{'db'}->{errstr} $self->{'sql'}", $self->{'db'}->err, 
                __LINE__, __FILE__, 
		$self->{config}->{config_data}->{conf_install_site},
		$self->{config}->{config_data}->{error_system},
                $self->{config}->{config_data}->{email_from},
                $self->{config}->{config_data}->{error_subject},
                $self->{config}->{config_data}->{email_smtp} )
    }

        $self->{'statement'}->execute( @values );   #   ignores @values if undefined  ( right? )

        if ( $DBI::err ) {
		#die "Cannot execute statement (error ".$self->{'db'}->err."): ".$self->{'db'}->errstr. " " . $self->{'sql'} . "\n";
	        error("Cannot execute statement: $self->{'db'}->{errstr} $self->{'sql'}", $self->{'db'}->err, 
                __LINE__, __FILE__, 
		$self->{config}->{config_data}->{conf_install_site},
		$self->{config}->{config_data}->{error_system},
                $self->{config}->{config_data}->{email_from},
                $self->{config}->{config_data}->{error_subject},
                $self->{config}->{config_data}->{email_smtp} ) 	
        }

    my @results;

    my $count = $limit;

    #   the following if() strikes me as really stupid, as i must avoid the block
    #   so that the fetchrow calls do not error for non-SELECT statements...
    #   best to me would be for fetchrow to quietly do nothing if there are
    #   no rows... but hey.

    if ( $self->{'statement'}->{'NUM_OF_FIELDS'}) {
                if ( $wants_a_hash ) {
                        my $hash_ref;
                        while ( (!defined($limit) || $count--) && ($hash_ref  =  $self->{'statement'}->fetchrow_hashref()) ) {
                                if ( $self->{'force_lowercase'} ) {
                                        my %lc_hash;
                                        @lc_hash{ map { lc($_) } keys(%{$hash_ref}) }  =  values(%{$hash_ref});
                                        $hash_ref  =  \%lc_hash;
                                }
                                push @results, $hash_ref;
                        }
                } else {
                	my $array_ref;
                        while ( (!defined($limit) || $count--) && ($array_ref  =  $self->{'statement'}->fetchrow_arrayref()) ) {
                        	# Push a *copy* of the array onto results, since the arrays returned
                        	# by the statement handle all occupy the same space in memory (each
                        	# array is overwritten when the next one is retrieved)
                                push @results, [@$array_ref];
                        }
                }
    }
    return @results;
}

sub __add_to_array {
        my $self          =  shift;
        my $array_or_not  =  shift;
        my $target_array  =  shift;

        if ( ref($array_or_not) eq 'ARRAY' ) {
                push( @{$target_array}, @{$array_or_not} );
        }
        else {
                push( @{$target_array}, $array_or_not );
        }
}


sub getDbh
{
	my $self = shift;
#	return HealthStatus::Database::getDbh();
	return $self->{'db'};
}

sub email_sent
        {
        my $self = shift;
        my $user = shift;

        return if lc($self->{'config'}->db_driver) eq 'debug';

        $user->encrypt_in_place( $self->{'config'} );

        $self->{'db_id'} = $self->{'config'}->db_id;
        $self->{'user_db_id'} = $user->db_id;

        my $stipulations = "WHERE $self->{'db_id'} = ";
        $stipulations .= $self->{'db'}->quote( $self->{'user_db_id'} );

	print { $self->{'debug_handle'} } "Database:email_sent EM - $Tables{EM}, $stipulations\n"  if  $self->{'debug'};
       	if($Tables{EM})	{
			my @query_results  =  $self->select_all( $Tables{EM}, $stipulations, 1 );
			print { $self->{'debug_handle'} } "Database:email_sent - scalar(@query_results) \n"  if  $self->{'debug'};
        		$user->decrypt_in_place( $self->{'config'} );
			return scalar(@query_results);
			}
       	else		{
        		$user->decrypt_in_place( $self->{'config'} );
       			return FALSE;
       			}

        }

sub user_login
	{
	   my $self = shift;
        my $user = shift;
        my $time = shift;

        if(!$user->db_number && !$user->db_id){
			print { $self->{'debug_handle'} } "Database - user_login - no db_number set and no db_id set returning.\n"  if  $self->{'debug'};
        		return( FALSE , 0, 0); }

        $user->encrypt_in_place( $self->{'config'} );
        my ($lookup, $lookup_val);

	if($user->db_number){
		$lookup = 'unum';
		$lookup_val = $user->db_number;
		print { $self->{'debug_handle'} } "Database - user_login - db_number set.\n"  if  $self->{'debug'};
		}
	else 	{
		$lookup = $self->{'config'}->db_id;
		$lookup_val = $self->{'db'}->quote( $user->db_id );
		print { $self->{'debug_handle'} } "Database - user_login - no db_number set using db_id.\n"  if  $self->{'debug'};
		}

	my $stipulations = "WHERE $lookup = $lookup_val";

	print { $self->{'debug_handle'} } "Database - user_login - PASS - $Tables{PASS}, $stipulations\n"  if  $self->{'debug'};
	if ($self->count ( $Tables{PASS}, $stipulations ))
		{
		my @fields = ( 'loginstatus', 'logintime'  );
		my $id = $self->{'config'}->db_id;
		if  (lc($self->{'config'}->db_driver) eq 'oracle'){
			foreach my $tmp ( @fields ){ $tmp = uc($tmp) }
			$id = uc($id);
			}
		if  (lc($self->{'config'}->db_driver) eq 'postgres'){
			foreach my $tmp ( @fields ){ $tmp = lc($tmp) }
			$id = lc($id);
			}

		my @query_results  =  $self->select_all ($Tables{PASS}, $stipulations, 1);

		print { $self->{'debug_handle'} } "Database - user_login - PASS - $Tables{PASS}, status = $query_results[0]{$fields[0]}, time = $query_results[0]{$fields[1]}\n"  if  $self->{'debug'};
		my $logtime = $query_results[0]{$fields[1]};
		my $logstatus = $query_results[0]{$fields[0]};
		$user->db_id ( $query_results[0]{$id} );

		my %new_time;

		$new_time{logintime} = $time;

		$self->update($Tables{PASS}, \%new_time, $stipulations);

		print { $self->{'debug_handle'} } "Database - user_login - PASS - $Tables{PASS}, status = $query_results[0]{$fields[0]} - $logstatus, time = $query_results[0]{$fields[1]} - $logtime\n"  if  $self->{'debug'};
        	$user->decrypt_in_place( $self->{'config'} );
		return (TRUE, $logstatus, $logtime);
		}
	else	{
        	$user->decrypt_in_place( $self->{'config'} );
		return( FALSE , 0, 0);
		}
	}

sub lookup_user
	{
	my $self = shift;
        my $user = shift;
        my $config = shift;
        my $field = shift;

	my ($stipulations, $lookup, $lookup_val, $boolean);
	my (%multiples);

        $user->encrypt_in_place( $self->{'config'} );

# if no field specified  then db_id_number is assumed
# user, email are valid options

	if( lc($field) eq 'email'){
		$lookup = 'email';
		$lookup_val = $self->{'db'}->quote( $user->db_email );
		}
	elsif( lc($field) eq 'user'){
		$lookup = $self->{'config'}->db_id;
		$lookup_val = $self->{'db'}->quote( $user->db_id );
		}
        else	{
		$lookup = 'unum';
		$lookup_val = $self->{'db'}->quote( $user->db_number );;
		}

        $lookup = uc($lookup) if ( lc($self->{'config'}->db_driver) eq 'oracle' );
        $lookup = lc($lookup) if ( lc($self->{'config'}->db_driver) eq 'postgres' );
	$stipulations = "WHERE $lookup = $lookup_val";

	return ($self->_lookup_user( $user, $config, $stipulations));
	}

sub lookup_user_by_id_ts
	{
	my $self = shift;
        my $user = shift;
        my $config = shift;
        my $ts = shift;

	my ($stipulations, $lookup, $lookup_val);
	my (%multiples);

        $user->encrypt_in_place( $self->{'config'} );

	$lookup = $self->{'config'}->db_id;
	$lookup_val = $self->{'db'}->quote( $user->db_id );

	$stipulations = "WHERE $lookup = $lookup_val AND ts = $ts";

	return ($self->_lookup_user( $user, $config, $stipulations));
	}

sub _lookup_user
	{
	my $self = shift;
        my $user = shift;
        my $config = shift;
        my $stipulations = shift;

	my ($lookup, $lookup_val, $boolean);
	my (%multiples);

	print { $self->{'debug_handle'} } "Database:lookup_user - REG - $Tables{REG}, $stipulations\n"  if  $self->{'debug'};

	my $rec_count = $self->count ( $Tables{REG}, $stipulations );
	print { $self->{'debug_handle'} } "Database:lookup_user - records found = $rec_count\n"  if  $self->{'debug'};

	if ($rec_count > 0)
		{
		my @query_results  =  $self->select_all ( $Tables{REG}, $stipulations, 1);
		print { $self->{'debug_handle'} } "Database:lookup_user - lookup - records found = $rec_count - scalar(@query_results) \n"  if  $self->{'debug'};

		my $pass_key = $self->{'config'}->db_auth;
		my $db_id = $self->{'config'}->db_id;

		# if we only find one record, load the user object and return
		if($rec_count == 1)
			{
			my @field_kys = keys %{$query_results[0]};
			foreach my $field ( @field_kys )
				{
				my $obj_name = $field;
				$obj_name = $ORACLE_CVRT{uc($field)} if  lc($self->{'config'}->db_driver) eq 'oracle' ;
				$obj_name = $POSTGRES_CVRT{lc($field)} if  lc($self->{'config'}->db_driver) eq 'postgres' ;

				print { $self->{'debug_handle'} } "Database - Lookup user - $query_results[0]{$field}, $field, $obj_name\n"  if  $self->{'debug'};

				my $user_obj = $Fields{REG}{$obj_name};
				$user_obj = $obj_name if(!$user_obj);
				$user_obj = $Fields{REG}{$field} if !($user_obj);

				if( lc($user_obj) ne 'null' )    { $user->$user_obj ( $query_results[0]{$field} ) }

				}

			$lookup = 'unum';
			$lookup_val = $user->db_number;

			$stipulations = "WHERE $lookup = $lookup_val";
			
			print { $self->{'debug_handle'} } "Database:lookup_user - REG - $Tables{PASS}, $stipulations\n"  if  $self->{'debug'};

			if ($lookup_val  && $self->{'config'}->authenticate_method eq 'hs')
				{
				@query_results  =  $self->select_all ( $Tables{PASS}, $stipulations, 1);

				print { $self->{'debug_handle'} } "Database:lookup_user - scalar(@query_results) \n"  if  $self->{'debug'};

				@field_kys = keys %{$query_results[0]};

				foreach my $field ( @field_kys )
					{
					my $obj_name = $field;
					$obj_name = $ORACLE_CVRT{uc($field)} if  lc($self->{'config'}->db_driver) eq 'oracle' ;
					$obj_name = $POSTGRES_CVRT{lc($field)} if  lc($self->{'config'}->db_driver) eq 'postgres' ;

					my $user_obj = $Fields{PASS}{$obj_name};
					$user_obj = $obj_name if(!$user_obj);
					$user_obj = $Fields{PASS}{$field} if !($user_obj);

					print { $self->{'debug_handle'} } "Database:lookup_user - - Lookup pass - $query_results[0]{$field}, $field, $obj_name, $user_obj\n"  if  $self->{'debug'};

					if( lc($user_obj) ne 'null' )    { $user->$user_obj ( $query_results[0]{$field} ) }
					}
				$multiples{$query_results[0]{'unum'}}{db_id}=$query_results[0]{$db_id};
				$multiples{$query_results[0]{'unum'}}{auth_password}=$query_results[0]{$pass_key};
				}
			}
		else	{
			foreach my $customer ( @query_results )
				{
				$lookup = 'unum';
				$lookup_val = $self->{'db'}->quote( $customer->{'unum'} );
				if ($lookup_val  && $self->{'config'}->authenticate_method eq 'hs')
					{
					$stipulations = "WHERE $lookup = $lookup_val";
					print { $self->{'debug_handle'} } "Database:lookup_user - REG - $Tables{PASS}, $stipulations\n"  if  $self->{'debug'};

					my @query_pass  =  $self->select_all ( $Tables{PASS}, $stipulations, 1);

					foreach my $cust_rec ( @query_pass ) {
						$multiples{$lookup_val}{db_id}= $cust_rec->{$db_id};
						$multiples{$lookup_val}{auth_password}=$cust_rec->{$pass_key};
						print { $self->{'debug_handle'} } "Database:lookup_user - Multiple registrations - $lookup_val -  $cust_rec->{$db_id} - $cust_rec->{$pass_key}\n"  if  $self->{'debug'};
						}
					}
				}
			}
		$boolean = TRUE;
		}
	else	{
		$boolean = FALSE;
		return ($boolean);
		exit;
		}

        $user->decrypt_in_place( $self->{'config'} );
	return ($boolean, \%multiples);

	}

sub add_user
	{
        my $self = shift;
        my $user = shift;

        return unless ref $user eq 'HealthStatus::User';

        return if lc($self->{'config'}->db_driver) eq 'debug';

        $user->encrypt_in_place( $self->{'config'} );

        $self->{'db_id'} = $self->{'config'}->db_id;
        $self->{'user_db_id'} = $user->db_id;

        my $stipulations = "WHERE $self->{'db_id'} = ";
        $stipulations .= $self->{'db'}->quote( $self->{'user_db_id'} );

	print { $self->{'debug_handle'} } "Database:add_user -REG - $Tables{REG}, $stipulations\n"  if  $self->{'debug'};
        my @query_results  =  $self->select_one_column ( $self->{'db_id'}, $Tables{REG}, $stipulations );
        print { $self->{'debug_handle'} } "scalar(@query_results) \n"  if  $self->{'debug'};

	if (scalar(@query_results)) 	{
        	$user->decrypt_in_place( $self->{'config'} );
	        return DUPLICATE;
	        }
	else
		{
		$self->time_date( $user );

		$self->next_number( $user );

		my @field_kys = keys %{$Fields{REG}};

		my %save_data = ();

		foreach my $field ( @field_kys )
			{
			print { $self->{'debug_handle'} } "Database:add_user Add user - $query_results[0]{$field}, $field, REG\n"  if  $self->{'debug'};

			my $user_obj = $Fields{REG}{$field};

			if( $user_obj ne 'null' && $user->get($user_obj) )    { $save_data{$field} = $user->$user_obj }

			}

		$self->insert( $Tables{REG}, \%save_data );

		$user->db_record ($self->{'statement'}->{'mysql_insertid'}) if lc($self->{'config'}->db_driver) eq 'mysql';

		if($self->{'config'}->authenticate_method eq 'hs')
			{
			@field_kys = keys %{$Fields{PASS}};

			%save_data = ();

			foreach my $field ( @field_kys )
				{
				print { $self->{'debug_handle'} } "Database:add_user Add user - $query_results[0]{$field}, $field, PASS\n"  if  $self->{'debug'};

				my $user_obj = $Fields{PASS}{$field};

				if( $user_obj ne 'null' && $user->get($user_obj) )    { $save_data{$field} = $user->$user_obj }

				}

			$self->insert( $Tables{PASS}, \%save_data );
			}

        	$user->decrypt_in_place( $self->{'config'} );
		return TRUE;

		}

	}

sub update_user
	{
        my $self = shift;
        my $user = shift;

        return unless ref $user eq 'HealthStatus::User';

        return if lc($self->{'config'}->db_driver) eq 'debug';

        $user->encrypt_in_place( $self->{'config'} );

	my ($stipulations, $lookup, $lookup_val, $lookup_field);

	if( $user->db_id ){
		$lookup = $self->{'config'}->db_id;
		$lookup_val = $self->{'db'}->quote( $user->db_id );
		$lookup_field = 'unum';
		}
        else	{
		$lookup = 'unum';
		$lookup_val = $user->db_number;
		$lookup_field = $self->{'config'}->db_id;
		}

	$stipulations = "WHERE $lookup = $lookup_val";

	print { $self->{'debug_handle'} } "Database - update_user - $lookup_field, $Tables{REG}, $stipulations\n"  if  $self->{'debug'};
        my $query_results  =  $self->select_one_value ( $lookup_field, $Tables{REG}, $stipulations );
        print { $self->{'debug_handle'} } "Database - update_user - $query_results \n"  if  $self->{'debug'};

	if (!$query_results) 	{
        	$user->decrypt_in_place( $self->{'config'} );
		return BAD_ACCOUNT;
		}
	else
		{
		$self->time_date( $user );

		my @field_kys = keys %{$Fields{REG}};

		my %new_data = ();

		foreach my $field ( @field_kys )
			{
	        	my $user_obj = $Fields{REG}{$field};

			if( $user_obj ne 'null' && $user_obj ne 'db_id' && $user_obj ne 'db_number' && $user_obj ne 'db_record'  && $user_obj ne 'db_ip_address'  && $user_obj ne 'db_sortdate'   && $user_obj ne 'db_timestamp' && $user->get($user_obj))    { $new_data{$field} = $user->$user_obj }

			print { $self->{'debug_handle'} } "Database - update_user - $query_results, $field, REG, $Fields{REG}{$field}, $new_data{$field}\n"  if  $self->{'debug'};
			}

		$self->update( $Tables{REG}, \%new_data, $stipulations );

		$query_results  =  $self->select_one_value ( $lookup_field, $Tables{PASS}, $stipulations );
		print { $self->{'debug_handle'} } "Database - update_user - $query_results \n"  if  $self->{'debug'};

		if (!$query_results) 	{
			$user->decrypt_in_place( $self->{'config'} );
			return NOT_LOGGED;
			exit;
			}
		else
			{
			$self->time_date( $user );

			if($self->{'config'}->authenticate_method eq 'hs')
				{
				my @field_kys = keys %{$Fields{PASS}};

				my %new_data = ();

				foreach my $field ( @field_kys )
					{
					my $user_obj = $Fields{PASS}{$field};

					if( $user_obj ne 'null' && $user_obj ne 'db_id' && $user_obj ne 'db_number' && $user_obj ne 'db_record'  && $user_obj ne 'db_ip_address'  && $user_obj ne 'db_sortdate'   && $user_obj ne 'db_timestamp' )    { $new_data{$field} = $user->$user_obj }

					print { $self->{'debug_handle'} } "Database - update_user - $query_results, $field, PASS, $Fields{PASS}{$field}, $new_data{$field}\n"  if  $self->{'debug'};
					}

				$self->update( $Tables{PASS}, \%new_data, $stipulations );
				}

        		$user->decrypt_in_place( $self->{'config'} );

			return TRUE;
			}
		}
	}

sub update_user_login
	{
        my $self = shift;
        my $user = shift;

        return unless ref $user eq 'HealthStatus::User';

        return if lc($self->{'config'}->db_driver) eq 'debug';

        $user->encrypt_in_place( $self->{'config'} );

	my ($stipulations, $lookup, $lookup_val);

	if( $user->db_id ){
		$lookup = $self->{'config'}->db_id;
		$lookup_val = $self->{'db'}->quote( $user->db_id );
		}
        else	{
		$lookup = 'unum';
		$lookup_val = $self->{'db'}->quote( $user->db_number );
		}

	$stipulations = "WHERE $lookup = $lookup_val";

	print { $self->{'debug_handle'} } "1Database - Update User Login - PASS - $Tables{PASS}, $stipulations\n"  if  $self->{'debug'};
	my @query_results  =  $self->select_all ( $Tables{PASS}, $stipulations, 1 );
	print { $self->{'debug_handle'} } "1aUpdate User Login - @query_results \n"  if  $self->{'debug'};

	if (!scalar(@query_results)) 	{
		$user->decrypt_in_place( $self->{'config'} );
		print { $self->{'debug_handle'} } "2Database - Update user Login - failed - @query_results\n"  if  $self->{'debug'};
		return NOT_LOGGED;
		}
	else
		{
		$self->time_date( $user );

		my @field_kys = keys %{$Fields{PASS}};

		my %new_data = ();

		foreach my $field ( @field_kys )
			{
			my $user_obj = $Fields{PASS}{$field};

			if( $user_obj eq 'auth_login_status' || $user_obj eq 'auth_tries' || $user_obj eq 'auth_accesses' || $user_obj eq 'auth_login_time' )    { $new_data{$field} = $user->$user_obj || 1; }
#			if(  $user_obj eq 'auth_login_time' )    { $new_data{$field} = $user->$user_obj }

			}

		$self->update( $Tables{PASS}, \%new_data, $stipulations );

		$user->decrypt_in_place( $self->{'config'} );

		print { $self->{'debug_handle'} } "3Database - Update user Login - OK - %new_data\n"  if  $self->{'debug'};

		return TRUE;
		}
	}

sub site_list
        {
        my $self = shift;
        my $stipulations = shift;

        return if lc($self->{'config'}->db_driver) eq 'debug';

        my @query_results = ();

        my $field = 'site';

        $field = uc($field) if ( lc($self->{'config'}->db_driver) eq 'oracle' );

        $stipulations .= ' ORDER BY site';

        if($Tables{REG} && $self->{'config'}->authenticate_method eq 'hs' )
        	{
        	print { $self->{'debug_handle'} } "Database:Site List from REG - $field, $stipulations \n"  if  $self->{'debug'};
        	@query_results  =  $self->select_one_column_distinct ( $field, $Tables{REG}, $stipulations);
        	}
        else	{
		my @assessments = split /\s+/, $self->{'config'}->ggr_tables;
        	print { $self->{'debug_handle'} } "Site List from EM - $field, $stipulations \n"  if  $self->{'debug'};
		my %site_hash;
		foreach (@assessments) {
			my @query_results  =  $self->select_one_column_distinct ( $field, $Tables{$_}, $stipulations);
			foreach my $q_result (@query_results){
				$site_hash{$q_result} = 1;
				}
			}
		foreach my $group (sort keys %site_hash){
			push(@query_results, $group);
			}
	        }

        print { $self->{'debug_handle'} } "Database:Site List - @query_results \n"  if  $self->{'debug'};


        { @query_results }
        }

=item get_assessments

Retrieves all matching assessments in an array of hashes

In:
$assessments: array of assessment types to search
$stipulations: The WHERE clause
$fields: array of fields to retrieve.
$options: Extra information such as ordering, limits, etc.

Out:
$resultset - an array of hashes

Note that the number of rows read is not the total number of
rows in the set, just the number of rows that have been read
*this time through*.

=cut
sub get_assessments {
	my ($self, $assessments, $stipulations, $fields, $options) = @_;
	my $sth = $self->get_assessments_sth($assessments, $stipulations, $fields, $options);
	my @to_return = ();
	my $limit = $$options{limit};
	my $rowcount = 0;
	my $tmp;

	# TODO: Find a portable, better way of getting results X..Y
	#  (right now I'm just reading to the offset I want)
	if ($$options{offset}) {foreach(1 .. $$options{offset}) {$sth->fetchrow_hashref();}}

	while (!$limit || $rowcount < $limit) {
		$tmp = $$self{sth}->fetchrow_hashref();
		last if !$tmp;
		push @to_return, $tmp;
		$rowcount++;
	}

	# Return the whole array, or just the first result if they want a scalar.
	return wantarray() ? @to_return : $to_return[0];
}

=item get_assessments_sth

Retrieves a statement handle for retrieving all matching assessments

In:
$assessments: array of assessment types to search
$stipulations: The WHERE clause
$fields: array of fields to retrieve.
$options: Extra information such as ordering, limits, etc.

Out:
$sth - The statement handle from which one may fetch results

=cut
sub get_assessments_sth() {
	my ($self, $assessments, $stipulations, $fields, $options) = @_;
	$options ||= {};
	$fields = (ref $fields eq 'ARRAY' ? $fields : [$fields]);
	$assessments = (ref $assessments eq 'ARRAY' ? $assessments : [$assessments]);

	# Default fields (enough to uniquely identify an assessment)
	# Place them in the fields array if they are not in already
	foreach my $f('<assessment_type> AS assessment_type', 'xnum') {
		if (!grep(/^$f$/, @$fields)) {push @$fields, $f;}
	}

	# Make things easier - if this is a straight-up fieldname
	# (without any special functions/treatement) assume it's
	# going to be retrieved from the assessment, not the user
	foreach my $i (0 .. (@$fields - 1)) {if ($$fields[$i] =~ /^\w+$/) {$$fields[$i] = "a." . $$fields[$i];}}

	my $base_statement = "SELECT " . join(',', @$fields) . " FROM <table> a";

	if (!$$options{no_join_user}) {$base_statement .= " LEFT JOIN $Tables{REG} u ON a.unum=u.unum ";}
	$base_statement .= $stipulations;
	$base_statement = "($base_statement)";
	my @statements;
	my $tmp;

	# Create a super-query that is a UNION of individual queries - each
	# getting information from one assessment table.
	foreach my $i (0 .. $#$assessments) {
		($statements[$i] = $base_statement) =~ s/<table>/$Tables{$$assessments[$i]}/g;
		$statements[$i] =~ s/<assessment_type>/'$$assessments[$i]'/g;
	}

	my $sql = join("\n UNION \n", @statements) . ' ' . $$options{order_by};

	carp "Database get_assessments_sth - ".$sql;

	$$self{sth} = $$self{db}->prepare($sql);
	$$self{sth}->execute();
	return $$self{sth};
}


sub group_assessment_count
        {
        my $self = shift;
        my $breakout_field = shift;
        my $assessment = shift;
        my $stipulation = shift;
        my $group_by = shift;
        my $nulls = shift;

        return if lc($self->{'config'}->db_driver) eq 'debug';

        my @query_results = ();

        my $field = $breakout_field;
        my $lookup = $self->{'config'}->db_id;

        if(!$field){ print { $self->{'debug_handle'} } "$breakout_field - not found in the Registered user table\n"; return 0; }

	if ( lc($self->{'config'}->db_driver) eq 'oracle' )
		{
        	$field = uc($field);
        	$lookup = uc($lookup);
        	}

        my $focus = $Tables{REG} . '.' . $field;
        my $connect1 = '';
        $connect1 = ' and ' if ($stipulation);
        my $connect = '';
        $connect = ' and ' if ($stipulation && $nulls);
        $stipulation = $Tables{REG} . '.' . $stipulation if ($stipulation);
        my $group_by_phrase = ' group by ' . $focus if($group_by);
        my $null_phrase = $Tables{$assessment} . '.' . $field . " is NULL" if ($nulls);

        my $sql = 'Select  count(' . $focus . ') as counter from ' .  $Tables{REG} . ', ' . $Tables{$assessment} . ' where ' . $Tables{REG} . '.' . $lookup . ' = ' . $Tables{$assessment} . '.' . $lookup . $connect1 . $stipulation . $connect . $null_phrase . $group_by_phrase;
	$self->{'sql'}  =  $sql;
	print { $self->{'debug_handle'} } "Database:group_assessment-count hs_count - $self->{'sql'}\n"  if  $self->{'debug'};

	{
	my @query_results  =  $self->__sql_execute();

	$self->debug( "@query_results \n" );

	return $query_results[0]->[0];
	}
}

# Returns a list of distinct values from the user table.
#
# In:
# $in_field: Field to retrieve from the database.
# $stipulations: Where/Orderby clauses for results.
sub reg_group_list
        {
        my $self = shift;
        my $in_field = shift;
        my $stipulations = shift;
        my $root = shift;

        print { $self->{'debug_handle'} } "Database:reg group List top \n"  if  $self->{'debug'};
        return if lc($self->{'config'}->db_driver) eq 'debug';

        $stipulations =~ s/A\.//g;

# Oracle needs to be told our date format.
	if ( lc($self->{'config'}->db_driver) eq 'oracle' )
		{
		my $APrev = "ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY-MM-DD HH24:MI:SS'";
		$self->execute_sql($APrev);
		}

        my @query_results = ();

        my $field = $in_field;

        $field = uc($field) if ( lc($self->{'config'}->db_driver) eq 'oracle' );

	my @stip_conditions;
	my $connector = '=';
	my $close = "'";
	my $stip_conditions;
	if($root){
		$_ = $root;
		if(/\/$/){
			$connector = ' LIKE ';
			$close = q|%'|; #'
			}
		$stip_conditions = $field . $connector . " '" . $root . $close;
		}

	$stipulations = 'WHERE ' if $stipulations eq '' && $root;
	$stipulations .= ' and ' if $stipulations ne 'WHERE ' && $root;
	$stipulations .= $stip_conditions if $root;
        print { $self->{'debug_handle'} } "Database:reg group List - $stipulations \n"  if  $self->{'debug'};

        if($Tables{REG})
        	{
        	print { $self->{'debug_handle'} } "Database:reg group List $in_field List from REG - $field, $stipulations \n"  if  $self->{'debug'};
        	@query_results  =  $self->select_one_column_distinct ( $field, $Tables{REG}, $stipulations);
        	}

        print { $self->{'debug_handle'} } "Database:reg group List - @query_results \n"  if  $self->{'debug'};

        { @query_results }
        }
# Returns a list of distinct values from the user table.
#
# In:
# $in_field: Field to retrieve from the database.
# $stipulations: Where/Orderby clauses for results.
sub assessment_group_list
        {
        my $self = shift;
        my $in_field = shift;
        my $assessment_ref = shift;
        my $stipulations = shift;
        my $root = shift;

        $stipulations =~ s/A\.//g;

        print { $self->{'debug_handle'} } "Database: Assessment group List top \n"  if  $self->{'debug'};
        return if lc($self->{'config'}->db_driver) eq 'debug';

# Oracle needs to be told our date format.
	if ( lc($self->{'config'}->db_driver) eq 'oracle' )
		{
		my $APrev = "ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY-MM-DD HH24:MI:SS'";
		$self->execute_sql($APrev);
		}

        my @query_results = ();
        my @query_results2 = ();

        my $field = $in_field;

        $field = uc($field) if ( lc($self->{'config'}->db_driver) eq 'oracle' );

	my @stip_conditions;
	my $connector = '=';
	my $close = "'";
	my $stip_conditions;
	if($root){
		$_ = $root;
		if(/\/$/){
			$connector = ' LIKE ';
			$close = q|%'|; #'
			}
		$stip_conditions = $field . $connector . " '" . $root . $close;
		}

	$stipulations = 'WHERE ' if $stipulations eq '' && $root;
	$stipulations .= ' and ' if $stipulations ne 'WHERE ' && $root;
	$stipulations .= $stip_conditions if $root;
        print { $self->{'debug_handle'} } "Database: Assessment group List - $stipulations \n"  if  $self->{'debug'};

        print { $self->{'debug_handle'} } "Database: Assessment group List assessments to use @$assessment_ref \n"  if  $self->{'debug'};
        foreach my $table ( @$assessment_ref )
        	{
        	if($Tables{$table}){
			print { $self->{'debug_handle'} } "Database: Assessment group List $in_field List from $table - $field, $stipulations \n"  if  $self->{'debug'};
			my @query_results1  =  $self->select_one_column_distinct ( $field, $Tables{$table}, $stipulations);
			print { $self->{'debug_handle'} } "Database: Assessment group List from $table - @query_results \n"  if  $self->{'debug'};
			push (@query_results2, @query_results1);
			}
        	}

        print { $self->{'debug_handle'} } "Database: Assessment group List  - @query_results \nReturning\n"  if  $self->{'debug'};
        my %remove_duplicates= ();
        foreach my $item (@query_results2){
        	$remove_duplicates{$item}++;
        	}
        @query_results = keys %remove_duplicates;

        { @query_results }
        }


# batch_list
# Returns a list of distinct values from the user table. with at least one entry in an assessment table
#
# In:
# $in_field: Field to retrieve from the database.
# @assessments: list of assessments to check
# $stipulations: Where/Orderby clauses for results.
#
sub batch_list
        {
        my $self = shift;
        my $in_fields = shift;
        my $assessment_ref = shift;
        my $stipulations = shift;

        return if lc($self->{'config'}->db_driver) eq 'debug';

# Oracle needs to be told our date format.
	if ( lc($self->{'config'}->db_driver) eq 'oracle' )
		{
		my $APrev = "ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY-MM-DD HH24:MI:SS'";
		$self->execute_sql($APrev);
		}

        my @query_results = ();
	my @returned_recs;

        my $field = $in_fields;

        my @desired_fields;
        my @desired_fields_wanted = ( 'adate', 'xnum', 'last_name', 'first_name', 'client2', 'tmplte' );

	my $assessment_field = $self->{'config'}->batch_id;
        $field = uc($field) if ( lc($self->{'config'}->db_driver) eq 'oracle' );
        $assessment_field = uc($assessment_field) if ( lc($self->{'config'}->db_driver) eq 'oracle' );

        if($Tables{REG})
        	{
        	print { $self->{'debug_handle'} } "Database:batch_list $in_fields List from REG - $field, $stipulations \n"  if  $self->{'debug'};
        	@query_results  =  $self->select_one_column_distinct ( $field, $Tables{REG}, $stipulations);
        	}

	foreach my $batch_number (@query_results){
        	my @query_results1 = ();
		print { $self->{'debug_handle'} } "Database:batch_list - @query_results \n"  if  $self->{'debug'};

		my $assessment_stipulations = "WHERE ".$self->{'config'}->db_id." = ".$self->{'db'}->quote( $batch_number );

		my @results;
		my $cnt =0;

		#loop through the assessment list passed to us, look up all the assessments taken by the user for that
		#assessment, then add a key value telling us which assessment it is then add them to @results for return
		foreach my $table ( @$assessment_ref ){
			print { $self->{'debug_handle'} } "Database:batch list - $table - $Tables{$table}, $assessment_stipulations\n"  if  $self->{'debug'};
			if($Tables{$table}){
				 foreach my $fw (@desired_fields_wanted)
					{
					print { $self->{'debug_handle'} } "$fw - $Fields{$table}{$fw}, " if  $self->{'debug'};
					push(@desired_fields, $fw ) if(exists $Fields{$table}{$fw}) ;
					}
				print  { $self->{'debug_handle'} } " - $table\n" if  $self->{'debug'};
				@query_results1  =  $self->select( \@desired_fields, $Tables{$table}, $assessment_stipulations, 1 );
				$cnt += scalar(@query_results1);
				}
			else 	{  warn "This is not a valid assessment name.\n" }
			}
		carp "qr - ".$cnt." stip - ".$assessment_stipulations." id - ".$self->{'config'}->batch_id. " results - ".$self->select_one_value( $self->{'config'}->batch_id, $Tables{REG}, $assessment_stipulations)."\n";
		if($cnt){ push @returned_recs, $self->select_one_value( $self->{'config'}->batch_id, $Tables{REG}, $assessment_stipulations); }
#		if(scalar(@query_results1)){ push @returned_recs, $batch_number;}

		}



	{ @returned_recs; }
        }

sub get_users_bio_taken
        {
        my $self = shift;
        my $user = shift;
        my $config = shift;
        my $assessments = shift;
        my $stipulation = shift;

        return unless ref $user   eq 'HealthStatus::User';
        return unless ref $config eq 'HealthStatus::Config';

        my @desired_fields;
        my @desired_fields_wanted = ( 'adate', 'xnum', 'last_name', 'first_name', 'tmplte', 'client1', 'client2', 'client3', 'client4', 'client5', 'client6', 'client7' );


	my $assessment = 'BIO';
        $user->encrypt_in_place( $self->{'config'} );

        $self->{'db_id'} = $self->{'config'}->db_id;
        $self->{'user_db_id'} = $user->db_id;

# Oracle needs to be told our date format.
	if ( lc($self->{'config'}->db_driver) eq 'oracle' )
		{
		my $APrev = "ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY-MM-DD HH24:MI:SS'";
		$self->execute_sql($APrev);
		$self->{'db_id'} = uc($self->{'db_id'});
#		$self->{'user_db_id'} = uc($self->{'user_db_id'});
		}

#print "DB: stipulation $stipulation<br>";
	my $status;

	my $rec_count = $self->count (  $Tables{$assessment}, $stipulation );

	print { $self->{'debug_handle'} } "Database:get_users_bio - records found = $rec_count\n"  if  $self->{'debug'};

	if ($rec_count > 0)
		{
		$stipulation .= " Order by xnum ";
		$stipulation .= 'DESC';

		my @query_results  =  $self->select_one_row(  [ "*" ], $Tables{$assessment}, $stipulation, 1 );
		$self->process_user_assessment($user, $query_results[0], $assessment);

		$status = 1;
		}

        $user->decrypt_in_place( $self->{'config'} );

        return $status;
 #
#  copy from my @results in users_assessments_taken if above doesn't work out.
#       my @results;

        }

sub get_users_assessments_taken
        {
        my $self = shift;
        my $user = shift;
        my $config = shift;
        my $assessments = shift;
        my $stipulation = shift;


        return unless ref $user   eq 'HealthStatus::User';
        return unless ref $config eq 'HealthStatus::Config';

        my @desired_fields;
        my @desired_fields_wanted = ( 'adate', 'xnum', 'last_name', 'first_name', 'tmplte' );


        $user->encrypt_in_place( $self->{'config'} );

        $self->{'db_id'} = $self->{'config'}->db_id;
        $self->{'user_db_id'} = $user->db_id;

# Oracle needs to be told our date format.
	if ( lc($self->{'config'}->db_driver) eq 'oracle' )
		{
		my $APrev = "ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY-MM-DD HH24:MI:SS'";
		$self->execute_sql($APrev);
		$self->{'db_id'} = uc($self->{'db_id'});
#		$self->{'user_db_id'} = uc($self->{'user_db_id'});
		}

#print "DB: stipulation $stipulation<br>";
	my $stipulations = do	{if(!$stipulation)	{"WHERE $self->{'db_id'} = ";}
        			 else			{$stipulation . " AND $self->{'db_id'} = ";}
        			 };

        $stipulations .= $self->{'db'}->quote( $self->{'user_db_id'} );

        my @results;

        #loop through the assessment list passed to us, look up all the assessments taken by the user for that
        #assessment, then add a key value telling us which assessment it is then add them to @results for return
        foreach my $table ( @$assessments ){
    		print { $self->{'debug_handle'} } "Database:get users assessments taken - $table - $Tables{$table}, $stipulations\n"  if  $self->{'debug'};
        	if($Tables{$table}){
		 foreach my $fw (@desired_fields_wanted)
			{
			print { $self->{'debug_handle'} } "$fw - $Fields{$table}{$fw}, " if  $self->{'debug'};
			push(@desired_fields, $fw ) if(exists $Fields{$table}{$fw}) ;
			}
		print  { $self->{'debug_handle'} } " - $table\n" if  $self->{'debug'};
       		my @query_results  =  $self->select( \@desired_fields, $Tables{$table}, $stipulations, 1 );
        		for ( @query_results){
        			my %temp_hash = ();
        			%temp_hash = %$_;
				if ( lc($self->{'config'}->db_driver) eq 'oracle' )
					{
					my %temp1_hash;
					foreach (keys %temp_hash){ $temp1_hash{$ORACLE_CVRT{uc($_)}} = $temp_hash{$_}; print { $self->{'debug_handle'} } "$_ - $ORACLE_CVRT{uc($_)} - $temp_hash{$_} - $table\n"  if  $self->{'debug'}; }
					$temp1_hash{assessment} = $table;
					push @results, \%temp1_hash;
					}
				else
					{
					$temp_hash{assessment} = $table;
					push @results, \%temp_hash;
					}
        			}
        		}
        	else 	{  warn "This is not a valid assessment name.\n" }
        	}
	$user->pretty_print( $self->{'debug_handle'} ) if $self->{'debug'};

        $user->decrypt_in_place( $self->{'config'} );

	$user->pretty_print( $self->{'debug_handle'} ) if $self->{'debug'};

	my @sorted_results = map { $_->[2] }
		     sort { $b->[1] cmp $a->[1] || $a->[0] cmp $b->[0] }
		     map { [$_->{assessment}, $_->{adate}, $_] } @results;

        { @sorted_results }
        }

sub get_users
        {
        my $self = shift;
        my $config = shift;
        my $assessments = shift;
        my $countem = shift;

        my %user_hash=();

        my $field = $self->{'config'}->db_id;
        my $field1 = $field;
        $field = uc($field) if ( lc($self->{'config'}->db_driver) eq 'oracle' );

        my @user_list = ();

        foreach ( @$assessments )
        	{
        	print { $self->{'debug_handle'} } "Database:Get Users - $field, $_  \n"  if  $self->{'debug'};
        	my @query_results  =  $self->select_one_column( $field, $Tables{$_} );
        	foreach my $id ( @query_results ) {
        		print { $self->{'debug_handle'} } "Database:Get Users - $id, $_ , $Tables{$_} \n"  if  $self->{'debug'};
        		++$user_hash{$id}{$_};
        		++$user_hash{$id}{total};
        		}
        	}

        { \%user_hash }
        }

sub get_users_by_stipulation
        {
        my $self = shift;
        my $config = shift;
        my $assessments = shift;
        my $stipulations = shift;
        my $multi = shift;

        my %user_hash=();

        my $field = '';

        $field = 'u.' if $multi;

        $field .= $self->{'config'}->db_id;

        my @user_list = ();

# Oracle needs to be told our date format.
	if ( lc($self->{'config'}->db_driver) eq 'oracle' )
		{
        	$field = uc($field);
		my $APrev = "ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY-MM-DD HH24:MI:SS'";
		$self->execute_sql($APrev);
		}

        foreach ( @$assessments )
        	{
        	print { $self->{'debug_handle'} } "Database:Get Users by stip- $field, $_ , $stipulations\n"  if  $self->{'debug'};
        	my @query_results  =  $self->select_one_column ( $field, $Tables{$_}, $stipulations );
        	foreach my $id ( @query_results ) { ++$user_hash{$id}{$_}; ++$user_hash{$id}{total};print { $self->{'debug_handle'} } "Get Users by stip id - $id \n"  if  $self->{'debug'}; }
        	}

        { \%user_hash }
        }

sub hs_count {
    my $self          =  shift;
    my $assessment    =  shift;
    my $stipulations  =  shift;

    print { $self->{'debug_handle'} } "Database:hs_count - ".$assessment.' - '. $Tables{$assessment}.' - '.$stipulations."\n"  if  $self->{'debug'};
    $self->{'sql'}  =  "SELECT COUNT(*) FROM $Tables{$assessment} $stipulations";
    print { $self->{'debug_handle'} } "Database:hs_count - $self->{'sql'}\n"  if  $self->{'debug'};

    my @query_results  =  $self->__sql_execute();
    return $query_results[0]->[0];
}

sub count_users
	{
        my $self = shift;
        my $config = shift;
        my $assessments = shift;
        my $stipulations = shift;

        my $count_results;

        my %user_hash=();

        my $field = $self->{'config'}->db_id;

        my @user_list = ();

# Oracle needs to be told our date format.
	if ( lc($self->{'config'}->db_driver) eq 'oracle' )
		{
        	$field = uc($field);
		my $APrev = "ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY-MM-DD HH24:MI:SS'";
		$self->execute_sql($APrev);
		}

        foreach ( @$assessments )
        	{
        	print { $self->{'debug_handle'} } "Database:Count Users by stip- $field, $_ , $stipulations\n"  if  $self->{'debug'};
        	my @query_results  =  $self->select_one_column ( $field, $Tables{$_}, $stipulations );
        	foreach my $id ( @query_results ) { ++$user_hash{$id}{$_}; ++$user_hash{$id}{total}; }
        	}

        my @users = keys %user_hash;
        $count_results = scalar(@users);
        return $count_results;
        }

sub get_users_details
{
	my $self = shift;
	my $config = shift;
	my $assessments = shift;
	my $user_list = shift;
	my $stipulation_in = shift;
	my $unique = shift;
	my $batchlookup = shift;

	my $stipulations;
	if ( ref($stipulation_in) eq 'ARRAY' ) {

#print 'stipulation is an array<br>';

		my $stip_count = @$stipulation_in;
		my @temp_stip = @$stipulation_in;
		my $count=1;
		while ($count < $stip_count){
			$temp_stip[$count]=~ s/WHERE //i;
			++$count;
			}
		$stipulations= join(' and ', @temp_stip);
		}
	else	{
		$stipulations = $stipulation_in;
		}
	my $count_results;
	my %user_count;

	my %user_hash;

	my $field = "A." . $self->{'config'}->db_id;
       	my $field_a = $self->{'config'}->db_id;
      	my $field_xnum = 'xnum';

        my @user_list = ();

        my $select_mode = 'SELECT ';

	print { $self->{'debug_handle'} } "Database:get users details:\n" if ( $self->{'debug'});
# Oracle needs to be told our date format.
	if ( lc($self->{'config'}->db_driver) eq 'oracle' )
		{
		print { $self->{'debug_handle'} } "Database:get users details oracle\n" if ( $self->{'debug'});
		$field = uc($field);
		$field_a = uc($field_a);
		$field_xnum = uc($field_xnum);
		my $APrev = "ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY-MM-DD HH24:MI:SS'";
		$self->execute_sql($APrev);
		}
	my $j=0;
	my $list_uid = "";
	foreach my $list ( @$user_list )
		{
		my $stip = $stipulations;
		print { $self->{'debug_handle'} } "\n$j - $list\n" if ( $self->{'debug'} && $j > 899);
		$list_uid = $self->{'db'}->quote($list);
		$stip =~ s/XX_X_XX/$list_uid/;
		print { $self->{'debug_handle'} } "$j - $list_uid - $stip\n" if ( $self->{'debug'} && $j > 899 );

		foreach my $table ( @$assessments )
			{
			my $sql_statement;
			if( $config->authenticate_method eq 'hs' || $config->authenticate_method eq 'client'){
				$sql_statement = "$select_mode $field, $field_xnum FROM $Tables{REG} U, $Tables{$table} A $stip";
				}
			else	{
				$sql_statement = "$select_mode $field_a, $field_xnum FROM $Tables{$table} $stip";
				}

#print "Database:Get Users assessments details part 1 - $field, $table, $list, $list_uid, $sql_statement\n"  if ( $j < 5 );
			print { $self->{'debug_handle'} } "Database:Get Users assessments details part 1 - $field, $table, $list, $list_uid, $sql_statement<br>\n"  if ( $self->{'debug'} );
			$self->{'sql'}    =  $sql_statement;
			my @query_results  =  $self->__sql_execute ( 1 );

			$count_results += scalar(@query_results);

			if ( ( $j % 100 ) == 0 && $j > 1){ print "\0"; }

#print  "Database:Get Users assessments count retrieved: $count_results<br><br>\n"  if ( $j < 5 );
			print { $self->{'debug_handle'} } "Database:Get Users assessments count retrieved: $count_results\n"  if ( $self->{'debug'});

			foreach my $id ( @query_results )
				{
				if($user_hash{$id->{$field_a}}{$table} && !$unique){
					$user_hash{$id->{$field_a}}{$table} .= ',' .$id->{$field_xnum};}
				elsif($user_hash{$id->{$field_a}}{$table} && $batchlookup && (substr($list, 0, 4) eq 'b200' || substr($list, 0, 4) eq 'b201') ){
					$user_hash{$id->{$field_a}}{$table} .= ',' .$id->{$field_xnum};}
				else	{
					$user_hash{$id->{$field_a}}{$table} = $id->{$field_xnum};}
				++$user_count{$id->{$field_a}}{$table};
				++$user_count{$id->{$field_a}}{total};

				print { $self->{'debug_handle'} } "Database:Get Users assessments details part 2 - " . $id->{$field_xnum} . ' - ' . $id->{$field_a} . " \n"  if ( $self->{'debug'});
				++$j;
				}
			}
        		$user_hash{hs_selected} = TRUE;
        		$self->debug_off() if ($j > 30);

		}
	my @users = keys %user_count;
	print { $self->{'debug_handle'} } "Database:Get Users assessments total user count: ". scalar(@users)  if ( $self->{'debug'});
	$user_hash{count_results} = $count_results;

        	{return \%user_hash};
}

sub get_users_assessments_by_stipulation
        {
        my $self = shift;
        my $config = shift;
        my $assessments = shift;
        my $stipulations = shift;

        my %user_hash=();

        my $field = "u." . $self->{'config'}->db_id;
        my $field_a = $self->{'config'}->db_id;
        my $field_xnum = $self->{'config'}->db_record;

        my @user_list = ();

# Oracle needs to be told our date format.
	if ( lc($self->{'config'}->db_driver) eq 'oracle' )
		{
        	$field = uc($field);
		my $APrev = "ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY-MM-DD HH24:MI:SS'";
		$self->execute_sql($APrev);
		}

        foreach ( @$assessments )
        	{
        	my $field_date = $Fields{$_}{db_sortdate};
        	my $sql_statement = "SELECT DISTINCT $field, $field_xnum FROM $Tables{REG} u JOIN $Tables{$_} a ON a." . $field_a . " = u." . $field_a ." ORDER by " . $field_date . " ASC";
        	print { $self->{'debug_handle'} } "Database:Get Users assessments by stip- $field, $_ , $sql_statement\n"  if  $self->{'debug'};
        	my @query_results  =  $self->execute_sql ( $sql_statement, 1 );
        	foreach my $id ( @query_results ) { $user_hash{$id->{$field_a}}{$_} = $id->{$field_xnum}; ++$user_hash{$id->{$field_a}}{total};print { $self->{'debug_handle'} } "Get Users by stip id - " . $id->{$field_a} ." \n"  if  $self->{'debug'}; }
        	}
        	$user_hash{hs_selected} = TRUE;

        { \%user_hash }
        }

sub get_users_assessment
        {
        my $self = shift;
        my $user = shift;
        my $config = shift;
        my $assessment = shift;
        my $record = shift;

        my %height = ();
        my $status = 0;
        my $record_name = 'xnum';

        $assessment = uc($assessment);

        return unless ref $user   eq 'HealthStatus::User';
        return unless ref $config eq 'HealthStatus::Config';

        return if lc($self->{'config'}->db_driver) eq 'debug';

        $user->encrypt_in_place( $self->{'config'} );

        $self->{'db_id'} = $self->{'config'}->db_id;
        $self->{'user_db_id'} = $user->db_id;

# Oracle needs to be told our date format.
	if ( lc($self->{'config'}->db_driver) eq 'oracle' )
		{
		my $APrev = "ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY-MM-DD HH24:MI:SS'";
		$self->execute_sql($APrev);
        	$record_name = uc($record_name);
        	$self->{'db_id'} = uc($self->{'db_id'});
		}

        my $stipulations = "WHERE $record_name = ";
        $stipulations .= $self->{'db'}->quote( $record );
        $stipulations .= " AND $self->{'db_id'} = ";
        $stipulations .= $self->{'db'}->quote( $self->{'user_db_id'} );

	my $rec_count = $self->count (  $Tables{$assessment}, $stipulations );

	print { $self->{'debug_handle'} } "Database:get users assessment - records found = $rec_count\n"  if  $self->{'debug'};

	if ($rec_count > 0)
		{
		my @query_results  =  $self->select_all( $Tables{$assessment}, $stipulations, 1 );
		$self->process_user_assessment($user, $query_results[0], $assessment);

		$user->set_assessment_date ( );
		$status = 1;
		}

        $user->decrypt_in_place( $self->{'config'} );

        return $status;
        }

sub get_user_registration {
	my ($self, $fields, $stipulation, $options) = @_;

	my @fieldlist = @$fields;
	my @fieldslist;
	my %FieldsbyValue;
	my @results;
	my @ufield_keys;
	my @afield_keys;
	my $key;
	my $value;
	my $limit = $$options{limit};
	my $rowcount = 0;
	my $tmp;
	if (!$limit){ $limit = 0; }

	while (($key, $value) = each %{$Fields{PASS}}) {
		$FieldsbyValue{PASS}{$value} = $key;
	}
	while (($key, $value) = each %{$Fields{REG}}) {
		$FieldsbyValue{REG}{$value} = $key;
	}

	foreach my $field (@fieldlist){
		if(defined $FieldsbyValue{REG}{$field}){
			push @fieldslist, "u.".$FieldsbyValue{REG}{$field} ;
			push @ufield_keys, $FieldsbyValue{REG}{$field};
			}
		elsif(defined $FieldsbyValue{PASS}{$field})	{
			push @fieldslist, "a.".$FieldsbyValue{PASS}{$field} ;
			push @afield_keys, $FieldsbyValue{PASS}{$field};
			}
		}

	$stipulation = ' '.$stipulation;


        my $sql_statement = "SELECT ". join(',', @fieldslist) ." FROM $Tables{REG} u, $Tables{PASS} a where a." . $FieldsbyValue{PASS}{db_id} . " = u." . $FieldsbyValue{REG}{db_id} . $stipulation. " ORDER by " . $FieldsbyValue{REG}{db_fullname} . " ASC";

        print { $self->{'debug_handle'} } "Database:get_user_registration ready to process-" . $sql_statement .   "\n"  if  $self->{'debug'};

	my (@query_results)  =  $self->execute_sql_return( $sql_statement, 1 );

	my $total_count = scalar(@query_results);

	my $cnt = 0;

	if (scalar(@query_results) > 0){
		foreach my $working (@query_results){
			my %result;
#			print { $self->{'debug_handle'} } "Database:get_user_registration a - ". $working.' - '. $limit.' - '.$$options{offset}.' - '.$cnt."\n";
			if ($$options{offset} && $$options{offset} > $cnt) {
#				print { $self->{'debug_handle'} } "Database:get_user_registration - ". $working.' - '.$$options{offset}.' - '.$cnt."\n";
				++$cnt;
				next;
				}
			if (!$limit || $rowcount < $limit) {
				$rowcount++;
	#			print { $self->{'debug_handle'} } "Database:get_user_registration - ". $working;

#				foreach (keys %$working){print { $self->{'debug_handle'} } "Database:get_user_registration - $_ =". $$working{$_};}
				foreach my $field ( @afield_keys ) {
					my $obj_name = $field;
					$obj_name = $ORACLE_CVRT{uc($field)} if  lc($self->{'config'}->db_driver) eq 'oracle' ;
					$obj_name = $POSTGRES_CVRT{lc($field)} if  lc($self->{'config'}->db_driver) eq 'postgres' ;

					my $user_obj = $Fields{PASS}{$obj_name};
					$user_obj = $obj_name if(!$user_obj);
					$user_obj = $Fields{PASS}{$field} if !($user_obj);

					print { $self->{'debug_handle'} } "Database:get_user_registration - $field - $obj_name, $user_obj," . $$working{$field} . ", PASS\n"  if  $self->{'debug'};

					$result{$user_obj} = $$working{$field};
					}
				foreach my $field ( @ufield_keys ) {
					my $obj_name = $field;
					$obj_name = $ORACLE_CVRT{uc($field)} if  lc($self->{'config'}->db_driver) eq 'oracle' ;
					$obj_name = $POSTGRES_CVRT{lc($field)} if  lc($self->{'config'}->db_driver) eq 'postgres' ;

					my $user_obj = $Fields{REG}{$obj_name};
					$user_obj = $obj_name if(!$user_obj);
					$user_obj = $Fields{REG}{$field} if !($user_obj);

					print { $self->{'debug_handle'} } "Database:get_user_registration - $field - $obj_name, $user_obj," . $$working{$field} . ", REG\n" if  $self->{'debug'};

					$result{$user_obj} = $$working{$field};
					}

				++$cnt;
				$result{db_pos_count} = $cnt;
				$self->__add_to_array( \%result, \@results );
				}
			}
		}
	else	{
		return (0,0);
		}
	return ($total_count, \@results);
}

sub get_users_first_assessment
	{
        my $self = shift;
        my $user = shift;
        my $config = shift;
        my $assessment = shift;

	my $status = $self->get_users_first_or_last_assessment($user, $config, $assessment, 0);

        return $status;
	}
sub get_users_last_assessment
	{
        my $self = shift;
        my $user = shift;
        my $config = shift;
        my $assessment = shift;

	my $status = $self->get_users_first_or_last_assessment($user, $config, $assessment, 1);

        return $status;
	}
sub get_users_first_or_last_assessment
        {
        my $self = shift;
        my $user = shift;
        my $config = shift;
        my $assessment = shift;
        my $last = shift;

        my %height = ();
        my $status = 0;
        my $record_name = 'xnum';

        $assessment = uc($assessment);

        return unless ref $user   eq 'HealthStatus::User';
        return unless ref $config eq 'HealthStatus::Config';

        return if lc($self->{'config'}->db_driver) eq 'debug';

        $user->encrypt_in_place( $self->{'config'} );

        $self->{'db_id'} = $self->{'config'}->db_id;
        $self->{'user_db_id'} = $user->db_id;

# Oracle needs to be told our date format.
	if ( lc($self->{'config'}->db_driver) eq 'oracle' )
		{
		my $APrev = "ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY-MM-DD HH24:MI:SS'";
		$self->execute_sql($APrev);
        	$record_name = uc($record_name);
        	$self->{'db_id'} = uc($self->{'db_id'});
		}

        my $stipulations = "WHERE $self->{'db_id'} = ";
        $stipulations .= $self->{'db'}->quote( $self->{'user_db_id'} );
        $stipulations .= " Order by $record_name ";
        $stipulations .= 'ASC' if(!$last);
        $stipulations .= 'DESC' if ($last);
   
	my $rec_count = $self->count (  $Tables{$assessment}, $stipulations );

	print { $self->{'debug_handle'} } "Database:get_users_first_or_last_assessment - records found = $rec_count\n"  if  $self->{'debug'};

	if ($rec_count > 0)
		{
		my @query_results  =  $self->select_one_row(  [ "*" ], $Tables{$assessment}, $stipulations, 1 );
		
		$self->process_user_assessment($user, $query_results[0], $assessment);

		$user->set_assessment_date ( );
		$status = 1;
		}

        $user->decrypt_in_place( $self->{'config'} );

        return $status;
        }

sub get_user {
	my ($self, $stipulation, $hash) = @_;
	my %hash;
	%hash = %$hash if ref $hash eq 'HASH';

	my $res1 = $self->select_one_row
		('*', $Tables{REG}, $stipulation, 1);
	if(!defined $res1) {return undef;}

	my $res2 = $self->select_one_row
		('*', $Tables{PASS},
		 "WHERE unum=$$res1{unum}", 1);
	if(!defined $res2) {return undef;}

	my $tmp = $Fields{REG};
	foreach(keys %$tmp) {$hash{$$tmp{$_}} = $$res1{lc($_)};}
	$tmp = $Fields{PASS};
	foreach(keys %$tmp) {$hash{$$tmp{$_}} = $$res2{lc($_)};}

	# TODO
	# Legacy code - Due to the way templates are loaded on some
	# pages, a User is expected to have a "config" key containing
	# the configuration hash, even though this key is not
	# found anywhere in HealthStatus::User.  Old pages
	# should be rewritten to avoid this, and this code
	# should then be removed.
	$hash{config} = $$self{config}->as_hash();
	return new HealthStatus::User({%hash});
}

sub get_user_by_id {
	my ($self, $id, $hash) = @_;
	if ($id !~ /^\d+$/) {return undef;}
	return $self->get_user("WHERE unum=$id", $hash);
}

sub get_user_by_uname {
	my ($self, $uname, $hash) = @_;
	return $self->get_user("WHERE " . $self->{'config'}->db_id . "=" . $self->quote($uname), $hash);
}


=item process_user_assessment

Takes an assessment record and uses it to set all of
the appropriate fields for a User object

In:
$user: User object to use for storage
$assessment: An assessment hashref - just retrieved from the database.

=cut
sub process_user_assessment {
	my($self, $user, $assessment, $assessment_type) = @_;
	my @field_kys = keys %$assessment;
	my %height;

	if(!$assessment_type) {$assessment_type = $$assessment{assessment_type};}


	foreach my $field ( @field_kys ) {
		my $obj_name = $field;
		$obj_name = $ORACLE_CVRT{uc($field)} if  lc($self->{'config'}->db_driver) eq 'oracle' ;
		$obj_name = $POSTGRES_CVRT{lc($field)} if  lc($self->{'config'}->db_driver) eq 'postgres' ;

		my $user_obj = $Fields{$assessment_type}{$obj_name};
		$user_obj = $obj_name if(!$user_obj);
		$user_obj = $Fields{$assessment_type}{$field} if !($user_obj);
       
		print { $self->{'debug_handle'} } "Database:Process Users_assessment - $field - $obj_name, $user_obj," . $$assessment{$field} . ", $assessment_type\n"  if  $self->{'debug'};

		if( $obj_name eq 'Feet' && $$assessment{$field} ) { $height{height} += ($$assessment{$field} * 12) }
		elsif( $obj_name eq 'Inches' )	{ $height{height} += $$assessment{$field} }
		elsif( lc($user_obj) eq 'height' )	{ $height{height} = $$assessment{$field} }
		elsif( lc($user_obj) eq 'weight' )	{ $height{weight} = $$assessment{$field} }
		elsif( lc($user_obj) eq 'birth_year' )	{ $height{birth_year} = $$assessment{$field} }
		elsif( lc($user_obj) eq 'birth_month' )	{ $height{birth_month} = $$assessment{$field} }
		elsif( lc($user_obj) eq 'birth_date' )	{ $height{birth_date} = $$assessment{$field} }
		elsif( lc($user_obj) eq 'units' )	{ $height{units} = $$assessment{$field}; $user->$user_obj ( $$assessment{$field} ); }
		elsif( lc($user_obj) ne 'null' )    { $height{$user_obj} = $$assessment{$field}; $user->$user_obj ( $$assessment{$field} ) }
	}
      
	  
 if ($height{height}) {
	$user->set_birthday( $height{birth_year}, $height{birth_month}, $height{birth_date} ) if ( $height{birth_year} && $height{birth_month} && $height{birth_date} );
	$user->_init( \%height );
	$user->set_body_mass_index;
	$user->birth_date( $height{birth_date} );
	$user->birth_month( $height{birth_month} );
	$user->birth_year( $height{birth_year} );
	
	}
	if ($height{birth_year}) {
		$user->_init( \%height );
		$user->set_birthday( $height{birth_year}, $height{birth_month}, $height{birth_date} ) if ( $height{birth_year} && $height{birth_month} && $height{birth_date} );
		$user->birth_date( $height{birth_date} );
		$user->birth_month( $height{birth_month} );
		$user->birth_year( $height{birth_year} );
		
	}
	else	{  
		$user->set_birthday( $user->birth_year, $user->birth_month, $user->birth_date );
		
	}
}

=item process_select

Takes an array of selected records and uses it to set all of
the appropriate fields for a User object

In:
$assessment: An assessment hashref - just retrieved from the database.
$assessment_type: Entry from the database config files that holds the hash with table names, column value and corresponding User object name.

=cut
sub process_select {
	my($self, $assessment, $assessment_type) = @_;
	my @field_kys = keys %$assessment;
	my %height;

	my %results;

	if(!$assessment_type) {$assessment_type = $$assessment{assessment_type};}


	foreach my $field ( @field_kys ) {
		my $obj_name = $field;
		$obj_name = $ORACLE_CVRT{uc($field)} if  lc($self->{'config'}->db_driver) eq 'oracle' ;
		$obj_name = $POSTGRES_CVRT{lc($field)} if  lc($self->{'config'}->db_driver) eq 'postgres' ;

		my $user_obj = $Fields{$assessment_type}{$obj_name};
		$user_obj = $obj_name if(!$user_obj);
		$user_obj = $Fields{$assessment_type}{$field} if !($user_obj);

		print { $self->{'debug_handle'} } "Database:Process Users_assessment - $field - $obj_name, $user_obj," . $$assessment{$field} . ", $assessment_type\n"  if  $self->{'debug'};

		$results{$user_obj} = $$assessment{$field};

	}

	return \%results;

}

sub save_users_assessment
        {
        my $self = shift;
        my $user = shift;
        my $assessment = shift;

        return unless ref $user eq 'HealthStatus::User';

	$self->time_date( $user );

        my @field_kys = keys %{$Fields{$assessment}};

        my %save_data = ();

        return if lc($self->{'config'}->db_driver) eq 'debug';

        $user->encrypt_in_place( $self->{'config'} );
		
#     print STDERR "tbale dumper====".Dumper %Tables;
	# if  (!($self->{'config'}->db_oldnumbers)){ print STDERR "assessments from db.pm=====$assessment";
		# $user->db_record($self->{sequence}->Next($Tables{$assessment}));
		# }
	foreach my $field ( @field_kys )
		{
        	print { $self->{'debug_handle'} } "Database:Save Users_assessment - @field_kys, $field, $assessment\n"  if  $self->{'debug'};

        	my $user_obj = $Fields{$assessment}{$field};
			
		if( $user_obj ne 'null' && $user->get($user_obj) )    { $save_data{$field} = $user->$user_obj; }
          
		} 
	
        $self->insert( $Tables{$assessment}, \%save_data );

        $user->decrypt_in_place( $self->{'config'} );

        { 1 }
        }

sub update_users_assessment
        {
        my $self = shift;
        my $user = shift;
        my $assessment = shift;
        my $stipulations = shift;

        print { $self->{'debug_handle'} } "Database:update_users_assessment -" . $assessment . " - " . $stipulations . "\n";

        return unless ref $user eq 'HealthStatus::User';

	$self->time_date( $user );

        my %save_data = ();

        return if lc($self->{'config'}->db_driver) eq 'debug';

        $user->encrypt_in_place( $self->{'config'} );

	foreach my $field ( keys %{$Fields{$assessment}} )
		{
        	print { $self->{'debug_handle'} } "Database:Update Users_assessment - $field, $assessment\n"  if  $self->{'debug'};

        	my $user_obj = $Fields{$assessment}{$field};

		if( $user_obj ne 'null' && $user->get($user_obj) )    {
			$save_data{$field} = $user->$user_obj;
			print { $self->{'debug_handle'} } "Database:Update Users_assessment - $field - $user_obj, SAVED\n"  if  $self->{'debug'};
			}
		else	{
			print { $self->{'debug_handle'} } "Database:Update Users_assessment - $field - $user_obj, SKIPPED\n"  if  $self->{'debug'};
			}

		}

        $self->update( $Tables{$assessment}, \%save_data, $stipulations );

        $user->db_record ($self->{'statement'}->{'mysql_insertid'}) if lc($self->{'config'}->db_driver) eq 'mysql';

        $user->decrypt_in_place( $self->{'config'} );

        { 1 }
        }


=item update_hs

updates a record in a HealthStatus database table

In:
$user: User object to use for storage
$assessment: Entry from the database config files that holds the hash with table names, column value and corresponding User object name.
$keyfield: The user element to be used as the key in the update
$stipulation: Additional stipulations that should be used in the update, should start with WHERE

=cut
sub update_hs
        {
        my $self = shift;
        my $user = shift;
        my $assessment = shift;
        my $keyfield = shift;
        my $stipulation = shift;

        print { $self->{'debug_handle'} } "Database:update_hs -" . $assessment . " - " . $keyfield. " - " . $stipulation . "\n"  if  $self->{'debug'};

        return unless ref $user eq 'HealthStatus::User';

	$self->time_date( $user );

        my %save_data = ();

        return if lc($self->{'config'}->db_driver) eq 'debug';

        my $dbkey = $Fields{$assessment}{$keyfield};

	my $stipulations = do	{if(!$stipulation)	{"WHERE $dbkey = ";}
        			 else			{$stipulation . " AND $dbkey = ";}
        			 };

        $stipulations .= $self->{'db'}->quote( $user->$keyfield );

        print { $self->{'debug_handle'} } "Database:update_hs ready to process-" . $assessment . " - " . $dbkey. " - " . $stipulations . "\n"  if  $self->{'debug'};

        $user->encrypt_in_place( $self->{'config'} );

	foreach my $field ( keys %{$Fields{$assessment}} )
		{
        	print { $self->{'debug_handle'} } "Database:update_hs - $field, $assessment\n"  if  $self->{'debug'};

        	my $user_obj = $Fields{$assessment}{$field};

		if( $user_obj ne 'null' && $user->get($user_obj) )    {
			$save_data{$field} = $user->$user_obj;
			print { $self->{'debug_handle'} } "Database:update_hs - $field - $user_obj, SAVED\n"  if  $self->{'debug'};
			}
		else	{
			print { $self->{'debug_handle'} } "Database:update_hs - $field - $user_obj, SKIPPED\n"  if  $self->{'debug'};
			}

		}

        $self->update( $Tables{$assessment}, \%save_data, $stipulations );

        $user->decrypt_in_place( $self->{'config'} );

        { 1 }
        }

=item delete_hs

deletes a record in a HealthStatus database table

In:
$user: User object to use for storage
$assessment: Entry from the database config files that holds the hash with table names, column value and corresponding User object name.
$keyfield: The user element to be used as the key in the delete, no other stipulations are allowed to prevent SQL Injection

all * characters in the $user->keyfield value are removed

=cut
sub delete_hs
        {
        my $self = shift;
        my $user = shift;
        my $assessment = shift;
        my $keyfield = shift;

        print { $self->{'debug_handle'} } "Database:delete_hs -" . $assessment . " - " . $keyfield. "\n"  if  $self->{'debug'};

        return unless ref $user eq 'HealthStatus::User';

	$self->time_date( $user );

        my %save_data = ();

        return if lc($self->{'config'}->db_driver) eq 'debug';

        my $dbkey = $Fields{$assessment}{$keyfield};

	my $stipulations = "WHERE $dbkey = ";

        $stipulations .= $self->{'db'}->quote( $user->$keyfield );

        $stipulations =~ s/\Q*\E//g;

        print { $self->{'debug_handle'} } "Database:delete_hs ready to process-" . $assessment . " - " . $dbkey. " - " . $stipulations . "\n"  if  $self->{'debug'};

        $self->delete( $Tables{$assessment}, $stipulations );

        $user->decrypt_in_place( $self->{'config'} );

        { 1 }
        }

=item select_all_hs

selects all the records in a HealthStatus database table

In:
$user: User object to use for storage
$assessment: Entry from the database config files that holds the hash with table names, column value and corresponding User object name.

=cut
sub select_all_hs
        {
        my $self = shift;
        my $user = shift;
        my $assessment = shift;
#        my $keyfield = shift;
#        my $stipulation = shift;

        print { $self->{'debug_handle'} } "Database:select_all_hs -" . $assessment .   "\n"  if  $self->{'debug'};

        return unless ref $user eq 'HealthStatus::User';

	$self->time_date( $user );

        my @results;

        return if lc($self->{'config'}->db_driver) eq 'debug';

#        my $dbkey = $Fields{$assessment}{$keyfield};

#	my $stipulations = do	{if(!$stipulation)	{"WHERE $dbkey = ";}
#        			 else			{$stipulation . " AND $dbkey = ";}
#        			 };

#        $stipulations .= $self->{'db'}->quote( $user->$keyfield );

#        my $dbkey = $Fields{$assessment}{$keyfield};


        print { $self->{'debug_handle'} } "Database:select_all_hs ready to process-" . $assessment .   "\n"  if  $self->{'debug'};

	my $rec_count = $self->count (  $Tables{$assessment} );

	print { $self->{'debug_handle'} } "Database:select_all_hs - records found = $rec_count\n"  if  $self->{'debug'};

	if ($rec_count > 0)
		{
		my @query_results  =  $self->select_all( $Tables{$assessment}, '', 1 );
		foreach my $working (@query_results){
			my $temp = $self->process_select($working, $assessment);
        		$self->__add_to_array( $temp, \@results );
			}

		}

        $user->decrypt_in_place( $self->{'config'} );

        return @results
        }
		
sub get_group {
	my ($self, $stipulation) = @_;
	my %hash;

	my $res1 = $self->select_one_row
		('*', $Tables{GRP}, $stipulation, 1);
	if(!defined $res1) {return FALSE;}

	my $tmp = $Fields{GRP};
	foreach(keys %$tmp) {$hash{$$tmp{$_}} = $$res1{lc($_)};}
   
	return \%hash;
	
	
}

sub get_subgroup {
	my ($self, $stipulation) = @_;	
    
	my  $data = $self->select_one_value( 'subgroupNames', $Tables{GRP}, $stipulation );
	print STDERR "\nhello databaggggggg".  Dumper ($data) ;
	if(!defined $data) { return undef; }
    	  
	return $data;	
}

sub time_date
	{
        my $self = shift;
        my $user = shift;

        return unless ref $user eq 'HealthStatus::User';

	require Date::Calc;

	my ($year, $mon, $mday, $mhour, $mmin, $msec) = Date::Calc::Today_and_Now();

#	$self->debug_on( \*STDERR );

	my @month = qw{ x jan feb mar apr may jun jul aug sep oct nov dec };

# Oracle likes a particular date format.
	if ( lc($self->{'config'}->db_driver) eq 'oracle' )
		{
		$user->db_sortdate ( sprintf("%02d-%s-%04d %02d:%02d:%02d", $mday, $month[$mon], $year, $mhour, $mmin, $msec) );
		$user->db_timestamp ( sprintf("%02d-%s-%04d %02d:%02d:%02d", $mday, $month[$mon], $year, $mhour, $mmin, $msec) );
		my $APrev = "ALTER SESSION SET NLS_DATE_FORMAT = 'DD-MON-YYYY HH24:MI:SS'";
		$self->execute_sql($APrev);
		}
	elsif ( lc($self->{'config'}->db_driver) eq 'mssql' )
		{
		$user->db_sortdate ( sprintf("%04d-%02d-%02d %02d:%02d:%02d.000", $year, $mon, $mday, $mhour, $mmin, $msec) );
		$user->db_timestamp ( '' );
		}
	else
		{
		$user->db_sortdate ( sprintf("%04d-%02d-%02d %02d:%02d:%02d", $year, $mon, $mday, $mhour, $mmin, $msec) );
		$user->db_timestamp ( sprintf("%04d-%02d-%02d %02d:%02d:%02d", $year, $mon, $mday, $mhour, $mmin, $msec) );
		}


# Oracle/postGres doesn't create sequential numbers and give them right back (easily) so we create a unique key
	my $rec = $user->db_number;
	$rec .= sprintf("%04d-%02d-%02d_%02d%02d%02d", $year, $mon, $mday, $mhour, $mmin, $msec);

	$user->db_record ( $rec ) if (lc($self->{'config'}->db_driver) eq 'oracle'  || lc($self->{'config'}->db_driver) eq 'postgres' || $self->{'config'}->db_oldnumbers);

	return;

	}

sub next_number
	{
        my $self = shift;
        my $user = shift;

        return unless (ref $user eq 'HealthStatus::User');
        return if ($user->db_number > 0);
        print { $self->{'debug_handle'} } "Database:Next number - " . $user->db_number . "\n"  if  $self->{'debug'};

      	$user->db_number ( $self->{'sequence'}->Next($Tables{REG}) );
	}

sub user_to_db
	{
        my $self = shift;
        my $user_list_ref = shift;
        my $db_list_ref = shift;
        my $assessment = shift;

        my %map_out;

	my @user_list = @$user_list_ref;
	my @db_list = @$db_list_ref;

	if(@user_list){
		foreach my $user_key(@user_list){
			foreach my $db_key (keys %{$Fields{$assessment}}){
				$map_out{'user'}{$user_key} = $db_key if ($user_key  eq $Fields{$assessment}{$db_key});
				}
			}
		%{$map_out{'db'}} = reverse %{$map_out{'user'}};
		}
	else	{
		foreach my $db_key (@db_list){
			 if ($Fields{$assessment}{$db_key}){
			 	$map_out{'db'}{$db_key} = $Fields{$assessment}{$db_key};
			 	}
			}
		%{$map_out{'user'}} = reverse %{$map_out{'db'}};
		}

	return (\%map_out);

	}
sub assessment_user_to_db{
        my $self = shift;
        my $assessment = shift;

        my %map_out;

	foreach my $db_key (keys %{$Fields{uc $assessment}}){
		$map_out{'user'}{$Fields{uc $assessment}{$db_key}} = $db_key;
		}
	%{$map_out{'db'}} = reverse %{$map_out{'user'}};

	return (\%map_out);

	}
sub table_names
	{
        my $self = shift;
        my $assessments = shift;

        my %table_names;

        foreach (@$assessments){
        	$table_names{$_} = $Tables{$_};
        	}
        return (\%table_names);

	}

sub all_table_names
	{
        my $self = shift;

        my %table_names;

        foreach (sort keys %Tables){
        	$table_names{$_} = $Tables{$_};
        	}
        return (\%table_names);

	}

sub count_of_hs_users
	{
        my $self = shift;
        my $stipulations = shift;

        my $total_users = $self->count($Tables{REG},$stipulations);

        return $total_users;

	}

sub count_of_hs_assessments
	{
        my $self = shift;
        my $table = shift;
        my $stipulations = shift;

        my $total_assessments = $self->count($Tables{$table},$stipulations);

        return $total_assessments;

	}

sub hs_sql
	{
        my $self = shift;
        my $user_list_ref = shift;
        my $db_list_ref = shift;
        my $assessment = shift;

        my %map_out;

	return (\%map_out);

	}
sub get_default_config_variables {
	my ($self, $stipulation) = @_;
	my %hash ;
	my @query_results  =  $self->select( ['*'], $Tables{CONF}, $stipulation, 1 );

	foreach my $c (@query_results) {
		#$self->{'config'}->{'config_data'}->{$$c{conf_name}} = $$c{conf_value};
		$hash{$$c{conf_name}} = $$c{conf_value};
	}

	return \%hash;
}

sub save_import_data
        {
        my $self = shift;
        my $user = shift;
        my $importTable = "IMP";
        my $dbId = shift;
        my $profileData = shift;
        my $profileName = shift;
        my $profileCols = shift;

        my %values = ();
        return unless ref $user eq 'HealthStatus::User';

        $self->time_date( $user );

        my @field_kys = keys %{$Fields{IMP}};

        my %save_data = ();

        return if lc($self->{'config'}->db_driver) eq 'debug';

        $user->encrypt_in_place( $self->{'config'} );

        if  (!($self->{'config'}->db_oldnumbers)){
                $user->db_record($self->{sequence}->Next($importTable));
                }
        foreach my $field ( @field_kys )
                {
                print { $self->{'debug_handle'} } "Database:Save Import_Data- @field_kys, $field, $importTable\n"  if  $self->{'debug'};
                # print STDERR "Database:Save Import_Data- @field_kys, $field, $importTable\n";
                if ($field eq 'hs_uid')
                {
                        $save_data{$field} = $dbId;
                }
                #elsif ($field eq 'unum')
                #{
                        #my $query_results  =  $self->select_one_value ( 'max(unum)', $Tables{IMP} );
                # print STDERR "Select one value resuly: $query_results\n";
                        #$save_data{$field} = $query_results+1;
                #}
                elsif ($field eq 'profile')
                {
                        $save_data{$field} = $profileName;
                }
                elsif ($field eq 'profile_data')
                {
                        $save_data{$field} = $profileData;
                }
                elsif ($field eq 'adate')
                {
                        $self->time_date( $user );
                        $save_data{$field} = $user->db_timestamp;
                }
                elsif ($field eq 'profile_cols')
                {
                        $save_data{$field} = $profileCols;
                }
                }
        $self->insert( $Tables{IMP}, \%save_data );

        $user->decrypt_in_place( $self->{'config'} );

        { 1 }

}


sub save_import_count()
{

        my ($self, $user, $table, $vars) = @_;
        my @field_kys = keys %{$Fields{IMP_COUNT}};

        my %save_data = ();
        return if lc($self->{'config'}->db_driver) eq 'debug';
       #Check if the file has been imported before against same profile
	   
        my $stipulation = " WHERE filename='$vars->{'filename'}' AND hs_uid='$vars->{'db_id'}' AND profile='$vars->{'profile'}'";
        my @result 	= $self->select(['unum'], $Tables{$table}, $stipulation, 1);
        my $unum	= $result[0]->{unum};
        foreach my $field ( @field_kys )
        {
                print { $self->{'debug_handle'} } "Database:Save Import_Count- @field_kys, $field\n"  if  $self->{'debug'};
                my $user_obj = $Fields{$table}{$field};               
                if( $user_obj ne 'null' )    { $save_data{$field} = $vars->{$user_obj} }
                if ($field eq 'adate')      {  $save_data{$field} = $user->db_timestamp; }
        }
         if ($unum == '')
        {
        	$self->insert( $Tables{$table}, \%save_data );
        }
        else
        {
                $save_data{unum} = $unum;
                $self->update( $Tables{$table}, \%save_data, $stipulation );
        }
}

sub export_to_file()
{   
       my ($self,  $table, $file, $flag) = @_;

        my  @query_results  =  $self->select_all( $Tables{$table}, '', 1);

        my $backup_txt;
        foreach(@query_results) 
        {
                $backup_txt .= "INSERT INTO $Tables{$table}(" . join(",", keys %$_) . ") VALUES (" if $flag;

                my $first = 1;

                foreach(values %$_) {
                        $backup_txt .= "," if !$first;
                        $first = 0;
                        $backup_txt .= $self->{db}->quote($_)
                }
                $backup_txt .= ");" if $flag;
                $backup_txt .= "\n";

                $backup_txt .= ");\n" if $flag;
         }
        open ( FILE, ">$file" ) or die "$!";
        print FILE $backup_txt;
        close FILE;
}

	
sub export()
{
         my ($self,$user,$ref_setup_tables,$ref_field_info, $table, $file) = @_;		
	     my $desired_field;	
         $desired_field= $$ref_setup_tables{$table}{fields};           
		 my $temp_field;
		 my @temp_field_type;
		 my $field_types;
         my @array_field =split(/\s+/, $desired_field);		 
		
		 foreach my $fields (@array_field) {		 
		   $temp_field = $$ref_field_info{$fields}{mssql};
		   push  @temp_field_type,$temp_field;		  
		 }
		   foreach my $field_type(@temp_field_type){
		     $field_types .= '"' ;
             $field_types .= $field_type;
			 $field_types .= '",' ; 
		  }	  
             $desired_field =~ s/\s+/\,/g;
		        
        		 
		my $stipulations = "where hs_uid='$user->{'db_id'}' order by adate desc limit 1";		
		my @query_results  =  $self->select( $desired_field, $Tables{$table}, $stipulations, 0);
       		 
        my $desired_field_tofile;	
        foreach (@query_results) {                             
				foreach(@$_) {			 	
                        $desired_field_tofile .= '"' ;                      
                        $desired_field_tofile .= $self->{db}->quote($_);						
						$desired_field_tofile .= '",' ; 
                }                
                $desired_field_tofile =~ s/\'//g;            
         }
		 $desired_field = "Assessment,". $desired_field;
		 $field_types   = $table .",". $field_types;
         $desired_field_tofile = "," . $desired_field_tofile;
		 open ( FILE, ">$file" ) or die "$!";
	    print FILE $desired_field ."\n";
		print FILE $field_types ."\n";
        print FILE $desired_field_tofile;
        close FILE;
}
#
# Input parameters:
# self:  DB Object
# table: The acronym of table like REG, PASS
# file:  Output file
# flag:  Value 1: The file contains insert command
#        Value 0: The file contains csv data 
sub import_from_file()
{  
        my ($self,  $table, $file, $flag) = @_;
        open ( FILE, "$file") or die "$!";
        while(<FILE>) 
        {
                chomp;
                next if ($_ =~ /^\s*$/);
                $_ =~ s/\'//g; 

				
                if ($flag)
                {  
                        $self->{'sql'} = $_;
                        print { $self->{'debug_handle'} } "Database:import_from_file - sql: $self->{'sql'}\n"  if  $self->{'debug'};
                        print STDERR "\nSQL is: $self->{'sql'}\n\n";
                        $self->__sql_execute( );
                }
                else
                {  
                        my @field_kys = keys %{$Fields{$table}};
                        my %save_data = ();
                        my $i=0;
                        my @data = split(',', $_);
                        foreach my $field ( @field_kys )
                        {
                                my $user_obj = $Fields{$table}{$field};
                                if( $user_obj) { $save_data{$field} = $data[$i]; $i++;}
                        }
                        $self->insert( $Tables{$table}, \%save_data );
                       
                }
        }

}                    

=item get_pending_import

=cut
sub get_pending_import 
{
        my $self 		= shift;
        my $user 		= shift;
        my $importTable 	= "IMP";

	return unless ref $user eq 'HealthStatus::User';

        my $stipulations 	= "WHERE hs_uid='$user->{'db_id'}' ";
        my @query_results  	=  $self->select_all( $Tables{$importTable}, $stipulations, 1);
        return (@query_results);

}
=back

=item create_text_file

create a text file of the database table into a specified path.

In:
$table: table name
$stipulation: The WHERE clause
$file_path: file path to be create.

=cut
sub create_text_file {
	my ($self, $table, $file_path, $stipulation) = @_;
	if( lc($self->{'config'}->db_driver) eq 'mysql') {
		$self->execute_sql( "select * from $table $stipulation into outfile '$file_path'");
	} elsif  (lc($self->{'config'}->db_driver) eq 'postgres'){
		$self->execute_sql( "COPY (SELECT * FROM $table $stipulation) TO '$file_path'");
	}

	return 1;
}


sub getDatabaseBackup{
        my $self 		= shift;
        my $backup_file_name = shift;		
		my $table_name;			        		
			 foreach my $key_value(keys %Tables){				  				    
						$table_name =  $key_value;
						$self->backup_database($table_name , $backup_file_name); 
				  
			}			
}
sub backup_database()
{   
         my ($self,  $table, $file) = @_;		
		 my  @query_results;		 
		 @query_results  =  $self->select_all( $Tables{$table}, '', 1);
			
        my $backup_txt;
		my $q;
		my $key;
        foreach(@query_results) 
        {     
		         $backup_txt .= "INSERT INTO $Tables{$table}(";
        	    foreach $key(keys %$_){				 
				  if( lc($self->{'config'}->db_driver) eq 'mssql') {
                   next if($key eq 'ts'); 
                  }				   
                	$q .= $key;					
					$backup_txt .= $key . ",";
					
				 }
				chop $backup_txt;
				$backup_txt .= ") VALUES (";                
                my $first = 1;

                foreach $key(keys %$_) {
				      if( lc($self->{'config'}->db_driver) eq 'mssql') {
						next if($key eq 'ts'); 
						}
                        $backup_txt .= "," if !$first;
                        $first = 0;
                        $backup_txt .= $self->{db}->quote($$_{$key})
                } 
				
                $backup_txt .= ");";
                $backup_txt .= "\n";
               
         }
        open ( FILE, ">>$file" ) or die "$!";
        print FILE $backup_txt;
        close FILE;
}

sub getDatabaseRestore{
     my $self = shift;
     my $restore_file= shift;
		  
            foreach my $key_value(keys %Tables){		   
				  $self->execute_sql("truncate table $Tables{$key_value}" ); 					 
			  }
		$self->restore_database_from_file($restore_file);			
	   
}

sub restore_database_from_file()
{  
        my ($self,  $file) = @_;
        open ( FILE, "$file") or die "$!";
        while(<FILE>) 
        {
                chomp;
                next if ($_ =~ /^\s*$/);
                $_ =~ s/\ / /g;               
                
                        $self->{'sql'} = $_;
                        print { $self->{'debug_handle'} } "Database:restore_database_from_file - sql: $self->{'sql'}\n"  if  $self->{'debug'};
                        $self->__sql_execute( );
                
	}
}

sub get_user_elements
{
    my $self 		= shift;
    my $assessment  = shift;
	
	my @rev_data;
	my @field_keys = keys %{$Fields{$assessment}};
	foreach my $field ( @field_keys )
        {
                push  @rev_data,$Fields{$assessment}{$field};
               
        }
	return 	@rev_data;
}

sub check_temp_data
{
	my $self 		= shift;   
	my $table		= shift;
	my $field		= shift;
	my $xnum  		= shift;	

	my (%inches_hs_uids,@existing_column_db);
	
	#Get all fields having respective database table
	my @fields_from_db = $self->execute_sql_return("SHOW COLUMNS FROM $table"); 	

	foreach my $row (@fields_from_db) {
		next if($row->[0] eq 'hs_uid' || $row->[0] eq 'unum' || $row->[0] eq 'xnum' || $row->[0] eq 'adate');
		push(@existing_column_db, $row->[0]); 
	}

	#Get all fields having NULL values
	my @hsuid_from_gha = $self->execute_sql_return("SELECT * FROM $table WHERE xnum=$xnum AND $field IS NULL",1);
	foreach my $hs_uid(@hsuid_from_gha){
		my @column_ref ;
		foreach(@existing_column_db){
			if(!$hs_uid->{$_}){
				push(@column_ref,$_);
			}
		}
		$inches_hs_uids{$hs_uid->{hs_uid}}= \@column_ref; 
	}	

	#Update all fields having NULL values from temp data
	if(%inches_hs_uids){
		foreach my $hsuid( keys %inches_hs_uids) {		
			
			my $update_qry;	
			my @hsuid_from_ghatemp = $self->execute_sql_return("SELECT * FROM hs_tmp_ghadata WHERE hs_uid = '$hsuid'",1);
			foreach my $hs_uid(@hsuid_from_ghatemp){
				foreach(@{$inches_hs_uids{$hsuid}}){			
					if($hs_uid->{$_}){
						$update_qry .= "$_='$hs_uid->{$_}',";
					}
				}
			}			
			if($update_qry){
				 chop($update_qry);
				 my $update_str = "UPDATE $table SET $update_qry WHERE hs_uid='$hsuid' AND xnum=$xnum";
				 my @update_row = $self->execute_sql_return("UPDATE $table SET $update_qry WHERE hs_uid='$hsuid' AND xnum=$xnum",1);	
				 #print STDERR "Updated record for hs_uid : $update_str\n";
				 return 1;	
			}
		}

	}else{
		return 0;
	}	
}

=back


sub DESTROY
        {
        $self->disconnect;
        }

=head1 BUGS

=head1 TO-DO
Add alternative to site_list if not using emails

=head1 AUTHOR

Greg White <gwhite@healthstatus.com>

=head1 COPYRIGHT

Copyright 2001-2004, HealthStatus.com

=cut

1;
