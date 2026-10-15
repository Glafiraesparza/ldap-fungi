
#!/usr/bin/env python3
import re
import sys
from datetime import datetime

connections = {}

for line in sys.stdin:
    conn_match = re.search(r'\bconn=(\d+)', line)
    if not conn_match:
        continue

    conn_id = conn_match.group(1)

    accept = re.search(
        r'ACCEPT from IP=([^:\s]+):\d+ \(IP=[^)]*:636\)',
        line
    )
    if accept:
        connections[conn_id] = accept.group(1)
        continue

    failure = re.search(r'\bRESULT tag=97 err=49\b', line)
    if failure and conn_id in connections:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(
            f"{timestamp} FAILED_LDAPS "
            f"ip={connections[conn_id]} conn={conn_id}",
            flush=True
        )
