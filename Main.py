import sys
import asyncio
import config
import discord
from discord.ext import commands
import logging

import utils

print("Bot Writen By: KAJ7#0001, Larvey#0001")

local_version = "v0.1.14a"

logging.basicConfig(level=logging.INFO, format="DiscordClassroom [%(levelname)s] | %(message)s")


async def get_prefix(bot, message):
    return commands.when_mentioned_or(config.PREFIX)(bot, message)


# Set prefix and set case insensitive to true so the a command will work if miscapitlized
bot = commands.Bot(command_prefix=get_prefix, case_insensitive=True)

# Remove default help command
bot.remove_command("help")

def owner(ctx):
    return int(ctx.author.id) in config.OWNERIDS

@bot.command(aliases=['link'])
async def invite(ctx):
    await ctx.send(embed=discord.Embed(
        description="🔗 [**Invite Link**](https://discord.com/api/oauth2/authorize?client_id=732013656149196823&permissions=363586&scope=bot)",
        color=config.MAINCOLOR))


@bot.command()
async def help(ctx):
    await ctx.send(embed=discord.Embed(
        description="`d!profile` - Show your profile\n`d!class [code]` - use d!class to vies your classes. Add a code to view specific information about a class\n`d!join <code>` - join a class\n`d!leave <code>` - leave a class\n`d!create [name]` - start the class creation wizard\n`d!note [note]` - start the note setting wizard\n\n**Teacher Commands**\n`d!remove <user>` - remove a user from a class\n`d!announce <class> <announcement>` - send a message to your class\n`d!add <class> <user>` - add a user to a class directly\n\n**Notes**\n*`Users can join classes with the class join link found in the class info (d!class <code>)`*\n\n*`You can change settings such as notifications using d!class <code> <setting to toggle>`*\n\n*`visit us at`*https://discordclassroom.com",
        color=config.MAINCOLOR))


@bot.command(aliases=['v'])
async def vote(ctx):
    await ctx.send(
        embed=discord.Embed(description="<a:dbl:732105777703288883> [**Vote for the bot here**](https://top.gg/bot/732013656149196823/vote)",
                            color=config.MAINCOLOR))

@bot.command()
async def repo(ctx):
    await ctx.send(
        embed=discord.Embed(description=utils.emoji('git') + " [**View Source code**](https://github.com/LuisVervaet/DiscordClassroom)",
                            color=config.MAINCOLOR))

@bot.command()
async def version(ctx):
    current_version = utils.get_new_version()
    if current_version != local_version:
        embed = discord.Embed(title=f"{utils.emoji('cloud')} Updates are available!", description=f"**{current_version}**\n\n{utils.get_new_version_text()}\n\n[**Click Me to Update!**](https://github.com/LuisVervaet/DiscordClassroom)", color = config.ERRORCOLOR)
        embed.set_footer(text="This bot is running " + local_version)
    else:
        embed = discord.Embed(title=f"{utils.emoji('check')} You are up to date!", color = config.MAINCOLOR)
    await ctx.send(embed=embed)

@bot.group()
@commands.check(owner)
async def purge(ctx):
    if ctx.invoked_subcommand is None:
        embed = discord.Embed(title="<:error:732714132461191330> WARNING", description="This command is very dangerous, use `d!purge confirm` to purge the DB", color = config.ERRORCOLOR)
        await ctx.send(embed=embed)

@purge.command()
@commands.check(owner)
async def confirm(ctx):
    embed = discord.Embed(description="<:error:732714132461191330> Purging DB", color = config.ERRORCOLOR)
    msg = await ctx.send(embed=embed)
    x = config.CLASSES.delete_many({})
    y = config.USERS.delete_many({})
    embed = discord.Embed(title="<:checkb:732103029020557323> Purged DB", description=f"Deleted {x.deleted_count} Classes, and {y.deleted_count} Users from the DB", color = config.MAINCOLOR)
    await msg.edit(embed=embed)



# Cogs
cogs = ["Profile", "Classes", "Notifications"]

# Starts all cogs
for cog in cogs:
    bot.load_extension("Cogs." + cog)


# Check to see if the user invoking the command is in the OWNERIDS Config



@bot.command()
@commands.check(owner)
async def restart(ctx):
    await ctx.send("Force Restarting...")
    await bot.change_presence(
        activity=discord.Activity(type=discord.ActivityType.watching, name="Restarting, hold on..."),
        status=discord.Status.idle)
    sys.exit()

# Restarts and reloads all cogs
@bot.command()
@commands.check(owner)
async def reload(ctx):
    """
    Restart the bot.
    """

    restarting = discord.Embed(
        title="Restarting...",
        color=config.MAINCOLOR
    )
    msg = await ctx.send(embed=restarting)
    for cog in cogs:
        bot.reload_extension("Cogs." + cog)
        restarting.add_field(name=f"{cog}", value="✅ Restarted!")
        #await msg.edit(embed=restarting)
    restarting.title = "Bot Restarted"
    await msg.edit(embed=restarting)
    logging.info(
        f"Bot has been restarted succesfully in {len(bot.guilds)} server(s) with {len(bot.users)} users by {ctx.author.name}#{ctx.author.discriminator} (ID - {ctx.author.id})!")
    await msg.delete(delay=3)
    if ctx.guild != None:
        await ctx.message.delete(delay=3)

@bot.event
async def on_guild_join(guild):
    logging.info("JOINED guild " + guild.name + " | current guilds: " + str(len(bot.guilds)))


@bot.event
async def on_guild_remove(guild):
    logging.info("LEFT guild " + guild.name + " | current guilds: " + str(len(bot.guilds)))


# Command error
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        pass
    else:
        embed = discord.Embed(
            description = f"<:poo:732103029553364992> An error has occured while executing this command!\n Please [**join the support server**](https://discord.gg/kXKbKXx) and report the issue!",
            color=config.ERRORCOLOR
        )
        await ctx.send(embed=embed)
        raise error


# On ready
@bot.event
async def on_ready():
    logging.info(f"Bot has started succesfully in {len(bot.guilds)} server(s) with {len(bot.users)} users!")
    await bot.change_presence(
        activity=discord.Activity(type=discord.ActivityType.watching, name="Bot Restarted!"),
        status=discord.Status.online)
    await asyncio.sleep(5)
    await bot.change_presence(activity=None)


# Starts bot
bot.run(config.TOKEN)
