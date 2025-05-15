from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

class EmailAccountBase(BaseModel):
    email: EmailStr
    password: str
    recovery: str
    secret: str

class EmailAccountCreate(EmailAccountBase):
    pass

class EmailAccount(EmailAccountBase):
    id: int

    class Config:
        from_attributes = True

class EmailMessage(BaseModel):
    subject: str
    sender: str
    date: datetime
    body: str
    attachments: Optional[List[str]] = None

class EmailInbox(BaseModel):
    email_account_id: int
    messages: List[EmailMessage] 