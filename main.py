import os
import telebot

# التوكن الصحيح والكامل الخاص بك
TOKEN = "8059225231:AAHYr_PqgGjdHFEf_VKQ-5Fv5CrODWUUM1k"

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "أهلاً بك! تم الربط مع Render بنجاح ✅\n\nأرسل رابط السناب الآن وسأحاول سحبه لك.")

@bot.message_handler(func=lambda message: True)
def handle_all(message):
    if "snapchat.com" in message.text:
        bot.reply_to(message, "وصل الرابط! 📥 جاري العمل على محرك السحب... يرجى الانتظار.")
    else:
        bot.reply_to(message, "⚠️ يرجى إرسال رابط سناب شات صحيح.")

if __name__ == "__main__":
    print("البوت بدأ العمل بنجاح...")
    bot.infinity_polling()
