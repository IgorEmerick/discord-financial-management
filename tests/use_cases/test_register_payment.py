from datetime import UTC, datetime
from decimal import Decimal

import pytest

from domain.errors import NothingToSettleError
from tests.fakes.repositories import FakeExpenseRepository, FakePaymentRepository
from use_cases.add_expense import AddExpenseUseCase
from use_cases.register_payment import RegisterPaymentUseCase

FIXED_NOW = datetime(2025, 5, 7, 10, 0, 0, tzinfo=UTC)


@pytest.fixture
def expense_repo() -> FakeExpenseRepository:
  return FakeExpenseRepository()


@pytest.fixture
def payment_repo() -> FakePaymentRepository:
  return FakePaymentRepository()


@pytest.fixture
def payment_use_case(
  expense_repo: FakeExpenseRepository, payment_repo: FakePaymentRepository
) -> RegisterPaymentUseCase:
  return RegisterPaymentUseCase(expense_repo=expense_repo, payment_repo=payment_repo, clock=lambda: FIXED_NOW)


async def _seed_expense(expense_repo: FakeExpenseRepository, expense_id: str = "exp-1") -> None:
  use_case = AddExpenseUseCase(expense_repo=expense_repo, clock=lambda: FIXED_NOW, id_generator=lambda: expense_id)
  await use_case.execute(
    guild_id="g1",
    channel_id="c1",
    category="Food",
    description="Pizza",
    value=Decimal("90.00"),
    author_id="user1",
    channel_members=["user1", "user2", "user3"],
    paying_person="user1",
    involved_people=["user1", "user2", "user3"],
    destination_month="2025-05",
  )


@pytest.mark.asyncio
async def test_settle_all_creates_payment_per_debtor(
  expense_repo: FakeExpenseRepository, payment_repo: FakePaymentRepository, payment_use_case: RegisterPaymentUseCase
) -> None:
  await _seed_expense(expense_repo)
  payments = await payment_use_case.execute(guild_id="g1", month="2025-05")

  assert len(payments) == 2
  assert all(p.creditor == "user1" for p in payments)
  assert {p.debtor for p in payments} == {"user2", "user3"}
  assert all(p.amount == Decimal("30.00") for p in payments)


@pytest.mark.asyncio
async def test_settle_specific_creditor_debtor_pair(
  expense_repo: FakeExpenseRepository, payment_use_case: RegisterPaymentUseCase
) -> None:
  await _seed_expense(expense_repo)
  payments = await payment_use_case.execute(guild_id="g1", month="2025-05", creditor="user1", debtor="user2")

  assert len(payments) == 1
  assert payments[0].creditor == "user1"
  assert payments[0].debtor == "user2"
  assert payments[0].amount == Decimal("30.00")


@pytest.mark.asyncio
async def test_raises_when_no_outstanding_balances(payment_use_case: RegisterPaymentUseCase) -> None:
  with pytest.raises(NothingToSettleError):
    await payment_use_case.execute(guild_id="g1", month="2025-05")


@pytest.mark.asyncio
async def test_raises_when_specified_pair_has_no_balance(
  expense_repo: FakeExpenseRepository, payment_use_case: RegisterPaymentUseCase
) -> None:
  await _seed_expense(expense_repo)
  with pytest.raises(NothingToSettleError):
    await payment_use_case.execute(guild_id="g1", month="2025-05", creditor="user2", debtor="user1")


@pytest.mark.asyncio
async def test_payments_are_persisted(
  expense_repo: FakeExpenseRepository, payment_repo: FakePaymentRepository, payment_use_case: RegisterPaymentUseCase
) -> None:
  await _seed_expense(expense_repo)
  await payment_use_case.execute(guild_id="g1", month="2025-05")
  persisted = await payment_repo.find_by_month("g1", "2025-05")
  assert len(persisted) == 2


@pytest.mark.asyncio
async def test_payments_use_correct_timestamp(
  expense_repo: FakeExpenseRepository, payment_use_case: RegisterPaymentUseCase
) -> None:
  await _seed_expense(expense_repo)
  payments = await payment_use_case.execute(guild_id="g1", month="2025-05")
  assert all(p.paid_at == FIXED_NOW for p in payments)
