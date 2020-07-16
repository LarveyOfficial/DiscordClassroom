import pymongo
import asyncio
import config
import discord
from discord.ext import commands, tasks

import utils


class Notifications(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    def unload_cog(self):
        self.send_notifications.cancel()

    @commands.Cog.listener()
    async def on_ready(self):
        self.send_notifications.start()

    @tasks.loop(seconds=10)
    async def send_notifications(self):
        to_delete = []
        # loop through all recent notifications
        for notification in config.NOTIFICATIONS.find({}).sort('date', pymongo.DESCENDING):
            to_delete.append(notification)

            # get the user
            user = self.bot.get_user(notification['reciever'])
            if user is not None:

                # create embed to send to user
                embed = discord.Embed(title=notification['title'], description=notification['content'],
                                      color=config.MAINCOLOR)
                if notification['footer'] is not None:
                    embed.set_footer(text=notification['footer'])
                if notification['footer_icon'] is not None:
                    embed.set_footer(text=embed.footer.text, icon_url=notification['footer_icon'])

                # send embed and wait to not abuse API
                await user.send(embed=embed)
                await asyncio.sleep(1)

        # delete all notifications sent
        config.NOTIFICATIONS.delete_many({'_id': {'$in': list(x['_id'] for x in to_delete)}})



def setup(bot):
    bot.add_cog(Notifications(bot))
