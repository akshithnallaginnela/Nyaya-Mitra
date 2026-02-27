# Nyaya Mitra

AI-powered legal assistance platform for Indian college students facing legal challenges, false accusations, and extortion.

## Features

- **Legal Rights Query System**: AI chatbot for instant legal guidance
- **Case Validity Checker**: Analyze complaint strength and validity
- **Step-by-Step Guidance**: Action plans with timelines
- **Document Generator**: Generate legal letters, RTI applications, counter-petitions
- **Free Legal Aid Connector**: Find and connect with legal services
- **Multilingual Support**: English, Hindi, and regional Indian languages
- **Evidence Documentation Guide**: Learn how to collect and preserve evidence
- **Emergency SOS**: Quick access to emergency contacts and crisis support

## Tech Stack

### Frontend
- React.js with TypeScript
- Chakra UI + Tailwind CSS
- Vite

### Backend
- Python FastAPI
- PostgreSQL
- SQLAlchemy

### AI/ML
- Ollama + Mistral 7B
- LangChain
- Chroma Vector Database
- Sentence Transformers

## Setup Instructions

### Prerequisites
- Python 3.10+
- Node.js 16+
- Docker and Docker Compose
- Git

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
copy .env.example .env
# Edit .env with your configuration

# Start PostgreSQL with Docker
cd ..
docker-compose up -d

# Run database migrations
cd backend
alembic upgrade head

# Start the backend server
python main.py
```

The backend will be available at `http://localhost:8000`

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

The frontend will be available at `http://localhost:3000`

### Ollama Setup

```bash
# Install Ollama (visit https://ollama.ai for installation instructions)

# Pull Mistral 7B model
ollama pull mistral:7b

# Start Ollama server
ollama serve
```

## Development

### Running Tests

Backend:
```bash
cd backend
pytest
```

Frontend:
```bash
cd frontend
npm test
```

### Code Quality

Backend:
```bash
cd backend
black .
flake8 .
mypy .
```

Frontend:
```bash
cd frontend
npm run lint
```

## Deployment

### Frontend (Vercel)
1. Push code to GitHub
2. Connect repository to Vercel
3. Configure environment variables
4. Deploy

### Backend (Render)
1. Push code to GitHub
2. Create new Web Service on Render
3. Connect repository
4. Configure environment variables
5. Deploy

## Project Structure

```
nyaya-mitra/
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   ├── models/
│   ├── routes/
│   ├── services/
│   └── utils/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── utils/
│   ├── package.json
│   └── vite.config.ts
├── docker-compose.yml
└── README.md
```

## Contributing

This is a hackathon project. Contributions are welcome!

## License

MIT License

## Support

For support, email support@nyayamitra.com or open an issue on GitHub.

## Acknowledgments

- Built for Indian college students facing legal challenges
- Powered by open-source technologies
- Zero infrastructure cost

---

**Nyaya Mitra** - Empowering 10M+ students with instant, free legal guidance 🚀
