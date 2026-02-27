ks a # Implementation Plan: Nyaya Mitra

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


  - [ ]* 9.5 Write property tests for case analysis
    - **Property 8: Validity score bounds** - Verify score is 0-100
    - **Property 9: Score breakdown completeness** - Verify all components present
    - **Property 10: Weakness highlighting for low scores** - Verify weaknesses for score <40
    - **Property 11: Legal consultation recommendation for high scores** - Verify recommendation for score >70
    - **Property 12: Missing elements identification** - Verify missing elements identified
    - **Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5, 2.6**

  - [ ]* 9.6 Write unit tests for case analysis edge cases
    - Test minimal complaint details
    - Test maximum complaint details
    - Test missing required fields
    - Test invalid data types
    - _Requirements: 2.1, 2.2_

### Phase 5: Action Plans and Document Generation

- [ ] 10. Implement action plan generation
  - [ ] 10.1 Create action plan generator
    - Generate numbered steps based on case type
    - Add specific timelines for each step
    - Identify and highlight legal deadlines
    - Sort steps by urgency (urgent first)
    - Add time estimates for each step
    - Include alternative approaches when applicable
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6_

  - [ ] 10.2 Integrate action plan with chat system
    - Add action plan generation as chat command
    - Store generated action plans in database
    - Allow users to retrieve and update action plans
    - _Requirements: 3.1_

  - [ ]* 10.3 Write property tests for action plans
    - **Property 13: Numbered steps structure** - Verify sequential numbering from 1
    - **Property 14: Timeline presence** - Verify each step has timeline
    - **Property 15: Deadline highlighting** - Verify legal deadlines highlighted
    - **Property 16: Urgency ordering** - Verify urgent steps (>7/10) appear first
    - **Property 17: Time estimate presence** - Verify each step has time estimate
    - **Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5**


- [ ] 11. Implement document generation system
  - [ ] 11.1 Create document templates using Jinja2
    - Create template for legal letters
    - Create template for RTI applications
    - Create template for counter-petitions
    - Define required and optional fields for each template
    - Add proper legal formatting and language
    - _Requirements: 4.3, 4.4_

  - [ ] 11.2 Implement document generator service
    - Load and validate Jinja2 templates
    - Validate user inputs against template requirements
    - Render templates with user data
    - Generate PDF using ReportLab
    - Generate editable text version
    - Add placeholders for missing optional fields
    - _Requirements: 4.2, 4.5, 4.6_

  - [ ] 11.3 Create document generation endpoints
    - Create GET /api/documents/templates endpoint to list templates
    - Create POST /api/documents/generate endpoint
    - Create GET /api/documents/{id} endpoint to retrieve documents
    - Store generated documents with metadata
    - _Requirements: 4.1, 4.2_

  - [ ] 11.4 Add attachment checklist generation
    - Define attachment requirements for each document type
    - Generate checklist based on document type and user inputs
    - Include checklist in generated document
    - _Requirements: 4.7_

  - [ ]* 11.5 Write property tests for document generation
    - **Property 18: Form presentation** - Verify form structure for each document type
    - **Property 19: Document generation from valid input** - Verify successful generation
    - **Property 20: Dual format output** - Verify PDF and text formats
    - **Property 21: Placeholder inclusion** - Verify placeholders for empty optional fields
    - **Property 22: Attachment checklist** - Verify checklist for documents requiring attachments
    - **Validates: Requirements 4.1, 4.2, 4.5, 4.6, 4.7**

  - [ ]* 11.6 Write unit tests for document generation edge cases
    - Test missing required fields
    - Test invalid template names
    - Test PDF generation failures
    - Test very long input text
    - _Requirements: 4.1, 4.2_


- [ ] 12. Checkpoint - Verify action plans and document generation
  - Run all tests for action plans and documents
  - Manually test document generation for all template types
  - Verify PDF and text format outputs
  - Verify action plan generation with various case types
  - Ask the user if questions arise

### Phase 6: Legal Aid and Multilingual Support

- [ ] 13. Implement legal aid search system
  - [ ] 13.1 Create legal aid provider database seeding
    - Compile list of legal aid providers across India
    - Create seed data with contact info, specializations, languages, locations
    - Implement database seeding script
    - _Requirements: 5.5_

  - [ ] 13.2 Implement legal aid search logic
    - Create search query builder with filters (location, case type, language, expertise)
    - Implement multi-criteria filtering
    - Add relevance scoring for search results
    - Implement fallback to national helplines when no local results
    - _Requirements: 5.1, 5.3, 5.6_

  - [ ] 13.3 Create legal aid endpoints
    - Create GET /api/legal-aid/search endpoint with query parameters
    - Create GET /api/legal-aid/{id} endpoint for detailed provider info
    - Return contact information, specializations, availability
    - Include multiple contact methods (phone, email, address, website)
    - _Requirements: 5.2, 5.4_

  - [ ]* 13.4 Write property tests for legal aid search
    - **Property 23: Location and case type filtering** - Verify results match both criteria
    - **Property 24: Provider information completeness** - Verify all required fields present
    - **Property 25: Multi-criteria filtering** - Verify all filters applied
    - **Property 26: Multiple contact methods** - Verify at least 2 contact methods
    - **Property 27: National fallback** - Verify fallback when no local results
    - **Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.6**


