import telebot
import yt_dlp
import threading
import http.server
import time
import random

# التوكن الخاص بك
MY_TOKEN = "8059225231:AAGCWo5MS2R3yT-y3KX9-IMSBidnBkFE17c"
bot = telebot.TeleBot(MY_TOKEN, threaded=False)

# قائمة متصفحات عشوائية لخداع نظام حماية سناب شات في ريندر
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
]

def handle_render():
    server_address = ('', 8080)
    httpd = http.server.HTTPServer(server_address, http.server.SimpleHTTPRequestHandler)
    httpd.serve_forever()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "تم تحديث البوت بنظام 'كسر القيود' 👻\nأرسل اليوزر الآن وسأحاول سحب كامل القصة.")

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    user_input = message.text.strip()
    target_url = user_input if "snapchat.com" in user_input else f"https://www.snapchat.com/add/{user_input}"

    wait_msg = bot.reply_to(message, "📡 جاري الاتصال بسناب شات وتخطي قيود العدد...")
    
    # إعدادات مخصصة لكسر حماية الـ 3 مقاطع
    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
        'extract_flat': 'in_playlist',
        'playlist_items': '1-50',
        'user_agent': random.choice(USER_AGENTS), # اختيار متصفح عشوائي في كل طلب
        'referer': 'https://www.snapchat.com/',
        'ignoreerrors': True,
        'add_header': ['Accept: */*', 'Connection: keep-alive']
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # محاولة جلب البيانات (Scraping)
            info = ydl.extract_info(target_url, download=False)
            
            # استخلاص السنابات (سواء كانت في قائمة أو فردية)
            if 'entries' in info:
                entries = [e for e in info['entries'] if e]
            else:
                entries = [info] if info.get('url') else []

            total = len(entries)
            if total == 0:
                bot.edit_message_text("❌ لم أجد سنابات عامة حالياً (قد يكون الحساب خاصاً).", message.chat.id, wait_msg.message_id)
                return

            bot.edit_message_text(f"🚀 نجحت في تخطي الحماية! وجدت {total} سنابة. جاري الإرسال...", message.chat.id, wait_msg.message_id)

            for i, entry in enumerate(entries, 1):
                m_url = entry.get('url')
                if not m_url: continue
                
                try:
                    # فحص النوع (فيديو أو صورة)
                    if any(ext in m_url.lower() for ext in [".jpg", ".png", ".jpeg"]):
                        bot.send_photo(message.chat.id, m_url, caption=f"سنابة [{i}]")
                    else:
                        bot.send_video(message.chat.id, m_url, caption=f"سنابة [{i}]")
                    
                    # تأخير عشوائي بسيط لخداع الحماية
                    time.sleep(random.uniform(0.5, 1.2)) 
                except:
                    continue

            bot.send_message(message.chat.id, f"✅ اكتمل سحب القصة بنجاح.")

    except Exception as e:
        bot.edit_message_text("⚠️ فشل الاتصال العميق. سناب شات يرفض طلبات Render حالياً.", message.chat.id, wait_msg.message_id)

if __name__ == "__main__":
    bot.remove_webhook()
    threading.Thread(target=handle_render, daemon=True).start()
    bot.infinity_polling()
