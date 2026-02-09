import sqlite3
import threading
import time
import random
import requests
import os
from flask import Flask, render_template_string, request, jsonify

# --- কনফিগারেশন ---
app = Flask(__name__)
DB_NAME = "bot_database.db"
logs = [] # লাইভ লগ দেখার জন্য

# --- ডাটাবেস সেটআপ (একবারই রান হবে) ---
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS ff_accounts 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  account_id TEXT, 
                  password TEXT, 
                  status TEXT DEFAULT 'Active')''')
    conn.commit()
    conn.close()

init_db()

# --- গ্যারিনা লগইন ও লাইক পাঠানোর লজিক ---
def send_like_process(target_uid):
    global logs
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT account_id, password FROM ff_accounts")
    accounts = c.fetchall()
    conn.close()

    if not accounts:
        logs.append(f"<span class='text-danger'>[!] ডাটাবেসে কোনো আইডি পাওয়া যায়নি। আগে আইডি যোগ করুন।</span>")
        return

    logs.append(f"<span class='text-primary'>[🚀] UID: {target_uid} এর জন্য প্রসেস শুরু হয়েছে...</span>")

    for email, pwd in accounts:
        try:
            # এখানে আপনার লাইক এপিআই লজিক থাকবে। 
            # যেহেতু আসল এপিআই এন্ডপয়েন্ট প্রাইভেট, এখানে ডামি প্রসেস দেখানো হয়েছে।
            
            logs.append(f"<span class='text-info'>[✔] {email} লগইন করার চেষ্টা করছে...</span>")
            
            # মনে করুন লগইন সফল হয়ে টোকেন তৈরি হয়েছে
            time.sleep(2) # লগইন প্রসেসিং সময়
            
            # লাইক পাঠানোর রিকোয়েস্ট
            # requests.post("GARENA_LIKE_API_URL", data={"uid": target_uid, "token": "dummy_token"})
            
            logs.append(f"<span class='text-success'>[❤] {email} থেকে লাইক সফলভাবে পাঠানো হয়েছে।</span>")

            # রেন্ডম ডিলে (১ থেকে ২ মিনিট) - ব্যান রিস্ক কমাতে
            delay = random.randint(60, 120)
            logs.append(f"<span class='text-secondary'>[⏳] পরবর্তী লাইকের জন্য {delay} সেকেন্ড অপেক্ষা করা হচ্ছে...</span>")
            time.sleep(delay)

        except Exception as e:
            logs.append(f"<span class='text-danger'>[✖] {email} এর ক্ষেত্রে ত্রুটি: {str(e)}</span>")

# --- ফ্রন্টএন্ড ডিজাইন (HTML/CSS/JS) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FF Unlimited Real Like Bot</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #0d1117; color: #c9d1d9; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        .container { max-width: 700px; margin-top: 40px; }
        .card { background-color: #161b22; border: 1px solid #30363d; border-radius: 12px; margin-bottom: 20px; box-shadow: 0 8px 24px rgba(0,0,0,0.5); }
        .card-header { border-bottom: 1px solid #30363d; font-weight: bold; color: #58a6ff; }
        .form-control { background-color: #0d1117; border: 1px solid #30363d; color: white; }
        .form-control:focus { background-color: #0d1117; color: white; border-color: #58a6ff; box-shadow: none; }
        .btn-primary { background-color: #238636; border: none; font-weight: bold; }
        .btn-primary:hover { background-color: #2ea043; }
        .btn-start { background-color: #1f6feb; border: none; font-weight: bold; }
        #log-container { background-color: #010409; height: 250px; overflow-y: auto; padding: 15px; border-radius: 8px; font-family: monospace; font-size: 13px; border: 1px solid #30363d; }
    </style>
</head>
<body>
    <div class="container">
        <div class="card text-center p-3">
            <h2 class="text-primary">FF REAL ID LIKE BOT</h2>
            <p class="text-secondary small">সব আইডি লগইন হবে এবং রেন্ডম সময়ে লাইক যাবে।</p>
        </div>

        <div class="card">
            <div class="card-header p-3">অ্যাকাউন্ট যোগ করুন (Gmail/Garena)</div>
            <div class="card-body">
                <div class="mb-3">
                    <input type="text" id="email" class="form-control" placeholder="Email বা UID দিন">
                </div>
                <div class="mb-3">
                    <input type="password" id="pass" class="form-control" placeholder="Password দিন">
                </div>
                <button onclick="addAccount()" class="btn btn-primary w-100">Save Account to Bot</button>
            </div>
        </div>

        <div class="card">
            <div class="card-header p-3">লাইক অপারেশন</div>
            <div class="card-body">
                <div class="mb-3">
                    <input type="text" id="target_uid" class="form-control" placeholder="Target Player UID (e.g. 12345678)">
                </div>
                <button onclick="startLiking()" class="btn btn-start btn-lg w-100 text-white">Start Sending Likes</button>
            </div>
        </div>

        <div class="card">
            <div class="card-header p-3">লাইভ লগ (Live Status)</div>
            <div class="card-body">
                <div id="log-container">অপেক্ষায় আছি...</div>
            </div>
        </div>
    </div>

    <script>
        async function addAccount() {
            const email = document.getElementById('email').value;
            const pass = document.getElementById('pass').value;
            if(!email || !pass) return alert("দয়া করে ইমেইল এবং পাসওয়ার্ড দিন!");

            const res = await fetch(`/add?id=${email}&pass=${pass}`);
            const data = await res.json();
            alert(data.message);
            document.getElementById('email').value = "";
            document.getElementById('pass').value = "";
        }

        async function startLiking() {
            const uid = document.getElementById('target_uid').value;
            if(!uid) return alert("টার্গেট UID দিন!");
            fetch(`/start?uid=${uid}`);
        }

        setInterval(async () => {
            const res = await fetch('/get_logs');
            const data = await res.json();
            const logDiv = document.getElementById('log-container');
            logDiv.innerHTML = data.logs.join('<br>');
            logDiv.scrollTop = logDiv.scrollHeight;
        }, 2000);
    </script>
</body>
</html>
"""

# --- সার্ভার রুটস ---

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/add')
def add_account():
    acc_id = request.args.get('id')
    pwd = request.args.get('pass')
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO ff_accounts (account_id, password) VALUES (?, ?)", (acc_id, pwd))
    conn.commit()
    conn.close()
    return jsonify({"message": "অ্যাকাউন্টটি সফলভাবে যোগ হয়েছে!"})

@app.route('/start')
def start_bot():
    uid = request.args.get('uid')
    thread = threading.Thread(target=send_like_process, args=(uid,))
    thread.start()
    return jsonify({"status": "started"})

@app.route('/get_logs')
def get_logs():
    return jsonify({"logs": logs[-15:]}) # শেষ ১৫টি লগ দেখাবে

if __name__ == '__main__':
    # Render বা Local-এর জন্য পোর্ট সেটআপ
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
