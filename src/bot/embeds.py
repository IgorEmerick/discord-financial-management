from decimal import Decimal

import discord

from domain.entities import Expense, Payment, Report

_GREEN = discord.Color.green()
_RED = discord.Color.red()
_BLUE = discord.Color.blue()


def expense_added(expense: Expense) -> discord.Embed:
  embed = discord.Embed(title="Expense Added", color=_GREEN)
  embed.add_field(name="ID", value=f"`{expense.id}`", inline=False)
  embed.add_field(name="Category", value=expense.category)
  embed.add_field(name="Description", value=expense.description)
  embed.add_field(name="Value", value=f"${expense.value:.2f}")
  embed.add_field(name="Paid by", value=f"<@{expense.paying_person}>")
  embed.add_field(name="Month", value=expense.destination_month)
  embed.add_field(name="Participants", value=" ".join(f"<@{p}>" for p in expense.involved_people), inline=False)
  return embed


def expense_edited(expense: Expense) -> discord.Embed:
  embed = discord.Embed(title="Expense Updated", color=_GREEN)
  embed.add_field(name="ID", value=f"`{expense.id}`", inline=False)
  embed.add_field(name="Category", value=expense.category)
  embed.add_field(name="Description", value=expense.description)
  embed.add_field(name="Value", value=f"${expense.value:.2f}")
  embed.add_field(name="Paid by", value=f"<@{expense.paying_person}>")
  embed.add_field(name="Month", value=expense.destination_month)
  embed.add_field(name="Participants", value=" ".join(f"<@{p}>" for p in expense.involved_people), inline=False)
  return embed


def expense_deleted(expense_id: str) -> discord.Embed:
  embed = discord.Embed(title="Expense Deleted", color=_GREEN)
  embed.description = f"Expense `{expense_id}` has been deleted."
  return embed


def monthly_report(report: Report) -> discord.Embed:
  embed = discord.Embed(title=f"Report — {report.month}", color=_BLUE)

  if report.expenses:
    lines = [
      f"`{e.id[:10]}…` **{e.description}** — ${e.value:.2f} (paid by <@{e.paying_person}>)"
      for e in report.expenses
    ]
    embed.add_field(name="Expenses", value="\n".join(lines), inline=False)
  else:
    embed.add_field(name="Expenses", value="No expenses this month.", inline=False)

  if report.balances:
    lines = []
    for b in report.balances:
      label = f"owes ${abs(b.net):.2f}" if b.net < Decimal(0) else f"is owed ${b.net:.2f}"
      lines.append(f"<@{b.user_id}> {label}")
    embed.add_field(name="Balances", value="\n".join(lines), inline=False)

  if report.settlements:
    lines = [f"<@{s.debtor}> → <@{s.creditor}>: ${s.amount:.2f}" for s in report.settlements]
    embed.add_field(name="Recommended Settlements", value="\n".join(lines), inline=False)

  return embed


def payments_registered(payments: list[Payment]) -> discord.Embed:
  embed = discord.Embed(title="Payments Registered", color=_GREEN)
  lines = [f"<@{p.debtor}> → <@{p.creditor}>: ${p.amount:.2f}" for p in payments]
  embed.description = "\n".join(lines)
  return embed


def error(title: str, description: str) -> discord.Embed:
  return discord.Embed(title=title, description=description, color=_RED)


def help_info() -> discord.Embed:
  embed = discord.Embed(title="Expense Bot — Commands", color=_BLUE)
  embed.add_field(
    name="/add-expense",
    value=(
      "Register a shared expense.\n"
      "**Required:** `category`, `description`, `value`\n"
      "**Optional:** `paying_person` (defaults to you), `participants` (defaults to channel members),"
      " `month` (defaults to current)"
    ),
    inline=False,
  )
  embed.add_field(
    name="/edit-expense",
    value=(
      "Edit a previously registered expense.\n"
      "**Required:** `expense_id`\n"
      "**Optional:** `category`, `description`, `value`, `paying_person`, `participants`, `month`"
    ),
    inline=False,
  )
  embed.add_field(
    name="/delete-expense",
    value="Delete a previously registered expense.\n**Required:** `expense_id`",
    inline=False,
  )
  embed.add_field(
    name="/report",
    value="Generate a monthly financial report.\n**Optional:** `month` (defaults to current month)",
    inline=False,
  )
  embed.add_field(
    name="/pay",
    value=(
      "Register a payment to settle balances.\n"
      "**Optional:** `creditor`, `debtor`, `month` — omit creditor and debtor to settle all outstanding balances"
    ),
    inline=False,
  )
  embed.add_field(name="/help", value="Show this message.", inline=False)
  embed.set_footer(text="Month format: YYYY-MM  •  e.g. 2025-05")
  return embed
