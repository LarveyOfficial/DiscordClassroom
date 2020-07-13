import pymongo
import asyncio
import config
import discord
from discord.ext import commands

import utils


class Profile(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['p', 'user'])
    async def profile(self, ctx, user: discord.Member = None):
        owner = False
        if user is None:
            user = ctx.author
            owner = True
        account, first_time = utils.get_profile(user.id)
        embed = discord.Embed(title=f"<:enter:732105777577459723> {user.name}'s Profile",
                              color=config.MAINCOLOR)
        embed.set_thumbnail(url=str(user.avatar_url))
        if owner and account['is_student'] and len(account['classes']) < 1:
            embed.set_footer(text="Are you a teacher? Make sure to type 'd!class'", icon_url="https://cdn.discordapp.com/emojis/732116410553073674.png?v=1")
        if account['bio'] is None:
            embed.add_field(name="<:news:732103029565685770> Note", value=f"{user.name}'s Note can be set using `d!note`", inline=False)
        else:
            embed.add_field(name="<:news:732103029565685770> Note", value=f"{account['bio']}", inline=False)

        if account['google_classroom'] is not None:
            embed.add_field(name="<:people:732103029565947934> Google Classroom", value=f"{account['google_classroom']} <:check_verify:732103029121089638>", inline=False)
        else:
            embed.add_field(name="<:people:732103029565947934> Google Classroom",
                            value="<:cross:732103029712617482> Not Linked. [**Link now**](https://classroom.google.com)", inline=False)

        if len(account['classes']) > 0:
            if account['is_student']:
                embed.add_field(name="<:inv:732103029213364295> Classes", value=f"{str(len(account['classes']))} Classes joined", inline=True)
                embed.add_field(name="<:auth:732103030110945332> Role", value=f"Student", inline=True)
            else:
                embed.add_field(name="<:inv:732103029213364295> Classes", value=f"{str(len(account['classes']))} Classes teaching", inline=True)
                embed.add_field(name="<:auth:732103030110945332> Role", value=f"Teacher", inline=True)



        await ctx.send(embed=embed)




def setup(bot):
    bot.add_cog(Profile(bot))
