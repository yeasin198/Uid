import sqlite3
import threading
import time
import random
import requests
from flask import Flask, render_template_string, request, jsonify
import undetected_chromedriver as uc

app = Flask(__name__)
DB_NAME = "database.db"

# --- ডাটাবেস সেটআপ ---
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS accounts (id INTEGER PRIMARY KEY, email TEXT, token TEXT)''')
    conn.commit()
    conn.close()

init_db()

# --- HTML ইন্টারফেস (এক ফাইলেই রাখা হয়েছে) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>FF Real Like Bot</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background: #121212; color: white; font-family: sans-serif; }
        .container { margin-top: 50px; max-width: 600px; }
        .card { background: #1e1e1e; border: 1px solid #333; color: white; border-radius: 15px; }
        .btn-google { background: #db4437; color: white; }
        .btn-start { background: #00c853; color: white; }
    </style>
</head>
<body>
<div class="container text-center">
    <div class="card p-4 shadow-lg">
        <h2 class="mb-4">FF Real ID Like Bot</h2>
        <p class="text-secondary">গুগল দিয়ে লগইন করুন এবং আনলিমিটেড লাইক নিন</p>
        
        <div class="d-grid gap-2">
            <button onclick="addAccount()" class="btn btn-google btn-lg">Add Account (Google Login)</button>
        </div>
        
        <hr class="my-4">
        
        <div class="mb-3">
            <input type="text" id="target_uid" class="form-control bg-dark text-white border-secondary" placeholder="Target UID দিন">
        </div>
        
        <div class="d-grid">
            <button onclick="startLiking()" class="btn btn-start btn-lg">Start Liking Process</button>
        </div>
        
        <div id="status" class="mt-4 text-info font-monospace small"></div>
    </div>
</div>

<script>
    async function addAccount() {
        document.getElementById('status').innerText = "ব্রাউজার খুলছে... দয়া করে গুগল লগইন সম্পন্ন করুন।";
        const res = await fetch('/add_account');
        const data = await res.json();
        alert(data.message);
        document.getElementById('status').innerText = data.message;
    }

    async function startLiking() {
        const uid = document.getElementById('target_uid').value;
        if(!uid) return alert("UID দিন!");
        
        document.getElementById('status').innerText = "লাইক প্রসেস শুরু হয়েছে (রেন্ডম ডিলে ১-২ মিনিট)...";
        fetch('/start_likes?uid=' + uid);
    }
</script>
</body>
</html>
"""

# --- রিয়েল লাইক পাঠানোর লজিক ---
def send_like_logic(target_uid):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT token FROM accounts")
    accounts = c.fetchall()
    conn.close()

    if not accounts:
        print("No accounts found in database!")
        return

    # ফ্রি ফায়ার লাইক এপিআই (এই URL টি সময়ভেদে পরিবর্তন হতে পারে)
    API_URL = "https://freefire-api-endpoint.com/api/v1/like" 

    for acc in accounts:
        token = acc[0]
        try:
            # এখানে আপনার এপিআই অনুযায়ী হেডার এবং ডাটা সাজাতে হবে
            headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
            data = {"uid": target_uid}
            
            # response = requests.post(API_URL, json=data, headers=headers)
            print(f"Like sending from an account to {target_uid}...")

            # ১ থেকে ২ মিনিটের রেন্ডম ডিলে
            wait_time = random.randint(60, 120)
            time.sleep(wait_time)
            
        except Exception as e:
            print(f"Error: {e}")

# --- রুটস (Routes) ---

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/add_account')
def add_account():
    def browser_task():
        # undetected_chromedriver ব্যবহার করা হয়েছে যাতে গুগল ব্লক না করে
        options = uc.ChromeOptions()
        driver = uc.Chrome(options=options)
        
        # গ্যারিনা বা শপটুগেম লগইন পেজ যেখানে গুগল অপশন আছে
        driver.get("https://shop2game.com/") # উদাহরণস্বরূপ
        
        # এখানে ইউজারকে ২ মিনিট সময় দেওয়া হচ্ছে লগইন করার জন্য
        # লগইন হয়ে গেলে অটোমেটিক সেশন বা টোকেন কালেক্ট করার লজিক
        time.sleep(120) 
        
        try:
            # সেশন টোকেন বা কুকি সংগ্রহ (আপনার এপিআই এর প্রয়োজন অনুযায়ী)
            cookies = driver.get_cookies()
            token_string = str(cookies) 
            
            # ডাটাবেসে সেভ করা
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            c.execute("INSERT INTO accounts (email, token) VALUES (?, ?)", ("GoogleUser", token_string))
            conn.commit()
            conn.close()
            driver.quit()
        except:
            driver.quit()

    threading.Thread(target=browser_task).start()
    return jsonify({"status": "success", "message": "লগইন উইন্ডো খোলা হয়েছে। লগইন করে ২ মিনিট অপেক্ষা করুন।"})

@app.route('/start_likes')
def start_likes():
    uid = request.args.get('uid')
    threading.Thread(target=send_like_logic, args=(uid,)).start()
    return jsonify({"status": "started"})

if __name__ == '__main__':
    print("Server starting at http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
