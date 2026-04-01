import telebot
from telebot import types
import yt_dlp
import threading
import http.server
import os
import time

# التوكن الخاص بك
MY_NEW_TOKEN = "8059225231:AAGCWo5MS2R3yT-y3KX9-IMSBidnBkFE17c"
bot = telebot.TeleBot(MY_NEW_TOKEN, threaded=False)
bot.remove_webhook()

user_links = {}

# إعدادات السحب الموحدة (تمويه آيفون)
YDL_OPTIONS = {
    'format': 'best',
    'quiet': True,
    'no_warnings': True,
    'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
    'referer': 'https://www.snapchat.com/',
}

def handle_render():
    server_address = ('', 8080)
    httpd = http.server.HTTPServer(server_address, http.server.SimpleHTTPRequestHandler)
    httpd.serve_forever()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, f"Welcome {message.from_user.first_name}! 👻\nأرسل رابط السناب الآن واكتشف الخيارات الجديدة.")

@bot.message_handler(func=lambda message: "snapchat.com" in message.text)
def ask_options(message):
    user_links[message.chat.id] = message.text
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    btn1 = types.InlineKeyboardButton("تحميل المقطع الحالي فقط 📥", callback_data="single_v")
    btn2 = types.InlineKeyboardButton("تحميل القصة (مقاطع منفصلة) 🎞️", callback_data="split_v")
    btn3 = types.InlineKeyboardButton("دمج القصة في فيديو واحد 🔄", callback_data="merge_v")
    
    markup.add(btn1, btn2, btn3)
    bot.reply_to(message, "تم استلام الرابط! اختر ما تريد فعله:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    url = user_links.get(chat_id)
    
    if not url:
        bot.send_message(chat_id, "⚠️ أرسل الرابط مرة أخرى.")
        return

    # 1. تحميل مقطع واحد
    if call.data == "single_v":
        bot.edit_message_text("⏳ جاري سحب المقطع الحالي...", chat_id, call.message.message_id)
        try:
            with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(url, download=False)
                bot.send_video(chat_id, info.get('url'), caption="✅ تم تحميل المقطع بنجاح!")
        except:
            bot.send_message(chat_id, "❌ فشل السحب. تأكد أن القصة عامة وليست خاصة.")

    # 2. تحميل القصة مقاطع منفصلة (الاقتراح الجديد)
    elif call.data == "split_v":
        bot.edit_message_text("🎞️ جاري سحب كامل القصة كمقاطع منفصلة... انتظر ثواني.", chat_id, call.message.message_id)
        try:
            with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(url, download=False)
                if 'entries' in info:
                    for entry in info['entries']:
                        bot.send_video(chat_id, entry.get('url'))
                    bot.send_message(chat_id, "✅ تم إرسال جميع مقاطع القصة.")
                else:
                    # إذا كان الرابط يحتوي على فيديو واحد فقط
                    bot.send_video(chat_id, info.get('url'), caption="✅ الرابط يحتوي على مقطع واحد فقط.")
        except:
            bot.send_message(chat_id, "⚠️ حدث خطأ أثناء سحب القصة كاملة.")

    # 3. دمج القصة (متواصل)
    elif call.data == "merge_v":
        bot.send_message(chat_id, "🚧 ميزة الدمج تحت الصيانة حالياً لضمان استقرار السيرفر. استخدم خيار (المقاطع المنفصلة) حالياً.")

if __name__ == "__main__":
    threading.Thread(target=handle_render, daemon=True).start()
    bot.infinity_polling()
