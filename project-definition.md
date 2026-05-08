# Discord Expense Bot — Technical Documentation

---

## 1. Overview

### Objective

The **Discord Expense Bot** is a bot application integrated into Discord servers that enables groups of people to track shared expenses, generate financial reports, and register payments between members — all without leaving the Discord environment.

It is designed to solve the common problem of splitting costs among groups (roommates, travel companions, event organizers, etc.) by automating the calculation of balances, credits, and debits per month.

### Scope

#### Included

- Registration of shared expenses with metadata (category, description, value, payer, participants, target month)
- Automatic inference of payer, participants, and target month when not explicitly provided
- Generation of monthly financial reports, including itemized expenses and final balance (creditors vs. debtors)
- Registration of payments between members (full or partial settlement)
- Automatic settlement of all outstanding credits when no specific creditor/debtor is specified

#### Excluded

- Integration with external payment platforms (e.g., PayPal, Pix, Stripe)
- Persistent multi-server data isolation (behavior across multiple guilds is out of scope for v1.0.0)
- Currency conversion or multi-currency support
- User authentication beyond Discord's native identity system
- Expense editing or deletion after registration

---

## 2. Requirements

### 2.1 Functional Requirements

| ID | Description |
|----|-------------|
| FR-01 | The bot must allow a user to register a shared expense with the following fields: **category**, **description**, **value**, **paying person**, **involved people**, and **destination month**. |
| FR-02 | If no **paying person** is specified, the bot must automatically assign the command author as the payer. |
| FR-03 | If no **involved people** are specified, the bot must automatically include all members currently in the channel as expense participants. |
| FR-04 | If no **destination month** is specified, the bot must default to the current calendar month. |
| FR-05 | The bot must generate a monthly financial report containing all registered expenses for the requested month and a final balance listing all creditor-debtor relationships. |
| FR-06 | The bot must allow a user to register a payment from a specific creditor to a specific debtor for a given month. |
| FR-07 | If no creditor and no debtor are specified during payment registration, the bot must automatically settle all outstanding credits for the month. |

### 2.2 Non-Functional Requirements

| ID | Category | Description |
|----|----------|-------------|
| NFR-01 | Performance | Command responses must be delivered within **3 seconds** under normal load. |
| NFR-02 | Availability | The bot must maintain **99% uptime** during active hours. |
| NFR-03 | Fault Tolerance | If the database is unreachable, the bot must respond with a user-friendly error message and not crash. |
| NFR-04 | Scalability | The bot must support at least **10 concurrent Discord servers** in v1.0.0. |
| NFR-05 | Data Integrity | Expense and payment records must be persisted atomically; partial writes must be rolled back. |
| NFR-06 | Auditability | All commands and their resolved parameters (including inferred values) must be logged. |
| NFR-07 | Usability | All bot responses must use Discord embeds with clear formatting, including success/error states. |

---

## 3. Data Flow

### 3.1 Add Expense (`/add-expense`)

**Macro steps:**

1. User invokes the `/add-expense` command in a Discord channel.
2. The bot receives the interaction payload from the Discord Gateway.
3. The bot resolves optional fields: infers payer (command author), participants (all channel members), and month (current month) if not provided.
4. The bot validates the resolved inputs (e.g., positive value, valid month format).
5. The bot persists the expense record to the database.
6. The bot responds to the user with a confirmation embed.

```mermaid
sequenceDiagram
    actor User
    participant Discord Gateway
    participant Bot Handler
    participant Resolver Service
    participant Database

    User->>Discord Gateway: /add-expense [category] [description] [value] [payer?] [participants?] [month?]
    Discord Gateway->>Bot Handler: Interaction Payload
    Bot Handler->>Resolver Service: Resolve optional fields
    Resolver Service->>Discord Gateway: Fetch channel members (if participants omitted)
    Discord Gateway-->>Resolver Service: Member list
    Resolver Service-->>Bot Handler: Resolved fields (payer, participants, month)
    Bot Handler->>Bot Handler: Validate inputs
    Bot Handler->>Database: INSERT expense record
    Database-->>Bot Handler: Success / Error
    Bot Handler->>Discord Gateway: Send confirmation embed
    Discord Gateway-->>User: Expense registered ✅
```

