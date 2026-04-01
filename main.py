import telebot
import time
import http.server
import threading

# التوكن الجديد والمفعل
MY_NEW_TOKEN = "8059225231:AAGCWo5MS2R3yT-y3KX9-IMSBidnBkFE17c"

bot = telebot.TeleBot(MY_NEW_TOKEN, threaded=False)
bot.remove_webhook()

# سطر مهم جداً لإرضاء Render ومنع تعليق الـ Port
def handle_render():
    server_address = ('', 8080)
    httpd = http.server.HTTPServer(server_address, http.server.SimpleHTTPRequestHandler)
    httpd.serve_forever()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "أهلاً بك يا ماجد! البوت شغال الآن بنجاح ✅")

@bot.message_handler(func=lambda message: True)
def handle_all(message):
    if "snapchat.com" in message.text:
        bot.reply_to(message, "📥 جاري معالجة الرابط...")
    else:
        bot.reply_to(message, "أرسل رابط سناب شات صحيح.")

if __name__ == "__main__":
    # تشغيل سيرفر وهمي في الخلفية لإرضاء Render
    threading.Thread(target=handle_render, daemon=True).start()
    print("تم تشغيل السيرفر الوهمي والبوت يبدأ الآن...")
    bot.infinity_polling()
