import telebot
import time

# التوكن الجديد والمفعل
MY_NEW_TOKEN = "8059225231:AAGCWo5MS2R3yT-y3KX9-IMSBidnBkFE17c"

# تشغيل البوت مع تعطيل التعدد لمنع خطأ 409
bot = telebot.TeleBot(MY_NEW_TOKEN, threaded=False)

# حذف أي اتصال قديم (Webhook) قبل البدء
bot.remove_webhook()
time.sleep(2)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "أهلاً بك يا ماجد! البوت يعمل الآن بنجاح ✅")

@bot.message_handler(func=lambda message: True)
def handle_all(message):
    if "snapchat.com" in message.text:
        bot.reply_to(message, "📥 جاري معالجة الرابط...")
    else:
        bot.reply_to(message, "أرسل رابط سناب شات صحيح.")

if __name__ == "__main__":
    print("تم تنظيف الاتصالات.. البوت يبدأ الآن.")
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
