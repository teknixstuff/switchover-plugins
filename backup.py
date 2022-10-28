import keepalive
import clientsettings
import asyncio
import time
import os
import sys
import json
import requests
import discord
import libcord
import logging
import random
import datetime
import socket
from multiprocessing import Process
import importlib
from types import ModuleType
from pyext import RuntimeModule
from replit import db
from discord.ext import commands
import importlib.util
import re

plugin_meta_regex = re.compile(r'^\s*#PLUGINCONFIG#\n(#\s*[^=\n]*\s*=\s*[^\n]*\s*#\n*)#\/PLUGINCONFIG#')
plugin_meta_key_val_regex = re.compile(r'(?:#\s*([^=\n]*)\s*=\s*([^\n]*)\s*#\n)')

if 'plugins' not in db:
		db['plugins'] = {}

#plugins = json.loads(db['plugins'])

client = commands.Bot(command_prefix=['.back', '/backover:'],
											intents=discord.Intents().all())
cord = libcord.Cord(client)
logger = logging.getLogger('bot')

plugprocs = {}

@client.event
async def on_ready():
		print('We have logged in as {0.user}'.format(client))
		await client.change_presence(
				activity=discord.Game('.?help | The all-in-one bot'))
		print(f'Loading plugins: {str(db["plugins"].value)}')
		for name, p in db['plugins'].items():
				name, proc = KLoadPluginFromURL(p['URL'], p['guildID'], *p['args'], **p['kwargs'])
				plugprocs[name] = proc


#class EmbedHelp(commands.HelpCommand):
#		async def send_pages(self):
#				destination = self.get_destination()
#				for page in self.paginator.pages:
#						emby = discord.Embed(description=page)
#						await destination.send(embed=emby)
#
#
#client.help_command = EmbedHelp

@client.command(name="khelp")
@libcord.parse_args
async def khelp(ctx):
		embed = discord.Embed(title="Internal Help", color=0xFF0000)
		embed.add_field(name='KGetPlugins', value='Get the plugin object', inline=False)
		embed.add_field(name='KLoadPluginFromURL', value='Load a plugin from a URL. This will NOT update the plugin object.', inline=False)
		embed.add_field(name='KInfo', value='Get debug info about the bot', inline=False)
		await ctx.reply(embed=embed)
	#but about the bot? Like what it uses (e.g python) ah okay ill make that ill fix the error

client.help_command = None
@client.command(name='help')
@libcord.parse_args
async def help(ctx):
		embed = discord.Embed(title="Help", color=0xFF0000)
		embed.add_field(name='timeout <@user> <seconds>',
 										value='Timeout a user',
										inline=False)
		embed.add_field(name='kick <@user>', value='Kick a user', inline=True)
		embed.add_field(name='ban <@user>', value='Ban a user', inline=True)
		embed.add_field(name='warn <@user>', value='Warn a user', inline=True)
		embed.add_field(name='purge <messages>', value='Delete the most recent <messages> messages', inline=False)
		embed.add_field(name='LoadPluginFromURL <URL> [arg1, arg2, ..., argN]', value='Load a plugin from a URL', inline=False)
		embed.add_field(name='RemovePlugin <name>', value='Removes a plugin', inline=True)
		embed.set_footer(text='use khelp to see internal commands\nMade by Tech Stuff#2849 and ItzMeow#9322')
		await ctx.reply(embed=embed)

@client.command(name='KInfo')
@libcord.parse_args
async def KInfo(ctx):
		embed = discord.Embed(title="Help", color=0xFF0000)
		embed.add_field(name='Libraries', value='Discord.py\nlibcord\nrequests\nmultiprocessing\nreplit.db', inline=True)
		embed.add_field(name='IP', value=str(socket.gethostbyname(socket.gethostname())), inline=True)
		embed.add_field(name='Hostname', value=str(socket.gethostname()), inline=True)
		await ctx.reply(embed=embed)

# @client.command(name='LoadPluginFromFile')
# @commands.has_permissions(manage_guild=True)
# @libcord.parse_args
# async def LoadPluginFromFile(ctx, name, *args, **kwargs):
#		 plugin = importlib.import_module(f'plugins.{name}')
#		 plugin.args = args
#		 plugin.kwargs = kwargs
#		 proc = Process(target=plugin.client.run, args=[os.environ['TOKEN']])
#		 proc.start()
#		 await ctx.reply('Okay')


@client.command(name='LoadPluginFromURL')
@commands.has_permissions(manage_guild=True)
@libcord.parse_args
async def LoadPluginFromURL(ctx, url, *args, **kwargs):
		name, proc = KLoadPluginFromURL(url, ctx.guild.id, *args, **kwargs)
		if name in plugprocs:
			plugprocs[name].terminate()
		plugprocs[name] = proc
		db['plugins'][f'{name}_{ctx.guild.id}'] = {
				'URL': url,
				'guildID': ctx.guild.id,
				'args': args,
				'kwargs': kwargs,
				'name': name
		}
		#db['plugins'] = json.dumps(plugins)
		await ctx.reply(f'Loaded {name} from {url}.')


