from discord.ext import Commands



class UserBlackListed(commands.CheckFailure):
    """
    Thrown when a user is attempting something, but is blacklisted.
    """
    def __init__(self, message="User is blacklisted."):
        self.message = message
        super().__init__(self.message)



class UserNotOwner(commands.CheckFailure):
    """
    Thrown when a user is attempting something, but is not an owner of the bot.
    """
    def __init__(self, message="User is not owner of this bot."):
        self.message = message
        super().__init__(self.message)
