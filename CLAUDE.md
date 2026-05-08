# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

A Discord bot for shared expense management. Groups (roommates, travel companions, etc.) register expenses, generate monthly financial reports, and settle payments — all via Discord slash commands.

### Commands

| Command | Description |
|---------|-------------|
| `/add-expense` | Register a shared expense (category, description, value, payer, participants, month) |
| `/report` | Generate a monthly report with itemized expenses and creditor/debtor balances |
| `/pay` | Register a payment between a creditor and debtor; if both are omitted, settles all outstanding balances for the month |

### Field Inference (auto-resolved when omitted)

- **Payer** → command author
- **Participants** → all members currently in the channel (fetched from Discord REST)
- **Month** → current calendar month (`YYYY-MM`)

### Data Models

**Expense:** `id`, `guild_id`, `channel_id`, `category`, `description`, `value`, `paying_person` (Discord user ID), `involved_people` (Discord user ID list), `destination_month` (YYYY-MM), `created_at`

**Payment:** `id`, `guild_id`, `month`, `creditor`, `debtor`, `amount`, `paid_at`

**Report payload:** list of expenses + per-person net balances + recommended settlements to zero out all balances

### Architecture Targets

- All command responses must use Discord embeds (success and error states)
- All commands and their resolved parameters (including inferred values) must be logged
- Expense and payment writes must be atomic; partial writes must be rolled back
- Handle Discord 429 rate-limit responses with exponential backoff
- Responses must be delivered within 3 seconds under normal load

## External Dependencies

| Service | Env Var | Notes |
|---------|---------|-------|
| Discord Gateway (WebSocket) | `DISCORD_BOT_TOKEN` | Intents: `GUILDS`, `GUILD_MEMBERS`, `GUILD_MESSAGES` |
| Discord REST API v10 | `DISCORD_BOT_TOKEN` | Used to fetch channel members |
| PostgreSQL | `DATABASE_URL` | Requires connection pooling in production |

## Setup

```bash
source .venv/bin/activate
pip install -r requirements.txt   # once requirements.txt exists
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

Use `.env` or `.envrc` for secrets — both are gitignored. Required vars: `DISCORD_BOT_TOKEN`, `DATABASE_URL`.

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
- This project is in early development; no source files or dependency manifest exist yet.
