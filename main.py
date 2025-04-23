from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ChatJoinRequestHandler, filters
from keep_alive import keep_alive

TOKEN = "7733018409:AAEbDTiRTrs4Os7ZQUzaAVCPS-7QFG9mwTs"
ADMIN_IDS = [7886987683, 5116530698]  
USER_LIST = set()  # Stocker les utilisateurs sous forme d'ensemble pour éviter les doublons

async def start(update: Update, context):
    keyboard = [
        [InlineKeyboardButton("➕ Ajouter au Groupe 💬", url=f"https://t.me/{context.bot.username}?startgroup=true")],
        [InlineKeyboardButton("👑 Ajouter au Canal 📢", url=f"https://t.me/{context.bot.username}")],
        [InlineKeyboardButton("🔄 Mise à jour 📲", url="https://t.me/originstation")],
        [InlineKeyboardButton("🆘 Support", url="https://t.me/sineur_x_bot")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "👋 Bienvenue sur notre bot ! 🎉\n\n"
        "Ce bot gère **automatiquement** les demandes d'adhésion aux groupes et canaux Telegram, "
        "sans intervention manuelle des administrateurs. "
        "Utilisez les boutons ci-dessous pour découvrir ses fonctionnalités.",
        reply_markup=reply_markup
    )

async def send_message_to_all(update: Update, context):
    if update.effective_user.id in ADMIN_IDS:
        if USER_LIST:
            for user_id in USER_LIST:
                try:
                    await context.bot.send_message(chat_id=user_id, text="📢 Annonce pour tous les utilisateurs !")
                except Exception as e:
                    print(f"Erreur en envoyant le message à {user_id}: {e}")
            await update.message.reply_text("✅ Message envoyé à tous les utilisateurs !")
        else:
            await update.message.reply_text("⚠️ Aucun utilisateur enregistré.")
    else:
        await update.message.reply_text("🚫 Vous n'avez pas accès à cette commande.")

async def view_stats(update: Update, context):
    if update.effective_user.id in ADMIN_IDS:
        total_users = len(USER_LIST)
        await update.message.reply_text(f"📊 Nombre total d'utilisateurs : {total_users}")
    else:
        await update.message.reply_text("🚫 Vous n'avez pas accès à cette commande.")

async def auto_accept_channel(update: Update, context):
    try:
        chat_id = update.chat_join_request.chat.id
        user_id = update.chat_join_request.from_user.id

        await context.bot.approve_chat_join_request(chat_id=chat_id, user_id=user_id)
        USER_LIST.add(user_id)

        keyboard = [[InlineKeyboardButton("🔹 Rejoindre le support", url="https://t.me/sineur_x_bot")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await context.bot.send_message(chat_id=user_id, text="🎉 Votre demande d'adhésion a été acceptée automatiquement ! Bienvenue 👋", reply_markup=reply_markup)
    except Exception as e:
        print(f"Erreur lors de l'acceptation automatique : {e}")

async def track_new_users(update: Update, context):
    user_id = update.effective_user.id
    USER_LIST.add(user_id)

def main():
    keep_alive()
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, track_new_users))
    app.add_handler(ChatJoinRequestHandler(auto_accept_channel))
    app.add_handler(CommandHandler("send_all", send_message_to_all))
    app.add_handler(CommandHandler("view_stats", view_stats))

    app.run_polling()

if __name__ == "__main__":
    main()