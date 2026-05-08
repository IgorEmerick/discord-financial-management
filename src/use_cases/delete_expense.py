from domain.errors import ExpenseNotFoundError
from repositories.protocols import ExpenseRepository


class DeleteExpenseUseCase:
  def __init__(self, expense_repo: ExpenseRepository) -> None:
    self._repo = expense_repo

  async def execute(self, *, expense_id: str) -> None:
    if await self._repo.find_by_id(expense_id) is None:
      raise ExpenseNotFoundError(expense_id)
    await self._repo.delete(expense_id)
