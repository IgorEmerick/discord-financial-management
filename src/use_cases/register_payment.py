import uuid
from collections.abc import Callable
from datetime import UTC, datetime

from domain.entities import Payment
from domain.errors import NothingToSettleError
from domain.services import compute_net_balances, compute_settlements
from repositories.protocols import ExpenseRepository, PaymentRepository


def _utcnow() -> datetime:
  return datetime.now(UTC)


def _new_id() -> str:
  return str(uuid.uuid4())


class RegisterPaymentUseCase:
  def __init__(
    self,
    expense_repo: ExpenseRepository,
    payment_repo: PaymentRepository,
    clock: Callable[[], datetime] = _utcnow,
    id_generator: Callable[[], str] = _new_id,
  ) -> None:
    self._expense_repo = expense_repo
    self._payment_repo = payment_repo
    self._clock = clock
    self._id_generator = id_generator

  async def execute(
    self,
    *,
    guild_id: str,
    month: str,
    creditor: str | None = None,
    debtor: str | None = None,
  ) -> list[Payment]:
    expenses = await self._expense_repo.find_by_month(guild_id, month)
    existing_payments = await self._payment_repo.find_by_month(guild_id, month)

    net = compute_net_balances(expenses, existing_payments)
    settlements = compute_settlements(net)

    if not settlements:
      raise NothingToSettleError(month)

    if creditor is not None and debtor is not None:
      settlements = [s for s in settlements if s.creditor == creditor and s.debtor == debtor]
      if not settlements:
        raise NothingToSettleError(month)

    now = self._clock()
    payments = []
    for settlement in settlements:
      payment = Payment(
        id=self._id_generator(),
        guild_id=guild_id,
        month=month,
        creditor=settlement.creditor,
        debtor=settlement.debtor,
        amount=settlement.amount,
        paid_at=now,
      )
      await self._payment_repo.save(payment)
      payments.append(payment)

    return payments
