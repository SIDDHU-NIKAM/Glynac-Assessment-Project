# Backend Data Pipeline Assessment

A complete data pipeline project with 3 Docker services: Flask Mock Server, FastAPI Ingestion Pipeline, and PostgreSQL Database.

## Project Architecture

```
Flask (Port 5000)
    ↓ JSON Data
FastAPI (Port 8000)
    ↓ Upsert Logic
PostgreSQL (Port 5432)
    ↓
API Response
```

## Project Structure

```
project-root/
├── docker-compose.yml          # Docker services configuration
├── README.md                   # This file
│
├── mock-server/                # Flask Mock Server
│   ├── app.py                 # Flask application
│   ├── Dockerfile             # Container configuration
│   ├── requirements.txt        # Python dependencies
│   └── data/
│       └── customers.json     # 20+ customers data
│
└── pipeline-service/           # FastAPI Pipeline Service
    ├── main.py                # FastAPI application
    ├── database.py            # Database configuration
    ├── Dockerfile             # Container configuration
    ├── requirements.txt        # Python dependencies
    ├── models/
    │   └── customer.py        # SQLAlchemy model + schema
    └── services/
        └── ingestion.py       # Data ingestion logic
```

## Prerequisites

- **Docker Desktop** (running)
- **Python 3.10+**
- **Git**
- **docker-compose** (usually comes with Docker Desktop)

Verify prerequisites:
```bash
docker --version
docker-compose --version
python --version
```

## Quick Start

1. **Clone/Navigate to project**
   ```bash
   cd d:\Videos\Glynac-Assessment-Project
   ```

2. **Start all services**
   ```bash
   docker-compose up -d
   ```

3. **Verify services are running**
   ```bash
   docker-compose ps
   ```

4. **Run ingestion**
   ```bash
   curl -X POST http://localhost:8000/api/ingest
   ```

## Service Details

### Part 1: Flask Mock Server (Port 5000)

**Purpose:** Serves mock customer data from JSON file

**Endpoints:**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/customers` | GET | Paginated customer list |
| `/api/customers/{id}` | GET | Single customer |

**Example Requests:**

```bash
# Health check
curl http://localhost:5000/api/health

# Get all customers (page 1, 10 per page)
curl http://localhost:5000/api/customers?page=1&limit=10

# Get customer by ID
curl http://localhost:5000/api/customers/CUST001

# Pagination examples
curl http://localhost:5000/api/customers?page=2&limit=5
curl http://localhost:5000/api/customers?page=1&limit=20
```

**Response Format:**
```json
{
  "data": [
    {
      "customer_id": "CUST001",
      "first_name": "John",
      "last_name": "Smith",
      "email": "john.smith@email.com",
      "phone": "555-0101",
      "address": "123 Main St, New York, NY 10001",
      "date_of_birth": "1985-03-15",
      "account_balance": 5250.50,
      "created_at": "2023-01-10T08:30:00Z"
    }
  ],
  "total": 20,
  "page": 1,
  "limit": 10
}
```

**Data File:** `mock-server/data/customers.json`
- Contains 20 customers
- Each with: customer_id, first_name, last_name, email, phone, address, date_of_birth, account_balance, created_at

### Part 2: FastAPI Pipeline Service (Port 8000)

**Purpose:** Ingests data from Flask into PostgreSQL with automatic pagination

**Endpoints:**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/ingest` | POST | Fetch & upsert all customers |
| `/api/customers` | GET | Paginated customers from DB |
| `/api/customers/{id}` | GET | Single customer from DB |

**Example Requests:**

```bash
# Health check
curl http://localhost:8000/api/health

# Ingest all customers from Flask into PostgreSQL
curl -X POST http://localhost:8000/api/ingest

# Get customers from database (paginated)
curl http://localhost:8000/api/customers?page=1&limit=5

# Get single customer from database
curl http://localhost:8000/api/customers/CUST001

# Different pagination options
curl http://localhost:8000/api/customers?page=1&limit=20
curl http://localhost:8000/api/customers?page=2&limit=10
```

**Ingestion Response:**
```json
{
  "status": "success",
  "records_processed": 20,
  "timestamp": "2024-03-27T10:30:00.123456"
}
```

**Features:**
- **Automatic Pagination:** Handles Flask pagination automatically
- **Upsert Logic:** Updates existing records, inserts new ones
- **Error Handling:** Graceful error handling with detailed logging
- **Type Safety:** Full type hints and validation

### PostgreSQL Database

**Configuration:**
- **Image:** postgres:15
- **Port:** 5432
- **User:** postgres
- **Password:** password
- **Database:** customer_db

**Table: customers**

| Column | Type | Constraints |
|--------|------|-----------|
| customer_id | VARCHAR(50) | PRIMARY KEY |
| first_name | VARCHAR(100) | NOT NULL |
| last_name | VARCHAR(100) | NOT NULL |
| email | VARCHAR(255) | NOT NULL, INDEX |
| phone | VARCHAR(20) | - |
| address | TEXT | - |
| date_of_birth | DATE | - |
| account_balance | DECIMAL(15,2) | - |
| created_at | TIMESTAMP | - |

**Access Database:**
```bash
# Connect to PostgreSQL
docker exec -it postgres_customer_db psql -U postgres -d customer_db

# Common queries
SELECT COUNT(*) FROM customers;
SELECT * FROM customers LIMIT 5;
SELECT * FROM customers WHERE customer_id = 'CUST001';
\dt  -- list tables
\q   -- quit
```

## Testing Workflow

