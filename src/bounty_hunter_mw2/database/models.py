from typing import Optional, Union

from hashlib import sha256
from datetime import datetime, timedelta

from sqlalchemy import BigInteger, Column, Integer, Boolean, DateTime, Date, ForeignKey, Table, String, Float
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from discord import Member, User, Message



Base = declarative_base()


class GuildMember(Base):
    __tablename__ = "member"
    id = Column(BigInteger, primary_key=True, autoincrement=False)
    discord_username = Column(String(32), index=True)
    twitter_name = Column(String(32), index=True, unique=True)
    activision_id = Column(String(128), index=True, unique=True)
    passkey_hash = Column(String(128))
    joined_on = Column(DateTime)
    trust_rating = Column(Float, default=0.0)
    notoriety = Column(Float, default=0.0)

    def __init__(
        self,
        *,
        member: Union[Member, User],
        activision_id: str,
        twitter_name: Optional[str],
        passkey: Optional[int],
    ):
        self.id = member.id
        self.activision_id = activision_id
        if len(str(passkey)) != 4:
            passkey = 0000

        self.passkey_hash = sha256(str(passkey).encode('utf-8')).hexdigest()
        self.joined_on = datetime.utcnow()

        self.twitter_name = twitter_name

    def check_passkey(self, passkey: int):
        hashed_passkey = sha256(str(passkey).encode('utf-8')).hexdigest()
        return self.passkey_hash == hashed_passkey 



class Report(Base):
    """ The id and primary key for this table should be a big integer [id of the message that made the report]"""
    __tablename__ = "report"
    id = Column(BigInteger, primary_key=True, autoincrement=False)
    timestamp = Column(DateTime, index=True)
    tzone = Column(String, index=True, default="CST")

    location = Column(String(32), index=True, default="Public Matchmaking")
    reporter_message = Column(String(256), nullable=True)

    suspect_activision_id = Column(String(32), index=True)
    suspect_gamebattles = Column(String(32), index=True)
    suspect_cmg = Column(String(32), index=True)
    suspect_platform = Column(String(32), index=True, default="Battle.net")

    proof_link_1 = Column(String(128))
    proof_link_2 = Column(String(128))
    proof_link_3 = Column(String(128))
    authorized = Column(Boolean, default=False)

    member_id = Column(ForeignKey("member.id"))
    member = relationship("Member", back_populates="reports")

    case_id = Column(ForeignKey("case.id"))
    case = relationship("Case", back_populates="reports")

    def __init__(
        self,
        passke: int,
        *,
        discord_message: Message,
        reporting_member: GuildMember,
        tzone: Literal["PST", "CST", "MST", "EST", "Other"],
        location: Literal["Public Matchmaking", "CMGs", "GBs", "Customs", "CDL Moshpit", "Ranked Mode"],
        suspect_activision_id: str,
        platform: Literal["Playstation", "Xbox", "Battle.net", "Unknown"],
        reporter_message: Optional[str],
        proof_link_1: Optional[str],
        **aliases
    ):
        self.id = int(discord_message.id)
        self.member = reporting_member
        self.timestamp = datetime.utcnow()
        self.tzone = tzone

        self.location = location
        self.reporter_message = reporter_message

        self.suspect_activision_id = suspect_activision_id
        for alias_key in aliases:
            setattr(self, alias_key, aliases[alias_key])
        self.platform = platform
        self.proof_link_1 = proof_link_1
        if self.member.check_passkey(passkey):
            self.authorized = True



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

