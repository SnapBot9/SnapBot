import telebot
import yt_dlp
import random
import threading
import http.server
import time

# 1. التوكن الخاص بك
MY_TOKEN = "8059225231:AAGCWo5MS2R3yT-y3KX9-IMSBidnBkFE17c"
bot = telebot.TeleBot(MY_TOKEN, threaded=False)

# 2. قائمة البروكسيات العشرة الخاصة بك (من صورتك في Webshare)
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

# 3. إعدادات المحرك (تخطي حماية الـ 3 مقاطع)
def get_ydl_options():
    selected_proxy = random.choice(PROXIES_LIST)
    return {
        'format': 'best',
        'proxy': selected_proxy,
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
        'playlist_items': '1-100', # محاولة سحب حتى 100 سنابة
        'nocheckcertificate': True,
        'ignoreerrors': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'referer': 'https://www.snapchat.com/',
    }

# 4. وظيفة لضمان عمل Render بدون توقف
def handle_render():
    server_address = ('', 8080)
    httpd = http.server.HTTPServer(server_address, http.server.SimpleHTTPRequestHandler)
    httpd.serve_forever()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "أهلاً ماجد! تم تشغيل نظام البروكسي الدوار 🚀\nأرسل اليوزر الآن وسأحاول كسر حماية الـ 3 مقاطع.")

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    target = message.text.strip()
    url = target if "snapchat.com" in target else f"https://www.snapchat.com/add/{target}"
    
    wait_msg = bot.reply_to(message, "⚙️ جاري فحص القصة وتخطي الحماية... لحظات.")
    
    try:
        with yt_dlp.YoutubeDL(get_ydl_options()) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # استخراج كافة العناصر (فيديو أو صور)
            entries = []
            if 'entries' in info:
                entries = [e for e in info['entries'] if e]
            elif info.get('url'):
                entries = [info]

            total = len(entries)
            if total == 0:
                bot.edit_message_text("❌ لم أجد سنابات عامة حالياً (تأكد أن الحساب ليس خاصاً).", message.chat.id, wait_msg.message_id)
                return

            bot.edit_message_text(f"✅ تم العثور على {total} عنصر. جاري الإرسال...", message.chat.id, wait_msg.message_id)

            for i, entry in enumerate(entries, 1):
                m_url = entry.get('url')
                if not m_url: continue
                
                try:
                    # التفريق بين الصورة والفيديو لإرسالها بشكل صحيح
                    if any(ext in m_url.lower() for ext in [".jpg", ".png", ".jpeg", ".webp"]):
                        bot.send_photo(message.chat.id, m_url, caption=f"السنابة رقم [{i}]")
                    else:
                        bot.send_video(message.chat.id, m_url, caption=f"السنابة رقم [{i}]")
                    
                    time.sleep(1.5) # تأخير بسيط لتجنب حظر التلجرام (Flood)
                except Exception:
                    continue

            bot.send_message(message.chat.id, f"🏁 اكتمل السحب! الإجمالي: {total}")

    except Exception as e:
        bot.edit_message_text("⚠️ فشل الاتصال بسناب شات. حاول مرة أخرى لاحقاً.", message.chat.id, wait_msg.message_id)

if __name__ == "__main__":
    # حل مشكلة الـ Conflict 409
    bot.remove_webhook()
    time.sleep(1)
    
    # تشغيل سيرفر Render
    threading.Thread(target=handle_render, daemon=True).start()
    
    print("البوت يعمل الآن بنظام البروكسي...")
    bot.infinity_polling(timeout=20, long_polling_timeout=10)
