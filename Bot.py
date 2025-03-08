import os
import logging
import ffmpeg
import pymongo
import gridfs
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackQueryHandler, Filters, CallbackContext

# Charger les variables d'environnement
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

# Configurer MongoDB
client = pymongo.MongoClient(MONGO_URI)
db = client["videobot"]
fs = gridfs.GridFS(db)

# Configurer le log
logging.basicConfig(level=logging.INFO)

# Qualité de compression
quality_options = {
    "low": {"size": "30%", "bitrate": "300k"},
    "medium": {"size": "50%", "bitrate": "500k"},
    "high": {"size": "80%", "bitrate": "1500k"}
}
selected_quality = "medium"

# Stockage temporaire des fichiers
STORAGE_DIR = "storage"
os.makedirs(STORAGE_DIR, exist_ok=True)

# Liste des admins et bannissements
admins = [ADMIN_ID]
banned_users = []

# 📌 Commande /start
def start(update: Update, context: CallbackContext):
    keyboard = [
        [
            InlineKeyboardButton("⚡️Faible", callback_data="low_quality"),
            InlineKeyboardButton("🔥Moyenne", callback_data="medium_quality"),
            InlineKeyboardButton("☀️Haute", callback_data="high_quality"),
        ],
        [InlineKeyboardButton("📂 Mon stockage", callback_data="storage")],
    ]
    update.message.reply_text("👋 *Bienvenue !*\nEnvoyez une vidéo pour la compresser.", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

# 📌 Commande /admin
def admin(update: Update, context: CallbackContext):
    if update.message.chat_id not in admins:
        update.message.reply_text("🚫 Accès refusé.")
        return
    keyboard = [
        [InlineKeyboardButton("➕ Ajouter Admin", callback_data="add_admin")],
        [InlineKeyboardButton("🚫 Bannir un utilisateur", callback_data="ban_user")],
        [InlineKeyboardButton("📢 Faire une annonce", callback_data="send_announcement")],
        [InlineKeyboardButton("📊 Voir Statistiques", callback_data="stats")],
    ]
    update.message.reply_text("⚙️ *Panneau Admin*", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

# 📌 Gestion des boutons (choix de la qualité)
def button_handler(update: Update, context: CallbackContext):
    global selected_quality
    query = update.callback_query
    data = query.data
    if data in quality_options:
        selected_quality = data
        query.edit_message_text(f"✅ Qualité {data.capitalize()} sélectionnée.")

# 📌 Stockage MongoDB GridFS
def store_video(file_path):
    with open(file_path, "rb") as f:
        return fs.put(f, filename=os.path.basename(file_path))

def retrieve_video(file_id, output_path):
    file_data = fs.get(file_id)
    with open(output_path, "wb") as f:
        f.write(file_data.read())

# 📌 Diviser une vidéo trop grande
def split_video(input_path, output_prefix, chunk_size=100):
    file_size = os.path.getsize(input_path) / (1024 * 1024)
    if file_size <= chunk_size:
        return [input_path]
    print("🔹 Division de la vidéo...")
    os.system(f"ffmpeg -i {input_path} -c copy -segment_time 300 -f segment -reset_timestamps 1 {output_prefix}%03d.mp4")
    return [f"{output_prefix}{i:03d}.mp4" for i in range(int(file_size // chunk_size) + 1)]

# 📌 Compression vidéo
def compress_video(input_path, output_path, quality="medium"):
    options = quality_options[quality]
    ffmpeg.input(input_path).output(output_path, vf=f"scale=-2:{options['size']}", **{"b:v": options["bitrate"]}).run(overwrite_output=True)

# 📌 Gestion des vidéos envoyées
def video_handler(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    if chat_id in banned_users:
        update.message.reply_text("🚫 Vous êtes banni.")
        return

    video_file = update.message.video
    file_size_mb = video_file.file_size / (1024 * 1024)

    # Télécharger la vidéo
    input_path = os.path.join(STORAGE_DIR, "input.mp4")
    output_path = os.path.join(STORAGE_DIR, "output.mp4")
    file = context.bot.getFile(video_file.file_id)
    file.download(input_path)

    update.message.reply_text("⏳ Compression en cours...")

    try:
        if file_size_mb > 200:  # Diviser si > 200 Mo
            parts = split_video(input_path, os.path.join(STORAGE_DIR, "split"))
            for part in parts:
                compress_video(part, output_path, selected_quality)
                context.bot.send_video(chat_id, video=open(output_path, "rb"))
        else:
            compress_video(input_path, output_path, selected_quality)
            context.bot.send_video(chat_id, video=open(output_path, "rb"))

        update.message.reply_text("✅ Compression terminée !")
        os.remove(input_path)
        os.remove(output_path)

    except Exception as e:
        update.message.reply_text(f"❌ Erreur : {str(e)}")

# 📌 Annonce admin
def send_announcement(update: Update, context: CallbackContext):
    if update.message.chat_id not in admins:
        update.message.reply_text("🚫 Accès refusé.")
        return

    announcement = " ".join(context.args)
    if not announcement:
        update.message.reply_text("📢 Utilisation : /send_announcement [message]")
        return

    for user in admins:
        try:
            context.bot.send_message(user, f"📢 Annonce : {announcement}")
        except Exception:
            pass

    update.message.reply_text("✅ Annonce envoyée.")

# 📌 Initialisation du bot
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("admin", admin))
    dp.add_handler(CommandHandler("send_announcement", send_announcement))
    dp.add_handler(CallbackQueryHandler(button_handler))
    dp.add_handler(MessageHandler(Filters.video, video_handler))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
