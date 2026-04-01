import telebot
from telebot import types
import yt_dlp
import threading
import http.server

# التوكن الخاص بك
MY_TOKEN = "8059225231:AAGCWo5MS2R3yT-y3KX9-IMSBidnBkFE17c"
bot = telebot.TeleBot(MY_TOKEN, threaded=False)

# إعدادات لفك قيود العدد (السر هنا في تجنب الحظر وجمع الروابط)
YDL_OPTIONS = {
    'format': 'best',
    'quiet': True,
    'no_warnings': True,
    'extract_flat': 'in_playlist', # تجبره على جلب كل محتوى القائمة
    'playlist_items': '1-50', # نرفع العدد لـ 50 لضمان سحب القصة كاملة
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'referer': 'https://www.snapchat.com/',
    'sleep_interval': 1, # ننتظر ثانية بين كل عملية سحب لتجنب قيود سناب شات
}

def handle_render():
    server_address = ('', 8080)
    httpd = http.server.HTTPServer(server_address, http.server.SimpleHTTPRequestHandler)
    httpd.serve_forever()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "أهلاً ماجد! تم تحديث محرك السحب لفك قيد الـ 3 مقاطع. أرسل اليوزر الآن.")

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    input_text = message.text.strip()
    
    if "snapchat.com" not in input_text:
        target_url = f"https://www.snapchat.com/add/{input_text}"
    else:
        target_url = input_text

    wait_msg = bot.reply_to(message, "⚙️ جاري كسر قيود سناب شات وجلب القصة كاملة... انتظر لحظات.")
    
    try:
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            # استخراج شامل مع معالجة الأخطاء
            info = ydl.extract_info(target_url, download=False)
            
            # جلب العناصر سواء كانت في قائمة أو مفردة
            entries = []
            if 'entries' in info:
                entries = list(info['entries'])
            else:
                entries = [info]

            total_found = len(entries)
            
            if total_found == 0:
                bot.edit_message_text("❌ لم يتم العثور على أي سنابات. قد يكون الحساب خاصاً.", message.chat.id, wait_msg.message_id)
                return

            bot.edit_message_text(f"✅ تم العثور على {total_found} سنابة. جاري الإرسال التدريجي...", message.chat.id, wait_msg.message_id)

            for i, entry in enumerate(entries, 1):
                # أحياناً يكون الرابط داخل 'url' وأحياناً يحتاج استخراج جديد
                m_url = entry.get('url') or entry.get('webpage_url')
                if not m_url: continue
                
                try:
                    # فحص نوع الملف وإرساله
                    if any(ext in m_url.lower() for ext in [".jpg", ".png", ".jpeg", "webp"]):
                        bot.send_photo(message.chat.id, m_url, caption=f"السنابة رقم [{i}]")
                    else:
                        bot.send_video(message.chat.id, m_url, caption=f"السنابة رقم [{i}]")
                except:
                    # إذا فشل الرابط المختصر، نحاول جلب الرابط المباشر للمقطع
                    try:
                        with yt_dlp.YoutubeDL({'format': 'best', 'quiet': True}) as ydl_inner:
                            inner_info = ydl_inner.extract_info(m_url, download=False)
                            bot.send_video(message.chat.id, inner_info['url'], caption=f"السنابة رقم [{i}]")
                    except:
                        continue 

            bot.send_message(message.chat.id, f"🏁 اكتمل سحب القصة. إجمالي العناصر: {total_found}")

    except Exception as e:
        bot.edit_message_text("⚠️ فشل السحب. سناب شات قد يفرض قيوداً مؤقتة، حاول مرة أخرى لاحقاً.", message.chat.id, wait_msg.message_id)

if __name__ == "__main__":
    threading.Thread(target=handle_render, daemon=True).start()
    bot.infinity_polling()
