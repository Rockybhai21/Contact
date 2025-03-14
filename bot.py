"""
Telegram Bot for Anonymous Chat Between Users and Admin.

Features:
- Users send messages to the bot.
- Admin receives user messages and can reply anonymously.
- Admin's reply is sent back to the correct user.
- Supports text, images, videos, and voice messages.
- Persistent message tracking using a JSON file.

Author: [Your Name]
"""

import os
import json
import telebot

# Load secrets
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")
DATA_FILE = "messages.json"

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is missing! Please set it as a GitHub Secret.")
if not ADMIN_ID:
    raise ValueError("ADMIN_ID is missing! Please set it as a GitHub Secret.")

ADMIN_ID = int(ADMIN_ID)  # Convert to integer
bot = telebot.TeleBot(BOT_TOKEN)


# Load previous messages if available
def load_messages():
    """Load message mappings from JSON file."""
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}  # Return empty dictionary if file is missing or invalid


def save_messages(data):
    """Save message mappings to JSON file."""
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


message_tracker = load_messages()


@bot.message_handler(func=lambda message: message.chat.id != ADMIN_ID)
def handle_user_message(message):
    """
    Handles messages from users and forwards them to the admin.
    - Stores user ID and message ID mapping.
    - Supports text, photos, videos, and voice messages.
    """
    user_id = message.chat.id
    user_name = message.from_user.first_name or "User"
    
    if message.text:
        user_text = message.text
        sent_msg = bot.send_message(
            ADMIN_ID,
            f"📩 New Message from <b>{user_name} ({user_id})</b>:\n\n{user_text}",
            parse_mode="HTML",
        )
    elif message.photo:
        sent_msg = bot.send_photo(
            ADMIN_ID, message.photo[-1].file_id,
            caption=f"📷 Photo from <b>{user_name} ({user_id})</b>",
            parse_mode="HTML"
        )
    elif message.video:
        sent_msg = bot.send_video(
            ADMIN_ID, message.video.file_id,
            caption=f"🎥 Video from <b>{user_name} ({user_id})</b>",
            parse_mode="HTML"
        )
    elif message.voice:
        sent_msg = bot.send_voice(
            ADMIN_ID, message.voice.file_id,
            caption=f"🎤 Voice message from <b>{user_name} ({user_id})</b>",
            parse_mode="HTML"
        )
    else:
        bot.send_message(user_id, "⚠️ Unsupported message type.")

        return

    # Store the message mapping
    message_tracker[str(sent_msg.message_id)] = user_id
    save_messages(message_tracker)  # Save data


@bot.message_handler(func=lambda message: message.chat.id == ADMIN_ID and message.reply_to_message)
def handle_admin_reply(message):
    """
    Handles admin replies and sends them back to the correct user.
    """
    reply_to_msg_id = str(message.reply_to_message.message_id)
    reply_text = message.text

    if reply_to_msg_id in message_tracker:
        user_id = message_tracker[reply_to_msg_id]

        if message.text:
            bot.send_message(user_id, f"💬 Reply from Admin:\n\n{reply_text}")
        elif message.photo:
            bot.send_photo(user_id, message.photo[-1].file_id, caption="📷 Reply from Admin")
        elif message.video:
            bot.send_video(user_id, message.video.file_id, caption="🎥 Reply from Admin")
        elif message.voice:
            bot.send_voice(user_id, message.voice.file_id, caption="🎤 Reply from Admin")

        bot.send_message(ADMIN_ID, "✅ Message sent to user successfully!")
    else:
        bot.send_message(ADMIN_ID, "⚠️ This message is not linked to a user.")


# Start the bot
if __name__ == "__main__":
    bot.polling(none_stop=True)
