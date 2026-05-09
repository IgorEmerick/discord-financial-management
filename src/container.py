from dependency_injector import containers, providers

from repositories.postgres.postgres_expense_repository import PostgresExpenseRepository
from repositories.postgres.postgres_payment_repository import PostgresPaymentRepository
from use_cases.add_expense import AddExpenseUseCase
from use_cases.delete_expense import DeleteExpenseUseCase
from use_cases.edit_expense import EditExpenseUseCase
from use_cases.generate_report import GenerateReportUseCase
from use_cases.list_expenses import ListExpensesUseCase
from use_cases.register_payment import RegisterPaymentUseCase


class Container(containers.DeclarativeContainer):
  pool = providers.Dependency()

  expense_repo = providers.Singleton(PostgresExpenseRepository, pool=pool)
  payment_repo = providers.Singleton(PostgresPaymentRepository, pool=pool)

  add_expense_uc = providers.Factory(AddExpenseUseCase, expense_repo=expense_repo)
  edit_expense_uc = providers.Factory(EditExpenseUseCase, expense_repo=expense_repo)
  delete_expense_uc = providers.Factory(DeleteExpenseUseCase, expense_repo=expense_repo)

  list_expenses_uc = providers.Factory(ListExpensesUseCase, expense_repo=expense_repo)

  generate_report_uc = providers.Factory(
    GenerateReportUseCase,
    expense_repo=expense_repo,
    payment_repo=payment_repo,
  )
  register_payment_uc = providers.Factory(
    RegisterPaymentUseCase,
    expense_repo=expense_repo,
    payment_repo=payment_repo,
  )
