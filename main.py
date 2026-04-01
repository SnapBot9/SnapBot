import telebot
import yt_dlp
import random
import threading
import http.server
import time

# التوكن الخاص بك
MY_TOKEN = "8059225231:AAGCWo5MS2R3yT-y3KX9-IMSBidnBkFE17c"
bot = telebot.TeleBot(MY_TOKEN, threaded=False)

# قائمة البروكسيات العشرة الخاصة بك من Webshare (تم استخراجها من صورتك)
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
    # اختيار بروكسي عشوائي من القائمة لضمان عدم الحظر
    selected_proxy = random.choice(PROXIES_LIST)
    return {
        'format': 'best',
        'proxy': selected_proxy,
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
        'playlist_items': '1-100', # لسحب القصة كاملة حتى لو كانت طويلة
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'referer': 'https://www.snapchat.com/',
    }

def handle_render():
    server_address = ('', 8080)
    httpd = http.server.HTTPServer(server_address, http.server.SimpleHTTPRequestHandler)
    httpd.serve_forever()

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    target = message.text.strip()
    # التحقق إذا كان الرابط كاملاً أو مجرد يوزر
    url = target if "snapchat.com" in target else f"https://www.snapchat.com/add/{target}"
    
    wait_msg = bot.reply_to(message, "🌐 جاري سحب القصة كاملة عبر البروكسي... انتظر قليلاً.")
    
    try:
        with yt_dlp.YoutubeDL(get_ydl_options()) as ydl:
            info = ydl.extract_info(url, download=False)
            entries = info.get('entries', [info]) if 'entries' in info or info.get('url') else []
            
            if not entries:
                bot.edit_message_text("⚠️ لم يتم العثور على مقاطع فيديو في هذه القصة.", message.chat.id, wait_msg.message_id)
                return

            for i, entry in enumerate(entries, 1):
                video_url = entry.get('url')
                if video_url:
                    try:
                        bot.send_video(message.chat.id, video_url, caption=f"السنابة رقم [{i}]")
                        time.sleep(1) # تأخير بسيط لتجنب سبام تلجرام
                    except:
                        continue
            
            bot.send_message(message.chat.id, f"✅ اكتمل السحب! إجمالي المقاطع: {len(entries)}")
            
    except Exception as e:
        print(f"Error: {e}")
        bot.edit_message_text("❌ عذراً، واجه البروكسي مشكلة أو القصة محمية جداً. حاول مرة أخرى.", message.chat.id, wait_msg.message_id)

if __name__ == "__main__":
    bot.remove_webhook()
    # تشغيل سيرفر Render في الخلفية
    threading.Thread(target=handle_render, daemon=True).start()
    bot.infinity_polling()
