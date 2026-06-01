#!/usr/bin/env python
"""
Wat2Do Discord Bot
===================
This script runs a standalone Discord bot client that listens for new messages
in your designated #events channel (which collects followed channel announcements
from other clubs) and forwards them to the wat2do.ca event processing pipeline.

Setup:
1. Install requirements:
   pip install discord.py requests python-dotenv

2. Configure environment variables in your backend `.env` file:
   DISCORD_BOT_TOKEN=your_bot_token_here
   DISCORD_EVENTS_CHANNEL_ID=your_channel_id_here
   AUTOMATE_WEBHOOK_KEY=your_secure_webhook_key_here
   # Optional: Default URL is http://localhost:8000/api/scraping/discord-webhook/
   # set to https://wat2do.ca/api/scraping/discord-webhook/ in production.
   WAT2DO_API_URL=https://wat2do.ca/api/scraping/discord-webhook/

3. Run the script:
   python scripts/run_discord_bot.py
"""

import os
import sys
import logging
import requests
from pathlib import Path
from dotenv import load_dotenv

# Ensure backend directory is in the path to load dotenv correctly
backend_dir = Path(__file__).resolve().parent.parent
load_dotenv(backend_dir / ".env")

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(backend_dir / "logs" / "discord_bot.log", encoding="utf-8") if (backend_dir / "logs").exists() else logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("discord_bot")

try:
    import discord
    from discord.ext import commands
except ImportError:
    logger.critical("Missing dependency: 'discord.py' is not installed. Please run: pip install discord.py")
    sys.exit(1)

# Retrieve configuration
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
CHANNEL_ID_STR = os.getenv("DISCORD_EVENTS_CHANNEL_ID") or os.getenv("DISCORD_EVENTS_CHANNEL")
API_KEY = os.getenv("AUTOMATE_WEBHOOK_KEY")
API_URL = os.getenv("WAT2DO_API_URL", "http://localhost:8000/api/scraping/discord-webhook/")

# Basic validations
if not TOKEN:
    logger.error("DISCORD_BOT_TOKEN is not set in your environment or .env file.")
if not CHANNEL_ID_STR:
    logger.error("Neither DISCORD_EVENTS_CHANNEL_ID nor DISCORD_EVENTS_CHANNEL is set in your environment or .env file.")
if not API_KEY:
    logger.error("AUTOMATE_WEBHOOK_KEY is not set in your environment or .env file.")

try:
    CHANNEL_ID = int(CHANNEL_ID_STR) if CHANNEL_ID_STR else None
except ValueError:
    logger.critical(f"Invalid DISCORD_EVENTS_CHANNEL_ID: '{CHANNEL_ID_STR}'. Must be a number.")
    sys.exit(1)

# Configure Discord bot intents
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    logger.info(f"Wat2Do bot is logged in as: {bot.user} (ID: {bot.user.id})")
    logger.info(f"Target Events Channel ID: {CHANNEL_ID}")
    logger.info(f"Forwarding events to: {API_URL}")
    
    # Verify the channel exists/is visible to the bot
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        logger.info(f"Verified channel accessibility: #{channel.name} on server '{channel.guild.name}'")
    else:
        logger.warning(
            f"Could not fetch channel with ID {CHANNEL_ID} from cache. "
            "Please verify the bot is added to the server and has access to this channel."
        )




async def process_and_forward_message(message):
    """Core logic to serialize, build payload, and POST to wat2do backend pipeline."""
    # We want to process announcements, which can come from users, other bots, or webhooks
    author_name = message.author.display_name or message.author.name
    
    # If it was sent by a webhook or cross-posted channel, author name is sometimes best resolved
    # from the display name or message.webhook_id if present
    if message.webhook_id:
        logger.info(f"Processing message {message.id} sent by Webhook (Author: {author_name})")
        
    logger.info(f"Processing event message: ID={message.id} from Author='{author_name}'")
    
    # Collect image attachments
    attachments = []
    for att in message.attachments:
        if att.content_type and att.content_type.startswith("image/"):
            attachments.append(att.url)
            
    # Also check for embedded images from links inside the message
    for embed in message.embeds:
        if embed.image and embed.image.url:
            attachments.append(embed.image.url)
            
    # Remove duplicates while keeping order
    attachments = list(dict.fromkeys(attachments))

    # Default to current channel and guild
    guild_id = str(message.guild.id) if message.guild else "0"
    channel_id = str(message.channel.id)
    message_id = str(message.id)

    # Check if the message is a crosspost from another server's announcement channel
    if message.flags.is_crossposted and message.reference:
        ref = message.reference
        if ref.guild_id and ref.channel_id and ref.message_id:
            guild_id = str(ref.guild_id)
            channel_id = str(ref.channel_id)
            message_id = str(ref.message_id)
            logger.info(f"Crosspost detected! Using original message IDs: Guild={guild_id}, Channel={channel_id}, Message={message_id}")

    # Build payload
    payload = {
        "content": message.content,
        "author_name": author_name,
        "message_id": message_id,
        "channel_id": channel_id,
        "guild_id": guild_id,
        "timestamp": message.created_at.isoformat(),
        "attachments": attachments
    }
    
    # Configure headers
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Forward to wat2do API pipeline
    try:
        logger.info(f"Forwarding message {message.id} to wat2do backend pipeline...")
        response = requests.post(API_URL, json=payload, headers=headers, timeout=30)
        
        if response.status_code in (200, 201):
            res_data = response.json()
            status = res_data.get("status")
            
            if status == "success":
                saved = res_data.get("saved_count", 0)
                events = res_data.get("events", [])
                logger.info(f"Successfully processed: extracted {res_data.get('processed_count')} events, saved {saved} to DB.")
                for evt in events:
                    logger.info(f"  -> [{evt.get('status').upper()}] Title: '{evt.get('title')}' at Location: '{evt.get('location')}'")
            elif status == "duplicate":
                logger.info(f"Successfully processed: Event already exists in database (duplicate message).")
            elif status == "no_events_found":
                logger.info(f"Successfully processed: Message did not contain any valid event details.")
            else:
                logger.info(f"Processed response: {res_data}")
        else:
            logger.error(f"Failed to forward message. Server returned status {response.status_code}: {response.text}")
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error trying to contact wat2do API: {e}")
    except Exception as e:
        logger.error(f"Unexpected error processing message: {e}")


@bot.event
async def on_message(message):
    # Ignore messages sent by this bot itself
    if message.author == bot.user:
        return

    # Check if the message is in the target #events channel
    if message.channel.id == CHANNEL_ID:
        await process_and_forward_message(message)

    # Allow normal commands processing (if any command handlers are added later)
    await bot.process_commands(message)

def main():
    if not TOKEN or not CHANNEL_ID or not API_KEY:
        logger.critical("Missing vital environment variables. Bot cannot start. Check .env configurations.")
        sys.exit(1)
        
    logger.info("Starting Wat2Do Discord bot service...")
    try:
        bot.run(TOKEN)
    except discord.errors.LoginFailure:
        logger.critical("Failed to log in: Invalid Discord token provided.")
        sys.exit(1)
    except Exception as e:
        logger.critical(f"Critical bot crash: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
