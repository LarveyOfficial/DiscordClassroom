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
            account, first_time = utils.get_profile(ctx.author.id)
            embed = discord.Embed(title="<:inv:732103029213364295> Your Classes",
                                  color = config.MAINCOLOR)
            for aclass in config.CLASSES.find({'members': ctx.author.id}):
                classname = aclass['name']
                classcode = aclass['code']
                classowner = aclass['owner']
                embed.add_field(name="<:enter:732105777577459723> " + classname + " ["+classcode+"]",
                                value="Teacher: <@" + str(classowner) + ">\nSize: " + str(len(aclass['members'])) + "\n",
                                inline=False)
            embed.description = "*Use `d!join` to join and `d!create` to create a class.*"
            await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Class(bot))
