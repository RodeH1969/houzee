from flask import Flask, send_from_directory, jsonify, render_template, request
from routes.load_suburbs import load_suburb_list
from routes.house_loader import get_current_house_data
from routes.submit_answer import save_winner
import urllib.parse
import os
import json
import socket
import requests

# 🧪 ENVIRONMENT VARIABLE TESTING
print("=" * 60)
print("🧪 ENVIRONMENT VARIABLE TEST")
print("=" * 60)
print("🧪 TELEGRAM_BOT_TOKEN =", os.environ.get('TELEGRAM_BOT_TOKEN', 'MISSING'))
print("🧪 TELEGRAM_CHAT_ID =", os.environ.get('TELEGRAM_CHAT_ID', 'MISSING'))
print("🧪 GOOGLE_API_KEY =", os.environ.get('GOOGLE_API_KEY', 'MISSING'))
print("=" * 60)

# 🚀 TELEGRAM STARTUP TEST
print("🚀 TESTING TELEGRAM ON APP STARTUP...")
bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
chat_id = os.environ.get('TELEGRAM_CHAT_ID')

if bot_token and chat_id:
    try:
        print(f"🔍 Sending test message to chat_id: {chat_id}")
        response = requests.post(
            f"https://api.telegram.org/bot{bot_token}/sendMessage",
            json={
                "chat_id": chat_id, 
                "text": "🚀 Houzee app started successfully! Environment variables are working!"
            },
            timeout=10
        )
        print(f"🔍 Telegram response status: {response.status_code}")
        print(f"🔍 Telegram response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Telegram test message sent successfully on app startup!")
        else:
            print(f"❌ Telegram test failed with status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Telegram startup test error: {e}")
else:
    if not bot_token:
        print("❌ TELEGRAM_BOT_TOKEN is missing!")
    if not chat_id:
        print("❌ TELEGRAM_CHAT_ID is missing!")

print("=" * 60)

app = Flask(__name__, static_folder="../", template_folder="templates")

# ✅ SECURE: Get Google API key from environment variable
google_api_key = os.environ.get('GOOGLE_API_KEY', 'AIzaSyBJoyvCd3fWMnk0O5wWY3pH98n2wkKCCxc')

@app.route('/')
def serve_home():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/load_suburbs')
def load_suburbs():
    suburbs = load_suburb_list()
    return jsonify({'suburbs': suburbs})

@app.route('/suburb/<path:suburb_path>')
def serve_suburb_game(suburb_path):
    suburb_name = urllib.parse.unquote(suburb_path)
    valid_suburbs = load_suburb_list()
    if suburb_name not in valid_suburbs:
        return f"Invalid suburb: {suburb_name}", 404

    house_data = get_current_house_data(suburb_name)
    if not house_data:
        return render_template(
            'no_houses.html', 
            suburb=suburb_name
        ), 200

    return render_template(
        'suburb_page.html',
        suburb=suburb_name,
        image_path=house_data['image_path'],
        address=house_data['answer'],
        google_api_key=google_api_key  # ✅ Pass API key securely to template
    )

@app.route('/submit_winner', methods=['POST'])
def submit_winner():
    data = request.get_json()
    
    # 🧪 DEBUG: Log the winner submission
    print(f"🧪 WINNER SUBMISSION DEBUG: Received data: {data}")
    
    saved = save_winner(data)
    
    # 🧪 DEBUG: Log after save_winner returns
    print(f"🧪 save_winner RETURNED: {saved}")
    
    return jsonify(saved)

@app.route('/winners.json')
def get_winners():
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
    winners_file = os.path.join(base_path, 'winners.json')
    
    if not os.path.exists(winners_file):
        return jsonify([])

    with open(winners_file, 'r') as f:
        winners = json.load(f)
    
    return jsonify(winners)

# ✅ ✅ ✅ NEW — Download winners.json
@app.route('/download_winners')
def download_winners():
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
    winners_file = os.path.join(base_path, 'winners.json')
    
    if not os.path.exists(winners_file):
        return "No winners file found.", 404

    return send_from_directory(base_path, 'winners.json', as_attachment=True)

# ✅ ✅ ✅ NEW — Return current house data without advancing
@app.route('/next_house/<suburb>')
def next_house(suburb):
    """Get next house data without incrementing"""
    house_data = get_current_house_data(suburb)
    return jsonify(house_data)

@app.route('/<path:path>')
def static_proxy(path):
    return send_from_directory(app.static_folder, path)

def get_local_ip():
    """Get the local IP address"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "Unable to determine IP"

if __name__ == '__main__':
    # ✅ Production vs Development configuration
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    
    if debug:
        # Local development - show helpful info
        local_ip = get_local_ip()
        print("\n" + "="*50)
        print("🏠 HOUZEE SERVER STARTED!")
        print("="*50)
        print(f"🖥️  DESKTOP: http://localhost:{port}")
        print(f"📱 MOBILE:  http://{local_ip}:{port}")
        print("="*50)
        print("Make sure mobile is on same WiFi network!")
        print("="*50 + "\n")
    
    app.run(debug=debug, port=port, host='0.0.0.0')
