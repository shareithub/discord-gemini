import json
import time
import os
import random
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

discord_token = os.getenv('DISCORD_TOKEN')
google_api_key = os.getenv('GOOGLE_API_KEY')

last_message_id = None
bot_user_id = None

# Rate limiting parameters
GEMINI_RETRY_DELAY = 60  # Delay in seconds before retrying Gemini API
DISCORD_RETRY_DELAY = 5  # Delay in seconds before retrying Discord API
MAX_RETRIES = 3

def log_message(message):
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}")

def get_random_message():
    try:
        with open('pesan.txt', 'r', encoding='utf-8') as file:
            lines = [line.strip() for line in file.readlines() if line.strip()]
            if lines:
                return random.choice(lines)
            else:
                log_message("⚠️ pesan.txt is empty")
                return "No messages available"
    except FileNotFoundError:
        log_message("⚠️ pesan.txt not found")
        return "pesan.txt not found"
    except Exception as e:
        log_message(f"⚠️ Error reading pesan.txt: {str(e)}")
        return "Error reading messages"

def generate_gemini_reply(prompt, language="id", retry_count=0):
    """Generate reply using Google Gemini AI with retry logic"""
    if retry_count >= MAX_RETRIES:
        log_message("❌ Max retries reached for Gemini API")
        return None

    try:
        if language == "en":
            ai_prompt = f"{prompt}\n\nRespond with only one sentence in casual urban English, like a natural conversation, and do not use symbols."
        else:
            ai_prompt = f"{prompt}\n\nBerikan 1 kalimat saja dalam bahasa gaul daerah Jakarta seperti obrolan dan jangan gunakan simbol apapun."
            
        url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={google_api_key}'
        headers = {'Content-Type': 'application/json'}
        data = {'contents': [{'parts': [{'text': ai_prompt}]}]}
        
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 429:
            log_message(f"⏳ Rate limited by Gemini API, waiting {GEMINI_RETRY_DELAY} seconds...")
            time.sleep(GEMINI_RETRY_DELAY)
            return generate_gemini_reply(prompt, language, retry_count + 1)
            
        response.raise_for_status()
        result = response.json()
        
        if 'candidates' in result and len(result['candidates']) > 0:
            text = result['candidates'][0]['content']['parts'][0]['text']
            log_message(f"✅ Gemini response: {text}")
            return text
            
        return None
            
    except Exception as e:
        log_message(f"⚠️ Gemini API error: {str(e)}")
        if retry_count < MAX_RETRIES:
            log_message(f"⏳ Retrying in {GEMINI_RETRY_DELAY} seconds...")
            time.sleep(GEMINI_RETRY_DELAY)
            return generate_gemini_reply(prompt, language, retry_count + 1)
        return None

def send_message(channel_id, message_text, reply_to=None, reply_mode=True):
    """Send message to Discord with improved rate limit handling"""
    headers = {
        'Authorization': f'{discord_token}',
        'Content-Type': 'application/json'
    }

    payload = {'content': message_text}
    if reply_mode and reply_to:
        payload['message_reference'] = {'message_id': reply_to}

    while True:
        try:
            response = requests.post(
                f"https://discord.com/api/v9/channels/{channel_id}/messages",
                json=payload,
                headers=headers
            )
            
            if response.status_code == 429:
                retry_after = float(response.json().get('retry_after', DISCORD_RETRY_DELAY))
                log_message(f"⏳ Rate limited by Discord, waiting {retry_after} seconds...")
                time.sleep(retry_after)
                continue  # Retry immediately after timeout
            
            response.raise_for_status()
            log_message(f"✅ Sent: {message_text}")
            return True
            
        except Exception as e:
            log_message(f"⚠️ Discord API error: {str(e)}")
            return False

