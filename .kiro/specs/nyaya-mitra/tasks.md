a # Implementation Plan: Nyaya Mitra

## Overview

This implementation plan breaks down the Nyaya Mitra AI-powered legal assistance platform into discrete, actionable coding tasks. The plan follows an incremental approach where each task builds on previous work, ensuring continuous integration and early validation of core functionality.

The implementation uses:
- **Frontend**: React.js with Chakra UI and Tailwind CSS
- **Backend**: Python FastAPI with SQLAlchemy
- **AI/ML**: Ollama with Mistral 7B, LangChain, Chroma vector database
- **Database**: PostgreSQL for structured data
- **Mobile**: React Native for cross-platform mobile apps

## Tasks

### Phase 1: Foundation and Infrastructure

- [ ] 1. Set up project structure and development environment
  - Create monorepo structure with frontend, backend, and mobile directories
  - Initialize Python FastAPI backend with virtual environment
  - Initialize React.js frontend with Vite and TypeScript
  - Set up PostgreSQL database with Docker Compose
  - Configure environment variables and secrets management
  - Set up Git repository with .gitignore for all platforms
  - Create README with setup instructions
  - _Requirements: All requirements depend on proper setup_

- [ ] 2. Implement database models and migrations
  - [ ] 2.1 Create SQLAlchemy base configuration and database connection
    - Set up SQLAlchemy engine with PostgreSQL connection
    - Create Base model class with common fields (id, created_at, updated_at)
    - Implement database session management with context managers
    - _Requirements: 9.3, 9.5_

  - [ ] 2.2 Implement User model with authentication fields
    - Create User model with email, password_hash, full_name, college_name, preferred_language
    - Add password hashing utilities using bcrypt with 10 rounds
    - Implement user validation methods
    - _Requirements: 9.1, 6.4_

  - [ ] 2.3 Implement Conversation and Message models
    - Create Conversation model with user relationship
    - Create Message model with role, content, citations, confidence_score
    - Set up foreign key relationships
    - _Requirements: 1.6_


  - [ ] 2.4 Implement CaseAnalysis and GeneratedDocument models
    - Create CaseAnalysis model with complaint_details, validity_score, score_breakdown
    - Create GeneratedDocument model with document_type, template_inputs, file_path
    - Set up relationships with User model
    - _Requirements: 2.1, 4.2_

  - [ ] 2.5 Implement LegalAidProvider model
    - Create LegalAidProvider model with name, organization_type, specializations, languages_supported
    - Add location fields (city, state) and contact information
    - Create indexes for efficient searching by location and specialization
    - _Requirements: 5.1, 5.2_

  - [ ]* 2.6 Write property tests for data models
    - **Property 44: Password encryption strength** - Verify bcrypt with 10+ rounds
    - **Property 48: Account deletion completeness** - Verify cascade deletion of related data
    - **Validates: Requirements 9.1, 9.5**

- [ ] 3. Implement authentication system with JWT
  - [ ] 3.1 Create JWT token generation and validation utilities
    - Implement JWT token creation with 24-hour expiration
    - Create token validation middleware for protected routes
    - Add token refresh endpoint logic
    - _Requirements: 9.2_

  - [ ] 3.2 Implement authentication endpoints
    - Create POST /api/auth/register endpoint with email validation
    - Create POST /api/auth/login endpoint with credential verification
    - Create POST /api/auth/refresh endpoint for token renewal
    - Create DELETE /api/auth/account endpoint for account deletion
    - _Requirements: 9.1, 9.2, 9.5_

  - [ ]* 3.3 Write property tests for authentication
    - **Property 45: JWT token expiration** - Verify 24-hour expiration
    - **Property 49: Session timeout** - Verify 30-minute inactivity timeout
    - **Validates: Requirements 9.2, 9.7**

  - [ ]* 3.4 Write unit tests for authentication edge cases
    - Test invalid email formats
    - Test weak passwords
    - Test duplicate email registration
    - Test invalid credentials
    - Test expired token handling
    - _Requirements: 9.1, 9.2_


- [ ] 4. Checkpoint - Ensure database and authentication work
  - Run all tests to verify database models and authentication
  - Manually test registration and login flows
  - Verify JWT tokens are properly generated and validated
  - Ask the user if questions arise

### Phase 2: AI/ML Infrastructure

- [ ] 5. Set up vector database and RAG system
  - [ ] 5.1 Initialize Chroma vector database
    - Set up Chroma client with persistent storage
    - Create collection for legal documents with metadata schema
    - Configure embedding model (sentence-transformers)
    - _Requirements: 10.1_

  - [ ] 5.2 Implement document ingestion pipeline
    - Create script to load IPC sections, CrPC sections, case laws
    - Generate embeddings for each document
    - Store documents in Chroma with metadata (source, category, language, date)
    - Create indexing for efficient retrieval
    - _Requirements: 10.2_

  - [ ] 5.3 Implement RAG retrieval system
    - Create query embedding generation
    - Implement similarity search to retrieve top 5 documents
    - Add metadata filtering by language and category
    - Calculate relevance scores for retrieved documents
    - _Requirements: 10.1, 1.3_

  - [ ]* 5.4 Write property tests for RAG system
    - **Property 50: Retrieval count consistency** - Verify exactly 5 documents retrieved
    - **Property 51: Response grounding** - Verify responses use retrieved content
    - **Property 52: Knowledge gap acknowledgment** - Verify low-confidence handling
    - **Validates: Requirements 10.1, 10.3, 10.5**


