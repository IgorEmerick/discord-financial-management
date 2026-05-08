from datetime import UTC, datetime
from decimal import Decimal

import pytest

from domain.errors import ExpenseNotFoundError
from fakes.repositories import FakeExpenseRepository
from use_cases.add_expense import AddExpenseUseCase
from use_cases.delete_expense import DeleteExpenseUseCase

FIXED_NOW = datetime(2025, 5, 7, 10, 0, 0, tzinfo=UTC)


@pytest.fixture
def repo() -> FakeExpenseRepository:
  return FakeExpenseRepository()


@pytest.fixture
def add_use_case(repo: FakeExpenseRepository) -> AddExpenseUseCase:
  return AddExpenseUseCase(expense_repo=repo, clock=lambda: FIXED_NOW, id_generator=lambda: "exp-1")


@pytest.fixture
def delete_use_case(repo: FakeExpenseRepository) -> DeleteExpenseUseCase:
  return DeleteExpenseUseCase(expense_repo=repo)


@pytest.fixture
async def existing_expense(add_use_case: AddExpenseUseCase):
  return await add_use_case.execute(
    guild_id="g1",
    channel_id="c1",
    category="Food",
    description="Pizza",
    value=Decimal("90.00"),
    author_id="user1",
    channel_members=["user1"],
    destination_month="2025-05",
  )


@pytest.mark.asyncio
async def test_delete_removes_expense(
  delete_use_case: DeleteExpenseUseCase, repo: FakeExpenseRepository, existing_expense
) -> None:
  await delete_use_case.execute(expense_id="exp-1")
  assert await repo.find_by_id("exp-1") is None


@pytest.mark.asyncio
async def test_raises_when_expense_not_found(delete_use_case: DeleteExpenseUseCase) -> None:
  with pytest.raises(ExpenseNotFoundError):
    await delete_use_case.execute(expense_id="nonexistent")
