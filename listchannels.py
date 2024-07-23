#!/usr/bin/env python
from telethon import TelegramClient
import config

"""
This file is used to list all channels / contacts and their respective IDs
"""

client = TelegramClient(config.SESSION_NAME, config.API_ID, config.API_HASH)
client.start()


print('Channel | ID')
for dialog in client.get_dialogs():
    print(f'{dialog.name} | {dialog.entity.id}')
