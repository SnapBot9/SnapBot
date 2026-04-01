import telebot
from telebot import types
import yt_dlp
import threading
import http.server
import os
from moviepy.editor import VideoFileClip, concatenate_videoclips

# التوكن الخاص بك
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
    bot.reply_to(message, f"Welcome {message.from_user.first_name}! 👻\nأرسل رابط السناب وسأقوم بدمج القصة لك.")

@bot.message_handler(func=lambda message: "snapchat.com" in message.text)
def ask_options(message):
    user_links[message.chat.id] = message.text
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn1 = types.InlineKeyboardButton("تحميل هذا المقطع فقط 📥", callback_data="single_v")
    btn2 = types.InlineKeyboardButton("دمج القصة كاملة (متواصلة) 🔄", callback_data="merge_v")
    markup.add(btn1, btn2)
    bot.reply_to(message, "اختر الطريقة:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    url = user_links.get(chat_id)
    
    # خيارات الـ yt-dlp الموحدة للتمويه
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
                video_url = info.get('url')
                bot.send_video(chat_id, video_url, caption="✅ تم السحب!")
        except Exception as e:
            bot.send_message(chat_id, "❌ فشل السحب الفردي.")

    elif call.data == "merge_v":
        bot.edit_message_text("🎬 بدأت عملية الدمج.. يرجى الانتظار (قد تستغرق دقيقة).", chat_id, call.message.message_id)
        
        try:
            temp_files = []
            clips = []
            
            # 1. سحب وتحميل المقاطع
            ydl_opts_merge = ydl_opts_base.copy()
            ydl_opts_merge['outtmpl'] = f'vid_{chat_id}_%(autonumber)s.mp4'
            
            with yt_dlp.YoutubeDL(ydl_opts_merge) as ydl:
                # استخراج جميع المقاطع المتاحة في الرابط
                info = ydl.extract_info(url, download=True)
                # إذا كان الرابط يحتوي على مقاطع متعددة
                downloaded_files = sorted([f for f in os.listdir('.') if f.startswith(f'vid_{chat_id}_')])
                temp_files.extend(downloaded_files)

            if not temp_files:
                bot.send_message(chat_id, "❌ لم أجد مقاطع لدمجها.")
                return

            # 2. معالجة الدمج بـ MoviePy
            for file in temp_files:
                clip = VideoFileClip(file)
                clips.append(clip)
            
            final_clip = concatenate_videoclips(clips, method="compose")
            output_name = f"merged_{chat_id}.mp4"
            final_clip.write_videofile(output_name, codec="libx264", audio_codec="aac", verbose=False, logger=None)
            
            # 3. إرسال الفيديو المدمج
            with open(output_name, 'rb') as f:
                bot.send_video(chat_id, f, caption="✅ تم دمج القصة كاملة!")

            # 4. تنظيف الملفات (حذفها من السيرفر)
            final_clip.close()
            for c in clips: c.close()
            for f in temp_files + [output_name]:
                if os.path.exists(f): os.remove(f)

        except Exception as e:
            bot.send_message(chat_id, "⚠️ عذراً، القصة طويلة جداً على قدرات السيرفر المجاني أو حدث خطأ في الدمج.")
            print(f"Merge Error: {e}")

if __name__ == "__main__":
    threading.Thread(target=handle_render, daemon=True).start()
    bot.infinity_polling()
