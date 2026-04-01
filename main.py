import telebot
from telebot import types
import yt_dlp
import threading
import http.server
import os
import time

# التوكن الخاص بك
MY_NEW_TOKEN = "8059225231:AAGCWo5MS2R3yT-y3KX9-IMSBidnBkFE17c"
bot = telebot.TeleBot(MY_NEW_TOKEN, threaded=False)
bot.remove_webhook()

# قاموس لحفظ روابط المستخدمين مؤقتاً
user_links = {}

# سيرفر وهمي لإبقاء الخدمة تعمل على Render
def handle_render():
    server_address = ('', 8080)
    httpd = http.server.HTTPServer(server_address, http.server.SimpleHTTPRequestHandler)
    httpd.serve_forever()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    # رسالة الترحيب بـ Welcome كما طلبت
    welcome_text = (f"Welcome {message.from_user.first_name}! 👻\n\n"
                    "أرسل لي رابط سناب شات (Story أو Spotlight) وسأقوم بسحب الفيديو لك مباشرة.")
    bot.reply_to(message, welcome_text)

@bot.message_handler(func=lambda message: "snapchat.com" in message.text)
def ask_options(message):
    # حفظ الرابط في الذاكرة لربطه بالأزرار
    user_links[message.chat.id] = message.text
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn1 = types.InlineKeyboardButton("تحميل هذا المقطع فقط 📥", callback_data="single_v")
    btn2 = types.InlineKeyboardButton("دمج القصة كاملة (قريباً) 🔄", callback_data="merge_v")
    markup.add(btn1, btn2)
    
    bot.reply_to(message, "وصل الرابط! اختر طريقة التحميل المطلوبة:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    url = user_links.get(chat_id)
    
    if not url:
        bot.send_message(chat_id, "⚠️ انتهت صلاحية الرابط، يرجى إرساله مرة أخرى.")
        return

    if call.data == "single_v":
        bot.edit_message_text("⏳ جاري محاولة سحب الفيديو... يرجى الانتظار.", chat_id, call.message.message_id)
        
        try:
            # إعدادات متقدمة لتمويه البوت كأنه متصفح آيفون لفك حظر سناب
            ydl_opts = {
                'format': 'best',
                'quiet': True,
                'no_warnings': True,
                'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
                'referer': 'https://www.snapchat.com/',
                'add_header': [
                    'Accept-Language: en-US,en;q=0.9',
                    'Connection: keep-alive'
                ],
                'extract_flat': False,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                video_url = info.get('url')
                
                if video_url:
                    bot.send_video(chat_id, video_url, caption="✅ تم سحب المقطع بنجاح!")
                else:
                    bot.send_message(chat_id, "❌ فشل استخراج الفيديو. تأكد أن الحساب عام (Public).")
                    
        except Exception as e:
            bot.send_message(chat_id, "⚠️ سناب شات يرفض الاتصال حالياً. جرب رابط Spotlight أو حاول لاحقاً.")
            print(f"Error details: {e}")

    elif call.data == "merge_v":
        bot.edit_message_text("🎬 ميزة الدمج قيد البرمجة، سيتم إضافتها فور انتهاء الاختبارات.", chat_id, call.message.message_id)

if __name__ == "__main__":
    # تشغيل السيرفر الوهمي في خلفية الكود
    threading.Thread(target=handle_render, daemon=True).start()
    print("البوت يعمل الآن بأحدث نسخة...")
    bot.infinity_polling(timeout=20, long_polling_timeout=10)
