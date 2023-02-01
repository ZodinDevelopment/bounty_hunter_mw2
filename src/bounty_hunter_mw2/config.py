import os
from dotenv import load_dotenv



load_dotenv()
class Config(object):
    PREFIX = os.environ.get("PREFIX")
    TOKEN = os.environ.get("BOT_TOKEN")
    PERMISSIONS = int(os.environ.get("PERMISSIONS_INTEGER"))
    APPLICATION_ID = int(os.environ.get("APPLICATION_ID"))
    OWNERS = [int(os.environ.get("OWNER"))]

    @staticmethod
    def to_dict():
        return {
            "prefix": self.PREFIX,
            "token": self.TOKEN,
            "permissions": self.PERMISSIONS,
            "application_id": self.APPLICATION_ID,
            "owners": self.OWNERS
        }
