from discord.ext import Commands
from discord.ext.commands import Context

from bounty_hunter_mw2.helpers import checks

class Template(commands.Cog, name="template"):
    def __init__(self, bot):
        self.bot = bot 

    @commands.hybrid_command(
        name="testcommand",
        description="This is a testing command that does nothing.",
    )
    @checks.not_blacklisted()
    @checks.is_owner()
    async def testcommand(self, context: Context):
        """
        This is a testing command that does nothing.

        :param context: The application command context.
        """
        pass



async def setup(bot):
    await bot.add_cog(Template(bot))
