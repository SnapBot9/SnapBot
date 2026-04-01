import telebot
from telebot import types
import yt_dlp
import threading
import http.server

# التوكن
MY_TOKEN = "8059225231:AAGCWo5MS2R3yT-y3KX9-IMSBidnBkFE17c"
bot = telebot.TeleBot(MY_TOKEN, threaded=False)

# إعدادات كسر حماية العدد المحدود
YDL_OPTIONS = {
    'format': 'best',
    'quiet': True,
    'no_warnings': True,
    'extract_flat': False,
    'playlist_items': '1-100', # نجبره يبحث عن أول 100 عنصر
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'referer': 'https://www.snapchat.com/',
    'nocheckcertificate': True,
}

def handle_render():
    server_address = ('', 8080)
    httpd = http.server.HTTPServer(server_address, http.server.SimpleHTTPRequestHandler)
    httpd.serve_forever()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "أهلاً ماجد! تم تحديث النظام لسحب كامل الستوري (أكثر من 3 مقاطع). أرسل اليوزر أو الرابط الآن.")

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    input_text = message.text.strip()
    
    # تحديد الهدف (رابط مباشر أو يوزر)
    if "snapchat.com" not in input_text:
        target_url = f"https://www.snapchat.com/add/{input_text}"
    else:
        target_url = input_text

    wait_msg = bot.reply_to(message, "🔍 جاري استخراج كافة السنابات... قد يستغرق ذلك لحظات.")
    
    try:
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            # استخراج شامل
            info = ydl.extract_info(target_url, download=False)
            
            # التأكد من وجود قائمة مقاطع (Entries)
            entries = info.get('entries', [])
            
            # إذا كان الرابط لسنابة واحدة فقط وليس بروفايل كامل
            if not entries and info.get('url'):
                entries = [info]

            total_found = len(entries)
            if total_found == 0:
                bot.edit_message_text("❌ لم أجد سنابات عامة حالياً.", message.chat.id, wait_msg.message_id)
                return

            bot.edit_message_text(f"✅ تم العثور على {total_found} سنابة. جاري الإرسال...", message.chat.id, wait_msg.message_id)

            for i, entry in enumerate(entries, 1):
                m_url = entry.get('url')
                if not m_url: continue
                
                try:
                    # فحص النوع (صورة أو فيديو) وإرسال
                    if any(ext in m_url.lower() for ext in [".jpg", ".png", ".jpeg"]):
                        bot.send_photo(message.chat.id, m_url, caption=f"السنابة رقم [{i}]")
                    else:
                        bot.send_video(message.chat.id, m_url, caption=f"السنابة رقم [{i}]")
                except Exception:
                    continue # تخطي المقاطع المعطوبة

            bot.send_message(message.chat.id, f"✅ اكتمل التحميل. إجمالي ما تم إرساله: {total_found}")

    except Exception as e:
        bot.edit_message_text(f"❌ فشل السحب. الحساب قد يكون خاصاً أو الرابط غير صحيح.", message.chat.id, wait_msg.message_id)

if __name__ == "__main__":
    threading.Thread(target=handle_render, daemon=True).start()
    bot.infinity_polling()
