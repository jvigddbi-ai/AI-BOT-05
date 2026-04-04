import telebot
from telebot import types
import random
import time
from flask import Flask
from threading import Thread

# ================= CONFIGURATION =================
# अपना असली टेलीग्राम टोकन नीचे सिंगल कोट्स के बीच डालें
API_TOKEN = '8382219456:AAEIDFCwzbeDj22RCR8QYQTSzdLPPayxt6I' 

# अपने टेलीग्राम चैनल का यूजरनेम यहाँ डालें (@ के साथ)
CHANNELS = ['@MANOFGET', '@MANOFGET'] 

# अपनी टेलीग्राम ID यहाँ डालें (पॉइंट्स ऐड करने के लिए)
# अपनी ID जानने के लिए टेलीग्राम पर @userinfobot पर मैसेज करें
ADMIN_ID = 123456789 
# =================================================

bot = telebot.TeleBot(API_TOKEN)
server = Flask('')

@server.route('/')
def home():
    return "Bot is Active!"

def run():
    server.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# User Data Storage
user_data = {}

def check_join(user_id):
    """चेक करता है कि यूजर ने चैनल जॉइन किया है या नहीं"""
    for channel in CHANNELS:
        try:
            status = bot.get_chat_member(channel, user_id).status
            if status == 'left':
                return False
        except Exception:
            return False
    return True

@bot.message_handler(commands=['start'])
def welcome(message):
    uid = message.chat.id
    if uid not in user_data:
        user_data[uid] = {'points': 100, 'level': 1}
    
    if not check_join(uid):
        markup = types.InlineKeyboardMarkup()
        for ch in CHANNELS:
            markup.add(types.InlineKeyboardButton(text=f"Join {ch}", url=f"https://t.me/{ch.replace('@','')}"))
        markup.add(types.InlineKeyboardButton(text="✅ Check Joined", callback_data="verify"))
        
        bot.send_message(uid, "🚫 **Access Denied!**\n\nप्रेडिक्शन शुरू करने के लिए पहले हमारे चैनल्स जॉइन करें।", reply_markup=markup, parse_mode="Markdown")
    else:
        show_menu(uid)

def show_menu(uid):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🔮 Wingo 1M", "🔮 Wingo 30S")
    markup.add("💰 My Points", "📊 Status")
    bot.send_message(uid, f"👋 **Welcome!**\nPoints: {user_data[uid]['points']}\n\nSelect a Game:", reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text in ["🔮 Wingo 1M", "🔮 Wingo 30S"])
def start_prediction(message):
    uid = message.chat.id
    if not check_join(uid): return welcome(message)
    
    if user_data[uid]['points'] <= 0:
        bot.send_message(uid, "❌ आपके पॉइंट्स खत्म हो गए हैं! कल फिर से 100 पॉइंट्स मिल जाएंगे।")
        return

    # Subtract Point
    user_data[uid]['points'] -= 1
    
    # Prediction Calculation
    game = message.text
    period = time.strftime("%Y%m%d") + "100" + str(random.randint(100, 999))
    result = random.choice(["BIG", "SMALL"])
    nums = "6,7,8,9" if result == "BIG" else "0,1,2,3"
    sticker = random.choice(["WIN ✅", "LOSS ❌", "JACKPOT 🔥"])
    
    # Level Logic
    current_level = user_data[uid]['level']
    if "LOSS" in sticker:
        user_data[uid]['level'] += 1
    else:
        user_data[uid]['level'] = 1

    msg = f"""
🎮 **{game} PREDICTION**
━━━━━━━━━━━━━━━━━━
📅 **PERIOD:** `{period}`
🎯 **RESULT:** `{result}`
🔢 **NUMBER:** `{nums}`
📈 **LEVEL:** `{current_level}`
━━━━━━━━━━━━━━━━━━
{sticker}
Remaining Points: {user_data[uid]['points']}
    """
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("NEXT ⏩", callback_data="next_pred"))
    bot.send_message(uid, msg, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    uid = call.from_user.id
    if call.data == "verify":
        if check_join(uid):
            bot.answer_callback_query(call.id, "Verified!")
            show_menu(uid)
        else:
            bot.answer_callback_query(call.id, "❌ आपने जॉइन नहीं किया!", show_alert=True)
    elif call.data == "next_pred":
        bot.send_message(uid, "कृपया फिर से गेम बटन दबाएं।")

@bot.message_handler(commands=['add100'])
def admin_add(message):
    if message.chat.id == ADMIN_ID:
        uid = message.chat.id
        if uid not in user_data: user_data[uid] = {'points': 0, 'level': 1}
        user_data[uid]['points'] += 100
        bot.send_message(uid, "✅ 100 Points Added Successfully!")

@bot.message_handler(func=lambda m: m.text == "💰 My Points")
def check_pts(message):
    uid = message.chat.id
    pts = user_data.get(uid, {}).get('points', 0)
    bot.send_message(uid, f"💰 Your Current Points: **{pts}**", parse_mode="Markdown")

if __name__ == "__main__":
    keep_alive() # Render को जगाए रखने के लिए
    print("Bot is starting...")
    bot.polling(none_stop=True)
