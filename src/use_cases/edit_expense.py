from datetime import UTC, datetime
from decimal import Decimal

from domain.entities import Expense
from domain.errors import ExpenseNotFoundError, InvalidExpenseValueError, NoEditFieldsProvidedError
from repositories.protocols import ExpenseRepository


class EditExpenseUseCase:
  def __init__(self, expense_repo: ExpenseRepository) -> None:
    self._repo = expense_repo

  def _utcnow(self) -> datetime:
    return datetime.now(UTC)

  async def execute(
    self,
    *,
    expense_id: str,
    category: str | None = None,
    description: str | None = None,
    value: Decimal | None = None,
    paying_person: str | None = None,
    involved_people: list[str] | None = None,
    destination_month: str | None = None,
  ) -> Expense:
    updates = {
      k: v
      for k, v in {
        "category": category,
        "description": description,
        "value": value,
        "paying_person": paying_person,
        "involved_people": involved_people,
        "destination_month": destination_month,
      }.items()
      if v is not None
    }

    if not updates:
      raise NoEditFieldsProvidedError()

    if "value" in updates and updates["value"] <= 0:
      raise InvalidExpenseValueError(updates["value"])

    expense = await self._repo.find_by_id(expense_id)
    if expense is None:
      raise ExpenseNotFoundError(expense_id)

    for field, val in updates.items():
      setattr(expense, field, val)
    expense.updated_at = self._utcnow()

    await self._repo.update(expense)
    return expense
