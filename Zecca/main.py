import discord
from discord.ext import commands
import os
import keep_alive

intents = discord.Intents.default()
intents.members = True
intents.bans = intents.integrations = intents.webhooks = intents.invites = intents.typing = False
client = commands.Bot(command_prefix=os.getenv("PREFIX"), intents=intents, activity=discord.Game(name="Minecraft"))
for cog in ["Eval", "Minecraft"]:
	client.load_extension(f"extensions.{cog}")

@client.event
async def on_ready():
	print(f"{client.user.name} bot is now online.")


keep_alive.host()

client.run(os.getenv("TOKEN"))
