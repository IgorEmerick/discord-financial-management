import csv
import io

from domain.entities import Expense, Payment


def _name(uid: str, user_names: dict[str, str]) -> str:
  return user_names.get(uid, uid)


def expenses_txt(expenses: list[Expense], month: str, user_names: dict[str, str] | None = None) -> io.BytesIO:
  names = user_names or {}
  buf = io.StringIO()
  buf.write(f"Expenses — {month}\n")
  buf.write("=" * 40 + "\n\n")
  for i, e in enumerate(expenses, 1):
    participants = ", ".join(_name(uid, names) for uid in e.involved_people)
    buf.write(f"{i}. [{e.category}] {e.description}\n")
    buf.write(f"   Value: ${e.value:.2f} | Paid by: {_name(e.paying_person, names)}\n")
    buf.write(f"   Participants: {participants}\n")
    buf.write(f"   Added: {e.created_at.strftime('%Y-%m-%d %H:%M UTC')}\n")
    buf.write(f"   ID: {e.id}\n\n")
  return io.BytesIO(buf.getvalue().encode())


def deleted_user_data_txt(
  expenses: list[Expense],
  payments: list[Payment],
  guild_name: str,
  user_name: str,
  user_names: dict[str, str] | None = None,
) -> io.BytesIO:
  names = user_names or {}
  buf = io.StringIO()
  buf.write(f"Deleted Data — {user_name} — Server: {guild_name}\n")
  buf.write("=" * 50 + "\n\n")

  buf.write(f"EXPENSES ({len(expenses)})\n")
  buf.write("-" * 30 + "\n")
  if expenses:
    for i, e in enumerate(expenses, 1):
      participants = ", ".join(_name(uid, names) for uid in e.involved_people)
      buf.write(f"{i}. [{e.category}] {e.description} — {e.destination_month}\n")
      buf.write(f"   Value: ${e.value:.2f} | Paid by: {_name(e.paying_person, names)}\n")
      buf.write(f"   Participants: {participants}\n")
      buf.write(f"   Added: {e.created_at.strftime('%Y-%m-%d %H:%M UTC')}\n")
      buf.write(f"   ID: {e.id}\n\n")
  else:
    buf.write("No expenses found.\n\n")

  buf.write(f"PAYMENT RECORDS ({len(payments)})\n")
  buf.write("-" * 30 + "\n")
  if payments:
    for i, p in enumerate(payments, 1):
      buf.write(f"{i}. {_name(p.debtor, names)} → {_name(p.creditor, names)}: ${p.amount:.2f} ({p.month})\n")
      buf.write(f"   ID: {p.id}\n\n")
  else:
    buf.write("No payment records found.\n\n")

  return io.BytesIO(buf.getvalue().encode())


def expenses_csv(expenses: list[Expense], month: str, user_names: dict[str, str] | None = None) -> io.BytesIO:
  names = user_names or {}
  buf = io.StringIO()
  writer = csv.writer(buf)
  writer.writerow(["id", "category", "description", "value", "paying_person", "participants", "month", "created_at"])
  for e in expenses:
    writer.writerow(
      [
        e.id,
        e.category,
        e.description,
        f"{e.value:.2f}",
        _name(e.paying_person, names),
        ",".join(_name(uid, names) for uid in e.involved_people),
        e.destination_month,
        e.created_at.isoformat(),
      ]
    )
  return io.BytesIO(buf.getvalue().encode())
