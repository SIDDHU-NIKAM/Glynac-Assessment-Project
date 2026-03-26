import requests
from datetime import datetime
from sqlalchemy.orm import Session
from models.customer import Customer
import logging

logger = logging.getLogger(__name__)

FLASK_API_URL = "http://mock-server:5000"
BATCH_SIZE = 10

def fetch_customers_from_flask(page: int = 1, limit: int = 100) -> dict:
    """Fetch customers from Flask API with pagination"""
    try:
        url = f"{FLASK_API_URL}/api/customers?page={page}&limit={limit}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Error fetching from Flask: {str(e)}")
        raise

def upsert_customers(db: Session, customers_data: list) -> int:
    """
    Upsert customers into database (update if exists, insert if new)
    Returns count of processed records
    """
    processed_count = 0
    
    for customer_data in customers_data:
        try:
            # Parse date fields
            dob = None
            if customer_data.get('date_of_birth'):
                try:
                    dob = datetime.strptime(
                        customer_data['date_of_birth'], 
                        '%Y-%m-%d'
                    ).date()
                except:
                    pass
            
            created_at = None
            if customer_data.get('created_at'):
                try:
                    created_at = datetime.fromisoformat(
                        customer_data['created_at'].replace('Z', '+00:00')
                    )
                except:
                    created_at = datetime.utcnow()
            
            # Check if customer exists
            existing = db.query(Customer).filter(
                Customer.customer_id == customer_data['customer_id']
            ).first()
            
            if existing:
                # Update existing customer
                existing.first_name = customer_data.get('first_name', existing.first_name)
                existing.last_name = customer_data.get('last_name', existing.last_name)
                existing.email = customer_data.get('email', existing.email)
                existing.phone = customer_data.get('phone', existing.phone)
                existing.address = customer_data.get('address', existing.address)
                existing.date_of_birth = dob or existing.date_of_birth
                existing.account_balance = customer_data.get('account_balance', existing.account_balance)
            else:
                # Create new customer
                new_customer = Customer(
                    customer_id=customer_data['customer_id'],
                    first_name=customer_data.get('first_name'),
                    last_name=customer_data.get('last_name'),
                    email=customer_data.get('email'),
                    phone=customer_data.get('phone'),
                    address=customer_data.get('address'),
                    date_of_birth=dob,
                    account_balance=customer_data.get('account_balance', 0.0),
                    created_at=created_at
                )
                db.add(new_customer)
            
            processed_count += 1
        except Exception as e:
            logger.error(f"Error processing customer {customer_data.get('customer_id')}: {str(e)}")
            continue
    
    try:
        db.commit()
    except Exception as e:
        logger.error(f"Error committing transaction: {str(e)}")
        db.rollback()
        raise
    
    return processed_count

def ingest_all_customers(db: Session) -> dict:
    """
    Ingest all customers from Flask API into PostgreSQL
    Handles pagination automatically
    """
    total_processed = 0
    page = 1
    
    while True:
        try:
            response_data = fetch_customers_from_flask(page=page, limit=BATCH_SIZE)
            customers = response_data.get('data', [])
            
            if not customers:
                break
            
            processed = upsert_customers(db, customers)
            total_processed += processed
            
            # Check if we've processed all customers
            total = response_data.get('total', 0)
            if total_processed >= total:
                break
            
            page += 1
        except Exception as e:
            logger.error(f"Error during ingestion at page {page}: {str(e)}")
            raise
    
    return {
        "status": "success",
        "records_processed": total_processed
    }

def get_customers_paginated(db: Session, page: int = 1, limit: int = 10) -> dict:
    """Get paginated customers from database"""
    if page < 1:
        page = 1
    if limit < 1 or limit > 100:
        limit = 10
    
    skip = (page - 1) * limit
    
    total = db.query(Customer).count()
    customers = db.query(Customer).offset(skip).limit(limit).all()
    
    return {
        "data": customers,
        "total": total,
        "page": page,
        "limit": limit
    }

def get_customer_by_id(db: Session, customer_id: str) -> Customer:
    """Get single customer by ID"""
    return db.query(Customer).filter(Customer.customer_id == customer_id).first()
