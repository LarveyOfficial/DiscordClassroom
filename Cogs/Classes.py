import random
import string

import pymongo
import asyncio
import config
import discord
from discord.ext import commands
import utils


def gen_code(stringLength=6):
    """Generate a random string of letters and digits """
    lettersAndDigits = string.ascii_letters + string.digits
    return ''.join(random.choice(lettersAndDigits) for i in range(stringLength))

class Classes(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['classes', 'c'], name="class")
    async def dash(self, ctx):
        account, first_time = utils.get_profile(ctx.author.id)
        embed = discord.Embed(title="<:inv:732103029213364295> Your Classes",
                              color=config.MAINCOLOR)
        for aclass in utils.get_teaching_classes(ctx.author.id):
            classname = aclass['name']
            classcode = aclass['code']
            classowner = aclass['owner']
            embed.add_field(name="<:crown:732103028781613117> " + classname + " [" + classcode + "]",
                            value="Teacher: **You**\nStudents: " + str(len(aclass['members'])) + "\n",
                            inline=True)
        for aclass in utils.get_user_classes(ctx.author.id):
            classname = aclass['name']
            classcode = aclass['code']
            classowner = aclass['owner']
            embed.add_field(name="<:enter:732105777577459723> " + classname + " [" + classcode + "]",
                            value="Teacher: <@" + str(classowner) + ">\nClassmates: " + str(len(aclass['members'])) + "\n",
                            inline=True)
        embed.description = "*Use `d!join` to join and `d!create` to create a class.*"
        await ctx.send(embed=embed)

    @commands.command()
    async def join(self, ctx, code:str=None):
        account, first_time = utils.get_profile(ctx.author.id)
        chosen_class = config.CLASSES.find_one({'code': code})
        if chosen_class is not None:
            if chosen_class['owner'] != ctx.author.id:
                if ctx.author.id not in chosen_class['members']:
                    config.CLASSES.update_one({'code': code}, {'$push': {'members': ctx.author.id}})
                    embed=discord.Embed(title="<:plus:732103029435924491> Class Joined", description=f"You have enrolled in **{chosen_class['name']}**.\nYou can see information about the class by typing `d!class {chosen_class['code']}`", color=config.MAINCOLOR)
                    await ctx.send(embed=embed)
                    teacher_account, first_time = utils.get_profile(chosen_class['owner'])
                    teacher = self.bot.get_user(chosen_class['owner'])
                    if teacher is not None and teacher_account['teacher_notifications']:
                        embed=discord.Embed(title="<a:bell:732103030488432720> Class Notification", description=f"A student named {ctx.author.name} ({str(ctx.author.id)}) has enrolled in {chosen_class['name']} [{chosen_class['code']}]", color=config.MAINCOLOR)
                        embed.set_footer(text="to disable notifications type 'd!noti disable'", icon_url="https://cdn.discordapp.com/emojis/732116410553073674.png?v=1")
                        await teacher.send(embed=embed)
                else:
                    embed = discord.Embed(title="<:cross:732103029712617482> You are already enrolled in this class", color=config.MAINCOLOR)
                    await ctx.send(embed=embed)
            else:
                embed = discord.Embed(title="<:cross:732103029712617482> A Teacher cannot join their own class", color=config.MAINCOLOR)
                await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="<:cross:732103029712617482> That class does not exist", color=config.MAINCOLOR)
            await ctx.send(embed=embed)

    @commands.command()
    async def leave(self, ctx, code:str=None):
        account, first_time = utils.get_profile(ctx.author.id)
        chosen_class = config.CLASSES.find_one({'code': code})
        if chosen_class is not None:

            if chosen_class['owner'] == ctx.author.id:
                embed = discord.Embed(title="<:cross:732103029712617482> Use 'd!delete " + code + "' to delete a class",
                                      color=config.MAINCOLOR)
                await ctx.send(embed=embed)
                return

            if ctx.author.id in chosen_class['members']:
                config.CLASSES.update_one({'code': code}, {'$pull': {'members': ctx.author.id}})
                embed = discord.Embed(title="<:minus:732103028726824982> Left Class", description=f"You have left **{chosen_class['name']}**.", color=config.MAINCOLOR)
                await ctx.send(embed=embed)
                teacher_account, first_time = utils.get_profile(chosen_class['owner'])
                teacher = self.bot.get_user(chosen_class['owner'])
                if teacher is not None and teacher_account['teacher_notifications']:
                    embed=discord.Embed(title="<a:bell:732103030488432720> Class Notification", description=f"A Student named {ctx.author.name} ({str(ctx.author.id)}) has unenrolled from {chosen_class['name']} [{chosen_class['code']}]", color=config.MAINCOLOR)
                    embed.set_footer(text="to disable notifications type 'd!noti disable'", icon_url="https://cdn.discordapp.com/emojis/732116410553073674.png?v=1")
                    await teacher.send(embed=embed)
            else:
                embed = discord.Embed(title="<:cross:732103029712617482> You are not enrolled in that class", color=config.MAINCOLOR)
                await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="<:cross:732103029712617482> You are not enrolled in that class", color=config.MAINCOLOR)
            await ctx.send(embed=embed)

    @commands.command()
    async def create(self, ctx, name: str = None):
        account, first_time = utils.get_profile(ctx.author.id)

        teaching = list(utils.get_teaching_classes(ctx.author.id))
        if len(teaching) >= 8:
            embed = discord.Embed(title="<:card:732103029523873823> Premium",
                                  description=f"It looks like you have reached the maximum amount of classes you can teach. Premium allows for unlimited classes, and benifits all yoru students!\n\n- One time purchase\n- unlimited classes\n- tons of amazing features\n\nVisit [**Our website**](https://zombo.com) to purchase premium!",
                                  color=config.MAINCOLOR)
            await ctx.send(embed=embed)
            return

        if name is None:
            embed = discord.Embed(title="<:people:732103029565947934> Create a new class",
                                  description=f"Creating a class is simple. All you need to do is type the name of the class in this channel.",
                                  color=config.MAINCOLOR)
            embed.set_footer(text="Message timout in 60 seconds", icon_url="https://cdn.discordapp.com/emojis/732714132461191330.png?v=1")
            start_message = await ctx.send(embed=embed)

            def check(msg):
                return msg.author.id == ctx.author.id and msg.channel.id == ctx.channel.id and len(msg.content) < 100

            try:
                name_message = await self.bot.wait_for('message', check=check, timeout=60.0)
                name = name_message.content
            except asyncio.TimeoutError:
                embed.description = "Class creation has timed out. Please type `d!create` to try again."
                embed.set_footer()
                await start_message.edit(embed=embed)
                return

        new_class = {'name': name, 'code': gen_code(), 'owner': ctx.author.id, 'members': [], 'assignments': []}
        config.CLASSES.insert_one(new_class)

        embed = discord.Embed(title="<:checkb:732103029020557323> Class Created", color=config.MAINCOLOR, description=f"**{new_class['name']} [{new_class['code']}] has been created.**\n\nStudents can enroll by typing `d!join {new_class['code']}`.\nView more information with `d!class {new_class['code']}`")
        await ctx.send(embed=embed)

        if account['is_student']:
            config.USERS.update({'user_id': ctx.author.id}, {'$set': {'is_student': False}})

        if account['teacher_notifications']:
            embed = discord.Embed(title="<a:bell:732103030488432720> Class Notification",
                                  description=f"You will receive notifications from your class {new_class['name']} [{new_class['code']}] and can be turned off at any time.",
                                  color=config.MAINCOLOR)
            embed.set_footer(text="to disable notifications type 'd!noti disable'",
                             icon_url="https://cdn.discordapp.com/emojis/732116410553073674.png?v=1")
            await ctx.author.send(embed=embed)

def setup(bot):
    bot.add_cog(Classes(bot))
