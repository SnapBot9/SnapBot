import telebot
from telebot import types
import yt_dlp
import threading
import http.server
import os

# التوكن الخاص بك
MY_NEW_TOKEN = "8059225231:AAGCWo5MS2R3yT-y3KX9-IMSBidnBkFE17c"
bot = telebot.TeleBot(MY_NEW_TOKEN, threaded=False)
bot.remove_webhook()

user_links = {}

# إعدادات محسنة لجلب القصة كاملة بدون استثناءات
YDL_OPTIONS = {
    'format': 'best',
    'quiet': True,
    'no_warnings': True,
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'referer': 'https://www.snapchat.com/',
    'extract_flat': False,
    'force_generic_extractor': False,
}

def handle_render():
    server_address = ('', 8080)
    httpd = http.server.HTTPServer(server_address, http.server.SimpleHTTPRequestHandler)
    httpd.serve_forever()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "أهلاً ماجد! تم تحديث محرك السحب لضمان جلب كافة السنابات بالترتيب. أرسل الرابط الآن.")

@bot.message_handler(func=lambda message: "snapchat.com" in message.text)
def ask_options(message):
    user_links[message.chat.id] = message.text
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("تحميل السنابة المطلوبة 🎯", callback_data="single_v"),
        types.InlineKeyboardButton("تحميل القصة كاملة 🎞️", callback_data="split_v")
    )
    bot.reply_to(message, "تم استلام الرابط! اختر نوع السحب:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    url = user_links.get(chat_id)
    if not url: return

    # --- خيار 1: تحميل السنابة المحددة بالضبط ---
    if call.data == "single_v":
        bot.edit_message_text("⏳ جاري البحث عن السنابة المحددة...", chat_id, call.message.message_id)
        try:
            # استخراج معرف السنابة من الرابط (الموجود بعد /t/)
            target_id = url.split('/')[-1].split('?')[0]
            with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(url, download=False)
                found = False
                if 'entries' in info:
                    for entry in info['entries']:
                        # البحث عن المعرف في روابط المدخلات
                        if target_id in entry.get('url', '') or target_id in entry.get('id', ''):
                            media_url = entry.get('url')
                            if ".jpg" in media_url or ".png" in media_url:
                                bot.send_photo(chat_id, media_url, caption="✅ تم سحب الصورة المطلوبة!")
                            else:
                                bot.send_video(chat_id, media_url, caption="✅ تم سحب المقطع المطلوب!")
                            found = True
                            break
                
                if not found:
                    # إذا لم يجد تطابقاً، يسحب العنصر الحالي المتاح
                    media_url = info.get('url') or info['entries'][0].get('url')
                    bot.send_video(chat_id, media_url, caption="✅ تم سحب المقطع المتاح.")
        except:
            bot.send_message(chat_id, "❌ فشل سحب السنابة المحددة.")

    # --- خيار 2: تحميل القصة كاملة بالترتيب ---
    elif call.data == "split_v":
        bot.edit_message_text("📦 جاري سحب كافة محتويات القصة... يرجى الانتظار.", chat_id, call.message.message_id)
        try:
            with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(url, download=False)
                if 'entries' in info:
                    count = 0
                    for entry in info['entries']:
                        media_url = entry.get('url')
                        if media_url:
                            if any(ext in media_url.lower() for ext in [".jpg", ".png", ".jpeg"]):
                                bot.send_photo(chat_id, media_url)
                            else:
                                bot.send_video(chat_id, media_url)
                            count += 1
                    bot.send_message(chat_id, f"✅ اكتمل السحب! إجمالي العناصر: {count}")
                else:
                    bot.send_message(chat_id, "ℹ️ لم أجد قصة كاملة في هذا الرابط، سأرسل المقطع المتاح فقط.")
                    bot.send_video(chat_id, info.get('url'))
        except Exception as e:
            bot.send_message(chat_id, "⚠️ حدث خطأ أثناء سحب القصة.")

if __name__ == "__main__":
    threading.Thread(target=handle_render, daemon=True).start()
    bot.infinity_polling()
