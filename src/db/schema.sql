CREATE TABLE IF NOT EXISTS expenses (
  id                TEXT          PRIMARY KEY,
  guild_id          TEXT          NOT NULL,
  channel_id        TEXT          NOT NULL,
  category          TEXT          NOT NULL,
  description       TEXT          NOT NULL,
  value             NUMERIC(12,2) NOT NULL,
  paying_person     TEXT          NOT NULL,
  involved_people   TEXT[]        NOT NULL,
  destination_month TEXT          NOT NULL,
  created_at        TIMESTAMPTZ   NOT NULL,
  updated_at        TIMESTAMPTZ   NOT NULL
);

CREATE INDEX IF NOT EXISTS expenses_guild_month ON expenses (guild_id, destination_month);

CREATE TABLE IF NOT EXISTS payments (
  id        TEXT          PRIMARY KEY,
  guild_id  TEXT          NOT NULL,
  month     TEXT          NOT NULL,
  creditor  TEXT          NOT NULL,
  debtor    TEXT          NOT NULL,
  amount    NUMERIC(12,2) NOT NULL,
  paid_at   TIMESTAMPTZ   NOT NULL
);

CREATE INDEX IF NOT EXISTS payments_guild_month ON payments (guild_id, month);
