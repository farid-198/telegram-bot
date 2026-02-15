
import telebot
from telebot import types

TOKEN = "8581414528:AAHImgFvDPlFDN-rRedxIYNc-NrQ_D8IyaU"
CHANNEL_USERNAME = "@elonreklama3"
ADMIN_ID = 8577002578

bot = telebot.TeleBot(TOKEN)

reklama_text = "Hozircha reklama yo'q"
users = {}
referrals = {}

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

    # Referral
    args = message.text.split()
    if len(args) > 1:
        ref_id = int(args[1])
        if ref_id != user_id:
            referrals[ref_id] = referrals.get(ref_id, 0) + 1

    if not check_sub(user_id):
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton("📢 Obuna bo‘lish", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")
        btn2 = types.InlineKeyboardButton("✅ Tekshirish", callback_data="check")
        markup.add(btn1, btn2)
        bot.send_message(message.chat.id, "❌ Kanalga obuna bo‘ling!", reply_markup=markup)
        return

    users[user_id] = True

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("👥 Referalim", "📢 Reklama")
    bot.send_message(message.chat.id, f"🎉 Xush kelibsiz!\n\n{reklama_text}", reply_markup=markup)

# CHECK BUTTON
@bot.callback_query_handler(func=lambda call: call.data == "check")
def check_button(call):
    if check_sub(call.from_user.id):
        bot.answer_callback_query(call.id, "✅ Obuna tasdiqlandi!")
        bot.send_message(call.message.chat.id, "Qayta /start bosing")
    else:
        bot.answer_callback_query(call.id, "❌ Hali obuna bo‘lmagansiz!", show_alert=True)

# REFERAL
@bot.message_handler(func=lambda m: m.text == "👥 Referalim")
def referral_menu(message):
    user_id = message.from_user.id
    link = f"https://t.me/{bot.get_me().username}?start={user_id}"
    count = referrals.get(user_id, 0)
    bot.send_message(message.chat.id,
                     f"🔗 Sizning referal linkingiz:\n{link}\n\n👥 Taklif qilganlar soni: {count}")

# REKLAMA KO'RISH
@bot.message_handler(func=lambda m: m.text == "📢 Reklama")
def reklama_show(message):
    bot.send_message(message.chat.id, reklama_text)

# ADMIN REKLAMA QO'SHISH
@bot.message_handler(commands=['reklama'])
def add_reklama(message):
    if message.from_user.id == ADMIN_ID:
        global reklama_text
        reklama_text = message.text.replace("/reklama ", "")
        bot.send_message(message.chat.id, "✅ Reklama saqlandi!")
    else:
        bot.send_message(message.chat.id, "❌ Siz admin emassiz")

print("Bot ishga tushdi...")
bot.infinity_polling()










