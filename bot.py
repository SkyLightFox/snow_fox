import discord
import os
import time
import datetime
import asyncio
import shutil
from dotenv import load_dotenv
from discord.ext import commands
import logging

logging.basicConfig(filename='bot.log', level=logging.DEBUG)

# Load environment variables
print("Loading bot...")
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Define intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Reaction Role Configuration
ROLE_MAP = {
    '🔴': 'Red Team',
    '🔵': 'Blue Team',
    '🟢': 'Green Team'
}
REACTION_MESSAGE_ID = None

class SnowFoxBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='\\', intents=intents)
        self.start_time = time.time()

    async def setup_hook(self):
        extensions = [
            'giveaway_cog', 'poll_cog', 'forms_cog', 'strikes_cog',
            'antispam_cog', 'custom_commands_cog', 'notes_cog',
            'modstats_cog', 'diagnose_cog', 'ranks_cog', 'embed_cog',
            'music_cog', 'twitch_cog', 'permissions_cog',
            'logging_cog', 'whitelist_cog'
        ]
        
        for ext in extensions:
            try:
                await self.load_extension(ext)
                print(f"{ext.replace('_cog', '').title()} cog loaded successfully.")
            except Exception as e:
                print(f"Failed to load {ext}: {e}")

# Create bot instance
bot = SnowFoxBot()

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    await bot.change_presence(activity=discord.Streaming(name="Discord: https://discord.gg/yJJCyHt", url="https://twitch.tv/skylightfox_"))

@bot.command(name='reaction_roles')
@commands.has_permissions(administrator=True)
async def reaction_roles(ctx):
    global REACTION_MESSAGE_ID
    
    description = "React to this message to get a role!\n\n"
    for emoji, role_name in ROLE_MAP.items():
        description += f"{emoji} : {role_name}\n"
        
    embed = discord.Embed(title="Role Menu", description=description, color=discord.Color.blue())
    message = await ctx.send(embed=embed)
    REACTION_MESSAGE_ID = message.id
    
    # Add initial reactions
    for emoji in ROLE_MAP.keys():
        await message.add_reaction(emoji)

@bot.event
async def on_raw_reaction_add(payload):
    if REACTION_MESSAGE_ID is None or payload.message_id != REACTION_MESSAGE_ID:
        return
        
    if payload.member.bot:
        return
        
    role_name = ROLE_MAP.get(str(payload.emoji))
    if role_name:
        guild = bot.get_guild(payload.guild_id)
        role = discord.utils.get(guild.roles, name=role_name)
        
        if role:
            await payload.member.add_roles(role)
            print(f"Added {role.name} to {payload.member.name}")
        else:
            print(f"Role {role_name} not found")

@bot.event
async def on_raw_reaction_remove(payload):
    if REACTION_MESSAGE_ID is None or payload.message_id != REACTION_MESSAGE_ID:
        return
        
    role_name = ROLE_MAP.get(str(payload.emoji))
    if role_name:
        guild = bot.get_guild(payload.guild_id)
        role = discord.utils.get(guild.roles, name=role_name)
        
        if role:
            member = guild.get_member(payload.user_id)
            if member:
                await member.remove_roles(role)
                print(f"Removed {role.name} from {member.name}")

@bot.command(name='ping')
async def ping(ctx):
    await ctx.send('Pong!')

@bot.command(name='kick')
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f'User {member} has been kicked')

@bot.command(name='ban')
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f'User {member} has been banned')

@bot.command(name='timeout')
@commands.has_permissions(moderate_members=True)
async def timeout(ctx, member: discord.Member, minutes: int, *, reason=None):
    """
    Timeouts a member for a specified number of minutes.
    Usage: \\timeout @User 10 Bad behavior
    """
    duration = datetime.timedelta(minutes=minutes)
    await member.timeout(duration, reason=reason)
    await ctx.send(f'{member} has been timed out for {minutes} minutes. Reason: {reason}')

@bot.command(name='unban')
@commands.has_permissions(ban_members=True)
async def unban(ctx, *, member_str):
    """
    Unbans a user.
    Usage: \\unban User#1234 or \\unban UserID
    """
    banned_users = [entry async for entry in ctx.guild.bans()]
    
    for ban_entry in banned_users:
        user = ban_entry.user
        
        if (str(user) == member_str) or (str(user.id) == member_str):
            await ctx.guild.unban(user)
            await ctx.send(f'Unbanned {user.mention}')
            return
            
    await ctx.send(f'User {member_str} not found in ban list.')

@bot.command(name='lock')
@commands.has_permissions(manage_channels=True)
async def lock(ctx):
    """
    Locks the current channel so members cannot send messages.
    """
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
    await ctx.send('Channel locked.')

@bot.command(name='unlock')
@commands.has_permissions(manage_channels=True)
async def unlock(ctx):
    """
    Unlocks the current channel.
    """
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
    await ctx.send('Channel unlocked.')

@bot.command(name='clear', aliases=['purge'])
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount=5):
    await ctx.channel.purge(limit=amount + 1)

@bot.command(name='setstatus')
@commands.has_permissions(administrator=True)
async def setstatus(ctx, status_type: str, *, status_text: str):
    """
    Sets the bot's status.
    Usage: \\setstatus <playing|watching|listening|streaming> <text>
    Example: \\setstatus playing Minecraft
    """
    status_type = status_type.lower()
    
    if status_type == 'playing':
        activity = discord.Game(name=status_text)
    elif status_type == 'watching':
        activity = discord.Activity(type=discord.ActivityType.watching, name=status_text)
    elif status_type == 'listening':
        activity = discord.Activity(type=discord.ActivityType.listening, name=status_text)
    elif status_type == 'streaming':
        # Check if a custom URL is provided in the text (separated by |)
        if '|' in status_text:
            name, url = status_text.split('|', 1)
            activity = discord.Streaming(name=name.strip(), url=url.strip())
        else:
            activity = discord.Streaming(name=status_text, url="https://twitch.tv/skylightfox_")
    else:
        await ctx.send("Invalid status type! Use 'playing', 'watching', 'listening', or 'streaming'.")
        return

    await bot.change_presence(activity=activity)
    await ctx.send(f"Status changed to: {status_type.capitalize()} {status_text}")

@kick.error
@ban.error
@clear.error
@timeout.error
@unban.error
@lock.error
@unlock.error
async def admin_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have permission to do that!")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.lower() == 'hello':
        await message.channel.send('Hello there!')

    await bot.process_commands(message)

@bot.command(name='github')
async def github(ctx):
    """
    Sends the link to the bot's GitHub repository.
    Usage: \\github
    """
    await ctx.send("Check out the project on GitHub: https://github.com/SkyLightFox")

@bot.command(name='discordlink')
async def discordlink(ctx):
    """
    Sends the link to the bot's Discord server.
    Usage: \\discord
    """
    await ctx.send("Join us on Discord: https://discord.gg/yJJCyHt")

@bot.command(name='websites', aliases=['links'])
async def websites(ctx):
    """
    Sends an embed with useful links for the bot and community.
    Usage: \\websites
    """
    embed = discord.Embed(title="Useful Links", color=discord.Color.blue())
    embed.add_field(name="SkyLightFox's Discord Server", value="https://discord.gg/yJJCyHt", inline=False)


    await ctx.send(embed=embed)

if __name__ == "__main__":
    if shutil.which("ffmpeg") is None:
        print("Warning: ffmpeg not found in PATH. Music features might not work.")
    
    print("Starting bot...")
    bot.run(TOKEN)

