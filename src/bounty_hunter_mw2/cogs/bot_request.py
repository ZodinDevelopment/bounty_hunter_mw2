import platform
import aiohttp
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context

from helpers import checks


class HttpRequest(commands.Cog, name="general"):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="bitcoin",
        description="Get the current price of bitcoin."
    )
    @checks.not_blacklisted()
    async def bitcoin(self, context: Context) -> None:
        """
        Get the current price of bitcoin. THis is just to demonstrate asynchronous HTTP requests.

        :param context: The command context
        """
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.coindesk.com/v1/bpi/currentprice/BTC.json") as request:
                if request.status == 200:
                    data = await request.json(content_type="application/javascript")
                    embed = discord.Embed(
                        title="Bitcoin Price",
                        description=f"The current price is {data['bpi']['USD']['rate']} :dollar:",
                        color=0x9C84EF
                    )
                else:
                    embed = discord.Embed(
                        title="Error!",
                        description="There's an error with the API, please try again later.",
                        color=0xE02B2B
                    )
                await context.send(embed=embed)

