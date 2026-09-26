import os
import json
import asyncio
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
from mcstatus import JavaServer

# 1. Load environment variables FIRST
load_dotenv()

# 2. Import custom UI components
from ui.components import ServerControlView
from services.aws_service import get_ec2_status, stop_ec2_instance
from services.ptero_service import send_ptero_power

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
    
    if interaction.user.id == owner or interaction.user.id == BOT_OWNER_ID:
        return True
        
    if interaction.user.id not in allowed:
        await interaction.response.send_message("⛔ **Access Denied:** You are not on the permitted list.", ephemeral=True)
        return False
    return True

# --- AUTO-SHUTDOWN BACKGROUND MONITOR ---
EMPTY_CHECKS = 0
MAX_EMPTY_CHECKS = 3  # 3 checks x 5 mins = 15 mins of zero players -> shutdown

@tasks.loop(minutes=5)
async def auto_shutdown_monitor():
    global EMPTY_CHECKS
    aws_status = get_ec2_status()
    
    # Only monitor if AWS is currently running
    if aws_status != "RUNNING":
        EMPTY_CHECKS = 0
        return

    try:
        server = JavaServer.lookup(SERVER_ADDRESS)
        status = server.status()
        players_online = status.players.online

        if players_online == 0:
            EMPTY_CHECKS += 1
            print(f"ℹ️ Auto-Shutdown Monitor: 0 players online ({EMPTY_CHECKS}/{MAX_EMPTY_CHECKS}).")
            
            if EMPTY_CHECKS >= MAX_EMPTY_CHECKS:
                print("🛑 15 minutes of inactivity detected. Shutting down Minecraft & AWS...")
                send_ptero_power("stop")
                await asyncio.sleep(15)  # Allow world save
                stop_ec2_instance()
                EMPTY_CHECKS = 0
        else:
            EMPTY_CHECKS = 0
            print(f"🎮 Auto-Shutdown Monitor: {players_online} players online.")
    except Exception:
        # If server is booting up or unreachable, don't trigger shutdown
        pass

@auto_shutdown_monitor.before_loop
async def before_auto_shutdown():
    await bot.wait_until_ready()

# --- EVENTS & COMMANDS ---
@bot.event
async def on_ready():
    print(f"✅ Minecraft Manager logged in as {bot.user.name}")
    await bot.change_presence(activity=discord.Game(name=SERVER_ADDRESS))
    if not auto_shutdown_monitor.is_running():
        auto_shutdown_monitor.start()

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

# --- OWNER ONLY COMMANDS ---
@bot.command(name="allow")
async def add_user(ctx, user: discord.User):
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