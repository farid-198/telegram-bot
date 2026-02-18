import telebot
from telebot import types
import sqlite3

TOKEN = "8581414528:AAHImgFvDPlFDN-rRedxIYNc-NrQ_D8IyaU" 
CHANNEL_USERNAME = "@elonreklama3" 
ADMIN_ID = 8577002578  # o'zingizning ID

# ================= SOZLAMALAR =================
ADMIN_USERNAME = "@elon_reklama456"  # reklama uchun

bot = telebot.TeleBot(TOKEN)

# ========= DATABASE =========
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

cursor.execute("""
CREATE TABLE IF NOT EXISTS premium (
    text TEXT
)
""")

conn.commit()

# default reklama
cursor.execute("SELECT * FROM reklama")
if not cursor.fetchone():
    cursor.execute("INSERT INTO reklama (text) VALUES ('Hozircha reklama yo''q')")
    conn.commit()

cursor.execute("SELECT * FROM premium")
if not cursor.fetchone():
    cursor.execute("INSERT INTO premium (text) VALUES ('')")
    conn.commit()

# ========= START =========
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
    markup.add("👥 Referalim", "🏆 Top 5")
    markup.add("📊 Statistika")
    markup.add("💰 Reklama berish")

    cursor.execute("SELECT text FROM reklama")
    reklama_text = cursor.fetchone()[0]

    cursor.execute("SELECT text FROM premium")
    premium_text = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    bot.send_message(message.chat.id,
                     f"""🔥 BONUS BOTGA XUSH KELIBSIZ!

👥 Jami foydalanuvchilar: {total_users}

{premium_text}

🎁 5 ta do‘st = 1 bonus
🎁 10 ta do‘st = 3 bonus
🎁 20 ta do‘st = 10 bonus

📢 Reklama:
{reklama_text}
""", reply_markup=markup)

# ========= REFERAL =========
@bot.message_handler(func=lambda m: m.text == "👥 Referalim")
def referral_menu(message):
    user_id = message.from_user.id
    link = f"https://t.me/{bot.get_me().username}?start={user_id}"

    cursor.execute("SELECT referrals FROM users WHERE user_id=?", (user_id,))
    count = cursor.fetchone()[0]

    if count >= 20:
        bonus = 10
    elif count >= 10:
        bonus = 3
    else:
        bonus = count // 5

    text = f"""🔥 REFERAL BO‘LIMI

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

# ========= TOP =========
@bot.message_handler(func=lambda m: m.text == "🏆 Top 5")
def top_users(message):
    cursor.execute("SELECT user_id, referrals FROM users ORDER BY referrals DESC LIMIT 5")
    top = cursor.fetchall()

    text = "🏆 TOP 5 REFERAL:\n\n"
    for i, user in enumerate(top, start=1):
        text += f"{i}. ID: {user[0]} — {user[1]} ta\n"

    bot.send_message(message.chat.id, text)

# ========= STATISTIKA =========
@bot.message_handler(func=lambda m: m.text == "📊 Statistika")
def stats(message):
    cursor.execute("SELECT COUNT(*) FROM users")
    total = cursor.fetchone()[0]
    bot.send_message(message.chat.id, f"👥 Jami foydalanuvchilar: {total}")

# ========= REKLAMA BUYURTMA =========
@bot.message_handler(func=lambda m: m.text == "💰 Reklama berish")
def reklama_buyurtma(message):
    text = f"""💰 REKLAMA NARXLARI:

1 kun — 20 000 so'm
3 kun — 50 000 so'm

Buyurtma uchun admin:
{ADMIN_USERNAME}
"""
    bot.send_message(message.chat.id, text)

# ========= ADMIN REKLAMA =========
@bot.message_handler(commands=['reklama'])
def add_reklama(message):
    if message.from_user.id == ADMIN_ID:
        new_text = message.text.replace("/reklama ", "")
        cursor.execute("UPDATE reklama SET text=?", (new_text,))
        conn.commit()
        bot.send_message(message.chat.id, "✅ Oddiy reklama yangilandi!")
    else:
        bot.send_message(message.chat.id, "❌ Siz admin emassiz")

# ========= PREMIUM REKLAMA =========
@bot.message_handler(commands=['premium'])
def add_premium(message):
    if message.from_user.id == ADMIN_ID:
        new_text = message.text.replace("/premium ", "")
        cursor.execute("UPDATE premium SET text=?", (new_text,))
        conn.commit()
        bot.send_message(message.chat.id, "🔥 Premium reklama yangilandi!")
    else:
        bot.send_message(message.chat.id, "❌ Siz admin emassiz")

print("Super bot ishga tushdi...")
bot.infinity_polling()










