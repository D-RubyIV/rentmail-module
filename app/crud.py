from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from . import models, schemas

async def create_email_account(db: AsyncSession, email_account: schemas.EmailAccountCreate):
    db_email_account = models.EmailAccount(**email_account.model_dump())
    db.add(db_email_account)
    await db.commit()
    await db.refresh(db_email_account)
    return db_email_account

async def get_email_account(db: AsyncSession, email_account_id: int):
    result = await db.execute(
        select(models.EmailAccount).filter(models.EmailAccount.id == email_account_id)
    )
    return result.scalar_one_or_none()

async def get_email_account_by_email(db: AsyncSession, email: str):
    result = await db.execute(
        select(models.EmailAccount).filter(models.EmailAccount.email == email)
    )
    return result.scalar_one_or_none()

async def get_email_accounts(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(
        select(models.EmailAccount).offset(skip).limit(limit)
    )
    return result.scalars().all()

async def update_email_account(
    db: AsyncSession, 
    email_account_id: int, 
    email_account: schemas.EmailAccountCreate
):
    db_email_account = await get_email_account(db, email_account_id)
    if db_email_account:
        for key, value in email_account.model_dump().items():
            setattr(db_email_account, key, value)
        await db.commit()
        await db.refresh(db_email_account)
    return db_email_account

async def delete_email_account(db: AsyncSession, email_account_id: int):
    db_email_account = await get_email_account(db, email_account_id)
    if db_email_account:
        await db.delete(db_email_account)
        await db.commit()
        return True
    return False 