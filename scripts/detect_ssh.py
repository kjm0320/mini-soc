import re
import sys
from collections import defaultdict, deque
from datetime import datetime

WINDOW_SECONDS = 60
THRESHOLD = 3

pattern = re.compile(
    r"Failed password for (?:invalid user )?\S+ "
    r"from (?P<ip>\S+) port \d+"
)

failures = defaultdict(deque)
alert_count = 0
failure_count = 0

for line in sys.stdin:
    match = pattern.search(line)
    if not match:
        continue

    try:
        timestamp = line.split()[0]
        event_time = datetime.fromisoformat(
            timestamp.replace("Z", "+00:00")
        )
    except (ValueError, IndexError):
        print("[WARN] Cannot parse timestamp:", line.strip())
        continue

    failure_count += 1
    ip = match.group("ip")
    recent = failures[ip]

    while recent and (
        event_time - recent[0]
    ).total_seconds() > WINDOW_SECONDS:
        recent.popleft()

    previous_count = len(recent)
    recent.append(event_time)

    if previous_count < THRESHOLD <= len(recent):
        alert_count += 1
        print(
            f"[ALERT] Repeated SSH login failures "
            f"ip={ip} count={len(recent)} "
            f"window={WINDOW_SECONDS}s "
            f"time={event_time.isoformat()}"
        )

print(
    f"[SUMMARY] failed_logins={failure_count} "
    f"alerts={alert_count}"
)