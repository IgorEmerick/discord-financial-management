from decimal import Decimal

import asyncpg

from domain.entities import Payment


class PostgresPaymentRepository:
  def __init__(self, pool: asyncpg.Pool) -> None:
    self._pool = pool

  async def save(self, payment: Payment) -> None:
    async with self._pool.acquire() as conn:
      await conn.execute(
        """
        INSERT INTO payments (id, guild_id, month, creditor, debtor, amount, paid_at)
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        """,
        payment.id, payment.guild_id, payment.month,
        payment.creditor, payment.debtor, payment.amount, payment.paid_at,
      )

  async def find_by_month(self, guild_id: str, month: str) -> list[Payment]:
    async with self._pool.acquire() as conn:
      rows = await conn.fetch(
        "SELECT * FROM payments WHERE guild_id = $1 AND month = $2 ORDER BY paid_at",
        guild_id, month,
      )
    return [_to_payment(r) for r in rows]


def _to_payment(row: asyncpg.Record) -> Payment:
  return Payment(
    id=row["id"],
    guild_id=row["guild_id"],
    month=row["month"],
    creditor=row["creditor"],
    debtor=row["debtor"],
    amount=Decimal(str(row["amount"])),
    paid_at=row["paid_at"],
  )
