from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging
from datetime import datetime

from database import Base, engine, get_db
from models.customer import Customer
from services.ingestion import (
    ingest_all_customers,
    get_customers_paginated,
    get_customer_by_id
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(title="Customer Ingestion Pipeline", version="1.0.0")

@app.on_event("startup")
async def startup_event():
    """Initialize database tables on startup"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.post("/api/ingest")
async def ingest_data(db: Session = Depends(get_db)):
    """
    Fetch all data from Flask API and upsert into PostgreSQL
    Returns count of processed records
    """
    try:
        result = ingest_all_customers(db)
        return {
            "status": result["status"],
            "records_processed": result["records_processed"],
            "timestamp": datetime.utcnow().isoformat()
        }
    except SQLAlchemyError as e:
        logger.error(f"Database error during ingestion: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Database error during ingestion"
        )
    except Exception as e:
        logger.error(f"Error during ingestion: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error during ingestion: {str(e)}"
        )

@app.get("/api/customers")
async def get_customers(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get paginated list of customers from database
    Query params: page, limit
    """
    try:
        result = get_customers_paginated(db, page=page, limit=limit)
        
        # Convert SQLAlchemy objects to dictionaries
        data = []
        for customer in result["data"]:
            data.append({
                "customer_id": customer.customer_id,
                "first_name": customer.first_name,
                "last_name": customer.last_name,
                "email": customer.email,
                "phone": customer.phone,
                "address": customer.address,
                "date_of_birth": customer.date_of_birth.isoformat() if customer.date_of_birth else None,
                "account_balance": float(customer.account_balance) if customer.account_balance else 0.0,
                "created_at": customer.created_at.isoformat() if customer.created_at else None
            })
        
        return {
            "data": data,
            "total": result["total"],
            "page": result["page"],
            "limit": result["limit"]
        }
    except Exception as e:
        logger.error(f"Error fetching customers: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching customers")

@app.get("/api/customers/{customer_id}")
async def get_customer(customer_id: str, db: Session = Depends(get_db)):
    """
    Get single customer by ID
    Returns 404 if customer not found
    """
    try:
        customer = get_customer_by_id(db, customer_id)
        
        if not customer:
            raise HTTPException(
                status_code=404,
                detail=f"Customer {customer_id} not found"
            )
        
        return {
            "customer_id": customer.customer_id,
            "first_name": customer.first_name,
            "last_name": customer.last_name,
            "email": customer.email,
            "phone": customer.phone,
            "address": customer.address,
            "date_of_birth": customer.date_of_birth.isoformat() if customer.date_of_birth else None,
            "account_balance": float(customer.account_balance) if customer.account_balance else 0.0,
            "created_at": customer.created_at.isoformat() if customer.created_at else None
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching customer {customer_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching customer")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Customer Ingestion Pipeline",
        "version": "1.0.0",
        "endpoints": {
            "health": "/api/health",
            "ingest": "POST /api/ingest",
            "customers": "GET /api/customers",
            "customer": "GET /api/customers/{customer_id}"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
