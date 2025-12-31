import argparse
import csv
import datetime as dt
import os
import re
import socket
import statistics
import subprocess
import time
from dataclasses import dataclass, field
from typing import List, Optional

PING_TIME_RE = re.compile(r"time[=<]\s*(\d+)\s*ms", re.IGNORECASE)


def is_windows():
    return os.name == "nt"


def clear():
    os.system("cls" if is_windows() else "clear")


def now():
    return dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def run(cmd, timeout=3):
    try:
        p = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=timeout,
        )
        return p.returncode, p.stdout or ""
    except Exception:
        return 1, ""


def parse_ping(out):
    m = PING_TIME_RE.search(out)
    if not m:
        return None
    try:
        return float(m.group(1))
    except ValueError:
        return None


def ping(host, timeout_ms=1000):
    code, out = run(["ping", "-n", "1", "-w", str(timeout_ms), host], timeout=2.5)
    if code != 0:
        return None
    return parse_ping(out)


def dns_time(host):
    try:
        socket.inet_pton(socket.AF_INET, host)
        return 0.0, host
    except OSError:
        pass

    t0 = time.perf_counter()
    try:
        info = socket.getaddrinfo(host, None)
        t1 = time.perf_counter()
        ip = info[0][4][0] if info and info[0] and info[0][4] else None
        return (t1 - t0) * 1000.0, ip
    except Exception:
        return None, None


def trace(host):
    code, out = run(["tracert", "-d", "-h", "20", host], timeout=12)
    if code != 0:
        return None

    hops = []
    for line in out.splitlines():
        line = line.strip()
        if not line:
            continue
        low = line.lower()
        if low.startswith("tracing route") or low.startswith("over a maximum") or low.startswith("trace complete"):
            continue

        parts = line.split()
        if not parts:
            continue
        last = parts[-1]
        if re.fullmatch(r"\d{1,3}(\.\d{1,3}){3}", last):
            hops.append(last)

    return "->".join(hops) if hops else None


def jitter(samples):
    if len(samples) < 2:
        return None
    diffs = [abs(samples[i] - samples[i - 1]) for i in range(1, len(samples))]
    return statistics.mean(diffs) if diffs else None


@dataclass
class Target:
    host: str
    window: int
    sent: int = 0
    received: int = 0
    values: List[float] = field(default_factory=list)
    last: Optional[float] = None
    dns: Optional[float] = None
    ip: Optional[str] = None
    route: Optional[str] = None
    changed: bool = False

    def add(self, val):
        self.sent += 1
        self.last = val
        if val is None:
            return
        self.received += 1
        self.values.append(val)
        if len(self.values) > self.window:
            self.values = self.values[-self.window :]

    def loss(self):
        if self.sent == 0:
            return 0.0
        return (self.sent - self.received) / self.sent * 100.0

    def stats(self):
        if not self.values:
            return None, None, None
        return min(self.values), statistics.mean(self.values), max(self.values)


def fmt(v):
    if v is None:
        return "—"
    if v >= 100:
        return f"{v:.0f}"
    return f"{v:.1f}"


def prompt_targets(default_csv: str) -> str:
    print("NetPulse")
    print("Enter targets separated by commas (IP or hostname).")
    print(f"Press Enter to use default: {default_csv}")
    s = input("Targets: ").strip()
    return s if s else default_csv


def parse_targets(csv_str: str) -> List[str]:
    items = [x.strip() for x in csv_str.split(",") if x.strip()]
    # keep it sane in the terminal
    return items[:20]


def main():
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument("--targets", default="", help="Comma-separated targets (IPs/hostnames)")
    parser.add_argument("--interval", type=float, default=1.0)
    parser.add_argument("--timeout", type=int, default=1000)
    parser.add_argument("--window", type=int, default=20)
    parser.add_argument("--route-check", action="store_true")
    parser.add_argument("--route-every", type=int, default=30)
    parser.add_argument("--log", default="", help="CSV log file path (optional)")
    args = parser.parse_args()

    default_targets = "1.1.1.1,8.8.8.8,github.com"
    targets_csv = args.targets.strip() or prompt_targets(default_targets)
    targets_list = parse_targets(targets_csv)

    targets = {t: Target(t, args.window) for t in targets_list}

    log = None
    writer = None
    if args.log:
        log = open(args.log, "a", newline="", encoding="utf-8")
        writer = csv.writer(log)
        if log.tell() == 0:
            writer.writerow(["timestamp", "target", "resolved_ip", "last_ms", "avg_ms", "min_ms", "max_ms", "jitter_ms", "loss_pct", "dns_ms", "route_changed"])

    cycle = 0

    try:
        while True:
            cycle += 1

            for t in targets.values():
                t.dns, t.ip = dns_time(t.host)
                t.add(ping(t.host, args.timeout))
                t.changed = False  # reset visual flag each loop unless route check sets it

            if args.route_check and cycle % max(1, args.route_every) == 0:
                for t in targets.values():
                    new = trace(t.host)
                    if t.route and new and new != t.route:
                        t.changed = True
                    if new:
                        t.route = new

            clear()
            print("NetPulse")
            print(f"Targets: {', '.join(targets_list)}")
            print("-" * 86)
            print(f"{'Target':<22} {'Last':>6} {'Avg':>6} {'Min':>6} {'Max':>6} {'Jit':>6} {'Loss':>7} {'DNS':>6} {'Route':>6}")
            print("-" * 86)

            for t in targets.values():
                mn, av, mx = t.stats()
                j = jitter(t.values)
                route_flag = "CHG" if t.changed else ("OK" if t.route else "")
                print(
                    f"{t.host:<22} "
                    f"{fmt(t.last):>6} {fmt(av):>6} {fmt(mn):>6} {fmt(mx):>6} "
                    f"{fmt(j):>6} {t.loss():>6.1f}% "
                    f"{fmt(t.dns):>6} {route_flag:>6}"
                )

            print("-" * 86)
            print("Ctrl+C to stop")
            if writer:
                for t in targets.values():
                    mn, av, mx = t.stats()
                    writer.writerow([
                        now(), t.host, t.ip or "",
                        t.last if t.last is not None else "",
                        av if av is not None else "",
                        mn if mn is not None else "",
                        mx if mx is not None else "",
                        jitter(t.values) if jitter(t.values) is not None else "",
                        t.loss(),
                        t.dns if t.dns is not None else "",
                        "1" if t.changed else "0",
                    ])
                log.flush()

            time.sleep(max(0.2, args.interval))

    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        if log:
            log.close()


if __name__ == "__main__":
    main()
