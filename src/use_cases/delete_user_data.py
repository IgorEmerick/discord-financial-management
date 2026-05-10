from dataclasses import dataclass

from domain.entities import Expense, Payment
from repositories.protocols import ExpenseRepository, PaymentRepository


@dataclass
class DeleteUserDataResult:
  expenses: list[Expense]
  payments: list[Payment]


class DeleteUserDataUseCase:
  def __init__(self, expense_repo: ExpenseRepository, payment_repo: PaymentRepository) -> None:
    self._expense_repo = expense_repo
    self._payment_repo = payment_repo

  async def execute(self, *, guild_id: str, user_id: str) -> DeleteUserDataResult:
    expenses = await self._expense_repo.delete_by_user(guild_id, user_id)
    payments = await self._payment_repo.delete_by_user(guild_id, user_id)
    return DeleteUserDataResult(expenses=expenses, payments=payments)
