import telebot
from telebot import types
import sqlite3

TOKEN = "8581414528:AAHImgFvDPlFDN-rRedxIYNc-NrQ_D8IyaU" 
CHANNEL_USERNAME = "@elonreklama3" 
ADMIN_ID = 8577002578  # o'zingizning ID

# ================= SOZLAMALAR =================
ADMIN_USERNAME = "@elon_reklama456"  # reklama uchun

bot = telebot.TeleBot(TOKEN)

# ====== DATABASE ======
conn = sqlite3.connect("database.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    referrals INTEGER DEFAULT 0
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS reklama (
    text TEXT
)
""")

conn.commit()

# default reklama
cursor.execute("SELECT * FROM reklama")
if not cursor.fetchone():
    cursor.execute("INSERT INTO reklama (text) VALUES ('Hozircha reklama yo''q')")
    conn.commit()

# ====== START ======
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    args = message.text.split()

    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = cursor.fetchone()

    if not user:
        cursor.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
        conn.commit()

        if len(args) > 1:
            try:
                ref_id = int(args[1])
                if ref_id != user_id:
                    cursor.execute("UPDATE users SET referrals = referrals + 1 WHERE user_id=?", (ref_id,))
                    conn.commit()
            except:
                pass

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("👥 Referalim")
    markup.add("💰 Reklama berish")
    markup.add("🏆 Top 5")

    cursor.execute("SELECT text FROM reklama")
    reklama_text = cursor.fetchone()[0]

    bot.send_message(message.chat.id,
                     f"""🔥 BONUS BOTGA XUSH KELIBSIZ!

🎁 5 ta do‘st taklif qil → 1 BONUS

📢 Reklama:
{reklama_text}
""", reply_markup=markup)

# ====== REFERAL ======
@bot.message_handler(func=lambda m: m.text == "👥 Referalim")
def referral_menu(message):
    user_id = message.from_user.id
    link = f"https://t.me/{bot.get_me().username}?start={user_id}"

    cursor.execute("SELECT referrals FROM users WHERE user_id=?", (user_id,))
    count = cursor.fetchone()[0]

    bonus = count // 5

    text = f"""🔥 DO‘STLARINGGA ULASHING!

👥 Takliflar: {count}
🎁 Bonuslar: {bonus}

🔗 Sening linking:
{link}
"""

    markup = types.InlineKeyboardMarkup()
    share_btn = types.InlineKeyboardButton(
        "📣 Do‘stlarga ulashish",
        url=f"https://t.me/share/url?url={link}"
    )
    markup.add(share_btn)

    bot.send_message(message.chat.id, text, reply_markup=markup)

# ====== TOP 5 ======
@bot.message_handler(func=lambda m: m.text == "🏆 Top 5")
def top_users(message):
    cursor.execute("SELECT user_id, referrals FROM users ORDER BY referrals DESC LIMIT 5")
    top = cursor.fetchall()

    text = "🏆 TOP 5 REFERAL:\n\n"
    for i, user in enumerate(top, start=1):
        text += f"{i}. ID: {user[0]} — {user[1]} ta\n"

    bot.send_message(message.chat.id, text)

# ====== REKLAMA BERISH ======
@bot.message_handler(func=lambda m: m.text == "💰 Reklama berish")
def reklama_buyurtma(message):
    text = f"""💰 REKLAMA NARXLARI:

1 kun — 15 000 so'm
3 kun — 35 000 so'm

Buyurtma uchun admin:
{ADMIN_USERNAME}
"""
    bot.send_message(message.chat.id, text)

# ====== ADMIN REKLAMA QO'SHISH ======
@bot.message_handler(commands=['reklama'])
def add_reklama(message):
    if message.from_user.id == ADMIN_ID:
        new_text = message.text.replace("/reklama ", "")
        cursor.execute("UPDATE reklama SET text=?", (new_text,))
        conn.commit()
        bot.send_message(message.chat.id, "✅ Reklama yangilandi!")
    else:
        bot.send_message(message.chat.id, "❌ Siz admin emassiz")

print("Bot ishga tushdi...")
bot.infinity_polling()







