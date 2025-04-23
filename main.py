from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ChatJoinRequestHandler, filters
from keep_alive import keep_alive

TOKEN = "7733018409:AAEbDTiRTrs4Os7ZQUzaAVCPS-7QFG9mwTs"
ADMIN_IDS = [7886987683, 5116530698]  

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
        "📌 Ce bot vous permet de gérer automatiquement les demandes d'adhésion aux groupes et canaux. "
        "Utilisez les boutons ci-dessous pour accéder aux différentes fonctionnalités disponibles !\n\n"
        "🔹 **Admin commandes**:\n"
        "📢 **Envoyer un message à tous** ➝ `/send_all`\n"
        "📊 **Voir les statistiques** ➝ `/view_stats`",
        reply_markup=reply_markup
    )

async def send_message_to_all(update: Update, context):
    if update.effective_user.id in ADMIN_IDS:
        users = context.bot_data.get("users", [])
        for user_id in users:
            try:
                await context.bot.send_message(chat_id=user_id, text="📢 Annonce pour tous les utilisateurs !")
            except Exception as e:
                print(f"Erreur en envoyant le message à {user_id}: {e}")
    else:
        await update.message.reply_text("🚫 Vous n'avez pas accès à cette commande.")

async def view_stats(update: Update, context):
    if update.effective_user.id in ADMIN_IDS:
        users = context.bot_data.get("users", [])
        total_users = len(users)
        await update.message.reply_text(f"📊 Nombre total d'utilisateurs: {total_users}")
    else:
        await update.message.reply_text("🚫 Vous n'avez pas accès à cette commande.")

async def track_new_users(update: Update, context):
    user_id = update.effective_user.id
    users = context.bot_data.get("users", [])
    if user_id not in users:
        users.append(user_id)
        context.bot_data["users"] = users

def main():
    keep_alive()
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, track_new_users))
    app.add_handler(CommandHandler("send_all", send_message_to_all))
    app.add_handler(CommandHandler("view_stats", view_stats))

    app.run_polling()

if __name__ == "__main__":
    main()