from datetime import UTC, datetime
from decimal import Decimal
from unittest.mock import patch

import pytest
from fakes.repositories import FakeExpenseRepository

from domain.errors import InvalidExpenseValueError
from use_cases.add_expense import AddExpenseUseCase

FIXED_NOW = datetime(2025, 5, 7, 21, 0, 0, tzinfo=UTC)
FIXED_ID = "exp-test-id"


@pytest.fixture
def repo() -> FakeExpenseRepository:
  return FakeExpenseRepository()


@pytest.fixture
def use_case(repo: FakeExpenseRepository) -> AddExpenseUseCase:
  return AddExpenseUseCase(expense_repo=repo)


@pytest.mark.asyncio
async def test_add_expense_with_all_fields(use_case: AddExpenseUseCase, repo: FakeExpenseRepository) -> None:
  with (
    patch.object(use_case, "_utcnow", return_value=FIXED_NOW),
    patch.object(use_case, "_new_id", return_value=FIXED_ID),
  ):
    expense = await use_case.execute(
      guild_id="g1",
      channel_id="c1",
      category="Food",
      description="Pizza night",
      value=Decimal("85.50"),
      author_id="user1",
      channel_members=["user1", "user2"],
      paying_person="user1",
      involved_people=["user1", "user2"],
      destination_month="2025-05",
    )

  assert expense.id == FIXED_ID
  assert expense.paying_person == "user1"
  assert expense.involved_people == ["user1", "user2"]
  assert expense.destination_month == "2025-05"
  assert expense.created_at == FIXED_NOW
  assert expense.updated_at == FIXED_NOW
  assert await repo.find_by_id(FIXED_ID) is expense


@pytest.mark.asyncio
async def test_infers_payer_as_author_when_omitted(use_case: AddExpenseUseCase) -> None:
  expense = await use_case.execute(
    guild_id="g1",
    channel_id="c1",
    category="Food",
    description="Lunch",
    value=Decimal("30.00"),
    author_id="user1",
    channel_members=["user1", "user2"],
  )
  assert expense.paying_person == "user1"


@pytest.mark.asyncio
async def test_infers_participants_as_channel_members_when_omitted(use_case: AddExpenseUseCase) -> None:
  expense = await use_case.execute(
    guild_id="g1",
    channel_id="c1",
    category="Food",
    description="Lunch",
    value=Decimal("30.00"),
    author_id="user1",
    channel_members=["user1", "user2", "user3"],
  )
  assert expense.involved_people == ["user1", "user2", "user3"]


@pytest.mark.asyncio
async def test_infers_month_from_clock_when_omitted(use_case: AddExpenseUseCase) -> None:
  with patch.object(use_case, "_utcnow", return_value=FIXED_NOW):
    expense = await use_case.execute(
      guild_id="g1",
      channel_id="c1",
      category="Food",
      description="Lunch",
      value=Decimal("30.00"),
      author_id="user1",
      channel_members=["user1"],
    )
  assert expense.destination_month == "2025-05"


@pytest.mark.asyncio
async def test_raises_on_zero_value(use_case: AddExpenseUseCase) -> None:
  with pytest.raises(InvalidExpenseValueError):
    await use_case.execute(
      guild_id="g1",
      channel_id="c1",
      category="Food",
      description="Lunch",
      value=Decimal("0"),
      author_id="user1",
      channel_members=["user1"],
    )


@pytest.mark.asyncio
async def test_raises_on_negative_value(use_case: AddExpenseUseCase) -> None:
  with pytest.raises(InvalidExpenseValueError):
    await use_case.execute(
      guild_id="g1",
      channel_id="c1",
      category="Food",
      description="Lunch",
      value=Decimal("-10.00"),
      author_id="user1",
      channel_members=["user1"],
    )
