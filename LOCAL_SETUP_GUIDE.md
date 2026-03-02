# Local Setup Guide - Nyaya Mitra (Windows)

This guide will help you run Nyaya Mitra on your local Windows machine.

## Prerequisites Checklist

Before starting, ensure you have:

- [ ] Windows 10/11
- [ ] Python 3.9 or higher
- [ ] Node.js 18 or higher
- [ ] PostgreSQL 14 or higher
- [ ] Git (optional, for version control)
- [ ] At least 10GB free disk space (for Ollama model)

---

## Part 1: Install Required Software

### 1.1 Install Python (if not installed)

1. Download Python from: https://www.python.org/downloads/
2. Run installer
3. ✅ **IMPORTANT:** Check "Add Python to PATH"
4. Click "Install Now"
5. Verify installation:
   ```cmd
   python --version
   ```
   Should show: Python 3.9.x or higher

### 1.2 Install Node.js (if not installed)

1. Download Node.js LTS from: https://nodejs.org/
2. Run installer with default settings
3. Verify installation:
   ```cmd
   node --version
   npm --version
   ```

### 1.3 Install PostgreSQL

1. Download PostgreSQL from: https://www.postgresql.org/download/windows/
2. Run installer
3. During installation:
   - Port: 5432 (default)
   - Password: Choose a password (remember this!)
   - Locale: Default
4. Verify installation:
   ```cmd
   psql --version
   ```

### 1.4 Install Ollama

1. Download Ollama for Windows from: https://ollama.com/download/windows
2. Run the installer
3. Ollama will start automatically
4. Verify installation:
   ```cmd
   ollama --version
   ```

---

## Part 2: Database Setup

### 2.1 Create Database

Open Command Prompt or PowerShell and run:

```cmd
# Connect to PostgreSQL (enter your password when prompted)
psql -U postgres

# In PostgreSQL prompt, run:
CREATE DATABASE nyaya_mitra;

# Create user (optional, or use postgres user)
CREATE USER nyaya_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE nyaya_mitra TO nyaya_user;

# Exit PostgreSQL
\q
```

### 2.2 Verify Database

```cmd
psql -U postgres -d nyaya_mitra -c "SELECT version();"
```

Should show PostgreSQL version.

---

## Part 3: Backend Setup

### 3.1 Navigate to Backend Directory

```cmd
cd backend
```

### 3.2 Create Virtual Environment

```cmd
# Create virtual environment
python -m venv .venv

# Activate virtual environment
.venv\Scripts\activate

# You should see (.venv) in your prompt
```

### 3.3 Install Python Dependencies

```cmd
# Upgrade pip
python -m pip install --upgrade pip

# Install all dependencies
pip install -r requirements.txt
```

This will take 5-10 minutes. If you see errors, try:
```cmd
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

### 3.4 Install spaCy English Model

```cmd
python -m spacy download en_core_web_sm
```

### 3.5 Configure Environment Variables

1. Copy the example env file:
   ```cmd
   copy .env.example .env
   ```

2. Edit `.env` file (use Notepad or VS Code):
   ```cmd
   notepad .env
   ```

3. Update with your settings:
   ```env
   # Database Configuration
   DATABASE_URL=postgresql://postgres:your_password@localhost:5432/nyaya_mitra

   # JWT Configuration (generate a secure key)
   JWT_SECRET=your-super-secret-jwt-key-min-32-characters-long
   JWT_ALGORITHM=HS256
   JWT_EXPIRATION_HOURS=24

   # Ollama Configuration
   OLLAMA_BASE_URL=http://localhost:11434
   OLLAMA_MODEL=mistral:7b

   # CORS Configuration
   CORS_ORIGINS=http://localhost:3000,http://localhost:5173

   # Application Settings
   ENVIRONMENT=development
   LOG_LEVEL=INFO
   ```

4. Save and close

**Generate Secure Keys:**
```cmd
# Generate JWT secret
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate encryption key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Add the encryption key to your `.env`:
```env
ENCRYPTION_KEY=your-generated-encryption-key
```

### 3.6 Initialize Database

```cmd
# Make sure virtual environment is activated
python -c "from database import init_db; init_db()"
```

You should see: "Database initialized successfully" or similar.

### 3.7 Seed Initial Data

```cmd
# Seed emergency contacts
python seed_emergency_contacts.py

# Seed legal aid providers
python seed_legal_aid_providers.py
```

### 3.8 Download Ollama Model

Open a **new** Command Prompt window (keep backend terminal open):

```cmd
# Download Mistral 7B model (this is ~4GB, will take time)
ollama pull mistral:7b

# Verify model is downloaded
ollama list
```

You should see `mistral:7b` in the list.

