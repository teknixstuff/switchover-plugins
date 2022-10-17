import discord
from discord.ext import commands
from libover import plugin_perms
plugin_perms.guildID = guildID
from replit import db
import json
import datetime

client = commands.Bot(command_prefix=['/log++:'], intents=discord.Intents().all())
name = 'log++'
if 'log++.logusers' not in db:
  db['log++.logusers'] = '[]'
logusers = [await client.fetch_user(i) for i in json.loads(db['log++.logusers'])]

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
  logusers.append(await client.fetch_user())
  db['log++.logusers'] = json.dumps([i.id for i in logusers])
  
