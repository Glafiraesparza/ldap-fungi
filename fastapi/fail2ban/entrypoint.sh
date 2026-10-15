#!/bin/sh
set -e

mkdir -p /var/log/nginx /var/run/fail2ban
touch /var/log/nginx/access.log /var/log/nginx/error.log

uvicorn app.main:app --host 127.0.0.1 --port 8001 &
UVICORN_PID=$!

fail2ban-server -f -x &
FAIL2BAN_PID=$!

nginx -g 'daemon off;' &
NGINX_PID=$!

cleanup() {
    kill "$NGINX_PID" "$FAIL2BAN_PID" "$UVICORN_PID" 2>/dev/null || true
}

trap cleanup TERM INT

wait "$NGINX_PID"