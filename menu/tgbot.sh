#!/bin/bash
# Fichier : menu/tgbot.sh
# Rôle : Interface Terminal pour installer et gérer le Bot Telegram

clear
echo -e "\e[36m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\e[0m"
echo -e "\e[32m      🤖 GESTIONNAIRE BOT TELEGRAM        \e[0m"
echo -e "\e[36m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\e[0m"
echo -e "\e[33mCe module relie votre serveur VPN à Telegram.\e[0m"
echo -e "\e[33mIl tournera 24h/24 et 7j/7 en arrière-plan.\e[0m"
echo ""

# Demander les informations à l'utilisateur directement dans le terminal
read -p "👉 Entrez le Token de votre Bot : " BOT_TOKEN
read -p "👉 Entrez votre ID Telegram (Admin) : " ADMIN_ID

echo ""
echo -e "\e[34m[1/4] Installation des prérequis Python...\e[0m"
apt-get update -y &>/dev/null
apt-get install python3 python3-pip unzip zip qrencode -y &>/dev/null
pip3 install pyTelegramBotAPI psutil qrcode pillow &>/dev/null

echo -e "\e[34m[2/4] Création de l'architecture du Bot...\e[0m"
mkdir -p /root/doty_bot/core
mkdir -p /root/doty_bot/utils
mkdir -p /root/doty_bot/tg_interface

# Création du fichier de configuration sécurisé
cat <<EOF > /root/doty_bot/config.json
{
  "BOT_TOKEN": "$BOT_TOKEN",
  "ADMINS": [$ADMIN_ID],
  "BUG_HOST": "bug.cdn.com"
}
EOF

echo -e "\e[34m[3/4] Téléchargement des modules depuis GitHub...\e[0m"
# URL de ton dossier source sur GitHub
REPO_URL="https://raw.githubusercontent.com/tchindaazice/Script-hysteria-and-any-other/main/doty_bot_source"

wget -q -O /root/doty_bot/main.py $REPO_URL/main.py
wget -q -O /root/doty_bot/core/xray_handler.py $REPO_URL/core/xray_handler.py
wget -q -O /root/doty_bot/core/ssh_handler.py $REPO_URL/core/ssh_handler.py
wget -q -O /root/doty_bot/utils/qr_generator.py $REPO_URL/utils/qr_generator.py

echo -e "\e[34m[4/4] Activation du Bot 24h/24...\e[0m"
cat <<EOF > /etc/systemd/system/dotybot.service
[Unit]
Description=Dotycat Telegram Bot Pro
After=network.target

[Service]
ExecStart=/usr/bin/python3 /root/doty_bot/main.py
WorkingDirectory=/root/doty_bot
Restart=always
User=root

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable dotybot &>/dev/null
systemctl restart dotybot

echo -e "\e[36m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\e[0m"
echo -e "\e[32m✅ BOT INSTALLÉ ET CONNECTÉ AVEC SUCCÈS ! \e[0m"
echo -e "\e[36m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\e[0m"
echo -e "📱 Ouvrez Telegram et envoyez \e[32m/start\e[0m à votre bot."
echo ""
read -n 1 -s -r -p "Appuyez sur une touche pour retourner au menu..."
