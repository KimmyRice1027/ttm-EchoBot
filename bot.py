import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# Logging စနစ် သတ်မှတ်ခြင်း (Errors တွေ ကြည့်လို့ရအောင်)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# စာပို့လာရင် ပြန်ဖြေမည့် Function (Echo လုပ်မည့် Function)
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    # ပို့လိုက်တဲ့ စာကို အတူတူ ပြန်ပို့ပေးမည်
    await update.message.reply_text(user_text)

if __name__ == '__main__':
    # Render က ပေးမယ့် Port ကို ဖမ်းယူရန် (Render အတွက် လိုအပ်ပါသည်)
    PORT = int(os.environ.get('PORT', 8443))
    
    # Environment Variable ကနေ Bot Token ကို ယူမည်
    TOKEN = os.environ.get('BOT_TOKEN')
    
    if not TOKEN:
        raise ValueError("BOT_TOKEN environment variable is missing!")

    # Application တည်ဆောက်ခြင်း
    application = ApplicationBuilder().token(TOKEN).build()

    # စာလာရင် echo function ဆီ ပို့ရန် 
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    application.add_handler(echo_handler)

    # Webhook ဖြင့် Render ပေါ်တွင် Run ရန်
    # Render URL ကို ဖြည့်ရပါမည် (ဥပမာ - https://your-app-name.onrender.com)
    RENDER_EXTERNAL_URL = os.environ.get('RENDER_EXTERNAL_URL')
    
    if RENDER_EXTERNAL_URL:
        webhook_url = f"{RENDER_EXTERNAL_URL}/{TOKEN}"
        print(f"Starting webhook on port {PORT} with URL {webhook_url}")
        
        application.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=TOKEN,
            webhook_url=webhook_url
        )
    else:
        # Local မှာ စမ်းချင်ရင် Polling နဲ့ သုံးလို့ရပါတယ်
        print("Starting polling...")
        application.run_polling()