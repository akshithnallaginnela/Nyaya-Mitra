# Design Document: Nyaya Mitra

## Overview

Nyaya Mitra is an AI-powered legal assistance platform built on a RAG (Retrieval-Augmented Generation) architecture. The system combines a React.js frontend with a Python FastAPI backend, leveraging Mistral 7B LLM through Ollama for natural language understanding and generation. The platform uses Chroma vector database for semantic search over legal knowledge, PostgreSQL for structured data storage, and implements comprehensive security measures to protect sensitive user information.

The architecture is designed for zero-cost operation using free-tier hosting (Vercel for frontend, Render for backend) while maintaining high performance and scalability to serve 10M+ Indian college students.

## Architecture+

### High-Level Architecture

The Nyaya Mitra platform follows a layered architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER INTERFACE LAYER                          │
│  ┌──────────────────────┐      ┌──────────────────────┐        │
│  │   React Web App      │      │  React Native App    │        │
│  │  (Chakra UI +        │      │  (Android + iOS)     │        │
│  │   Tailwind CSS)      │      │                      │        │
│  └──────────────────────┘      └──────────────────────┘        │
└─────────────────────────────────────────────────────────────────┘
                              │
                    HTTPS/REST API (JWT Auth)
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    API GATEWAY LAYER                             │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │         FastAPI Backend (Python)                          │  │
│  │  - JWT Authentication Middleware                          │  │
│  │  - Rate Limiting (100 req/hour)                          │  │
│  │  - Request Validation & Sanitization                     │  │
│  │  - CORS Configuration                                    │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                  AI/ML PROCESSING LAYER                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  LangChain Orchestrator                                   │  │
│  │    ├─> Ollama + Mistral 7B (Text Generation)            │  │
│  │    ├─> Sentence-Transformers (Embeddings)               │  │
│  │    ├─> spaCy (NLP & Entity Extraction)                  │  │
│  │    └─> IndicNLP (Indian Language Processing)            │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     DATABASE LAYER                               │
│  ┌─────────────────────┐      ┌─────────────────────┐          │
│  │    PostgreSQL       │      │   Chroma Vector DB  │          │
│  │  (User Data, Cases, │      │  (Legal Knowledge   │          │
│  │   Documents)        │      │   Embeddings)       │          │
│  └─────────────────────┘      └─────────────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   EXTERNAL SERVICES                              │
│  - Tesseract.js OCR (Document Text Extraction)                  │
│  - Legal Aid Directory API                                       │
│  - Emergency Contact Services                                    │
└─────────────────────────────────────────────────────────────────┘
```

### Architecture Flow

**User Request Flow:**
1. User interacts with React Web App or React Native Mobile App
2. Request sent to FastAPI backend with JWT token
3. API Gateway validates token, checks rate limits, sanitizes input
4. Request routed to appropriate service (Auth, Query Engine, Document Generator, etc.)
5. Service processes request, potentially calling AI/ML layer
6. AI/ML layer uses LangChain to orchestrate RAG pipeline:
   - Generate embeddings for query
   - Retrieve relevant documents from Chroma
   - Construct prompt with context
   - Generate response using Mistral 7B via Ollama
7. Response formatted and returned to user
8. User sees result in their preferred language

**RAG Pipeline Flow (Legal Query Processing):**
1. User submits legal query in any supported language
2. Translation Service translates to English if needed
3. Sentence-Transformers generates query embedding (768-dim vector)
4. Chroma performs semantic search, returns top-5 relevant legal documents
5. LangChain constructs prompt with retrieved context + user query
6. Ollama/Mistral 7B generates response with legal citations
7. Response translated back to user's language
8. Citations extracted and formatted
9. Query and response stored in PostgreSQL for history

### Architecture Layers

**User Interface Layer:**
- React.js web application with Chakra UI and Tailwind CSS for responsive design
- React Native mobile application for Android and iOS
- Client-side OCR using Tesseract.js for document scanning
- Offline support for mobile app with local storage

**API Gateway Layer:**
- FastAPI backend with async request handling
- JWT-based authentication middleware
- Rate limiting (100 requests/hour per user)
- Request validation and sanitization
- CORS configuration for web and mobile clients

**AI/ML Processing Layer:**
- LangChain for orchestrating RAG pipeline
- Ollama serving Mistral 7B model for text generation
- Sentence-Transformers for generating embeddings
- spaCy for NLP tasks (entity extraction, text processing)
- IndicNLP for Indian language processing
- LlamaIndex for advanced retrieval strategies

**Database Layer:**
- PostgreSQL for structured data (users, cases, documents, sessions)
- Chroma vector database for legal knowledge embeddings
- Redis cache for session management and frequently accessed data

**External Services:**
- Legal Aid Directory API
- Emergency contact services
- Document storage (local filesystem for free tier)

## Components and Interfaces

### 1. Authentication Service

**Responsibilities:**
- User registration and login
- JWT token generation and validation
- Password hashing and verification
- Session management

**Key Interfaces:**

```python
class AuthenticationService:
    def register_user(email: str, password: str, name: str, college: str) -> User:
        """
        Register a new user with encrypted password.
        Returns User object with generated ID.
        Raises ValueError if email already exists.
        """
        
    def login_user(email: str, password: str) -> TokenPair:
        """
        Authenticate user and generate JWT tokens.
        Returns access token (24h validity) and refresh token.
        Raises AuthenticationError if credentials invalid.
        """
        
    def verify_token(token: str) -> User:
        """
        Verify JWT token and return associated user.
        Raises TokenExpiredError or InvalidTokenError.
        """
        
    def hash_password(password: str) -> str:
        """
        Hash password using bcrypt with 12 rounds.
        """
