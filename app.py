from flask import Flask, render_template, request, redirect, url_for, session
import datetime

app = Flask(__name__)
app.secret_key = 'honeygate_pro_2026'

user_status = {}

def log_attack(path, severity, action):
    log_file = "attacks_log.txt"
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ip = request.remote_addr
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] ALERT | {severity} | IP: {ip} | Target: {path} | Action: {action}\n")
    if severity == "CRITICAL":
        print(f"\n[!!!] SECURITY ALERT: Critical Threat from {ip} on {path}\n")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    if email == "admin@bank.com" and password == "123456":
        session['user'] = email
        return redirect(url_for('dashboard'))
    return "<h1>Login Failed</h1><p>Invalid credentials.</p><a href='/'>Back to Home</a>"

@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        session_id = "eyJfc2Vzc2lvbiI6ImR..."
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        return render_template('dashboard.html', user=session['user'], sid=session_id, datetime=now)
    return redirect(url_for('home'))

@app.route('/admin/config_backup')
@app.route('/settings')
@app.route('/config')
@app.route('/transfer')
@app.route('/admin')
def smart_trap():
    ip = request.remote_addr
    user_status[ip] = user_status.get(ip, 0) + 1
    attempts = user_status[ip]

    if attempts == 1:
        log_attack(request.path, "LOW", "Triggered Fake 404")
        return "<h1>404 Not Found</h1><p>The requested URL was not found on this server.</p>", 404

    elif attempts == 2:
        log_attack(request.path, "MEDIUM", "Redirected to Admin Portal")
        return render_template('admin_panel.html')

    else:
        log_attack(request.path, "CRITICAL", "Deployed Interactive Terminal")
        return render_template('fake_root_console.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)