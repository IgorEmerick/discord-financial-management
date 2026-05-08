from decimal import Decimal

from domain.entities import Expense, Payment, Settlement

_ZERO = Decimal(0)


def compute_net_balances(expenses: list[Expense], payments: list[Payment]) -> dict[str, Decimal]:
  net: dict[str, Decimal] = {}

  for expense in expenses:
    share = expense.value / Decimal(len(expense.involved_people))
    net[expense.paying_person] = net.get(expense.paying_person, _ZERO) + expense.value
    for person in expense.involved_people:
      net[person] = net.get(person, _ZERO) - share

  for payment in payments:
    net[payment.creditor] = net.get(payment.creditor, _ZERO) - payment.amount
    net[payment.debtor] = net.get(payment.debtor, _ZERO) + payment.amount

  return net


def compute_settlements(net: dict[str, Decimal]) -> list[Settlement]:
  creditors = sorted([(amount, uid) for uid, amount in net.items() if amount > _ZERO], reverse=True)
  debtors = sorted([(-amount, uid) for uid, amount in net.items() if amount < _ZERO], reverse=True)

  settlements = []
  i, j = 0, 0
  while i < len(creditors) and j < len(debtors):
    credit_amount, creditor = creditors[i]
    debt_amount, debtor = debtors[j]
    amount = min(credit_amount, debt_amount)
    settlements.append(Settlement(debtor=debtor, creditor=creditor, amount=amount))
    creditors[i] = (credit_amount - amount, creditor)
    debtors[j] = (debt_amount - amount, debtor)
    if creditors[i][0] == _ZERO:
      i += 1
    if debtors[j][0] == _ZERO:
      j += 1

  return settlements