```

### 2. Legal Query Engine

**Responsibilities:**
- Process natural language legal queries
- Retrieve relevant legal provisions using RAG
- Generate contextual responses with citations
- Maintain conversation context

**Key Interfaces:**

```python
class LegalQueryEngine:
    def process_query(query: str, user_id: str, language: str, 
                     conversation_history: List[Message]) -> QueryResponse:
        """
        Process legal query using RAG architecture.
        Steps:
        1. Translate query to English if needed
        2. Generate query embedding
        3. Retrieve top-k relevant documents from Chroma
        4. Construct prompt with retrieved context
        5. Generate response using Mistral 7B
        6. Translate response back to user's language
        7. Extract and format citations
        
        Returns QueryResponse with answer, citations, and confidence score.
        """
        
    def retrieve_relevant_docs(query_embedding: np.ndarray, 
                              top_k: int = 5) -> List[LegalDocument]:
        """
        Retrieve most relevant legal documents from vector DB.
        Uses cosine similarity for ranking.
        """
        
    def generate_response(prompt: str, context: List[str]) -> str:
        """
        Generate response using Mistral 7B through Ollama.
        Includes system prompt for legal accuracy and citation requirements.
        """
        
    def extract_citations(response: str, context_docs: List[LegalDocument]) -> List[Citation]:
        """
        Extract and validate legal citations from generated response.
        """
```

### 3. Case Validator

**Responsibilities:**
- Analyze complaint validity
- Assess case strength
- Identify missing legal elements
- Provide validity scoring

**Key Interfaces:**

```python
class CaseValidator:
    def analyze_case(case_details: CaseDetails) -> ValidationReport:
        """
        Analyze case validity against legal requirements.
        Steps:
        1. Extract key elements (charges, evidence, parties)
        2. Retrieve relevant legal provisions
        3. Check completeness of complaint elements
        4. Assess evidence strength
        5. Generate validity score (0-100)
        6. Identify missing elements
        
        Returns ValidationReport with score, assessment, and recommendations.
        """
        
    def assess_validity(charges: List[str], evidence: List[Evidence], 
                       circumstances: str) -> ValidityScore:
        """
        Calculate validity score based on legal requirements.
        Categories: Strong (75-100), Moderate (50-74), Weak (25-49), Invalid (0-24)
        """
        
    def identify_missing_elements(case_details: CaseDetails, 
                                  legal_requirements: List[Requirement]) -> List[str]:
        """
        Identify missing elements required for legal validity.
        """
```

### 4. Document Generator

**Responsibilities:**
- Generate legal documents from templates
- Fill templates with user-provided data
- Format documents according to legal standards
- Support multiple document types and languages

**Key Interfaces:**

```python
class DocumentGenerator:
    def generate_document(doc_type: DocumentType, data: Dict[str, Any], 
                         language: str) -> GeneratedDocument:
        """
        Generate legal document from template.
        Supported types: reply_notice, complaint_letter, rti_application,
                        affidavit, police_complaint, counter_petition
        
        Steps:
        1. Load template for document type and language
        2. Validate required fields are present
        3. Fill template with provided data
        4. Add legal citations if applicable
        5. Format according to legal standards
        6. Generate PDF and DOCX versions
        
        Returns GeneratedDocument with content and download links.
        """
        
    def validate_fields(doc_type: DocumentType, data: Dict[str, Any]) -> ValidationResult:
        """
        Validate that all required fields are present and valid.
        """
        
    def extract_from_notice(notice_text: str) -> Dict[str, Any]:
        """
        Extract relevant information from received notice using NLP.
        Pre-fills fields for response document.
        """
```

### 5. Knowledge Base Manager

**Responsibilities:**
- Store and index legal knowledge
- Generate embeddings for legal documents
- Support semantic search
- Maintain version history

**Key Interfaces:**

```python
class KnowledgeBaseManager:
    def add_legal_document(doc: LegalDocument) -> str:
        """
        Add legal document to knowledge base.
        Steps:
        1. Extract text from document
        2. Chunk text into semantic segments
        3. Generate embeddings using Sentence-Transformers
        4. Store in Chroma with metadata
        5. Index in PostgreSQL for structured queries
        
        Returns document ID.
        """
        
    def search_semantic(query: str, filters: Dict[str, Any], 
                       top_k: int = 10) -> List[SearchResult]:
        """
        Perform semantic search over knowledge base.
        Filters can include: document_type, jurisdiction, date_range, section_number
        """
        
    def update_document(doc_id: str, updated_content: str) -> None:
        """
        Update existing document and regenerate embeddings.
        Maintains version history.
        """
        
    def bulk_import(pdf_files: List[Path]) -> ImportReport:
        """
        Bulk import legal documents from PDF files.
        Extracts text, generates embeddings, stores in vector DB.
        """
```

### 6. OCR Service

**Responsibilities:**
- Extract text from document images
- Identify key information (dates, case numbers, parties)
- Handle multiple image formats
- Provide confidence scores

**Key Interfaces:**

```python
class OCRService:
    def extract_text(image: bytes, file_format: str) -> OCRResult:
        """
        Extract text from document image using Tesseract.
        Supports JPEG, PNG, PDF formats up to 10MB.
        
        Returns OCRResult with extracted text and confidence score.
        Raises OCRError if extraction fails or confidence < 70%.
        """
        
    def extract_key_info(text: str, doc_type: DocumentType) -> Dict[str, Any]:
        """
        Extract structured information from OCR text.
        Uses spaCy NER and regex patterns to identify:
        - Case numbers
        - Dates
        - Party names
        - Charges/sections
        - Court names
        """
        
    def preprocess_image(image: bytes) -> bytes:
        """
        Preprocess image for better OCR accuracy.
        - Deskew
        - Denoise
        - Enhance contrast
        """