### 3.9 Test Ollama

```cmd
# Test Ollama is working
ollama run mistral:7b "Hello, how are you?"
```

Press Ctrl+D or type `/bye` to exit.

### 3.10 Start Backend Server

Back in your backend terminal (with virtual environment activated):

```cmd
# Start the FastAPI server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 3.11 Test Backend

Open a **new** Command Prompt and test:

```cmd
# Test health endpoint
curl http://localhost:8000/health

# Or open in browser:
# http://localhost:8000/health
# http://localhost:8000/docs (API documentation)
```

**Keep this terminal running!**

---

## Part 4: Frontend Setup

### 4.1 Open New Terminal

Open a **new** Command Prompt or PowerShell window.

### 4.2 Navigate to Frontend Directory

```cmd
cd frontend
```

### 4.3 Install Dependencies

```cmd
npm install
```

This will take 2-5 minutes.

If you see errors, try:
```cmd
npm cache clean --force
npm install
```

### 4.4 Configure API Endpoint

The frontend is already configured to use `/api` which will proxy to `http://localhost:8000` via Vite.

Check `vite.config.ts` - it should have:
```typescript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    }
  }
}
```

### 4.5 Start Frontend Development Server

```cmd
npm run dev
```

You should see:
```
  VITE v5.0.8  ready in 500 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h to show help
```

### 4.6 Open Application

Open your browser and go to:
```
http://localhost:5173
```

You should see the Nyaya Mitra application!

**Keep this terminal running!**

---

## Part 5: Testing the Application

### 5.1 Test Registration

1. Go to http://localhost:5173
2. Click "Register here"
3. Fill in the form:
   - Full Name: Test User
   - Email: test@example.com
   - Password: TestPassword123!
   - College Name: Test College (optional)
4. Click "Register"
5. You should be redirected to the dashboard

### 5.2 Test Login

1. Logout if logged in
2. Go to login page
3. Enter credentials:
   - Email: test@example.com
   - Password: TestPassword123!
4. Click "Login"
5. Should redirect to dashboard

### 5.3 Test Features

From the dashboard, test each feature:

**Chat:**
- Click "Legal Chat"
- Ask: "What is IPC Section 499?"
- Wait for AI response (may take 10-30 seconds first time)

**Case Analyzer:**
- Click "Case Analyzer"
- Fill in complaint details
- Click "Analyze Case"
- View validity score

**Document Generator:**
- Click "Document Generator"
- Select a document type
- Fill in the form
- Generate document

**Legal Aid Search:**
- Click "Legal Aid Search"
- Enter location (e.g., "Delhi")
- Search for providers

**Evidence Guide:**
- Click "Evidence Guide"
- Select case type
- View evidence collection steps

**Emergency SOS:**
- Click "Emergency SOS" (red button in navbar)
- View emergency contacts

---

## Part 6: Troubleshooting

### Issue: Backend won't start

**Error: "Address already in use"**
```cmd
# Find process using port 8000
netstat -ano | findstr :8000

# Kill the process (replace PID with actual number)
taskkill /PID <PID> /F

# Restart backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Error: "Database connection failed"**
- Check PostgreSQL is running:
  ```cmd
  # Check if PostgreSQL service is running
  sc query postgresql-x64-14
  
  # Start if not running
  net start postgresql-x64-14
  ```
- Verify DATABASE_URL in `.env` is correct
- Test connection:
  ```cmd
  psql -U postgres -d nyaya_mitra
  ```

**Error: "Module not found"**
```cmd
# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: Frontend won't start

**Error: "Port 5173 already in use"**
```cmd
# Find and kill process
netstat -ano | findstr :5173
taskkill /PID <PID> /F

# Or use different port
npm run dev -- --port 3000
```

**Error: "Cannot find module"**
```cmd
# Delete node_modules and reinstall
rmdir /s /q node_modules
npm install
```

### Issue: Ollama not responding

**Check Ollama is running:**
```cmd
# Test Ollama
curl http://localhost:11434/api/tags

# If not working, restart Ollama
# Close Ollama from system tray
# Start Ollama again from Start menu
```

**Model not found:**
```cmd
# Re-download model
ollama pull mistral:7b
```

### Issue: Chat responses are slow

- First response is always slow (model loading)
- Subsequent responses should be faster
- Ensure no other heavy applications are running
- Check CPU/RAM usage in Task Manager

### Issue: CORS errors in browser

- Check backend CORS configuration in `main.py`
- Ensure frontend URL is in CORS_ORIGINS
- Restart backend after changes

---

## Part 7: Stopping the Application

### Stop Backend:
- Go to backend terminal
- Press `Ctrl+C`
- Deactivate virtual environment:
  ```cmd
  deactivate
  ```

