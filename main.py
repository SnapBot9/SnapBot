import telebot
import yt_dlp
import random
import threading
import http.server
import time

MY_TOKEN = "8059225231:AAGCWo5MS2R3yT-y3KX9-IMSBidnBkFE17c"
bot = telebot.TeleBot(MY_TOKEN, threaded=False)

PROXIES_LIST = [
    'http://hoxhnwln:q2wym85y5h7a@31.59.20.176:6754',
    'http://hoxhnwln:q2wym85y5h7a@23.95.150.145:6114',
    'http://hoxhnwln:q2wym85y5h7a@198.23.239.134:6540',
    'http://hoxhnwln:q2wym85y5h7a@45.38.107.97:6014',
    'http://hoxhnwln:q2wym85y5h7a@107.172.163.27:6543',
    'http://hoxhnwln:q2wym85y5h7a@198.105.121.200:6462',
    'http://hoxhnwln:q2wym85y5h7a@216.10.27.159:6837',
    'http://hoxhnwln:q2wym85y5h7a@142.111.67.146:5611',
    'http://hoxhnwln:q2wym85y5h7a@191.96.254.138:6185',
    'http://hoxhnwln:q2wym85y5h7a@31.58.9.4:6077'
]

def get_ydl_options():
    selected_proxy = random.choice(PROXIES_LIST)
    return {
        'proxy': selected_proxy,
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,
        'force_generic_extractor': False,
        'nocheckcertificate': True,
        'ignoreerrors': True,
        # إضافة Headers تحاكي تطبيق السناب الفعلي وليس فقط المتصفح
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
            'Accept': '*/*',
            'Accept-Language': 'ar-SA,ar;q=0.9,en-US;q=0.8,en;q=0.7',
            'Referer': 'https://www.snapchat.com/',
        }
    }

def start_server():
    server_address = ('', 8080)
    http.server.HTTPServer(server_address, http.server.SimpleHTTPRequestHandler).serve_forever()

@bot.message_handler(func=lambda message: True)
def handle_msg(message):
    user_input = message.text.strip()
    # تنظيف الرابط لضمان عدم حدوث خطأ 404
    username = user_input.split('/')[-1].replace('@', '')
    url = f"https://www.snapchat.com/add/{username}"
    
    status = bot.reply_to(message, "🔍 جاري الاتصال بخوادم سناب شات...")
    
    try:
        with yt_dlp.YoutubeDL(get_ydl_options()) as ydl:
            # محاولة الاستخراج القوية
            info = ydl.extract_info(url, download=False)
            
            # جلب القائمة كاملة (Playlist)
            entries = info.get('entries', [])
            if not entries and 'url' in info:
                entries = [info]

            if not entries:
                bot.edit_message_text("❌ لم أتمكن من العثور على القصة. جرب يوزر آخر.", message.chat.id, status.message_id)
                return

            bot.edit_message_text(f"🚀 تم اختراق الحماية! جاري إرسال {len(entries)} سنابة...", message.chat.id, status.message_id)

            for i, entry in enumerate(entries, 1):
                link = entry.get('url')
                if not link: continue
                
                try:
                    # فحص هل هو فيديو أم صورة
                    if any(x in link.lower() for x in ['.jpg', '.jpeg', '.png']):
                        bot.send_photo(message.chat.id, link, caption=f"سنابة رقم [{i}]")
                    else:
                        bot.send_video(message.chat.id, link, caption=f"سنابة رقم [{i}]")
                    time.sleep(0.5)
                except:
                    # إذا فشل الرفع نرسل الرابط مباشرة (لحل مشكلة البوت الوهمي)
                    bot.send_message(message.chat.id, f"🔗 سنابة رقم [{i}]: {link}")

            bot.send_message(message.chat.id, "🏁 تم الانتهاء من التوريد.")

    except Exception as e:
        bot.edit_message_text(f"⚠️ خطأ بالسيرفر: {str(e)[:40]}", message.chat.id, status.message_id)

if __name__ == "__main__":
    bot.remove_webhook()
    time.sleep(1)
    threading.Thread(target=start_server, daemon=True).start()
    bot.infinity_polling(timeout=30)
