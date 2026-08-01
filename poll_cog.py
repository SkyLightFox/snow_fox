import discord
from discord.ext import commands

class Poll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.numbers = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]

    @commands.command(name="poll")
    @commands.has_permissions(manage_messages=True)
    async def poll(self, ctx, question: str, *options):
        """
        Creates a poll.
        Usage: 
        \poll "Question?" (Yes/No poll)
        \poll "Question?" "Option 1" "Option 2" (Multiple choice)
        """
        if len(options) == 0:
            # Yes/No Poll
            embed = discord.Embed(title="📊 Poll", description=question, color=discord.Color.blue())
            embed.set_footer(text=f"Poll created by {ctx.author.display_name}")
            message = await ctx.send(embed=embed)
            await message.add_reaction("👍")
            await message.add_reaction("👎")
        
        elif len(options) > 10:
            await ctx.send("You can only have up to 10 options!")
            return
            
        else:
            # Multiple Choice Poll
            description = []
            for i, option in enumerate(options):
                description.append(f"{self.numbers[i]} {option}")
            
            embed = discord.Embed(title=question, description="\n".join(description), color=discord.Color.blue())
            embed.set_footer(text=f"Poll created by {ctx.author.display_name}")
            
            message = await ctx.send(embed=embed)
            
            for i in range(len(options)):
                await message.add_reaction(self.numbers[i])

    @poll.error
    async def poll_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You don't have permission to create polls!")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Usage: \\poll "Question" [Option1] [Option2]...')

async def setup(bot):
    await bot.add_cog(Poll(bot))
