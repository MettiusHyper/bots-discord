import discord
from discord.ext import commands
import os
import datetime
import asyncio
from core.Find import get_member
from replit import db as collection

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
        embed_description += f"\n<@{stipendiato}> | {embed_var[stipendiato]}"
    await guild.get_channel(794543080547287052).send(
        embed = discord.Embed(
            color = 0x6eab3d, title = "Stipendi", description = embed_description
        ).set_footer(text = guild.name, icon_url = guild.icon_url)
    )
    old = data[str(self.client.user.id)]
    data.update({str(self.client.user.id) : old - total_removed})
    collection["quarantini"] = data

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
    
    @commands.command()
    async def force(self, ctx):
        console = ctx.guild.get_role(793985236735229953)
        if console in ctx.author.roles:
            await stipendi(self)
            await ctx.message.add_reaction(os.getenv('TICK'))
    
    @commands.command(aliases = ["paga", "transazione"])
    async def pay(self, ctx, member : str = None, money : str = None, *, reason : str = None):
        if reason == None:
            reason = "Nessuna Ragione"
        var = collection["quarantini"]
        reciver = get_member(ctx, member)
        if reciver == None:
            return await ctx.send(f"{os.getenv('CROSS')} Impossibile trovare l'utente")
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
    
    @commands.command(aliases = ["saldo", "bal", "balance"])
    async def bilancio(self, ctx):
        try:
            total_money = collection["quarantini"][str(ctx.author.id)]
        except:
            return await ctx.send(f"{os.getenv('CROSS')} Non sei registrato nel database, non hai quindi un conto!")
        async with ctx.channel.typing():
            #we search for logs in the last two days and, we will get an array with all of the messages objects
            logs = await self.client.get_channel(794242034722013214).history(after = (datetime.datetime.now() - datetime.timedelta(days = 2))).flatten()
            #from the logs finds the ones involving the author
            author_logs = []
            for message in logs:
                if str(ctx.author.id) in message.content:
                    author_logs.append(message)
            #check
            if len(author_logs) <= 0:
                recent = "```Non ci sono state transizioni recenti!```"
            else:
                #devides between income and outgoings and creates a json containing all of the informations
                InOut = []
                for message in author_logs:
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
                    InOut.append({
                        "income" : income,
                        "reciver" : reciver,
                        "payer" : payer,
                        "amount" : money,
                        "reason" : reason
                    })
                #constructing string
                recent = "```diff"
                for el in InOut:
                    reciver = await self.client.fetch_user(el["reciver"])
                    payer = await self.client.fetch_user(el["payer"])
                    amount = el["amount"]
                    reason = el["reason"]
                    if el["income"] == True:
                        recent += f"\n+ {amount} (da {payer} a te)\nragione: {reason}\n"
                    else:
                        recent += f"\n- {amount} (da te a {reciver})\nragione: {reason}\n"
                recent += "```"
            try:
                await ctx.author.send(embed = discord.Embed(title = "Bilancio", description = f"Nel tuo conto ci sono attualmente {total_money} quarantini.\n\n**Attività Recente:**\n{recent}", color = 0x6eab3d))
                await ctx.message.add_reaction(os.getenv("TICK"))
            except:
                return await ctx.send(f"{os.getenv('CROSS')} Non posso inviarti dm! Controlla di non aver bloccato il bot.")
    
    @commands.command(aliases = ["registra", "aggiungi", "add"])
    async def register(self, ctx, member : str = None):
        console = ctx.guild.get_role(793985236735229953)
        if console in ctx.author.roles:
            member = get_member(ctx, member)
            if member == None:
                return await ctx.send(f"{os.getenv('CROSS')} Impossibile trovare l'utente")
            var = collection["quarantini"]
            try:
                var[str(member.id)]
                return await ctx.send(f"{os.getenv('CROSS')} l'utente è già registrato!")
            except:
                var.update({str(member.id) : 500})
                collection["quarantini"] = var
                role = ctx.guild.get_role(797414084915626024)
                await member.add_roles(role)
                await ctx.send(f"{os.getenv('TICK')} l'utente {member.mention} è stato registrato correttamente")
        else:
            return await ctx.send(f"{os.getenv('CROSS')} Non sei un console! Non puoi eseguire questo comando.")

def setup(client):
    client.add_cog(CustomMinecraft(client))