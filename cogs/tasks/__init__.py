import logging
from main import AIKyaru
import discord
from discord.ext import commands
import asyncio
from datetime import datetime, time


class Tasks(commands.Cog):
    def __init__(self, bot: AIKyaru):
        self.bot = bot
        self.logger = logging.getLogger("AIKyaru.Tasks")
        self.loop = asyncio.get_event_loop()
        
        self.task_update_checker = self.loop.create_task(self.update_checker())

    def cog_unload(self):
        self.task_update_checker.cancel()

    async def update_checker(self):
        try:
            while True:
                await asyncio.sleep(0)
                now = datetime.now()
                # Runs only at 5 or 16 o'clock and skip first time
                if now.hour not in (5, 16) or not self.bot.is_ready():
                    wait_until = datetime.combine(
                        now, time(hour=now.hour + 1, minute=5, second=0)
                    )  # wait until XX:05:00
                    wait_seconds = (wait_until - now).seconds
                    self.logger.debug(f"Need wait: {wait_seconds}")

                    await asyncio.sleep(wait_seconds)
                    continue

                self.logger.info("Starting update task...")
                await self.bot.config.update()
                asyncio.sleep(3600)  # wait 1 hour

        except asyncio.CancelledError:
            self.logger.info("Update task cancelled.")


def setup(bot):
    bot.add_cog(Tasks(bot))