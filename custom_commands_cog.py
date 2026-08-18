import discord
from discord.ext import commands
import json
import os

class CustomCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.file_path = 'custom_commands.json'
        self.custom_commands = self.load_commands()

    def load_commands(self):
        if not os.path.exists(self.file_path):
            return {}
        try:
            with open(self.file_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}

    def save_commands(self):
        with open(self.file_path, 'w') as f:
            json.dump(self.custom_commands, f, indent=4)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        # Get context to parse prefix and check for existing commands
        ctx = await self.bot.get_context(message)
        
        # If it's already a valid command registered with the bot, ignore it
        if ctx.command:
            return

        # If no prefix found, ignore
        if not ctx.prefix:
            return

        # Extract potential command name
        # message.content is "\cmdname args" -> remove prefix
        content_without_prefix = message.content[len(ctx.prefix):]
        parts = content_without_prefix.split(' ')
        command_name = parts[0]

        guild_id = str(message.guild.id) if message.guild else None
        
        if not guild_id:
            return

        # Check if this command exists in our custom list for this guild
        response = None
        if guild_id in self.custom_commands and command_name in self.custom_commands[guild_id]:
            response = self.custom_commands[guild_id][command_name]
        elif "global" in self.custom_commands and command_name in self.custom_commands["global"]:
            response = self.custom_commands["global"][command_name]
            
        if response:
            await ctx.send(response)

    @commands.command(name="addcmd")
    @commands.has_permissions(administrator=True)
    async def add_command(self, ctx, name: str, *, response: str):
        """
        Adds a custom command.
        Usage: \\addcmd <name> <response>
        """
        guild_id = str(ctx.guild.id)
        
        if guild_id not in self.custom_commands:
            self.custom_commands[guild_id] = {}
        
        if name in self.custom_commands[guild_id]:
            await ctx.send(f"Command **{name}** already exists. Use `\\delcmd {name}` to delete it first.")
            return
        
        # Check if it conflicts with a bot command
        if self.bot.get_command(name):
             await ctx.send(f"⚠️ **{name}** is already a built-in bot command. Please choose a different name.")
             return

        self.custom_commands[guild_id][name] = response
        self.save_commands()
        await ctx.send(f"✅ Custom command **{name}** added!")

    @commands.command(name="delcmd")
    @commands.has_permissions(administrator=True)
    async def delete_command(self, ctx, name: str):
        """
        Deletes a custom command.
        Usage: \\delcmd <name>
        """
        guild_id = str(ctx.guild.id)
        
        if guild_id in self.custom_commands and name in self.custom_commands[guild_id]:
            del self.custom_commands[guild_id][name]
            self.save_commands()
            await ctx.send(f"🗑️ Custom command **{name}** deleted.")
        else:
            await ctx.send(f"❌ Command **{name}** not found.")

    @commands.command(name="reloadcmds")
    @commands.has_permissions(administrator=True)
    async def reload_commands(self, ctx):
        """
        Reloads custom commands from the JSON file.
        Usage: \\reloadcmds
        """
        self.custom_commands = self.load_commands()
        await ctx.send("✅ Custom commands reloaded from file.")

    @commands.command(name="listcmds")
    @commands.has_permissions(manage_messages=True)
    async def list_commands(self, ctx):
        """
        Lists all custom commands for this server.
        Usage: \listcmds
        """
        guild_id = str(ctx.guild.id)
        
        cmds = []
        if guild_id in self.custom_commands:
            cmds.extend(self.custom_commands[guild_id].keys())
        
        if "global" in self.custom_commands:
            cmds.extend([f"{cmd} (Global)" for cmd in self.custom_commands["global"].keys()])
            
        if cmds:
            embed = discord.Embed(title="Custom Commands", description=", ".join(cmds), color=discord.Color.gold())
            await ctx.send(embed=embed)
        else:
            await ctx.send("No custom commands configured for this server.")

async def setup(bot):
    await bot.add_cog(CustomCommands(bot))

