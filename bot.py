import discord
from discord.ext import commands
from discord.ui import Button, View
import re  # To handle scam link detection
from datetime import timedelta
import random  # For the coin flip command

# Define intents
intents = discord.Intents.default()
intents.message_content = True  # Enable reading message content
intents.moderation = True  # Enable moderation intents

# Create the bot instance with a default prefix
default_prefix = '!'
bot = commands.Bot(command_prefix=default_prefix, intents=intents)

mod_channel_name = '🔑︱moderators'  # Default moderator channel name
welcome_channel_name = '👋︱welcome'  # Default welcome channel name
warnings = {}  # Store user warnings

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    print('Pro Heroes Association is now active!')
    
    with open('ProHeroesAssociation.png', 'rb') as avatar:
        await bot.user.edit(username="Pro Heroes Association", avatar=avatar.read())

    # Set bot presence
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="for villains"))

@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name=welcome_channel_name)
    if channel:
        await channel.send(f'Welcome to the server, {member.mention}! The World Heroes Association salutes you!')

@bot.remove_command('help')  # Remove the default help command

@bot.command()
async def help(ctx):
    """Send the user a direct message with a list of commands."""
    help_text = (
        "**Pro Heroes Association Commands:**\n"
        "`!hello` - Greet the bot.\n"
        "`!flip` - Flip a coin.\n"
        "`!unban <member_name>` - Unban a user by name.\n"
        "`!mute <member> <duration>` - Temporarily mute a user for a set duration (in minutes).\n"
        "`!unmute <member>` - Unmute a user.\n"
        "`!deafen <member>` - Deafen a user in voice chat.\n"
        "`!undeafen <member>` - Undeafen a user in voice chat.\n"
        "`!warn <member> <reason>` - Warn a user.\n"
        "`!delwarn <member> <index>` - Delete a specific warning for a user.\n"
        "`!softban <member> <reason>` - Softban a user (ban and immediately unban).\n"
        "`!set_mod_channel <channel_name>` - Set the moderator channel.\n"
        "`!set_welcome_channel <channel_name>` - Set the welcome channel.\n"
        "`!purge <amount>` - Delete a number of messages in the current channel.\n"
        "`!clean` - Delete all messages sent by the bot in the current channel.\n"
        "`!set_prefix <prefix>` - Change the bot's activation prefix."
    )
    try:
        await ctx.author.send(help_text)
        await ctx.send("I've sent you a DM with a list of commands!")
    except discord.Forbidden:
        await ctx.send("I couldn't send you a DM. Please check your privacy settings.")

@bot.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, *, member_name):
    banned_users = await ctx.guild.bans()
    for ban_entry in banned_users:
        user = ban_entry.user
        if user.name == member_name:
            await ctx.guild.unban(user)
            await ctx.send(f'{user.mention} has been unbanned.')
            return
    await ctx.send(f'No banned user found with the name {member_name}.')

@bot.command()
@commands.has_permissions(moderate_members=True)
async def mute(ctx, member: discord.Member, duration: int, *, reason=None):
    until = discord.utils.utcnow() + timedelta(minutes=duration)
    try:
        await member.timeout(until, reason=reason)
        await ctx.send(f'{member.mention} has been muted for {duration} minutes. Reason: {reason}')
    except Exception as e:
        await ctx.send(f'Failed to mute {member.mention}. Error: {e}')

@bot.command()
@commands.has_permissions(moderate_members=True)
async def unmute(ctx, member: discord.Member):
    try:
        await member.timeout(None)
        await ctx.send(f'{member.mention} has been unmuted.')
    except Exception as e:
        await ctx.send(f'Failed to unmute {member.mention}. Error: {e}')

@bot.command()
@commands.has_permissions(mute_members=True)
async def deafen(ctx, member: discord.Member, *, reason=None):
    try:
        await member.edit(deafen=True, reason=reason)
        await ctx.send(f'{member.mention} has been deafened. Reason: {reason}')
    except Exception as e:
        await ctx.send(f'Failed to deafen {member.mention}. Error: {e}')

@bot.command()
@commands.has_permissions(mute_members=True)
async def undeafen(ctx, member: discord.Member):
    try:
        await member.edit(deafen=False)
        await ctx.send(f'{member.mention} has been undeafened.')
    except Exception as e:
        await ctx.send(f'Failed to undeafen {member.mention}. Error: {e}')

@bot.command()
@commands.has_permissions(manage_messages=True)
async def warn(ctx, member: discord.Member, *, reason=None):
    if member.id not in warnings:
        warnings[member.id] = []
    warnings[member.id].append(reason)
    await ctx.send(f'{member.mention} has been warned. Reason: {reason}')

@bot.command()
@commands.has_permissions(manage_messages=True)
async def delwarn(ctx, member: discord.Member, index: int):
    if member.id in warnings and 0 <= index < len(warnings[member.id]):
        removed_warning = warnings[member.id].pop(index)
        await ctx.send(f'Removed warning from {member.mention}: {removed_warning}')
    else:
        await ctx.send(f'Invalid warning index for {member.mention}.')

@bot.command()
@commands.has_permissions(ban_members=True)
async def softban(ctx, member: discord.Member, *, reason=None):
    try:
        await member.ban(reason=reason)
        await ctx.guild.unban(member)
        await ctx.send(f'{member.mention} has been softbanned. Reason: {reason}')
    except Exception as e:
        await ctx.send(f'Failed to softban {member.mention}. Error: {e}')

@bot.command()
async def hello(ctx):
    await ctx.send(f'Hello {ctx.author.mention}! Welcome to PLUS ULTRA!')

@bot.command()
async def flip(ctx):
    """Flip a coin and return Heads or Tails."""
    result = random.choice(["Heads", "Tails"])
    await ctx.send(f'The coin landed on: {result}')

@bot.command()
@commands.has_permissions(manage_channels=True)
async def set_mod_channel(ctx, channel_name: str):
    global mod_channel_name
    mod_channel_name = channel_name
    await ctx.send(f'The moderator channel has been updated to: {channel_name}')

@bot.command()
@commands.has_permissions(manage_channels=True)
async def set_welcome_channel(ctx, channel_name: str):
    global welcome_channel_name
    welcome_channel_name = channel_name
    await ctx.send(f'The welcome channel has been updated to: {channel_name}')

@bot.command()
@commands.has_permissions(manage_messages=True)
async def purge(ctx, amount: int):
    try:
        deleted = await ctx.channel.purge(limit=amount)
        await ctx.send(f'Deleted {len(deleted)} messages.', delete_after=5)
    except Exception as e:
        await ctx.send(f'Failed to purge messages. Error: {e}', delete_after=5)

@bot.command()
@commands.has_permissions(manage_messages=True)
async def clean(ctx):
    """Delete all messages sent by the bot in the current channel."""
    def is_bot_message(message):
        return message.author == bot.user

    try:
        deleted = await ctx.channel.purge(limit=100, check=is_bot_message)
        await ctx.send(f'Removed {len(deleted)} bot messages.', delete_after=5)
    except Exception as e:
        await ctx.send(f'Failed to clean bot messages. Error: {e}', delete_after=5)

@bot.command()
@commands.has_permissions(manage_channels=True)
async def set_prefix(ctx, prefix: str):
    """Change the bot's activation prefix."""
    bot.command_prefix = prefix
    await ctx.send(f'The command prefix has been updated to: `{prefix}`')

TOKEN = [BOT TOKEN]
bot.run(TOKEN)
