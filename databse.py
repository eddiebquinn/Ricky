from sqlalchemy import create_engine, MetaData, Table, Column, ForeignKey, update
from sqlalchemy.dialects.mysql import BIGINT, INTEGER, TEXT, DATETIME, TINYINT, VARCHAR
from datetime import datetime

class Database:

    def __init__(self, dbUserName, dbUserPassword, dbIP, dbName):

        self.pymsql_string = f"mysql+pymysql://{dbUserName}:{dbUserPassword}@{dbIP}/{dbName}"
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
