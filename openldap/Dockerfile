FROM osixia/openldap:1.5.0

USER root

RUN sed -i \
    -e 's|deb.debian.org/debian|archive.debian.org/debian|g' \
    -e 's|security.debian.org/debian-security|archive.debian.org/debian-security|g' \
    -e '/buster-updates/d' \
    -e '/buster-backports/d' \
    /etc/apt/sources.list \
    && apt-get -o Acquire::Check-Valid-Until=false update \
    && apt-get install -y --no-install-recommends \
        fail2ban \
        python3 \
        iptables \
    && rm -rf /var/lib/apt/lists/*

COPY fail2ban/filter-ldaps.conf /etc/fail2ban/filter.d/ldaps.conf
COPY fail2ban/jail-ldaps.local /etc/fail2ban/jail.d/ldaps.local
COPY fail2ban/jail.local /etc/fail2ban/jail.local
COPY fail2ban/parse-ldap-logs.py /usr/local/bin/parse-ldap-logs.py

COPY openldap/process.sh /container/service/slapd/process.sh
COPY openldap/entrypoint.sh /entrypoint-custom.sh

RUN chmod +x \
    /usr/local/bin/parse-ldap-logs.py \
    /container/service/slapd/process.sh \
    /entrypoint-custom.sh

ENTRYPOINT ["/entrypoint-custom.sh"]
