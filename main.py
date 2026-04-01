import telebot
import time

# التوكن الجديد
MY_NEW_TOKEN = "8059225231:AAGCWo5MS2R3yT-y3KX9-IMSBidnBkFE17c"

#threaded=False تمنع التضارب في السيرفرات الضعيفة
bot = telebot.TeleBot(MY_NEW_TOKEN, threaded=False)

# مسح أي طلبات قديمة عالقة في تليجرام
bot.remove_webhook()
time.sleep(2)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "تم حل التعارض! ✅ البوت شغال الآن يا ماجد.")

@bot.message_handler(func=lambda message: True)
def handle_all(message):
    if "snapchat.com" in message.text:
        bot.reply_to(message, "📥 جاري المعالجة...")
    else:
        bot.reply_to(message, "أرسل رابط سناب شات.")

if __name__ == "__main__":
    print("بدأ التشغيل بنجاح...")
    # non_stop=True تجعل البوت يحاول الاتصال حتى لو وجد تعارض مؤقت
    bot.infinity_polling(timeout=20, long_polling_timeout=10)
