# Fichier : main.py
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import json
import os

from core.xray_handler import create_vless_user
from core.ssh_handler import create_ssh_user
from utils.qr_generator import generate_vpn_qr

CONFIG_FILE = "/root/doty_bot/config.json"

if not os.path.exists(CONFIG_FILE):
    print("Erreur: config.json introuvable.")
    exit(1)

with open(CONFIG_FILE, "r") as f:
    config = json.load(f)

bot = telebot.TeleBot(config.get("BOT_TOKEN"))

def is_admin(user_id):
    with open(CONFIG_FILE, "r") as f:
        current_config = json.load(f)
    return user_id in current_config.get("ADMINS", [])

# --- MENU PRINCIPAL ---
@bot.message_handler(commands=['start', 'menu'])
def send_welcome(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "⛔ Accès refusé.")
        return

    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🟢 Xray (Vless/Vmess)", callback_data="menu_xray"),
        InlineKeyboardButton("🔵 SSH / OpenVPN", callback_data="menu_ssh"),
        InlineKeyboardButton("🟣 ZIVPN / SlowDNS", callback_data="menu_udp"),
        InlineKeyboardButton("📊 Statut du Serveur", callback_data="menu_status")
    )
    bot.send_message(message.chat.id, "🚀 *Panel de Contrôle Dotycat*\nSélectionnez une option :", parse_mode="Markdown", reply_markup=markup)

# --- ROUTEUR DE BOUTONS ---
@bot.callback_query_handler(func=lambda call: True)
def callback_manager(call):
    if not is_admin(call.from_user.id):
        return

    # --- SOUS-MENUS ---
    if call.data == "menu_xray":
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("➕ Créer Vless", callback_data="action_create_vless"),
            InlineKeyboardButton("🔙 Retour Menu", callback_data="menu_main")
        )
        bot.edit_message_text("🟢 *Gestion Xray*\nQue voulez-vous faire ?", call.message.chat.id, call.message.message_id, parse_mode="Markdown", reply_markup=markup)

    elif call.data == "menu_ssh":
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("➕ Créer compte SSH", callback_data="action_create_ssh"),
            InlineKeyboardButton("🔙 Retour Menu", callback_data="menu_main")
        )
        bot.edit_message_text("🔵 *Gestion SSH & SOCKS*", call.message.chat.id, call.message.message_id, parse_mode="Markdown", reply_markup=markup)

    # --- ACTIONS RÉELLES (CRÉATION) ---
    elif call.data == "action_create_vless":
        bot.answer_callback_query(call.id, "Génération en cours...")
        
        username = "User_VIP_" + str(os.urandom(2).hex())
        bug_host = config.get("BUG_HOST", "bug.cdn.com")
        
        success, result = create_vless_user(username, bug_host)
        
        if success:
            vless_link = result
            qr_path = generate_vpn_qr(vless_link, username)
            
            with open(qr_path, 'rb') as photo:
                bot.send_photo(
                    call.message.chat.id, 
                    photo, 
                    caption=f"✅ *Compte VLESS Créé*\n👤 Utilisateur: `{username}`\n\n`{vless_link}`", 
                    parse_mode="Markdown"
                )
            os.remove(qr_path)
        else:
            bot.send_message(call.message.chat.id, f"❌ Erreur: {result}")

    elif call.data == "action_create_ssh":
        bot.answer_callback_query(call.id, "Génération en cours...")
        username = "ssh_" + str(os.urandom(2).hex())
        password = "123" # Dans une version finale, on demandera le mot de passe
        
        success, result = create_ssh_user(username, password)
        if success:
            bot.send_message(call.message.chat.id, f"✅ *Compte SSH Créé*\n👤 Utilisateur: `{username}`\n🔑 Pass: `{password}`\n\n📌 Prêt pour le tunnel SSH/WS.", parse_mode="Markdown")
        else:
            bot.send_message(call.message.chat.id, f"❌ Erreur: {result}")

    elif call.data == "menu_main":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        send_welcome(call.message)

if __name__ == '__main__':
    print("Bot en ligne...")
    bot.infinity_polling()
  
