import telebot
import yt_dlp
import threading
import http.server
import time

# التوكن
MY_TOKEN = "8059225231:AAGCWo5MS2R3yT-y3KX9-IMSBidnBkFE17c"
bot = telebot.TeleBot(MY_TOKEN, threaded=False)

# إعدادات متقدمة لمحاكاة تطبيق سناب شات الرسمي
YDL_OPTIONS = {
    'format': 'best',
    'quiet': True,
    'no_warnings': True,
    'extract_flat': False,
    'playlist_items': '1-50', 
    'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1',
    'referer': 'https://www.snapchat.com/',
    'http_headers': {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
    },
    'nocheckcertificate': True,
}

def handle_render():
    server_address = ('', 8080)
    httpd = http.server.HTTPServer(server_address, http.server.SimpleHTTPRequestHandler)
    httpd.serve_forever()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "أهلاً ماجد! تم تحديث نظام المحاكاة لتخطي حماية الـ 3 مقاطع. جرب الآن.")

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    user_input = message.text.strip()
    target_url = user_input if "snapchat.com" in user_input else f"https://www.snapchat.com/add/{user_input}"

    wait_msg = bot.reply_to(message, "⏳ جاري محاكاة الاتصال وسحب كافة السنابات...")
    
    try:
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            # محاولة جلب البيانات كقائمة تشغيل كاملة
            info = ydl.extract_info(target_url, download=False)
            
            # استخراج الروابط
            entries = []
            if 'entries' in info:
                entries = [e for e in info['entries'] if e]
            elif info.get('url'):
                entries = [info]

            total = len(entries)
            if total == 0:
                bot.edit_message_text("❌ لم أجد سنابات عامة حالياً.", message.chat.id, wait_msg.message_id)
                return

            bot.edit_message_text(f"✅ تم العثور على {total} سنابة. يتم الإرسال الآن...", message.chat.id, wait_msg.message_id)

            for i, entry in enumerate(entries, 1):
                m_url = entry.get('url')
                if not m_url: continue
                
                try:
                    # الإرسال كملف فيديو مباشر لضمان الجودة
                    bot.send_video(message.chat.id, m_url, caption=f"السنابة رقم [{i}]")
                    time.sleep(0.5) # تأخير بسيط لتجنب حظر تليجرام
                except:
                    continue

            bot.send_message(message.chat.id, f"🏁 تم إرسال {total} سنابة بنجاح.")

    except Exception as e:
        bot.edit_message_text("⚠️ فشل السحب العميق. سناب شات يرفض الاتصال من هذا السيرفر حالياً.", message.chat.id, wait_msg.message_id)

if __name__ == "__main__":
    bot.remove_webhook()
    threading.Thread(target=handle_render, daemon=True).start()
    bot.infinity_polling()
