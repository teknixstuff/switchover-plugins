import discord
from discord.ext import commands
from libover import plugin_perms
plugin_perms.guildID = guildID
from replit import db
import json

client = commands.Bot(command_prefix=['/log++:'], intents=discord.Intents().all())
name = 'log++'
if 'log++.logusers' not in db:
  db['log++.logusers'] = '[]'
logusers = json.loads(db['log++.logusers'])

@client.event
@plugin_perms.check_guild
async def on_message(ctx):
  if ctx.author == client.user:
    return
  for i in logusers:
    try:
      await i.send()
    except discord.errors.Forbidden:
      pass

@client.command(name='adduser')
@plugin_perms.check_guild
async def adduser(ctx, user):