---

### 3.2 Request Monthly Report (`/report`)

**Macro steps:**

1. User invokes the `/report` command with a target month.
2. The bot queries the database for all expenses of that month.
3. The bot calculates per-person net balances (paid vs. owed).
4. The bot generates the creditor-debtor relationship table.
5. The bot responds with a formatted report embed.

```mermaid
sequenceDiagram
    actor User
    participant Discord Gateway
    participant Bot Handler
    participant Balance Calculator
    participant Database

    User->>Discord Gateway: /report [month]
    Discord Gateway->>Bot Handler: Interaction Payload
    Bot Handler->>Database: SELECT expenses WHERE month = [month]
    Database-->>Bot Handler: Expense records
    Bot Handler->>Balance Calculator: Compute net balances per person
    Balance Calculator-->>Bot Handler: Creditor / Debtor map
    Bot Handler->>Discord Gateway: Send report embed (expenses + balance)
    Discord Gateway-->>User: Monthly Report 📊
```

---

### 3.3 Register Payment (`/pay`)

**Macro steps:**

1. User invokes the `/pay` command, optionally specifying creditor, debtor, and month.
2. If creditor and debtor are omitted, the bot fetches all outstanding credits for the month.
3. The bot validates that the payment is consistent with the current balance.
4. The bot persists the payment record(s) to the database.
5. The bot responds with a settlement confirmation embed.

```mermaid
sequenceDiagram
    actor User
    participant Discord Gateway
    participant Bot Handler
    participant Balance Calculator
    participant Database

    User->>Discord Gateway: /pay [creditor?] [debtor?] [month]
    Discord Gateway->>Bot Handler: Interaction Payload
    alt Creditor and debtor specified
        Bot Handler->>Database: SELECT balance for creditor-debtor pair
        Database-->>Bot Handler: Specific balance
    else No creditor/debtor specified
        Bot Handler->>Database: SELECT all outstanding balances for month
        Database-->>Bot Handler: All balances
    end
    Bot Handler->>Balance Calculator: Validate payment against balance
    Balance Calculator-->>Bot Handler: Validated payment(s)
    Bot Handler->>Database: INSERT payment record(s)
    Database-->>Bot Handler: Success / Error
    Bot Handler->>Discord Gateway: Send settlement confirmation embed
    Discord Gateway-->>User: Payment registered 💸
```

---

## 4. Data Sources

| Source | Type | Endpoint / Location | Authentication | Rate Limit / Notes |
|--------|------|---------------------|----------------|--------------------|
| Discord Gateway | WebSocket API | `wss://gateway.discord.gg` | Bot Token (Bearer) | Discord's default rate limits apply per route |
| Discord REST API | REST API | `https://discord.com/api/v10` | Bot Token (Bearer) | 50 requests/second global; per-route buckets |
| Application Database | Relational DB (PostgreSQL recommended) | Internal (e.g., `localhost:5432/expensebot`) | DB credentials (env vars) | N/A — internal service |

---

## 5. Data Contracts

### 5.1 Expense Record

**Command:** `/add-expense`

| Field | Type | Required | Validation | Default |
|-------|------|----------|------------|---------|
| `category` | `string` | ✅ | Non-empty, max 50 chars | — |
| `description` | `string` | ✅ | Non-empty, max 200 chars | — |
| `value` | `number` | ✅ | Positive decimal, max 2 decimal places | — |
| `paying_person` | `string` (Discord User ID) | ❌ | Must be a valid Discord member | Command author |
| `involved_people` | `string[]` (Discord User IDs) | ❌ | Each must be a valid channel member | All channel members |
| `destination_month` | `string` | ❌ | Format: `YYYY-MM` | Current month |
| `guild_id` | `string` | ✅ (auto) | Discord guild snowflake | From interaction context |
| `channel_id` | `string` | ✅ (auto) | Discord channel snowflake | From interaction context |
| `created_at` | `datetime` | ✅ (auto) | ISO 8601 UTC | Server timestamp |

