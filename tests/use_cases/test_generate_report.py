from datetime import UTC, datetime
from decimal import Decimal

import pytest

from domain.entities import Expense
from fakes.repositories import FakeExpenseRepository, FakePaymentRepository
from use_cases.generate_report import GenerateReportUseCase

FIXED_NOW = datetime(2025, 5, 7, 10, 0, 0, tzinfo=UTC)


async def _seed_expense(
  repo: FakeExpenseRepository,
  *,
  expense_id: str,
  guild_id: str = "g1",
  value: Decimal,
  paying_person: str,
  involved_people: list[str],
  destination_month: str = "2025-05",
) -> None:
  await repo.save(
    Expense(
      id=expense_id,
      guild_id=guild_id,
      channel_id="c1",
      category="Food",
      description="Pizza",
      value=value,
      paying_person=paying_person,
      involved_people=involved_people,
      destination_month=destination_month,
      created_at=FIXED_NOW,
      updated_at=FIXED_NOW,
    )
  )


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
  await _seed_expense(
    expense_repo,
    expense_id="exp-1",
    value=Decimal("90.00"),
    paying_person="user1",
    involved_people=["user1", "user2", "user3"],
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
  await _seed_expense(
    expense_repo,
    expense_id="exp-1",
    value=Decimal("90.00"),
    paying_person="user1",
    involved_people=["user1", "user2", "user3"],
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
  await _seed_expense(
    expense_repo,
    expense_id="exp-1",
    guild_id="other-guild",
    value=Decimal("50.00"),
    paying_person="user1",
    involved_people=["user1"],
  )

  report = await report_use_case.execute(guild_id="g1", month="2025-05")
  assert report.expenses == []


@pytest.mark.asyncio
async def test_excludes_expenses_from_other_months(
  expense_repo: FakeExpenseRepository, report_use_case: GenerateReportUseCase
) -> None:
  await _seed_expense(
    expense_repo,
    expense_id="exp-1",
    value=Decimal("50.00"),
    paying_person="user1",
    involved_people=["user1"],
    destination_month="2025-04",
  )

  report = await report_use_case.execute(guild_id="g1", month="2025-05")
  assert report.expenses == []
