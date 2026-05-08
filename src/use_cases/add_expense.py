import uuid
from collections.abc import Callable
from datetime import UTC, datetime
from decimal import Decimal

from domain.entities import Expense
from domain.errors import InvalidExpenseValueError
from repositories.protocols import ExpenseRepository


def _utcnow() -> datetime:
  return datetime.now(UTC)


def _new_id() -> str:
  return str(uuid.uuid4())


class AddExpenseUseCase:
  def __init__(
    self,
    expense_repo: ExpenseRepository,
    clock: Callable[[], datetime] = _utcnow,
    id_generator: Callable[[], str] = _new_id,
  ) -> None:
    self._repo = expense_repo
    self._clock = clock
    self._id_generator = id_generator

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

    now = self._clock()
    expense = Expense(
      id=self._id_generator(),
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
