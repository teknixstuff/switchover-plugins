#PLUGINCONFIG#
# name=Logger #
# ver=1.0.0   #
#/PLUGINCONFIG#

import discord
from discord.ext import commands
from libover import plugin_perms
plugin_perms.guildID = guildID
import json
import datetime
import re

client = commands.Bot(command_prefix=['/CWSM:','.?'], intents=discord.Intents().all())

@client.command(name='curseforgecwsm')
@plugin_perms.check_guild
async def adduser(ctx, user):
  ctx.reply('https://www.curseforge.com/minecraft/mc-mods/crackers-wither-storm-mod')