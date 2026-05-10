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

  async def delete_by_user(self, guild_id: str, user_id: str) -> list[Expense]:
    to_delete = [
      e
      for e in self._store.values()
      if e.guild_id == guild_id and (e.paying_person == user_id or user_id in e.involved_people)
    ]
    for e in to_delete:
      del self._store[e.id]
    return to_delete


class FakePaymentRepository:
  def __init__(self) -> None:
    self._store: dict[str, Payment] = {}

  async def save(self, payment: Payment) -> None:
    self._store[payment.id] = payment

  async def find_by_month(self, guild_id: str, month: str) -> list[Payment]:
    return [p for p in self._store.values() if p.guild_id == guild_id and p.month == month]

  async def delete_by_user(self, guild_id: str, user_id: str) -> list[Payment]:
    to_delete = [
      p for p in self._store.values() if p.guild_id == guild_id and (p.creditor == user_id or p.debtor == user_id)
    ]
    for p in to_delete:
      del self._store[p.id]
    return to_delete