```

### 7. Translation Service

**Responsibilities:**
- Translate UI elements and content
- Maintain legal terminology accuracy
- Support 10 Indian languages
- Handle bidirectional translation

**Key Interfaces:**

```python
class TranslationService:
    def translate_text(text: str, source_lang: str, target_lang: str) -> str:
        """
        Translate text between supported languages.
        Uses IndicNLP for Indian languages.
        Preserves legal terminology using custom dictionary.
        """
        
    def translate_ui(language_code: str) -> Dict[str, str]:
        """
        Load UI translations for specified language.
        Returns dictionary of UI element keys to translated strings.
        """
        
    def validate_legal_terms(translated_text: str, original_text: str) -> bool:
        """
        Validate that legal terms are correctly preserved in translation.
        """
```

### 8. Legal Aid Connector

**Responsibilities:**
- Search legal aid directory
- Filter by location and case type
- Provide contact information
- Track availability

**Key Interfaces:**

```python
class LegalAidConnector:
    def search_providers(location: Location, case_type: str, 
                        language: str, radius_km: int = 50) -> List[Provider]:
        """
        Search for legal aid providers.
        Prioritizes providers within specified radius.
        Filters by case type specialization and language support.
        """
        
    def get_provider_details(provider_id: str) -> ProviderDetails:
        """
        Get detailed information about legal aid provider.
        Includes: contact info, address, specializations, operating hours,
                 required documents, eligibility criteria.
        """
        
    def check_eligibility(user_profile: UserProfile, 
                         provider: Provider) -> EligibilityResult:
        """
        Check if user is eligible for free legal aid from provider.
        Based on income, case type, and provider criteria.
        """
```

### 9. Emergency Handler

**Responsibilities:**
- Provide emergency resources
- Display crisis contacts
- Generate emergency documents
- Prioritize urgent information

**Key Interfaces:**

```python
class EmergencyHandler:
    def get_emergency_contacts(location: Location) -> EmergencyContacts:
        """
        Get location-specific emergency contacts.
        Includes: police, legal aid helplines, student support, crisis counseling.
        """
        
    def generate_emergency_complaint(incident_details: str) -> Document:
        """
        Generate emergency complaint/FIR template.
        Pre-filled with incident details for quick filing.
        """
        
    def get_immediate_actions(situation_type: str) -> List[Action]:
        """
        Get prioritized list of immediate actions for emergency situation.
        Situation types: threat, extortion, false_accusation, harassment
        """
```

## Data Models

### User Model

```python
class User:
    id: UUID
    email: str  # unique, indexed
    password_hash: str  # bcrypt hashed
    name: str
    college: str
    phone: Optional[str]
    state: str
    preferred_language: str  # default: 'en'
    created_at: datetime
    last_login: datetime
    is_active: bool
    
    # Relationships
    queries: List[Query]
    cases: List[Case]
    documents: List[Document]
```

### Query Model

```python
class Query:
    id: UUID
    user_id: UUID  # foreign key to User
    query_text: str
    language: str
    response_text: str
    citations: List[Citation]
    confidence_score: float  # 0.0 to 1.0
    created_at: datetime
    conversation_id: UUID  # groups related queries
    
    # Metadata
    processing_time_ms: int
    tokens_used: int
```

### Case Model

```python
class Case:
    id: UUID
    user_id: UUID  # foreign key to User
    title: str
    description: str
    case_type: str  # criminal, civil, consumer, etc.
    status: str  # active, resolved, closed
    validity_score: int  # 0-100
    validity_category: str  # Strong, Moderate, Weak, Invalid
    
    # Case details
    charges: List[str]
    evidence: List[Evidence]
    parties_involved: List[str]
    important_dates: Dict[str, datetime]
    
    # Analysis
    missing_elements: List[str]
    recommendations: List[str]
    action_plan: List[Action]
    
    created_at: datetime
    updated_at: datetime
```

### LegalDocument Model

```python
class LegalDocument:
    id: UUID
    document_type: str  # IPC_section, CrPC_section, case_law, etc.
    title: str
    content: str
    section_number: Optional[str]
    jurisdiction: str  # India, state-specific
    effective_date: datetime
    
    # Vector search
    embedding: np.ndarray  # stored in Chroma
    
    # Metadata
    related_sections: List[str]
    keywords: List[str]
    category: str
    version: int
    
    created_at: datetime
    updated_at: datetime
```

### GeneratedDocument Model

```python
class GeneratedDocument:
    id: UUID
    user_id: UUID
    case_id: Optional[UUID]
    document_type: str  # reply_notice, rti_application, etc.
    language: str
    
    # Content
    content_text: str
    content_pdf: bytes
    content_docx: bytes
    
    # Template data
    template_id: str
    filled_fields: Dict[str, Any]
    
    created_at: datetime
```

### Evidence Model

```python
class Evidence:
    id: UUID
    case_id: UUID
    evidence_type: str  # document, photo, video, witness, digital
    description: str
    file_path: Optional[str]
    ocr_text: Optional[str]
    
    # Metadata
    date_collected: datetime
    admissibility_notes: str
    is_verified: bool
    
    created_at: datetime
