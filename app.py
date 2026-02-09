import sqlite3
import threading
import time
import random
import requests
from flask import Flask, render_template_string, request, jsonify

# --- কনফিগারেশন ও ডাটাবেস ---
DB_NAME = "database.db"
app = Flask(__name__)

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS accounts (id INTEGER PRIMARY KEY, token TEXT, name TEXT)''')
    conn.commit()
    conn.close()

init_db()

# --- এইচটিএমএল ইন্টারফেস (সম্পূর্ণ এক ফাইলে) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FF Real Like Bot - Mobile</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #0f172a; color: white; padding-top: 30px; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        .card { background-color: #1e293b; border: none; border-radius: 15px; color: white; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); }
        .btn-success { background-color: #10b981; border: none; }
        .btn-primary { background-color: #3b82f6; border: none; }
        .status-box { background: #334155; padding: 15px; border-radius: 10px; font-size: 14px; max-height: 200px; overflow-y: auto; }
    </style>
</head>
<body>
    <div class="container">
        <div class="row justify-content-center">
            <div class="col-md-8">
                <div class="card p-4 text-center">
                    <h2 class="text-info font-weight-bold">FF REAL ID LIKE BOT</h2>
                    <p class="text-secondary small">মোবাইল দিয়ে কন্ট্রোল করুন আপনার রিয়েল আইডি লাইক বট</p>
                </div>

                <div class="card p-4">
                    <h5>১. অ্যাকাউন্ট যোগ করুন</h5>
                    <p class="small text-warning">Kiwi Browser দিয়ে আপনার জিমেইল আইডির টোকেন বের করে এখানে দিন।</p>
                    <input type="text" id="acc_name" class="form-control mb-2 bg-dark text-white border-secondary" placeholder="আইডির নাম (চেনার জন্য)">
                    <textarea id="acc_token" class="form-control mb-2 bg-dark text-white border-secondary" rows="3" placeholder="এখানে Token বা Session Cookie পেস্ট করুন"></textarea>
                    <button onclick="saveAccount()" class="btn btn-primary w-100">Save Account</button>
                </div>

                <div class="card p-4">
                    <h5>২. লাইক পাঠানো শুরু করুন</h5>
                    <input type="text" id="target_uid" class="form-control mb-3 bg-dark text-white border-secondary" placeholder="টার্গেট UID দিন (যেমন: 12345678)">
                    <button onclick="startLiking()" class="btn btn-success btn-lg w-100">Start Liking Process</button>
                </div>

                <div class="card p-4">
                    <h5>অপারেশন স্ট্যাটাস</h5>
                    <div id="status" class="status-box">এখানকার মেসেজগুলো লক্ষ্য করুন...</div>
                </div>
            </div>
        </div>
    </div>

    <script>
        async function saveAccount() {
            const name = document.getElementById('acc_name').value;
            const token = document.getElementById('acc_token').value;
            if(!token) return alert("টোকেন দিন!");
            
            const res = await fetch(`/add_acc?name=${name}&token=${token}`);
            const data = await res.json();
            alert(data.message);
            document.getElementById('acc_token').value = "";
        }

        async function startLiking() {
            const uid = document.getElementById('target_uid').value;
            if(!uid) return alert("UID দিন!");
            
            document.getElementById('status').innerHTML += `<br><span class="text-success">[🚀] UID: ${uid} এর জন্য প্রসেস শুরু হয়েছে...</span>`;
            
            const res = await fetch(`/start_like?uid=${uid}`);
            const data = await res.json();
        }

        // রিয়েলটাইম স্ট্যাটাস আপডেট দেখার জন্য (ঐচ্ছিক)
        setInterval(async () => {
            const res = await fetch('/get_logs');
            const data = await res.json();
            if(data.logs) {
                document.getElementById('status').innerHTML = data.logs;
            }
        }, 3000);
    </script>
</body>
</html>
"""

# --- সার্ভার লজিক ---

logs = []

def send_like_task(target_uid):
    global logs
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT token, name FROM accounts")
    accounts = c.fetchall()
    conn.close()

    if not accounts:
        logs.append("<span class='text-danger'>[!] কোন আইডি পাওয়া যায়নি! আগে আইডি যোগ করুন।</span>")
        return

    for acc in accounts:
        token, name = acc
        try:
            # এখানে ফ্রি ফায়ার লাইক এপিআই এন্ডপয়েন্ট বসাতে হবে। 
            # বিভিন্ন ওপেন সোর্স প্রজেক্ট থেকে আপডেট এপিআই পাওয়া যায়।
            api_url = "https://freefire-api-endpoint.com/api/v1/like" 
            
            logs.append(f"<span class='text-info'>[✔] {name} থেকে লাইক পাঠানো হচ্ছে...</span>")
            
            # ডামি রিকোয়েস্ট লজিক (রিয়েল এপিআই এখানে কল হবে)
            # requests.post(api_url, headers={"Authorization": f"Bearer {token}"}, json={"uid": target_uid})
            
            # রেন্ডম ডিলে (১ থেকে ২ মিনিট)
            delay = random.randint(60, 120)
            logs.append(f"<span class='text-secondary'>[⏳] {delay} সেকেন্ড অপেক্ষা করা হচ্ছে...</span>")
            time.sleep(delay)
            
        except Exception as e:
            logs.append(f"<span class='text-danger'>[✖] Error: {str(e)}</span>")

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/add_acc')
def add_acc():
    name = request.args.get('name')
    token = request.args.get('token')
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO accounts (name, token) VALUES (?, ?)", (name, token))
    conn.commit()
    conn.close()
    return jsonify({"message": "অ্যাকাউন্টটি সফলভাবে ডাটাবেসে সেভ করা হয়েছে!"})

@app.route('/start_like')
def start_like():
    uid = request.args.get('uid')
    thread = threading.Thread(target=send_like_task, args=(uid,))
    thread.start()
    return jsonify({"status": "started"})

@app.route('/get_logs')
def get_logs():
    return jsonify({"logs": "<br>".join(logs[-10:])}) # শেষ ১০টি মেসেজ দেখাবে

if __name__ == '__main__':
    # Termux-এ চালানোর জন্য লোকাল হোস্ট ০.০.০.০ দিতে হবে
    app.run(host='0.0.0.0', port=8080)
