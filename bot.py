import telebot
import json
import random
import string
import os

TOKEN = "7799355783:AAFn5k3dRB5813vY4TzS-uHCMM4u6nC-i1w"
ADMIN_ID = 6947378236  # Replace with the actual Telegram user ID of the admin
DATA_FILE = "messages.json"

bot = telebot.TeleBot(TOKEN)


# Load messages from file
def load_messages():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    return {}


# Save messages to file
def save_messages(data):
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


# Generate a unique encrypted code
def generate_encrypted_code():
    return ''.join(random.choices(string.digits, k=8))


# Store user messages with unique encrypted code
def store_message(user_id, text):
    messages = load_messages()
    encrypted_code = generate_encrypted_code()
    messages[encrypted_code] = {"user_id": user_id, "message": text}
    save_messages(messages)
    return encrypted_code


@bot.message_handler(commands=["start"])
def start(message):
    """Handle /start command and show options"""
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("Send Message", callback_data="send_message"))
    markup.add(telebot.types.InlineKeyboardButton("Retrieve Message", callback_data="retrieve_message"))
    bot.send_message(
        message.chat.id,
        "💬 *Welcome to the Secret Chat Bot!*\n\n"
        "You can send anonymous messages to the admin or retrieve a response using an encrypted code.\n\n"
        "Choose an option below:",
        parse_mode="Markdown", reply_markup=markup
    )


# Handle button clicks
@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    """Handle inline button actions."""
    if call.data == "send_message":
        msg = bot.send_message(call.message.chat.id, "✉️ *Send me the message:*", parse_mode="Markdown")
        bot.register_next_step_handler(msg, process_message)
    elif call.data == "retrieve_message":
        msg = bot.send_message(call.message.chat.id, "📩 *Enter the encrypted code to retrieve your message:*", parse_mode="Markdown")
        bot.register_next_step_handler(msg, process_retrieve_message)


# Process user message and send to admin
def process_message(message):
    """Store message and send encrypted code."""
    user_id = message.chat.id
    text = message.text.strip()

    if not text:
        bot.send_message(user_id, "❌ Message cannot be empty. Try again.")
        return

    encrypted_code = store_message(user_id, text)
    bot.send_message(user_id, f"✅ *Your message has been sent!*\n\n🔐 Your secret code: `{encrypted_code}`", parse_mode="Markdown")
    admin_text = f"📩 *New Anonymous Message!*\n\n💬 {text}\n\n📬 *Encrypted Code:* `{encrypted_code}`"
    bot.send_message(ADMIN_ID, admin_text, parse_mode="Markdown")


@bot.message_handler(commands=["reply"])
def reply_message(message):
    """Admin replies to a secret message using the encrypted code."""
    if message.chat.id != ADMIN_ID:
        bot.send_message(message.chat.id, "🚫 You are not authorized to use this command.")
        return

    msg = bot.send_message(ADMIN_ID, "✏️ *Enter the encrypted code:*", parse_mode="Markdown")
    bot.register_next_step_handler(msg, get_code)


def get_code(message):
    """Ask for the encrypted code from admin."""
    if message.chat.id != ADMIN_ID:
        bot.send_message(message.chat.id, "🚫 You are not allowed to use this feature.")
        return

    code = message.text.strip()
    messages = load_messages()
    if code in messages:
        user_info = messages[code]
        user_id = user_info["user_id"]
        bot.send_message(ADMIN_ID, f"💬 *Message:* {user_info['message']}\n\n✏️ *Reply with your message:*")
        bot.register_next_step_handler(message, reply_to_user, user_id, code)
    else:
        bot.send_message(message.chat.id, "❌ Invalid code. No message found.")


def process_message(message):
    """Process the message and store it with a unique code."""
    user_id = message.chat.id
    text = message.text.strip()

    if not text:
        bot.send_message(user_id, "❌ Message cannot be empty. Try again.")
        return

    encrypted_code = store_message(user_id, text)
    bot.send_message(user_id, f"✅ *Message Sent!*\n\n📬 *Your Secret Code:* `{encrypted_code}`\n\n"
                     "The admin will use this code to reply to your message.", parse_mode="Markdown")

    admin_text = f"📩 *New Secret Message Received!*\n\n💬 `{text}`\n\n📌 *Encrypted Code:* `{encrypted_code}`\n\n"
    bot.send_message(ADMIN_ID, admin_text, parse_mode="Markdown")


@bot.message_handler(commands=["decrypt"])
def decrypt_message(message):
    """Retrieve the message using an encrypted code."""
    msg = bot.send_message(message.chat.id, "🔓 *Enter the encrypted code to retrieve your message:*", parse_mode="Markdown")
    bot.register_next_step_handler(msg, process_retrieve_message)


def process_retrieve_message(message):
    """Process encrypted code and send message to the user."""
    code = message.text.strip()
    messages = load_messages()

    if code in messages:
        user_id = messages[code]["user_id"]
        message_text = messages[code]["message"]
        bot.send_message(message.chat.id, f"💬 Message Found:\n\n`{message_text}`", parse_mode="Markdown")
        bot.send_message(message.chat.id, "✏️ *Reply to this message to respond:*", parse_mode="Markdown")
        bot.register_next_step_handler_by_chat_id(message.chat.id, send_reply, user_id, message_text)
    else:
        bot.send_message(message.chat.id, "❌ Invalid code. Please check and try again.")

# Handle admin's reply
def process_admin_reply(message):
    reply_text = message.text.strip()
    if not reply_text:
        bot.send_message(message.chat.id, "❌ Reply cannot be empty.")
        return
    
    encrypted_code = message.reply_to_message.text.split("`")[1]
    messages = load_messages()

    if code := messages.get(encrypted_code):
        user_id = code["user_id"]
        bot.send_message(user_id, f"📩 *Reply from Admin:*\n\n💬 {reply_text}", parse_mode="Markdown")
        bot.send_message(message.chat.id, "✅ Your reply has been sent.")

        # Delete message after sending
        del messages[code]
        save_messages(messages)
    else:
        bot.send_message(message.chat.id, "❌ Invalid code. Message not found.")

# Start polling the bot
bot.polling(none_stop=True)
