# tg-relay
Relay Telegram messages to Discord and Telegram (optionnal), using your own user.

## Installation

Register a Telegram app (here)[https://my.telegram.org/apps]
Copy `.env.example` to `.env`
Fill in your `API_ID` and `API_HASH` in .env
Create a `relay_config.json` file and fill it in with the config you need (see below)

## Configuration

```
[
  {
    "name": "DSB Calls", 
    "source_tg_channel_id": 0000000000,
    "dest_tg_channel_ids": [
      "1111111111",
      "2222222222"
    ],
    "discord_webhook": "https://discord.com/api/webhooks/123456789,
    "senders_ids": [
      "3333333333",
      "4444444444"
    ],
    "regexFiltersInclude": [
      "\n\n"
    ],
    "regexFiltersExclude": [
      "Call placed on:"
    ],
    "pingRoles": [
      "1234567891011121314"
    ]
  },
  ...
]
```

## Usage

```python3 relay.py```

name : Used to bind custom functions and know what channel you're looking at in the config
source_tg_channel_id : The source ID of the Telegram channel you want to relay
dest_tg_channel_id : If you also want to forward messages to one or multiple telegram channels, you can specify it [optionnal]
discord_webhook : The Discord webhook URL to relay the message
senders_ids : If the array isn't empty, it will only forward messages from the specified telegram user(s) [optionnal]
regexFiltersInclude : If the array isn't empty, it will only display the message if the regex(es) is found [optionnal]
regexFiltersExclude : If the array isn't empty, it won't display the message if the regex(es) is found [optionnal]
pingRoles : If the array isn't empty, it will ping every Discord role IDs present in it [optionnal] 

## Useful informations

- Forwarding (sending) to telgram is API-rate limited, reading isn't.
- When creating your App, you can input any URL. This is only a placeholder.
- If you want to quickly grab IDs from telegram, whether it's a user or a channel, enable developper mode and click on the entity. The ID will be displayed. You can also use the file `listchannels.py`, it will list the ID of every channel you're in.