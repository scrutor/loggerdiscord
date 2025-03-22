import websocket
import json
import threading
import time
import getpass
from datetime import datetime
from colorama import Fore, Style, init
from tqdm import tqdm

init(autoreset=True)

def send_json_request(ws, request):
    ws.send(json.dumps(request))

def receive_json_response(ws):
    response = ws.recv()
    if response:
        return json.loads(response)

def heartbeat(interval, ws):
    """💓 Envoie un heartbeat toutes les X secondes pour maintenir la connexion active."""
    print(Fore.CYAN + "[INFO] 💓 Démarrage du système de ping...")
    while True:
        time.sleep(interval)
        heartbeatJSON = {"op": 1, "d": None}
        send_json_request(ws, heartbeatJSON)
        print(Fore.GREEN + "[INFO] ✅ Ping vers discord envoyé")


print(Fore.MAGENTA + "🔧 Tool développé par Scrutor")


token = getpass.getpass(Fore.YELLOW + "🔐 Entrez votre token Discord : ")


print(Fore.CYAN + "[INFO] 🌐 Connexion a Discord a partir du Token...")
for _ in tqdm(range(20), desc="Connexion", bar_format="{l_bar}{bar}"):
    time.sleep(0.1)

try:
    ws = websocket.WebSocket()
    ws.connect('wss://gateway.discord.gg/?v=6&encoding=json')

    event = receive_json_response(ws)
    heartbeat_interval = event['d']['heartbeat_interval'] / 1000


    thread = threading.Thread(target=heartbeat, args=(heartbeat_interval, ws))
    thread.daemon = True
    thread.start()


    payload = {
        "op": 2,
        "d": {
            "token": token,
            "properties": {
                "$os": "windows",
                "$browser": "chrome",
                "$device": "pc"
            }
        }
    }
    send_json_request(ws, payload)

    print(Fore.GREEN + "[INFO] ✅ Authentification réussie !")


    with open("messages.txt", "a", encoding="utf-8") as file:
        while True:
            event = receive_json_response(ws)
            try:
                if event['t'] == "MESSAGE_CREATE":
                    data = event['d']
                    message_content = data['content']
                    username = data['author']['username']
                    user_id = data['author']['id']
                    message_id = data['id']
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')


                    server_id = data.get('guild_id', "DM/Privé")
                    channel_id = data.get('channel_id', "Inconnu")
                    server_name = f"🌍 Serveur {server_id}" if server_id != "DM/Privé" else "💬 DM/Privé"


                    roles = data['member']['roles'] if 'member' in data and 'roles' in data['member'] else []
                    role_display = f"🎭 Rôles: {', '.join(roles)}" if roles else "🎭 Aucun rôle"


                    print(Fore.CYAN + "═" * 70)
                    print(Fore.YELLOW + f"📅 [{timestamp}] {Fore.BLUE}{server_name} {Fore.MAGENTA}# {channel_id}")
                    print(Fore.GREEN + f"👤 {username} ({user_id}) ✉️ {message_content}")
                    print(Fore.LIGHTBLACK_EX + f"🆔 Message ID: {message_id} | {role_display}")
                    print(Fore.CYAN + "═" * 70)


                    file.write(f"[{timestamp}] [{server_name} - #{channel_id}] {username} ({user_id}): {message_content}\n")


                if event['op'] == 11:
                    print(Fore.MAGENTA + "[INFO] 💖 Heartbeat reçu")

            except Exception as e:
                print(Fore.RED + f"[ERREUR] 🚨 {e}")

except Exception as e:
    print(Fore.RED + f"[ERREUR CRITIQUE] ❌ Impossible de se connecter : {e}")
