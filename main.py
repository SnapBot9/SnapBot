import os
import requests
from pyrogram import Client, filters

# بيانات البوت الأساسية
BOT_TOKEN = "8059225231:AAGCWo5MS2R3yT-y3KX9-IMSBidnBkFE17c"
# يفضل وضع الـ ID والـ Hash في Render، لكن سأضع لك قيم افتراضية مؤقتاً
API_ID = os.getenv("API_ID", "25726207") # استبدله بـ ID الخاص بك إذا كان مختلفاً
API_HASH = os.getenv("API_HASH", "824b2053676770287a2a6886866299f1") 

# مفاتيح الـ API (تأكد من إضافتها في Render Environment)
KEY_1 = os.getenv("NUMLOOKUP_KEY", "num_live_ofz3TgmJbL6Aw3udS3Jwh8WsStwY59ZnMq0JdNYR")
KEY_2 = os.getenv("SECONDARY_KEY", "KEY019D6896AD71FA419BB1C3434A54D4BD_UWNH4NORRUAHwERRFRvvwq")

app = Client("saudi_number_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

def format_num(n):
    """تنسيق الرقم للصيغة الدولية للسعودية"""
    n = n.strip().replace(" ", "").replace("+", "")
    if n.startswith("05") and len(n) == 10:
        return "966" + n[1:]
    if n.startswith("5") and len(n) == 9:
        return "966" + n
    return n

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply("أهلاً بك في بوت كاشف الأرقام 🇸🇦\nأرسل الرقم الذي تريد البحث عنه (مثال: 050xxxxxxx)")

@app.on_message(filters.text & filters.private)
async def handle_search(client, message):
    target = format_num(message.text)
    
    if not target.isdigit():
        await message.reply("الرجاء إرسال أرقام فقط.")
        return

    m = await message.reply(f"🔎 جاري الفحص دولياً للرقم: `{target}`...")
    
    try:
        # المحاولة بالمصدر الأول (المفتاح الذي أرسلته لي مؤخراً)
        # الرابط الافتراضي لمعظم مقدمي الـ API المشابهين لمفتاحك
        url = f"https://api.proweblook.com/v1/lookup?key={KEY_2}&number={target}"
        res = requests.get(url, timeout=10)
        data = res.json()
        
        name = data.get("name") or data.get("display_name")
        
        if name:
            response = f"✅ **تم العثور على النتيجة:**\n\n👤 الاسم: `{name}`\n📞 الرقم: `{target}`"
            await m.edit_text(response)
        else:
            # إذا لم يجد اسماً، يجرب المصدر الثاني (Numlookupapi)
            url2 = f"https://api.numlookupapi.com/v1/validate/{target}?apikey={KEY_1}"
            res2 = requests.get(url2, timeout=10)
            data2 = res2.json()
            carrier = data2.get("carrier", "غير معروف")
            await m.edit_text(f"لم نجد اسماً، لكن البيانات
