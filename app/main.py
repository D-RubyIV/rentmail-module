from typing import List

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from . import crud, models, schemas
from .database import get_db, engine
from .imap import ImapBox

app = FastAPI(title="Email Accounts API")


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)


@app.post("/accounts/email", response_model=schemas.EmailAccount)
async def create_email_account(
        email_account: schemas.EmailAccountCreate,
        db: AsyncSession = Depends(get_db)
):
    db_email = await crud.get_email_account_by_email(db, email=email_account.email)
    if db_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    return await crud.create_email_account(db=db, email_account=email_account)


@app.get("/accounts/email", response_model=List[schemas.EmailAccount])
async def read_email_accounts(
        skip: int = 0,
        limit: int = 100,
        db: AsyncSession = Depends(get_db)
):
    email_accounts = await crud.get_email_accounts(db, skip=skip, limit=limit)
    return email_accounts


@app.get("/accounts/email/{email_account_id}", response_model=schemas.EmailAccount)
async def read_email_account(
        email_account_id: int,
        db: AsyncSession = Depends(get_db)
):
    db_email_account = await crud.get_email_account(db, email_account_id=email_account_id)
    if db_email_account is None:
        raise HTTPException(status_code=404, detail="Email account not found")
    return db_email_account


@app.put("/accounts/email/{email_account_id}", response_model=schemas.EmailAccount)
async def update_email_account(
        email_account_id: int,
        email_account: schemas.EmailAccountCreate,
        db: AsyncSession = Depends(get_db)
):
    db_email_account = await crud.update_email_account(
        db=db,
        email_account_id=email_account_id,
        email_account=email_account
    )
    if db_email_account is None:
        raise HTTPException(status_code=404, detail="Email account not found")
    return db_email_account


@app.delete("/accounts/email/{email_account_id}")
async def delete_email_account(
        email_account_id: int,
        db: AsyncSession = Depends(get_db)
):
    success = await crud.delete_email_account(db=db, email_account_id=email_account_id)
    if not success:
        raise HTTPException(status_code=404, detail="Email account not found")
    return {"message": "Email account deleted successfully"}


@app.get("/accounts/email/inbox/{email_account_id}", response_model=schemas.EmailInbox)
async def read_email_account_inbox(
        email_account_id: int,
        db: AsyncSession = Depends(get_db)
):
    try:
        db_email_account = await crud.get_email_account(db, email_account_id=email_account_id)
        if db_email_account is None:
            raise HTTPException(status_code=404, detail="Email account not found")
        
        imap_box = ImapBox(
            email_string=db_email_account.email,
            secret_string=db_email_account.secret
        )
        
        try:
            messages = imap_box.print_hi()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
        return {
            "email_account_id": email_account_id,
            "messages": messages
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


