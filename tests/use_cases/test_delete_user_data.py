from datetime import UTC, datetime
from decimal import Decimal

import pytest

from tests.fakes.repositories import FakeExpenseRepository, FakePaymentRepository
from use_cases.add_expense import AddExpenseUseCase
from use_cases.delete_user_data import DeleteUserDataUseCase
from use_cases.register_payment import RegisterPaymentUseCase

CURRENT_MONTH = datetime.now(UTC).strftime("%Y-%m")


@pytest.fixture
def expense_repo() -> FakeExpenseRepository:
  return FakeExpenseRepository()


@pytest.fixture
def payment_repo() -> FakePaymentRepository:
  return FakePaymentRepository()


@pytest.fixture
def add_uc(expense_repo: FakeExpenseRepository) -> AddExpenseUseCase:
  return AddExpenseUseCase(expense_repo=expense_repo)


@pytest.fixture
def register_payment_uc(
  expense_repo: FakeExpenseRepository,
  payment_repo: FakePaymentRepository,
) -> RegisterPaymentUseCase:
  return RegisterPaymentUseCase(expense_repo=expense_repo, payment_repo=payment_repo)


@pytest.fixture
def delete_uc(
  expense_repo: FakeExpenseRepository,
  payment_repo: FakePaymentRepository,
) -> DeleteUserDataUseCase:
  return DeleteUserDataUseCase(expense_repo=expense_repo, payment_repo=payment_repo)


async def _add(add_uc: AddExpenseUseCase, guild_id: str, author_id: str, paying_person: str, members=None, **kwargs):
  return await add_uc.execute(
    guild_id=guild_id,
    channel_id="c1",
    category="Food",
    description="desc",
    value=Decimal("30"),
    author_id=author_id,
    channel_members=members or [author_id],
    paying_person=paying_person,
    **kwargs,
  )


@pytest.mark.asyncio
async def test_deletes_expenses_where_user_is_payer(
  add_uc: AddExpenseUseCase,
  delete_uc: DeleteUserDataUseCase,
  expense_repo: FakeExpenseRepository,
) -> None:
  await _add(add_uc, "g1", "u1", "u1")
  await _add(add_uc, "g1", "u2", "u2", members=["u2"])

  result = await delete_uc.execute(guild_id="g1", user_id="u1")

  assert len(result.expenses) == 1
  assert all(e.paying_person != "u1" for e in expense_repo._store.values())


@pytest.mark.asyncio
async def test_deletes_expenses_where_user_is_participant_only(
  add_uc: AddExpenseUseCase,
  delete_uc: DeleteUserDataUseCase,
  expense_repo: FakeExpenseRepository,
) -> None:
  await add_uc.execute(
    guild_id="g1",
    channel_id="c1",
    category="Food",
    description="Pizza",
    value=Decimal("30"),
    author_id="u2",
    channel_members=["u2"],
    paying_person="u2",
    involved_people=["u1", "u2"],
  )

  result = await delete_uc.execute(guild_id="g1", user_id="u1")

  assert len(result.expenses) == 1
  assert expense_repo._store == {}


@pytest.mark.asyncio
async def test_does_not_delete_expenses_from_other_guilds(
  add_uc: AddExpenseUseCase,
  delete_uc: DeleteUserDataUseCase,
  expense_repo: FakeExpenseRepository,
) -> None:
  await _add(add_uc, "g1", "u1", "u1")
  await _add(add_uc, "g2", "u1", "u1")

  result = await delete_uc.execute(guild_id="g1", user_id="u1")

  assert len(result.expenses) == 1
  assert len(expense_repo._store) == 1
  assert list(expense_repo._store.values())[0].guild_id == "g2"


@pytest.mark.asyncio
async def test_deletes_payments_where_user_is_creditor_or_debtor(
  add_uc: AddExpenseUseCase,
  register_payment_uc: RegisterPaymentUseCase,
  delete_uc: DeleteUserDataUseCase,
  payment_repo: FakePaymentRepository,
) -> None:
  await add_uc.execute(
    guild_id="g1",
    channel_id="c1",
    category="Food",
    description="Pizza",
    value=Decimal("30"),
    author_id="u1",
    channel_members=["u1", "u2"],
    paying_person="u1",
    involved_people=["u1", "u2"],
  )
  await register_payment_uc.execute(guild_id="g1", month=CURRENT_MONTH, creditor="u1", debtor="u2")

  result = await delete_uc.execute(guild_id="g1", user_id="u1")

  assert len(result.payments) == 1
  assert payment_repo._store == {}


@pytest.mark.asyncio
async def test_returns_zero_counts_when_no_data(delete_uc: DeleteUserDataUseCase) -> None:
  result = await delete_uc.execute(guild_id="g1", user_id="u1")

  assert result.expenses == []
  assert result.payments == []
