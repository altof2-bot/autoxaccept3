import json
import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ChatJoinRequestHandler, filters, ContextTypes
from keep_alive import keep_alive

TOKEN = "7733018409:AAEbDTiRTrs4Os7ZQUzaAVCPS-7QFG9mwTs"
ADMIN_ID = 5116530698  # Remplace par ton ID Telegram
USERS_FILE = "users.json"

# ========== Utilisateurs ==========
def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return []

def save_user(user_id):
    users = load_users()
    if user_id not in users:
        users.append(user_id)
        with open(USERS_FILE, "w") as f:
            json.dump(users, f)

# ========== Commande /start ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    save_user(user_id)

    keyboard = [
        [InlineKeyboardButton("➕ Add to Group 💬", url=f"https://t.me/{context.bot.username}?startgroup=true")],
        [InlineKeyboardButton("👑 Add to Channel 📢", url=f"https://t.me/{context.bot.username}")],
        [InlineKeyboardButton("🔄 Update 📲", url="https://t.me/originstation")],
        [InlineKeyboardButton("❓ HOW TO USE 📖", url="https://t.me/originstation/9")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("👋 Bienvenue ! Utilisez les boutons ci-dessous pour configurer le bot :", reply_markup=reply_markup)

# ========== Auto accept group ==========
async def auto_accept_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        for member in update.message.new_chat_members:
            username = member.username
            user_id = member.id
            save_user(user_id)

            keyboard = [[InlineKeyboardButton("JOIN", url="https://t.me/originstation")]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await context.bot.send_message(chat_id=user_id, text=f"👋 Bienvenue @{username} !\nCliquez sur le bouton ci-dessous pour rejoindre et vous informer :", reply_markup=reply_markup)
    except Exception as e:
        print(f"Erreur message privé groupe : {e}")

# ========== Auto accept channel ==========
async def auto_accept_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        chat_id = update.chat_join_request.chat.id
        user_id = update.chat_join_request.from_user.id
        save_user(user_id)

        await context.bot.approve_chat_join_request(chat_id=chat_id, user_id=user_id)

        keyboard = [[InlineKeyboardButton("JOIN", url="https://t.me/originstation")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await context.bot.send_message(chat_id=user_id, text=f"🎉 Félicitations, votre demande d'accès a été acceptée !\nCliquez sur le bouton ci-dessous pour rejoindre et en savoir plus :", reply_markup=reply_markup)
    except Exception as e:
        print(f"Erreur canal : {e}")

# ========== Commande /broadcast ==========
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ Tu n'es pas autorisé.")
        return

    if not context.args:
        await update.message.reply_text("Utilisation : /broadcast Votre message ici")
        return

    msg = " ".join(context.args)
    users = load_users()
    count = 0

    for user_id in users:
        try:
            await context.bot.send_message(chat_id=user_id, text=msg)
            count += 1
        except:
            pass

    await update.message.reply_text(f"✅ Message envoyé à {count} utilisateurs.")

# ========== Commande /sponsor ==========
async def sponsor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ Tu n'es pas autorisé.")
        return

    if not context.args:
        await update.message.reply_text("Utilisation : /sponsor Votre message sponsorisé ici")
        return

    sponsor_msg = " ".join(context.args)
    sent = await update.message.reply_text(sponsor_msg)

    # Supprimer après 30 minutes (1800 secondes)
    async def delete_later(chat_id, message_id):
        await asyncio.sleep(1800)
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
        except:
            pass

    asyncio.create_task(delete_later(sent.chat_id, sent.message_id))

# ========== Main ==========
def main():
    keep_alive()
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CommandHandler("sponsor", sponsor))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, auto_accept_group))
    app.add_handler(ChatJoinRequestHandler(auto_accept_channel))

    app.run_polling()

if __name__ == "__main__":
    main()