@client.command(name='RemovePlugin')
@commands.has_permissions(manage_guild=True)
@libcord.parse_args
async def RemovePlugin(ctx, name):
		del db['plugins'][f'{name}_{ctx.guild.id}']
		#db['plugins'] = json.dumps(plugins)
		await ctx.reply(f'Removed {name}')


@client.command(name='KGetPlugins')
@commands.has_permissions(manage_guild=True)
@libcord.parse_args
async def KGetPlugins(ctx):
		await ctx.reply(str(db['plugins']))

@client.command(name='GetPlugins')
@commands.has_permissions(manage_guild=True)
@libcord.parse_args
async def GetPlugins(ctx):
		await ctx.reply(str(['plugins']))

@client.command(name='KLoadPluginFromURL')
@commands.has_permissions(manage_guild=True)
async def KLoadPluginFromURL_wrapper(ctx, *args, **kwargs):
		await ctx.reply(str(KLoadPluginFromURL(*args, **kwargs)))

def KLoadPluginFromURL(url, guildID, *args, **kwargs):
		r = requests.get(url)
		plugin_meta_meta = plugin_meta_regex.match(r.text)
		if plugin_meta_meta is None:
			raise Exception('Bad plugin meta')
		plugin_meta = dict([(i.group(1), i.group(2)) for i in plugin_meta_key_val_regex.finditer(plugin_meta_meta.group(1))])
		def mainloader():
			spec = importlib.util.spec_from_loader('plugin', loader=None)
			plugin = importlib.util.module_from_spec(spec)
			plugin.guildID = guildID
			plugin.db = db
			plugin.args = args
			plugin.kwargs = kwargs
			exec(r.text, plugin.__dict__)
			plugin.client.run(os.environ['TOKEN'])
		proc = Process(target=mainloader)
		proc.start()
		return (plugin_meta['name'], proc)


@client.command(name='ban')
@commands.has_permissions(ban_members=True)
@libcord.parse_args
async def ban(ctx, user, reason=None):
		user = await cord.mention2user(user)
		await user.send('You were banned from {0.guild.name} for {1}'.format(
				ctx, reason))
		await ctx.guild.ban(user, reason=reason)
		embed = discord.Embed(title="Banned {0.name}".format(user), color=0xFF0000)
		await ctx.reply(embed=embed)


@client.command(name='kick')
@commands.has_permissions(kick_members=True)
@libcord.parse_args
async def kick(ctx, user, reason=None):
		user = await cord.mention2user(user)
		await user.send('You were kicked from {0.guild.name} for {1}'.format(
				ctx, reason))
		await ctx.guild.kick(user, reason=reason)
		embed = discord.Embed(title="Kicked {0.name}".format(user), color=0xFF0000)
		await ctx.reply(embed=embed)


@client.command(name="rnduser")
@libcord.parse_args
async def rnduser(ctx, rolename):
		role = discord.utils.get(ctx.guild.roles, name=rolename)
		await ctx.reply(
				random.choice(
						list(filter(lambda member: role in member.roles,
												ctx.guild.members))))


@client.command(name="timeout")
@commands.has_permissions(kick_members=True)
@libcord.parse_args
async def timeout(ctx, usermention, seconds):
		user = libcord.mention2id(usermention)
		headers = {"Authorization": f"Bot {client.http.token}"}
		url = f"https://discord.com/api/v9/guilds/{ctx.guild.id}/members/{user}"
		timeout = (datetime.datetime.utcnow() +
							 datetime.timedelta(seconds=int(seconds))).isoformat()
		json = {'communication_disabled_until': timeout}
		session = requests.patch(url, json=json, headers=headers)
		print(session.status_code)
		print(session.content)

@client.command(name='warn')
@commands.has_permissions(kick_members=True)
@libcord.parse_args
async def warn(ctx, user, reason=None):
		user = await cord.mention2user(user)
		await user.send('You were kicked from {0.guild.name} for {1}'.format(
				ctx, reason))
		embed = discord.Embed(title="Warned {0.name}".format(user), color=0xFF0000)
		await ctx.reply(embed=embed)


@client.command(name="purge")
@commands.has_permissions(manage_messages=True)
async def clean(ctx, limit: int):
		await ctx.channel.purge(limit=limit + 1)
		await ctx.send('Cleared by {}'.format(ctx.author.mention))
		await ctx.message.delete()


@clean.error
async def clear_error(ctx, error):
		if isinstance(error, commands.MissingPermissions):
				await ctx.send("You cant do that!")


@client.event
async def on_message(message):
		await client.process_commands(message)


async def main():
		while True:
				try:
						await client.login(os.environ['TOKEN'])
						break
				except (discord.errors.HTTPException, discord.ConnectionClosed):
						print('Login error, restarting pid 1')
						os.system('kill 1')
						time.sleep(9223372036854775807)

		try:
				await client.connect(reconnect=False)
		except (discord.errors.HTTPException, discord.ConnectionClosed):
				print('Connection error, restarting pid 1')
				os.system('kill 1')
				time.sleep(9223372036854775807)


asyncio.run(main())
