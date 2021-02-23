import discord
from discord.ext import commands
from datetime import datetime
import os
import keep_alive
from replit import db

intents = discord.Intents.default()
intents.members = True
intents.bans = intents.integrations = intents.webhooks = intents.invites = intents.typing = False
client = commands.Bot(command_prefix= "%", intents=intents)

@client.event
async def on_ready():
    client.load_extension("Eval")
    print(f"{client.user.name} bot is now online.")

@client.event
async def on_message(message):   
    if message.channel.id == 808617734539182100 and message.embeds != []:
        data = db["data"]
        data.update({str(message.id) : message.embeds[0].fields[1].value})
        db["data"] = data
    await client.process_commands(message)

@client.event
async def on_raw_message_delete(payload):
    if payload.channel_id == 808617734539182100:
        data = db["data"]
        name = data[str(payload.message_id)]
        await client.get_guild(808617491580452875).get_channel(809910085622038542).send(embed = discord.Embed(
            title = "Richiesta Completata ✅", description = f"La richiesta di `{name}` è stata completata", timestamp = datetime.utcnow(), color = 0xE8B125
        ).set_footer(text = client.get_guild(808617491580452875).name, icon_url = client.get_guild(808617491580452875).icon_url))

keep_alive.host()

client.run(os.getenv("TOKEN"))