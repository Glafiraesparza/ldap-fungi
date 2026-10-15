#!/bin/bash
set -e

mkdir -p /var/log/fail2ban
mkdir -p /var/run/fail2ban
touch /var/log/slapd.log /var/log/ldap-fail2ban.log

fail2ban-server -f -x &
FAIL2BAN_PID=$!

/container/tool/run &
LDAP_PID=$!

cleanup() {
    kill "$LDAP_PID" "$FAIL2BAN_PID" 2>/dev/null || true
}

trap cleanup TERM INT

# Esperar a que OpenLDAP esté disponible y ajustar la verificación TLS.
for i in $(seq 1 30); do
    if ldapsearch -Y EXTERNAL -H ldapi:/// -b cn=config -s base dn >/dev/null 2>&1; then
        ldapmodify -Y EXTERNAL -H ldapi:/// <<'EOF' || true
dn: cn=config
changetype: modify
replace: olcTLSVerifyClient
olcTLSVerifyClient: never
EOF
        break
    fi
    sleep 2
done

wait "$LDAP_PID"