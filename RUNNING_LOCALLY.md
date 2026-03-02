# Running Nyaya Mitra Locally

This guide will help you run the Nyaya Mitra application on your local machine.

## Prerequisites

- Python 3.9 or higher
- Node.js 18 or higher
- PostgreSQL 14 or higher
- Ollama with Mistral 7B model

## Backend Setup

### 1. Install Python Dependencies

```bash
cd backend
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/Mac:
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Set Up PostgreSQL Database

Create a PostgreSQL database:

```sql
CREATE DATABASE nyaya_mitra;
CREATE USER nyaya_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE nyaya_mitra TO nyaya_user;
```

### 3. Configure Environment Variables

Create a `.env` file in the `backend` directory:

```env
DATABASE_URL=postgresql://nyaya_user:your_password@localhost:5432/nyaya_mitra
JWT_SECRET_KEY=your-secret-key-here-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
ENCRYPTION_KEY=your-encryption-key-here
OLLAMA_BASE_URL=http://localhost:11434
```

### 4. Set Up Ollama

Install Ollama from https://ollama.ai and run:

```bash
ollama pull mistral:7b
ollama serve
```

### 5. Initialize Database

```bash
cd backend
python -c "from database import init_db; init_db()"
```

### 6. Seed Data (Optional)

Seed emergency contacts and legal aid providers:

```bash
python -c "from emergency_contacts_seed_data import seed_emergency_contacts; seed_emergency_contacts()"
python -c "from legal_aid_providers_seed_data import seed_legal_aid_providers; seed_legal_aid_providers()"
```

### 7. Run Backend Server

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The backend API will be available at http://localhost:8000

## Frontend Setup

### 1. Install Node Dependencies

```bash
cd frontend
npm install
```

### 2. Run Frontend Development Server

```bash
cd frontend
npm run dev
```

The frontend will be available at http://localhost:5173

## Testing the Application

1. Open your browser and navigate to http://localhost:5173
2. Register a new account
3. Login with your credentials
4. Explore the features:
   - Legal Chat: Ask legal questions
   - Case Analyzer: Analyze complaint validity
   - Document Generator: Generate legal documents
   - Legal Aid Search: Find free legal help
   - Evidence Guide: Learn to collect evidence
   - Emergency SOS: Access emergency contacts

## Troubleshooting

### Backend Issues

- **Database connection error**: Check PostgreSQL is running and credentials are correct
- **Ollama connection error**: Ensure Ollama is running with `ollama serve`
- **Import errors**: Make sure all dependencies are installed with `pip install -r requirements.txt`

### Frontend Issues

- **API connection error**: Ensure backend is running on port 8000
- **Build errors**: Delete `node_modules` and run `npm install` again
- **Port already in use**: Change the port in `vite.config.ts`

## API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Security Notes

- Change all default passwords and secret keys in production
- Use HTTPS in production
- Set up proper CORS origins for production
- Enable rate limiting and monitoring
- Regular security audits recommended

## Next Steps

- Complete remaining optional tasks (OCR, mobile app)
- Run comprehensive tests
- Deploy to production (see deployment guide)
- Set up monitoring and logging
- Configure backup systems
