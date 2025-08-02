{\rtf1\ansi\ansicpg1252\cocoartf2761
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx566\tx1133\tx1700\tx2267\tx2834\tx3401\tx3968\tx4535\tx5102\tx5669\tx6236\tx6803\pardirnatural\partightenfactor0

\f0\fs24 \cf0 import wifi\
import socketpool\
import microcontroller\
import time\
import board\
import digitalio\
import usb_hid\
from adafruit_hid.keyboard import Keyboard\
from adafruit_hid.keycode import Keycode\
import json\
\
import commands  # notre module commands.py\
from secrets import secrets\
\
# Connexion Wi-Fi\
print("Connexion au Wi-Fi...")\
wifi.radio.connect(secrets['ssid'], secrets['password'])\
print("Connect\'e9 au r\'e9seau", secrets['ssid'])\
pool = socketpool.SocketPool(wifi.radio)\
server = pool.socket(pool.AF_INET, pool.SOCK_STREAM)\
server.bind(('0.0.0.0', 80))\
server.listen(1)\
print("Serveur web d\'e9marr\'e9")\
\
# Clavier HID\
kbd = Keyboard(usb_hid.devices)\
\
# --- Fonctions pour interpr\'e9ter les commandes ---\
# Exemple: "GUI r" => appuie sur GUI (Win/Cmd) + r\
# "DELAY 1000" => pause 1000 ms\
# "ENTRER" => touche ENTER\
# "cmd" (texte normal) => tape le texte\
\
def parse_and_execute(commands_list):\
    for cmd in commands_list:\
        cmd = cmd.strip()\
        if cmd.upper().startswith("DELAY"):\
            # Ex: DELAY 1000\
            try:\
                ms = int(cmd.split()[1])\
                print(f"Pause de \{ms\} ms")\
                time.sleep(ms / 1000)\
            except:\
                pass\
        elif cmd.upper() == "ENTRER":\
            print("Touche ENTER")\
            kbd.send(Keycode.ENTER)\
        elif cmd.upper().startswith("GUI"):\
            # Ex: GUI r => Win+R\
            parts = cmd.split()\
            if len(parts) == 2:\
                key = parts[1].upper()\
                # Conversion lettre en Keycode\
                try:\
                    keycode = getattr(Keycode, key)\
                    print(f"Appuie sur GUI + \{key\}")\
                    kbd.press(Keycode.GUI, keycode)\
                    kbd.release_all()\
                except AttributeError:\
                    print("Touche inconnue pour GUI:", key)\
        else:\
            # Texte normal\
            print(f"Tape texte : \{cmd\}")\
            for c in cmd:\
                kbd.send(ord(c))\
\
# HTML+JS de l'interface web\
\
html_page = """\
<!DOCTYPE html>\
<html lang="fr">\
<head>\
<meta charset="UTF-8" />\
<title>Contr\'f4le HID Pico W</title>\
<style>\
body \{ font-family: Arial, sans-serif; margin: 20px; \}\
h1 \{ color: #333; \}\
button \{ margin: 5px; padding: 10px; font-size: 1em; \}\
textarea \{ width: 100%; height: 60px; font-size: 1em; \}\
input[type=text] \{ width: 100%; padding: 5px; font-size: 1em; \}\
.command-item \{ border: 1px solid #ddd; margin: 5px 0; padding: 10px; \}\
</style>\
</head>\
<body>\
<h1>Contr\'f4le HID Pico W</h1>\
\
<h2>Clavier virtuel</h2>\
<textarea id="textInput" placeholder="\'c9crire du texte ici..."></textarea><br />\
<button onclick="sendText()">Envoyer texte</button>\
\
<h2>Commandes enregistr\'e9es</h2>\
<div id="commandsList">Chargement...</div>\
\
<h3>Ajouter une commande</h3>\
<label>Nom :</label><br />\
<input type="text" id="cmdName" placeholder="Nom de la commande" /><br />\
<label>Actions (s\'e9par\'e9es par des virgules):</label><br />\
<textarea id="cmdActions" placeholder="Ex: GUI r, DELAY 1000, cmd, DELAY 300, ENTRER"></textarea><br />\
<button onclick="addCommand()">Ajouter</button>\
\
<script>\
// R\'e9cup\'e8re les commandes depuis le Pico\
function fetchCommands() \{\
    fetch('/commands')\
    .then(response => response.json())\
    .then(data => \{\
        const listDiv = document.getElementById('commandsList');\
        listDiv.innerHTML = '';\
        data.forEach((cmd, i) => \{\
            const div = document.createElement('div');\
            div.className = 'command-item';\
            div.innerHTML = `<strong>$\{cmd.name\}</strong><br />Actions: $\{cmd.actions.join(', ')\}<br />\
            <button onclick="runCommand($\{i\})">Ex\'e9cuter</button>\
            <button onclick="deleteCommand($\{i\})">Supprimer</button>`;\
            listDiv.appendChild(div);\
        \});\
    \});\
\}\
\
function sendText() \{\
    const text = document.getElementById('textInput').value;\
    if(text.trim() === '') \{\
        alert("\'c9cris quelque chose avant d'envoyer !");\
        return;\
    \}\
    fetch('/send_text', \{\
        method: 'POST',\
        headers: \{ 'Content-Type': 'application/json' \},\
        body: JSON.stringify(\{ text: text \})\
    \}).then(() => \{\
        alert("Texte envoy\'e9 !");\
        document.getElementById('textInput').value = '';\
    \});\
\}\
\
function runCommand(index) \{\
    fetch('/run_command', \{\
        method: 'POST',\
        headers: \{ 'Content-Type': 'application/json' \},\
        body: JSON.stringify(\{ index: index \})\
    \});\
\}\
\
function addCommand() \{\
    const name = document.getElementById('cmdName').value.trim();\
    const actionsRaw = document.getElementById('cmdActions').value.trim();\
    if(name === '' || actionsRaw === '') \{\
        alert("Nom et actions sont requis.");\
        return;\
    \}\
    // Split actions par virgule et trim\
    const actions = actionsRaw.split(',').map(s => s.trim());\
    fetch('/add_command', \{\
        method: 'POST',\
        headers: \{ 'Content-Type': 'application/json' \},\
        body: JSON.stringify(\{ name: name, actions: actions \})\
    \}).then(() => \{\
        alert("Commande ajout\'e9e !");\
        document.getElementById('cmdName').value = '';\
        document.getElementById('cmdActions').value = '';\
        fetchCommands();\
    \});\
\}\
\
function deleteCommand(index) \{\
    fetch('/delete_command', \{\
        method: 'POST',\
        headers: \{ 'Content-Type': 'application/json' \},\
        body: JSON.stringify(\{ index: index \})\
    \}).then(() => fetchCommands());\
\}\
\
// Chargement initial des commandes\
fetchCommands();\
</script>\
\
</body>\
</html>\
"""\
\
# --- Serveur web minimal ---\
\
def handle_client(client):\
    try:\
        request = client.recv(1024).decode('utf-8')\
        # print("Requ\'eate re\'e7ue:", request)\
        if not request:\
            client.close()\
            return\
\
        # Analyse requ\'eate HTTP\
        lines = request.split("\\r\\n")\
        method, path, _ = lines[0].split(" ")\
\
        # GET page d'accueil\
        if method == "GET" and path == "/":\
            response = html_page\
            client.send(b"HTTP/1.1 200 OK\\r\\nContent-Type: text/html\\r\\n\\r\\n")\
            client.send(response.encode('utf-8'))\
\
        # GET commandes JSON\
        elif method == "GET" and path == "/commands":\
            cmds = commands.load_commands()\
            client.send(b"HTTP/1.1 200 OK\\r\\nContent-Type: application/json\\r\\n\\r\\n")\
            client.send(json.dumps(cmds).encode('utf-8'))\
\
        # POST : ex\'e9cuter commande par index\
        elif method == "POST" and path == "/run_command":\
            length = 0\
            for line in lines:\
                if line.startswith("Content-Length:"):\
                    length = int(line.split(":")[1].strip())\
            body = client.recv(length).decode('utf-8')\
            data = json.loads(body)\
            index = data.get("index", -1)\
            cmds = commands.load_commands()\
            if 0 <= index < len(cmds):\
                print(f"Ex\'e9cution de la commande '\{cmds[index]['name']\}'")\
                parse_and_execute(cmds[index]['actions'])\
            client.send(b"HTTP/1.1 200 OK\\r\\nContent-Type: text/plain\\r\\n\\r\\nOK")\
\
        # POST : envoyer texte simple\
        elif method == "POST" and path == "/send_text":\
            length = 0\
            for line in lines:\
                if line.startswith("Content-Length:"):\
                    length = int(line.split(":")[1].strip())\
            body = client.recv(length).decode('utf-8')\
            data = json.loads(body)\
            text = data.get("text", "")\
            if text:\
                parse_and_execute([text])\
            client.send(b"HTTP/1.1 200 OK\\r\\nContent-Type: text/plain\\r\\n\\r\\nOK")\
\
        # POST : ajouter une commande\
        elif method == "POST" and path == "/add_command":\
            length = 0\
            for line in lines:\
                if line.startswith("Content-Length:"):\
                    length = int(line.split(":")[1].strip())\
            body = client.recv(length).decode('utf-8')\
            data = json.loads(body)\
            name = data.get("name", "").strip()\
            actions = data.get("actions", [])\
            if name and actions:\
                new_cmd = \{"name": name, "actions": actions\}\
                commands.add_command(new_cmd)\
            client.send(b"HTTP/1.1 200 OK\\r\\nContent-Type: text/plain\\r\\n\\r\\nOK")\
\
        # POST : supprimer une commande\
        elif method == "POST" and path == "/delete_command":\
            length = 0\
            for line in lines:\
                if line.startswith("Content-Length:"):\
                    length = int(line.split(":")[1].strip())\
            body = client.recv(length).decode('utf-8')\
            data = json.loads(body)\
            index = data.get("index", -1)\
            commands.delete_command(index)\
            client.send(b"HTTP/1.1 200 OK\\r\\nContent-Type: text/plain\\r\\n\\r\\nOK")\
\
        else:\
            # 404 Not Found\
            client.send(b"HTTP/1.1 404 Not Found\\r\\nContent-Type: text/plain\\r\\n\\r\\nPage non trouv\'e9e")\
\
    except Exception as e:\
        print("Erreur lors du traitement :", e)\
    finally:\
        client.close()\
\
# --- Boucle principale ---\
\
while True:\
    client, addr = server.accept()\
    print("Client connect\'e9 depuis", addr)\
    handle_client(client)\
}