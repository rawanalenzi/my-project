from flask import Flask, render_template, request, redirect, url_for, session, make_response
import datetime
import os

app = Flask(__name__)

app.secret_key = 'honeygate_secret_key_2026'
app.permanent_session_lifetime = datetime.timedelta(minutes=10)

def log_attack(path):
    log_file = "attacks_log.txt"
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ip_address = request.remote_addr
    user_agent = request.user_agent.string
    session_id = request.cookies.get('session', 'No Session Found')
    
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] ⚠️ ALERT | IP: {ip_address} | Target: {path} | Stolen_SID: {session_id} | Device: {user_agent}\n")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    
    if email == "admin@bank.com" and password == "123456":
        session.permanent = True
        session['user'] = email
        return redirect(url_for('dashboard'))
    
    return "<h1>خطأ في بيانات الدخول</h1><a href='/'>العودة للرئيسية</a>"

@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        session_id = request.cookies.get('session')
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        return render_template('dashboard.html', user=session['user'], sid=session_id, datetime=now)
    return redirect(url_for('home'))

@app.route('/admin')
@app.route('/config')
@app.route('/backup')
def external_honeypot():
    log_attack(request.path)
    return render_honeypot_ui()

@app.route('/transfer')
@app.route('/cards')
@app.route('/loans')
@app.route('/settings')
def internal_honeypot():
    log_attack(request.path)
    return render_honeypot_ui()

def render_honeypot_ui():
    return """
    <body style="background:#0d0d0d; color:#00ff41; font-family: 'Courier New', monospace; padding:50px; direction:ltr; text-align:left;">
        <h2 style="color: #ff3e3e;">[!] CRITICAL SYSTEM ACCESS DETECTED</h2>
        <p>--------------------------------------------------</p>
        <p>Target System: <b>Bank_Core_V2</b></p>
        <p>Access Level: <span style="background:#ff3e3e; color:white;">ROOT_PRIVILEGED</span></p>
        <p>Status: Initializing Decrypting Protocol...</p>
        <div style="border: 1px solid #00ff41; padding: 15px; margin: 20px 0;">
            > Bypass Firewall... [SUCCESS]<br>
            > Extracting User_Table... [RUNNING]<br>
            > Mapping Network Topology... [DONE]
        </div>
        <p style="color: #555;">Warning: All activities are being recorded by System Watchdog.</p>
    </body>
    """

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)