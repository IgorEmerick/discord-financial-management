# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

A Discord bot for financial management. Python 3.12 project with a `.venv` virtual environment already created.

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

## Environment

The `.gitignore` excludes `.env` and `.envrc` — use one of these for Discord bot tokens and other secrets.

## Commit Messages

Follow the Conventional Commits format:

```
type(scope): subject
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`

- Subject is lowercase, no trailing period
- Use imperative mood ("add feature" not "added feature")

## Notes

- This project is in early development; no source files or dependency manifest exist yet.
- The `.gitignore` is pre-configured for Ruff (linter/formatter), so prefer Ruff when adding linting/formatting tooling.
