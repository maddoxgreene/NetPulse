🚀 NetPulse

NetPulse is a lightweight Windows network diagnostics tool designed to monitor latency, packet loss, DNS performance, and routing behavior in real time.

It’s built as a learning-focused side project using only native system tools and Python - no bloat, no telemetry, no background services.

✨ Features

Live ping monitoring (latency, min/avg/max)

Jitter calculation

Packet loss tracking

DNS resolution timing

Optional route change detection

Multi-target monitoring

CSV logging support

Lightweight and fast

No third-party dependencies

🧰 Requirements

Windows 10 or 11

Python 3.9+

Command Prompt or PowerShell

To check Python:

python --version

📦 Installation

Download or clone the repository

Save the file as:

netpulse.py


Make sure Python is installed and added to PATH

That’s it — no setup required.

▶️ How to Run

Open Command Prompt in the folder containing netpulse.py and run:

python netpulse.py

Example with options:
python netpulse.py --targets 1.1.1.1,8.8.8.8,google.com --route-check

⚙️ Available Options

Option	Description

--targets	Comma-separated IPs or hostnames

--interval	Delay between checks (seconds)

--timeout	Ping timeout (ms)

--window	Rolling average window size

--route-check	Detect route changes

--route-every	How often to run traceroute

--log	Write results to CSV

📊 Example Output
Target                  Last   Avg   Min   Max  Jit  Loss  DNS  Route
1.1.1.1                 12.3   13.1  11.9  15.4  0.8   0%   2.1   OK
8.8.8.8                 18.4   19.0  17.5  21.2  1.1   0%   2.3   OK

📁 Logging

To log results to a file:

python netpulse.py --log netpulse_log.csv


This records:

Timestamp

Target

Ping stats

Jitter

Packet loss

DNS time

Route status

🎯 Use Cases

Network troubleshooting

Latency analysis

ISP testing

Gaming & VoIP monitoring

Learning how networking behaves in real time

🧠 About This Project

NetPulse is a personal learning project created to explore:

Windows networking behavior

Packet timing and latency

CLI tooling

Real-time diagnostics



ChatGPT can make mistakes. Check important info.
