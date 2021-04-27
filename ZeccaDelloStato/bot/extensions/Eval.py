import os
import ast
import discord

from discord.ext import commands
from replit import db as collection
from discord_slash import cog_ext
from discord_slash.utils.manage_commands import create_option

def insert_returns(body):
    if isinstance(body[-1], ast.Expr):
        body[-1] = ast.Return(body[-1].value)
        ast.fix_missing_locations(body[-1])

    if isinstance(body[-1], ast.If):
        insert_returns(body[-1].body)
        insert_returns(body[-1].orelse)

    if isinstance(body[-1], ast.With):
        insert_returns(body[-1].body)

class Eval(commands.Cog):
    def __init__(self, client):
        self.client = client

    @cog_ext.cog_slash(name="ping", description = "Risponde con il ping del bot", guild_ids = [793981775193964564])
    async def _ping(self, ctx):
        await ctx.send(f":ping_pong: {round(self.client.latency*1000)} ms")

    @cog_ext.cog_slash(name="eval", description = "Esegue del codice (Admin Only)", 
    options=[
        create_option(
            name="code",
            description="The code that gets executed.",
            option_type=3,
            required=False
        )
    ], guild_ids = [793981775193964564])
    async def _eval(self, ctx, *, code: str = None):
        if ctx.author.guild_permissions.administrator == True:
            python = "```py\n{}\n```"
            if code == None:
                return await ctx.send("**Enviroment variable**\n'client': self.client\n'ctx': ctx\n'collection' : collection", hidden = True)
            code = code.strip("` ")
            code = "\n".join(f"    {i}" for i in code.splitlines())
            result = "None"

            env = {
                'self': self,
                'ctx': ctx,
                'collection' : collection
            }
            env.update(globals())

            try:
                fn_name = "_eval_expr"

                body = f"async def {fn_name}():\n{code}"

                parsed = ast.parse(body)
                body = parsed.body[0].body

                insert_returns(body)

                exec(compile(parsed, filename="<ast>", mode="exec"), env)

                result = (await eval(f"{fn_name}()", env))
            except Exception as e:
                return await ctx.send(python.format(type(e).__name__ + ': ' + str(e)), hidden = True)
            
            result = str(result)

            if len(result) > 1985:
                await ctx.send(f"{python.format(result[:1985])}...", hidden = True)
            else:
                await ctx.send(python.format(result), hidden = True)

        else:
            await ctx.send(f"{os.getenv('CROSS')} Non hai i permessi necessari per eseguire il comando (Amministratore)", hidden = True)

def setup(client):
    client.add_cog(Eval(client))