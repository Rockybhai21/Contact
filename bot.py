import os
import json
import telebot
import base64
import secrets
from cryptography.fernet import Fernet

# Get the bot token from the environment variable
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

# Load or create message storage
DATA_FILE = "messages.json"

if os.path.exists("messages.json"):
    with open("messages.json", "r") as f:
        try:
            stored_messages = json.load(f)
        except json.JSONDecodeError:
            stored_messages = {}
else:
    stored_messages = {}

# Encryption key (Ensure this is kept safe and secure)
SECRET_KEY = Fernet.generate_key()
cipher_suite = Fernet(SECRET_KEY)

# Function to encrypt a message
def encrypt_message(message):
    return base64.urlsafe_b64encode(
        Fernet(Fernet.generate_key()).encrypt(message.encode("utf-8"))
    ).decode()

# Function to decrypt a message using a code
def decrypt_message(encrypted_code):
    if stored_messages.get(encrypted_code):
        decrypted_message = stored_messages[encrypted_code]
        return f"Here is your message: {decrypted_message}"
    return "Invalid or expired code. No message found."

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    bot.send_message(user_id, f"Hello {message.from_user.first_name}! 👋\n"
                               "I'm here to help you send secret messages securely! 🔒\n"
                               "Press the button below to send a secret message!", 
                     reply_markup=main_menu())

def main_menu():
    keyboard = telebot.types.InlineKeyboardMarkup()
    send_message_button = telebot.types.InlineKeyboardButton("📩 Send Message", callback_data="send_message")
    keyboard.add(send_message_button)
    return keyboard

@bot.callback_query_handler(func=lambda call: call.data == "send_message")
def send_message(call):
    msg = bot.send_message(call.message.chat.id, "💬 Please enter the message you want to send.")
    bot.register_next_step_handler(msg, save_message)

def generate_encryption_key():
    return Fernet.generate_key()

def encrypt_message(message, key):
    f = Fernet(key)
    return f.encrypt(message.encode()).decode()

def decrypt_message(encrypted_message, key):
    f = Fernet(key)
    try:
        return f.decrypt(encrypted_message.encode()).decode()
    except:
        return "Invalid code! Either the message is incorrect or the code has expired."

@bot.message_handler(commands=['send'])
def send_message_step1(message):
    keyboard = telebot.types.InlineKeyboardMarkup()
    button = telebot.types.InlineKeyboardButton("📩 Send Message", callback_data="send_message")
    keyboard.add(send_message_button)
    bot.send_message(message.chat.id, 
                     "💬 *You Can Use Me To Do A Secret Chat With Anyone!*\n\nMade by @YourBotUsername", 
                     parse_mode="Markdown", 
                     reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data == "send_message")
def ask_for_message(call):
    msg = bot.send_message(call.message.chat.id, "📩 *Send Me The Message* 🔒", 
                           parse_mode="Markdown")
    bot.register_next_step_handler(msg, get_message)

def get_encryption_key():
    return Fernet.generate_key()

@bot.message_handler(func=lambda message: True)
def save_message(message):
    key = Fernet.generate_key()
    encrypted_message = encrypt_message(message.text, key)
    
    encrypted_code = key.decode()[:8]  # Generate short key
    stored_messages[encrypted_message] = message.text  # Store original message

    # Save encrypted messages in JSON
    with open("messages.json", "w") as f:
        json.dump(stored_messages, f)

    keyboard = telebot.types.InlineKeyboardMarkup()
    decrypt_button = telebot.types.InlineKeyboardButton("🔓 Decrypt", callback_data=f"decrypt_{encrypted_message}_{key.decode()}")
    keyboard.add(telebot.types.InlineKeyboardButton("📩 Send Message", callback_data="send_message"))

    bot.reply_to(message, f"❤️ Here Is Your Encrypted Code ➜ `{encrypted_message}` ❤️", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "send_message":
        bot.send_message(call.message.chat.id, "Please enter your secret message:")
        bot.register_next_step_handler(call.message, encrypt_and_store_message)

    elif call.data.startswith("send_message"):
        bot.send_message(call.from_user.id, "📥 Send Me The Message 📩")
    
    elif call.data.startswith("decrypt_"):
        _, encrypted_message, key = call.data.split("_", 2)
        decrypted_text = decrypt_message(encrypted_message, key.encode())
        bot.send_message(call.from_user.id, decrypted_message)

def encrypt_and_store_message(message):
    key = get_encryption_key()
    encrypted_message = encrypt_message(message.text, key)
    message_code = encrypted_message[:8]  # Shorten for user
    stored_messages[message.from_user.id] = {"key": key.decode(), "message": encrypted_message}
    
    bot.send_message(message.chat.id, f"Here Is Your Encrypted Code ➜ ❤️ {message_id} ❤️")

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"{APP_URL}/{TOKEN}")
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
