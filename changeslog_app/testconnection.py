# test_connection.py
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.sql import text

DB_USER = "mrizal"
DB_PASS = "$MR1zal$"
DB_HOST = "gp-d9jyy7frv19345067o-master.gpdbmaster.ap-southeast-5.rds.aliyuncs.com"
DB_NAME = "lscentral_dwhp"

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"

async def test_connection():
    engine = create_async_engine(DATABASE_URL, echo=True)
    async with engine.begin() as conn:
        result = await conn.execute(text("SELECT 1"))
        print(result.fetchone())

asyncio.run(test_connection())
