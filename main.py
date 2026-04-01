import telebot
from telebot import types
import yt_dlp
import threading
import http.server
import time

# التوكن الخاص بك
MY_TOKEN = "8059225231:AAGCWo5MS2R3yT-y3KX9-IMSBidnBkFE17c"
bot = telebot.TeleBot(MY_TOKEN, threaded=False)

# حل مشكلة الـ Conflict فور تشغيل البوت
bot.remove_webhook()
time.sleep(1) # انتظار بسيط للتأكد من إغلاق الاتصال القديم

# إعدادات لضمان سحب القصة كاملة بدون توقف عند رقم 3
YDL_OPTIONS = {
    'format': 'best',
    'quiet': True,
    'no_warnings': True,
    'extract_flat': False,
    'playlist_items': '1-100', 
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'referer': 'https://www.snapchat.com/',
}

def handle_render():
    server_address = ('', 8080)
    httpd = http.server.HTTPServer(server_address, http.server.SimpleHTTPRequestHandler)
    httpd.serve_forever()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "أهلاً ماجد! تم حل مشكلة التضارب وتحديث نظام السحب. أرسل اليوزر الآن.")

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    input_text = message.text.strip()
    target_url = input_text if "snapchat.com" in input_text else f"https://www.snapchat.com/add/{input_text}"

    wait_msg = bot.reply_to(message, "⚙️ جاري الفحص والسحب الشامل... يرجى الانتظار.")
    
    try:
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(target_url, download=False)
            entries = info.get('entries', [info]) if 'entries' in info or info.get('url') else []
            
            total = len(entries)
            if total == 0:
                bot.edit_message_text("❌ لم أجد سنابات عامة.", message.chat.id, wait_msg.message_id)
                return

            bot.edit_message_text(f"✅ تم العثور على {total} سنابة. يتم الإرسال...", message.chat.id, wait_msg.message_id)

            for i, entry in enumerate(entries, 1):
                m_url = entry.get('url')
                if not m_url: continue
                try:
                    if any(ext in m_url.lower() for ext in [".jpg", ".png", ".jpeg"]):
                        bot.send_photo(message.chat.id, m_url, caption=f"السنابة رقم [{i}]")
                    else:
                        bot.send_video(message.chat.id, m_url, caption=f"السنابة رقم [{i}]")
                except: continue

            bot.send_message(message.chat.id, f"🏁 تم سحب {total} سنابة بنجاح.")
    except Exception as e:
        bot.edit_message_text("⚠️ خطأ في السحب، تأكد من أن الحساب عام.", message.chat.id, wait_msg.message_id)

if __name__ == "__main__":
    threading.Thread(target=handle_render, daemon=True).start()
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
