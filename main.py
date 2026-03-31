import os
import telebot

# تم تغيير اسم المتغير لضمان تجاوز أي تعليق في سيرفر Render
MY_NEW_TOKEN = "8059225231:AAGCWo5MS2R3yT-y3KX9-IMSBidnBkFE17c"

# تشغيل البوت باستخدام التوكن الجديد
bot = telebot.TeleBot(MY_NEW_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "أهلاً بك يا ماجد! 🚀\n\n"
        "تم تشغيل البوت بنجاح بالتوكن الجديد.\n"
        "أرسل رابط السناب شات الآن وسأقوم بالتعامل معه."
    )
    bot.reply_to(message, welcome_text)

@bot.message_handler(func=lambda message: True)
def handle_all(message):
    if "snapchat.com" in message.text:
        bot.reply_to(message, "📥 وصل الرابط! جاري العمل على محرك السحب... يرجى الانتظار.")
    else:
        bot.reply_to(message, "⚠️ من فضلك، أرسل رابط سناب شات صحيح.")

if __name__ == "__main__":
    print("جاري تشغيل البوت بالتوكن الجديد...")
    bot.infinity_polling()
