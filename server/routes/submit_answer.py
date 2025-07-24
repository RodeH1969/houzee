import os
import json
import requests
import traceback
from datetime import datetime

def send_telegram_notification(winner_data, suburb):
    """Send Telegram notification of new winner"""
    
    print(f"🔍 TELEGRAM DEBUG: Function called with suburb={suburb}")
    
    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    
    print(f"🔍 TELEGRAM DEBUG: bot_token={'SET' if bot_token else 'NOT SET'}")
    print(f"🔍 TELEGRAM DEBUG: chat_id={'SET' if chat_id else 'NOT SET'}")
    
    if not bot_token or not chat_id:
        print("⚠️ Telegram not configured - skipping notification")
        return
    
    print(f"🔍 TELEGRAM DEBUG: About to send message for {winner_data.get('name')}")
    
    try:
        # Create rich Telegram message
        message = f"""🏆 *NEW HOUZEE WINNER!* 🏆

🏘️ *Suburb:* {suburb}
👤 *Winner:* {winner_data.get('name', 'Unknown')}
📱 *Mobile:* {winner_data.get('mobile', 'Not provided')}
🏠 *Address:* {winner_data.get('address', 'Unknown')}
🖼️ *House:* {winner_data.get('image', 'Unknown')}

⏰ *Time:* {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"""

        # Send to Telegram
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }
        
        print(f"🔍 TELEGRAM DEBUG: Sending POST to {url}")
        
        response = requests.post(url, json=payload)
        
        print(f"🔍 TELEGRAM DEBUG: Response status: {response.status_code}")
        print(f"🔍 TELEGRAM DEBUG: Response text: {response.text}")
        
        if response.status_code == 200:
            print(f"✅ Telegram notification sent for {winner_data.get('name')} - {suburb}")
        else:
            print(f"❌ Telegram notification failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Telegram notification error: {e}")
        print(f"❌ Full traceback: {traceback.format_exc()}")

def save_winner(winner_data):
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
    winners_file = os.path.join(base_path, 'winners.json')
    current_file = os.path.join(base_path, 'current_house.json')

    print(f"DEBUG: save_winner called with data: {winner_data}")

    # Ensure winners.json exists
    if not os.path.exists(winners_file):
        with open(winners_file, 'w') as f:
            json.dump([], f)

    # Load + append winner (temporarily in memory)
    with open(winners_file, 'r') as f:
        winners = json.load(f)

    winners.append(winner_data)

    # ✅ Try to save (will work locally, fail on Render)
    try:
        with open(winners_file, 'w') as f:
            json.dump(winners, f, indent=2)
        print("✅ Winner saved to file")
    except Exception as e:
        print(f"⚠️ File save failed (expected on Render): {e}")

    # ✅ Extract suburb from image path
    image_path = winner_data.get('image', '')
    suburb = None
    
    print(f"DEBUG: Processing image path: {image_path}")
    
    if '_houses/' in image_path:
        suburb_folder = image_path.split('_houses/')[0]
        print(f"DEBUG: Extracted suburb folder: {suburb_folder}")
        
        if suburb_folder == "Ashgrove":
            suburb = "Ashgrove"
        elif suburb_folder == "TheGap":
            suburb = "The Gap"
        elif suburb_folder == "RedHill":
            suburb = "Red Hill"
        elif suburb_folder == "Bardon":
            suburb = "Bardon"
        elif suburb_folder == "Paddington":
            suburb = "Paddington"
        elif suburb_folder == "Enoggera":
            suburb = "Enoggera"
        
        print(f"DEBUG: Mapped to suburb: {suburb}")
    
    if not suburb:
        print(f"ERROR: Could not determine suburb from image path: {image_path}")
        return winner_data

    # ✅ SEND TELEGRAM NOTIFICATION
    send_telegram_notification(winner_data, suburb)

    # Handle house progression
    if not os.path.exists(current_file):
        with open(current_file, 'w') as f:
            json.dump({}, f)

    with open(current_file, 'r') as f:
        current = json.load(f)

    current_index = current.get(suburb, 1)
    print(f"DEBUG: Current index for {suburb}: {current_index}")
    
    current[suburb] = current_index + 1
    print(f"DEBUG: New index for {suburb}: {current[suburb]}")

    try:
        with open(current_file, 'w') as f:
            json.dump(current, f, indent=2)
        print("✅ House progression saved")
    except Exception as e:
        print(f"⚠️ House progression save failed (expected on Render): {e}")

    return winner_data