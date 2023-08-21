# TeleGPTbot
Telegram bot connecting to ChatGPT 3.5 using OpenAI API. Supports multiple users, multiple conversations with chat context. Also has a few prompts presets.

# Setup
```bash
pip install -r requirements.txt ; mkdir users
```
## Change config.py
```bash
TOKEN = 'TGBOTAPI'
OPENAIKEY = 'OPENAIAPI'
BOTNICKNAME = '@BOTUSERNAME'
```

# Usage
- Start bot with `/start` command
- See available commands with `/help` or `/start` command
- If you've got some error, do `/reset` command.

# Customize
If you want to add new presets, redact contexts.py

## features
- Add bot to your group
- Create new conversations and switch between your conversations with bot
- Switch between prompt presets

