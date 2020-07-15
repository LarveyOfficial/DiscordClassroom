import logging
import os

import pymongo
import asyncio
import config
import discord
from discord.ext import commands

import flask_discord
from flask import url_for, session, Flask, redirect, render_template, request, flash
import config
from flask_discord import DiscordOAuth2Session
import utils


class Website(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.app = Flask(__name__)
        self.app.config["DISCORD_CLIENT_ID"] = 732013656149196823  # Discord client ID.
        self.app.config["DISCORD_CLIENT_SECRET"] = "V8e9Kcl51YM4zPGKmAacO751ckrw5Ni3"  # Discord client secret.
        self.app.config["DISCORD_REDIRECT_URI"] = "https://discordclassroom.com/callback"  # Redirect URI.

        self.discordOA = DiscordOAuth2Session(self.app)
        self.app.secret_key = "super_hot_kangaroo_panda_ew"

    @commands.Cog.listener()
    async def on_ready(self):
        logging.info("Starting webserver on port 6969")
        port = int(os.environ.get('PORT', 6969))

        self.app.add_url_rule('/', 'home', view_func=self.home)

        self.app.run(host="0.0.0.0", port=port, debug=True)

    def home(self):
        return "Discord classroom website its so good thanks for visiting."




def setup(bot):
    bot.add_cog(Website(bot))
