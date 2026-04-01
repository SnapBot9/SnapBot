import telebot
import yt_dlp
import random
import threading
import http.server
import time

MY_TOKEN = "8059225231:AAGCWo5MS2R3yT-y3KX9-IMSBidnBkFE17c"
bot = telebot.TeleBot(MY_TOKEN, threaded=False)

# قائمة البروكسيات الخاصة بك
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
    # اختيار بروكسي عشوائي لكل عملية بحث جديدة لكسر الحجب
    selected_proxy = random.choice(PROXIES_LIST)
    return {
        'proxy': selected_proxy,
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True, 
        'force_generic_extractor': False,
        'playlist_items': '1-100',
        'nocheckcertificate': True,
        'ignoreerrors': True,
        # هيدرز لمحاكاة متصفح حقيقي كما تفعل البوتات الكبيرة
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    }

def handle_render():
    server_address = ('', 8080)
    httpd = http.server.HTTPServer(server_address, http.server.SimpleHTTPRequestHandler)
    httpd.serve_forever()

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    target = message.text.strip()
    url = target if "snapchat.com" in target else f"https://www.snapchat.com/add/{target}"
    
    status_msg = bot.reply_to(message, "🔍 جاري محاكاة جلسة تصفح حقيقية لسحب القصة كاملة...")
    
    try:
        with yt_dlp.YoutubeDL(get_ydl_options()) as ydl:
            # محاولة جلب البيانات
            info = ydl.extract_info(url, download=False)
            
            # استخراج المدخلات سواء كانت فيديو أو صورة
            entries = info.get('entries', [])
            if not entries and 'url' in info:
                entries = [info]

            total = len(entries)
            if total == 0:
                bot.edit_message_text("❌ لم ينجح السحب. جرب يوزر آخر أو انتظر دقيقة.", message.chat.id, status_msg.message_id)
                return

            bot.edit_message_text(f"✅ تم العثور على {total} سنابة. جاري التوريد من السيرفر...", message.chat.id, status_msg.message_id)

            for i, entry in enumerate(entries, 1):
                file_url = entry.get('url')
                if not file_url: continue
                
                try:
                    # فحص النوع (صورة أو فيديو) للإرسال الصحيح
                    if any(ext in file_url.lower() for ext in [".jpg", ".png", ".jpeg"]):
                        bot.send_photo(message.chat.id, file_url, caption=f"سنابة رقم [{i}]")
                    else:
                        bot.send_video(message.chat.id, file_url, caption=f"سنابة رقم [{i}]")
                    
                    # تأخير بسيط جداً لمنع اكتشاف "التدفق السريع"
                    time.sleep(0.8)
                except:
                    continue
            
            bot.send_message(message.chat.id, f"🏁 اكتمل السحب بنجاح! الإجمالي: {total}")

    except Exception:
        bot.edit_message_text("⚠️ خطأ في الاتصال بالسيرفر. البروكسي مشغول، حاول مرة أخرى.", message.chat.id, status_msg.message_id)

if __name__ == "__main__":
    # تنظيف الجلسات القديمة لحل مشكلة Conflict 409
    try: bot.remove_webhook()
    except: pass
    
    # تشغيل سيرفر Render للحفاظ على استمرارية البوت
    threading.Thread(target=handle_render, daemon=True).start()
    
    print("البوت يعمل الآن بنفس تقنية البوتات الكبيرة...")
    bot.infinity_polling(timeout=20)
