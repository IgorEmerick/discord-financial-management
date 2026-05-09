from datetime import UTC, datetime
from decimal import Decimal
from unittest.mock import patch

import pytest
from fakes.repositories import FakeExpenseRepository

from domain.entities import Expense
from domain.errors import ExpenseNotFoundError, InvalidExpenseValueError, NoEditFieldsProvidedError
from use_cases.edit_expense import EditExpenseUseCase

CREATED_AT = datetime(2025, 5, 7, 10, 0, 0, tzinfo=UTC)
UPDATED_AT = datetime(2025, 5, 7, 12, 0, 0, tzinfo=UTC)


@pytest.fixture
def repo() -> FakeExpenseRepository:
  return FakeExpenseRepository()


@pytest.fixture
def edit_use_case(repo: FakeExpenseRepository) -> EditExpenseUseCase:
  return EditExpenseUseCase(expense_repo=repo)


@pytest.fixture
async def existing_expense(repo: FakeExpenseRepository) -> Expense:
  expense = Expense(
    id="exp-1",
    guild_id="g1",
    channel_id="c1",
    category="Food",
    description="Pizza",
    value=Decimal("90.00"),
    paying_person="user1",
    involved_people=["user1", "user2"],
    destination_month="2025-05",
    created_at=CREATED_AT,
    updated_at=CREATED_AT,
  )
  await repo.save(expense)
  return expense


@pytest.mark.asyncio
async def test_edit_single_field(edit_use_case: EditExpenseUseCase, existing_expense: Expense) -> None:
  with patch.object(edit_use_case, "_utcnow", return_value=UPDATED_AT):
    updated = await edit_use_case.execute(expense_id="exp-1", description="Pizza + drinks")
  assert updated.description == "Pizza + drinks"
  assert updated.category == "Food"
  assert updated.updated_at == UPDATED_AT
  assert updated.created_at == CREATED_AT


@pytest.mark.asyncio
async def test_edit_multiple_fields(edit_use_case: EditExpenseUseCase, existing_expense: Expense) -> None:
  updated = await edit_use_case.execute(expense_id="exp-1", description="Updated", value=Decimal("102.00"))
  assert updated.description == "Updated"
  assert updated.value == Decimal("102.00")


@pytest.mark.asyncio
async def test_raises_when_expense_not_found(edit_use_case: EditExpenseUseCase) -> None:
  with pytest.raises(ExpenseNotFoundError):
    await edit_use_case.execute(expense_id="nonexistent", description="x")


@pytest.mark.asyncio
async def test_raises_when_no_fields_provided(edit_use_case: EditExpenseUseCase, existing_expense: Expense) -> None:
  with pytest.raises(NoEditFieldsProvidedError):
    await edit_use_case.execute(expense_id="exp-1")


@pytest.mark.asyncio
async def test_raises_on_non_positive_value(edit_use_case: EditExpenseUseCase, existing_expense: Expense) -> None:
  with pytest.raises(InvalidExpenseValueError):
    await edit_use_case.execute(expense_id="exp-1", value=Decimal("0"))
