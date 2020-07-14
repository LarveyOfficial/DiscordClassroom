import pymongo
import asyncio
import config
import discord
from discord.ext import commands
import utils


class Class(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['class','c'])
    async def dash(self, ctx):
        account, first_time = utils.get_profile(ctx.author.id)
        embed = discord.Embed(title="<:inv:732103029213364295> Your Classes",
                              color=config.MAINCOLOR)
        for aclass in config.CLASSES.find({'members': ctx.author.id}):
            classname = aclass['name']
            classcode = aclass['code']
            classowner = aclass['owner']
            embed.add_field(name="<:enter:732105777577459723> " + classname + " [" + classcode + "]",
                            value="Teacher: <@" + str(classowner) + ">\nSize: " + str(len(aclass['members'])) + "\n",
                            inline=False)
        embed.description = "*Use `d!join` to join and `d!create` to create a class.*"
        await ctx.send(embed=embed)

    @commands.command()
    async def join(self, ctx, code:str=None):
        account, first_time = utils.get_profile(ctx.author.id)
        chosen_class = config.CLASSES.find_one({'code': code})
        if chosen_class is not None:
            config.CLASSES.update_one({'code': code}, {'$push': {'members': ctx.author.id}})
            embed=discord.Embed(title="<:plus:732103029435924491> Class Joined", description=f"You have enrolled in **{chosen_class['name']}**.\nYou can see information about the class by typing `d!class {chosen_class['code']}`", color=config.MAINCOLOR)
            await ctx.send(embed)
            teacher_account, first_time = utils.get_profile(chosen_class['owner'])
            teacher = self.bot.get_user(chosen_class['owner'])
            if teacher is not None and teacher_account['teacher_notifications']:
                embed=discord.Embed(title="<:pin:732461353830449173> Class Notification", description=f"A student named {ctx.author.name} ({str(ctx.author.id)}) has enrolled in {chosen_class['name']} [{chosen_class['code']}]", color=config.MAINCOLOR)
                embed.set_footer(text="to disable notifications type 'd!noti disable'", icon_url="https://cdn.discordapp.com/emojis/732116410553073674.png?v=1")
                await teacher_account.send(embed=embed)




def setup(bot):
    bot.add_cog(Class(bot))
