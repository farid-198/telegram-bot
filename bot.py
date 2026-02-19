import telebot
from telebot import types
import sqlite3

TOKEN = "8581414528:AAHImgFvDPlFDN-rRedxIYNc-NrQ_D8IyaU" 
CHANNEL_USERNAME = "@elonreklama3" 
ADMIN_ID = 8577002578  # o'zingizning ID

# ================= SOZLAMALAR =================
ADMIN_USERNAME = "@elon_reklama456"  # reklama uchun

bot = telebot.TeleBot(TOKEN)
import telebot
from telebot import types
import sqlite3

TOKEN = "SENING_TOKENING"
ADMIN_ID = 123456789
ADMIN_USERNAME = "@SENING_USERNAME"

bot = telebot.TeleBot(TOKEN)

conn = sqlite3.connect("database.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    user_id INTEGER PRIMARY KEY,
    referrals INTEGER DEFAULT 0,
    balance INTEGER DEFAULT 0
)
""")

cursor.execute("CREATE TABLE IF NOT EXISTS reklama(text TEXT)")
cursor.execute("CREATE TABLE IF NOT EXISTS premium(text TEXT)")
conn.commit()

if not cursor.execute("SELECT * FROM reklama").fetchone():
    cursor.execute("INSERT INTO reklama VALUES('Hozircha reklama yo''q')")
    conn.commit()

if not cursor.execute("SELECT * FROM premium").fetchone():
    cursor.execute("INSERT INTO premium VALUES('')")
    conn.commit()

# ===== START =====
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    args = message.text.split()

    if not cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,)).fetchone():
        cursor.execute("INSERT INTO users(user_id) VALUES(?)", (user_id,))
        conn.commit()

        if len(args) > 1:
            try:
                ref_id = int(args[1])
                if ref_id != user_id:
                    cursor.execute("""
                        UPDATE users 
                        SET referrals = referrals + 1,
                            balance = balance + 1000
                        WHERE user_id=?
                    """, (ref_id,))
                    conn.commit()

                    count = cursor.execute(
                        "SELECT referrals FROM users WHERE user_id=?",
                        (ref_id,)
                    ).fetchone()[0]

                    if count in [5,10,20]:
                        bot.send_message(ref_id,
                            f"🎉 Tabriklaymiz! {count} ta referalga yetdingiz!")
            except:
                pass

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("👥 Referalim","🏆 Top 5")
    markup.add("📊 Statistika","💳 Balans")
    markup.add("💰 Reklama berish","💸 Pul yechish")

    if user_id == ADMIN_ID:
        markup.add("⚙️ Admin Panel")

    total = cursor.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    reklama = cursor.execute("SELECT text FROM reklama").fetchone()[0]
    premium = cursor.execute("SELECT text FROM premium").fetchone()[0]

    bot.send_message(message.chat.id,
f"""🔥 SUPER BONUS BOT

👥 Jami foydalanuvchilar: {total}

{premium}

🎁 Har referal = 1000 so'm

📢 Reklama:
{reklama}
""", reply_markup=markup)

# ===== REFERAL =====
@bot.message_handler(func=lambda m: m.text=="👥 Referalim")
def ref(message):
    link = f"https://t.me/{bot.get_me().username}?start={message.from_user.id}"
    count = cursor.execute(
        "SELECT referrals FROM users WHERE user_id=?",
        (message.from_user.id,)
    ).fetchone()[0]

    bot.send_message(message.chat.id,
f"""👥 Takliflar: {count}

🔗 Linking:
{link}
""")

# ===== BALANS =====
@bot.message_handler(func=lambda m: m.text=="💳 Balans")
def balans(message):
    bal = cursor.execute(
        "SELECT balance FROM users WHERE user_id=?",
        (message.from_user.id,)
    ).fetchone()[0]

    bot.send_message(message.chat.id,f"💰 Balans: {bal} so'm")

# ===== PUL YECHISH =====
@bot.message_handler(func=lambda m: m.text=="💸 Pul yechish")
def withdraw(message):
    bal = cursor.execute(
        "SELECT balance FROM users WHERE user_id=?",
        (message.from_user.id,)
    ).fetchone()[0]

    if bal < 10000:
        bot.send_message(message.chat.id,
            "❌ Minimal yechish 10 000 so'm")
    else:
        bot.send_message(message.chat.id,
            "💳 Karta raqamingizni yuboring:")
        bot.register_next_step_handler(message, process_card)

def process_card(message):
    user_id = message.from_user.id
    card = message.text

    bal = cursor.execute(
        "SELECT balance FROM users WHERE user_id=?",
        (user_id,)
    ).fetchone()[0]

    bot.send_message(ADMIN_ID,
f"""💸 Yangi yechish so‘rovi

User: {user_id}
Balans: {bal}
Karta: {card}
""")

    bot.send_message(user_id,
        "✅ So‘rov yuborildi. Admin tekshiradi.")

# ===== TOP =====
@bot.message_handler(func=lambda m: m.text=="🏆 Top 5")
def top(message):
    users = cursor.execute(
        "SELECT user_id, referrals FROM users ORDER BY referrals DESC LIMIT 5"
    ).fetchall()

    text="🏆 TOP 5:\n\n"
    for i,u in enumerate(users,1):
        try:
            name = bot.get_chat(u[0]).first_name
        except:
            name = u[0]
        text+=f"{i}. {name} — {u[1]} ta\n"

    bot.send_message(message.chat.id,text)

# ===== STAT =====
@bot.message_handler(func=lambda m: m.text=="📊 Statistika")
def stat(message):
    total = cursor.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    bot.send_message(message.chat.id,
        f"👥 Jami foydalanuvchilar: {total}")

# ===== REKLAMA =====
@bot.message_handler(func=lambda m: m.text=="💰 Reklama berish")
def reklama(message):
    bot.send_message(message.chat.id,
f"""💰 Narxlar:

Oddiy — 20 000 so'm
Premium — 50 000 so'm

Admin: {ADMIN_USERNAME}
""")

# ===== ADMIN PANEL =====
@bot.message_handler(func=lambda m: m.text=="⚙️ Admin Panel")
def admin(message):
    if message.from_user.id==ADMIN_ID:
        bot.send_message(message.chat.id,
"""⚙️ Buyruqlar:
/reklama matn
/premium matn
/broadcast xabar
""")

@bot.message_handler(commands=['reklama'])
def setrek(message):
    if message.from_user.id==ADMIN_ID:
        text=message.text.replace("/reklama ","")
        cursor.execute("UPDATE reklama SET text=?", (text,))
        conn.commit()
        bot.send_message(message.chat.id,"✅ Yangilandi")

@bot.message_handler(commands=['premium'])
def setpre(message):
    if message.from_user.id==ADMIN_ID:
        text=message.text.replace("/premium ","")
        cursor.execute("UPDATE premium SET text=?", (text,))
        conn.commit()
        bot.send_message(message.chat.id,"🔥 Premium yangilandi")

@bot.message_handler(commands=['broadcast'])
def bc(message):
    if message.from_user.id==ADMIN_ID:
        text=message.text.replace("/broadcast ","")
        users=cursor.execute("SELECT user_id FROM users").fetchall()
        for u in users:
            try:
                bot.send_message(u[0],text)
            except:
                pass
        bot.send_message(message.chat.id,"✅ Yuborildi")

print("FINAL BOT ISHLADI")
bot.infinity_polling()





