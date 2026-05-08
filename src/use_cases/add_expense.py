from datetime import UTC, datetime
from decimal import Decimal

from ulid import ULID

from domain.entities import Expense
from domain.errors import InvalidExpenseValueError
from repositories.protocols import ExpenseRepository


class AddExpenseUseCase:
  def __init__(self, expense_repo: ExpenseRepository) -> None:
    self._repo = expense_repo

  def _utcnow(self) -> datetime:
    return datetime.now(UTC)

  def _new_id(self) -> str:
    return str(ULID())

  async def execute(
    self,
    *,
    guild_id: str,
    channel_id: str,
    category: str,
    description: str,
    value: Decimal,
    author_id: str,
    channel_members: list[str],
    paying_person: str | None = None,
    involved_people: list[str] | None = None,
    destination_month: str | None = None,
  ) -> Expense:
    if value <= 0:
      raise InvalidExpenseValueError(value)

    now = self._utcnow()
    expense = Expense(
      id=self._new_id(),
      guild_id=guild_id,
      channel_id=channel_id,
      category=category,
      description=description,
      value=value,
      paying_person=paying_person or author_id,
      involved_people=involved_people or list(channel_members),
      destination_month=destination_month or now.strftime("%Y-%m"),
      created_at=now,
      updated_at=now,
    )
    await self._repo.save(expense)
    return expense
