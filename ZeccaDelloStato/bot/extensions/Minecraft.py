import discord
from discord.ext import commands
import os
import datetime
import asyncio
from replit import db as collection
from discord_slash import cog_ext
from discord_slash.utils.manage_commands import create_option

async def stipendi(self):
    data = collection["quarantini"]
    embed_var = {}
    avaiable = data[str(self.client.user.id)]/2
    guild = self.client.get_guild(793981775193964564)
    console = guild.get_role(793985236735229953)
    legislatore = guild.get_role(794134393102663680)
    giudice = guild.get_role(794134343496499201)
    architetto = guild.get_role(794134534215172157)
    tesoriere =guild.get_role(794134480306044948) 
    premium_roles = [console, legislatore, giudice, architetto, tesoriere]
    users_with_role = 0
    for member in guild.members:
        if len(set(member.roles).intersection(set(premium_roles))) > 0:
            users_with_role += 1
    percentage = 1/((len(data) - 1) + users_with_role)
    total_removed = 0
    for el in data:
        member = guild.get_member(int(el))
        if member.bot == False:
            assigned_percentage = percentage + percentage * len(set(member.roles).intersection(set(premium_roles)))
            arg = avaiable * assigned_percentage
            if arg > 1:
                quarantini = int(arg)
            else:
                quarantini = 0
            old_quarantini = data[el]
            embed_var.update({el : quarantini})
            data.update({el : (old_quarantini + quarantini)})
            total_removed += quarantini
    embed_description = "Sono stati assegnati gli stipendi, ecco un breve report."
    for stipendiato in embed_var:
        if embed_var[stipendiato] != 0:
            embed_description += f"\n<@{stipendiato}> | {embed_var[stipendiato]}"
    if embed_description != "Sono stati assegnati gli stipendi, ecco un breve report.":
        await guild.get_channel(794543080547287052).send(
            embed = discord.Embed(
                color = 0x6eab3d, title = "Stipendi", description = embed_description
            ).set_footer(text = guild.name, icon_url = guild.icon_url)
        )
        old = data[str(self.client.user.id)]
        data.update({str(self.client.user.id) : old - total_removed})
        collection["quarantini"] = data
    else:
        await guild.get_channel(794543080547287052).send(
            embed = discord.Embed(
                color = 0x6eab3d, title = "Stipendi", description = "Non ci sono state modifiche nei bilanci."
            ).set_footer(text = guild.name, icon_url = guild.icon_url)
        )

