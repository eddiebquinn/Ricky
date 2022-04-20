from sqlalchemy import create_engine, MetaData, Table, Column, ForeignKey, update
from sqlalchemy.dialects.mysql import BIGINT, INTEGER, TEXT, DATETIME, TINYINT, VARCHAR
from datetime import datetime

class Database:

    def __init__(self, config:dict):
        """_summary_

        Args:
            config (dict): Part of the settings.JSON file, should contain
                -Mysql username
                -Mysql password
                -Host IP
                -Host port
                -Scheema name
        """

        self.pymsql_string = f"mysql+pymysql://{config['username']}:{config['password']}@{config['host']}/{config['database']}"
        self.engine = create_engine(self.pymsql_string, echo=True)
        self.conn = self.engine.connect()
        self.meta = MetaData()

        self.userTab = Table(
            'user', self.meta,
            Column('discord_user_id', BIGINT, primary_key=True, nullable=False),
            Column('last_update', DATETIME)
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
            Column('role_config_id', INTEGER, primary_key=True, nullable=False, autoincrement=True),
            Column('guild_id', BIGINT, ForeignKey("guild.guild_id"), nullable=False),
            Column('day_reach', INTEGER, nullable=False),
            Column('role_id', BIGINT, nullable=False)
        )

        self.relapseTab = Table(
            "relapse_data", self.meta,
            Column("relapse_id", INTEGER, primary_key=True, nullable=False, autoincrement=True),
            Column("discord_user_id", BIGINT, ForeignKey("user.discord_user_id"), nullable=False),
            Column("relapse_utc", DATETIME, nullable=False),
            Column("previous_streak_invalid", INTEGER)
        )

        self.webConfigTab = Table(
            "web_config_edit", self.meta,
            Column("edit_id", INTEGER, primary_key=True, nullable=False, autoincrement=True),
            Column('guild_id', BIGINT, ForeignKey("guild.guild_id"), nullable=False),
            Column('random_string', VARCHAR(10), nullable=False),
            Column('utc_expire', DATETIME, nullable=False),
            Column('server_channel_json', TEXT, nullable=False),
            Column('server_roles_json', TEXT, nullable=False),
        )
        
        self.meta.create_all(self.engine)

    #Relapse Tab
    async def insert_relapse(self, user_id:int, relapse_utc=datetime.utcnow(), previous_streak_invalid=False):
        query = self.relapseTab.insert().values(
            discord_user_id=user_id,
            relapse_utc=relapse_utc,
            previous_streak_invalid=previous_streak_invalid
        )
        self.conn.execute(query)

    #Guild Tab
    
    async def select_guild_data(self, guild_id:int):
        query = self.guildTab.select().where(self.guildTab.c.guild_id == guild_id)
        return self.conn.execute(query).fetchall()

    #Relapse Tab

    async def select_relapse_data(self, user_id:int):
        query = self.relapseTab.select().where(relapseTab.c.discord_user_id == user_id).order_by(self.relapseTab.c.relapse_utc)
        return self.conn.execute(query).fetchall
     
    #Userdata Tab

    async def insert_user_data(self, user_id:int):
        query = self.userTab.insert().values(
            discord_user_id = user_id,
            last_update = datetime.utcnow())
        self.conn.execute(query)
    
    async def update_user_data(self, user_id:int):
        query = update(userTab).where(userdata.c.id == user_id).values(
            last_update = datetime.utcnow())
        self.conn.execute(query)