from datetime import UTC, datetime
from decimal import Decimal

import pytest

from tests.fakes.repositories import FakeExpenseRepository, FakePaymentRepository
from use_cases.add_expense import AddExpenseUseCase
from use_cases.generate_report import GenerateReportUseCase

FIXED_NOW = datetime(2025, 5, 7, 10, 0, 0, tzinfo=UTC)


def _add_use_case(repo: FakeExpenseRepository, expense_id: str) -> AddExpenseUseCase:
  return AddExpenseUseCase(expense_repo=repo, clock=lambda: FIXED_NOW, id_generator=lambda: expense_id)


@pytest.fixture
def expense_repo() -> FakeExpenseRepository:
  return FakeExpenseRepository()


@pytest.fixture
def payment_repo() -> FakePaymentRepository:
  return FakePaymentRepository()


@pytest.fixture
def report_use_case(expense_repo: FakeExpenseRepository, payment_repo: FakePaymentRepository) -> GenerateReportUseCase:
  return GenerateReportUseCase(expense_repo=expense_repo, payment_repo=payment_repo)


@pytest.mark.asyncio
async def test_empty_month_returns_empty_report(report_use_case: GenerateReportUseCase) -> None:
  report = await report_use_case.execute(guild_id="g1", month="2025-05")
  assert report.expenses == []
  assert report.balances == []
  assert report.settlements == []


@pytest.mark.asyncio
async def test_single_expense_splits_equally(
  expense_repo: FakeExpenseRepository, report_use_case: GenerateReportUseCase
) -> None:
  await _add_use_case(expense_repo, "exp-1").execute(
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

  report = await report_use_case.execute(guild_id="g1", month="2025-05")
  net = {b.user_id: b.net for b in report.balances}

  assert net["user1"] == Decimal("60.00")
  assert net["user2"] == Decimal("-30.00")
  assert net["user3"] == Decimal("-30.00")


@pytest.mark.asyncio
async def test_settlements_zero_out_all_balances(
  expense_repo: FakeExpenseRepository, report_use_case: GenerateReportUseCase
) -> None:
  await _add_use_case(expense_repo, "exp-1").execute(
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

  report = await report_use_case.execute(guild_id="g1", month="2025-05")
  residual = {b.user_id: b.net for b in report.balances}
  for s in report.settlements:
    residual[s.creditor] -= s.amount
    residual[s.debtor] += s.amount

  for remaining in residual.values():
    assert abs(remaining) < Decimal("0.01")


@pytest.mark.asyncio
async def test_excludes_expenses_from_other_guilds(
  expense_repo: FakeExpenseRepository, report_use_case: GenerateReportUseCase
) -> None:
  await _add_use_case(expense_repo, "exp-1").execute(
    guild_id="other-guild",
    channel_id="c1",
    category="Food",
    description="Pizza",
    value=Decimal("50.00"),
    author_id="user1",
    channel_members=["user1"],
    destination_month="2025-05",
  )

  report = await report_use_case.execute(guild_id="g1", month="2025-05")
  assert report.expenses == []


@pytest.mark.asyncio
async def test_excludes_expenses_from_other_months(
  expense_repo: FakeExpenseRepository, report_use_case: GenerateReportUseCase
) -> None:
  await _add_use_case(expense_repo, "exp-1").execute(
    guild_id="g1",
    channel_id="c1",
    category="Food",
    description="Pizza",
    value=Decimal("50.00"),
    author_id="user1",
    channel_members=["user1"],
    destination_month="2025-04",
  )

  report = await report_use_case.execute(guild_id="g1", month="2025-05")
  assert report.expenses == []