### 1. Start Services
```bash
docker-compose up -d
```

### 2. Verify Services
```bash
# Check all containers running
docker-compose ps

# Check logs
docker-compose logs -f mock-server
docker-compose logs -f pipeline-service
docker-compose logs -f postgres
```

### 3. Test Flask Mock Server
```bash
# Health check
curl http://localhost:5000/api/health

# Get paginated customers
curl http://localhost:5000/api/customers?page=1&limit=5

# Get single customer
curl http://localhost:5000/api/customers/CUST001
```

### 4. Test FastAPI Pipeline
```bash
# Health check
curl http://localhost:8000/api/health

# Run ingestion (fetch from Flask, upsert to PostgreSQL)
curl -X POST http://localhost:8000/api/ingest

# Verify data in database
curl http://localhost:8000/api/customers?page=1&limit=5

# Get specific customer
curl http://localhost:8000/api/customers/CUST001
```

### 5. Verify Database
```bash
# Check customer count
docker exec -it postgres_customer_db psql -U postgres -d customer_db -c "SELECT COUNT(*) as total_customers FROM customers;"

# Check specific customer
docker exec -it postgres_customer_db psql -U postgres -d customer_db -c "SELECT * FROM customers WHERE customer_id='CUST001';"
```

## Docker Commands

### View Logs
```bash
# All services
docker-compose logs

# Specific service (follow mode)
docker-compose logs -f mock-server
docker-compose logs -f pipeline-service
docker-compose logs -f postgres

# Last 100 lines
docker-compose logs --tail=100
```

### Container Management
```bash
# Stop all services
docker-compose down

# Stop services and remove volumes
docker-compose down -v

# Restart services
docker-compose restart

# Rebuild images
docker-compose build

# Rebuild and start
docker-compose up -d --build
```

### Database Access
```bash
# Direct PostgreSQL access
docker exec -it postgres_customer_db psql -U postgres -d customer_db

# Run single query
docker exec postgres_customer_db psql -U postgres -d customer_db -c "SELECT * FROM customers LIMIT 5;"

# Export data
docker exec postgres_customer_db pg_dump -U postgres customer_db > backup.sql
```

## Implementation Details

### Flask Mock Server (`mock-server/app.py`)
- Loads 20 customers from JSON file on startup
- Implements full REST API with pagination
- Validates page and limit parameters
- Returns 404 for missing customers
- Error handling for all endpoints

### FastAPI Pipeline (`pipeline-service/main.py`)
- Fetches customers from Flask API with automatic pagination
- Handles all date/time format conversions
- Implements full CRUD operations through API
- Comprehensive logging for debugging
- Automatic database table creation on startup

### Ingestion Service (`pipeline-service/services/ingestion.py`)
- **fetch_customers_from_flask():** Calls Flask API with pagination support
- **upsert_customers():** Updates existing records or inserts new ones
- **ingest_all_customers():** Orchestrates full ingestion with automatic pagination
- **get_customers_paginated():** Retrieves paginated results from database
- **get_customer_by_id():** Gets single customer by ID

### Database Models (`pipeline-service/models/customer.py`)
- SQLAlchemy ORM model for customers table
- Full field mapping with proper types
- Schema class for data validation

### Database Config (`pipeline-service/database.py`)
- SQLAlchemy engine configuration
- Session factory setup
- Dependency injection for FastAPI

## Evaluation Checklist

- [x] All 3 services start with `docker-compose up`
- [x] Flask serves customer data with pagination
- [x] FastAPI ingests data successfully with automatic pagination
- [x] All API endpoints work correctly
- [x] Upsert logic updates existing records
- [x] Error handling for missing resources (404)
- [x] Database properly persists data
- [x] Proper Dockerfile configuration for both services
- [x] Requirements.txt with all dependencies
- [x] Comprehensive documentation

## Common Issues & Solutions

### Port Already in Use
```bash
# Find process using port
netstat -ano | findstr :5000
netstat -ano | findstr :8000
netstat -ano | findstr :5432

# Kill process (replace PID)
taskkill /PID <PID> /F
```

### Container Exit or Fails
```bash
# Check logs
docker-compose logs <service-name>

# Rebuild from scratch
docker-compose down -v
docker-compose up -d --build
```

### Database Connection Issues
```bash
# Verify database is running
docker-compose ps

# Check PostgreSQL logs
docker-compose logs postgres

# Wait for database to be ready
docker-compose down -v
docker-compose up -d postgres
# Wait 10 seconds
docker-compose up -d mock-server pipeline-service
```

### Ingestion Fails
```bash
# Check if Flask is accessible from pipeline
docker exec pipeline_service curl http://mock-server:5000/api/health

# Check database connection from pipeline
docker exec pipeline_service curl http://localhost:8000/api/health
```

## Performance Notes

- Batch size for ingestion: 10 records per request (configurable in `services/ingestion.py`)
- Database indexes on: customer_id (primary key), email
- Connection pooling enabled by default in SQLAlchemy
- Health checks configured for service dependencies

## Security Notes

This is a development/assessment project. For production:
- Use environment variables for all credentials
- Implement authentication/authorization
- Add API rate limiting
- Validate and sanitize all inputs
- Use HTTPS
- Implement audit logging
- Add request/response encryption

## Support

For issues or questions:
1. Check logs: `docker-compose logs <service>`
2. Verify all services running: `docker-compose ps`
3. Test individual endpoints with curl
4. Check environment variables in docker-compose.yml
5. Verify PostgreSQL is accessible

## Additional Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Docker Documentation](https://docs.docker.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
