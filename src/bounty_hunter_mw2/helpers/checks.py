import json
import os
from dotenv import load_dotenv
from typing import Callable, TypeVar

from discord.ext import commands

from exceptions import *
from bounty_hunter_mw2.helpers import db_manager
from bounty_hunter_mw2.config import Config



#load_dotenv()
#config_path = os.environ.get("BOT_CONFIG_PATH")
T = TypeVar("T")
config = Config.todict()


def is_owner() -> Callable[[T], T]:
    """
    This is a custom check to see if the user executing the command an owner of the bot.
    """
    async def predicate(context: commands.Context) -> bool:
        
        if context.author.id not in config['owners']:
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
