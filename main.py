import telebot
import yt_dlp
import random
import threading
import http.server
import time

MY_TOKEN = "8059225231:AAGCWo5MS2R3yT-y3KX9-IMSBidnBkFE17c"
bot = telebot.TeleBot(MY_TOKEN, threaded=False)

# البروكسيات الخاصة بك من صورتك في Webshare
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
        'extract_flat': 'in_playlist', # سحب الروابط دفعة واحدة وبسرعة
        'playlist_items': '1-100',
        'nocheckcertificate': True,
        'ignoreerrors': True,
        'headers': {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Origin': 'https://www.snapchat.com',
            'Referer': 'https://www.snapchat.com/',
            'Sec-Fetch-Mode': 'cors',
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
    
    wait_msg = bot.reply_to(message, "⚡ جاري محاولة سحب القصة كاملة عبر نظام التخفي...")
    
    try:
        with yt_dlp.YoutubeDL(get_ydl_options()) as ydl:
            # محاولة الاستخراج مع البروكسي المختار
            info = ydl.extract_info(url, download=False)
            
            entries = info.get('entries', [])
            if not entries and 'url' in info:
                entries = [info]

            total = len(entries)
            if total == 0:
                bot.edit_message_text("❌ لم ينجح المتصفح في جلب المحتوى. قد يكون الحساب محظوراً أو محمياً جداً.", message.chat.id, wait_msg.message_id)
                return

            bot.edit_message_text(f"🚀 تم كسر الحماية! جاري إرسال {total} سنابة...", message.chat.id, wait_msg.message_id)

            for i, entry in enumerate(entries, 1):
                video_url = entry.get('url')
                if video_url:
                    try:
                        # محاولة الإرسال كفيديو، وإذا فشل يتم الإرسال كصورة
                        if ".jpg" in video_url.lower() or ".png" in video_url.lower():
                            bot.send_photo(message.chat.id, video_url, caption=f"سنابة [{i}]")
                        else:
                            bot.send_video(message.chat.id, video_url, caption=f"سنابة [{i}]")
                        time.sleep(1) # تأخير بسيط لضمان وصول الترتيب صح
                    except:
                        continue
            
            bot.send_message(message.chat.id, f"✅ تم إكمال المهمة لسحب {total} مقطع/صورة.")
            
    except Exception:
        bot.edit_message_text("❌ عذراً، سناب شات يرفض الاتصال حالياً. جرب مرة أخرى بعد قليل.", message.chat.id, wait_msg.message_id)

if __name__ == "__main__":
    try: bot.remove_webhook()
    except: pass
    threading.Thread(target=handle_render, daemon=True).start()
    bot.infinity_polling(timeout=20)
