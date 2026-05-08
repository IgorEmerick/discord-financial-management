import asyncio
import logging
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

from bot.expense_cog import ExpensesCog
from db.pool import create_pool
from repositories.postgres.postgres_expense_repository import PostgresExpenseRepository
from repositories.postgres.postgres_payment_repository import PostgresPaymentRepository
from use_cases.add_expense import AddExpenseUseCase
from use_cases.delete_expense import DeleteExpenseUseCase
from use_cases.edit_expense import EditExpenseUseCase
from use_cases.generate_report import GenerateReportUseCase
from use_cases.register_payment import RegisterPaymentUseCase

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)


class _ExpenseBot(commands.Bot):
  def __init__(self, cog: ExpensesCog) -> None:
    intents = discord.Intents.default()
    intents.guilds = True
    intents.members = True
    super().__init__(command_prefix="!", intents=intents)
    self._cog = cog

  async def setup_hook(self) -> None:
    await self.add_cog(self._cog)
    await self.tree.sync()
    logger.info("Slash commands synced")

  async def on_ready(self) -> None:
    logger.info("Logged in as %s (id=%s)", self.user, self.user.id)


async def _run(token: str, database_url: str) -> None:
  pool = await create_pool(database_url)
  try:
    expense_repo = PostgresExpenseRepository(pool)
    payment_repo = PostgresPaymentRepository(pool)

    cog = ExpensesCog(
      add_expense_uc=AddExpenseUseCase(expense_repo),
      edit_expense_uc=EditExpenseUseCase(expense_repo),
      delete_expense_uc=DeleteExpenseUseCase(expense_repo),
      generate_report_uc=GenerateReportUseCase(expense_repo, payment_repo),
      register_payment_uc=RegisterPaymentUseCase(expense_repo, payment_repo),
    )

    await _ExpenseBot(cog).start(token)
  finally:
    await pool.close()


def main() -> None:
  load_dotenv()
  token = os.environ["DISCORD_BOT_TOKEN"]
  database_url = os.environ["DATABASE_URL"]
  asyncio.run(_run(token, database_url))


if __name__ == "__main__":
  main()
