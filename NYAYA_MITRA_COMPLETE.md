# Nyaya Mitra - Complete Project & Tech Stack Guide

## Table of Contents
1. [Project Overview](#project-overview)
2. [Problem & Solution](#problem--solution)
3. [Features](#features)
4. [Complete Tech Stack](#complete-tech-stack)
5. [Architecture](#architecture)
6. [Development Timeline](#development-timeline)
7. [Setup & Implementation](#setup--implementation)
8. [Deployment](#deployment)
9. [Demo & Pitch](#demo--pitch)

---

## Project Overview

**Nyaya Mitra** is an AI-powered legal assistance platform designed exclusively for Indian college students facing legal challenges, false accusations, extortion, and threats.

### The Vision
Empower 10M+ vulnerable Indian students with instant, free, AI-powered legal guidance in their language, 24/7.

### Key Stats
- **Problem Size**: 10M+ college students affected
- **Cost**: ₹0 (completely free stack)
- **Timeline**: 2 weeks to working MVP
- **Impact**: Protect students from exploitation
- **Tech**: Modern RAG + Open-source

---

## Problem & Solution

### The Problem

**What students face:**
- False legal complaints (hostel disputes, academic misconduct)
- Extortion using legal threats
- Complete lack of legal knowledge
- Fear and panic when receiving legal notices
- Tendency to make bad decisions (bribes, unfair settlements)

**Why it matters:**
- No student-specific legal solution exists
- Generic legal apps don't understand student scenarios
- Legal aid is complex to access
- Students are vulnerable and exploitable
- Problem affects millions annually

### The Solution

**Nyaya Mitra provides:**
- ✅ Instant legal guidance based on Indian law
- ✅ Case validity analysis (frivolous vs legitimate)
- ✅ Step-by-step action plans
- ✅ Legal document generation
- ✅ Free legal aid service connections
- ✅ Multilingual support (Hindi, English, regional)
- ✅ 24/7 availability
- ✅ Completely FREE

### Example Use Case

```
Student Arjun receives: "You damaged hostel property. Pay ₹50,000"

WITHOUT Nyaya Mitra:
- Panics
- Doesn't know rights
- Considers paying bribe
- Makes legal mistakes

WITH Nyaya Mitra:
- Opens app
- Describes situation to AI
- Gets legal analysis: "This is likely frivolous - no evidence"
- Gets action plan
- Gets response letter template
- Connects with legal aid
- Protects himself legally
```

---

## Features

### 8 Core Features (MVP)

**1. Legal Rights Query System**
- AI chatbot for legal questions
- Natural language input: "False hostel damage complaint - what to do?"
- Instant response with:
  - Applicable IPC/CrPC sections
  - Legal rights explanation
  - Action steps
  - Links to legal aid

**2. Case Validity Checker**
- Upload complaint text or document
- AI analyzes legal strength
- Output: "Validity Score: 15% - WEAK"
- Explains why (missing evidence, unclear timeline, etc.)
- Recommendation: File counter-petition

**3. Step-by-Step Response Guidance**
- Immediate actions (Day 1)
- Documentation procedures (Days 2-3)
- Evidence collection (Week 1)
- Legal response (Week 2)
- Court procedures (Week 3+)

**4. Document Generator**
- Response letter to complaint
- RTI application
- Response to legal notice
- Demand letter
- Counter-petition
- 10+ ready-to-use templates

**5. Free Legal Aid Connector**
- Search by city/district
- District legal services authority
- Student legal cells
- Pro bono lawyer networks
- One-click calling
- Eligibility checker

**6. Multilingual Support**
- English, Hindi, Tamil, Telugu
- Bengali, Gujarati, Marathi
- Legal terminology accuracy
- Context-aware translation

**7. Evidence Documentation Guide**
- How to photograph evidence
- Record conversations legally
- Preserve digital evidence
- Create witness statements
- What courts accept

**8. Emergency SOS Feature**
- One-tap emergency contacts
- Police complaint procedures
- Campus security info
- Mental health support
- Crisis counseling resources

---

## Complete Tech Stack

### Summary: COMPLETELY FREE & OPEN-SOURCE
**Total Infrastructure Cost: ₹0**

### Frontend Technologies

#### Web Framework
- **React.js** (FREE, open-source)
  - Component-based architecture
  - Mobile-responsive by default
  - Excellent for chat interfaces
  - Large community + resources

#### UI Components
- **Chakra UI** (FREE, open-source)
  - Pre-built professional components
  - Accessibility built-in
  - Customizable theming
  - Great documentation

#### Styling
- **Tailwind CSS** (FREE, open-source)
  - Utility-first CSS framework
  - Rapid development
  - Mobile-first responsive design
  - No design skills needed

#### Chat Interface
- **Rasa Open Source** or **React Chat UI** (FREE)
  - Conversational components
  - Easy to customize
  - Integrates with NLP

#### Document Scanning
- **Tesseract.js** (FREE, open-source)
  - Client-side OCR
  - Works in browser
  - No server needed

#### Mobile App
- **React Native** (FREE, open-source)
  - Write once, run iOS + Android
  - Share code with web
  - Strong community

### Backend Technologies

#### API Framework
- **Python FastAPI** (FREE, open-source)
  - High performance (3x faster than Django)
  - Auto-generated API docs (Swagger)
  - Perfect for AI/ML integration
  - Async support
  - Modern Python syntax

#### Server
- **Uvicorn** (FREE, open-source)
  - ASGI server for FastAPI
  - Production-ready
  - Lightweight

#### Database Interface
- **SQLAlchemy** (FREE, open-source)
  - Object-relational mapper
  - Support for multiple databases
  - Type hints
  - Migration support

### AI/ML Technologies

#### LLM Runner
- **Ollama** (FREE, open-source)
  - Run language models locally
  - No API costs (save ₹1000s)
  - Privacy-first (data stays on your server)
  - Simple installation
  - Works on CPU (no GPU needed)
  - ~10 minute setup

#### Language Model
- **Mistral 7B** (FREE, open-source)
  - High quality responses
  - Only 7B parameters = ~4GB RAM
  - Better than larger closed models for legal tasks
  - Easy to run locally
  - Can be optimized (quantized to 2-4 bits)

**Why Mistral 7B?**
```
✅ No API costs
✅ Privacy preserved
✅ Fast enough (2-5 sec responses)
✅ Legal knowledge in training
✅ Better than ChatGPT for grounded tasks
✅ Can be fine-tuned
✅ Works without GPU
```

#### LLM Integration
- **LangChain** (FREE, open-source)
  - Simplifies LLM integration
  - Prompt templates and chaining
  - Memory management
  - RAG support
  - Excellent documentation

#### RAG Framework
- **LlamaIndex** (FREE, open-source)
  - Specialized for Retrieval-Augmented Generation
  - Easy document indexing
  - Semantic search
  - Multiple storage backends

**What is RAG?**
```
Traditional LLM:
Question → LLM → Answer (may be wrong/hallucinated)

RAG:
Question → Search legal database → Find relevant docs 
→ Pass docs + question to LLM → Answer based on facts
= More accurate, less hallucination, grounded in law
```

#### Text Embeddings
- **Sentence-Transformers** (FREE, open-source)
  - Convert text to vectors (embeddings)
  - Understand semantic meaning
  - Multi-language support
  - Pre-trained models

#### Vector Database
- **Chroma** (FREE, open-source)
  - Lightweight vector database
  - Perfect for RAG
  - In-memory or SQLite storage
  - No server needed
  - Simple to use

#### NLP Libraries
- **spaCy** (FREE, open-source)
  - Named entity recognition
  - Text classification
  - Tokenization and parsing
  - Pre-trained models
  - Fast and accurate

- **IndicNLP** (FREE, open-source)
  - Support for 10+ Indian languages
  - Hindi, Tamil, Telugu, Bengali, etc.
  - Tokenization, parsing
  - Language detection

#### Machine Learning
- **Scikit-learn** (FREE, open-source)
  - Case validity scoring
  - Text vectorization
  - Classification models
  - No GPU needed

### Database

#### Primary Database
- **PostgreSQL** (FREE, open-source)
  - Robust and reliable
  - ACID compliance
  - JSON support
  - Full-text search
  - Industry standard

**Schema:**
```sql
users (user_id, email, language, created_at)
queries (query_id, user_id, question, response)
cases (case_id, user_id, complaint, validity_score)
documents (doc_id, user_id, type, content)
legal_references (ref_id, section, description)
legal_aid (aid_id, city, name, phone, address)
```

### Security

- **JWT** (FREE) - Authentication
- **bcrypt** (FREE) - Password hashing
- **Let's Encrypt** (FREE) - SSL/HTTPS

### Deployment

#### Containerization
- **Docker** (FREE, open-source)
  - Package entire application
  - Consistent everywhere

#### Frontend Hosting
- **Vercel** (FREE tier)
  - Optimized for React
  - Zero-config deployment
  - CDN included
  - Auto-scales

#### Backend Hosting
- **Render** or **Railway** (FREE tier)
  - GitHub integration
  - PostgreSQL included
  - Environment variables
  - One-click deployment

#### Version Control
- **Git + GitHub** (FREE)
  - Code repository
  - CI/CD integration
  - Collaboration

### Development Tools (All FREE)

- **VS Code** - Code editor
- **Postman** - API testing
- **pgAdmin** - Database management

### Tech Stack Summary

```
FRONTEND (0 Cost)
├─ React.js
├─ Chakra UI
├─ Tailwind CSS
├─ Tesseract.js (OCR)
└─ React Native (mobile)

BACKEND (0 Cost)
├─ Python FastAPI
├─ Uvicorn
└─ SQLAlchemy

AI/ML (0 Cost)
├─ Ollama (LLM runner)
├─ Mistral 7B (language model)
├─ LangChain (integration)
├─ LlamaIndex (RAG)
├─ Sentence-Transformers (embeddings)
├─ Chroma (vector DB)
├─ spaCy (NLP)
├─ IndicNLP (Indian languages)
└─ Scikit-learn (ML)

DATABASE (0 Cost)
├─ PostgreSQL (primary)
└─ Chroma (vector storage)

SECURITY (0 Cost)
├─ JWT (auth)
├─ bcrypt (passwords)
└─ Let's Encrypt (HTTPS)

HOSTING (0 Cost)
├─ Vercel (frontend)
├─ Render/Railway (backend)
└─ GitHub (CI/CD)

TOTAL COST: ₹0
```

---

## Architecture

### System Diagram

```
┌────────────────────────────────────┐
│    User Interface Layer            │
├────────────────────────────────────┤
│  Web (React) │ Mobile (React Native)
└────────────┬──────────────────────┘
             │
    ┌────────▼───────────┐
    │  FastAPI REST API  │
    ├────────────────────┤
    │ /api/chat/query    │
    │ /api/case/analyze  │
    │ /api/doc/generate  │
    │ /api/legal-aid/*   │
    └────────┬────────────┘
             │
    ┌────────▼──────────────────┐
    │   AI/ML Processing Layer   │
    ├────────────────────────────┤
    │ LangChain + LlamaIndex     │
    │ Ollama + Mistral 7B        │
    │ spaCy + IndicNLP           │
    │ Sentence-Transformers      │
    └────────┬────────────────────┘
             │
    ┌────────┴────────────┐
    │                     │
┌───▼──────┐        ┌────▼────┐
│PostgreSQL│        │  Chroma │
│ Database │        │Vector DB│
└──────────┘        └─────────┘
    │                     │
    └────────┬────────────┘
             │
    ┌────────▼──────────────────┐
    │  Knowledge Base Layer      │
    ├────────────────────────────┤
    │ IPC Sections (500+)        │
    │ CrPC Sections (400+)       │
    │ Sample Q&A (50+)           │
    │ Case Laws (100+)           │
    │ Legal Aid Directory        │
    └────────────────────────────┘
```

### RAG (Retrieval-Augmented Generation) Flow

```
STUDENT QUESTION
    ↓
Convert to embedding (Sentence-Transformers)
    ↓
Search Chroma vector database
    ↓
Retrieve top 5 relevant legal documents
(IPC sections, case laws, precedents)
    ↓
LangChain creates prompt:
"Based on these legal documents: [retrieved]
Answer this question: [student question]"
    ↓
Send to Ollama → Mistral 7B
    ↓
Mistral generates response:
- Applicable IPC/CrPC sections
- Legal explanation
- Action steps
- Links to legal aid
    ↓
Return to student with sources
```

---

## Development Timeline

### 14-Day Hackathon Plan

**Days 1-2: Setup & Infrastructure**
```
[ ] Install Python 3.10+, Node.js, VS Code, Git
[ ] Create GitHub repo
[ ] Download & install Ollama
[ ] Pull Mistral 7B model
[ ] Create React project
[ ] Set up FastAPI project
[ ] Create PostgreSQL database
[ ] Create Vercel + Render accounts
```

**Days 3-4: Backend Foundation**
```
[ ] Design database schema
[ ] Create SQLAlchemy models
[ ] Set up FastAPI endpoints
[ ] Create authentication (JWT)
[ ] Create API request/response schemas
[ ] Test with Postman
```

**Day 5: AI/ML Pipeline**
```
[ ] Collect legal documents (IPC, CrPC, Q&A)
[ ] Create embeddings for documents
[ ] Set up Chroma vector database
[ ] Test Ollama + Mistral 7B
[ ] Build RAG pipeline
[ ] Test end-to-end AI responses
```

**Days 6-8: Frontend**
```
[ ] Create React structure
[ ] Build Chat component
[ ] Build Case Analyzer component
[ ] Build Document Generator
[ ] Build Legal Aid Finder
[ ] Connect to backend APIs
[ ] Apply Chakra UI styling
```

**Days 9-10: Features & Integration**
```
[ ] Knowledge Base search
[ ] Emergency SOS feature
[ ] Evidence guide
[ ] End-to-end testing
[ ] Fix bugs
```

**Days 11-12: Polish & Optimization**
```
[ ] Multilingual support (English + Hindi)
[ ] Mobile responsive design
[ ] Performance optimization
[ ] Security review
[ ] Bug fixes
```

**Days 13-14: Deployment & Demo**
```
[ ] Push code to GitHub
[ ] Deploy to Vercel (frontend)
[ ] Deploy to Render (backend)
[ ] Practice demo 10+ times
[ ] Record backup video
[ ] Prepare presentation
```

**Total Effort**: ~75-80 hours (~5-6 hours/day)

---

## Setup & Implementation

### Prerequisites

```
Hardware:
- CPU: 4+ cores
- RAM: 8GB minimum (16GB better for LLM)
- Storage: 30GB (for model + code)

Software:
- Python 3.10+
- Node.js 16+
- Git
- VS Code (or any editor)
```

### Quick Start

```bash
# 1. Clone repo
git clone https://github.com/team/nyaya-mitra.git
cd nyaya-mitra

# 2. Backend setup
cd backend
python -m venv venv
source venv/bin/activate

pip install fastapi uvicorn sqlalchemy psycopg2-binary
pip install langchain llamaindex sentence-transformers chromadb
pip install spacy scikit-learn pydantic pyjwt python-dotenv

python -m spacy download en_core_web_sm

# 3. Frontend setup
cd ../frontend
npm install @chakra-ui/react @emotion/react @emotion/styled
npm install axios react-router-dom i18next

# 4. Create .env file
cat > ../backend/.env << EOF
DATABASE_URL=postgresql://user:pwd@localhost:5432/nyaya
OLLAMA_BASE_URL=http://localhost:11434
JWT_SECRET=your-secret
CORS_ORIGINS=http://localhost:3000
EOF

# 5. Create database
createdb nyaya

# 6. Terminal 1: Run Ollama
ollama serve

# 7. Terminal 2: Download Mistral
ollama pull mistral

# 8. Terminal 3: Run backend
cd backend
python -m uvicorn main:app --reload

# 9. Terminal 4: Run frontend
cd frontend
npm start

# Access: http://localhost:3000
```

### Sample API Implementation

```python
# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio

app = FastAPI(title="Nyaya Mitra API")

# CORS
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:3000"])

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/api/chat/query")
async def chat_query(question: str):
    """Answer legal questions using RAG"""
    try:
        response = rag_pipeline.query(question)
        return {
            "response": response["answer"],
            "sources": response["sources"]
        }
    except Exception as e:
        return {"error": str(e)}, 500

@app.post("/api/case/analyze")
async def analyze_case(complaint: str):
    """Analyze case validity"""
    try:
        score = case_analyzer.analyze(complaint)
        return {
            "validity_score": score,
            "analysis": explanation
        }
    except Exception as e:
        return {"error": str(e)}, 500

@app.post("/api/documents/generate")
async def generate_doc(template: str, data: dict):
    """Generate legal documents"""
    try:
        doc = doc_generator.generate(template, data)
        return {"document": doc, "pdf_url": pdf_url}
    except Exception as e:
        return {"error": str(e)}, 500

@app.get("/api/legal-aid/{city}")
async def find_legal_aid(city: str):
    """Find legal aid services"""
    services = db.query(LegalAidService)\
        .filter_by(city=city).all()
    return {"services": services}
```

### Sample React Component

```jsx
// frontend/src/components/Chat.jsx
import React, { useState } from 'react';
import { Box, Input, Button, VStack, Text } from '@chakra-ui/react';
import axios from 'axios';

export default function Chat() {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSend = async () => {
        if (!input.trim()) return;

        // Add user message
        setMessages([...messages, 
            { role: 'user', content: input }
        ]);
        setInput('');
        setLoading(true);

        try {
            // Call API
            const response = await axios.post(
                '/api/chat/query',
                { question: input }
            );

            // Add AI response
            setMessages(prev => [...prev, {
                role: 'ai',
                content: response.data.response
            }]);
        } catch (error) {
            setMessages(prev => [...prev, {
                role: 'error',
                content: 'Error getting response'
            }]);
        }

        setLoading(false);
    };

    return (
        <VStack spacing={4} p={4}>
            <Box maxH="400px" overflowY="auto" w="100%">
                {messages.map((msg, i) => (
                    <Box key={i} mb={2} p={2}>
                        <Text>
                            <strong>{msg.role}:</strong> {msg.content}
                        </Text>
                    </Box>
                ))}
            </Box>

            <Input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask about your legal situation..."
                onKeyPress={(e) => 
                    e.key === 'Enter' && handleSend()
                }
            />
            <Button onClick={handleSend} isLoading={loading}>
                Send
            </Button>
        </VStack>
    );
}
```

---

## Deployment

### Deploy Frontend to Vercel

```
1. Go to vercel.com
2. Click "Add New" → "Project"
3. Import GitHub repo (frontend)
4. Set build settings:
   - Framework: React
   - Build command: npm run build
   - Output: build
5. Set environment variables:
   REACT_APP_API_URL=https://your-backend.onrender.com
6. Click Deploy

Result: https://your-project.vercel.app
```

### Deploy Backend to Render

```
1. Go to render.com
2. Click "New Web Service"
3. Connect GitHub repo (backend)
4. Configure:
   - Name: nyaya-mitra-api
   - Environment: Python 3.10
   - Build: pip install -r requirements.txt
   - Start: uvicorn main:app --host 0.0.0.0 --port $PORT
5. Add PostgreSQL service
6. Set env variables:
   DATABASE_URL=provided_by_render
   OLLAMA_BASE_URL=http://localhost:11434
   JWT_SECRET=your-secret
7. Deploy

Result: https://your-backend.onrender.com
```

### Update Frontend to Connect Backend

```
1. Get backend URL from Render
2. Update frontend .env:
   REACT_APP_API_URL=https://your-backend.onrender.com
3. Redeploy frontend

Test: Make API call from live frontend
```

---

## Demo & Pitch

### 3-Minute Demo Script

```
OPENING (30 seconds):
"Meet Arjun, a college student who received a legal notice 
claiming he damaged hostel property. He panics - doesn't know 
his rights. With Nyaya Mitra, he gets instant legal help."

FEATURE 1: CHAT (30 seconds):
"He asks: 'False hostel complaint, what should I do?'
AI responds with:
- Applicable IPC sections
- Legal rights
- Action plan
- Confidence: Complaint is frivolous"

FEATURE 2: CASE ANALYZER (30 seconds):
"He uploads the complaint.
System shows: 'Validity 15% - This is weak'
Why: No evidence, no witnesses, no timeline"

FEATURE 3: DOCUMENT GENERATOR (20 seconds):
"One click generates response letter.
Downloads PDF ready to submit."

FEATURE 4: LEGAL AID FINDER (20 seconds):
"Searches Delhi → Gets legal services
Phone, address, one-tap call
Connected with free legal help"

CLOSING (20 seconds):
"With Nyaya Mitra:
- Arjun goes from panic to protected
- From bribes to legal empowerment
- 10M+ students get justice
All completely free."
```

### Judge Talking Points

```
Innovation:
First AI legal assistant designed specifically for students

Social Impact:
10M+ students face legal exploitation - this solves a real problem

Technical Excellence:
Modern RAG architecture, grounded in actual legal documents,
better than ChatGPT for legal accuracy

Cost Efficiency:
Zero infrastructure costs, completely open-source

Scalability:
Built for millions of users, modern cloud architecture

Sustainability:
Multiple revenue models (freemium, institutional, government)

Execution:
Professional development plan, realistic timeline, clear roadmap
```

---

## Success Checklist

```
Before Demo Day:
✅ All 8 features working
✅ Frontend deployed & live
✅ Backend deployed & responsive
✅ Database working in cloud
✅ Mobile responsive design
✅ No errors in console
✅ Demo practiced 10+ times
✅ Presentation polished
✅ GitHub repo clean
✅ README comprehensive
✅ Backup video recorded
✅ Team well-rested

Expected Results:
✅ Working AI chatbot (50+ Q&A scenarios)
✅ Case validity checker (80%+ accuracy)
✅ 10+ legal document templates
✅ Legal aid database (10+ cities)
✅ Bilingual interface (English + Hindi)
✅ Mobile responsive
✅ Live demo URL
✅ Professional presentation
```

---

## FAQ

**Q: Can we really build in 2 weeks?**
A: Yes with focused effort. Start MVP, skip advanced features.

**Q: What if Ollama is slow?**
A: Use smaller model, quantization, or cloud deployment.

**Q: How much does this cost?**
A: ₹0. Completely free stack.

**Q: Where do we get legal data?**
A: Public sources (indiankanoon.org, government PDFs).

**Q: About AI accuracy?**
A: RAG improves accuracy by grounding in actual legal documents.

**Q: Legal liability?**
A: Add disclaimers throughout. Don't claim to replace lawyers.

**Q: What if deployment fails?**
A: Render and Vercel are very reliable. Test locally first.

---

## Resources

**Official Docs:**
- FastAPI: https://fastapi.tiangolo.com/
- LangChain: https://python.langchain.com/
- React: https://react.dev/
- Ollama: https://ollama.ai/

**Legal Data:**
- indiankanoon.org
- lex.similars.io
- legislature.gov.in

**Communities:**
- r/LocalLLMs
- r/FastAPI
- LangChain Discord

---

## Conclusion

**Nyaya Mitra** solves a real problem affecting 10M+ students using:
✅ Modern AI/ML (RAG architecture)
✅ Completely free tech stack (₹0)
✅ 2-week development timeline
✅ Real social impact
✅ Sustainable business model

You have everything needed. Build it! 🚀

---

**Good luck! Build something amazing!** 💪
