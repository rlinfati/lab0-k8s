#!/usr/bin/env python3

import math
import sys
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

##########
# CONFIG #
##########

TIMEZONE      = ZoneInfo("America/Santiago")
WEEKDAY_TIMES = "10:00,13:30,17:00"
WEEKEND_TIMES = "13:00"

def parse_times(value: str) -> list:
    times = []
    for item in value.split(","):
        item = item.strip()
        if item:
            hour, minute = item.split(":")
            times.append((int(hour), int(minute)))

    return sorted(times)

def next_run(now: datetime) -> datetime:
    weekday_times = parse_times(WEEKDAY_TIMES)
    weekend_times = parse_times(WEEKEND_TIMES)

    for offset in range(8):
        day = now.date() + timedelta(days=offset)
        times = weekend_times if day.weekday() >= 5 else weekday_times

        for hour, minute in times:
            candidate = datetime(day.year, day.month, day.day, hour, minute, tzinfo=TIMEZONE)
            if candidate.timestamp() > now.timestamp():
                return candidate

    raise RuntimeError("No run time configured")

def main():
    now = datetime.now(TIMEZONE)
    target = next_run(now)
    seconds = math.ceil(target.timestamp() - now.timestamp())

    print(f"[NEXT] {target.isoformat()} in {seconds}s", file=sys.stderr)
    print(seconds)

if __name__ == "__main__":
    main()

# eof
