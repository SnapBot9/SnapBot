import telebot
from telebot import types
import yt_dlp
import threading
import http.server
import os
import time

# استدعاء مكتبة الدمج بطريقة آمنة
try:
    from moviepy.editor import VideoFileClip, concatenate_videoclips
except Exception as e:
    print(f"MoviePy Import Warning: {e}")

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
    btn1 = types.InlineKeyboardButton("تحميل هذا المقطع فقط 📥", callback_data="single_v")
    btn2 = types.InlineKeyboardButton("دمج القصة كاملة (متواصلة) 🔄", callback_data="merge_v")
    markup.add(btn1, btn2)
    bot.reply_to(message, "اختر طريقة التحميل:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    url = user_links.get(chat_id)
    
    ydl_opts_base = {
        'format': 'best',
        'quiet': True,
        'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
        'referer': 'https://www.snapchat.com/',
    }

    if call.data == "single_v":
        bot.edit_message_text("⏳ جاري سحب المقطع...", chat_id, call.message.message_id)
        try:
            with yt_dlp.YoutubeDL(ydl_opts_base) as ydl:
                info = ydl.extract_info(url, download=False)
                bot.send_video(chat_id, info.get('url'), caption="✅ تم السحب!")
        except:
            bot.send_message(chat_id, "❌ فشل السحب.")

    elif call.data == "merge_v":
        bot.edit_message_text("🎬 جاري التحميل والدمج.. انتظر قليلاً.", chat_id, call.message.message_id)
        try:
            # مسار التحميل
            ydl_opts_merge = ydl_opts_base.copy()
            ydl_opts_merge['outtmpl'] = f'v_{chat_id}_%(autonumber)s.mp4'
            
            with yt_dlp.YoutubeDL(ydl_opts_merge) as ydl:
                ydl.download([url])
            
            files = sorted([f for f in os.listdir('.') if f.startswith(f'v_{chat_id}_')])
            if not files:
                bot.send_message(chat_id, "❌ لم أجد مقاطع للدمج.")
                return

            clips = [VideoFileClip(f) for f in files]
            final = concatenate_videoclips(clips, method="compose")
            out = f"res_{chat_id}.mp4"
            final.write_videofile(out, codec="libx264", audio_codec="aac", logger=None)
            
            with open(out, 'rb') as f:
                bot.send_video(chat_id, f, caption="✅ تم الدمج بنجاح!")
            
            # تنظيف
            final.close()
            for c in clips: c.close()
            for f in files + [out]: os.remove(f)
        except Exception as e:
            bot.send_message(chat_id, f"⚠️ خطأ: تأكد من تثبيت MoviePy أو حجم القصة كبير.")

if __name__ == "__main__":
    threading.Thread(target=handle_render, daemon=True).start()
    bot.infinity_polling()