### Stop Frontend:
- Go to frontend terminal
- Press `Ctrl+C`

### Stop Ollama:
- Right-click Ollama icon in system tray
- Click "Quit Ollama"

### Stop PostgreSQL (optional):
```cmd
net stop postgresql-x64-14
```

---

## Part 8: Starting Again Later

### Quick Start Commands:

**Terminal 1 - Backend:**
```cmd
cd backend
.venv\Scripts\activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```cmd
cd frontend
npm run dev
```

**Make sure:**
- PostgreSQL is running
- Ollama is running (check system tray)

---

## Part 9: Development Tips

### View Backend Logs
Backend logs appear in the terminal where you ran `uvicorn`.

### View Frontend Logs
Frontend logs appear in:
- Terminal (build errors)
- Browser console (F12 → Console tab)

### API Documentation
Visit http://localhost:8000/docs for interactive API documentation.

### Database Management

**View data:**
```cmd
psql -U postgres -d nyaya_mitra

# List tables
\dt

# View users
SELECT * FROM users;

# Exit
\q
```

### Reset Database
```cmd
# Drop and recreate database
psql -U postgres -c "DROP DATABASE nyaya_mitra;"
psql -U postgres -c "CREATE DATABASE nyaya_mitra;"

# Reinitialize
cd backend
.venv\Scripts\activate
python -c "from database import init_db; init_db()"
python seed_emergency_contacts.py
python seed_legal_aid_providers.py
```

---

## Part 10: Common Development Tasks

### Update Backend Code
1. Make changes to Python files
2. Backend auto-reloads (if using `--reload` flag)
3. Check terminal for errors

### Update Frontend Code
1. Make changes to React files
2. Frontend auto-reloads in browser
3. Check browser console for errors

### Add New Python Package
```cmd
cd backend
.venv\Scripts\activate
pip install package-name
pip freeze > requirements.txt
```

### Add New NPM Package
```cmd
cd frontend
npm install package-name
```

### Run Tests
```cmd
# Backend tests
cd backend
.venv\Scripts\activate
pytest

# Frontend tests (if configured)
cd frontend
npm test
```

---

## System Requirements

**Minimum:**
- CPU: 4 cores
- RAM: 8 GB
- Disk: 10 GB free
- Internet: For downloading models

**Recommended:**
- CPU: 6+ cores
- RAM: 16 GB
- Disk: 20 GB free
- SSD for better performance

---

## Performance Tips

1. **Close unnecessary applications** when running Ollama
2. **Use SSD** for better database and model loading performance
3. **Increase RAM** if experiencing slowness
4. **Use smaller model** if needed:
   ```cmd
   ollama pull mistral:7b-instruct-q4_0
   ```
   Update `.env`:
   ```env
   OLLAMA_MODEL=mistral:7b-instruct-q4_0
   ```

---

## Security Notes for Local Development

- ✅ Use strong passwords for PostgreSQL
- ✅ Don't commit `.env` file to Git
- ✅ Change JWT_SECRET before deploying
- ✅ Use HTTPS in production
- ✅ Keep dependencies updated

---

## Getting Help

**Check logs:**
- Backend: Terminal where uvicorn is running
- Frontend: Browser console (F12)
- Database: PostgreSQL logs in installation directory

**Common log locations:**
- PostgreSQL: `C:\Program Files\PostgreSQL\14\data\log\`
- Ollama: Check Ollama app logs

**Resources:**
- FastAPI docs: https://fastapi.tiangolo.com
- React docs: https://react.dev
- Ollama docs: https://ollama.ai/docs
- PostgreSQL docs: https://www.postgresql.org/docs/

---

## Success Checklist

- [ ] Python installed and working
- [ ] Node.js installed and working
- [ ] PostgreSQL installed and running
- [ ] Ollama installed and model downloaded
- [ ] Backend virtual environment created
- [ ] Backend dependencies installed
- [ ] Database initialized and seeded
- [ ] Backend server running on port 8000
- [ ] Frontend dependencies installed
- [ ] Frontend server running on port 5173
- [ ] Can access http://localhost:5173
- [ ] Can register and login
- [ ] Chat feature works (AI responds)
- [ ] All features tested

---

## Next Steps

Once everything is working locally:

1. ✅ Test all features thoroughly
2. ✅ Make any necessary code changes
3. ✅ Commit your code to Git
4. ⏭️ Follow AWS deployment guide for production
5. ⏭️ Set up CI/CD pipeline
6. ⏭️ Add monitoring and logging

---

**Congratulations! You now have Nyaya Mitra running locally! 🎉**

For deployment to AWS, refer to `AWS_MVP_DEPLOYMENT_GUIDE.md`.
