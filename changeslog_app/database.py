from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql+asyncpg://mrizal:$MR1zal$@gp-d9jyy7frv19345067o-master.gpdbmaster.ap-southeast-5.rds.aliyuncs.com/lscentral_dwhp"
engine = create_async_engine(DATABASE_URL, echo=False, future=True)

# Session factory
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Dependency
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
