from decimal import Decimal

import asyncpg

from domain.entities import Expense


class PostgresExpenseRepository:
  def __init__(self, pool: asyncpg.Pool) -> None:
    self._pool = pool

  async def save(self, expense: Expense) -> None:
    async with self._pool.acquire() as conn:
      await conn.execute(
        """
        INSERT INTO expenses
          (id, guild_id, channel_id, category, description, value,
           paying_person, involved_people, destination_month, created_at, updated_at)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
        """,
        expense.id, expense.guild_id, expense.channel_id,
        expense.category, expense.description, expense.value,
        expense.paying_person, expense.involved_people,
        expense.destination_month, expense.created_at, expense.updated_at,
      )

  async def find_by_id(self, expense_id: str) -> Expense | None:
    async with self._pool.acquire() as conn:
      row = await conn.fetchrow("SELECT * FROM expenses WHERE id = $1", expense_id)
    return _to_expense(row) if row else None

  async def find_by_month(self, guild_id: str, month: str) -> list[Expense]:
    async with self._pool.acquire() as conn:
      rows = await conn.fetch(
        "SELECT * FROM expenses WHERE guild_id = $1 AND destination_month = $2 ORDER BY created_at",
        guild_id, month,
      )
    return [_to_expense(r) for r in rows]

  async def update(self, expense: Expense) -> None:
    async with self._pool.acquire() as conn:
      await conn.execute(
        """
        UPDATE expenses SET
          category = $1, description = $2, value = $3,
          paying_person = $4, involved_people = $5,
          destination_month = $6, updated_at = $7
        WHERE id = $8
        """,
        expense.category, expense.description, expense.value,
        expense.paying_person, expense.involved_people,
        expense.destination_month, expense.updated_at,
        expense.id,
      )

  async def delete(self, expense_id: str) -> None:
    async with self._pool.acquire() as conn:
      await conn.execute("DELETE FROM expenses WHERE id = $1", expense_id)


def _to_expense(row: asyncpg.Record) -> Expense:
  return Expense(
    id=row["id"],
    guild_id=row["guild_id"],
    channel_id=row["channel_id"],
    category=row["category"],
    description=row["description"],
    value=Decimal(str(row["value"])),
    paying_person=row["paying_person"],
    involved_people=list(row["involved_people"]),
    destination_month=row["destination_month"],
    created_at=row["created_at"],
    updated_at=row["updated_at"],
  )
