import utils.utils as utils
import utils.logger as logger
from sqlalchemy import create_engine, MetaData, Table, Column, ForeignKey, update, desc
from sqlalchemy.dialects.mysql import BIGINT, INTEGER, TEXT, DATETIME, TINYINT, VARCHAR
from datetime import datetime


class Database:

    def __init__(self, config: dict, echo: bool = True):
        """Initalises the databse

        Args:
            config (dict): Part of the settings.JSON file
            echo (bool, optional): Weather the SQLalchemy should be verbose. Defaults to True.
        """
        self.logger = logger.LOGGER

        self.pymsql_string = f"mysql+pymysql://{config['username']}:{config['password']}@{config['host']}/{config['database']}"
        self.engine = create_engine(self.pymsql_string, echo=echo)
        self.conn = self.engine.connect()
        self.meta = MetaData()

        self.userTab = Table(
            'user', self.meta,
            Column('discord_user_id', BIGINT,
                   primary_key=True, nullable=False),
            Column('last_update', DATETIME),
            Column('developer', TINYINT, nullable=False, default=0)
        )

        self.guildTab = Table(
            'guild', self.meta,
            Column('guild_id', BIGINT, primary_key=True, nullable=False),
            Column('streak_channel_limit', TINYINT, nullable=False),
            Column('strak_roles_channel', BIGINT),
            Column('roles_enabled', TINYINT, nullable=False),
            Column('porn_filter_enabled', TINYINT, nullable=False)
        )

        self.roleConfigTab = Table(
            'role_config', self.meta,
            Column('role_config_id', INTEGER, primary_key=True,
                   nullable=False, autoincrement=True),
            Column('guild_id', BIGINT, ForeignKey(
                "guild.guild_id"), nullable=False),
            Column('day_reach', INTEGER, nullable=False),
            Column('role_id', BIGINT, nullable=False)
        )

        self.relapseTab = Table(
            "relapse_data", self.meta,
            Column("relapse_id", INTEGER, primary_key=True,
                   nullable=False, autoincrement=True),
            Column("discord_user_id", BIGINT, ForeignKey(
                "user.discord_user_id"), nullable=False),
            Column("relapse_utc", DATETIME, nullable=False),
            Column("previous_streak_invalid", INTEGER)
        )

        self.webConfigTab = Table(
            "web_config_edit", self.meta,
            Column("edit_id", INTEGER, primary_key=True,
                   nullable=False, autoincrement=True),
            Column('guild_id', BIGINT, ForeignKey(
                "guild.guild_id"), nullable=False),
            Column('random_string', VARCHAR(10), nullable=False),
            Column('utc_expire', DATETIME, nullable=False),
            Column('server_channel_json', TEXT, nullable=False),
            Column('server_roles_json', TEXT, nullable=False),
        )

        self.meta.create_all(self.engine)
        self.logger.warning("Initilised database")

    async def do_log(self, query_type: str, table: str, params: dict):
        """Creates an IFO log with standard format

        Args:
            query_type (str): The type of query
            table (str): That table the query was performed on
            params (str): Relevant paramaters to the query 
        """
        msg = f"{query_type.upper()} to {table.lower()} - {str(params)}"
        self.logger.info(msg)

    # Guild Tab

    async def select_guild_data(self, guild_id: int):
        """Returns the data of the specified guild

        Args:
            guild_id (int): The id of the requested guild

        Returns:
            tuple: The data of the guild requested
        """
        await self.do_log("SELECT", "guild", {"guild_id": guild_id})
        query = self.guildTab.select().where(self.guildTab.c.guild_id == guild_id)
        return self.conn.execute(query).fetchone()

    async def insert_guild_data(self, guild_id: int):
        """Inserts data into the guild table

        Args:
            guild_id (int): The id of the guild which is subject to the data being inserted
        """
        await self.do_log("INSERT", "guild", {"guild_id": guild_id})
        query = self.guildTab.insert().values(
            guild_id=guild_id,
            streak_channel_limit=0,
            roles_enabled=0,
            porn_filter_enabled=0
        )
        self.conn.execute(query)

    async def update_guild_data(self, guild_id: int, data: dict):
        """Updates data in the guild table

        Args:
            guild_id (int): The id of the guild which is subject to the data being updated
            data (dict): The data being inserted

        Returns:
            Bool: Returns true of data is succsessfuly updated
        """
        log_dict = data
        log_dict["guild_id"] = guild_id
        await self.do_log("UPDATE", "guild", log_dict)
        query = update(self.guildTab).where(
            self.guildTab.c.guild_id == guild_id).values(data)
        self.conn.execute(query)
        return True

    # Relapse Tab

    async def select_relapse_data(self, user_id: int):
        """Returns a list of users previous relapses

        Args:
            user_id (int): The id of the requested user

        Returns:
            list: The previous relapses of that user
        """
        await self.do_log("SELECT", "relapse_data", {"user_id": user_id})
        query = self.relapseTab.select().where(self.relapseTab.c.discord_user_id ==
                                               user_id).order_by(desc(self.relapseTab.c.relapse_utc))
        return self.conn.execute(query).fetchall()

    async def insert_relapse(self, user_id: int, relapse_utc=datetime.utcnow(), previous_streak_invalid=False):
        """Inserts relapse into relapse table

        Args:
            user_id (int): The discord user id
            relapse_utc (_type_, optional): The utc of the relaspe.
            previous_streak_invalid (bool, optional): Weather the previous streak is valid.
        """
        await self.do_log("INSERT", "relapse_data", {
            "user_id": user_id,
            "relapse_utc": relapse_utc,
            "previous_streak_invalid": previous_streak_invalid})
        query = self.relapseTab.insert().values(
            discord_user_id=user_id,
            relapse_utc=relapse_utc,
            previous_streak_invalid=previous_streak_invalid
        )
        self.conn.execute(query)

    # Userdata Tab
    async def seclect_user_data(self, user_id: int):
        """Returns a tuple of the users data

        Args:
            user_id (int): The id of the requested user

        Returns:
            tuple: The user data
        """
        await self.do_log("SELECT", "user", {"user_id": user_id})
        query = self.userTab.select().where(self.userTab.c.discord_user_id == user_id)
        return self.conn.execute(query).fetchone()

    async def insert_user_data(self, user_id: int):
        """Inserts a new user into the databse

        Args:
            user_id (int): The id of the user being recorded
        """
        await self.do_log("INSERT", "user", {"user_id": user_id, "last_update": datetime.utcnow()})
        query = self.userTab.insert().values(
            discord_user_id=user_id,
            last_update=datetime.utcnow())
        self.conn.execute(query)

    async def update_user_data(self, user_id: int):
        """Updates the data of a specfic user in the user table

        Args:
            user_id (int): The user whos data is to be updated
        """
        await self.do_log("UPDATE", "user", {"user_id": user_id, "last_update": datetime.utcnow()})
        query = update(self.userTab).where(self.userTab.c.discord_user_id == user_id).values(
            last_update=datetime.utcnow())
        self.conn.execute(query)

    # Roleinfo Tab
    async def select_guild_roles(self, guild_id: int):
        """returns a list of the roles set up for a guild

        Args:
            guild_id (int): The guild of which the returned roles are subject to

        Returns:
            list: list of roles assoacited with the given server
        """
        await self.do_log("SELECT", "role_config", {"guild_id": guild_id})
        query = self.roleConfigTab.select().where(
            self.roleConfigTab.c.guild_id == guild_id)
        return self.conn.execute(query).fetchall()

    async def insert_guild_roles(self, guild_id, day_reach, role_id):
        """create this before merge"""
        await self.do_log("INSERT", "role_config", {"guild_id": guild_id, "day_reach": day_reach, "role_id": role_id})
        query = self.roleConfigTab.insert().values(
            guild_id=guild_id,
            day_reach=day_reach,
            role_id=role_id)
        self.conn.execute(query)

    async def delete_guild_roles(self, id: int):
        """deletes row with a specic role id"""
        await self.do_log("DELETE", "role_config", {"role_config_id": id})
        query = self.roleConfigTab.delete().where(
            self.roleConfigTab.c.role_config_id == id)
        self.conn.execute(query)


def database_init(echo=False):
    """Initalises the databse

    Args:
        echo (bool, optional): Weather the SQLalchemy should be verbose.. Defaults to True.
    """
    global DATABASE_CONN
    DATABASE_CONN = Database(config=utils.extract_json()[
        "sql_connection_settings"], echo=echo)
