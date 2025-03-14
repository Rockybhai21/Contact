import os
import telebot

# Load Environment Variables
TOKEN = os.getenv("BOT_TOKEN")  # Telegram Bot Token
ADMIN_IDS = os.getenv("ADMIN_IDS", "").split(",")  # Multi-Admin Support

# Initialize Bot
bot = telebot.TeleBot(TOKEN)

# Start Command
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, f"Hello {message.from_user.first_name}! 👋\nI'm here to help you communicate easily.")

# Handle Messages
@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    bot.reply_to(message, f"📩 You said: {message.text}")

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

# Start the bot using polling mode
if __name__ == "__main__":
    bot.remove_webhook()  # Ensure no webhook is set
    bot.polling(none_stop=True)
