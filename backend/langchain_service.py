"""
LangChain orchestration service for RAG-based legal query processing.
"""
import re
from typing import Dict, List, Optional, Any
from datetime import datetime
from langchain.prompts import PromptTemplate, ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from ollama_client import get_ollama_client
from aws_bedrock import BedrockClient
from groq_client import get_groq_client
from gemini_client import get_gemini_client
from rag_system import RAGRetrievalSystem
from vector_db import VectorDatabase
from multilingual_service import get_multilingual_service
import os


class LangChainOrchestrator:
    """Orchestrates RAG pipeline using LangChain for legal query processing."""
    
    # Legal query system prompt
    LEGAL_SYSTEM_PROMPT = """You are Nyaya Mitra, an AI legal assistant specializing in Indian law. 
Your role is to provide accurate, helpful legal information to Indian college students.

Guidelines:
1. Base your responses ONLY on the provided legal context
2. Cite specific IPC sections, CrPC sections, or case laws when applicable
3. Use clear, simple language that students can understand
4. If the context doesn't contain enough information, acknowledge limitations
5. Never provide definitive legal advice - always suggest consulting a lawyer for serious matters
6. Be empathetic and supportive in your tone
7. Format citations as [IPC Section XXX] or [Case: Name v. Name]

Context from Indian Legal Database:
{context}

Remember: You are providing legal information, not legal advice."""
    
    # Query prompt template
    QUERY_PROMPT_TEMPLATE = """Based on the legal context provided above, please answer the following question:

Question: {query}

Provide a clear, accurate response with relevant citations."""
    
    # Clarification prompt template
    CLARIFICATION_PROMPT_TEMPLATE = """The user's question is ambiguous or lacks sufficient detail. 
Ask 2-3 specific clarifying questions to better understand their situation.

User's question: {query}

Clarifying questions:"""
    
    def __init__(
        self,
        vector_db: Optional[VectorDatabase] = None,
        rag_system: Optional[RAGRetrievalSystem] = None
    ):
        """
        Initialize LangChain orchestrator.
        
        Args:
            vector_db: Vector database instance (optional, will create if not provided)
            rag_system: RAG retrieval system instance (optional, will create if not provided)
        """
        # Initialize AI Client (Gemini/Groq for Production, Bedrock/Ollama as fallback)
        self.ai_provider = os.getenv("AI_PROVIDER", "gemini").lower()
        
        if self.ai_provider == "gemini":
            self.ai_client = get_gemini_client()
        elif self.ai_provider == "groq":
            self.ai_client = get_groq_client()
        elif self.ai_provider == "bedrock":
            self.ai_client = BedrockClient(
                region=os.getenv("AWS_REGION", "us-east-1"),
                model_id=os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-haiku-20240307-v1:0")
            )
        else:
            self.ai_client = get_ollama_client()
            
        self.vector_db = vector_db or VectorDatabase()
        self.rag_system = rag_system or RAGRetrievalSystem(self.vector_db)
        self.multilingual_service = get_multilingual_service()
        
        # Create prompt templates
        self.query_prompt = PromptTemplate(
            template=self.QUERY_PROMPT_TEMPLATE,
            input_variables=["query"]
        )
        
        self.clarification_prompt = PromptTemplate(
            template=self.CLARIFICATION_PROMPT_TEMPLATE,
            input_variables=["query"]
        )

    
    def process_query(
        self,
        query: str,
        language: str = "en",
        conversation_context: Optional[List[Dict[str, str]]] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a legal query using RAG pipeline.
        
        Args:
            query: User's legal question
            language: Language code (default: "en")
            conversation_context: Previous conversation messages
            filters: Optional metadata filters for retrieval
            
        Returns:
            Dictionary containing:
            - response: AI-generated response
            - citations: List of legal citations
            - confidence: Confidence score (0-1)
            - retrieved_docs: Documents used for context
            - needs_clarification: Whether query needs clarification
            - language: Detected/used language
        """
        # Step 1: Process language
        language_info = self.multilingual_service.process_query_language(query, language)
        response_language = language_info["response_language"]
        
        # Step 2: Retrieve relevant documents using RAG
        context_str, rag_result = self.rag_system.retrieve_with_context(
            query=query,
            n_results=5,
            **(filters or {})
        )
        
        relevant_docs = [{"content": d.text, "metadata": d.metadata, "relevance_score": d.relevance_score} for d in rag_result.documents]
        confidence = rag_result.avg_relevance
        
        # Step 3: Format context from retrieved documents (may be empty)
        context = self._format_context(relevant_docs)
        
        # Step 4: Build system prompt with context and language instructions
        base_system_prompt = self.LEGAL_SYSTEM_PROMPT.format(context=context)
        system_prompt = self.multilingual_service.prepare_multilingual_prompt(
            base_system_prompt,
            response_language
        )
        
        # Step 5: Build user prompt
        user_prompt = self.query_prompt.format(query=query)
        
        # Step 6: Generate response using AI Provider
        try:
            if self.ai_provider == "groq":
                result = self.ai_client.generate(
                    prompt=user_prompt,
                    system_prompt=system_prompt,
                    context=conversation_context,
                    temperature=0.3
                )
                response_text = result["response"]
            elif self.ai_provider == "bedrock":
                response_text = self.ai_client.generate_response(
                    prompt=user_prompt,
                    system_prompt=system_prompt,
                    temperature=0.3
                )
            else:
                result = self.ai_client.generate(
                    prompt=user_prompt,
                    system_prompt=system_prompt,
                    context=conversation_context,
                    temperature=0.3
                )
                response_text = result["response"]
            
        except Exception as e:
            # Handle AI service errors
            error_msg = str(e)
            
            # Provide more helpful error message for payment/access issues
            if "INVALID_PAYMENT_INSTRUMENT" in error_msg or "AccessDeniedException" in error_msg:
                response_text = """I apologize, but the AI service is currently being set up. 

**Status**: AWS Bedrock model access is being configured. This typically takes 2-5 minutes after adding a payment method.

**What you can try**:
1. Wait 2-3 minutes and try again
2. Refresh the page and send your question again
3. Contact support if the issue persists

**For your project demo**: You can show the other features (user registration, legal aid search, document generation) while this is being resolved."""
            else:
                response_text = f"I apologize, but I'm currently unable to process your query due to a technical issue. Please try again in a moment.\n\nTechnical details: {error_msg}"
            
            return {
                "response": response_text,
                "citations": [],
                "confidence": 0.0,
                "retrieved_docs": [],
                "needs_clarification": False,
                "language": response_language,
                "error": error_msg
            }
        
        # Step 7: Extract citations from response
        citations = self._extract_citations(response_text, relevant_docs)
        
        # Step 8: Add disclaimer for low confidence responses
        if confidence < 0.7:
            response_text = self.multilingual_service.add_language_disclaimer(
                response_text,
                response_language,
                add_disclaimer=True
            )
        
        return {
            "response": response_text,
            "citations": citations,
            "confidence": confidence,
            "retrieved_docs": relevant_docs,
            "needs_clarification": False,
            "language": response_language
        }
    
    def _format_context(self, documents: List[Dict[str, Any]]) -> str:
        """
        Format retrieved documents as context for LLM.
        
        Args:
            documents: List of retrieved documents with metadata
            
        Returns:
            Formatted context string
        """
        if not documents:
            return "No relevant legal documents found."
        
        context_parts = []
        for i, doc in enumerate(documents, 1):
            metadata = doc.get("metadata", {})
            content = doc.get("content", "")
            
            # Format document with metadata
            doc_text = f"Document {i}:\n"
            
            if metadata.get("source"):
                doc_text += f"Source: {metadata['source']}\n"
            if metadata.get("category"):
                doc_text += f"Category: {metadata['category']}\n"
            if metadata.get("section"):
                doc_text += f"Section: {metadata['section']}\n"
            
            doc_text += f"Content: {content}\n"
            context_parts.append(doc_text)
        
        return "\n---\n".join(context_parts)
    
    def _extract_citations(
        self,
        response: str,
        retrieved_docs: List[Dict[str, Any]]
    ) -> List[Dict[str, str]]:
        """
        Extract legal citations from response.
        
        Args:
            response: AI-generated response text
            retrieved_docs: Documents used for context
            
        Returns:
            List of citation dictionaries with source, section, and text
        """
        citations = []
        
        # Pattern for IPC sections: [IPC Section XXX]
        ipc_pattern = r'\[IPC Section (\d+[A-Z]?)\]'
        ipc_matches = re.findall(ipc_pattern, response)
        for section in ipc_matches:
            citations.append({
                "type": "IPC",
                "section": section,
                "text": f"IPC Section {section}"
            })
        
        # Pattern for CrPC sections: [CrPC Section XXX]
        crpc_pattern = r'\[CrPC Section (\d+[A-Z]?)\]'
        crpc_matches = re.findall(crpc_pattern, response)
        for section in crpc_matches:
            citations.append({
                "type": "CrPC",
                "section": section,
                "text": f"CrPC Section {section}"
            })
        
        # Pattern for case citations: [Case: Name v. Name]
        case_pattern = r'\[Case: ([^\]]+)\]'
        case_matches = re.findall(case_pattern, response)
        for case_name in case_matches:
            citations.append({
                "type": "Case Law",
                "case_name": case_name,
                "text": f"Case: {case_name}"
            })
        
        # Add sources from retrieved documents
        for doc in retrieved_docs:
            metadata = doc.get("metadata", {})
            if metadata.get("source") and metadata.get("section"):
                # Check if this citation is already in the list
                citation_text = f"{metadata['source']} Section {metadata['section']}"
                if not any(c.get("text") == citation_text for c in citations):
                    citations.append({
                        "type": metadata.get("category", "Legal Document"),
                        "source": metadata["source"],
                        "section": metadata["section"],
                        "text": citation_text
                    })
        
        return citations
    
    def _generate_clarification(self, query: str, language: str = "en") -> str:
        """
        Generate clarifying questions for ambiguous queries.
        
        Args:
            query: User's ambiguous query
            language: Response language code
            
        Returns:
            Response with clarifying questions
        """
        prompt = self.clarification_prompt.format(query=query)
        
        # Add language instruction
        system_prompt = self.multilingual_service.prepare_multilingual_prompt(
            "You are a helpful legal assistant.",
            language
        )
        
        try:
            if self.ai_provider == "bedrock":
                clarification = self.ai_client.generate_response(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    temperature=0.5
                )
            else:
                result = self.ai_client.generate(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    temperature=0.5  # Slightly higher temperature for variety
                )
                clarification = result["response"]
            
            # Add preamble based on language
            if language == "hi":
                response = "मैं आपकी स्थिति को बेहतर ढंग से समझना चाहता हूं। कृपया स्पष्ट करें:\n\n"
            elif language == "ta":
                response = "உங்கள் சூழ்நிலையை நன்கு புரிந்து கொள்ள விரும்புகிறேன். தயவுசெய்து விளக்கவும்:\n\n"
            elif language == "te":
                response = "మీ పరిస్థితిని బాగా అర్థం చేసుకోవాలనుకుంటున్నాను. దయచేసి స్పష్టం చేయండి:\n\n"
            elif language == "bn":
                response = "আমি আপনার পরিস্থিতি ভালোভাবে বুঝতে চাই। অনুগ্রহ করে স্পষ্ট করুন:\n\n"
            elif language == "mr":
                response = "मला तुमची परिस्थिती चांगल्या प्रकारे समजून घ्यायची आहे. कृपया स्पष्ट करा:\n\n"
            elif language == "gu":
                response = "હું તમારી પરિસ્થિતિને વધુ સારી રીતે સમજવા માંગુ છું. કૃપા કરીને સ્પષ્ટ કરો:\n\n"
            else:  # English
                response = "I'd like to better understand your situation to provide accurate guidance. Could you please clarify:\n\n"
            
            response += clarification
            
            return response
            
        except RuntimeError:
            # Fallback clarification based on language
            if language == "hi":
                return "मैं आपकी स्थिति को बेहतर ढंग से समझना चाहता हूं। कृपया अधिक विवरण प्रदान करें:\n\n1. आपके मामले की विशिष्ट परिस्थितियां\n2. अब तक क्या कार्रवाई की गई है\n3. आप क्या परिणाम प्राप्त करना चाहते हैं"
            elif language == "ta":
                return "உங்கள் சூழ்நிலையை நன்கு புரிந்து கொள்ள விரும்புகிறேன். மேலும் விவரங்களை வழங்கவும்:\n\n1. உங்கள் வழக்கின் குறிப்பிட்ட சூழ்நிலைகள்\n2. இதுவரை என்ன நடவடிக்கைகள் எடுக்கப்பட்டுள்ளன\n3. நீங்கள் என்ன முடிவை எதிர்பார்க்கிறீர்கள்"
            else:
                return "I'd like to better understand your situation. Could you please provide more details about:\n\n1. The specific circumstances of your case\n2. What actions have been taken so far\n3. What outcome you're hoping to achieve"
    
    def process_query_stream(
        self,
        query: str,
        language: str = "en",
        conversation_context: Optional[List[Dict[str, str]]] = None,
        filters: Optional[Dict[str, Any]] = None
    ):
        """
        Process a legal query using RAG pipeline with streaming response.
        
        Args:
            query: User's legal question
            language: Language code (default: "en")
            conversation_context: Previous conversation messages
            filters: Optional metadata filters for retrieval
            
        Yields:
            Dictionary chunks containing:
            - type: "metadata", "token", "citations", or "error"
            - data: Chunk-specific data
        """
        try:
            # Step 1: Process language
            language_info = self.multilingual_service.process_query_language(query, language)
            response_language = language_info["response_language"]
            
            # Step 2: Retrieve relevant documents using RAG
            context_str, rag_result = self.rag_system.retrieve_with_context(
                query=query,
                n_results=5,
                **(filters or {})
            )
            
            relevant_docs = [{"content": d.text, "metadata": d.metadata, "relevance_score": d.relevance_score} for d in rag_result.documents]
            confidence = rag_result.avg_relevance
            
            # Send metadata first
            yield {
                "type": "metadata",
                "data": {
                    "confidence": confidence,
                    "language": response_language,
                    "needs_clarification": False
                }
            }
            
            # Step 3: Format context from retrieved documents
            context = self._format_context(relevant_docs)
            
            # Step 5: Build system prompt with context and language instructions
            base_system_prompt = self.LEGAL_SYSTEM_PROMPT.format(context=context)
            system_prompt = self.multilingual_service.prepare_multilingual_prompt(
                base_system_prompt,
                response_language
            )
            
            # Step 6: Build user prompt
            user_prompt = self.query_prompt.format(query=query)
            
            # Step 7: Stream response from AI Provider
            full_response = ""
            
            if self.ai_provider == "bedrock":
                for token in self.ai_client.stream_response(
                    prompt=user_prompt,
                    system_prompt=system_prompt
                ):
                    full_response += token
                    yield {
                        "type": "token",
                        "data": {"content": token}
                    }
            else:
                for chunk in self.ai_client.generate_stream(
                    prompt=user_prompt,
                    system_prompt=system_prompt,
                    context=conversation_context,
                    temperature=0.3
                ):
                    if chunk.get("message", {}).get("content"):
                        token = chunk["message"]["content"]
                        full_response += token
                        yield {
                            "type": "token",
                            "data": {"content": token}
                        }
            
            # Step 8: Extract citations from full response
            citations = self._extract_citations(full_response, relevant_docs)
            
            # Step 9: Send citations
            yield {
                "type": "citations",
                "data": {"citations": citations}
            }
            
        except Exception as e:
            yield {
                "type": "error",
                "data": {"message": str(e)}
            }
    
    def calculate_confidence_score(
        self,
        retrieved_docs: List[Dict[str, Any]],
        relevance_scores: List[float]
    ) -> float:
        """
        Calculate confidence score based on retrieval quality.
        
        Args:
            retrieved_docs: Retrieved documents
            relevance_scores: Relevance scores for each document
            
        Returns:
            Confidence score between 0 and 1
        """
        if not relevance_scores:
            return 0.0
        
        # Average relevance score
        avg_relevance = sum(relevance_scores) / len(relevance_scores)
        
        # Penalize if we have very few documents
        doc_count_factor = min(len(retrieved_docs) / 3, 1.0)
        
        # Final confidence is weighted average
        confidence = (avg_relevance * 0.8) + (doc_count_factor * 0.2)
        
        return min(max(confidence, 0.0), 1.0)


# Singleton instance
_langchain_orchestrator: Optional[LangChainOrchestrator] = None


def get_langchain_orchestrator() -> LangChainOrchestrator:
    """
    Get or create singleton LangChain orchestrator instance.
    
    Returns:
        LangChainOrchestrator instance
    """
    global _langchain_orchestrator
    if _langchain_orchestrator is None:
        _langchain_orchestrator = LangChainOrchestrator()
    return _langchain_orchestrator
