import os
import telebot
from flask import Flask, request

# Load Environment Variables
TOKEN = os.getenv("BOT_TOKEN")  # Telegram Bot Token
APP_URL = os.getenv("APP_URL")  # Render App URL
ADMIN_IDS = os.getenv("ADMIN_IDS", "").split(",")  # Multi-Admin Support

# Initialize Bot
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Start Command
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    bot.reply_to(message, f"Hello {message.from_user.first_name}! 👋\nI'm here to help you communicate easily.")

# Handle Messages
@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    user_id = message.from_user.id
    text = message.text
    bot.reply_to(message, f"📩 You said: {text}")

# Admin Command: Broadcast Message
@bot.message_handler(commands=['broadcast'])
def broadcast(message):
    if str(message.from_user.id) not in ADMIN_IDS:
        bot.reply_to(message, "❌ You are not an admin!")
        return

    text = message.text.replace("/broadcast ", "")
    if not text:
        bot.reply_to(message, "⚠️ Please provide a message to broadcast.")
        return

    bot.send_message(message.chat.id, f"📢 Broadcasting: {text}")

# Webhook Endpoint
@app.route(f"/{TOKEN}", methods=['POST'])
def webhook():
    json_str = request.get_data().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200

# Root Endpoint
@app.route("/")
def index():
    return "🤖 Bot is running!"

# Set Webhook on Startup
if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"{APP_URL}/{TOKEN}")
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
