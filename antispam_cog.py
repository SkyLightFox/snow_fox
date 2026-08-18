import discord
from discord.ext import commands
import datetime
from collections import defaultdict, deque

class AntiSpam(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Store last N messages for each user: {user_id: deque([(timestamp, content), ...])}
        self.user_messages = defaultdict(lambda: deque(maxlen=10))
        self.spam_config = {
            "max_messages": 5,       # Max messages in time_window
            "time_window": 5,        # Seconds
            "max_duplicates": 3,     # Max identical messages in time_window
            "enabled": True,
            "exempt_roles": [],      # Role IDs that are exempt
            "ignored_channels": []   # Channel IDs to ignore
        }

    def is_exempt(self, member):
        if member.guild_permissions.administrator:
            return True
        for role in member.roles:
            if role.id in self.spam_config["exempt_roles"]:
                return True
        return False

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.guild or message.author.bot or not self.spam_config["enabled"]:
            return

        if message.channel.id in self.spam_config["ignored_channels"]:
            return

        if isinstance(message.author, discord.Member) and self.is_exempt(message.author):
            return

        user_id = message.author.id
        now = datetime.datetime.now()
        
        # Add current message to history
        self.user_messages[user_id].append((now, message.content))
        
        # Check for spam
        history = self.user_messages[user_id]
        
        # 1. Rate Limit Check
        # Count messages in the last `time_window` seconds
        recent_messages = [msg for t, msg in history if (now - t).total_seconds() <= self.spam_config["time_window"]]
        
        if len(recent_messages) >= self.spam_config["max_messages"]:
            await self.handle_spam(message, "Sending messages too quickly")
            return

        # 2. Duplicate Check
        # Count identical messages in the recent window
        duplicates = [msg for t, msg in history if msg == message.content and (now - t).total_seconds() <= self.spam_config["time_window"]]
        
        if len(duplicates) >= self.spam_config["max_duplicates"]:
            await self.handle_spam(message, "Sending duplicate messages")
            return

    async def handle_spam(self, message, reason):
        # Delete the latest message (and potentially others if we wanted to be aggressive)
        try:
            await message.delete()
            
            # Send a warning (temp message)
            warning = await message.channel.send(f"⚠️ {message.author.mention}, please stop spamming! ({reason})")
            await warning.delete(delay=5)
            
            # Clear history to prevent infinite loop of deletions/warnings if they stop immediately
            # self.user_messages[message.author.id].clear()
            
            # Optionally: Apply a strike if the Strikes cog exists
            strikes_cog = self.bot.get_cog('Strikes')
            if strikes_cog:
                # We need to construct a context-like object or refactor Strikes cog.
                # For now, let's just log it or maybe timeout if possible.
                pass

        except discord.Forbidden:
            print(f"Missing permissions to delete spam in {message.channel.name}")
        except discord.NotFound:
            pass # Message already deleted

    @commands.group(name="antispam", invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def antispam(self, ctx):
        """
        Anti-spam settings.
        Usage: \antispam status
        """
        status = "Enabled" if self.spam_config["enabled"] else "Disabled"
        embed = discord.Embed(title="🛡️ Anti-Spam Configuration", color=discord.Color.blue())
        embed.add_field(name="Status", value=status, inline=False)
        embed.add_field(name="Max Messages", value=f"{self.spam_config['max_messages']} in {self.spam_config['time_window']}s", inline=True)
        embed.add_field(name="Max Duplicates", value=f"{self.spam_config['max_duplicates']} in {self.spam_config['time_window']}s", inline=True)
        await ctx.send(embed=embed)

    @antispam.command(name="toggle")
    @commands.has_permissions(administrator=True)
    async def toggle_antispam(self, ctx):
        """
        Toggles anti-spam on or off.
        Usage: \antispam toggle
        """
        self.spam_config["enabled"] = not self.spam_config["enabled"]
        status = "enabled" if self.spam_config["enabled"] else "disabled"
        await ctx.send(f"Anti-spam is now **{status}**.")

    @antispam.command(name="limit")
    @commands.has_permissions(administrator=True)
    async def set_limit(self, ctx, count: int, seconds: int):
        """
        Sets the max message rate.
        Usage: \antispam limit 5 5 (5 messages in 5 seconds)
        """
        self.spam_config["max_messages"] = count
        self.spam_config["time_window"] = seconds
        await ctx.send(f"Anti-spam limit set to **{count} messages** in **{seconds} seconds**.")

async def setup(bot):
    await bot.add_cog(AntiSpam(bot))
