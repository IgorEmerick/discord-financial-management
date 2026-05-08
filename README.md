# Discord Financial Management

A Discord bot for shared expense management. Groups — roommates, travel companions, project teams — register expenses, generate monthly financial reports, and settle debts, all via Discord slash commands.

---

## Table of Contents

- [User Manual](#user-manual)
- [Developer Guide](#developer-guide)

---

## User Manual

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
Generate a monthly financial report showing all expenses, per-person balances, and recommended payments to settle all debts.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `month` | ➖ | Month in `YYYY-MM` format — defaults to the current month |

**Example:**
```
/report
/report month:2025-04
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
# Edit .env and fill in DISCORD_BOT_TOKEN and DATABASE_URL

# 4. Start the bot
python src/main.py
```

---

### Running with Docker

Only `DISCORD_BOT_TOKEN` is needed in `.env` — `DATABASE_URL` is handled internally by Docker Compose.

```bash
cp .env.example .env
# Edit .env and fill in DISCORD_BOT_TOKEN

docker compose up --build
```

This starts two services: `app` (the bot) and `db` (PostgreSQL 16). The app waits for the database health check before connecting.

---

### Project structure

```
src/
  main.py                        # Entry point
  container.py                   # Dependency injection container
  bot/
    expense_cog.py               # Discord slash command handlers
    embeds.py                    # Discord embed builders
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
    generate_report.py
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

| Variable | Description |
|----------|-------------|
| `DISCORD_BOT_TOKEN` | Bot token from the Discord Developer Portal |
| `DATABASE_URL` | PostgreSQL connection string, e.g. `postgresql://user:password@localhost:5432/dbname` |

Copy `.env.example` to `.env` and fill in the values. Both `.env` and `.envrc` are gitignored.
