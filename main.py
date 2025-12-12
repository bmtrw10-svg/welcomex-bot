import os

from telegram import Update
from telegram.ext import Application, ContextTypes, CommandHandler, MessageHandler, filters
from telegram.constants import ChatMember

BOT_TOKEN = os.environ.get("BOT_TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
PORT = int(os.environ.get("PORT", 10000))

# === GROUP RULES (Edit as needed) ===
RULES = """
Group Rules:
1. Be respectful.
2. No spam or ads.
3. Follow topic.
4. No harassment.
"""

# === CAPTCHA (Simple math) ===
captcha = defaultdict(dict)

async def welcome_new(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        await update.message.reply_text(f"Welcome, {member.first_name}! {RULES}\n\nTo verify you're human, what's 2 + 2?")
        captcha[update.effective_chat.id] = {"user": member.id, "answer": "4"}

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    if chat_id in captcha and user_id == captcha[chat_id]["user"]:
        if text.strip() == captcha[chat_id]["answer"]:
            await update.message.reply_text("Verified! Enjoy the group.")
            del captcha[chat_id]
        else:
            await update.message.delete()
            await update.effective_chat.ban_member(user_id)
        return

    # Normal messages (optional - ignore if not needed)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("WelcomeX bot ready. Add me to your group as admin to greet new members.")

app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.STATUS_UPDATE.NEW_CHAT_MEMBERS, welcome_new))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
app.add_handler(CommandHandler("start", start))

if __name__ == "__main__":
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path="/webhook",
        webhook_url=WEBHOOK_URL
    )