```

### Provider Model (Legal Aid)

```python
class Provider:
    id: UUID
    name: str
    organization_type: str  # government, ngo, law_school, pro_bono
    
    # Contact
    phone: str
    email: str
    address: str
    city: str
    state: str
    pincode: str
    location: Point  # PostGIS geography type
    
    # Services
    specializations: List[str]
    languages_supported: List[str]
    operating_hours: Dict[str, str]
    
    # Eligibility
    eligibility_criteria: str
    required_documents: List[str]
    
    # Status
    is_active: bool
    last_verified: datetime
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

Before defining the correctness properties, let me analyze each acceptance criterion for testability:


### Property Reflection

After analyzing all acceptance criteria, I've identified several areas where properties can be consolidated:

**Authentication & Security:**
- Properties 1.1, 1.2, 1.3 can be combined into a comprehensive authentication property
- Property 1.4 (password hashing) is an invariant that should always hold
- Property 1.5 (token expiry) and 1.6 (profile updates) are distinct and should remain separate

**Query Processing:**
- Properties 2.1, 2.2, 2.3 describe the RAG pipeline and can be combined into one comprehensive property
- Property 2.6 (conversation context) and 2.7 (query storage) are distinct behaviors

**Case Validation:**
- Properties 3.1, 3.2, 3.3, 3.4, 3.6 all relate to case analysis output and can be combined
- Property 3.5 (multiple charges) is a specific case that should be tested separately

**Document Generation:**
- Properties 5.1, 5.3, 5.4 relate to document generation output and can be combined
- Property 5.5 (validation) and 5.6 (OCR pre-fill) are distinct behaviors

**Knowledge Base:**
- Properties 10.1, 10.2 relate to embedding generation and can be combined
- Properties 10.4, 10.5 relate to document metadata and can be combined

**OCR Processing:**
- Properties 11.1, 11.2, 11.3 relate to OCR extraction and can be combined
- Property 11.5 (error handling) is distinct

**Monitoring:**
- Properties 15.1, 15.2, 15.3, 15.6 all relate to metrics tracking and can be combined

### Correctness Properties

**Property 1: Authentication Round-Trip**
*For any* valid user registration data (email, password, name, college), registering a user then logging in with those credentials should succeed and return a valid JWT token with 24-hour expiry.
**Validates: Requirements 1.1, 1.2**

**Property 2: Password Security Invariant**
*For any* stored user password, the password hash should use bcrypt with at least 10 salt rounds, and the original password should never be stored in plaintext.
**Validates: Requirements 1.4**

**Property 3: Invalid Credentials Rejection**
*For any* invalid login credentials (wrong password, non-existent email, malformed input), the authentication service should reject the attempt and return an appropriate error without revealing whether the email exists.
**Validates: Requirements 1.3**

**Property 4: Token Expiry Enforcement**
*For any* expired JWT token, attempting to access protected resources should fail with an authentication error requiring re-login.
**Validates: Requirements 1.5**

**Property 5: Profile Update Persistence**
*For any* valid profile update (name, college, contact details), the changes should be persisted to the database and reflected in subsequent profile retrievals.
**Validates: Requirements 1.6**

**Property 6: RAG Query Processing Pipeline**
*For any* legal query in a supported language, the system should: (1) retrieve relevant documents from the knowledge base using semantic search, (2) generate a response using the LLM with retrieved context, (3) include specific IPC/CrPC citations in the response, and (4) return results in the user's selected language.
**Validates: Requirements 2.1, 2.2, 2.3**

**Property 7: Low Confidence Uncertainty Indication**
*For any* query where the knowledge base lacks sufficient information (relevance score below threshold), the response should explicitly indicate uncertainty and recommend consulting a legal professional.
**Validates: Requirements 2.5**

**Property 8: Conversation Context Preservation**
*For any* sequence of queries within the same session, follow-up questions should have access to previous queries and responses in the conversation history.
**Validates: Requirements 2.6**

**Property 9: Query History Persistence**
*For any* submitted query, the query text, response, citations, and metadata should be stored in the user's history and retrievable in subsequent sessions.
**Validates: Requirements 2.7**

**Property 10: Case Validity Analysis Completeness**
*For any* case details provided (accusation type, evidence, circumstances), the case validator should return: (1) a validity category (Strong/Moderate/Weak/Invalid), (2) a numerical score (0-100), (3) identified missing elements, (4) legal citations supporting the assessment, and (5) recommended actions.
**Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.6**

**Property 11: Multiple Charges Independent Analysis**
*For any* case involving multiple charges, each charge should be analyzed separately with its own validity assessment and legal citations.
**Validates: Requirements 3.5**

**Property 12: Action Plan Structure**
*For any* legal situation requiring response guidance, the generated action plan should: (1) contain numbered sequential steps, (2) prioritize time-sensitive actions first, (3) include specific deadlines for each action, (4) provide document templates for documentation steps, and (5) indicate which steps require professional legal assistance.
**Validates: Requirements 4.1, 4.2, 4.3, 4.4, 4.5**

**Property 13: Action Plan Progress Tracking**
*For any* action plan step marked as completed, the system should update the progress state and highlight the next incomplete step.
**Validates: Requirements 4.6**

**Property 14: Document Generation Completeness**
*For any* document type and valid input data, the generated document should: (1) be legally formatted, (2) include appropriate legal citations, (3) be available in both PDF and DOCX formats, and (4) be downloadable by the user.
**Validates: Requirements 5.1, 5.3, 5.4**

**Property 15: Document Field Validation**
*For any* document generation request with incomplete required fields, the system should reject the request with specific validation errors indicating which fields are missing.
**Validates: Requirements 5.5**

