# Upbot
**UpWork RSS to Telegram**

A simple bot that parses the UpWork RSS feed and sends new messages to Telegram. By default, the parsing frequency is set to 1 minute. All descriptions are summarized through ChatGPT to reduce reading unnecessary information. There are also two buttons to read the post in translation and in the original. The query request is set through environment variables and uses Python by default.

The prompts for translation and summarization are located in `gpt.py`.

This bot is not intended for mass use because user storage is not implemented. The code was written in 2 days for personal use only.

## Settings

The bot is configured through environment variables. Copy `.env.example` and fill in all the variables:
- `upwork_bot_token` - The token from the bot https://t.me/BotFather
- `openai_key` - The ChatGPT key https://platform.openai.com/api-keys
- `upwork_token`, `upwork_user_id`, `upwork_org_id` - Taken from the RSS link(pic). Query parameters: "securityToken", "userUid", "orgUid"

<p align="center">
  <img src="/docs/rss.png" alt="Login Interface Preview">
</p>

## Installing and starting

Clone repo

before start use `make install` to create venv

`make run` to start app 

## TODO
- Put it in Docker
