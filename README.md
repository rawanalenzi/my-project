# HoneyGate: Deception-Based Security for Banking Systems

##  Project Description
**HoneyGate** is a proactive cybersecurity system designed to protect online banking environments. Developed using **Flask**, the system integrates a realistic banking simulation with a sophisticated **Honeypot layer**. It aims to enhance security by misleading attackers into a controlled environment while allowing legitimate users to perform banking tasks securely.

##  System Architecture
The system is built on a multi-layered architecture:
* **Client Layer:** Professional banking front-end and decoy admin interfaces.
* **Security Layer:** A Flask-based engine that performs real-time anomaly detection.
* **Real Web App:** Secure services including transfers, card management, and settings.
* **Honeypot Layer:** A trap environment that intercepts traffic and logs malicious commands.
* **SOC Layer:** A centralized monitoring hub for behavioral analytics and high-risk IP tracking.

## 📂 Project Structure
```text
.
├── app.py                      # Main application logic
├── attacks_log.txt             # Records of intercepted attacks
├── failed_login_attempts.log   # Logs of unsuccessful logins
├── soc_state.json              # Dashboard state and statistics
├── static/                     # CSS, images, and UI assets
└── templates/                  # HTML pages (Real & Fake)
