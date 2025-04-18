#  Copyright (c) 2025 AshokShau.
#  TgMusicBot is an open-source Telegram music bot licensed under AGPL-3.0.
#  All rights reserved where applicable.
#
#

import asyncio
import os
import shutil

from pytdbot import Client, types

import config
from src.database import db
from src.modules.jobs import InactiveCallManager
from src.pytgcalls import call, start_clients

__version__ = "1.1.2"


class Telegram(Client):
    def __init__(self) -> None:
        self._check_config()
        super().__init__(
            token=config.TOKEN,
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            default_parse_mode="html",
            td_verbosity=2,
            td_log=types.LogStreamEmpty(),
            plugins=types.plugins.Plugins(folder="src/modules"),
            files_directory="",
            database_encryption_key="",
            options={"ignore_background_updates": True},
        )
        self.call_manager = InactiveCallManager(self)
        self.db = db

    async def start(self, login: bool = True) -> None:
        await self.db.ping()
        await start_clients()
        await call.add_bot(self)
        await call.register_decorators()
        await self.call_manager.start_scheduler()
        await super().start()
        self.logger.info("✅ Bot started successfully.")

    async def stop(self) -> None:
        shutdown_tasks = [
            self.db.close(),
            self.call_manager.stop_scheduler(),
            super().stop(),
        ]
        await asyncio.gather(*shutdown_tasks, return_exceptions=False)

    @staticmethod
    def _check_config() -> None:
        if os.path.exists("database"):
            shutil.rmtree("database")
        if not isinstance(config.MONGO_URI, str):
            raise TypeError("MONGO_URI must be a string")
        session_strings = [s for s in config.SESSION_STRINGS if s]
        if not session_strings:
            raise ValueError("No STRING session provided\n\nAdd STRING session in .env")


client = Telegram()
