import asyncio
import logging
import os

import discord
from dependency_injector import providers
from discord.ext import commands
from dotenv import load_dotenv

from bot.expense_cog import ExpensesCog
from container import Container
from db.pool import create_pool

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
    cog = ExpensesCog(
      add_expense_uc=self._container.add_expense_uc(),
      edit_expense_uc=self._container.edit_expense_uc(),
      delete_expense_uc=self._container.delete_expense_uc(),
      generate_report_uc=self._container.generate_report_uc(),
      list_expenses_uc=self._container.list_expenses_uc(),
      register_payment_uc=self._container.register_payment_uc(),
    )
    await self.add_cog(cog)
    await self.tree.sync()
    logger.info("Slash commands synced")

  async def on_ready(self) -> None:
    if self.user:
      logger.info("Logged in as %s (id=%s)", self.user, self.user.id)


async def _run(token: str, database_url: str) -> None:
  pool = await create_pool(database_url)
  try:
    container = Container()
    container.pool.override(providers.Object(pool))
    await _ExpenseBot(container).start(token)
  finally:
    await pool.close()


def main() -> None:
  load_dotenv()
  token = os.environ["DISCORD_BOT_TOKEN"]
  pg_user = os.environ.get("POSTGRES_USER", "postgres")
  pg_password = os.environ["POSTGRES_PASSWORD"]
  pg_host = os.environ.get("POSTGRES_HOST", "localhost")
  pg_port = os.environ.get("POSTGRES_PORT", "5432")
  pg_db = os.environ.get("POSTGRES_DB", "expenses")
  database_url = f"postgresql://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_db}"
  asyncio.run(_run(token, database_url))


if __name__ == "__main__":
  main()
