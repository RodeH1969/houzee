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
    
    print(f"🔍 TELEGRAM DEBUG: bot_token exists: {bool(bot_token)}")
    print(f"🔍 TELEGRAM DEBUG: chat_id exists: {bool(chat_id)}")
    
    if not bot_token or not chat_id:
        print("❌ TELEGRAM ERROR: Missing bot token or chat ID")
        return False
    
    # Format the message
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
        print(f"🔍 TELEGRAM DEBUG: Sending to URL: {url}")
        print(f"🔍 TELEGRAM DEBUG: Payload: {payload}")
        
        response = requests.post(url, json=payload, timeout=10)
        print(f"🔍 TELEGRAM DEBUG: Response status: {response.status_code}")
        print(f"🔍 TELEGRAM DEBUG: Response text: {response.text}")
        
        if response.status_code == 200:
            print("✅ TELEGRAM SUCCESS: Message sent!")
            return True
        else:
            print(f"❌ TELEGRAM ERROR: Status {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ TELEGRAM EXCEPTION: {str(e)}")
        print(f"❌ TELEGRAM TRACEBACK: {traceback.format_exc()}")
        return False

def save_winner(winner_data):
    """Save winner data and update house index"""
    
    print(f"🔍 SAVE_WINNER DEBUG: Received data: {winner_data}")
    
    try:
        suburb = winner_data.get('suburb', '')
        print(f"🔍 SAVE_WINNER DEBUG: Suburb: {suburb}")
        
        # Load winners.json
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
        winners_file = os.path.join(base_path, 'winners.json')
        winners = []
        if os.path.exists(winners_file):
            with open(winners_file, 'r') as f:
                winners = json.load(f)
        
        # Append new winner
        new_winner = {
            "name": f"Winner: {winner_data.get('name', 'Unknown')}",
            "mobile": winner_data.get('phone', 'Unknown'),
            "address": winner_data.get('address', 'Unknown'),
            "image": winner_data.get('image', '')
        }
        winners.append(new_winner)
        
        # Save updated winners.json
        with open(winners_file, 'w') as f:
            json.dump(winners, f, indent=2)
        
        # Update current_house.json
        ch_file = os.path.join(base_path, 'current_house.json')
        current = {}
        if os.path.exists(ch_file):
            with open(ch_file, 'r') as f:
                current = json.load(f)
        
        current_index = current.get(suburb, 1)
        current[suburb] = current_index + 1
        
        with open(ch_file, 'w') as f:
            json.dump(current, f, indent=2)
        
        # Send Telegram notification  
        telegram_sent = send_telegram_notification(winner_data, suburb)
        
        print(f"✅ SAVE_WINNER SUCCESS: Telegram sent: {telegram_sent}")
        
        return {
            'success': True,
            'telegram_sent': telegram_sent,
            'next_house_index': current[suburb]
        }
        
    except Exception as e:
        print(f"❌ SAVE_WINNER ERROR: {str(e)}")
        print(f"❌ SAVE_WINNER TRACEBACK: {traceback.format_exc()}")
        return {
            'success': False,
            'error': str(e),
            'telegram_sent': False
        }