import csv
import io

from domain.entities import Expense


def expenses_txt(expenses: list[Expense], month: str) -> io.BytesIO:
  buf = io.StringIO()
  buf.write(f"Expenses — {month}\n")
  buf.write("=" * 40 + "\n\n")
  for i, e in enumerate(expenses, 1):
    participants = ", ".join(e.involved_people)
    buf.write(f"{i}. [{e.category}] {e.description}\n")
    buf.write(f"   Value: ${e.value:.2f} | Paid by: {e.paying_person}\n")
    buf.write(f"   Participants: {participants}\n")
    buf.write(f"   ID: {e.id}\n\n")
  return io.BytesIO(buf.getvalue().encode())


def expenses_csv(expenses: list[Expense], month: str) -> io.BytesIO:
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
        e.paying_person,
        ",".join(e.involved_people),
        e.destination_month,
        e.created_at.isoformat(),
      ]
    )
  return io.BytesIO(buf.getvalue().encode())
