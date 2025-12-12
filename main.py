import os

from telegram import Update, ChatMember
from telegram.ext import Application, ContextTypes, CommandHandler, MessageHandler, filters
from telegram.constants import ParseMode

BOT_TOKEN = os.environ.get("BOT_TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
PORT = int(os.environ.get("PORT", 10000))

# === RULES ===
RULES = """
Group Rules:
• Be respectful to all members.
• No spam or ads.
• Stay on topic.
• No harassment.
"""

# === CAPTCHA ===
captcha = defaultdict(dict)

async def welcome_new(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        await update.message.reply_text(f"Welcome, {member.first_name}! We're glad you're here. Here's our rules:\n{RULES}\n\nTo verify you're human (anti-spam), what's 2 + 2?")
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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("WelcomeX bot ready. Add me to your group as admin to greet new members with rules and CAPTCHA.")

app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new))  # FIXED: StatusUpdate (correct case)
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
app.add_handler(CommandHandler("start", start))

if __name__ == "__main__":
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path="/webhook",
        webhook_url=WEBHOOK_URL
    )
