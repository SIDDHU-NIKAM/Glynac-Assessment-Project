from sqlalchemy import Column, String, Date, Integer, Numeric, DateTime, Text
from datetime import datetime
from database import Base

class Customer(Base):
    __tablename__ = "customers"
    
    customer_id = Column(String(50), primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    phone = Column(String(20))
    address = Column(Text)
    date_of_birth = Column(Date)
    account_balance = Column(Numeric(15, 2), default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    class Config:
        from_attributes = True

class CustomerSchema:
    """Pydantic schema for customer data"""
    def __init__(self, customer_id, first_name, last_name, email, phone=None, 
                 address=None, date_of_birth=None, account_balance=0.0, created_at=None):
        self.customer_id = customer_id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone = phone
        self.address = address
        self.date_of_birth = date_of_birth
        self.account_balance = account_balance
        self.created_at = created_at or datetime.utcnow()
