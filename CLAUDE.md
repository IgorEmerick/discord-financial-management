# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

A Discord bot for shared expense management. Groups (roommates, travel companions, etc.) register expenses, generate monthly financial reports, and settle payments — all via Discord slash commands.

### Commands

| Command | Description |
|---------|-------------|
| `/add-expense` | Register a shared expense (category, description, value, payer, participants, month) |
| `/edit-expense` | Edit any field of a previously registered expense by its ID |
| `/delete-expense` | Delete a previously registered expense by its ID |
| `/report` | Generate a monthly report with itemized expenses and creditor/debtor balances |
| `/pay` | Register a payment between a creditor and debtor; if both are omitted, settles all outstanding balances for the month |
| `/help` | Display all available commands with descriptions, parameters, and usage examples (stateless, no DB access) |

### Field Inference (auto-resolved when omitted)

- **Payer** → command author
- **Participants** → all members currently in the channel (fetched from Discord REST)
- **Month** → current calendar month (`YYYY-MM`)

### Data Models

**Expense:** `id`, `guild_id`, `channel_id`, `category`, `description`, `value`, `paying_person` (Discord user ID), `involved_people` (Discord user ID list), `destination_month` (YYYY-MM), `created_at`, `updated_at`

**Payment:** `id`, `guild_id`, `month`, `creditor`, `debtor`, `amount`, `paid_at`

**Report payload:** list of expenses + per-person net balances + recommended settlements to zero out all balances

### Architecture Targets

- All command responses must use Discord embeds (success and error states)
- All commands and their resolved parameters (including inferred values) must be logged
- Expense and payment writes must be atomic; partial writes must be rolled back
- Handle Discord 429 rate-limit responses with exponential backoff
- If the database is unreachable, respond with a user-friendly error embed and do not crash
- All entity IDs must use ULID (`python-ulid`) instead of UUID v4 — ULIDs are time-ordered and keep B-tree indexes compact; UUID v4 is random and causes index fragmentation
- Private helper methods (`_utcnow`, `_new_id`, etc.) must be defined as instance methods inside the class, not as module-level functions referenced in `__init__` signatures; tests patch them via `unittest.mock.patch.object`
- Dependency injection is managed by `dependency-injector` via `src/container.py`; the `Container` class declares the full dependency graph using `providers.Resource` (async lifecycle), `providers.Singleton`, and `providers.Factory`
- Database columns use `VARCHAR(n)` for short, bounded strings and `TEXT` only for free-form user content with no practical upper bound; standard sizes: `VARCHAR(26)` for ULIDs, `VARCHAR(20)` for Discord snowflake IDs, `VARCHAR(7)` for `YYYY-MM` months, `VARCHAR(100)` for short labels

## External Dependencies

| Service | Env Var | Notes |
|---------|---------|-------|
| Discord Gateway (WebSocket) | `DISCORD_BOT_TOKEN` | Intents: `GUILDS`, `GUILD_MEMBERS`, `GUILD_MESSAGES` |
| Discord REST API v10 | `DISCORD_BOT_TOKEN` | Used to fetch channel members |
| PostgreSQL | `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `POSTGRES_HOST`, `POSTGRES_PORT` | DSN is built at startup; requires connection pooling in production |

## Setup

**Local:**
```bash
source .venv/bin/activate
pip install -r requirements.lock
cp .env.example .env   # then fill in DISCORD_BOT_TOKEN
python src/main.py
```

**Docker:**
```bash
cp .env.example .env   # then fill in DISCORD_BOT_TOKEN and POSTGRES_PASSWORD
docker compose up --build
```

The compose stack runs two services: `app` (the bot) and `db` (PostgreSQL 16). The app builds its DSN from the `POSTGRES_*` environment variables; `POSTGRES_HOST` is set to `db` (the internal service name) by compose. The app waits for the database health check before starting.

For production, create a `.env.prod` file and run:
```bash
docker compose --env-file .env.prod up -d
```

## Lint & Format

```bash
ruff check .        # lint
ruff check . --fix  # lint with auto-fix
ruff format .       # format
```

Indent width is 2 spaces, line length is 120.

## Testing

Every new feature must have automated tests. Run the test suite with:

```bash
pytest
```

## Environment

Use `.env` or `.envrc` for secrets — both are gitignored. Required vars: `DISCORD_BOT_TOKEN`, `POSTGRES_PASSWORD`. Optional vars with defaults: `POSTGRES_USER` (postgres), `POSTGRES_DB` (expenses), `POSTGRES_HOST` (localhost), `POSTGRES_PORT` (5432).

## Commit Messages

Follow the Conventional Commits format:

```
type(scope): subject
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`

- Subject is lowercase, no trailing period
- Use imperative mood ("add feature" not "added feature")

## Notes

- The full technical spec (requirements, data contracts, sequence diagrams) lives in `project-definition.md`.
