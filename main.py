import telebot
from telebot import types
import yt_dlp
import threading
import http.server
import os

# التوكن
MY_NEW_TOKEN = "8059225231:AAGCWo5MS2R3yT-y3KX9-IMSBidnBkFE17c"
bot = telebot.TeleBot(MY_NEW_TOKEN, threaded=False)
bot.remove_webhook()

user_links = {}

# إعدادات متقدمة لمحاكاة متصفح حقيقي وتجاوز الحظر
YDL_OPTIONS = {
    'format': 'bestvideo+bestaudio/best',
    'quiet': True,
    'no_warnings': True,
    'ignoreerrors': True, # يتجاهل الصور المعطوبة ويستمر في البحث عن الفيديوهات
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'referer': 'https://www.snapchat.com/',
    'extract_flat': False, # تأكد من استخراج المحتوى بالكامل وليس العناوين فقط
}

def handle_render():
    server_address = ('', 8080)
    httpd = http.server.HTTPServer(server_address, http.server.SimpleHTTPRequestHandler)
    httpd.serve_forever()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "أهلاً بك! تم تحديث النظام لحل مشاكل الصور وفشل السحب. أرسل الرابط الآن.")

@bot.message_handler(func=lambda message: "snapchat.com" in message.text)
def ask_options(message):
    user_links[message.chat.id] = message.text
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("المقطع الحالي (محاولة قوية) 📥", callback_data="single_v"),
        types.InlineKeyboardButton("كل فيديوهات القصة (تخطي الصور) 🎞️", callback_data="split_v")
    )
    bot.reply_to(message, "اختر طريقة السحب:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    url = user_links.get(chat_id)
    
    if not url: return

    # --- حل مشكلة المقطع الفردي ---
    if call.data == "single_v":
        bot.edit_message_text("⏳ جاري محاولة السحب بأكثر من بروتوكول...", chat_id, call.message.message_id)
        try:
            with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(url, download=False)
                # التأكد من الحصول على رابط فيديو حقيقي
                video_url = info.get('url') or (info.get('entries')[0].get('url') if info.get('entries') else None)
                
                if video_url:
                    bot.send_video(chat_id, video_url, caption="✅ تم السحب بنجاح")
                else:
                    bot.send_message(chat_id, "❌ لم يتم العثور على فيديو في هذا الرابط (قد يكون صورة فقط).")
        except Exception as e:
            bot.send_message(chat_id, "⚠️ فشل السحب الفردي. سناب شات يرفض الاتصال من هذا السيرفر حالياً.")

    # --- حل مشكلة "تحميل الصور فقط" في القصة ---
    elif call.data == "split_v":
        bot.edit_message_text("🎞️ فحص القصة وتخطي الصور... لحظات.", chat_id, call.message.message_id)
        try:
            with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if 'entries' in info:
                    found_video = False
                    for entry in info['entries']:
                        # فحص إذا كان العنصر فيديو وليس صورة
                        if entry and 'url' in entry and ('.mp4' in entry['url'] or 'video' in entry.get('format', '')):
                            bot.send_video(chat_id, entry['url'])
                            found_video = True
                    
                    if not found_video:
                        bot.send_message(chat_id, "ℹ️ القصة تحتوي على صور فقط، ولا توجد فيديوهات لسحبها.")
                else:
                    bot.send_message(chat_id, "⚠️ لم نتمكن من العثور على قائمة مقاطع.")
        except:
            bot.send_message(chat_id, "❌ خطأ في فحص القصة.")

if __name__ == "__main__":
    threading.Thread(target=handle_render, daemon=True).start()
    bot.infinity_polling()
