# Pawments Bot — Terms of Service

_Last updated: 2026-05-10_

By adding Pawments Bot to your Discord server or using any of its commands, you agree to these terms.

---

## 1. What the Bot Does

Pawments Bot is a shared expense tracking tool for Discord servers. It allows groups to register expenses, generate monthly balance reports, and record settlements between members — entirely through Discord slash commands.

---

## 2. Data We Collect and Store

When you use the bot, the following data is stored in a PostgreSQL database:

- **Expenses:** Discord user IDs (payer and participants), guild ID, channel ID, category, description, amount, and month.
- **Payment records:** Discord user IDs (creditor and debtor), guild ID, amount, and month.

No message content, voice activity, direct messages, or data outside of explicit slash command interactions is ever collected.

---

## 3. How Your Data Is Used

Your data is used solely to:

- Compute balances and recommended settlements for your server.
- Generate monthly reports and expense exports on request.

Your data is never sold, shared with third parties, or used for advertising.

---

## 4. Data Retention

Data persists until explicitly deleted. To remove your data:

- **`/delete-my-data confirm:True`** — permanently and irreversibly deletes all your expense and payment records from the server where the command is run. **This action cannot be undone.**
- If you want your data removed from multiple servers, you must run the command in each server separately.
- Server administrators may also contact the developer to request bulk deletion of all data associated with their server.

---

## 5. Data Security

Data is stored in a private PostgreSQL database. Reasonable technical measures are taken to protect it from unauthorized access. However, no system is completely secure, and we cannot guarantee absolute data security.

---

## 6. Server Administrator Responsibilities

By adding the bot to your server, the server administrator takes responsibility for how the bot is used within that server. Administrators are responsible for informing their members that expense and payment data is being stored.

---

## 7. Disclaimer of Liability

Pawments Bot is a tracking tool, not a financial or legal instrument. Balances and settlements displayed by the bot are advisory only. We are not liable for:

- Financial disputes between users.
- Data loss due to database failure, accidental deletion, or service interruptions.
- Any damages arising from reliance on the bot's output.

The bot is provided **as-is**, without warranty of any kind.

---

## 8. Service Availability

We reserve the right to suspend or discontinue the bot at any time without notice. We are not liable for any loss of data or functionality resulting from service interruption.

---

## 9. Prohibited Use

You may not use the bot to:

- Store fraudulent, misleading, or illegal financial records.
- Harass or harm other users through fabricated expenses.
- Attempt to exploit, reverse-engineer, or otherwise compromise the bot or its infrastructure.

We reserve the right to remove the bot from any server that violates these terms.

---

## 10. Changes to These Terms

These terms may be updated at any time. Continued use of the bot after changes are published constitutes acceptance of the revised terms.

---

## 11. Contact

For questions, data deletion requests, or to report abuse:

- **Email:** igorbarbosaemerick@gmail.com
- **Discord:** phobos1261
