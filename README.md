# telegptbot
Telegram bot connecting to ChatGPT 3.5 using openai API. Suuports multiple users, multiple conversations with chat context. Also has few prompts presets.

## setup
```
pip install pip install pyTelegramBotAPI
pip install asyncio
```
fill config.py file

If you want to add new presets, redact contexts.txt.

Bot will automatically create user folders and keep their chat contexts there

## features
you can:
- add bot to your group
- create new conversations and switch between your conversations with bot
- switch between prompt presets

## usage
start bot with /start command

see awailable command with /help or /start command

if you've got some error, try /reset command.
