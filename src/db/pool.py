from pathlib import Path

import asyncpg


async def create_pool(database_url: str) -> asyncpg.Pool:
  pool = await asyncpg.create_pool(database_url)
  schema_sql = (Path(__file__).parent / "schema.sql").read_text()
  async with pool.acquire() as conn:
    await conn.execute(schema_sql)
  return pool
