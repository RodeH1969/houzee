import os
import json
import requests
import traceback
import base64
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

def update_github_file(filename, data):
    """Update a JSON file on GitHub using the GitHub API"""
    
    github_token = os.environ.get('GITHUB_TOKEN')
    if not github_token:
        print("❌ GITHUB ERROR: Missing GITHUB_TOKEN")
        return False
    
    owner = "RodeH1969"
    repo = "houzee"
    
    try:
        # Get current file content and SHA
        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{filename}"
        headers = {
            'Authorization': f'token {github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        print(f"🔍 GITHUB DEBUG: Getting current {filename}")
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            file_info = response.json()
            sha = file_info['sha']
            print(f"🔍 GITHUB DEBUG: Got SHA for {filename}: {sha}")
        elif response.status_code == 404:
            # File doesn't exist, create it
            sha = None
            print(f"🔍 GITHUB DEBUG: {filename} doesn't exist, will create")
        else:
            print(f"❌ GITHUB ERROR: Failed to get {filename}: {response.status_code}")
            return False
        
        # Prepare new content
        json_content = json.dumps(data, indent=2)
        encoded_content = base64.b64encode(json_content.encode()).decode()
        
        # Update/create file
        update_data = {
            "message": f"Update {filename} via Houzee game",
            "content": encoded_content
        }
        
        if sha:
            update_data["sha"] = sha
        
        print(f"🔍 GITHUB DEBUG: Updating {filename}")
        response = requests.put(url, headers=headers, json=update_data)
        
        if response.status_code in [200, 201]:
            print(f"✅ GITHUB SUCCESS: Updated {filename}")
            return True
        else:
            print(f"❌ GITHUB ERROR: Failed to update {filename}: {response.status_code}")
            print(f"❌ GITHUB ERROR: Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ GITHUB EXCEPTION: {str(e)}")
        print(f"❌ GITHUB TRACEBACK: {traceback.format_exc()}")
        return False

def save_winner(winner_data):
    """Save winner data and update house index"""
    
    print(f"🔍 SAVE_WINNER DEBUG: Received data: {winner_data}")
    
    try:
        suburb = winner_data.get('suburb', '')
        print(f"🔍 SAVE_WINNER DEBUG: Suburb: {suburb}")
        
        # Load winners.json from GitHub
        github_token = os.environ.get('GITHUB_TOKEN')
        headers = {
            'Authorization': f'token {github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        # Get current winners
        winners = []
        try:
            response = requests.get('https://api.github.com/repos/RodeH1969/houzee/contents/winners.json', headers=headers)
            if response.status_code == 200:
                content = base64.b64decode(response.json()['content']).decode()
                winners = json.loads(content)
                print(f"🔍 GITHUB DEBUG: Loaded {len(winners)} existing winners")
        except:
            print("🔍 GITHUB DEBUG: winners.json doesn't exist, starting fresh")
        
        # Append new winner
        new_winner = {
            "name": f"Winner: {winner_data.get('name', 'Unknown')}",
            "mobile": winner_data.get('phone', 'Unknown'),
            "address": winner_data.get('address', 'Unknown'),
            "image": winner_data.get('image', '')
        }
        winners.append(new_winner)
        print(f"🔍 SAVE_WINNER DEBUG: Added winner, now {len(winners)} total")
        
        # Get current house data
        current = {}
        try:
            response = requests.get('https://api.github.com/repos/RodeH1969/houzee/contents/current_house.json', headers=headers)
            if response.status_code == 200:
                content = base64.b64decode(response.json()['content']).decode()
                current = json.loads(content)
                print(f"🔍 GITHUB DEBUG: Loaded current house data: {current}")
        except:
            print("🔍 GITHUB DEBUG: current_house.json doesn't exist, starting fresh")
        
        current_index = current.get(suburb, 1)
        current[suburb] = current_index + 1
        print(f"🔍 SAVE_WINNER DEBUG: Advanced {suburb} from {current_index} to {current_index + 1}")
        
        # Update files on GitHub
        winners_updated = update_github_file('winners.json', winners)
        current_updated = update_github_file('current_house.json', current)
        
        # Send Telegram notification  
        telegram_sent = send_telegram_notification(winner_data, suburb)
        
        print(f"✅ SAVE_WINNER SUCCESS: Telegram sent: {telegram_sent}")
        print(f"✅ SAVE_WINNER SUCCESS: Winners updated: {winners_updated}")
        print(f"✅ SAVE_WINNER SUCCESS: Current house updated: {current_updated}")
        
        return {
            'success': True,
            'telegram_sent': telegram_sent,
            'next_house_index': current[suburb],
            'files_updated': winners_updated and current_updated
        }
        
    except Exception as e:
        print(f"❌ SAVE_WINNER ERROR: {str(e)}")
        print(f"❌ SAVE_WINNER TRACEBACK: {traceback.format_exc()}")
        return {
            'success': False,
            'error': str(e),
            'telegram_sent': False
        }