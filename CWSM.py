#PLUGINCONFIG#
# name=CWSM  #
# ver=1.0.0  #
#/PLUGINCONFIG#

import discord
from discord.ext import commands
from libover import plugin_perms
plugin_perms.guildID = guildID

client = commands.Bot(command_prefix=['/CWSM:','.?'], intents=discord.Intents().all())

@client.command(name='curseforgecwsm')
@plugin_perms.check_guild
async def curseforgecwsm(ctx, user):
  ctx.reply('https://www.curseforge.com/minecraft/mc-mods/crackers-wither-storm-mod')