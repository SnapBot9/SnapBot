import telebot
from telebot import types
import yt_dlp
import threading
import http.server
import os

# التوكن
MY_NEW_TOKEN = "8059225231:AAGCWo5MS2R3yT-y3KX9-IMSBidnBkFE17c"
bot = telebot.TeleBot(MY_NEW_TOKEN, threaded=False)
bot.remove_webhook()

user_links = {}

def handle_render():
    server_address = ('', 8080)
    httpd = http.server.HTTPServer(server_address, http.server.SimpleHTTPRequestHandler)
    httpd.serve_forever()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, f"Welcome {message.from_user.first_name}! 👻\nأرسل رابط السناب الآن.")

@bot.message_handler(func=lambda message: "snapchat.com" in message.text)
def ask_options(message):
    user_links[message.chat.id] = message.text
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn1 = types.InlineKeyboardButton("تحميل المقطع الحالي 📥", callback_data="single_v")
    btn2 = types.InlineKeyboardButton("دمج القصة (تجريبي) 🔄", callback_data="merge_v")
    markup.add(btn1, btn2)
    bot.reply_to(message, "تم استلام الرابط، اختر المهمة:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    url = user_links.get(chat_id)
    
    if call.data == "single_v":
        bot.edit_message_text("⏳ محاولة استخراج الرابط... يرجى الصبر.", chat_id, call.message.message_id)
        
        # محرك البحث عن الفيديو (نسخة خفيفة)
        ydl_opts = {
            'format': 'best',
            'quiet': True,
            'no_warnings': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                v_url = info.get('url')
                if v_url:
                    bot.send_video(chat_id, v_url, caption="✅ تم السحب بنجاح!")
                else:
                    bot.send_message(chat_id, "❌ سناب شات حجب الطلب حالياً، جرب رابط آخر بعد قليل.")
        except Exception as e:
            bot.send_message(chat_id, "⚠️ خطأ فني: السيرفر محظور من سناب شات حالياً.")

    elif call.data == "merge_v":
        bot.send_message(chat_id, "🚧 ميزة الدمج تتطلب ذاكرة عالية، جرب السحب الفردي أولاً للتأكد من الاتصال.")

if __name__ == "__main__":
    threading.Thread(target=handle_render, daemon=True).start()
    bot.infinity_polling()
