package HealthJibe;
use strict;
use base qw(Net::OAuth::Simple);
sub new {
    my $class  = shift;
    my %tokens = @_;
    return $class->SUPER::new( 
    	tokens => \%tokens, 
    	protocol_version => '1.0',
        urls   => {
             authorization_url => "http://sandbox.healthjibe.net/sso/v1/authorize",
             request_token_url => "http://sandbox.healthjibe.net/request-token.ashx",
             access_token_url  => "http://sandbox.healthjibe.net/access-token.ashx",
        },
    );
}
sub view_restricted_resource {

    my $self = shift;
    my $url  = shift;
    return $self->make_restricted_request( $url, 'GET' );
}
sub update_restricted_resource {

    my $self         = shift;
    my $url          = shift;
    my %extra_params = @_;
    return $self->make_restricted_request($url, 'POST', %extra_params);    
}

1;