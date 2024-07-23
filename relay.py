#!/usr/bin/env python
import asyncio
from datetime import datetime
import json
import logging
import re
import subprocess
import aiohttp
from telethon import TelegramClient, events
import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = TelegramClient(config.SESSION_NAME, config.API_ID, config.API_HASH)
client.start()

relay_config = []

async def run_script(script_name, *args):
    command = ['python3', script_name] + list(args)
    process = await asyncio.create_subprocess_exec(
        *command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    if process.returncode != 0:
        print(f"Error executing {script_name}: {stderr.decode()}")
        return None
    try:
        return str(stdout.decode().strip())
    except ValueError:
        return None

async def pump_whitelisted_creators_mints(message):
    with open('whitelisted_pump_devs.txt', 'r') as f:
        whitelist = f.read().splitlines()
    mint_pattern = r"Mint:\s*([^\n]+)"
    creator_pattern = r"Creator:\s*([^\n]+)"
    mint_match = re.search(mint_pattern, message)
    creator_match = re.search(creator_pattern, message)
    if mint_match and creator_match:
        mint = mint_match.group(1).strip()
        creator = creator_match.group(1).strip()
        if creator in whitelist:
            balance_result = await run_script('balance.py', creator, mint)
            holders = await run_script('holders.py', mint)
            last_tx_count = await run_script('txcount.py', mint)
            if balance_result:
                message += f"\n🔑 Creator token amount: {balance_result}"
            else:
                message += "\n❌ Dev Balance unavailable"
            if holders:
                message += f"\n👥 Holders count: {holders}"
            else:
                message += "\n❌ Failed to get holders count"
            if last_tx_count:
                message += f"\n🔄 Last 5 minutes transactions count: {last_tx_count}"
            else:
                message += "\n❌ Failed to get last 5 minutes transactions count"
            message += f"\n\n[DEX](https://dexscreener.com/solana/{mint})\n\nTime of posting: {datetime.now()}"
            return message
    return None


async def pump_live_mints(message):
    mint_pattern = r"Mint:\s*([^\n]+)"
    creator_pattern = r"Creator:\s*([^\n]+)"

    mint_match = re.search(mint_pattern, message)
    creator_match = re.search(creator_pattern, message)

    if mint_match and creator_match:
        mint = mint_match.group(1).strip()
        creator = creator_match.group(1).strip()
        """ Call the scripts to get the balance, holders, tx count and origin of funds.
            You can replace it with your own or just remove it if not needed.
        """
        balance_result = await run_script('balance.py', creator, mint)
        holders = await run_script('holders.py', mint)
        last_tx_count = await run_script('txcount.py', mint)
        origin = await run_script('origin.py', creator)
        if origin:
            message += f"\n" + origin
        else:
            message += '\nOrigin of funds not available'
        if balance_result:
            message += f"\n🔑 Creator token amount: {balance_result}"
        else:
            message += "\n❌ Dev Balance unavailable"
        if holders:
            message += f"\n👥 Holders count: {holders}"
        else:
            message += "\n❌ Failed to get holders count"
        if last_tx_count:
            message += f"\n🔄 Last 5 minutes transactions count: {last_tx_count}"
        else:
            message += "\n❌ Failed to get last 5 minutes transactions count"
        message += f"\n\n[DEX](https://dexscreener.com/solana/{mint})\n\nTime of posting: {datetime.now()}"

    return message

async def load_config():
    global relay_config
    try:
        with open('relay_config.json', 'r') as f:
            relay_config = json.load(f)
        logger.info('Configuration reloaded successfully')
    except Exception as e:
        logger.error(f'Failed to reload configuration: {e}')

async def periodic_config_reload(interval):
    while True:
        await load_config()
        await asyncio.sleep(interval)

async def setup():
    user = await client.get_me()
    logger.info('Started serving as {}'.format(user.first_name))
    await client.get_dialogs()

async def send_to_discord(username, message, webhook_url, role_ids):
    try:
        if role_ids:
            roles_mentions = ' '.join([f"<@&{role_id}>" for role_id in role_ids])
            allowed_mentions = {
                "roles": role_ids  
            }
        else:
            roles_mentions = ""
            allowed_mentions = {}
        payload = {
            "content": roles_mentions,
            "embeds": [{
                "title": username,
                "description": message,
                "color": 0x8f0fff
              }],
            "allowed_mentions": allowed_mentions
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(webhook_url, json=payload) as response:
                if response.status == 204:
                    logger.info('Message sent to Discord successfully')
                else:
                    logger.error(f'Failed to send message to Discord: {response.status}')
    except Exception as e:
        logger.error(f'Error during sending message to Discord: {e}')

@client.on(events.NewMessage)
async def my_event_handler(event):
    for entry in relay_config:
        if not entry["senders_ids"] or event.sender_id in entry["senders_ids"]:
            if event.chat and event.chat.id == entry["source_tg_channel_id"]:
                message_text = event.message.message
                sender = await event.get_sender()
                username = sender.username if sender.username else sender.id

                include = not entry.get("regexFiltersInclude") or any(re.search(pattern, message_text) for pattern in entry["regexFiltersInclude"])
                exclude = any(re.search(pattern, message_text) for pattern in entry.get("regexFiltersExclude", []))

                nosend = False

                if include and not exclude:
                    for rule_name, rule_function in custom_rules.items():
                        if entry["name"].lower() == rule_name.lower():
                            message_text = await rule_function(message_text)
                            if message_text is None:
                               nosend = True 
                            break
                    if nosend == False:
                        await send_to_discord(username, message_text, entry["discord_webhook"], entry['pingRoles'])
                    for dest_id in entry["dest_tg_channel_ids"]:
                        logger.info('Sending message from {} to {}'.format(event.chat.id, dest_id))
                        await client.forward_messages(dest_id, event.message)
                        break

async def main():
    await setup()
    asyncio.create_task(periodic_config_reload(300))
    await client.run_until_disconnected()

if __name__ == "__main__":
    
    """
    Bind your custom functions here.
    The key is the name of the rule in `relay_config.json` and the value is the function.
    Uncomment the lines below to use it.
    """
    
    #custom_rules = {
    #    "Pump Live Mints": pump_live_mints,
    #    "PumpFun Promising Mints": pump_whitelisted_creators_mints
    #}
    
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
