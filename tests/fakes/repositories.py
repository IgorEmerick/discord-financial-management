from domain.entities import Expense, Payment


class FakeExpenseRepository:
  def __init__(self) -> None:
    self._store: dict[str, Expense] = {}

  async def save(self, expense: Expense) -> None:
    self._store[expense.id] = expense

  async def find_by_id(self, expense_id: str) -> Expense | None:
    return self._store.get(expense_id)

  async def find_by_month(self, guild_id: str, month: str) -> list[Expense]:
    return [e for e in self._store.values() if e.guild_id == guild_id and e.destination_month == month]

  async def update(self, expense: Expense) -> None:
    self._store[expense.id] = expense

  async def delete(self, expense_id: str) -> None:
    self._store.pop(expense_id, None)


class FakePaymentRepository:
  def __init__(self) -> None:
    self._store: dict[str, Payment] = {}

  async def save(self, payment: Payment) -> None:
    self._store[payment.id] = payment

  async def find_by_month(self, guild_id: str, month: str) -> list[Payment]:
    return [p for p in self._store.values() if p.guild_id == guild_id and p.month == month]