- [ ] 14. Implement multilingual support system
  - [ ] 14.1 Set up translation infrastructure
    - Install and configure spaCy for English
    - Install and configure IndicNLP for Hindi and regional languages
    - Create language detection service using langdetect
    - Set up translation service for UI elements
    - _Requirements: 6.1, 6.5_

  - [ ] 14.2 Create translation files for UI elements
    - Create English translation file with all UI strings
    - Create Hindi translation file
    - Create translation files for 5 major regional languages (Tamil, Telugu, Bengali, Marathi, Gujarati)
    - Ensure consistent legal term translations
    - _Requirements: 6.2, 6.6_

  - [ ] 14.3 Implement language switching functionality
    - Add language preference to user profile
    - Create language selection API endpoint
    - Implement real-time language switching in frontend
    - Preserve legal terminology accuracy across translations
    - _Requirements: 6.3, 6.4_

  - [ ]* 14.4 Write property tests for multilingual support
    - **Property 28: UI language consistency** - Verify all UI elements in selected language
    - **Property 29: Language switching** - Verify immediate update on language change
    - **Property 30: Translation consistency** - Verify identical translations for same terms
    - **Validates: Requirements 6.2, 6.4, 6.6**

  - [ ]* 14.5 Write unit tests for translation edge cases
    - Test unsupported language handling
    - Test missing translation keys
    - Test language detection accuracy
    - Test special character handling in translations
    - _Requirements: 6.1, 6.2_


### Phase 7: Evidence Guide and Emergency Features

- [ ] 15. Implement evidence documentation guide
  - [ ] 15.1 Create evidence guide content system
    - Create case-type specific evidence guide templates
    - Add digital evidence preservation instructions
    - Add legal admissibility requirements
    - Include evidence tampering warnings
    - Add digital communication procedures (screenshots, backups)
    - _Requirements: 7.1, 7.2, 7.3, 7.6, 7.7_

  - [ ] 15.2 Create evidence guide generator
    - Implement case type detection
    - Generate customized evidence guides based on case type
    - Add step-by-step instructions with numbering
    - Include visual aid references
    - Generate evidence type checklists
    - _Requirements: 7.4, 7.5_

  - [ ] 15.3 Create evidence guide endpoint
    - Create GET /api/evidence/guide endpoint with case type parameter
    - Return formatted evidence guide with all sections
    - Support multiple languages
    - _Requirements: 7.1_

  - [ ]* 15.4 Write property tests for evidence guides
    - **Property 31: Case-specific guidance** - Verify case-type specific content
    - **Property 32: Digital preservation instructions** - Verify at least 3 instructions
    - **Property 33: Admissibility requirements** - Verify admissibility section present
    - **Property 34: Step-by-step format with visuals** - Verify numbered steps and visual aids
    - **Property 35: Evidence type checklists** - Verify at least 5 items per checklist
    - **Property 36: Tampering warnings** - Verify warning present
    - **Property 37: Digital communication procedures** - Verify screenshot/backup procedures
    - **Validates: Requirements 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7**


- [ ] 16. Implement emergency SOS feature
  - [ ] 16.1 Create emergency contacts database
    - Compile emergency contacts by category (police, legal helplines, mental health, student services)
    - Add location-specific contacts for all Indian states
    - Add national emergency numbers as fallbacks
    - Create database seeding script
    - _Requirements: 8.3, 8.5, 8.6_

  - [ ] 16.2 Create emergency contacts endpoint
    - Create GET /api/emergency/contacts endpoint
    - Accept location parameter (state/city)
    - Return categorized emergency contacts
    - Include phone numbers with calling capability metadata
    - Optimize for <1 second response time
    - _Requirements: 8.2, 8.4_

  - [ ] 16.3 Add emergency mode quick access
    - Create emergency mode flag in user session
    - Provide quick access links to evidence documentation in emergency mode
    - _Requirements: 8.7_

  - [ ]* 16.4 Write property tests for emergency features
    - **Property 38: Emergency response time** - Verify <1 second response
    - **Property 39: Contact categorization** - Verify 4+ categories
    - **Property 40: Callable phone numbers** - Verify phone number field present
    - **Property 41: Location-specific contacts** - Verify location-specific contact present
    - **Property 42: National fallback contacts** - Verify at least 2 national numbers
    - **Property 43: Evidence access in emergency mode** - Verify quick access links
    - **Validates: Requirements 8.2, 8.3, 8.4, 8.5, 8.6, 8.7**

- [ ] 17. Checkpoint - Verify evidence guides and emergency features
  - Run all tests for evidence guides and emergency features
  - Manually test evidence guide generation for different case types
  - Verify emergency contacts load within 1 second
  - Test emergency mode functionality
  - Ask the user if questions arise


