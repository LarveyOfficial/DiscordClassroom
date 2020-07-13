import pymongo
import asyncio
import config
import discord
from discord.ext import commands

import utils

class Class(commands.Cog):

    def setup(bot):
        bot.add_cog(Profile(bot))

    @commands.group(aliases=['class','c'])
    async def dash(self, ctx):
        if ctx.invoked_subcommand is None:
            user = ctx.author
            account, first_time = utils.get_profile(user.id)
            embed = discord.Embed(title="<:enter:732105777577459723> Your Dashboard",
                                  color = config.MAINCOLOR)
            if len(account['classes']) > 0:
                embed.add_field(name="<:inv:732103029213364295> Your Classes",value=".", inline=False)
                for aclass in config.CLASSES.find({'members': user.id}):
                    classname = aclass['name']
                    classcode = aclass['code']
                    classowner = aclass['owner']
                    embed.add_field(name="<:enter:732105777577459723> " + classname,value="Class Code : " + classcode + "\nClass Owner : <@"+str(classowner)+">\n", inline=False)
            else:
                embed.add_field(name="<:offline:732103028601258045> No Classes",value="Use `d!class join <code>` to join a class.")
            await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Class(bot))