class CustomMinecraft(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        now = datetime.datetime.now() + datetime.timedelta(hours = 1)
        remaining_delta = datetime.datetime(now.year, now.month, now.day, 23, 59, 59) - now
        await asyncio.sleep(remaining_delta.seconds)
        while True:
            await stipendi(self)
            await asyncio.sleep(86400)
    
    @cog_ext.cog_slash(name="stipendi", description = "Assegna gli stipendi forzatamente (solo consoli)", options = [], guild_ids = [793981775193964564])
    @commands.command()
    async def force(self, ctx):
        console = ctx.guild.get_role(793985236735229953)
        if console in ctx.author.roles:
            await stipendi(self)
            await ctx.send(os.getenv('TICK'), hidden = True)
        else:
            await ctx.send(f"{os.getenv('CROSS')} Non hai i permessi necessari per eseguire il comando (Console)", hidden = True)
    
    @cog_ext.cog_slash(name = "pay", description = "Invia del denaro ad un giocatore", options=[
        create_option(
            name="ricevente",
            description="L'utente a cui inviare il denaro.",
            option_type=6,
            required=True
        ),
        create_option(
            name="quantità",
            description="La quantità di quarantini da inviare.",
            option_type=4,
            required=True
        ),
        create_option(
            name="ragione",
            description="La motivazione per la transazione.",
            option_type=3,
            required=False
        )
    ], guild_ids = [793981775193964564])
    @commands.command(aliases = ["paga", "transazione"])
    async def pay(self, ctx, ricevente : discord.Member, quantità : int, *, ragione : str = None):
        reciver = ricevente
        money = quantità
        reason = ragione
        if reason == None:
            reason = "Nessuna Ragione"
        var = collection["quarantini"]
        payer = ctx.author
        if str(reciver.id) not in var or str(payer.id) not in var:
            return await ctx.send(f"{os.getenv('CROSS')} Uno dei due, il pagante o il ricevente, non è stato registrato nel database!")
        try:
            money = int(money)
        except:
            return await ctx.send(f"{os.getenv('CROSS')} Inserisci un numero valido")
        if var[str(payer.id)] > money:
            reciver_new_value = var[str(reciver.id)] + money
            payer_new_value = var[str(payer.id)] - money
            var.update({str(reciver.id) : reciver_new_value})
            var.update({str(payer.id) : payer_new_value})
            collection["quarantini"] = var
            await self.client.get_channel(794242034722013214).send(f"**Nuova Transazione**\n**Pagante:** {payer.name} | {payer.id}\n**Ricevente:** {reciver.name} | {reciver.id}\n**Quarantini:** {money}\n**Ragione:** {reason}")
            await ctx.send(f"{os.getenv('TICK')} Transazione completata con successo")
        else:
            return await ctx.send(f"{os.getenv('CROSS')} Non hai abbastanza quarantini per eseguire la transazione!")

    @cog_ext.cog_slash(name = "bal", description = "Invia il bilancio", guild_ids = [793981775193964564])
    async def _bilancio(self, ctx):
        try:
            total_money = collection["quarantini"][str(ctx.author.id)]
        except:
            return await ctx.send(f"{os.getenv('CROSS')} Non sei registrato nel database, non hai quindi un conto!", hidden = True)
        #we search for logs in the last two days and, we will get an array with all of the messages objects
        logs = await self.client.get_channel(794242034722013214).history(after = (datetime.datetime.now() - datetime.timedelta(days = 2))).flatten()
        #from the logs finds the ones involving the author
        recent = "```diff"
        #devides between income and outgoings and creates a json containing all of the informations
        for message in logs:
            if str(ctx.author.id) in message.content:
                lines = message.content.splitlines()
                for n, line in enumerate(lines):
                    if str(ctx.author.id) in line:
                        if n == 1:
                            income = False
                            payer = ctx.author.id
                            reciver = int(lines[2][-18:])    
                        elif n == 2:
                            income = True
                            reciver = ctx.author.id
                            payer = int(lines[1][-18:])
                money = int(lines[3][16:])
                try:
                    reason = lines[4][12:]
                except:
                    reason = "Nessuna Ragione"
                reciver = await self.client.fetch_user(reciver)
                payer = await self.client.fetch_user(payer)
                if income == True:
                    recent += f"\n+ {money} (da {payer} a te)\nragione: {reason}\n"
                else:
                    recent += f"\n- {money} (da te a {reciver})\nragione: {reason}\n"
        recent += "```"
        #check
        if recent == "```diff```":
            recent = "```Non ci sono state transizioni recenti!```"
            
        try:
            await ctx.author.send(embed = discord.Embed(title = "Bilancio", description = f"Nel tuo conto ci sono attualmente {total_money} quarantini.\n\n**Attività Recente:**\n{recent}", color = 0x6eab3d))
            await ctx.send(f"{os.getenv('TICK')} controlla i dm", hidden = True)
        except:
            await ctx.send(f"{os.getenv('CROSS')} Non posso inviarti dm! Controlla di non aver bloccato il bot.", hidden = True)
    
    @cog_ext.cog_slash(name = "registra", description = "Aggiunge un utente ai giocatori (solo consoli)", options=[
        create_option(
            name="utente",
            description="L'utente che deve essere registrato.",
            option_type=6,
            required=True
        )
    ], guild_ids = [793981775193964564])
    async def _register(self, ctx, utente : discord.Member):
        console = ctx.guild.get_role(793985236735229953)
        if console in ctx.author.roles:
            var = collection["quarantini"]
            try:
                var[str(utente.id)]
                return await ctx.send(f"{os.getenv('CROSS')} l'utente è già registrato!", hidden = True)
            except:
                var.update({str(utente.id) : 500})
                collection["quarantini"] = var
                role = ctx.guild.get_role(797414084915626024)
                await utente.add_roles(role)
                await ctx.send(f"{os.getenv('TICK')} l'utente {utente.mention} è stato registrato correttamente")
        else:
            await ctx.send(f"{os.getenv('CROSS')} Non hai i permessi necessari per eseguire il comando (Console)", hidden = True)

def setup(client):
    client.add_cog(CustomMinecraft(client))