FROM python:3.11-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        fail2ban \
        nginx \
        iptables \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY fail2ban/filter-http-flood.conf /etc/fail2ban/filter.d/http-flood.conf
COPY fail2ban/jail.local /etc/fail2ban/jail.local
COPY fail2ban/nginx.conf /etc/nginx/nginx.conf
COPY fail2ban/entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

CMD ["/entrypoint.sh"]