from domain.entities import Expense
from repositories.protocols import ExpenseRepository


class ListExpensesUseCase:
  def __init__(self, expense_repo: ExpenseRepository) -> None:
    self._expense_repo = expense_repo

  async def execute(self, *, guild_id: str, month: str) -> list[Expense]:
    return await self._expense_repo.find_by_month(guild_id, month)
