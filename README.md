# Pokémon Identifier Bot

This Discord bot is designed to identify Pokémon from images posted by the Poketwo bot. When Poketwo spawns a Pokémon, the bot will look into database for the matching hash of that picture, if it sees then it will tell the pokemon's name, if not then it will wait for you to answer and store it in its system



## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- A Discord bot token
- Discord server with Poketwo bot

### Installation

1. Clone this repository or download the files
2. Create and activate a virtual environment:

```bash
python -m venv venv
venv\Scripts\activate  # On Windows
```

3. Install the required packages:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root directory with your Discord bot token:
   ```
   DISCORD_BOT_TOKEN=your_discord_bot_token_here
   ```

5. Run the bot:

```bash
python main.py
```

### Discord Bot Setup

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Go to the "Bot" tab and click "Add Bot"
4. Under the "Privileged Gateway Intents" section, enable all intents
5. Copy your token and paste it in the `main.py` file
6. Go to the "OAuth2" tab, select the "bot" scope and the following permissions:
   - Read Messages/View Channels
   - Send Messages
   - Read Message History
7. Use the generated URL to invite the bot to your server

## Usage

Once the bot is running and added to your server, it will automatically detect when Poketwo spawns a Pokémon. 

Commands:
- `!help-pokemon` - Display help information
- `!setup` - Set up the bot in the current channel (requires administrator permissions)

## Disclaimer

This bot is for educational purposes only. It is not affiliated with Pokémon, Nintendo, or Poketwo.
