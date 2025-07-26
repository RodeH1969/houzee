import os
import json
import traceback
from datetime import datetime
import base64
import requests

def send_telegram_notification(winner_data, suburb):
    print(f"🔍 TELEGRAM DEBUG: Function called with suburb={suburb}")
    
    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    
    if not bot_token or not chat_id:
        print("❌ TELEGRAM ERROR: Missing bot token or chat ID")
        return False

    message = f"""🏠 NEW HOUZEE WINNER!

Name: {winner_data.get('name', 'Unknown')}
Email: {winner_data.get('email', 'Unknown')}
Phone: {winner_data.get('phone', 'Unknown')}
Suburb: {suburb}
House: (guessed correctly)
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

They've won the $10 gift card!"""

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'HTML'
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        print(f"🔍 TELEGRAM DEBUG: Response status: {response.status_code}")
        print(f"🔍 TELEGRAM DEBUG: Response text: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ TELEGRAM EXCEPTION: {str(e)}")
        print(traceback.format_exc())
        return False

def update_github_file(repo, path, message, local_path, branch='main'):
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("❌ GITHUB ERROR: Missing GITHUB_TOKEN")
        return False

    api_url = f"https://api.github.com/repos/{repo}/contents/{path}"

    try:
        with open(local_path, "rb") as f:
            content = base64.b64encode(f.read()).decode()

        r = requests.get(api_url, headers={"Authorization": f"token {token}"})
        sha = r.json().get('sha') if r.status_code == 200 else None

        data = {
            "message": message,
            "content": content,
            "branch": branch
        }
        if sha:
            data["sha"] = sha

        response = requests.put(api_url, json=data, headers={
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        })

        if response.status_code in [200, 201]:
            print(f"✅ GITHUB SUCCESS: {path} updated.")
            return True
        else:
            print(f"❌ GITHUB ERROR: {response.status_code} — {response.json()}")
            return False
    except Exception as e:
        print(f"❌ GITHUB EXCEPTION: {str(e)}")
        return False

def save_winner(winner_data):
    print(f"🔍 SAVE_WINNER DEBUG: Received data: {winner_data}")

    try:
        suburb = winner_data.get('suburb', '')
        print(f"🔍 SAVE_WINNER DEBUG: Suburb: {suburb}")

        DISK_PATH = '/opt/render/data'
        winners_file = os.path.join(DISK_PATH, 'winners.json')
        ch_file = os.path.join(DISK_PATH, 'current_house.json')

        winners = []
        if os.path.exists(winners_file):
            with open(winners_file, 'r') as f:
                winners = json.load(f)

        new_winner = {
            "name": f"Winner: {winner_data.get('name', 'Unknown')}",
            "mobile": winner_data.get('phone', 'Unknown'),
            "address": winner_data.get('address', 'Unknown'),
            "image": winner_data.get('image', '')
        }
        winners.append(new_winner)

        with open(winners_file, 'w') as f:
            json.dump(winners, f, indent=2)

        current = {}
        if os.path.exists(ch_file):
            with open(ch_file, 'r') as f:
                current = json.load(f)

        current_index = current.get(suburb, 1)
        current[suburb] = current_index + 1

        with open(ch_file, 'w') as f:
            json.dump(current, f, indent=2)

        telegram_sent = send_telegram_notification(winner_data, suburb)
        print(f"✅ SAVE_WINNER SUCCESS: Telegram sent: {telegram_sent}")

        repo = "RodeH1969/houzee"
        gh1 = update_github_file(
            repo=repo,
            path="winners.json",
            message="🎉 New winner added",
            local_path=winners_file
        )
        gh2 = update_github_file(
            repo=repo,
            path="current_house.json",
            message="🏠 House index updated",
            local_path=ch_file
        )

        print(f"📦 Pushing winners.json → GitHub: {gh1}")
        print(f"📍 Pushing current_house.json → GitHub: {gh2}")

        return {
            'success': True,
            'telegram_sent': telegram_sent,
            'github_sync': {'winners.json': gh1, 'current_house.json': gh2},
            'next_house_index': current[suburb]
        }

    except Exception as e:
        print(f"❌ SAVE_WINNER ERROR: {str(e)}")
        print(traceback.format_exc())
        return {
            'success': False,
            'error': str(e),
            'telegram_sent': False
        }
