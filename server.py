from flask import Flask, request, jsonify, render_template_string
import os
import json
import time
import random
from datetime import datetime
import g4f

app = Flask(__name__)
DATA_FILE = "users.json"

# Save loading
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        try:
            users = json.load(f)
        except json.JSONDecodeError:
            users = {}
else:
    users = {}

# Save
def save_users():
    with open(DATA_FILE, "w") as f:
        json.dump(users, f, indent=2)

# === Limit config ===
LIMIT_DOLLAR = 15
LIMIT_REQUESTS = 100
COST_PER_REQUEST = 0.1

# === Key generate ===
def generate_api_key():
    return f"honey_{random.randint(100000, 999999)}"

@app.route('/', methods=['POST'])
def standart():
    return "error: 404"

@app.route('/generate_key', methods=['POST'])
def generate_key():
    user_id = str(request.json.get("user_id"))
    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    if user_id in users:
        return jsonify({"api_key": users[user_id]["api_key"], "message": "Already exists."})

    api_key = generate_api_key()
    users[user_id] = {
        "api_key": api_key,
        "balance": LIMIT_DOLLAR,
        "requests_made": 0,
        "last_request_time": time.time(),
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    save_users()
    return jsonify({"api_key": api_key})

@app.route('/get_user_info', methods=['POST'])
def get_user_info():
    user_id = str(request.json.get("user_id"))
    user = users.get(user_id)

    if not user:
        return jsonify({"exists": False})

    return jsonify({
        "exists": True,
        "api_key": user["api_key"],
        "balance": round(user["balance"], 2),
        "requests": user["requests_made"],
        "created_at": user["created_at"]
    })

@app.route('/process_request', methods=['POST'])
def process_request():
    data = request.json
    user_id = str(data.get("user_id"))
    api_key = data.get("api_key")
    user_input = data.get("user_input")

    if not user_id or not api_key or not user_input:
        return jsonify({"error": "Missing parameters"}), 400

    user = users.get(user_id)
    if not user or user["api_key"] != api_key:
        return jsonify({"error": "Invalid credentials"}), 403

    if user["balance"] <= 0 or user["requests_made"] >= LIMIT_REQUESTS:
        return jsonify({"error": "Limit reached"}), 403

    try:
        response_text = g4f.ChatCompletion.create(
            model=g4f.models.default,
            messages=[
                {"role": "system", "content": (
                    "Your name is honeyAI. You don't have to mention that you are ChatGPT or openAI. You easily help with codes and homework. You can: generate texts, come up with ideas, are good at computer science, etc. You know and can speak 50 languages of the world, including: English, Russian, Ukrainian, French, Spanish, German, Chinese, Japanese, Korean, Arabic, Polish, Czech, Serbian, Bulgarian."
                )},
                {"role": "user", "content": user_input}
            ]
        )
    except Exception as e:
        return jsonify({"error": f"honeyAI error: {e}"}), 500

    user["requests_made"] += 1
    user["balance"] -= COST_PER_REQUEST
    save_users()

    return jsonify({
        "response": response_text,
        "remaining_balance": round(user["balance"], 2),
        "requests_made": user["requests_made"]
    })

@app.route('/check_balance', methods=['POST'])
def check_balance():
    user_id = str(request.json.get("user_id"))
    user = users.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "balance": round(user["balance"], 2),
        "requests": user["requests_made"]
    })

@app.route('/B30R03M2012HONEYKIWI', methods=['POST'])
def set_balance():
    data = request.json
    user_id = str(data.get("user_id"))
    new_balance = float(data.get("amount", 15))

    if data.get("secret") != "KIWI2024":
        return jsonify({"error": "Access denied"}), 403

    if user_id in users:
        users[user_id]["balance"] = new_balance
        save_users()
        return jsonify({"ok": True, "balance": new_balance})
    else:
        return jsonify({"error": "User not found"}), 404

@app.route("/debug_users", methods=["GET"])
def debug_users():
    return jsonify(users)

@app.route('/key_page')
def key_page():
    user_id = request.args.get("user_id")
    if not user_id:
        return "<h2>❌ Ошибка: параметр user_id обязателен.</h2>"

    # Если нет токена — создаём
    if user_id not in users:
        token = generate_api_key()
        users[user_id] = {
            "api_key": token,
            "balance": LIMIT_DOLLAR,
            "requests_made": 0,
            "last_request_time": time.time(),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        save_users()

    api_key = users[user_id]["api_key"]

    # HTML страница
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>honeyAPI</title>
        <style>
            body {{
                font-family: sans-serif;
                background: #f3f3f3;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
            }}
            .box {{
                background: white;
                padding: 30px;
                border-radius: 12px;
                box-shadow: 0 0 15px #ccc;
                text-align: center;
            }}
            code {{
                font-size: 18px;
                background: #eee;
                padding: 8px 16px;
                border-radius: 8px;
                display: inline-block;
                margin-bottom: 10px;
            }}
            button {{
                padding: 10px 18px;
                border: none;
                background: #4CAF50;
                color: white;
                border-radius: 6px;
                cursor: pointer;
            }}
        </style>
        <script>
            function copyToken() {{
                const tokenText = document.getElementById("token").innerText;
                navigator.clipboard.writeText(tokenText).then(function() {{
                    alert("✅ copied!");
                }});
            }}
        </script>
    </head>
    <body>
        <div class="box">
            <h2>API key:</h2>
            <code id="token">{api_key}</code><br>
            <button onclick="copyToken()">Copy</button>
        </div>
    </body>
    </html>
    """
    return render_template_string(html)

if __name__ == "__main__":
    app.run(debug=True)
