🚀 NetPulse

NetPulse is a lightweight Windows network diagnostics tool built to monitor latency, packet loss, DNS response time, and route behavior in real time.

It’s designed as a learning-focused utility using only native Windows tools and Python — no bloat, no background services.

🔧 What It Does

Monitors ping latency (min / avg / max)

Tracks jitter and packet loss

Measures DNS resolution time

Detects route changes (optional)

Supports multiple targets

Optional CSV logging

🎯 Use Cases

Network troubleshooting

Latency and stability monitoring

Gaming or VoIP diagnostics

Learning how Windows networking behaves

Lightweight alternative to heavy monitoring tools

▶ Usage
python netpulse.py


Example:

python netpulse.py --targets 1.1.1.1,8.8.8.8 --route-check

📌 Notes

Windows 10 / 11

Python 3.9+

No external dependencies

No telemetry or background services


ChatGPT can make mistakes.
