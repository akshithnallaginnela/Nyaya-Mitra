# Backend Setup Guide

This guide will help you set up the Nyaya Mitra backend with PostgreSQL database.

## Prerequisites

- Python 3.10 or higher
- Docker Desktop (for PostgreSQL)

## Step 1: Install Docker Desktop

### Windows

1. Download Docker Desktop from: https://www.docker.com/products/docker-desktop/
2. Run the installer and follow the installation wizard
3. After installation, restart your computer
4. Launch Docker Desktop from the Start menu
5. Wait for Docker to start (you'll see the Docker icon in the system tray)

### Verify Docker Installation

Open PowerShell and run:
```powershell
docker --version
docker compose version
```

You should see version information for both commands.

## Step 2: Start PostgreSQL Database

Once Docker is running, navigate to the project root directory and run:

```powershell
docker compose up -d
```

This will:
- Download the PostgreSQL 16 Alpine image (first time only)
- Create and start a PostgreSQL container named `nyaya_mitra_db`
- Expose PostgreSQL on port 5432
- Create a database named `nyaya_mitra`

### Verify PostgreSQL is Running

```powershell
docker compose ps
```

You should see the `nyaya_mitra_db` container with status "Up".

### Check PostgreSQL Logs

```powershell
docker compose logs postgres
```

## Step 3: Set Up Python Virtual Environment

Navigate to the `backend` directory:

```powershell
cd backend
```

Create a virtual environment:

```powershell
python -m venv venv
```

Activate the virtual environment:

```powershell
# Windows PowerShell
.\venv\Scripts\Activate.ps1

# Windows Command Prompt
.\venv\Scripts\activate.bat
```

## Step 4: Install Python Dependencies

With the virtual environment activated:

```powershell
pip install -r requirements.txt
```

This will install all required packages including:
- FastAPI and Uvicorn
- SQLAlchemy and PostgreSQL driver
- Authentication libraries
- AI/ML libraries
- Testing tools

## Step 5: Configure Environment Variables

The `.env` file has already been created with default values. Review and modify if needed:

```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/nyaya_mitra
```

## Step 6: Run Database Tests

Test the database connection:

```powershell
pytest test_database.py -v
```

All tests should pass, confirming:
- Database connection works
- SQLAlchemy is properly configured
- Base model provides required fields
- Session management works correctly

## Step 7: Start the FastAPI Server

```powershell
python main.py
```

Or using uvicorn directly:

```powershell
uvicorn main:app --reload
```

The API will be available at: http://localhost:8000

### Test the API

Open your browser and visit:
- Health check: http://localhost:8000/health
- Database health: http://localhost:8000/db-health
- API docs: http://localhost:8000/docs

## Troubleshooting

### Docker Issues

**Problem**: Docker commands not recognized
- **Solution**: Make sure Docker Desktop is installed and running

**Problem**: Port 5432 already in use
- **Solution**: Stop any existing PostgreSQL instances or change the port in `docker-compose.yml`

### Database Connection Issues

**Problem**: "Connection refused" error
- **Solution**: Ensure PostgreSQL container is running: `docker compose ps`

**Problem**: "Authentication failed"
- **Solution**: Check credentials in `.env` match those in `docker-compose.yml`

### Python Issues

**Problem**: Module not found errors
- **Solution**: Ensure virtual environment is activated and dependencies are installed

**Problem**: pydantic_settings import error
- **Solution**: Make sure you have the latest requirements: `pip install -r requirements.txt --upgrade`

## Stopping the Database

When you're done working:

```powershell
docker compose down
```

To stop and remove all data:

```powershell
docker compose down -v
```

## Next Steps

After completing this setup:
1. The database is ready for model implementations (Task 2.2+)
2. You can start implementing authentication (Task 3.1+)
3. The FastAPI server is ready for endpoint development

## Useful Commands

```powershell
# View running containers
docker compose ps

# View PostgreSQL logs
docker compose logs postgres -f

# Connect to PostgreSQL CLI
docker compose exec postgres psql -U postgres -d nyaya_mitra

# Restart PostgreSQL
docker compose restart postgres

# Run all tests
pytest -v

# Run specific test file
pytest test_database.py -v

# Run with coverage
pytest --cov=. --cov-report=html
```
