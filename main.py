import os
import telebot

# التوكن الجديد والنظيف الخاص بك
TOKEN = "8059225231:AAGCWo5MS2R3yT-y3KX9-IMSBidnBkFE17c"

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "أهلاً بك يا بطل! 🚀\n\nتم تشغيل البوت بنجاح بالتوكن الجديد. أرسل رابط السناب الآن.")

@bot.message_handler(func=lambda message: True)
def handle_all(message):
    if "snapchat.com" in message.text:
        bot.reply_to(message, "جاري العمل على الرابط... يرجى الانتظار 📥")
    else:
        bot.reply_to(message, "يرجى إرسال رابط سناب شات صحيح.")

if __name__ == "__main__":
    print("البوت يعمل الآن بالتوكن الجديد...")
    bot.infinity_polling()