**Example JSON (persisted):**

```json
{
  "id": "exp_01J3KXYZ",
  "guild_id": "1234567890",
  "channel_id": "9876543210",
  "category": "Food",
  "description": "Pizza night",
  "value": 85.50,
  "paying_person": "111222333",
  "involved_people": ["111222333", "444555666", "777888999"],
  "destination_month": "2025-05",
  "created_at": "2025-05-07T21:00:00Z"
}
```

---

### 5.2 Monthly Report Response

**Command:** `/report`

| Field | Type | Description |
|-------|------|-------------|
| `month` | `string` | Queried month in `YYYY-MM` format |
| `expenses` | `Expense[]` | List of all expense records for the month |
| `balances` | `Balance[]` | Net balance per person (positive = creditor, negative = debtor) |
| `settlements` | `Settlement[]` | Recommended payments to zero out all balances |

**Example JSON (report payload):**

```json
{
  "month": "2025-05",
  "expenses": [
    {
      "id": "exp_01J3KXYZ",
      "category": "Food",
      "description": "Pizza night",
      "value": 85.50,
      "paying_person": "111222333",
      "involved_people": ["111222333", "444555666", "777888999"]
    }
  ],
  "balances": [
    { "user_id": "111222333", "net": 57.00 },
    { "user_id": "444555666", "net": -28.50 },
    { "user_id": "777888999", "net": -28.50 }
  ],
  "settlements": [
    { "debtor": "444555666", "creditor": "111222333", "amount": 28.50 },
    { "debtor": "777888999", "creditor": "111222333", "amount": 28.50 }
  ]
}
```

---

### 5.3 Payment Record

**Command:** `/pay`

| Field | Type | Required | Validation | Default |
|-------|------|----------|------------|---------|
| `creditor` | `string` (Discord User ID) | ❌ | Must be a valid creditor for the month | All creditors |
| `debtor` | `string` (Discord User ID) | ❌ | Must be a valid debtor for the month | All debtors |
| `month` | `string` | ✅ | Format: `YYYY-MM` | — |
| `amount` | `number` | ✅ (auto) | Derived from current balance; must be > 0 | Full outstanding balance |
| `paid_at` | `datetime` | ✅ (auto) | ISO 8601 UTC | Server timestamp |

**Example JSON (persisted):**

```json
{
  "id": "pay_02K4LABC",
  "guild_id": "1234567890",
  "month": "2025-05",
  "creditor": "111222333",
  "debtor": "444555666",
  "amount": 28.50,
  "paid_at": "2025-05-10T14:30:00Z"
}
```

---

## 6. External Dependencies

| Service | Purpose | Auth Type | Notes |
|---------|---------|-----------|-------|
| Discord Gateway API | Real-time event reception (slash commands, interactions) | Bot Token | Requires `DISCORD_BOT_TOKEN` env var; Intents: `GUILDS`, `GUILD_MEMBERS`, `GUILD_MESSAGES` |
| Discord REST API v10 | Fetching channel members, sending responses/embeds | Bot Token | Rate-limited; implement exponential backoff on 429 responses |
| PostgreSQL (or equivalent) | Persistent storage of expenses, payments, and balances | DB credentials | `DATABASE_URL` env var; requires connection pooling in production |

---

## 7. Versioning

| Version | Date | Changes | Authors |
|---------|------|---------|---------|
| v1.0.0 | 2025-05-07 | Initial documentation based on core feature set: add expense, monthly report, register payment | Documentation Agent |