import os
import telebot

TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "أهلاً بك! تم الربط مع Render بنجاح. أرسل رابط السناب.")

@bot.message_handler(func=lambda message: True)
def handle_all(message):
    if "snapchat.com" in message.text:
        bot.reply_to(message, "وصل الرابط! جاري العمل على محرك السحب...")
    else:
        bot.reply_to(message, "أرسل رابط سناب شات صحيح.")

if __name__ == "__main__":
    bot.infinity_polling()
