import discord
from discord.ext import commands
import os
import keep_alive
from discord_slash import SlashCommand

intents = discord.Intents.default()
intents.members = True
intents.typing = False
client = commands.Bot(
    command_prefix=os.getenv("PREFIX"), intents=intents, activity=discord.Game(name="Minecraft"), case_insensitive = True
)
slash = SlashCommand(client, sync_commands=True)
guild_ids = [793981775193964564] # Put your server ID in this array.

for cog in ["Eval", "Minecraft"]:
	client.load_extension(f"extensions.{cog}")

@client.event
async def on_ready():
	print(f"{client.user.name} bot is now online.")

keep_alive.keep_alive()
client.run(os.getenv("TOKEN"))
