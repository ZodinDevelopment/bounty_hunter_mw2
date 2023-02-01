from typing import Optional, Literal

from hashlib import sha256
from datetime import datetime, timedelta

from sqlalchemy import BigInteger, Column, Integer, Boolean, DateTime, Date, ForeignKey, Table, String, Float
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, validates
from discord import Member, User, Message



Base = declarative_base()


class BotUser(Base):
    """
    A Database Model class to represent registered users of the bot.
    id is the Unique ID of the discord Member object.
    """
    __tablename__ = "bot_user"
    id = Column(BigInteger, primary_key=True, autoincrement=False)
    guild_id = Column(BigInteger, index=True)
    twitter_name = Column(String(32), index=True, unique=True)
    activision_id = Column(String(128), index=True, unique=True)
    passkey_hash = Column(String(128))
    joined_on = Column(DateTime)
    trust_rating = Column(Float, default=0.0)
    notoriety = Column(Float, default=0.0)

    def __init__(
        self,
        *,
        discord_member: Member,
        activision_id: str,
        passkey: int,
        twitter_name: Optional[str]
    ):
        self.id = discord_member.id
        self.guild_id = discord_member.guild.id
        self.activision_id = activision_id
        self.passkey_hash = sha256(str(passkey).encode('utf-8')).hexdigest()
        self.twitter_name = twitter_name
        self.joined_on = datetime.utcnow()



class Report(Base):
    """ The id and primary key for this table should be a big integer [id of the message that made the report]"""
    __tablename__ = "report"
    id = Column(BigInteger, primary_key=True, autoincrement=False)
    suspect_activision = Column(String(32), index=True)
    platform = Column(String(32), index=True, default="Unknown")
    timestamp = Column(DateTime, index=True)

    message = Column(String(144), default="")
    admin_notes = Column(String(256), default="")

    proof_link = Column(String(128))
    guild_id = Column(BigInteger, index=True)
    
    bot_user_id = Column(ForeignKey("bot_user.id"))
    bot_user = relationship("BotUser", back_populates="reports")
    
    def __init__(
        self,
        *,
        context_message: Message,
        bot_user: BotUser,
        suspect_activision: str,
        platform: Optional[Literal["Playstation", "Xbox", "Battle.net", "Unknown"]],
        message: Optional[str],
        proof_link: Optional[str]
    ):
        self.id = context_message.id
        self.guild_id = bot_user.guild_id
        self.bot_user = bot_user
        self.suspect_activision = suspect_activision
        self.platform = platform
        self.message = message
        self.proof_link = proof_link

o    

engine = create_async_engine("sqlite+aiosqlite:///data.db")
AioSession = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def init_db():
    """ create the tables and columns if they don'st exist
    """
    async with engine.begin() as conn:
        #wait conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()


if __name__ == "__main__":
    import asyncio
    asyncio.run(init_db())

