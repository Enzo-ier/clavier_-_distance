{\rtf1\ansi\ansicpg1252\cocoartf2761
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx566\tx1133\tx1700\tx2267\tx2834\tx3401\tx3968\tx4535\tx5102\tx5669\tx6236\tx6803\pardirnatural\partightenfactor0

\f0\fs24 \cf0 import json\
import os\
\
COMMANDS_FILE = "commands.json"\
\
def load_commands():\
    try:\
        with open(COMMANDS_FILE, "r") as f:\
            return json.load(f)\
    except Exception:\
        # Si fichier absent ou corrompu, renvoyer liste vide\
        return []\
\
def save_commands(commands):\
    with open(COMMANDS_FILE, "w") as f:\
        json.dump(commands, f, indent=2)\
\
def add_command(new_command):\
    commands = load_commands()\
    commands.append(new_command)\
    save_commands(commands)\
\
def delete_command(index):\
    commands = load_commands()\
    if 0 <= index < len(commands):\
        commands.pop(index)\
        save_commands(commands)\
}