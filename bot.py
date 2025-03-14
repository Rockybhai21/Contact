import telebot
import json
import random
import string

TOKEN = "YOUR_BOT_TOKEN"
ADMIN_ID = YOUR_ADMIN_TELEGRAM_ID  # Replace with the actual admin user ID
DATA_FILE = "messages.json"

bot = telebot.TeleBot(TOKEN)

# Load messages from file
def load_messages():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# Save messages to a JSON file
def save_messages(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

# Generate a unique encrypted code
def generate_encrypted_code():
    return ''.join(random.choices(string.digits, k=8))

# Store user messages with unique encrypted code
def store_message(user_id, message):
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}

    encrypted_code = generate_encrypted_code()
    data[encrypted_code] = {"user_id": user_id, "message": message}

    save_messages(data)
    return encrypted_code

# Handle the start command
@bot.message_handler(commands=["start"])
def start(message):
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("📩 Send Message", callback_data="send_message"))
    markup.add(telebot.types.InlineKeyboardButton("📩 Receive Message", callback_data="receive_message"))
    markup.add(telebot.types.InlineKeyboardButton(text="🔒 Password Protected Message", callback_data="password_protect"))
    markup.add(telebot.types.InlineKeyboardButton("📊 Statistics", callback_data="stats"))

    bot.send_message(
        message.chat.id, 
        "💬 *Welcome to Anonymous Chat Bot!*\n\n"
        "You can send anonymous messages to the admin or receive messages securely.\n\n"
        "*Choose an option below:*",
        parse_mode="Markdown",
        reply_markup=markup
    )

# Handle inline buttons
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "send_message":
        msg = bot.send_message(call.message.chat.id, "✉️ *Send Me The Message*", parse_mode="Markdown")
        bot.register_next_step_handler(msg, process_message)
    elif call.data == "receive_message":
        bot.send_message(call.message.chat.id, "📩 *Enter the encrypted code to retrieve your message:*", parse_mode="Markdown")
        bot.register_next_step_handler(call.message, process_retrieve_message)
    elif call.data == "stats":
        bot.send_message(call.message.chat.id, "📊 *Bot Statistics:*\n\n👥 Total Users: *90*\n\n✌️ _Coded by_ @Bot_hub_telegram", parse_mode="Markdown")

# Process user message
def process_message(message):
    user_id = message.chat.id
    text = message.text.strip()

    if not text:
        bot.send_message(user_id, "❌ Message cannot be empty. Try again.")
        return

    encrypted_code = generate_encrypted_code()
    
    data = load_messages()
    data[encrypted_code] = {"user_id": user_id, "message": text}
    save_messages(data)

    bot.send_message(user_id, f"🔐 *Here Is Your Encrypted Code ➜* ❤️ `{encrypted_code}` ❤️", parse_mode="Markdown")
    admin_text = f"📩 *New Anonymous Message!*\n\n💬 {text}\n\n📬 *Encrypted Code:* `{encrypted_code}`"
    bot.send_message(ADMIN_ID, admin_text, parse_mode="Markdown")

# Retrieve messages
@bot.message_handler(commands=["receive_message"])
def receive_message_command(message):
    markup = telebot.types.ForceReply(selective=True)
    bot.send_message(
        message.chat.id, 
        "📨 *Send me the encrypted code you received:*", 
        parse_mode="Markdown", reply_markup=markup
    )

@bot.message_handler(func=lambda message: message.reply_to_message is not None and "Enter the encrypted code" in message.reply_to_message.text)
def retrieve_message(message):
    code = message.text.strip()

    try:
        with open(DATA_FILE, "r") as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}

    if code in data:
        msg_text = data[code]["message"]
        del data[code]
        
        with open(DATA_FILE, "w") as file:
            json.dump(data, file)
        
        bot.send_message(message.chat.id, f"📩 *Your message:* {message.text}", parse_mode="Markdown")
        bot.send_message(message.chat.id, f"💌 *Your Secret Message:*\n\n`{data.get(code, 'Message not found!')}`", parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, "❌ Invalid code. Please check again.")

# Run bot in polling mode
if __name__ == "__main__":
    bot.polling(none_stop=True, timeout=30)
