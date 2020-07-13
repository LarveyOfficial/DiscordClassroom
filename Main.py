import sys

import asyncio

import config

print("Bot Writen By: KAJ7#0001, Larvey#0001")
# Imports
import discord
from discord.ext import commands
import logging

logging.basicConfig(level=logging.INFO, format="DiscordClassroom [%(levelname)s] | %(message)s")

async def get_prefix(bot, message):
    return commands.when_mentioned_or("d!")(bot, message)


# Set prefix and set case insensitive to true so the a command will work if miscapitlized
bot = commands.Bot(command_prefix=get_prefix, case_insensitive=True)

# Remove default help command
bot.remove_command("help")

@bot.command(aliases=['link', 'join'])
async def invite(ctx):
    await ctx.send(embed=discord.Embed(
        description="🔗 [**Invite Link**](https://discord.com/api/oauth2/authorize?client_id=732013656149196823&permissions=363586&scope=bot)",
        color=config.MAINCOLOR))


@bot.command(aliases=['v'])
async def vote(ctx):
    await ctx.send(
        embed=discord.Embed(description="<a:dbl:732105777703288883> [**Vote for the bot here**](https://top.gg/bot/732013656149196823/vote)",
                            color=config.MAINCOLOR))

# Cogs
cogs = ["Profile"]

# Starts all cogs
for cog in cogs:
    bot.load_extension("Cogs." + cog)


# Check to see if the user invoking the command is in the OWNERIDS Config
def owner(ctx):
    return int(ctx.author.id) in config.OWNERIDS


@bot.command()
@commands.check(owner)
async def restart(ctx):
    await ctx.send("Force Restarting...")
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
        activity=discord.Activity(type=discord.ActivityType.watching, name="Bot Restarted!"))
    await asyncio.sleep(10)
    await bot.change_presence(activity=None)


# Starts bot
bot.run(config.TOKEN)
