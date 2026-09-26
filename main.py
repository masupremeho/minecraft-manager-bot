import os
import json
import discord
from discord.ext import commands
from dotenv import load_dotenv

# 1. ALWAYS load environment variables FIRST
load_dotenv()

# 2. Import custom UI components
from ui.components import ServerControlView

# --- CONFIGURATION & VALIDATION ---
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
BOT_OWNER_ID = int(os.getenv("BOT_OWNER_ID", "0"))
SERVER_ADDRESS = os.getenv("SERVER_ADDRESS", "Server Offline / Not Configured")

if not DISCORD_TOKEN:
    raise ValueError("❌ DISCORD_TOKEN is missing from your .env file!")

# --- PERMISSIONS MANAGEMENT ---
DATA_FILE = "allowed_users.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        initial_data = {
            "owner_id": BOT_OWNER_ID,
            "allowed_users": [BOT_OWNER_ID] if BOT_OWNER_ID != 0 else []
        }
        save_data(initial_data)
        return initial_data
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# --- BOT SETUP ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

async def check_user_permission(interaction: discord.Interaction) -> bool:
    data = load_data()
    allowed = data.get("allowed_users", [])
    owner = data.get("owner_id", BOT_OWNER_ID)
    
    # Owner safeguard: Always allow the bot owner regardless of JSON file state
    if interaction.user.id == owner or interaction.user.id == BOT_OWNER_ID:
        return True
        
    if interaction.user.id not in allowed:
        await interaction.response.send_message("⛔ **Access Denied:** You are not on the permitted list.", ephemeral=True)
        return False
    return True

@bot.event
async def on_ready():
    print(f"✅ Minecraft Manager logged in as {bot.user.name}")
    await bot.change_presence(activity=discord.Game(name=SERVER_ADDRESS))

@bot.command(name="panel")
async def send_panel(ctx):
    """Sends the interactive control panel embed."""
    embed = discord.Embed(
        title="🎮 Minecraft Manager Control Panel",
        description="Select an option from the dropdown menu to inspect status, or use buttons to trigger actions.",
        color=discord.Color.blue()
    )
    embed.add_field(name="🌐 Server Address", value=f"`{SERVER_ADDRESS}`", inline=False)
    view = ServerControlView(check_user_permission)
    await ctx.send(embed=embed, view=view)

# --- OWNER ONLY MANAGEMENT COMMANDS ---
@bot.command(name="allow")
async def add_user(ctx, user: discord.User):
    """Add a user to the allowed list (Owner only)."""
    data = load_data()
    owner = data.get("owner_id", BOT_OWNER_ID)
    if ctx.author.id != owner and ctx.author.id != BOT_OWNER_ID:
        return await ctx.send("⛔ Only the main owner can manage allowed users.")
    
    if user.id not in data["allowed_users"]:
        data["allowed_users"].append(user.id)
        save_data(data)
        await ctx.send(f"✅ Added {user.mention} (`{user.id}`) to the allowed list.")
    else:
        await ctx.send(f"ℹ️ {user.mention} is already in the allowed list.")

@bot.command(name="deny")
async def remove_user(ctx, user: discord.User):
    """Remove a user from the allowed list (Owner only)."""
    data = load_data()
    owner = data.get("owner_id", BOT_OWNER_ID)
    if ctx.author.id != owner and ctx.author.id != BOT_OWNER_ID:
        return await ctx.send("⛔ Only the main owner can manage allowed users.")
    
    if user.id == owner or user.id == BOT_OWNER_ID:
        return await ctx.send("⚠️ You cannot remove yourself as the main owner.")

    if user.id in data["allowed_users"]:
        data["allowed_users"].remove(user.id)
        save_data(data)
        await ctx.send(f"🚫 Removed {user.mention} (`{user.id}`) from the allowed list.")
    else:
        await ctx.send(f"ℹ️ {user.mention} was not found in the allowed list.")

@bot.command(name="listusers")
async def list_users(ctx):
    """List all allowed users (Owner only)."""
    data = load_data()
    owner = data.get("owner_id", BOT_OWNER_ID)
    if ctx.author.id != owner and ctx.author.id != BOT_OWNER_ID:
        return await ctx.send("⛔ Only the main owner can view the permitted list.")
    
    users = [f"<@{uid}> (`{uid}`)" for uid in data["allowed_users"]]
    embed = discord.Embed(
        title="📋 Permitted Users List", 
        description="\n".join(users) if users else "No allowed users.", 
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

bot.run(DISCORD_TOKEN)