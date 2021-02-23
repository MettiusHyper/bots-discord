import discord
from discord.ext import commands
import ast

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

    @commands.command()
    async def ping(self, ctx):
        await ctx.send(f":ping_pong: {round(self.client.latency*1000)} ms")

    @commands.command()
    async def eval(self, ctx, *, code : str = None):
        print("lol")
        if ctx.author.guild_permissions.administrator == True:
            python = "```py\n{}\n```"
            if code == None:
                return await ctx.send("**Enviroment variable**\n'client': self.client\n'ctx': ctx")
            code = code.strip("` ")
            code = "\n".join(f"    {i}" for i in code.splitlines())
            result = "None"

            env = {
                'self': self,
                'ctx': ctx
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
                return await ctx.send(python.format(type(e).__name__ + ': ' + str(e)))

            try:
                result = str(result)
            except:
                pass
            
            await ctx.message.add_reaction("✅")
            while len(result) > 0:
                await ctx.send(python.format(result[:1988]))
                result = result[1988:]

def setup(client):
    client.add_cog(Eval(client))