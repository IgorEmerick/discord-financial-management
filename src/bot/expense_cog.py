import logging
import re
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation

import discord
from discord import app_commands
from discord.ext import commands

from bot import embeds
from domain.errors import (
  ExpenseNotFoundError,
  InvalidExpenseValueError,
  NoEditFieldsProvidedError,
  NothingToSettleError,
)
from use_cases.add_expense import AddExpenseUseCase
from use_cases.delete_expense import DeleteExpenseUseCase
from use_cases.edit_expense import EditExpenseUseCase
from use_cases.generate_report import GenerateReportUseCase
from use_cases.register_payment import RegisterPaymentUseCase

logger = logging.getLogger(__name__)

_MENTION_RE = re.compile(r"<@!?(\d+)>")


class ExpensesCog(commands.Cog):
  def __init__(
    self,
    add_expense_uc: AddExpenseUseCase,
    edit_expense_uc: EditExpenseUseCase,
    delete_expense_uc: DeleteExpenseUseCase,
    generate_report_uc: GenerateReportUseCase,
    register_payment_uc: RegisterPaymentUseCase,
  ) -> None:
    self._add_expense = add_expense_uc
    self._edit_expense = edit_expense_uc
    self._delete_expense = delete_expense_uc
    self._generate_report = generate_report_uc
    self._register_payment = register_payment_uc

  def _current_month(self) -> str:
    return datetime.now(UTC).strftime("%Y-%m")

  def _parse_participants(self, raw: str) -> list[str]:
    return _MENTION_RE.findall(raw)

  def _channel_member_ids(self, interaction: discord.Interaction) -> list[str]:
    channel = interaction.channel
    if isinstance(channel, discord.TextChannel):
      return [str(m.id) for m in channel.members if not m.bot]
    return [str(interaction.user.id)]

  @app_commands.command(name="add-expense", description="Register a shared expense")
  @app_commands.describe(
    category="Expense category (e.g. Food, Transport, Utilities)",
    description="Short description of the expense",
    value="Amount paid (e.g. 85.50)",
    paying_person="Who paid — defaults to you",
    participants="Space-separated mentions of participants — defaults to all channel members",
    month="Month in YYYY-MM format — defaults to current month",
  )
  async def add_expense(
    self,
    interaction: discord.Interaction,
    category: str,
    description: str,
    value: str,
    paying_person: discord.Member | None = None,
    participants: str | None = None,
    month: str | None = None,
  ) -> None:
    await interaction.response.defer()
    guild_id = str(interaction.guild_id)
    channel_id = str(interaction.channel_id)
    author_id = str(interaction.user.id)
    channel_members = self._channel_member_ids(interaction)
    resolved_payer = str(paying_person.id) if paying_person else None
    resolved_participants = self._parse_participants(participants) if participants else None

    logger.info(
      "add-expense guild=%s channel=%s author=%s category=%r value=%s payer=%s participants=%s month=%s",
      guild_id,
      channel_id,
      author_id,
      category,
      value,
      resolved_payer,
      resolved_participants,
      month,
    )

    try:
      parsed_value = Decimal(value)
    except InvalidOperation:
      await interaction.followup.send(
        embed=embeds.error("Invalid Value", f"`{value}` is not a valid number. Use a decimal like `85.50` or `120`.")
      )
      return

    try:
      expense = await self._add_expense.execute(
        guild_id=guild_id,
        channel_id=channel_id,
        category=category,
        description=description,
        value=parsed_value,
        author_id=author_id,
        channel_members=channel_members,
        paying_person=resolved_payer,
        involved_people=resolved_participants,
        destination_month=month,
      )
      await interaction.followup.send(embed=embeds.expense_added(expense))
    except InvalidExpenseValueError:
      await interaction.followup.send(embed=embeds.error("Invalid Value", "Expense value must be greater than zero."))
    except Exception:
      logger.exception("add-expense failed")
      await interaction.followup.send(
        embed=embeds.error("Error", "Could not save the expense. Please try again later.")
      )

  @app_commands.command(name="edit-expense", description="Edit a previously registered expense")
  @app_commands.describe(
    expense_id="ID of the expense to edit",
    category="New category",
    description="New description",
    value="New amount",
    paying_person="New payer",
    participants="New space-separated participant mentions",
    month="New month in YYYY-MM format",
  )
  async def edit_expense(
    self,
    interaction: discord.Interaction,
    expense_id: str,
    category: str | None = None,
    description: str | None = None,
    value: str | None = None,
    paying_person: discord.Member | None = None,
    participants: str | None = None,
    month: str | None = None,
  ) -> None:
    await interaction.response.defer()
    guild_id = str(interaction.guild_id)
    resolved_payer = str(paying_person.id) if paying_person else None
    resolved_participants = self._parse_participants(participants) if participants else None

    logger.info(
      "edit-expense guild=%s author=%s id=%s category=%r value=%s payer=%s participants=%s month=%s",
      guild_id,
      interaction.user.id,
      expense_id,
      category,
      value,
      resolved_payer,
      resolved_participants,
      month,
    )

    parsed_value: Decimal | None = None
    if value is not None:
      try:
        parsed_value = Decimal(value)
      except InvalidOperation:
        await interaction.followup.send(
          embed=embeds.error("Invalid Value", f"`{value}` is not a valid number. Use a decimal like `85.50` or `120`.")
        )
        return

    try:
      expense = await self._edit_expense.execute(
        expense_id=expense_id,
        category=category,
        description=description,
        value=parsed_value,
        paying_person=resolved_payer,
        involved_people=resolved_participants,
        destination_month=month,
      )
      await interaction.followup.send(embed=embeds.expense_edited(expense))
    except NoEditFieldsProvidedError:
      await interaction.followup.send(embed=embeds.error("Nothing to Edit", "Provide at least one field to update."))
    except InvalidExpenseValueError:
      await interaction.followup.send(embed=embeds.error("Invalid Value", "Expense value must be greater than zero."))
    except ExpenseNotFoundError:
      await interaction.followup.send(embed=embeds.error("Not Found", f"No expense with ID `{expense_id}`."))
    except Exception:
      logger.exception("edit-expense failed")
      await interaction.followup.send(
        embed=embeds.error("Error", "Could not update the expense. Please try again later.")
      )

  @app_commands.command(name="delete-expense", description="Delete a previously registered expense")
  @app_commands.describe(expense_id="ID of the expense to delete")
  async def delete_expense(self, interaction: discord.Interaction, expense_id: str) -> None:
    await interaction.response.defer()
    logger.info("delete-expense guild=%s author=%s id=%s", interaction.guild_id, interaction.user.id, expense_id)

    try:
      await self._delete_expense.execute(expense_id=expense_id)
      await interaction.followup.send(embed=embeds.expense_deleted(expense_id))
    except ExpenseNotFoundError:
      await interaction.followup.send(embed=embeds.error("Not Found", f"No expense with ID `{expense_id}`."))
    except Exception:
      logger.exception("delete-expense failed")
      await interaction.followup.send(
        embed=embeds.error("Error", "Could not delete the expense. Please try again later.")
      )

  @app_commands.command(name="report", description="Generate a monthly financial report")
  @app_commands.describe(month="Month in YYYY-MM format — defaults to current month")
  async def report(self, interaction: discord.Interaction, month: str | None = None) -> None:
    await interaction.response.defer()
    guild_id = str(interaction.guild_id)
    resolved_month = month or self._current_month()
    logger.info("report guild=%s author=%s month=%s", guild_id, interaction.user.id, resolved_month)

    try:
      result = await self._generate_report.execute(guild_id=guild_id, month=resolved_month)
      await interaction.followup.send(embed=embeds.monthly_report(result))
    except Exception:
      logger.exception("report failed")
      await interaction.followup.send(
        embed=embeds.error("Error", "Could not generate the report. Please try again later.")
      )

  @app_commands.command(name="pay", description="Register a payment to settle balances")
  @app_commands.describe(
    creditor="Who is owed money — omit to settle all outstanding balances",
    debtor="Who owes money — omit to settle all outstanding balances",
    month="Month in YYYY-MM format — defaults to current month",
  )
  async def pay(
    self,
    interaction: discord.Interaction,
    creditor: discord.Member | None = None,
    debtor: discord.Member | None = None,
    month: str | None = None,
  ) -> None:
    await interaction.response.defer()
    guild_id = str(interaction.guild_id)
    resolved_month = month or self._current_month()
    resolved_creditor = str(creditor.id) if creditor else None
    resolved_debtor = str(debtor.id) if debtor else None
    logger.info(
      "pay guild=%s author=%s creditor=%s debtor=%s month=%s",
      guild_id,
      interaction.user.id,
      resolved_creditor,
      resolved_debtor,
      resolved_month,
    )

    try:
      payments = await self._register_payment.execute(
        guild_id=guild_id,
        month=resolved_month,
        creditor=resolved_creditor,
        debtor=resolved_debtor,
      )
      await interaction.followup.send(embed=embeds.payments_registered(payments))
    except NothingToSettleError:
      await interaction.followup.send(
        embed=embeds.error("Nothing to Settle", f"No outstanding balances for {resolved_month}.")
      )
    except Exception:
      logger.exception("pay failed")
      await interaction.followup.send(
        embed=embeds.error("Error", "Could not register the payment. Please try again later.")
      )

  @app_commands.command(name="help", description="Show all available commands")
  async def help_command(self, interaction: discord.Interaction) -> None:
    logger.info("help guild=%s author=%s", interaction.guild_id, interaction.user.id)
    await interaction.response.send_message(embed=embeds.help_info())
