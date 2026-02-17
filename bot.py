import telebot
from telebot import types
import sqlite3

TOKEN = "8581414528:AAHImgFvDPlFDN-rRedxIYNc-NrQ_D8IyaU"
CHANNEL_USERNAME = "@elonreklama3"
ADMIN_ID = 8577002578

bot = telebot.TeleBot(TOKEN)

# DATABASE
conn = sqlite3.connect("database.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    referrals INTEGER DEFAULT 0
)
""")
conn.commit()

reklama_text = "Hozircha reklama yo'q"

# OBUNA TEKSHIRISH
def check_sub(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# START
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
            ref_id = int(args[1])
            if ref_id != user_id:
                cursor.execute("UPDATE users SET referrals = referrals + 1 WHERE user_id=?", (ref_id,))
                conn.commit()

    if not check_sub(user_id):
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton("📢 Obuna bo‘lish", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")
        btn2 = types.InlineKeyboardButton("✅ Tekshirish", callback_data="check")
        markup.add(btn1, btn2)
        bot.send_message(message.chat.id, "❌ Kanalga obuna bo‘ling!", reply_markup=markup)
        return

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("👥 Referalim", "📊 Statistika")
    bot.send_message(message.chat.id,
"""🔥 BONUS BOTGA XUSH KELIBSIZ!

🎁 5 ta do‘st taklif qil → 1 BONUS
🏆 Eng ko‘p taklif qilganlar sovg‘a oladi!

Pastdagi tugmalar orqali boshlang 👇

""" + reklama_text,
reply_markup=markup)


# CHECK
@bot.callback_query_handler(func=lambda call: call.data == "check")
def check_button(call):
    if check_sub(call.from_user.id):
        bot.answer_callback_query(call.id, "✅ Tasdiqlandi")
        bot.send_message(call.message.chat.id, "Qayta /start bosing")
    else:
        bot.answer_callback_query(call.id, "❌ Hali obuna bo‘lmagansiz!", show_alert=True)

@bot.message_handler(func=lambda m: m.text == "👥 Referalim")
def referral_menu(message):
    user_id = message.from_user.id
    link = f"https://t.me/{bot.get_me().username}?start={user_id}"

    cursor.execute("SELECT referrals FROM users WHERE user_id=?", (user_id,))
    result = cursor.fetchone()

    if result:
        count = result[0]
    else:
        count = 0

    bonus = count // 5

    text = f"""🔥 DO‘STLARINGGA YUBOR!

👥 Takliflar soni: {count}
🎁 Bonuslar: {bonus}

🔗 Shaxsiy linking:
{link}

5 ta odam = 1 bonus 🚀
Ko‘proq taklif qil — ko‘proq yut!
"""

    markup = types.InlineKeyboardMarkup()
    share_btn = types.InlineKeyboardButton(
        "📣 Do‘stlarga ulashish",
        url=f"https://t.me/share/url?url={link}"
    )
    markup.add(share_btn)

    bot.send_message(message.chat.id, text, reply_markup=markup)





# STATISTIKA
@bot.message_handler(func=lambda m: m.text == "📊 Statistika")
def stats(message):
    if message.from_user.id == ADMIN_ID:
        cursor.execute("SELECT COUNT(*) FROM users")
        total = cursor.fetchone()[0]
        bot.send_message(message.chat.id, f"👥 Jami foydalanuvchilar: {total}")
    else:
        bot.send_message(message.chat.id, "❌ Faqat admin uchun")

# REKLAMA QO'SHISH
@bot.message_handler(commands=['reklama'])
def add_reklama(message):
    global reklama_text
    if message.from_user.id == ADMIN_ID:
        reklama_text = message.text.replace("/reklama ", "")
        bot.send_message(message.chat.id, "✅ Reklama saqlandi!")
    else:
        bot.send_message(message.chat.id, "❌ Siz admin emassiz")

print("Bot ishga tushdi...")
@bot.message_handler(commands=['top'])
def top_users(message):
    cursor.execute("SELECT user_id, referrals FROM users ORDER BY referrals DESC LIMIT 5")
    top = cursor.fetchall()

    text = "🏆 TOP 5 REFERAL:\n\n"

    for i, user in enumerate(top, start=1):
        text += f"{i}. ID: {user[0]} — {user[1]} ta\n"

    bot.send_message(message.chat.id, text)
bot.infinity_polling()
















