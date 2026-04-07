import os
import requests
from pyrogram import Client, filters

# سحب الإعدادات من Render Environment Variables
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
KEY_1 = os.getenv("NUMLOOKUP_KEY")
KEY_2 = os.getenv("SECONDARY_KEY")

app = Client("saudi_number_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# دالة التنسيق السعودي
def format_num(n):
    n = n.strip().replace(" ", "").replace("+", "")
    return "966" + n[1:] if n.startswith("05") else n

@app.on_message(filters.text & filters.private)
async def handle(client, message):
    target = format_num(message.text)
    m = await message.reply("⚡️ جاري الفحص...")
    
    # محاولة جلب الاسم من المصدر الثاني (المفتاح الذي واجهت فيه مشكلة)
    try:
        # ملاحظة: تأكد من رابط الـ API الصحيح للمزود الخاص بك
        res = requests.get(f"https://api.proweblook.com/v1/lookup?key={KEY_2}&number={target}", timeout=10)
        data = res.json()
        name = data.get("name") or data.get("display_name")
        
        if name:
            await m.edit_text(f"✅ تم العثور على الاسم:\n👤 {name}")
        else:
            await m.edit_text("❌ لم يتم العثور على اسم، جرب رقم آخر.")
    except Exception as e:
        await m.edit_text("⚠️ حدث خطأ في الاتصال بالمزود.")

app.run()
