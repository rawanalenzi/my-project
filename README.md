# HoneyGate (SeC Bank)

![Python](https://img.shields.io/badge/Python-blue)
![Flask](https://img.shields.io/badge/Flask-black)
![Security](https://img.shields.io/badge/Security-red)
![Educational](https://img.shields.io/badge/Educational-green)

---

## Overview

HoneyGate is an educational deception-based security lab that simulates an online banking portal (SeC Bank) with integrated honeypots and a Security Operations Center (SOC) dashboard.

It is designed for cybersecurity education, allowing defenders to observe attacker behavior such as login abuse, probing, and command execution in a controlled environment.

> ⚠️ Disclaimer: This project is for educational and authorized lab use only. Do not deploy on real users, production systems, or unauthorized networks.

---

## Table of Contents

- Overview  
- Architecture  
- Security Features  
- Honeypot Design  
- SOC Dashboard & Logging  
- Routes Reference  
- Project Structure  
- Installation  
- Running the Application  
- Demo Credentials  
- Security Concepts  
- Future Improvements  
- Disclaimer  

---

## Architecture

```mermaid
graph TD
A[Client Browser] --> B[Flask App]
B --> C[Login System]
B --> D[Honeypots]
B --> E[SOC Dashboard]
B --> F[Logging Engine]
F --> G[attacks_log.txt]
F --> H[soc_state.json]
Security Features
Session-based authentication (Flask sessions)
Admin-only SOC dashboard
Decoy credentials for attacker detection
IP blocking simulation
Honeypot trap routes
Behavioral verification (reaction timing)
Unified forensic logging system
Fake command execution capture
Honeypot Design
HoneyGate uses deception-based security instead of direct blocking.
External Honeypots
/secure-admin → fake admin panel
/config → fake system console
/log_command → captures fake shell commands
Internal Honeypots
/transfer
/cards
/loans
/settings
These routes simulate sensitive banking operations to detect abuse.
SOC Dashboard & Logging
SOC Routes
/admin → SOC dashboard
/admin/live → live JSON feed
Log Format
Each event is stored as:
{
  "time": "YYYY-MM-DD HH:MM:SS",
  "ip": "client_ip",
  "type": "LOGIN | HONEYPOT | ALERT | COMMAND",
  "path": "/route",
  "action": "description",
  "device": "User-Agent",
  "session": "user"
}
Project Structure
HoneyGate/
├── app.py
├── attacks_log.txt
├── failed_login_attempts.log
├── soc_state.json
├── README.md
├── static/
├── templates/
└── my-project/
Installation
git clone <your-repo-url>
cd my-project

python -m venv venv
source venv/bin/activate  # Mac/Linux

pip install flask
Running the Application
python app.py
URL: http://127.0.0.1:8000
Demo Credentials
Type	Email	Password	Result
Valid	admin@bank.com	123456	Access dashboard
Decoy	admin@bank.com	admin123	Triggers alert
Decoy	backup@bank.com	123456	Blocked
Security Concepts Demonstrated
Honeypots & deception systems
Credential abuse detection
Session authentication
SOC monitoring dashboards
Digital forensics logging
Behavioral analysis
Attack surface simulation
Future Improvements
Add requirements.txt
Implement rate limiting
Use password hashing
Export logs to SIEM format
Docker deployment
Improve SOC analytics dashboard
Disclaimer
This project is strictly for educational purposes only.
Do not use on real systems or without authorization.