### Phase 8: OCR and Document Upload

- [ ] 18. Implement OCR functionality
  - [ ] 18.1 Set up Tesseract.js OCR service
    - Install and configure Tesseract.js
    - Download language models for English, Hindi, and regional languages
    - Create OCR processing service
    - _Requirements: 11.7_

  - [ ] 18.2 Create document upload and OCR endpoint
    - Create POST /api/ocr/upload endpoint
    - Accept image uploads (JPEG, PNG, PDF, HEIC)
    - Validate file format and size
    - Enforce 10-page limit for multi-page documents
    - Process OCR within 10 seconds
    - Return extracted text with confidence scores
    - _Requirements: 11.1, 11.2, 11.6_

  - [ ] 18.3 Implement OCR verification and editing
    - Create POST /api/ocr/verify endpoint for corrected text
    - Display extracted text for user verification
    - Allow text editing before analysis
    - Highlight low-confidence text segments (<80%)
    - _Requirements: 11.3, 11.4, 11.5_

  - [ ]* 18.4 Write property tests for OCR
    - **Property 55: OCR processing time** - Verify <10 second processing
    - **Property 56: Extracted text display** - Verify text returned for verification
    - **Property 57: Text editability** - Verify editing capability
    - **Property 58: Low confidence highlighting** - Verify highlighting for confidence <80%
    - **Property 59: Page limit enforcement** - Verify 10-page limit
    - **Property 60: Language-specific OCR models** - Verify correct model selection
    - **Validates: Requirements 11.1, 11.3, 11.4, 11.5, 11.6, 11.7**

  - [ ]* 18.5 Write unit tests for OCR edge cases
    - Test unsupported file formats
    - Test oversized files
    - Test corrupted images
    - Test very low quality images
    - Test multi-page documents
    - _Requirements: 11.1, 11.2, 11.6_


### Phase 9: Frontend Development - Web Application

- [ ] 19. Set up React frontend infrastructure
  - [ ] 19.1 Initialize React project with TypeScript
    - Create React app with Vite and TypeScript
    - Install Chakra UI and Tailwind CSS
    - Set up React Router for navigation
    - Configure environment variables for API endpoints
    - Set up Axios for API calls
    - _Requirements: All frontend requirements_

  - [ ] 19.2 Implement authentication UI components
    - Create Login component with form validation
    - Create Registration component with email validation
    - Create password reset flow
    - Implement JWT token storage in localStorage
    - Add authentication context provider
    - Add protected route wrapper
    - _Requirements: 9.1, 9.2_

  - [ ] 19.3 Implement language selector component
    - Create language dropdown with all supported languages
    - Persist language preference to user profile
    - Update all UI elements on language change
    - _Requirements: 6.2, 6.4_

- [ ] 20. Implement chat interface
  - [ ] 20.1 Create chat UI components
    - Create ChatInterface component with message list
    - Create message input with send button
    - Add typing indicators
    - Add message timestamps
    - Style messages differently for user vs assistant
    - _Requirements: 1.1, 1.6_

  - [ ] 20.2 Integrate chat with backend API
    - Connect to POST /api/chat/query endpoint
    - Display AI responses with citations
    - Show confidence scores
    - Handle loading states
    - Handle error states
    - _Requirements: 1.1, 1.4_

  - [ ] 20.3 Implement WebSocket streaming
    - Connect to WebSocket endpoint for real-time responses
    - Stream response tokens as they arrive
    - Handle connection errors and reconnection
    - _Requirements: 1.1_

  - [ ] 20.4 Add conversation history
    - Fetch and display conversation history
    - Implement pagination for long conversations
    - Allow users to start new conversations
    - _Requirements: 1.6_


- [ ] 21. Implement case analyzer UI
  - [ ] 21.1 Create case analysis form
    - Create form for complaint details (evidence, allegations, procedures, timeline)
    - Add form validation
    - Add multi-step form for better UX
    - _Requirements: 2.1_

  - [ ] 21.2 Create validity score display
    - Create component to display validity score (0-100)
    - Add visual indicator (color-coded gauge)
    - Display score breakdown with charts
    - Show weaknesses and recommendations
    - Highlight legal consultation recommendation for high scores
    - _Requirements: 2.1, 2.3, 2.4, 2.5_

  - [ ] 21.3 Add case analysis history
    - Fetch and display past analyses
    - Allow filtering by score range
    - Show analysis details on click
    - _Requirements: 2.1_

- [ ] 22. Implement document generator UI
  - [ ] 22.1 Create document template selector
    - Display available document templates
    - Show template descriptions
    - Allow template selection
    - _Requirements: 4.1_

  - [ ] 22.2 Create document generation form
    - Generate dynamic form based on template requirements
    - Add form validation for required fields
    - Show attachment checklist
    - _Requirements: 4.1, 4.7_

  - [ ] 22.3 Create document preview and download
    - Display generated document preview
    - Add download buttons for PDF and text formats
    - Show placeholders for manual completion
    - _Requirements: 4.5, 4.6_

