import telebot
from telebot import types
import yt_dlp
import threading
import http.server
import os

# التوكن الخاص بك
MY_NEW_TOKEN = "8059225231:AAGCWo5MS2R3yT-y3KX9-IMSBidnBkFE17c"
bot = telebot.TeleBot(MY_NEW_TOKEN, threaded=False)

# إعدادات لكسر حاجز الـ 4 عناصر وسحب كل القصة
YDL_OPTIONS = {
    'format': 'best',
    'quiet': True,
    'no_warnings': True,
    'extract_flat': False, # لضمان الدخول لعمق القصة
    'playlist_items': '1-100', # نأمر المكتبة بسحب أول 100 عنصر بدلاً من الاكتفاء بالبداية
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
}

def handle_render():
    server_address = ('', 8080)
    httpd = http.server.HTTPServer(server_address, http.server.SimpleHTTPRequestHandler)
    httpd.serve_forever()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "تم تحديث النظام لسحب القصة كاملة (حتى 100 عنصر) وتحديد السنابة المطلوبة بدقة 🎯")

@bot.message_handler(func=lambda message: "snapchat.com" in message.text)
def ask_options(message):
    user_links[message.chat.id] = message.text
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("🎯 تحميل السنابة اللي أرسلتها بالضبط", callback_data="single_v"),
        types.InlineKeyboardButton("🎞️ تحميل القصة كاملة (بدون حدود)", callback_data="split_v")
    )
    bot.reply_to(message, "الرابط جاهز، اختر نوع السحب:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    url = user_links.get(chat_id)
    if not url: return

    if call.data == "single_v":
        bot.edit_message_text("⏳ جاري تحديد السنابة المطلوبة من القصة...", chat_id, call.message.message_id)
        try:
            target_id = url.split('/')[-1].split('?')[0]
            with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(url, download=False)
                entries = info.get('entries', [info])
                found_item = None
                for entry in entries:
                    if target_id in entry.get('url', '') or target_id in entry.get('id', ''):
                        found_item = entry
                        break
                
                if not found_item: found_item = entries[0] # احتياطي

                m_url = found_item.get('url')
                if any(x in m_url for x in [".jpg", ".png", "webp"]):
                    bot.send_photo(chat_id, m_url, caption="✅ السنابة المطلوبة (صورة)")
                else:
                    bot.send_video(chat_id, m_url, caption="✅ السنابة المطلوبة (فيديو)")
        except:
            bot.send_message(chat_id, "❌ فشل سحب المقطع المحدد.")

    elif call.data == "split_v":
        bot.edit_message_text("📦 جاري جرد كافة عناصر القصة... انتظر قليلاً.", chat_id, call.message.message_id)
        try:
            with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(url, download=False)
                entries = info.get('entries', [])
                if not entries:
                    bot.send_video(chat_id, info.get('url'))
                    return
                
                count = 0
                for entry in entries:
                    m_url = entry.get('url')
                    if not m_url: continue
                    try:
                        if any(x in m_url.lower() for x in [".jpg", ".png", ".jpeg"]):
                            bot.send_photo(chat_id, m_url)
                        else:
                            bot.send_video(chat_id, m_url)
                        count += 1
                    except: continue
                
                bot.send_message(chat_id, f"✅ اكتمل السحب! تم إرسال {count} عنصر من القصة.")
        except:
            bot.send_message(chat_id, "⚠️ خطأ في سحب القصة كاملة.")

if __name__ == "__main__":
    user_links = {}
    threading.Thread(target=handle_render, daemon=True).start()
    bot.infinity_polling()
