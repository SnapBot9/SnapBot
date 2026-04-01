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
    selected_proxy = random.choice(PROXIES_LIST)
    return {
        'format': 'best',
        'proxy': selected_proxy,
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True, # تغيير هذا الخيار ليجلب الروابط بسرعة قبل الحظر
        'playlist_items': '1-100',
        'nocheckcertificate': True,
        'ignoreerrors': True,
        # إضافة هيدرز متصفح آيفون حقيقي (أصعب في الحظر)
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.snapchat.com/',
        },
    }

def handle_render():
    server_address = ('', 8080)
    httpd = http.server.HTTPServer(server_address, http.server.SimpleHTTPRequestHandler)
    httpd.serve_forever()

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    target = message.text.strip()
    url = target if "snapchat.com" in target else f"https://www.snapchat.com/add/{target}"
    
    wait_msg = bot.reply_to(message, "⏳ جاري محاولة كسر حماية سناب شات عبر متصفح وهمي...")
    
    try:
        with yt_dlp.YoutubeDL(get_ydl_options()) as ydl:
            # محاولة جلب البيانات مرتين في حال فشل البروكسي الأول
            info = ydl.extract_info(url, download=False)
            
            # إذا فشل استخراج العناصر، نحاول مرة أخرى ببروكسي مختلف فوراً
            if not info.get('entries'):
                info = ydl.extract_info(url, download=False)

            entries = info.get('entries', [])
            total = len(entries)

            if total == 0:
                bot.edit_message_text("❌ لم ينجح المتصفح في كسر الحماية، الحساب محمي بقوة.", message.chat.id, wait_msg.message_id)
                return

            bot.edit_message_text(f"🚀 نجح الاختراق! تم العثور على {total} سنابة. يتم الإرسال...", message.chat.id, wait_msg.message_id)

            for i, entry in enumerate(entries, 1):
                m_url = entry.get('url')
                if not m_url: continue
                
                try:
                    # إرسال كفيديو أو صورة
                    if any(ext in m_url.lower() for ext in [".jpg", ".png", ".jpeg"]):
                        bot.send_photo(message.chat.id, m_url, caption=f"سنابة [{i}]")
                    else:
                        bot.send_video(message.chat.id, m_url, caption=f"سنابة [{i}]")
                    time.sleep(1) 
                except: continue
            
            bot.send_message(message.chat.id, f"✅ تم سحب القصة كاملة ({total} عنصر).")

    except Exception:
        bot.edit_message_text("❌ حدث خطأ في البروكسي، جرب مرة أخرى.", message.chat.id, wait_msg.message_id)

if __name__ == "__main__":
    try: bot.remove_webhook()
    except: pass
    threading.Thread(target=handle_render, daemon=True).start()
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
