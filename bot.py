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

cursor.execute("CREATE TABLE IF NOT EXISTS reklama (text TEXT)")
cursor.execute("CREATE TABLE IF NOT EXISTS premium (text TEXT)")
conn.commit()

# default values
cursor.execute("SELECT * FROM reklama")
if not cursor.fetchone():
    cursor.execute("INSERT INTO reklama VALUES ('Hozircha reklama yo''q')")
    conn.commit()

cursor.execute("SELECT * FROM premium")
if not cursor.fetchone():
    cursor.execute("INSERT INTO premium VALUES ('')")
    conn.commit()

# ====== START ======
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    args = message.text.split()

    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = cursor.fetchone()

    if not user:
        cursor.execute("INSERT INTO users VALUES (?,0)", (user_id,))
        conn.commit()

        if len(args) > 1:
            try:
                ref_id = int(args[1])
                if ref_id != user_id:
                    cursor.execute("UPDATE users SET referrals = referrals + 1 WHERE user_id=?", (ref_id,))
                    conn.commit()

                    cursor.execute("SELECT referrals FROM users WHERE user_id=?", (ref_id,))
                    ref_count = cursor.fetchone()[0]

                    if ref_count in [5,10,20]:
                        bot.send_message(ref_id,
                            f"🎉 Tabriklaymiz! Siz {ref_count} ta referalga yetdingiz!")
            except:
                pass

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("👥 Referalim", "🏆 Top 5")
    markup.add("📊 Statistika", "💰 Reklama berish")

    if user_id == ADMIN_ID:
        markup.add("⚙️ Admin Panel")

    cursor.execute("SELECT COUNT(*) FROM users")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT text FROM premium")
    premium_text = cursor.fetchone()[0]

    cursor.execute("SELECT text FROM reklama")
    reklama_text = cursor.fetchone()[0]

    bot.send_message(message.chat.id,
        f"""🔥 BONUS BOTGA XUSH KELIBSIZ!

👥 Jami foydalanuvchilar: {total}

{premium_text}

🎁 5 = 1 bonus
🎁 10 = 3 bonus
🎁 20 = 10 bonus

📢 Reklama:
{reklama_text}
""", reply_markup=markup)

# ====== REFERAL ======
@bot.message_handler(func=lambda m: m.text == "👥 Referalim")
def referral(message):
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

    bot.send_message(message.chat.id,
        f"""👥 Takliflar: {count}
🎁 Bonuslar: {bonus}

🔗 Linking:
{link}
""")

# ====== TOP ======
@bot.message_handler(func=lambda m: m.text == "🏆 Top 5")
def top(message):
    cursor.execute("SELECT user_id, referrals FROM users ORDER BY referrals DESC LIMIT 5")
    top_users = cursor.fetchall()

    text = "🏆 TOP 5:\n\n"
    for i, user in enumerate(top_users, start=1):
        try:
            chat = bot.get_chat(user[0])
            name = chat.first_name
        except:
            name = user[0]
        text += f"{i}. {name} — {user[1]} ta\n"

    bot.send_message(message.chat.id, text)

# ====== STATISTIKA ======
@bot.message_handler(func=lambda m: m.text == "📊 Statistika")
def stat(message):
    cursor.execute("SELECT COUNT(*) FROM users")
    total = cursor.fetchone()[0]
    bot.send_message(message.chat.id, f"👥 Jami foydalanuvchilar: {total}")

# ====== REKLAMA ======
@bot.message_handler(func=lambda m: m.text == "💰 Reklama berish")
def reklama(message):
    bot.send_message(message.chat.id,
        f"""💰 NARXLAR:

Oddiy — 20 000 so'm
Premium — 50 000 so'm

Admin:
{ADMIN_USERNAME}
""")

# ====== ADMIN PANEL ======
@bot.message_handler(func=lambda m: m.text == "⚙️ Admin Panel")
def admin_panel(message):
    if message.from_user.id == ADMIN_ID:
        bot.send_message(message.chat.id,
            """⚙️ Admin buyruqlar:

/reklama matn
/premium matn
/broadcast xabar
""")

# ====== ADMIN REKLAMA ======
@bot.message_handler(commands=['reklama'])
def set_reklama(message):
    if message.from_user.id == ADMIN_ID:
        text = message.text.replace("/reklama ","")
        cursor.execute("UPDATE reklama SET text=?", (text,))
        conn.commit()
        bot.send_message(message.chat.id,"✅ Oddiy reklama yangilandi")

@bot.message_handler(commands=['premium'])
def set_premium(message):
    if message.from_user.id == ADMIN_ID:
        text = message.text.replace("/premium ","")
        cursor.execute("UPDATE premium SET text=?", (text,))
        conn.commit()
        bot.send_message(message.chat.id,"🔥 Premium reklama yangilandi")

# ====== BROADCAST ======
@bot.message_handler(commands=['broadcast'])
def broadcast(message):
    if message.from_user.id == ADMIN_ID:
        text = message.text.replace("/broadcast ","")
        cursor.execute("SELECT user_id FROM users")
        users = cursor.fetchall()

        for user in users:
            try:
                bot.send_message(user[0], text)
            except:
                pass

        bot.send_message(message.chat.id,"✅ Xabar yuborildi")

print("ULTRA BOT ishga tushdi...")
bot.infinity_polling()
