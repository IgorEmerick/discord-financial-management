from domain.entities import Balance, Report
from domain.services import compute_net_balances, compute_settlements
from repositories.protocols import ExpenseRepository, PaymentRepository


class GenerateReportUseCase:
  def __init__(self, expense_repo: ExpenseRepository, payment_repo: PaymentRepository) -> None:
    self._expense_repo = expense_repo
    self._payment_repo = payment_repo

  async def execute(self, *, guild_id: str, month: str) -> Report:
    expenses = await self._expense_repo.find_by_month(guild_id, month)
    payments = await self._payment_repo.find_by_month(guild_id, month)

    net = compute_net_balances(expenses, payments)
    balances = [Balance(user_id=uid, net=n) for uid, n in net.items()]
    settlements = compute_settlements(net)

    return Report(month=month, expenses=expenses, balances=balances, settlements=settlements)