**Property 16: OCR Pre-fill Round-Trip**
*For any* uploaded legal notice, the OCR service should extract text, identify relevant fields (parties, dates, case numbers), and pre-fill the corresponding response document fields with extracted values.
**Validates: Requirements 5.6**

**Property 17: Legal Aid Search Filtering**
*For any* legal aid search with location, case type, and language filters, the results should: (1) only include providers matching the filters, (2) prioritize providers within 50km by distance, (3) include all required information (contact, address, specialization, availability), and (4) support further filtering by case type.
**Validates: Requirements 6.1, 6.2, 6.3, 6.5**

**Property 18: Provider Detail Completeness**
*For any* selected legal aid provider, the detailed view should include operating hours, required documents, eligibility criteria, and contact information.
**Validates: Requirements 6.6**

**Property 19: UI Translation Completeness**
*For any* supported language selection, all UI elements and system messages should be translated to that language, and users should be able to switch languages at any time during a session.
**Validates: Requirements 7.2, 7.4**

**Property 20: Multilingual Document Generation**
*For any* document generation request, the document should be generated in the user's currently selected language while preserving legal terminology accuracy.
**Validates: Requirements 7.5**

**Property 21: Evidence Checklist Provision**
*For any* case type, the evidence guide should provide: (1) a checklist of required evidence, (2) admissibility requirements for each evidence type, (3) step-by-step documentation instructions for digital evidence, and (4) warnings about inadmissible evidence types.
**Validates: Requirements 8.1, 8.2, 8.3, 8.6**

**Property 22: Evidence OCR Indexing**
*For any* uploaded evidence document, the OCR service should extract text content and index it for case analysis and search.
**Validates: Requirements 8.5**

**Property 23: Emergency Contact Location Specificity**
*For any* user location (state/city), the emergency handler should display location-specific emergency contacts including police, legal aid helplines, and student support services.
**Validates: Requirements 9.4**

**Property 24: SOS Mode Action Prioritization**
*For any* SOS mode activation, the system should prioritize displaying immediate action steps over detailed legal analysis in the UI.
**Validates: Requirements 9.3**

**Property 25: Knowledge Base Embedding Generation**
*For any* new legal document added to the knowledge base, the system should: (1) generate vector embeddings using Sentence-Transformers, (2) store embeddings in Chroma vector database, (3) support semantic search with relevance scoring, and (4) include metadata (effective date, jurisdiction, related sections).
**Validates: Requirements 10.1, 10.2, 10.3, 10.5**

**Property 26: Legal Provision Versioning**
*For any* update to an existing legal provision, the system should create a new version, maintain historical records, and update embeddings while preserving the previous version.
**Validates: Requirements 10.4**

**Property 27: Bulk Import Processing**
*For any* batch of PDF legal documents, the bulk import should extract text from all documents, generate embeddings, and store them in the vector database with appropriate metadata.
**Validates: Requirements 10.6**

**Property 28: OCR Extraction Quality**
*For any* clear image (JPEG, PNG, or PDF up to 10MB), the OCR service should: (1) extract text with minimum 90% accuracy, (2) identify key information (case numbers, dates, parties, charges), and (3) complete processing within 15 seconds for single-page documents.
**Validates: Requirements 11.1, 11.2, 11.3**

**Property 29: OCR Low Confidence Handling**
*For any* OCR extraction with confidence below threshold or extraction failure, the system should notify the user and request manual input.
**Validates: Requirements 11.5**

**Property 30: Data Encryption at Rest**
*For any* sensitive user data stored in PostgreSQL (passwords, personal information, queries), the data should be encrypted at rest using appropriate encryption algorithms.
**Validates: Requirements 12.2**

**Property 31: Account Deletion Data Removal**
*For any* user account deletion request, all personal data should be marked for permanent removal and deleted within 30 days.
**Validates: Requirements 12.4**

**Property 32: Rate Limiting Enforcement**
*For any* user making requests, the system should enforce a rate limit of 100 requests per hour, rejecting requests that exceed this limit with appropriate error messages.
**Validates: Requirements 12.5**

**Property 33: Security Event Logging**
*For any* security event (failed login attempt, suspicious activity, rate limit violation), the system should log the event with timestamp, user identifier, and event details for audit purposes.
**Validates: Requirements 12.6**

**Property 34: Request Queuing Under Load**
*For any* high load scenario exceeding system capacity, the system should queue incoming requests and notify users of expected wait times rather than rejecting requests.
**Validates: Requirements 13.5**

**Property 35: Legal Provision Caching**
*For any* frequently accessed legal provision, the system should cache the content to reduce database load, with cache invalidation when provisions are updated.
**Validates: Requirements 13.6**

**Property 36: Mobile Offline Access**
*For any* previously accessed information or saved document in the mobile app, the content should be available offline, and sync with the backend when connectivity is restored.
**Validates: Requirements 14.3, 14.4**

**Property 37: Mobile Push Notifications**
*For any* important update or reminder (action plan deadline, case update, system notification), the mobile app should send a push notification to the user.
**Validates: Requirements 14.5**

**Property 38: Comprehensive Metrics Tracking**
*For any* system operation (query, document generation, authentication), the system should track relevant metrics including: query volume, response times, error rates, LLM inference time, token usage, failed queries, low-confidence responses, and user engagement metrics.
**Validates: Requirements 15.1, 15.2, 15.3, 15.6**

**Property 39: Error Rate Alerting**
*For any* time period where error rates exceed 5%, the system should send alerts to administrators with error details and affected components.
**Validates: Requirements 15.5**

