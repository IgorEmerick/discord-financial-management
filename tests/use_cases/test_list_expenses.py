from datetime import datetime, timezone
from decimal import Decimal

import pytest

from tests.fakes.repositories import FakeExpenseRepository
from use_cases.add_expense import AddExpenseUseCase
from use_cases.list_expenses import ListExpensesUseCase

CURRENT_MONTH = datetime.now(timezone.utc).strftime("%Y-%m")


@pytest.fixture
def repo():
  return FakeExpenseRepository()


@pytest.fixture
def add_uc(repo):
  return AddExpenseUseCase(expense_repo=repo)


@pytest.fixture
def list_uc(repo):
  return ListExpensesUseCase(expense_repo=repo)


@pytest.mark.asyncio
async def test_returns_expenses_for_month(add_uc, list_uc):
  await add_uc.execute(
    guild_id="g1",
    channel_id="c1",
    category="Food",
    description="Pizza",
    value=Decimal("30.00"),
    author_id="u1",
    channel_members=["u1", "u2"],
  )
  await add_uc.execute(
    guild_id="g1",
    channel_id="c1",
    category="Transport",
    description="Taxi",
    value=Decimal("15.00"),
    author_id="u2",
    channel_members=["u1", "u2"],
  )

  result = await list_uc.execute(guild_id="g1", month=CURRENT_MONTH)
  assert len(result) == 2


@pytest.mark.asyncio
async def test_returns_empty_for_unknown_month(add_uc, list_uc):
  await add_uc.execute(
    guild_id="g1",
    channel_id="c1",
    category="Food",
    description="Pizza",
    value=Decimal("30.00"),
    author_id="u1",
    channel_members=["u1"],
  )

  result = await list_uc.execute(guild_id="g1", month="2000-01")
  assert result == []


@pytest.mark.asyncio
async def test_filters_by_guild(add_uc, list_uc):
  await add_uc.execute(
    guild_id="g1",
    channel_id="c1",
    category="Food",
    description="Pizza",
    value=Decimal("30.00"),
    author_id="u1",
    channel_members=["u1"],
  )
  await add_uc.execute(
    guild_id="g2",
    channel_id="c1",
    category="Food",
    description="Burger",
    value=Decimal("20.00"),
    author_id="u1",
    channel_members=["u1"],
  )

  result = await list_uc.execute(guild_id="g1", month=CURRENT_MONTH)
  assert len(result) == 1
  assert result[0].description == "Pizza"
