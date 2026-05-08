class ExpenseNotFoundError(Exception):
  def __init__(self, expense_id: str) -> None:
    super().__init__(f"Expense '{expense_id}' not found")
    self.expense_id = expense_id


class NoEditFieldsProvidedError(Exception):
  def __init__(self) -> None:
    super().__init__("At least one field must be provided to edit an expense")


class InvalidExpenseValueError(Exception):
  def __init__(self, value: object) -> None:
    super().__init__(f"Expense value must be a positive decimal, got {value}")


class NothingToSettleError(Exception):
  def __init__(self, month: str) -> None:
    super().__init__(f"No outstanding balances to settle for month {month}")
