from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ChatJoinRequestHandler, filters
from keep_alive import keep_alive

TOKEN = "7733018409:AAEbDTiRTrs4Os7ZQUzaAVCPS-7QFG9mwTs"

async def start(update: Update, context):
    keyboard = [
        [InlineKeyboardButton("➕ Add to Group 💬", url=f"https://t.me/{context.bot.username}?startgroup=true")],
        [InlineKeyboardButton("👑 Add to Channel 📢", url=f"https://t.me/{context.bot.username}")],
        [InlineKeyboardButton("🔄 Update 📲", url="https://t.me/originstation")],
        [InlineKeyboardButton("❓ HOW TO USE 📖", url="https://t.me/originstation/9")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("👋 Bienvenue ! Utilisez les boutons ci-dessous pour configurer le bot :", reply_markup=reply_markup)

async def auto_accept_group(update: Update, context):
    try:
        for member in update.message.new_chat_members:
            username = member.username
            user_id = member.id

            keyboard = [[InlineKeyboardButton("JOIN", url="https://t.me/originstation")]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await context.bot.send_message(chat_id=user_id, text=f"👋 Bienvenue @{username} !\nCliquez sur le bouton ci-dessous pour rejoindre et vous informer :", reply_markup=reply_markup)
    except Exception as e:
        print(f"Erreur lors de l'envoi du message privé : {e}")

async def auto_accept_channel(update: Update, context):
    try:
        chat_id = update.chat_join_request.chat.id
        user_id = update.chat_join_request.from_user.id

        await context.bot.approve_chat_join_request(chat_id=chat_id, user_id=user_id)

        keyboard = [[InlineKeyboardButton("JOIN", url="https://t.me/originstation")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await context.bot.send_message(chat_id=user_id, text=f"🎉 Félicitations, votre demande d'accès a été acceptée !\nCliquez sur le bouton ci-dessous pour rejoindre et en savoir plus :", reply_markup=reply_markup)
    except Exception as e:
        print(f"Erreur lors de l'acceptation dans le canal : {e}")

def main():
    keep_alive()
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, auto_accept_group))
    app.add_handler(ChatJoinRequestHandler(auto_accept_channel))

    app.run_polling()

if __name__ == "__main__":
    main()