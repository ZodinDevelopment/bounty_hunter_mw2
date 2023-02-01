import asyncio
import json
import logging
import os
import platform
import random
import sys


import discord
from discord.ext import commands, tasks
from discord.ext.commands import Bot, Context

import bounty_hunter_mw2.exceptions
from bounty_hunter_mw2.models import Base, BotUser, Report, engine, AioSession, init_db



cog_path = f"{os.path.realpath(os.path.dirname(__file__))}/cogs"
config = Config.todict()

intents = discord.Intents.default()
intents.members = True
intents.message_content = True


bot = Bot(
    command_prefix=commands.when_mentioned_or(config['prefix']),
    intents=intents,
    help_command=None
)


class LoggingFormatter(logging.Formatter):
    black="\x1b[30m"
    red = "\x1b[31m"
    green = "\x1b[32m"
    yellow = "\x1b[33m"
    blue = "\x1b[34m"
    gray = "\x1b[38m"

    reset = "\x1b[0m"
    bold = "\x1b[1m"

    COLORS = {
        logging.DEBUG: gray + bold,
        logging.INFO: blue + bold,
        logging.WARNING: yellow + bold,
        logging.ERROR: red,
        logging.CRITICAL: red + bold
    }

    def format(self, record):
        log_color = self.COLORS[record.levelno]
        format = "(black){asctime}(reset) (levelcolor){levelname:<8}(reset) (green){name}(reset) {message}"
        format = format.replace("(black)", self.black + self.bold)
        format = format.replace("(reset)", self.reset)
        format = format.replace("(levelcolor)", log_color)
        format = format.replace("(green)", self.green + self.bold)
        formatter = logging.Formatter(format, "%Y-%m-%d %H:%M:%S", style="{")
        return formatter.format(record)


logger = logging.getLogger("discord_bot")
logger.setLevel(logging.INFO)


console_handler = logging.StreamHandler()
console_handler.setFormatter(LoggingFormatter())

file_handler = logging.FileHandler(
    filename="discord.log",
    encoding="utf-8",
    mode="w"
)
file_handler_formatter = logging.Formatter(
    "[{asctime}] [{levelname:<8}] {name}: {message}",
    "%Y-%m-%d %H:%M:%S",
    style="{"
)
file_handler.setFormatter(file_handler_formatter)


logger.addHandler(console_handler)
logger.addHandler(file_handler)
bot.logger = logger


async def setup_db():
    await init_db()


bot.config = config


@bot.event
async def on_ready() -> None:
    """
    The code in this event is called when the bot is ready.
    """
    bot.logger.info(f"Logged in as {bot.user.name}.")
    bot.logger.info(f"discord.py API version: {discord.__version__}")
    bot.logger.info(f"Python version: {platform.python_version()}")
    bot.logger.info(
        f"Running on: {platform.system()} {platform.release()} ({os.name})"
    )
    bot.logger.info("-------------")
    status_task.start()
    if config['sync_commands_globally']:
        bot.logger.info("Syncing commands globally.")
        await bot.tree.sync()


@tasks.loop(minutes=1.0)
async def status_task() -> None:
    """
    Setup the game status of the bot.
    """
    statuses = [
        "chillin",
        "camping",
        "grinding"
    ]
    await bot.change_presence(activity=discord.Game(random.choice(statuses)))


@bot.event
async def on_message(message: discord.Message) -> None:
    """
    Executed when a message is sent
    
    :param message: The message that was sent.
    """
    if message.author == bot.user or message.author.bot:
        return
    await bot.process_commands(message)


@bot.event
async def on_command_completion(context: Context) -> None:
    """
    Executed when a command is successfully executed.

    :param context: The context of the command.
    """
    full_command_name = context.command.qualified_name
    split = full_command_name.split(" ")
    executed_command = str(split[0])
    if context.guild is not None:
        bot.logger.info(
            f"Executed {executed_command} command in {context.guild.name} (ID: {context.guild.id}) by {context.author} (ID: {context.author.id})"
        )
    else:
        bot.logger.info(
            f"Executed {executed_command} command by {context.author} (ID: {context.author.id})"
        )


@bot.event
async def on_command_error(context: Context, error) -> None:
    """
    Executed when an error is caught on a command.

    :param context: The context of the command
    :param error: The error that was raised
    """
    if isinstance(error, commands.CommandOnCooldown):
        minutes, seconds = divmod(error.retry_after, 60)
        hours, minutes = dibmod(minutes, 60)
        hours = hours % 24
        embed = discord.Embed(
            description=f"**Please slow down** - You can use this command again in {f'{round(hours)} hours' if round(hours) > 0 else ''} {f'{round(minutes)} minutes' if round(minutes) > 0 else ''} {f'{round(seconds)} seconds' if round(seconds) > 0 else ''}",
            color=0xE02B2B
        )
        await context.send(embed=embed)
    
    elif isinstance(error, exceptions.UserBlacklisted):
        embed = discord.Embed(
            description="You are blacklisted from using the bot!",
            color=0xE02B2B
        )
        await context.send(embed=embed)
        bot.logger.warning(
            f"{context.author} (ID: {context.author.id}) tried to execute a command in guild {context.guild.name} (ID: {context.guild.id}), but the user is blacklisted."
        )

    elif isinstance(error, exceptions.UserNotOwner):
        embed = discord.Embed(
            description="You are not the owner of the bot!",
            color=0xE02B2B
        )
        await context.send(embed=embed)
        bot.logger.warning(
            f"{context.author} (ID: {context.author.id}) tried to execute an owner command in {context.guild.name} (ID: {context.guild.id})"
        )

    elif isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(
            description="You are missing the permission(s) `" + ", ".join(error.missing_permissions) + "` to execute this command.",
            color=0xE02B2B
        )
        await context.send(embed=embed)
        
    elif isinstance(error, commands.BotMissingPermissions):
        embed = discord.Embed(
            description="I am missing the permission(s) `" + ", ".join(error.missing_permissions) + "` to execute this command.",
            color=0xE02B2B
        )
        await context.send(embed=embed)

    elif isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(
            title="Error!",
            description=str(error).capitalize(),
            color=0xE02B2B
        )
        await context.send(embed=embed)

    else:
        raise error


async def load_cogs() -> None:
    """
    The code in this function is executed when the bot starts.
    """
    for file in os.listdir(cog_path):
        if file.endswith(".py"):
            extension = file[:-3]
            try:
                await bot.load_extension(f"cogs.{extension}")
                bot.logger.info(f"Loaded extension '{extension}'")
            except Exception as e:
                exception = f"{type(e).__name__}: {e}"
                bot.logger.error(f"Failed to load extension '{extension}'\n{exception}")



def start():
    asyncio.run(load_cogs())
    bot.run(config['token'])

