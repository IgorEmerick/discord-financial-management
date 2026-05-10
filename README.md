# Pawments Bot

A Discord bot for shared expense management. Groups — roommates, travel companions, project teams — register expenses, generate monthly financial reports, and settle debts, all via Discord slash commands.

---

## Table of Contents

- [User Manual](#user-manual)
- [Developer Guide](#developer-guide)
- [Terms of Service](service-terms.md)
- [Privacy Policy](privacy-policy.md)

---

## User Manual

### Add to your server

[Click here to invite the bot](https://discord.com/oauth2/authorize?client_id=1502428671531679816&scope=bot+applications.commands&permissions=19456) to your Discord server.

---

### How it works

Add your shared expenses to a channel as they happen. At the end of the month, run `/report` to see who owes what, then use `/pay` to record the settlements.

The bot infers sensible defaults when you omit optional fields:
- **Payer** defaults to you (the command author)
- **Participants** default to all non-bot members currently in the channel
- **Month** defaults to the current calendar month (`YYYY-MM`)

---

### Commands

#### `/add-expense`
Register a shared expense.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `category` | ✅ | Category label, e.g. `Food`, `Transport`, `Utilities` |
| `description` | ✅ | Short description of the expense |
| `value` | ✅ | Amount paid, e.g. `85.50` |
| `paying_person` | ➖ | Who paid — defaults to you |
| `participants` | ➖ | Space-separated @mentions of who shares the cost — defaults to all channel members |
| `month` | ➖ | Month in `YYYY-MM` format — defaults to the current month |

**Example:**
```
/add-expense category:Food description:Pizza night value:90.00
/add-expense category:Utilities description:Internet bill value:120.00 paying_person:@Alice month:2025-05
```

---

#### `/edit-expense`
Edit any field of a previously registered expense by its ID.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `expense_id` | ✅ | ID of the expense to edit (shown in the confirmation embed) |
| `category` | ➖ | New category |
| `description` | ➖ | New description |
| `value` | ➖ | New amount |
| `paying_person` | ➖ | New payer |
| `participants` | ➖ | New space-separated @mentions of participants |
| `month` | ➖ | New month in `YYYY-MM` format |

**Example:**
```
/edit-expense expense_id:01JWXYZ description:Pizza + drinks value:105.00
```

---

#### `/delete-expense`
Delete a previously registered expense by its ID.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `expense_id` | ✅ | ID of the expense to delete |

**Example:**
```
/delete-expense expense_id:01JWXYZ
```

---

#### `/report`
Generate a monthly financial report showing per-person balances and recommended payments to settle all debts.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `month` | ➖ | Month in `YYYY-MM` format — defaults to the current month |

**Example:**
```
/report
/report month:2025-04
```

---

#### `/expenses`
Export all expenses for a month as a file attachment. Defaults to `.txt`; pass `format:csv` to get a `.csv` file instead. Payer and participant names are resolved to their Discord display names.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `month` | ➖ | Month in `YYYY-MM` format — defaults to the current month |
| `format` | ➖ | File format: `txt` (default) or `csv` |

**Example:**
```
/expenses
/expenses month:2025-04
/expenses month:2025-04 format:csv
```

---

#### `/pay`
Record that a payment was made to settle a balance. If creditor and debtor are both omitted, all outstanding balances for the month are settled at once.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `creditor` | ➖ | Who is owed money |
| `debtor` | ➖ | Who owes money |
| `month` | ➖ | Month in `YYYY-MM` format — defaults to the current month |

**Example:**
```
/pay                                          # settle all balances for the current month
/pay creditor:@Alice debtor:@Bob              # settle only Alice ← Bob
/pay creditor:@Alice debtor:@Bob month:2025-04
```

---

#### `/delete-my-data`

> **⚠️ This action is permanent and cannot be undone.**

Permanently deletes all your expense and payment records in the current server. Responds with a `.txt` file listing everything that was removed, so you have a record before it is gone.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `confirm` | ➖ | Must be set to `True` to execute — defaults to `False` |

If `confirm` is omitted or `False`, the bot shows a warning without deleting anything.

**Example:**
```
/delete-my-data                  # shows a warning, nothing is deleted
/delete-my-data confirm:True     # permanently deletes all your data
```

---

#### `/help`
Display all available commands with their parameters. No database access required.

```
/help
```

---

## Developer Guide

### Prerequisites

- Python 3.12+
- PostgreSQL 16+ (or Docker)
- A Discord application with a bot token — create one at [discord.com/developers](https://discord.com/developers/applications)

Enable the following bot intents in the Discord Developer Portal: **Server Members Intent** and **Message Content Intent**.

---

### Running locally

```bash
# 1. Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.lock

# 3. Configure environment
cp .env.example .env
# Edit .env and fill in DISCORD_BOT_TOKEN and POSTGRES_PASSWORD

# 4. Start the bot
python src/main.py
```

---

### Running with Docker

```bash
cp .env.example .env
# Edit .env and fill in DISCORD_BOT_TOKEN and POSTGRES_PASSWORD

docker compose up --build
```

This starts two services: `app` (the bot) and `db` (PostgreSQL 16). The app builds its database connection from the `POSTGRES_*` variables; `POSTGRES_HOST` is set to the internal `db` service by Compose. The app waits for the database health check before connecting.

---

### Running in production

Create a `.env.prod` file with your production credentials (it is gitignored):

```bash
DISCORD_BOT_TOKEN=your-production-token
POSTGRES_PASSWORD=strong-password
POSTGRES_USER=postgres       # optional, default: postgres
POSTGRES_DB=expenses         # optional, default: expenses
```

Then deploy with:

```bash
docker compose --env-file .env.prod up -d
```

---

### Project structure

```
src/
  main.py                        # Entry point
  container.py                   # Dependency injection container
  bot/
    expense_cog.py               # Discord slash command handlers
    embeds.py                    # Discord embed builders
    files.py                     # File attachment generators (TXT, CSV)
  db/
    pool.py                      # asyncpg connection pool + schema init
    schema.sql                   # Table definitions
  domain/
    entities.py                  # Dataclasses: Expense, Payment, Balance, Settlement, Report
    errors.py                    # Domain exceptions
    services.py                  # Balance computation and settlement algorithm
  repositories/
    protocols.py                 # Repository interfaces (structural typing)
    postgres/
      postgres_expense_repository.py
      postgres_payment_repository.py
  use_cases/
    add_expense.py
    edit_expense.py
    delete_expense.py
    delete_user_data.py
    generate_report.py
    list_expenses.py
    register_payment.py
tests/
  fakes/
    repositories.py              # In-memory repository implementations for tests
  use_cases/                     # Unit tests for all use cases
```

The architecture follows a clean layered approach: Discord commands call use cases, use cases call repositories, repositories talk to PostgreSQL. The dependency graph is wired in `container.py` using `dependency-injector`.

---

### Testing

```bash
pytest
```

Every new feature must have automated tests. Unit tests use in-memory fake repositories — no database required.

---

### Linting and formatting

```bash
ruff check .        # lint
ruff check . --fix  # lint with auto-fix
ruff format .       # format
```

2-space indent, 120-character line length.

---

### Environment variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DISCORD_BOT_TOKEN` | ✅ | — | Bot token from the Discord Developer Portal |
| `POSTGRES_PASSWORD` | ✅ | — | PostgreSQL password |
| `POSTGRES_USER` | ➖ | `postgres` | PostgreSQL user |
| `POSTGRES_DB` | ➖ | `expenses` | PostgreSQL database name |
| `POSTGRES_HOST` | ➖ | `localhost` | PostgreSQL host (set to `db` automatically by Compose) |
| `POSTGRES_PORT` | ➖ | `5432` | PostgreSQL port |

Copy `.env.example` to `.env` and fill in the required values. Both `.env`, `.env.prod`, and `.envrc` are gitignored.
