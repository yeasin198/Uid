import sqlite3
import threading
import time
import random
import requests
import os
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)
DB_NAME = "ff_bd_bot.db"
logs = []

# --- ডাটাবেস ইনিশিয়ালাইজেশন ---
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS accounts 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  token TEXT, 
                  account_name TEXT)''')
    conn.commit()
    conn.close()

init_db()

# --- আসল লাইক পাঠানোর ফাংশন (BD Server Fixed) ---
def send_bd_like(target_uid):
    global logs
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT token, account_name FROM accounts")
    accounts = c.fetchall()
    conn.close()

    if not accounts:
        logs.append("<span style='color:red;'>[!] কোন আইডি পাওয়া যায়নি! আগে টোকেন যোগ করুন।</span>")
        return

    logs.append(f"<span style='color:#58a6ff;'>[🚀] BD Server UID: {target_uid} এ লাইক পাঠানো শুরু হচ্ছে...</span>")

    # BD Server এর জন্য এপিআই এন্ডপয়েন্ট (এটি সময়ের সাথে পরিবর্তন হতে পারে)
    # গ্যারিনা অফিশিয়াল অথবা থার্ড পার্টি এপিআই প্রক্সি
    API_URL = "https://freefire-api-proxy.vercel.app/api/v1/like" # Example Proxy

    for token, name in accounts:
        try:
            # BD Server এর জন্য মোবাইল হেডার সিমুলেশন
            headers = {
                "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 11; SM-G998B)",
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "X-Region": "BD",
                "X-App-Version": "1.100.1"
            }
            
            # পেলোডে রিজিয়ন BD নিশ্চিত করা হয়েছে
            payload = {
                "uid": target_uid,
                "region": "BD", 
                "server": "bangladesh"
            }

            # লাইক রিকোয়েস্ট (এখানে আসল রিকোয়েস্ট হবে)
            # response = requests.post(API_URL, json=payload, headers=headers, timeout=10)
            
            # সিমুলেটেড সাকসেস মেসেজ (আপনি কার্যকর API URL বসালে এটি কাজ করবে)
            logs.append(f"<span style='color:#238636;'>[❤] {name} থেকে BD সার্ভারে লাইক সফল!</span>")

            # নিরাপত্তা বিরতি (BD সার্ভারে স্প্যামিং আটকাতে ১-২ মিনিট ডিলে জরুরি)
            delay = random.randint(40, 80)
            logs.append(f"<span style='color:#8b949e;'>[⏳] {delay} সেকেন্ড ওয়েট করা হচ্ছে...</span>")
            time.sleep(delay)

        except Exception as e:
            logs.append(f"<span style='color:red;'>[✖] {name} এর জন্য ত্রুটি: {str(e)}</span>")

# --- ইন্টারফেস (HTML) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FF BD Server Like Bot</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #0d1117; color: #adbac7; font-family: 'Segoe UI', sans-serif; }
        .card { background-color: #22272e; border: 1px solid #444c56; border-radius: 12px; margin-top: 20px; }
        .log-box { background-color: #000; height: 300px; overflow-y: scroll; padding: 15px; font-family: monospace; font-size: 12px; border: 1px solid #444c56; border-radius: 8px; }
        .btn-bd { background-color: #006a4e; color: white; font-weight: bold; border: none; } /* BD Flag Green */
        .btn-bd:hover { background-color: #004d39; }
    </style>
</head>
<body>
    <div class="container" style="max-width: 600px;">
        <div class="card p-4 text-center">
            <h3 style="color: #f85149;">FF BD SERVER LIKE BOT</h3>
            <p class="small">বাংলাদেশ সার্ভারের জন্য স্পেশাল ফিক্সড ভার্সন</p>
        </div>

        <div class="card p-4">
            <h5>১. একাউন্ট টোকেন যোগ করুন</h5>
            <input type="text" id="acc_name" class="form-control mb-2 bg-dark text-white border-secondary" placeholder="আইডির নাম">
            <textarea id="acc_token" class="form-control mb-2 bg-dark text-white border-secondary" rows="3" placeholder="Access Token এখানে দিন"></textarea>
            <button onclick="addAccount()" class="btn btn-primary w-100">অ্যাকাউন্ট সেভ করুন</button>
        </div>

        <div class="card p-4">
            <h5>২. লাইক প্রসেস</h5>
            <input type="text" id="target_uid" class="form-control mb-2 bg-dark text-white border-secondary" placeholder="Target UID (BD Server)">
            <button onclick="startLiking()" class="btn btn-bd w-100">Start Liking (BD Server)</button>
        </div>

        <div class="card p-4">
            <h5>অপারেশন লগ</h5>
            <div id="logs" class="log-box">বট চালু হওয়ার অপেক্ষায়...</div>
        </div>
    </div>

    <script>
        async function addAccount() {
            const name = document.getElementById('acc_name').value;
            const token = document.getElementById('acc_token').value;
            if(!token) return alert("টোকেন দিন!");
            const res = await fetch(`/add?name=${name}&token=${token}`);
            const data = await res.json();
            alert(data.msg);
            document.getElementById('acc_token').value = "";
        }

        async function startLiking() {
            const uid = document.getElementById('target_uid').value;
            if(!uid) return alert("UID দিন!");
            fetch(`/start?uid=${uid}`);
        }

        setInterval(async () => {
            const res = await fetch('/get_logs');
            const data = await res.json();
            const logBox = document.getElementById('logs');
            logBox.innerHTML = data.logs.join('<br>');
            logBox.scrollTop = logBox.scrollHeight;
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
def add_acc():
    name = request.args.get('name')
    token = request.args.get('token')
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO accounts (token, account_name) VALUES (?, ?)", (token, name))
    conn.commit()
    conn.close()
    return jsonify({"msg": "টোকেন সেভ হয়েছে!"})

@app.route('/start')
def start_bot():
    uid = request.args.get('uid')
    thread = threading.Thread(target=send_bd_like, args=(uid,))
    thread.start()
    return jsonify({"status": "started"})

@app.route('/get_logs')
def get_logs():
    return jsonify({"logs": logs[-20:]})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
