import discord
from discord.ext import commands
import os
import keep_alive

intents = discord.Intents.default()
intents.members = True
intents.typing = False
client = commands.Bot(
    command_prefix=os.getenv("PREFIX"), intents=intents, activity=discord.Game(name="Minecraft"), case_insensitive = True
)
for cog in ["Eval", "Minecraft"]:
	client.load_extension(f"extensions.{cog}")

@client.event
async def on_ready():
	print(f"{client.user.name} bot is now online.")

keep_alive.host()
client.run(os.getenv("TOKEN"))
