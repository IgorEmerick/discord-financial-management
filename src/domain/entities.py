from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass
class Expense:
  id: str
  guild_id: str
  channel_id: str
  category: str
  description: str
  value: Decimal
  paying_person: str
  involved_people: list[str]
  destination_month: str
  created_at: datetime
  updated_at: datetime


@dataclass
class Payment:
  id: str
  guild_id: str
  month: str
  creditor: str
  debtor: str
  amount: Decimal
  paid_at: datetime


@dataclass
class Balance:
  user_id: str
  net: Decimal


@dataclass
class Settlement:
  debtor: str
  creditor: str
  amount: Decimal


@dataclass
class Report:
  month: str
  expenses: list[Expense]
  balances: list[Balance]
  settlements: list[Settlement]
