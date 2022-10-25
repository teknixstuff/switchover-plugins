#PLUGINCONFIG#
# name=Logger #
# ver=1.0.0   #
#/PLUGINCONFIG#

import discord
from discord.ext import commands
from libover import plugin_perms, Database
db = Database(os.environ['CONFIG_DB_URL'])
plugin_perms.guildID = guildID
import json
import datetime
import re

client = commands.Bot(command_prefix=['/logger;'], intents=discord.Intents().all())
if 'logger.logusers' not in db:
  db['logger.logusers'] = '[]'
logusers = []

@client.event
async def on_ready():
  logusers = [await client.fetch_user(i) for i in json.loads(db['logger.logusers'])]

@client.event
@plugin_perms.check_guild
async def on_message(ctx):
  if ctx.author == client.user:
    return
  for i in logusers:
    try:
      embed = discord.Embed(title=f'Message Created in {ctx.guild.name}:{ctx.channel.name}', description=message.content, timestamp=datetime.now())
      embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
      await i.send(embeds=[embed])
    except discord.errors.Forbidden:
      pass

@client.command(name='adduser')
@plugin_perms.check_guild
async def adduser(ctx, user):
  logusers.append(await client.fetch_user(re.match(r'<@([0-9]*)>', user).group(1)))
  db['log-plus-plus.logusers'] = json.dumps([i.id for i in logusers])
  ctx.reply(','.join([i.name for i in logusers]))
