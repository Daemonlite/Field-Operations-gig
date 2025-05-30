from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from decouple import config
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


DATABASE_URL = "postgresql+asyncpg://postgres:root123@localhost/field_operations"

engine = create_async_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

async def get_db():
    async with SessionLocal() as session:
        yield session
