# Pawments Bot — Privacy Policy

_Last updated: 2026-05-10_

This Privacy Policy explains what data Pawments Bot collects, how it is used, and what rights you have over your data. By using the bot, you agree to this policy.

---

## 1. Data We Collect

We collect only data that you explicitly provide through slash commands. No passive collection, message scanning, or tracking of any kind takes place.

| Data | Source | Example |
|------|--------|---------|
| Discord user ID | Command author / mentioned members | `123456789012345678` |
| Guild (server) ID | Server where the command is run | `987654321098765432` |
| Channel ID | Channel where the command is run | `111222333444555666` |
| Expense details | `/add-expense` | Category, description, amount, payer, participants, month |
| Payment records | `/pay` | Creditor, debtor, amount, month |

We do **not** collect: message content, direct messages, voice activity, reactions, presence data, or any information outside of explicit slash command interactions.

---

## 2. How Data Is Collected

Data is collected only when you or a server member explicitly runs one of the following commands:

- `/add-expense` — stores an expense record
- `/edit-expense` — updates an existing expense record
- `/pay` — stores a payment settlement record

Read-only commands (`/report`, `/expenses`, `/help`) do not create or modify stored data.

---

## 3. How Data Is Used

Your data is used exclusively to:

- Compute per-person balances and recommended settlements within your server.
- Generate monthly expense reports and file exports on request.

Your data is **never**:

- Sold or transferred to third parties.
- Used for advertising or profiling.
- Shared across servers — each server's data is fully isolated.

---

## 4. Data Storage and Security

All data is stored in a private PostgreSQL database controlled by the developer. Data is scoped by server: one server cannot access another server's data.

Reasonable technical measures are in place to protect your data from unauthorized access. However, no system is completely secure, and we cannot guarantee absolute data security.

---

## 5. Data Retention

Data is retained indefinitely until explicitly deleted. It is **not** automatically deleted if the bot is removed from a server.

To delete your data:

- **`/delete-my-data confirm:True`** — permanently deletes all your expense and payment records in the current server. This action cannot be undone. A `.txt` file with a full record of what was deleted is sent to you before removal.
- To delete your data from multiple servers, run the command in each server separately.
- To request deletion of all data associated with your server, contact the developer directly.

---

## 6. Your Rights

Depending on your location, you may have the following rights regarding your personal data:

- **Access** — export your expense data at any time using `/expenses`.
- **Deletion** — permanently remove your data using `/delete-my-data confirm:True` or by contacting the developer.
- **Correction** — update any expense record using `/edit-expense`.

To exercise any right not covered by a bot command, contact the developer using the information in Section 9.

---

## 7. Children's Privacy

Discord requires all users to be at least 13 years old. Pawments Bot does not knowingly collect data from anyone under 13. If you believe a minor has submitted data through the bot, please contact us and we will delete it promptly.

---

## 8. Third-Party Services

Pawments Bot interacts with the following third-party service:

- **Discord** — all commands are processed through the Discord API, which is governed by [Discord's Privacy Policy](https://discord.com/privacy).

No other third-party analytics, tracking, or data processing services are used.

---

## 9. Changes to This Policy

This policy may be updated at any time. The _Last updated_ date at the top of this document will reflect the most recent revision. Continued use of the bot after changes are published constitutes acceptance of the revised policy.

---

## 10. Contact

For privacy-related questions, data deletion requests, or concerns:

- **Email:** igorbarbosaemerick@gmail.com
- **Discord:** phobos1261
