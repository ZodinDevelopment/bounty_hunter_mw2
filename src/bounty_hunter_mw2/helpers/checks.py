import json
import os
from dotenv import load_dotenv
from typing import Callable, TypeVar

from discord.ext import commands

from exceptions import *
from helpers import db_manager



load_dotenv()
config_path = os.environ.get("BOT_CONFIG_PATH")
T = TypeVar("T")



def is_owner() -> Callable[[T], T]:
    """
    This is a custom check to see if the user executing the command an owner of the bot.
    """
    async def predicate(context: commands.Context) -> bool:
        with open(config_path, 'r') as file:
            data = json.load(file)

        if context.author.id not in data['owners']:
            raise UserNotOwner
        return True

    return commands.check(predicate)


def not_blacklisted() -> Callable[[T], T]:
    """
    This is a custom check to see if the user executing the command is blacklisted.
    """
    async def predicate(context: commands.Context) -> bool:
        if await db_manager.is_blacklisted(context.author.id):
            raise UserBlacklisted
        return True

    return commands.check(predicate)
