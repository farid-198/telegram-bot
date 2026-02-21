import telebot
from telebot import types
import sqlite3
import time
TOKEN = "8581414528:AAHImgFvDPlFDN-rRedxIYNc-NrQ_D8IyaU"  
ADMIN_ID = 8577002578  # o'zingizning ID

ADMIN_USERNAME = "@elon_reklama456"  # reklama uchun
bot = telebot.TeleBot(TOKEN)

conn = sqlite3.connect("database.db", check_same_thread=False)
cursor = conn.cursor()

# ===== DATABASE =====
cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    user_id INTEGER PRIMARY KEY,
    referrals INTEGER DEFAULT 0,
    balance INTEGER DEFAULT 0,
    referred_by INTEGER DEFAULT NULL,
    vip INTEGER DEFAULT 0
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS withdrawals(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    amount INTEGER,
    card TEXT,
    status TEXT DEFAULT 'pending'
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS premium(
    text TEXT,
    expire INTEGER
)
""")

cursor.execute("CREATE TABLE IF NOT EXISTS reklama(text TEXT)")
conn.commit()

if not cursor.execute("SELECT * FROM reklama").fetchone():
    cursor.execute("INSERT INTO reklama VALUES('Hozircha reklama yo''q')")
    conn.commit()

if not cursor.execute("SELECT * FROM premium").fetchone():
    cursor.execute("INSERT INTO premium VALUES('',0)")
    conn.commit()

# ===== START =====
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    username = message.from_user.username
    args = message.text.split()

    user = cursor.execute("SELECT * FROM users WHERE user_id=?",(user_id,)).fetchone()

    if not user:
        referred_by = None

        if len(args) > 1 and username:
            try:
                ref_id = int(args[1])
                if ref_id != user_id:
                    if cursor.execute("SELECT * FROM users WHERE user_id=?",(ref_id,)).fetchone():
                        referred_by = ref_id

                        ref_data = cursor.execute(
                            "SELECT referrals,vip FROM users WHERE user_id=?",
                            (ref_id,)
                        ).fetchone()

                        referrals = ref_data[0]
                        vip = ref_data[1]

                        reward = 1500 if vip else 1000

                        cursor.execute("""
                            UPDATE users
                            SET referrals=referrals+1,
                                balance=balance+?
                            WHERE user_id=?
                        """,(reward,ref_id))
                        conn.commit()

                        new_count = referrals + 1

                        if new_count >= 20:
                            cursor.execute("UPDATE users SET vip=1 WHERE user_id=?",(ref_id,))
                            conn.commit()

                        if new_count in [5,10,20]:
                            bot.send_message(ref_id,
                                f"🎉 {new_count} ta referalga yetdingiz!")

            except:
                pass

        cursor.execute("""
            INSERT INTO users(user_id,referred_by)
            VALUES(?,?)
        """,(user_id,referred_by))
        conn.commit()

    # ===== PREMIUM CHECK =====
    premium = cursor.execute("SELECT text,expire FROM premium").fetchone()
    premium_text = premium[0]
    expire = premium[1]

    if time.time() > expire:
        premium_text = ""

    total = cursor.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    reklama = cursor.execute("SELECT text FROM reklama").fetchone()[0]

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("👥 Referalim","🏆 Top 5")
    markup.add("📊 Statistika","💳 Balans")
    markup.add("💸 Pul yechish","💰 Reklama berish")

    if user_id == ADMIN_ID:
        markup.add("⚙️ Admin Panel")

    bot.send_message(message.chat.id,
f"""🔥 BUSINESS BONUS BOT

👥 Jami foydalanuvchilar: {total}

{premium_text}

🎁 Oddiy: 1000 so'm
💎 VIP: 1500 so'm

📢 Reklama:
{reklama}
""",reply_markup=markup)

# ===== BALANS =====
@bot.message_handler(func=lambda m: m.text=="💳 Balans")
def balans(message):
    bal = cursor.execute("SELECT balance FROM users WHERE user_id=?",
        (message.from_user.id,)).fetchone()[0]
    bot.send_message(message.chat.id,f"💰 Balans: {bal} so'm")

# ===== WITHDRAW =====
@bot.message_handler(func=lambda m: m.text=="💸 Pul yechish")
def withdraw(message):
    user_id = message.from_user.id
    bal = cursor.execute("SELECT balance FROM users WHERE user_id=?",
        (user_id,)).fetchone()[0]

    pending = cursor.execute("""
        SELECT * FROM withdrawals
        WHERE user_id=? AND status='pending'
    """,(user_id,)).fetchone()

    if pending:
        bot.send_message(message.chat.id,"⏳ Oldingi so‘rov ko‘rib chiqilmoqda")
        return

    if bal < 10000:
        bot.send_message(message.chat.id,"❌ Minimal 10 000 so'm")
        return

    bot.send_message(message.chat.id,"💳 Karta raqamingizni yuboring:")
    bot.register_next_step_handler(message,process_card)

def process_card(message):
    user_id = message.from_user.id
    card = message.text

    bal = cursor.execute("SELECT balance FROM users WHERE user_id=?",
        (user_id,)).fetchone()[0]

    cursor.execute("""
        INSERT INTO withdrawals(user_id,amount,card)
        VALUES(?,?,?)
    """,(user_id,bal,card))
    conn.commit()

    bot.send_message(ADMIN_ID,
f"""💸 So‘rov

User: {user_id}
Summa: {bal}
Karta: {card}

Tasdiqlash:
/approve_{user_id}

Rad:
/reject_{user_id}
""")

    bot.send_message(user_id,"✅ So‘rov yuborildi")

# ===== ADMIN APPROVE =====
@bot.message_handler(func=lambda m: m.text.startswith("/approve_"))
def approve(message):
    if message.from_user.id==ADMIN_ID:
        uid=int(message.text.split("_")[1])
        cursor.execute("UPDATE users SET balance=0 WHERE user_id=?",(uid,))
        cursor.execute("UPDATE withdrawals SET status='approved' WHERE user_id=?",(uid,))
        conn.commit()
        bot.send_message(uid,"✅ To‘lov tasdiqlandi")

@bot.message_handler(func=lambda m: m.text.startswith("/reject_"))
def reject(message):
    if message.from_user.id==ADMIN_ID:
        uid=int(message.text.split("_")[1])
        cursor.execute("UPDATE withdrawals SET status='rejected' WHERE user_id=?",(uid,))
        conn.commit()
        bot.send_message(uid,"❌ Rad etildi")

# ===== ADMIN PANEL =====
@bot.message_handler(func=lambda m: m.text=="⚙️ Admin Panel")
def admin_panel(message):
    if message.from_user.id==ADMIN_ID:
        bot.send_message(message.chat.id,
"""⚙️ Buyruqlar:

/reklama matn
/premium matn
/broadcast xabar
""")

@bot.message_handler(commands=['premium'])
def set_premium(message):
    if message.from_user.id==ADMIN_ID:
        text = message.text.replace("/premium ","")
        expire = int(time.time()) + 86400
        cursor.execute("DELETE FROM premium")
        cursor.execute("INSERT INTO premium VALUES(?,?)",(text,expire))
        conn.commit()
        bot.send_message(message.chat.id,"🔥 Premium 24 soatga yoqildi")

print("ULTIMATE BUSINESS BOT ISHLADI")
bot.infinity_polling()