def auto_reply(channel_id, read_delay, reply_delay, use_gemini, language, reply_mode):
    global last_message_id, bot_user_id

    headers = {'Authorization': f'{discord_token}'}
    
    try:
        bot_info = requests.get('https://discord.com/api/v9/users/@me', headers=headers)
        bot_info.raise_for_status()
        bot_user_id = bot_info.json().get('id')
        log_message(f"✅ Bot started with ID: {bot_user_id}")
    except Exception as e:
        log_message(f"⚠️ Failed to get bot info: {str(e)}")
        return

    # Set initial last_message_id
    try:
        response = requests.get(
            f'https://discord.com/api/v9/channels/{channel_id}/messages?limit=1',
            headers=headers
        )
        response.raise_for_status()
        messages = response.json()
        if messages and isinstance(messages, list) and len(messages) > 0:
            last_message_id = messages[0].get('id')
            log_message(f"✅ Initial message ID set to: {last_message_id}")
    except Exception as e:
        log_message(f"⚠️ Failed to get initial message ID: {str(e)}")

    while True:
        try:
            # Get latest messages, limit to 5 to catch any missed messages
            response = requests.get(
                f'https://discord.com/api/v9/channels/{channel_id}/messages?limit=5',
                headers=headers
            )
            
            if response.status_code == 429:
                retry_after = float(response.json().get('retry_after', read_delay))
                log_message(f"⏳ Rate limited, waiting {retry_after} seconds...")
                time.sleep(retry_after)
                continue
                
            response.raise_for_status()
            messages = response.json()
            
            if messages and isinstance(messages, list):
                # Sort messages by ID to process them in order
                messages.sort(key=lambda x: int(x.get('id', 0)))
                
                for message in messages:
                    message_id = message.get('id')
                    author_id = message.get('author', {}).get('id')
                    
                    # Check if this is a new message from someone else
                    if (last_message_id is None or int(message_id) > int(last_message_id)) and author_id != bot_user_id:
                        user_message = message.get('content', '')
                        log_message(f"📥 Received new message: {user_message}")

                        response_text = None
                        if use_gemini:
                            response_text = generate_gemini_reply(user_message, language)
                            
                        if response_text is None:
                            if use_gemini:
                                log_message("⚠️ Falling back to pesan.txt")
                            response_text = get_random_message()

                        # Wait before replying
                        if reply_delay > 0:
                            time.sleep(reply_delay)
                        
                        # Send the reply
                        if send_message(channel_id, response_text, message_id if reply_mode else None, reply_mode):
                            last_message_id = message_id
                            log_message(f"✅ Updated last message ID to: {last_message_id}")

            # Wait before checking for new messages
            if read_delay > 0:
                time.sleep(read_delay)
            
        except Exception as e:
            log_message(f"⚠️ Error in main loop: {str(e)}")
            time.sleep(read_delay)

def random_message_mode(channel_id, interval):
    log_message("✅ Random message mode started")
    
    while True:
        try:
            message_text = get_random_message()
            send_message(channel_id, message_text, reply_mode=False)
            time.sleep(interval)
                
        except Exception as e:
            log_message(f"⚠️ Error in random message mode: {str(e)}")
            time.sleep(interval)

if __name__ == "__main__":
    try:
        print("\n=== Discord Auto Reply Bot ===\n")
        
        mode = input("Pilih mode (1: Auto Reply, 2: Random Message): ").strip()
        channel_id = input("Masukkan ID channel: ").strip()

        if mode == "1":
            use_gemini = input("Gunakan Google Gemini AI? (y/n): ").lower() == 'y'
            reply_mode = input("Mode balas pesan? (y/n): ").lower() == 'y'
            language = input("Pilih bahasa (id/en): ").lower()
            
            if language not in ["id", "en"]:
                language = "id"
                log_message("⚠️ Invalid language, using Indonesian")
            
            read_delay = int(input("Delay membaca pesan (detik): "))
            reply_delay = int(input("Delay balas pesan (detik): "))

            print("\nKonfigurasi Bot:")
            print(f"- Menggunakan Gemini AI: {'Ya' if use_gemini else 'Tidak (menggunakan pesan.txt)'}")
            print(f"- Mode Reply: {'Ya' if reply_mode else 'Tidak'}")
            print(f"- Bahasa: {'Indonesia' if language == 'id' else 'Inggris'}")
            print(f"- Delay Membaca: {read_delay}s")
            print(f"- Delay Membalas: {reply_delay}s\n")

            auto_reply(channel_id, read_delay, reply_delay, use_gemini, language, reply_mode)
            
        elif mode == "2":
            interval = int(input("Interval kirim pesan (detik): "))
            random_message_mode(channel_id, interval)
            
        else:
            print("⚠️ Mode tidak valid")
            
    except KeyboardInterrupt:
        print("\n\n✅ Bot dihentikan oleh user")
    except Exception as e:
        print(f"\n⚠️ Error fatal: {str(e)}")