- [ ] 6. Integrate Ollama and LangChain
  - [ ] 6.1 Set up Ollama with Mistral 7B model
    - Install and configure Ollama
    - Download Mistral 7B model
    - Create Python client for Ollama API
    - Configure model parameters (temperature=0.3 for consistency)
    - _Requirements: 1.1_

  - [ ] 6.2 Implement LangChain orchestration
    - Create LangChain prompt templates for legal queries
    - Implement chain for RAG: retrieve → format context → generate response
    - Add response parsing and citation extraction
    - Implement confidence scoring based on retrieval relevance
    - _Requirements: 1.3, 1.4, 1.7_

  - [ ] 6.3 Implement multilingual query processing
    - Add language detection using langdetect
    - Create language-specific prompt templates
    - Implement query translation if needed
    - Ensure responses match input language
    - _Requirements: 1.2, 6.5_

  - [ ]* 6.4 Write property tests for AI response generation
    - **Property 1: Response time bound** - Verify <5 second response time
    - **Property 2: Language consistency** - Verify response language matches query
    - **Property 3: RAG retrieval requirement** - Verify RAG retrieval before generation
    - **Property 7: Low confidence disclaimer** - Verify disclaimer for confidence <0.7
    - **Validates: Requirements 1.1, 1.2, 1.3, 1.7**

  - [ ]* 6.5 Write unit tests for edge cases
    - Test very long queries (>2000 characters)
    - Test queries with special characters
    - Test queries in unsupported languages
    - Test Ollama service unavailability
    - _Requirements: 1.1, 1.2_


### Phase 3: Core Feature Implementation - Chat System

- [ ] 7. Implement chat API endpoints
  - [ ] 7.1 Create POST /api/chat/query endpoint
    - Accept user query and language preference
    - Call RAG system to retrieve context
    - Generate AI response using Ollama
    - Extract citations from response
    - Save message to database
    - Return response with citations and confidence score
    - _Requirements: 1.1, 1.3, 1.4_

  - [ ] 7.2 Create GET /api/chat/history endpoint
    - Retrieve conversation history for authenticated user
    - Support pagination for long conversations
    - Include message metadata (timestamps, confidence scores)
    - _Requirements: 1.6_

  - [ ] 7.3 Implement WebSocket endpoint for streaming responses
    - Create WebSocket connection handler at /api/chat/stream
    - Stream AI response tokens in real-time
    - Handle connection errors and reconnection
    - _Requirements: 1.1_

  - [ ] 7.4 Implement ambiguity detection and clarification
    - Add confidence threshold check (0.6) for ambiguous queries
    - Generate clarifying questions when confidence is low
    - Store clarification state in conversation context
    - _Requirements: 1.5_

  - [ ]* 7.5 Write property tests for chat system
    - **Property 4: Citation presence** - Verify citations when legal references exist
    - **Property 5: Ambiguity handling** - Verify clarifying questions for confidence <0.6
    - **Property 6: Context preservation** - Verify multi-message context access
    - **Validates: Requirements 1.4, 1.5, 1.6**

  - [ ]* 7.6 Write unit tests for chat edge cases
    - Test empty query handling
    - Test maximum conversation length
    - Test concurrent requests from same user
    - Test database save failures
    - _Requirements: 1.1, 1.6_


- [ ] 8. Checkpoint - Verify chat system functionality
  - Run all chat-related tests
  - Manually test chat queries in multiple languages
  - Verify RAG retrieval and citation extraction
  - Verify conversation history persistence
  - Ask the user if questions arise

### Phase 4: Case Validity Assessment

- [ ] 9. Implement case analysis system
  - [ ] 9.1 Create case validity scoring algorithm
    - Implement evidence strength analysis (0-40 points)
    - Implement legal basis checking (0-30 points)
    - Implement procedural compliance checking (0-20 points)
    - Implement timeline reasonableness analysis (0-10 points)
    - Calculate total validity score (0-100)
    - _Requirements: 2.1, 2.2_

  - [ ] 9.2 Implement weakness identification logic
    - Analyze score breakdown to identify weak areas
    - Generate specific weakness descriptions
    - Provide actionable recommendations for improvement
    - _Requirements: 2.4, 2.6_

  - [ ] 9.3 Create POST /api/case/analyze endpoint
    - Accept complaint details (evidence, allegations, procedures, timeline)
    - Run validity scoring algorithm
    - Generate detailed breakdown and recommendations
    - Add legal consultation recommendation for high scores (>70)
    - Save analysis to database
    - Return complete analysis results
    - _Requirements: 2.1, 2.3, 2.5_

  - [ ] 9.4 Create GET /api/case/history endpoint
    - Retrieve past case analyses for authenticated user
    - Support filtering by validity score range
    - Include full analysis details
    - _Requirements: 2.1_

