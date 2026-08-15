# Simple Discord Bot

This is a simple Discord bot built with Python and `discord.py`.
- This Bot is in  testing, things will\will not work. 

## Prerequisites

- Python 3.8 or higher
- A Discord account and a created Application/Bot in the [Discord Developer Portal](https://discord.com/developers/applications)

## Setup

1.  **Install Dependencies** (if you haven't already):
    ```bash
    pip install discord.py python-dotenv
    ```

2.  **Configure Token**:
    - Open the `.env` file in this directory.
    - Replace `your_discord_bot_token_here` with your actual Discord Bot Token.
    - You can get your token from the "Bot" section of your application in the Discord Developer Portal.

3.  **Run the Bot**:
    ```bash
    python bot.py
    ```

## Features

- **General**:
    - `\github`: Get the link to the bot's source code.
    - `\ping`: Check if the bot is responsive.
        - Responds to "hello" with "Hello there!".
- **Moderation**:
    - `\kick`, `\ban`, `\unban`: Manage users.
    - `\timeout`: Mute users for a duration.
    - `\lock`, `\unlock`: Lock down channels.
    - `\clear`: Delete messages.
    - `\blacklist`, `\unblacklist`: Prevent specific users from using the bot.
    - 
- **Utility**:
    - `\reaction_roles`: Set up role assignment menus.
    - `\poll "Question?" (Yes/No poll)` or `\poll "Question?" "Option 1" "Option 2" (Multiple choice)`: Be able to make Polls about anything.
    - 
## Notes

- Ensure "Message Content Intent" is enabled in the Discord Developer Portal under the "Bot" section for the bot to read message content.

