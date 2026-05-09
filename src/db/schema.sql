CREATE TABLE IF NOT EXISTS expenses (
  id                VARCHAR(26)   PRIMARY KEY,
  guild_id          VARCHAR(20)   NOT NULL,
  channel_id        VARCHAR(20)   NOT NULL,
  category          VARCHAR(100)  NOT NULL,
  description       TEXT          NOT NULL,
  value             NUMERIC(12,2) NOT NULL,
  paying_person     VARCHAR(20)   NOT NULL,
  involved_people   VARCHAR(20)[] NOT NULL,
  destination_month VARCHAR(7)    NOT NULL,
  created_at        TIMESTAMPTZ   NOT NULL,
  updated_at        TIMESTAMPTZ   NOT NULL
);

CREATE INDEX IF NOT EXISTS expenses_guild_month ON expenses (guild_id, destination_month);

CREATE TABLE IF NOT EXISTS payments (
  id        VARCHAR(26)   PRIMARY KEY,
  guild_id  VARCHAR(20)   NOT NULL,
  month     VARCHAR(7)    NOT NULL,
  creditor  VARCHAR(20)   NOT NULL,
  debtor    VARCHAR(20)   NOT NULL,
  amount    NUMERIC(12,2) NOT NULL,
  paid_at   TIMESTAMPTZ   NOT NULL
);

CREATE INDEX IF NOT EXISTS payments_guild_month ON payments (guild_id, month);
