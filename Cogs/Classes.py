import datetime
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
    async def dash(self, ctx, code:str=None, *, value:str=None):
        account, first_time = utils.get_profile(ctx.author)
        if code is None:
            embed = discord.Embed(title=f"{utils.emoji('inv')} Your Classes",
                                  color=config.MAINCOLOR)
            for aclass in utils.get_teaching_classes(ctx.author.id):
                classname = aclass['name']
                classcode = aclass['code']
                classowner = aclass['owner']
                embed.add_field(name=f"{utils.emoji('crown')} " + classname + " [" + classcode + "]",
                                value="Teacher: **You**\nStudents: " + str(len(aclass['members'])) + "\n",
                                inline=True)
            for aclass in utils.get_user_classes(ctx.author.id):
                classname = aclass['name']
                classcode = aclass['code']
                classowner = aclass['owner']
                embed.add_field(name=f"{utils.emoji('enter')} " + classname + " [" + classcode + "]",
                                value="Teacher: <@" + str(classowner) + ">\nClassmates: " + str(len(aclass['members'])) + "\n",
                                inline=True)
            embed.description = "*Use `d!join` to join and `d!create` to create a class.*"
            await ctx.send(embed=embed)
        else:
            the_class = config.CLASSES.find_one({'code': code})
            if the_class is None:
                embed = discord.Embed(title=f"{utils.emoji('cross')} That class does not exist",
                                      color=config.MAINCOLOR)
                await ctx.send(embed=embed)
            else:
                if value is None:
                    if ctx.author.id == the_class['owner'] or ctx.author.id in the_class['members']:
                        if ctx.author.id == the_class['owner']:
                            embed = discord.Embed(title=f"{utils.emoji('crown')} {the_class['name']} Info [**{the_class['code']}**]",description=f"Teacher: **You**\nClass Size: {str(len(the_class['members']))}", color = config.MAINCOLOR)
                        else:
                            embed = discord.Embed(title=f"{utils.emoji('inv')} {the_class['name']} Info [**{the_class['code']}**]",description=f"Teacher: <@{the_class['owner']}>\nClass size: {str(len(the_class['members']))}", color = config.MAINCOLOR)
                        mystring = f"No Students in class."
                        i = 1
                        for student in the_class['members']:
                            if i == 1:
                                mystring = ""
                            if i < len(the_class['members']):
                                if i % 3 == 0 and i != 0:
                                    mystring += f"<@{student}>\n"
                                else:
                                    mystring += f"<@{student}>, "
                            else:
                                mystring += f"<@{student}>"
                            i += 1
                        if the_class['link_joining']:
                            embed.add_field(name=f"{utils.emoji('enter')} Link Join", inline=False, value=f"[**Invite Link**](https://discordclassroom.com/{the_class['code']})")
                        embed.add_field(name=f"{utils.emoji('people')} Class Directory", value=mystring)
                        if ctx.author.id == the_class['owner']:
                            emoji_dict = {True: f"{utils.emoji('on')}", False: f"{utils.emoji('off')}"}
                            embed.add_field(name=f"{utils.emoji('settings')} Settings", inline=False, value=f"{emoji_dict[the_class['code_joining']]} Code joining\n{emoji_dict[the_class['link_joining']]} Link Joining\n{emoji_dict[the_class['notifications']]} Notifications\n{emoji_dict[the_class['google_classroom']]} Google Classroom Link\n{emoji_dict[account['premium']]} Premium Features\n\n*to toggle these values, type `d!class {the_class['code']} <value>`*")

                        await ctx.send(embed=embed)
                    else:
                        embed = discord.Embed(title=f"{utils.emoji('cross')} That class does not exist",
                                              color=config.MAINCOLOR)
                        await ctx.send(embed=embed)
                else:
                    value_dict = {"joining": "code_joining", "link": "link_joining", "notifications": "notifications", "gclassroom": "google_classroom"}
                    value = value.lower()
                    values = {"joining", "notifications", "gclassroom", "link"}
                    if ctx.author.id == the_class['owner']:
                        if value in values:
                            if the_class[value_dict[value]] == True:
                                config.CLASSES.update_one({'code': code}, {'$set': {value_dict[value]: False}})
                                embed = discord.Embed(title=f"{utils.emoji('off')} Setting **{value}** was turned Off.", color = config.MAINCOLOR)
                            else:
                                config.CLASSES.update_one({'code': code}, {'$set': {value_dict[value]: True}})
                                embed = discord.Embed(title=f"{utils.emoji('on')} Setting **{value}** was turned On.", color = config.MAINCOLOR)
                            await ctx.send(embed=embed)
                        else:
                            embed = discord.Embed(title=f"{utils.emoji('cross')} That value does not Exist.",description="Please try one of the following\nJoining,\nNotifications,\nGClassroom", color = config.MAINCOLOR)
                            await ctx.send(embed=embed)
                    elif ctx.author.id in the_class['members']:
                        embed = discord.Embed(title=f"{utils.emoji('cross')} Only the Teacher can change values.", color = config.MAINCOLOR)
                        await ctx.send(embed=embed)
                    else:
                        embed = discord.Embed(title=f"{utils.emoji('cross')} That class does not exist", color = config.MAINCOLOR)
                        await ctx.send(embed=embed)



    @commands.command()
    async def join(self, ctx, code:str=None):
        account, first_time = utils.get_profile(ctx.author)
        chosen_class = config.CLASSES.find_one({'code': code})
        if chosen_class is not None:
            if chosen_class['owner'] != ctx.author.id:
                if chosen_class['code_joining']:
                    if ctx.author.id not in chosen_class['members']:
                        config.CLASSES.update_one({'code': code}, {'$push': {'members': ctx.author.id}})
                        embed=discord.Embed(title=f"{utils.emoji('plus')} Class Joined", description=f"You have enrolled in **{chosen_class['name']}**.\nYou can see information about the class by typing `d!class {chosen_class['code']}`", color=config.MAINCOLOR)
                        await ctx.send(embed=embed)
                        teacher = self.bot.get_user(chosen_class['owner'])
                        if teacher is not None and chosen_class['notifications']:
                            config.NOTIFICATIONS.insert_one({'date': datetime.datetime.utcnow(),
                                                             'title': f"{utils.emoji('bell')} Class Notification",
                                                             'content': f"A student named {ctx.author.name} ({str(ctx.author.id)}) has enrolled in {chosen_class['name']} [{chosen_class['code']}]",
                                                             'footer': f"to disable notifications type 'd!class {chosen_class['code']} notifications'",
                                                             'footer_icon': "https://cdn.discordapp.com/emojis/732116410553073674.png?v=1",
                                                             'reciever': teacher.id})
                    else:
                        embed = discord.Embed(title=f"{utils.emoji('cross')} You are already enrolled in this class", color=config.MAINCOLOR)
                        await ctx.send(embed=embed)
                else:
                    embed = discord.Embed(title=f"{utils.emoji('cross')} That class does not exist", color=config.MAINCOLOR)
                    await ctx.send(embed=embed)

            else:
                embed = discord.Embed(title=f"{utils.emoji('cross')} A Teacher cannot join their own class", color=config.MAINCOLOR)
                await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title=f"{utils.emoji('cross')} That class does not exist", color=config.MAINCOLOR)
            await ctx.send(embed=embed)

    @commands.command()
    async def add(self, ctx, code:str=None, *, user: discord.Member = None):
        if code is not None:
            chosen_class = config.CLASSES.find_one({'code': code})
            if chosen_class is not None:
                if chosen_class['owner'] == ctx.author.id:
                    if user is not None:
                        if user.id is not None:
                            if user.id not in chosen_class['members']:
                                config.CLASSES.update_one({'code': code}, {'$push': {'members': user.id}})
                                embed = discord.Embed(title=f"{utils.emoji('plus')} Student Added", description=f"{user.name} has been added to the class",color = config.MAINCOLOR)
                                await ctx.send(embed=embed)
                                if chosen_class['notifications']:
                                    config.NOTIFICATIONS.insert_one({'date': datetime.datetime.utcnow(),
                                                                     'title': f"{utils.emoji('bell')} You have been added to {chosen_class['name']}",
                                                                     'content': f"<@{chosen_class['owner']}> has added you to their class.",
                                                                     'footer': None,
                                                                     'footer_icon': None,
                                                                     'reciever': user.id})
                            else:
                                embed = discord.Embed(title=f"{utils.emoji('cross')} User is already in the class.", color=config.MAINCOLOR)
                                await ctx.send(embed=embed)
                        else:
                            embed = discord.Embed(title=f"{utils.emoji('cross')} That user does not exist.", color=config.MAINCOLOR)
                            await ctx.send(embed=embed)
                    else:
                        embed = discord.Embed(title=f"{utils.emoji('cross')} Please specify a user.", color=config.MAINCOLOR)
                        await ctx.send(embed=embed)
                else:
                    if ctx.author.id in chosen_class['members']:
                        embed = discord.Embed(title=f"{utils.emoji('cross')} Only the teacher can use this command.", color=config.MAINCOLOR)
                        await ctx.send(embed=embed)
                    else:
                        embed = discord.Embed(title=f"{utils.emoji('cross')} That class does not exist.", color=config.MAINCOLOR)
                        await ctx.send(embed=embed)
            else:
                embed = discord.Embed(title=f"{utils.emoji('cross')} That class does not exist.", color=config.MAINCOLOR)
                await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title=f"{utils.emoji('cross')} Please specify a class code.", color=config.MAINCOLOR)
            await ctx.send(embed=embed)

    @commands.command(aliases=['kick', 'rem'])
    async def remove(self, ctx, code: str = None, *, user: discord.Member = None):
        if code is not None:
            chosen_class = config.CLASSES.find_one({'code': code})
            if chosen_class is not None:
                if chosen_class['owner'] == ctx.author.id:
                    if user is not None:
                        if user.id is not None:
                            if user.id in chosen_class['members']:
                                config.CLASSES.update_one({'code': code}, {'$pull': {'members': user.id}})
                                embed = discord.Embed(title=f"{utils.emoji('minus')}> Student Removed", description=f"{user.name} has been removed from the class",color = config.MAINCOLOR)
                                await ctx.send(embed=embed)
                                if chosen_class['notifications']:
                                    config.NOTIFICATIONS.insert_one({'date': datetime.datetime.utcnow(),
                                                                     'title': f"{utils.emoji('bell')} You have been removed from {chosen_class['name']}",
                                                                     'content': f"<@{chosen_class['owner']}> has removed you from their class.",
                                                                     'footer': None,
                                                                     'footer_icon': None,
                                                                     'reciever': user.id})
                            else:
                                embed = discord.Embed(title=f"{utils.emoji('cross')} User not in the class.", color=config.MAINCOLOR)
                                await ctx.send(embed=embed)
                        else:
                            embed = discord.Embed(title=f"{utils.emoji('cross')} That user does not exist.", color=config.MAINCOLOR)
                            await ctx.send(embed=embed)
                    else:
                        embed = discord.Embed(title=f"{utils.emoji('cross')} Please specify a user.", color=config.MAINCOLOR)
                        await ctx.send(embed=embed)
                else:
                    if ctx.author.id in chosen_class['members']:
                        embed = discord.Embed(title=f"{utils.emoji('cross')} Only the teacher can use this command.", color=config.MAINCOLOR)
                        await ctx.send(embed=embed)
                    else:
                        embed = discord.Embed(title=f"{utils.emoji('cross')} That class does not exist.", color=config.MAINCOLOR)
                        await ctx.send(embed=embed)
            else:
                embed = discord.Embed(title=f"{utils.emoji('cross')} That class does not exist.", color=config.MAINCOLOR)
                await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title=f"{utils.emoji('cross')} Please specify a class code.", color=config.MAINCOLOR)
            await ctx.send(embed=embed)



    @commands.command()
    async def leave(self, ctx, code:str=None):
        chosen_class = config.CLASSES.find_one({'code': code})
        if chosen_class is not None:

            if chosen_class['owner'] == ctx.author.id:
                embed = discord.Embed(title=f"{utils.emoji('cross')} Use 'd!delete " + code + "' to delete a class",
                                      color=config.MAINCOLOR)
                await ctx.send(embed=embed)
                return

            if ctx.author.id in chosen_class['members']:
                config.CLASSES.update_one({'code': code}, {'$pull': {'members': ctx.author.id}})
                embed = discord.Embed(title=f"{utils.emoji('minus')} Left Class", description=f"You have left **{chosen_class['name']}**.", color=config.MAINCOLOR)
                await ctx.send(embed=embed)
                teacher = self.bot.get_user(chosen_class['owner'])
                if teacher is not None and chosen_class['notifications']:
                    config.NOTIFICATIONS.insert_one({'date': datetime.datetime.utcnow(),
                                                     'title': f"{utils.emoji('bell')} Class Notification",
                                                     'content': f"A Student named {ctx.author.name} ({str(ctx.author.id)}) has unenrolled from {chosen_class['name']} [{chosen_class['code']}]",
                                                     'footer': f"to disable notifications type 'd!class {chosen_class['code']} notifications'",
                                                     'footer_icon': "https://cdn.discordapp.com/emojis/732116410553073674.png?v=1",
                                                     'reciever': teacher.id})
            else:
                embed = discord.Embed(title=f"{utils.emoji('cross')} You are not enrolled in that class", color=config.MAINCOLOR)
                await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title=f"{utils.emoji('cross')} You are not enrolled in that class", color=config.MAINCOLOR)
            await ctx.send(embed=embed)

    @commands.command(aliases=['cr'])
    async def create(self, ctx, *, name: str = None):
        account, first_time = utils.get_profile(ctx.author)

        teaching = list(utils.get_teaching_classes(ctx.author.id))
        if len(teaching) >= 8:
            embed = discord.Embed(title=f"{utils.emoji('card')} Premium",
                                  description=f"It looks like you have reached the maximum amount of classes you can teach. Premium allows for unlimited classes, and benifits all yoru students!\n\n- One time purchase\n- unlimited classes\n- tons of amazing features\n\nVisit [**Our website**](https://zombo.com) to purchase premium!",
                                  color=config.MAINCOLOR)
            await ctx.send(embed=embed)
            return

        if name is None:
            embed = discord.Embed(title=f"{utils.emoji('people')} Create a new class",
                                  description=f"Creating a class is simple. All you need to do is type the name of the class in this channel.",
                                  color=config.MAINCOLOR)
            embed.set_footer(text=f"Message timout in 60 seconds", icon_url="https://cdn.discordapp.com/emojis/732714132461191330.png?v=1")
            start_message = await ctx.send(embed=embed)

            def check(msg):
                return msg.author.id == ctx.author.id and msg.channel.id == ctx.channel.id and len(msg.content) < 100

            try:
                name_message = await self.bot.wait_for('message', check=check, timeout=60.0)
                name = name_message.content
            except asyncio.TimeoutError:
                embed.description = f"Class creation has timed out. Please type `d!create` to try again."
                embed.set_footer()
                await start_message.edit(embed=embed)
                return

        new_class = {'name': name, 'code': gen_code(), 'owner': ctx.author.id, 'members': [], 'assignments': [], 'code_joining': True, 'link_joining': True, 'notifications': True, 'google_classroom': False}
        config.CLASSES.insert_one(new_class)

        embed = discord.Embed(title=f"{utils.emoji('checkb')} Class Created", color=config.MAINCOLOR, description=f"**{new_class['name']} [{new_class['code']}] has been created.**\n\nStudents can enroll by typing `d!join {new_class['code']}` or visiting https://discordclassroom.com/{new_class['code']}.\nView more information with `d!class {new_class['code']}`")
        await ctx.send(embed=embed)

        if account['is_student']:
            config.USERS.update({'user_id': ctx.author.id}, {'$set': {'is_student': False}})

        if account['teacher_notifications']:
            embed = discord.Embed(title=f"{utils.emoji('bell')} Class Notification",
                                  description=f"You will receive notifications from your class {new_class['name']} [{new_class['code']}] and can be turned off at any time.",
                                  color=config.MAINCOLOR)
            embed.set_footer(text=f"to disable notifications type 'd!class {new_class['code']} notifications'",
                             icon_url="https://cdn.discordapp.com/emojis/732116410553073674.png?v=1")
            await ctx.author.send(embed=embed)

    @commands.command()
    async def announce(self, ctx, code: str=None, *, message: str=None):
        if code is None:
            embed = discord.Embed(title=f"{utils.emoji('cross')} Please specify a class code.", color = config.MAINCOLOR)
            await ctx.send(embed = embed)
        else:
            chosen_class = config.CLASSES.find_one({'code': code})
            if message is None:
                embed = discord.Embed(title=f"{utils.emoji('cross')} Please specify a message.", color = config.MAINCOLOR)
                await ctx.send(embed = embed)
            else:
                if len(message) > 2000:
                    embed = discord.Embed(title=f"{utils.emoji('cross')} Message has passed the 2000 character limit.", color = config.MAINCOLOR)
                    await ctx.send(embed = embed)
                else:
                    if chosen_class is None:
                        embed = discord.Embed(title=f"{utils.emoji('cross')} This class does not exist.", color = config.MAINCOLOR)
                        await ctx.send(embed = embed)
                    else:
                        if chosen_class['owner'] != ctx.author.id and ctx.author.id in chosen_class['members']:
                            embed = discord.Embed(title=f"{utils.emoji('cross')} Only the teacher can send an announcement.", color = config.MAINCOLOR)
                            await ctx.send(embed = embed)
                        elif chosen_class['owner'] == ctx.author.id:
                            if len(chosen_class['members']) == 0:
                                embed = discord.Embed(title=f"{utils.emoji('cross')} There are no students in this class.", color = config.MAINCOLOR)
                                await ctx.send(embed = embed)
                            else:
                                embed = discord.Embed(title=f"{utils.emoji('announce')} Teacher Announcement",description=f"Your Teacher has sent the following announcement:\n\n{message}", color = config.MAINCOLOR)
                                i = 0
                                for member in chosen_class['members']:
                                    user = discord.utils.get(self.bot.get_all_members(), id=member)
                                    await user.send(embed=embed)
                                    i += 1
                                embed = discord.Embed(title=f"{utils.emoji('checkb')} Teacher Announcement", description=f"Announcement sent to {i} student(s).",color=config.MAINCOLOR)
                                await ctx.send(embed=embed)
                        else:
                            embed = discord.Embed(title=f"{utils.emoji('cross')} This class does not exist.", color = config.MAINCOLOR)
                            await ctx.send(embed = embed)



def setup(bot):
    bot.add_cog(Classes(bot))
