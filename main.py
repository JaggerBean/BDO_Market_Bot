import requests
import json
import time
import os
import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv

load_dotenv()

TRADE_LOG_FILE = "premium_trades.json"
Discord_Token = os.getenv("DISCORD_TOKEN")
TARGET_CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))
delay = 15

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

def load_previous_trades():
    if os.path.exists(TRADE_LOG_FILE):
        with open(TRADE_LOG_FILE, "r") as f:
            return json.load(f)
    return {}

def save_current_trades(trade_map):
    with open(TRADE_LOG_FILE, "w") as f:
        json.dump(trade_map, f, indent=2)

def get_premium_pearl_items():
    url = "https://api.arsha.io/v2/na/pearlItems"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers)
    print("Status:", response.json())

    if response.status_code == 200:
        pearl_items = response.json()

        # Filter items containing 'Premium' in the name
        premium_items = [item for item in pearl_items if "Premium" in item['name']]

        # Build name → totalTrades dict
        trade_map = {item['name']: item['totalTrades'] for item in premium_items}
        stock_map = {item['name']: item['currentStock'] for item in premium_items}
        return trade_map, stock_map
    else:
        print("Failed to fetch pearl items.")
        return {}, {}

# ---- Main Logic ----
previous_trades = load_previous_trades()
current_trades, current_stock = get_premium_pearl_items()

moving_outfits = []

print("\n🧾 Premium Outfit Sales Since Last Run:")
for name, trades_now in current_trades.items():
    trades_before = previous_trades.get(name, 0)
    diff = trades_now - trades_before
    if diff >= 3:
        moving_outfits.append((name, diff))
        print(f"✅ {name} sold {diff} time(s) since last check!")

outfits_in_stock = []

print("\n🧾 Premium Outfits With Stock:")
for name, Stock in current_stock.items():
    if Stock > 0:
        outfits_in_stock.append((name, Stock))
        print(f"✅ {name} has {Stock} items in stock")
@bot.event
async def on_ready():

    channel = bot.get_channel(TARGET_CHANNEL_ID)
    print(f"✅ Logged in as {bot.user.name}")
    for outfit, diff in moving_outfits:
        await channel.send(f"___{outfit}___ is moving frequently! It has sold {diff} times in the last {delay} minutes.")
    for outfit, stock in outfits_in_stock:
        await channel.send(f"___{outfit}___ is sitting on the market! There are currently {stock} in stock.")
    await bot.close()  # Exit cleanly after posting

bot.run(Discord_Token, log_handler=handler, log_level=logging.DEBUG)
# Save current snapshot for next run
save_current_trades(current_trades)


