"""
Telegram Bot for Anonymous Chat Between Users and Admin.

Features:
- Users can send messages to the bot.
- Admin receives user messages and can reply anonymously.
- Admin's reply is sent back to the correct user.

Author: [Your Name]
"""

import os
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

# Dictionary to track messages (User ID ↔ Message ID)
message_tracker = {}

def start_bot():
    """Starts the bot and handles messages."""
    
    @bot.message_handler(func=lambda message: message.chat.id != ADMIN_ID)
    def handle_user_message(message):
        """
        Handles messages from users.
        - Stores the user ID and forwards the message to the admin.
        """
        user_id = message.chat.id
        user_text = message.text

        # Forward message to admin
        sent_msg = bot.send_message(
            ADMIN_ID,
            f"📩 New Message from <b>{user_id}</b>:\n\n{user_text}",
            parse_mode="HTML",
        )

        # Store the message ID mapping (User ID ↔ Message ID)
        message_tracker[sent_msg.message_id] = user_id

    @bot.message_handler(func=lambda message: message.chat.id == ADMIN_ID and message.reply_to_message)
    def handle_admin_reply(message):
        """
        Handles admin replies.
        - Sends the admin's reply back to the correct user.
        """
        reply_to_msg_id = message.reply_to_message.message_id
        reply_text = message.text

        # Check if the message is a reply to a tracked user message
        if reply_to_msg_id in message_tracker:
            user_id = message_tracker[reply_to_msg_id]

            # Send admin's reply to the user
            bot.send_message(user_id, f"💬 Reply from Admin:\n\n{reply_text}")

            # Notify admin about successful delivery
            bot.send_message(ADMIN_ID, "✅ Message sent to user successfully!")
        else:
            bot.send_message(ADMIN_ID, "⚠️ This message is not linked to a user.")

    bot.polling(none_stop=True)

if __name__ == "__main__":
    start_bot()
