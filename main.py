import telebot
from telebot import types
import yt_dlp
import os
import threading
import http.server
import time

# التوكن الخاص بك
MY_NEW_TOKEN = "8059225231:AAGCWo5MS2R3yT-y3KX9-IMSBidnBkFE17c"
bot = telebot.TeleBot(MY_NEW_TOKEN, threaded=False)
bot.remove_webhook()

# تخزين الروابط مؤقتاً لربطها بالأزرار
user_links = {}

# سيرفر وهمي لإرضاء Render
def handle_render():
    server_address = ('', 8080)
    httpd = http.server.HTTPServer(server_address, http.server.SimpleHTTPRequestHandler)
    httpd.serve_forever()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, f"Welcome {message.from_user.first_name}! 👻\nأرسل رابط السناب الآن.")

@bot.message_handler(func=lambda message: "snapchat.com" in message.text)
def ask_options(message):
    user_links[message.chat.id] = message.text  # حفظ الرابط مؤقتاً
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn1 = types.InlineKeyboardButton("تحميل هذا المقطع فقط 📥", callback_data="single_v")
    btn2 = types.InlineKeyboardButton("دمج القصة كاملة (متواصلة) 🔄", callback_data="merge_v")
    markup.add(btn1, btn2)
    bot.reply_to(message, "اختر طريقة التحميل:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    url = user_links.get(chat_id)
    
    if not url:
        bot.send_message(chat_id, "⚠️ انتهت صلاحية الرابط، أرسله مرة أخرى.")
        return

    if call.data == "single_v":
        bot.edit_message_text("⏳ جاري استخراج المقطع... انتظر قليلاً.", chat_id, call.message.message_id)
        
        try:
            ydl_opts = {'format': 'best', 'quiet': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                video_url = info.get('url')
                if video_url:
                    bot.send_video(chat_id, video_url, caption="✅ تم تحميل المقطع بنجاح!")
                else:
                    bot.send_message(chat_id, "❌ فشل استخراج الفيديو.")
        except Exception as e:
            bot.send_message(chat_id, f"⚠️ خطأ: {str(e)}")

    elif call.data == "merge_v":
        bot.edit_message_text("🎬 ميزة الدمج قيد التطوير البرمجي حالياً، سيتم تفعيلها في التحديث القادم.", chat_id, call.message.message_id)

if __name__ == "__main__":
    threading.Thread(target=handle_render, daemon=True).start()
    bot.infinity_polling()
