import discord
from discord.ui import Select, View, Button
from services.aws_service import get_ec2_status, start_ec2_instance, stop_ec2_instance
from services.ptero_service import get_ptero_status, send_ptero_power

class StatusSelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Check AWS Status", value="aws", emoji="☁️", description="Get current EC2 instance power state"),
            discord.SelectOption(label="Check Minecraft Status", value="mc", emoji="⛏️", description="Get Pterodactyl server state"),
            discord.SelectOption(label="Check Full System Status", value="all", emoji="📊", description="Get status for both AWS and Minecraft"),
        ]
        super().__init__(placeholder="🔍 Select a server state to inspect...", min_values=1, max_values=1, options=options, row=0)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        selected = self.values[0]
        
        if selected == "aws":
            state = get_ec2_status()
            embed = discord.Embed(title="☁️ AWS EC2 Instance Status", description=f"Current State: `{state}`", color=discord.Color.blue())
        elif selected == "mc":
            state = get_ptero_status()
            embed = discord.Embed(title="⛏️ Minecraft Server Status", description=f"Current State: `{state}`", color=discord.Color.green())
        else:
            aws_state = get_ec2_status()
            mc_state = get_ptero_status()
            embed = discord.Embed(title="📊 Full System Status", color=discord.Color.gold())
            embed.add_field(name="☁️ AWS EC2 State", value=f"`{aws_state}`", inline=True)
            embed.add_field(name="⛏️ Minecraft Server", value=f"`{mc_state}`", inline=True)

        await interaction.followup.send(embed=embed, ephemeral=True)

class ServerControlView(View):
    def __init__(self, check_permission_func):
        super().__init__(timeout=None)
        self.check_permission = check_permission_func
        self.add_item(StatusSelect())

    @discord.ui.button(label="Start AWS", style=discord.ButtonStyle.success, emoji="☁️", row=1)
    async def start_aws(self, interaction: discord.Interaction, button: Button):
        if not await self.check_permission(interaction): return
        await interaction.response.defer(ephemeral=True)
        _, msg = start_ec2_instance()
        await interaction.followup.send(msg, ephemeral=True)

    @discord.ui.button(label="Stop AWS", style=discord.ButtonStyle.danger, emoji="🔌", row=1)
    async def stop_aws(self, interaction: discord.Interaction, button: Button):
        if not await self.check_permission(interaction): return
        await interaction.response.defer(ephemeral=True)
        _, msg = stop_ec2_instance()
        await interaction.followup.send(msg, ephemeral=True)

    @discord.ui.button(label="Start MC", style=discord.ButtonStyle.primary, emoji="▶️", row=2)
    async def start_mc(self, interaction: discord.Interaction, button: Button):
        if not await self.check_permission(interaction): return
        await interaction.response.defer(ephemeral=True)
        _, msg = send_ptero_power("start")
        await interaction.followup.send(msg, ephemeral=True)

    @discord.ui.button(label="Stop MC", style=discord.ButtonStyle.secondary, emoji="⏹️", row=2)
    async def stop_mc(self, interaction: discord.Interaction, button: Button):
        if not await self.check_permission(interaction): return
        await interaction.response.defer(ephemeral=True)
        _, msg = send_ptero_power("stop")
        await interaction.followup.send(msg, ephemeral=True)

    @discord.ui.button(label="Restart MC", style=discord.ButtonStyle.secondary, emoji="🔄", row=2)
    async def restart_mc(self, interaction: discord.Interaction, button: Button):
        if not await self.check_permission(interaction): return
        await interaction.response.defer(ephemeral=True)
        _, msg = send_ptero_power("restart")
        await interaction.followup.send(msg, ephemeral=True)