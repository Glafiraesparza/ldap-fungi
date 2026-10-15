#!/bin/bash -e

log-helper level eq trace && set -x

ulimit -n "$LDAP_NOFILE"

FQDN="$(/bin/hostname --fqdn)"
HOST_PARAM="ldap://$FQDN:$LDAP_PORT ldaps://$FQDN:$LDAPS_PORT"

mkdir -p /var/log
touch /var/log/slapd.log /var/log/ldap-fail2ban.log

/usr/sbin/slapd \
    -h "$HOST_PARAM ldapi:///" \
    -u openldap \
    -g openldap \
    -d "$LDAP_LOG_LEVEL" 2>&1 \
    | tee -a /var/log/slapd.log \
    | tee /dev/stderr \
    | python3 /usr/local/bin/parse-ldap-logs.py \
        >> /var/log/ldap-fail2ban.log