## Error Handling

### Error Categories

**1. Authentication Errors**
- Invalid credentials: Return 401 with generic error message (don't reveal if email exists)
- Expired token: Return 401 with token_expired error code
- Missing token: Return 401 with missing_token error code
- Invalid token format: Return 401 with invalid_token error code

**2. Validation Errors**
- Missing required fields: Return 400 with list of missing fields
- Invalid field format: Return 400 with field-specific error messages
- File size exceeded: Return 413 with maximum size information
- Unsupported file format: Return 415 with list of supported formats

**3. AI/ML Processing Errors**
- LLM timeout: Return 504 with retry suggestion
- Low confidence response: Return 200 with uncertainty flag and disclaimer
- Knowledge base unavailable: Return 503 with retry-after header
- Embedding generation failure: Return 500 with error details

**4. Database Errors**
- Connection failure: Return 503 with retry-after header
- Query timeout: Return 504 with simplified query suggestion
- Duplicate entry: Return 409 with conflict details
- Record not found: Return 404 with resource identifier

**5. OCR Processing Errors**
- Low confidence extraction: Return 200 with low_confidence flag and extracted text for review
- Unsupported image format: Return 415 with supported formats
- Image too large: Return 413 with maximum size
- OCR service unavailable: Return 503 with retry-after header

**6. Rate Limiting Errors**
- Rate limit exceeded: Return 429 with retry-after header and current limit information
- Quota exceeded: Return 429 with quota reset time

### Error Response Format

All errors follow a consistent JSON format:

```json
{
  "error": {
    "code": "error_code",
    "message": "Human-readable error message",
    "details": {
      "field": "specific_field",
      "reason": "detailed_reason"
    },
    "timestamp": "2024-01-15T10:30:00Z",
    "request_id": "uuid"
  }
}
```

### Error Recovery Strategies

**Automatic Retry:**
- Network timeouts: Retry up to 3 times with exponential backoff
- Database connection failures: Retry with connection pool
- LLM timeouts: Retry once, then return cached response if available

**Graceful Degradation:**
- If Chroma unavailable: Fall back to PostgreSQL full-text search
- If LLM unavailable: Return cached responses for common queries
- If OCR fails: Allow manual text input
- If translation service fails: Fall back to English

**User Notification:**
- All errors include user-friendly messages in the user's selected language
- Critical errors trigger admin alerts
- Transient errors suggest retry actions
- Permanent errors suggest alternative approaches

## Testing Strategy

### Dual Testing Approach

The Nyaya Mitra platform requires both unit testing and property-based testing for comprehensive coverage:

**Unit Tests** focus on:
- Specific examples demonstrating correct behavior
- Edge cases (empty inputs, boundary values, special characters)
- Error conditions and exception handling
- Integration points between components
- Mock external dependencies (Ollama, Chroma, PostgreSQL)

**Property-Based Tests** focus on:
- Universal properties that hold for all inputs
- Comprehensive input coverage through randomization
- Invariants that must always hold
- Round-trip properties (encode/decode, store/retrieve)
- Metamorphic properties (relationships between operations)

### Property-Based Testing Configuration

**Framework:** Use `hypothesis` for Python backend testing

**Configuration:**
- Minimum 100 iterations per property test (due to randomization)
- Each property test must reference its design document property
- Tag format: `# Feature: nyaya-mitra, Property {number}: {property_text}`

**Example Property Test Structure:**

```python
from hypothesis import given, strategies as st
import pytest

@given(
    email=st.emails(),
    password=st.text(min_size=8, max_size=128),
    name=st.text(min_size=1, max_size=100),
    college=st.text(min_size=1, max_size=200)
)
@pytest.mark.property_test
def test_authentication_round_trip(email, password, name, college):
    """
    Feature: nyaya-mitra, Property 1: Authentication Round-Trip
    For any valid user registration data, registering then logging in
    should succeed and return a valid JWT token.
    """
    # Register user
    user = auth_service.register_user(email, password, name, college)
    assert user.id is not None
    assert user.email == email
    
    # Login with same credentials
    token_pair = auth_service.login_user(email, password)
    assert token_pair.access_token is not None
    assert token_pair.expires_in == 24 * 3600  # 24 hours
    
    # Verify token
    verified_user = auth_service.verify_token(token_pair.access_token)
    assert verified_user.id == user.id
```

### Test Coverage Requirements

**Backend (Python FastAPI):**
- Unit test coverage: Minimum 80%
- Property test coverage: All 39 correctness properties
- Integration tests: All API endpoints
- Security tests: Authentication, authorization, input validation

**Frontend (React.js):**
- Component tests: All UI components
- Integration tests: User flows (registration, query submission, document generation)
- Accessibility tests: WCAG 2.1 AA compliance
- Responsive design tests: Mobile, tablet, desktop viewports

**Mobile (React Native):**
- Component tests: All mobile-specific components
- Offline functionality tests: Data persistence and sync
- Platform-specific tests: Android and iOS differences

### Testing Tools

**Backend:**
- pytest: Test framework
- hypothesis: Property-based testing
- pytest-asyncio: Async test support
- pytest-cov: Coverage reporting
- faker: Test data generation
- responses: HTTP mocking

**Frontend:**
- Jest: Test framework
- React Testing Library: Component testing
- Cypress: End-to-end testing
- axe-core: Accessibility testing

**Mobile:**
- Jest: Test framework
- React Native Testing Library: Component testing
- Detox: End-to-end testing

### Continuous Integration

**GitHub Actions Workflow:**
1. Run linters (pylint, eslint, prettier)
2. Run unit tests with coverage reporting
3. Run property-based tests (100 iterations minimum)
4. Run integration tests
5. Run security scans (bandit, npm audit)
6. Build Docker images
7. Deploy to staging environment
8. Run smoke tests on staging

**Quality Gates:**
- All tests must pass
- Code coverage must be ≥80%
- No critical security vulnerabilities
- No linting errors
- Build must succeed

## Deployment Architecture

### Zero-Cost Hosting Strategy

**Frontend (Vercel Free Tier):**
- React.js web app deployed to Vercel
- Automatic HTTPS with Let's Encrypt
- Global CDN for fast loading
- Automatic deployments from GitHub main branch
- Environment variables for API endpoints

**Backend (Render Free Tier):**
- FastAPI backend deployed to Render
- Automatic HTTPS
- Auto-sleep after 15 minutes of inactivity (cold start ~30 seconds)
- PostgreSQL database (free tier: 1GB storage)
- Environment variables for secrets

**Vector Database (Chroma):**
- Self-hosted on Render alongside FastAPI
- Persistent volume for vector storage
- In-memory index for fast retrieval

**LLM (Ollama + Mistral 7B):**
- Self-hosted on Render (requires sufficient RAM)
- Alternative: Use Ollama cloud API (free tier available)
- Model loaded on startup, cached in memory

**File Storage:**
- Local filesystem on Render persistent volume
- Alternative: Cloudflare R2 (free tier: 10GB)

### Environment Configuration

**Development:**
```
API_URL=http://localhost:8000
DATABASE_URL=postgresql://localhost/nyaya_mitra_dev
CHROMA_HOST=localhost
CHROMA_PORT=8001
OLLAMA_HOST=http://localhost:11434
JWT_SECRET=dev_secret_key
ENVIRONMENT=development
```

**Production:**
```
API_URL=https://api.nyayamitra.org
DATABASE_URL=postgresql://render_db_url
CHROMA_HOST=localhost
CHROMA_PORT=8001
OLLAMA_HOST=http://localhost:11434
JWT_SECRET=production_secret_key
ENVIRONMENT=production
RATE_LIMIT_ENABLED=true
CACHE_ENABLED=true
```

### Monitoring and Observability

**Free Monitoring Tools:**
- Render built-in metrics (CPU, memory, response times)
- PostgreSQL query performance logs
- Application logs (structured JSON logging)
- Error tracking: Sentry (free tier: 5K events/month)
- Uptime monitoring: UptimeRobot (free tier: 50 monitors)

**Key Metrics to Track:**
- API response times (p50, p95, p99)
- LLM inference times
- Database query times
- Error rates by endpoint
- User registration and query volume
- Cache hit rates
- Rate limit violations

### Scaling Considerations

**When to Scale (Beyond Free Tier):**
- Consistent >1000 concurrent users
- API response times >5 seconds
- Database storage >1GB
- Frequent cold starts impacting UX

**Scaling Path:**
1. Upgrade Render to paid tier ($7/month) for always-on backend
2. Add Redis cache for session management and query caching
3. Upgrade PostgreSQL to larger instance
4. Consider managed Chroma or Pinecone for vector database
5. Use dedicated LLM API (OpenAI, Anthropic) instead of self-hosted

## Security Considerations

### Authentication & Authorization

**JWT Token Security:**
- Access tokens: 24-hour expiry
- Refresh tokens: 30-day expiry, stored securely
- Token signing: HS256 algorithm with strong secret key
- Token validation on every protected endpoint

**Password Security:**
- Minimum length: 8 characters
- Bcrypt hashing with 12 rounds
- No password complexity requirements (length is sufficient)
- Password reset via email with time-limited tokens

### Input Validation

**All User Inputs:**
- Sanitize HTML to prevent XSS
- Validate email formats
- Limit text field lengths
- Validate file uploads (type, size, content)
- Parameterized database queries to prevent SQL injection

**API Request Validation:**
- Pydantic models for request validation
- Type checking for all parameters
- Range validation for numerical inputs
- Enum validation for categorical inputs

### Data Protection

**Encryption:**
- TLS 1.3 for all data in transit
- Database encryption at rest (PostgreSQL native encryption)
- Sensitive fields encrypted with Fernet (symmetric encryption)

**Data Minimization:**
- Collect only necessary user information
- No tracking of user behavior beyond analytics
- Regular data cleanup (delete old sessions, expired tokens)

**Privacy:**
- No third-party data sharing
- User data deletion on account closure
- Anonymized analytics data
- Clear privacy policy and terms of service

### Rate Limiting & Abuse Prevention

**Rate Limits:**
- 100 requests/hour per user (authenticated)
- 20 requests/hour per IP (unauthenticated)
- 10 document generations/day per user
- 50 queries/day per user

**Abuse Detection:**
- Monitor for unusual patterns (rapid requests, large payloads)
- Block IPs with repeated failed login attempts
- CAPTCHA for registration and password reset
- Honeypot fields in forms

### Legal Disclaimers

**Required Disclaimers:**
- "This platform provides general legal information, not legal advice"
- "Consult a qualified lawyer for specific legal matters"
- "AI-generated responses may contain errors"
- "Users are responsible for verifying information accuracy"
- "Platform is not a substitute for professional legal counsel"

**Disclaimer Placement:**
- Prominent display on homepage
- Before first query submission
- In generated documents
- In SOS mode emergency information

## Performance Optimization

### Frontend Optimization

**Code Splitting:**
- Lazy load routes and components
- Dynamic imports for heavy libraries
- Separate bundles for different features

**Asset Optimization:**
- Image compression and lazy loading
- SVG icons instead of icon fonts
- Minified CSS and JavaScript
- Gzip compression

**Caching:**
- Service worker for offline support
- LocalStorage for user preferences
- IndexedDB for offline document storage
- Cache API for static assets

### Backend Optimization

**Database Optimization:**
- Indexes on frequently queried fields (user_id, email, created_at)
- Connection pooling (max 20 connections)
- Query optimization (avoid N+1 queries)
- Pagination for large result sets

**Caching Strategy:**
- Cache frequently accessed legal provisions (1-hour TTL)
- Cache user sessions (24-hour TTL)
- Cache LLM responses for common queries (7-day TTL)
- Cache embeddings for repeated queries

**Async Processing:**
- Async database queries
- Async LLM inference
- Background tasks for non-critical operations (analytics, logging)
- Task queue for bulk operations (document generation, bulk import)

### LLM Optimization

**Prompt Engineering:**
- Concise system prompts
- Structured output formats
- Few-shot examples for consistency
- Token limit management (max 2048 tokens per response)

**Inference Optimization:**
- Batch similar queries when possible
- Cache embeddings for repeated queries
- Use smaller context windows when appropriate
- Quantized model (4-bit) for faster inference

## Maintenance and Updates

### Regular Maintenance Tasks

**Daily:**
- Monitor error rates and system health
- Review security logs for suspicious activity
- Check database backup status

**Weekly:**
- Review user feedback and bug reports
- Update legal knowledge base with new provisions
- Analyze query patterns for quality improvement
- Review and respond to low-confidence queries

**Monthly:**
- Update dependencies and security patches
- Review and optimize database performance
- Analyze usage metrics and user engagement
- Update documentation

**Quarterly:**
- Major feature releases
- Legal knowledge base comprehensive review
- Security audit
- Performance optimization review

### Knowledge Base Updates

**Legal Provision Updates:**
- Monitor official government sources for new laws
- Update IPC/CrPC sections when amended
- Add new case law summaries
- Version all changes with effective dates

**Update Process:**
1. Extract text from official documents
2. Generate embeddings for new content
3. Store in Chroma with metadata
4. Update PostgreSQL index
5. Invalidate related caches
6. Test semantic search accuracy
7. Deploy to production

### Backup and Disaster Recovery

**Backup Strategy:**
- PostgreSQL: Daily automated backups (Render built-in)
- Chroma vector database: Weekly backups to cloud storage
- User-generated documents: Daily backups
- Configuration and secrets: Encrypted backups

**Recovery Procedures:**
- Database restore: <1 hour
- Vector database restore: <2 hours
- Full system restore: <4 hours
- Backup retention: 30 days

**Disaster Recovery Plan:**
1. Detect outage through monitoring
2. Assess impact and root cause
3. Restore from most recent backup
4. Verify data integrity
5. Resume service
6. Post-mortem analysis
7. Implement preventive measures

---

## Appendix: Technology Stack Details

### Backend Technologies

**FastAPI (Python 3.11+):**
- Async request handling
- Automatic API documentation (Swagger/OpenAPI)
- Pydantic for data validation
- Dependency injection for clean architecture

**SQLAlchemy:**
- ORM for PostgreSQL
- Async support with asyncpg
- Migration management with Alembic

**LangChain:**
- RAG pipeline orchestration
- LLM integration (Ollama)
- Vector store integration (Chroma)
- Prompt templates and chains

**Sentence-Transformers:**
- Model: `sentence-transformers/paraphrase-multilingual-mpnet-base-v2`
- Embedding dimension: 768
- Supports 50+ languages including Indian languages

**spaCy:**
- Model: `en_core_web_sm` for English
- NER for entity extraction
- Text preprocessing and tokenization

**IndicNLP:**
- Indian language processing
- Transliteration and translation
- Language detection

### Frontend Technologies

**React.js 18+:**
- Functional components with hooks
- Context API for state management
- React Router for navigation

**Chakra UI:**
- Accessible component library
- Dark mode support
- Responsive design utilities

**Tailwind CSS:**
- Utility-first CSS framework
- Custom design system
- Responsive breakpoints

**Tesseract.js:**
- Client-side OCR
- Supports 100+ languages
- WebAssembly for performance

### Mobile Technologies

**React Native:**
- Cross-platform (Android + iOS)
- Native performance
- Shared codebase with web (80%+)

**React Native Libraries:**
- React Navigation: Navigation
- AsyncStorage: Local storage
- React Native Camera: Document scanning
- React Native Push Notifications: Notifications

### Database Technologies

**PostgreSQL 15+:**
- JSONB for flexible schema
- Full-text search
- PostGIS for location queries (legal aid search)

**Chroma:**
- Vector database for embeddings
- Cosine similarity search
- Persistent storage
- Metadata filtering

### DevOps Technologies

**GitHub Actions:**
- CI/CD pipeline
- Automated testing
- Deployment automation

**Docker:**
- Containerization for consistent environments
- Multi-stage builds for optimization
- Docker Compose for local development

**Render:**
- Backend hosting
- PostgreSQL hosting
- Automatic deployments
- Environment management

**Vercel:**
- Frontend hosting
- Edge functions
- Automatic deployments
- Preview deployments for PRs

---

This design document provides a comprehensive blueprint for implementing the Nyaya Mitra platform. All components are designed to work together seamlessly while maintaining zero-cost operation through strategic use of free-tier services and open-source technologies.
