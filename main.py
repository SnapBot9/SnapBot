import telebot
from telebot import types
import yt_dlp
import threading
import http.server

# التوكن الخاص بك
MY_TOKEN = "8059225231:AAGCWo5MS2R3yT-y3KX9-IMSBidnBkFE17c"
bot = telebot.TeleBot(MY_TOKEN, threaded=False)

# إعدادات السحب القصوى لجلب كامل الستوري
YDL_OPTIONS = {
    'format': 'best',
    'quiet': True,
    'no_warnings': True,
    'extract_flat': False,
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'referer': 'https://www.snapchat.com/',
}

def handle_render():
    server_address = ('', 8080)
    httpd = http.server.HTTPServer(server_address, http.server.SimpleHTTPRequestHandler)
    httpd.serve_forever()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "أهلاً بك في بوت سحب ستوري السناب 👻\n\nأرسل الآن (اسم المستخدم) أو رابط الحساب مباشرة وسأقوم بسحب كامل القصص المتاحة لك.")

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    input_text = message.text.strip()
    
    # تحويل الإدخال إلى رابط حساب إذا كان يوزر فقط
    if "snapchat.com" not in input_text:
        target_url = f"https://www.snapchat.com/add/{input_text}"
    else:
        target_url = input_text

    wait_msg = bot.reply_to(message, "🔍 جاري فحص الحساب وسحب الستوريات... انتظر قليلاً.")
    
    try:
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            # استخراج معلومات الحساب والقصص
            info = ydl.extract_info(target_url, download=False)
            
            if 'entries' in info:
                entries = info['entries']
                total = len(entries)
                
                if total == 0:
                    bot.edit_message_text("❌ لا توجد قصص (ستوري) عامة متاحة حالياً لهذا الحساب.", message.chat.id, wait_msg.message_id)
                    return

                bot.edit_message_text(f"✅ تم العثور على {total} سنابة. جاري الإرسال بالترتيب...", message.chat.id, wait_msg.message_id)
                
                for index, entry in enumerate(entries, 1):
                    media_url = entry.get('url')
                    if media_url:
                        try:
                            # إرسال كفيديو أو صورة حسب النوع
                            if any(ext in media_url.lower() for ext in [".jpg", ".png", ".jpeg"]):
                                bot.send_photo(message.chat.id, media_url, caption=f"السنابة رقم [{index}]")
                            else:
                                bot.send_video(message.chat.id, media_url, caption=f"السنابة رقم [{index}]")
                        except:
                            continue # تخطي في حال فشل إرسال مقطع معين
                
                bot.send_message(message.chat.id, f"✅ انتهى تحميل الستوريات لـ {input_text}")
            else:
                # في حال كان الرابط لسنابة واحدة فقط
                media_url = info.get('url')
                bot.send_video(message.chat.id, media_url, caption="✅ تم تحميل المقطع.")
                bot.delete_message(message.chat.id, wait_msg.message_id)

    except Exception as e:
        bot.edit_message_text("❌ فشل السحب. تأكد من صحة اليوزر وأن الحساب يحتوي على ستوري عام (Public Story).", message.chat.id, wait_msg.message_id)

if __name__ == "__main__":
    threading.Thread(target=handle_render, daemon=True).start()
    bot.infinity_polling()
