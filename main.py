import discord
import os
import re
import datetime
from discord.ext import commands
import json
from io import BytesIO
from PIL import Image
import requests
import logging
from pokemon_database import PokemonDatabase
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('pokemon-identifier')

# Bot configuration
TOKEN = os.getenv("DISCORD_BOT_TOKEN")  # Get token from environment variable
POKETWO_BOT_ID = 716390085896962058  # Poketwo's bot ID

# Create bot instance with all intents
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

# Initialize Pokemon database
pokemon_db = PokemonDatabase()

# Track the last spawned Pokemon image URL
last_pokemon_image_url = None

@bot.event
async def on_ready():
    logger.info(f'{bot.user.name} has connected to Discord!')
    logger.info(f'Connected to {len(bot.guilds)} guilds')

@bot.event
async def on_message(message):
    global last_pokemon_image_url
    
    # Don't respond to our own messages
    if message.author == bot.user:
        return
    
    # Process commands
    await bot.process_commands(message)
    
    # Check if message is from Poketwo
    if message.author.id == POKETWO_BOT_ID:
        # Case 1: Pokemon spawn message with image
        if message.embeds and any(embed.image for embed in message.embeds):
            embed = message.embeds[0]
            
            # Check if this looks like a Pokemon spawn message
            if embed.image and "wild pokémon has appeared" in embed.title.lower():
                logger.info("Detected a Pokemon spawn from Poketwo")
                
                # Store the image URL for later use
                last_pokemon_image_url = embed.image.url
                
                # Try to identify the Pokemon
                pokemon_name, response_msg = await pokemon_db.identify_pokemon(last_pokemon_image_url)
                
                if pokemon_name:
                    await message.channel.send(response_msg)
                else:
                    await message.channel.send("I detected a Pokemon but couldn't identify it. I'll learn from your correct guess!")
        
        # Case 2: Successful catch confirmation message
        elif "congratulations" in message.content.lower():
            # Extract the Pokemon name using a simplified pattern
            match = re.search(r"caught a (?:Level \d+ )?([A-Za-z]+)", 
                            message.content, 
                            re.IGNORECASE)
            
            if match and last_pokemon_image_url:
                pokemon_name = match.group(1).strip()
                logger.info(f"Detected caught Pokemon: {pokemon_name}")
                logger.info(f"User correctly identified Pokemon: {pokemon_name}")
                
                # Learn this Pokemon
                success, learn_msg = await pokemon_db.learn_pokemon(last_pokemon_image_url, pokemon_name)
                
                if success:
                    await message.channel.send(f"I've learned that was a {pokemon_name}! I'll remember it next time.")
                    logger.info(f"Successfully learned Pokemon: {pokemon_name}")
                else:
                    logger.error(f"Failed to learn Pokemon: {pokemon_name}")
                
                # Reset the last image URL
                last_pokemon_image_url = None

@bot.command(name='help-pokemon')
async def help_pokemon(ctx):
    """Display help information for the Pokemon identifier bot"""
    help_text = (
        "**Pokemon Identifier Bot**\n\n"
        "This bot automatically detects when Poketwo spawns a Pokemon and attempts to identify it.\n"
        "It also learns from correct guesses automatically!\n\n"
        "**Commands:**\n"
        "`!help-pokemon` - Display this help message\n"
    )
    await ctx.send(help_text)

@bot.command(name='setup')
@commands.has_permissions(administrator=True)
async def setup(ctx):
    """Set up the bot in this channel"""
    await ctx.send(f"Pokemon Identifier Bot is now set up in {ctx.channel.mention}!")
    logger.info(f"Bot set up in channel {ctx.channel.name} in guild {ctx.guild.name}")

# Run the bot
def main():
    logger.info("Starting Pokemon Identifier Bot")
    
    # Check if token is available
    if not TOKEN:
        logger.error("No Discord bot token found in environment variables. Please set DISCORD_BOT_TOKEN in .env file.")
        return
        
    bot.run(TOKEN)

if __name__ == "__main__":
    main()