import asyncio
import logging
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

from container import Container

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)


class _ExpenseBot(commands.Bot):
  def __init__(self, container: Container) -> None:
    intents = discord.Intents.default()
    intents.guilds = True
    intents.members = True
    super().__init__(command_prefix=commands.when_mentioned, intents=intents)
    self._container = container

  async def setup_hook(self) -> None:
    await self.add_cog(self._container.cog())
    await self.tree.sync()
    logger.info("Slash commands synced")

  async def on_ready(self) -> None:
    if self.user:
      logger.info("Logged in as %s (id=%s)", self.user, self.user.id)


async def _run(token: str, database_url: str) -> None:
  container = Container()
  container.config.database_url.from_value(database_url)

  init = container.init_resources()
  if init is not None:
    await init

  try:
    await _ExpenseBot(container).start(token)
  finally:
    shutdown = container.shutdown_resources()
    if shutdown is not None:
      await shutdown


def main() -> None:
  load_dotenv()
  token = os.environ["DISCORD_BOT_TOKEN"]
  database_url = os.environ["DATABASE_URL"]
  asyncio.run(_run(token, database_url))


if __name__ == "__main__":
  main()
