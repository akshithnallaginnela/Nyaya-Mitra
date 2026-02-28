"""
Tests for LangChain orchestration service.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from langchain_service import LangChainOrchestrator, get_langchain_orchestrator


class TestLangChainOrchestrator:
    """Test suite for LangChainOrchestrator."""
    
    @patch('langchain_service.get_ollama_client')
    @patch('langchain_service.VectorDatabase')
    @patch('langchain_service.RAGRetrievalSystem')
    def test_initialization(self, mock_rag, mock_vdb, mock_ollama):
        """Test orchestrator initialization."""
        orchestrator = LangChainOrchestrator()
        
        assert orchestrator.ollama_client is not None
        assert orchestrator.vector_db is not None
        assert orchestrator.rag_system is not None
        assert orchestrator.query_prompt is not None
        assert orchestrator.clarification_prompt is not None
    
    @patch('langchain_service.get_ollama_client')
    @patch('langchain_service.RAGRetrievalSystem')
    def test_process_query_success(self, mock_rag_class, mock_ollama):
        """Test successful query processing."""
        # Mock RAG retrieval
        mock_rag = Mock()
        mock_rag.retrieve_with_context.return_value = {
            "documents": [
                {
                    "content": "IPC Section 499 defines defamation",
                    "metadata": {
                        "source": "IPC",
                        "category": "Criminal Law",
                        "section": "499"
                    }
                }
            ],
            "average_relevance": 0.85
        }
        mock_rag_class.return_value = mock_rag
        
        # Mock Ollama response
        mock_ollama_client = Mock()
        mock_ollama_client.generate.return_value = {
            "response": "Defamation is defined under [IPC Section 499]. It involves making false statements that harm someone's reputation.",
            "model": "mistral:7b",
            "done": True
        }
        mock_ollama.return_value = mock_ollama_client
        
        orchestrator = LangChainOrchestrator(rag_system=mock_rag)
        result = orchestrator.process_query("What is defamation?")
        
        assert "response" in result
        assert "citations" in result
        assert "confidence" in result
        assert result["confidence"] == 0.85
        assert result["needs_clarification"] is False
        assert len(result["citations"]) > 0
    
    @patch('langchain_service.get_ollama_client')
    @patch('langchain_service.RAGRetrievalSystem')
    def test_process_query_low_confidence_clarification(self, mock_rag_class, mock_ollama):
        """Test query processing with low confidence triggers clarification."""
        # Mock RAG retrieval with low confidence
        mock_rag = Mock()
        mock_rag.retrieve_with_context.return_value = {
            "documents": [],
            "average_relevance": 0.4
        }
        mock_rag_class.return_value = mock_rag
        
        # Mock Ollama clarification response
        mock_ollama_client = Mock()
        mock_ollama_client.generate.return_value = {
            "response": "1. What type of case is this?\n2. When did this happen?\n3. What evidence do you have?",
            "model": "mistral:7b",
            "done": True
        }
        mock_ollama.return_value = mock_ollama_client
        
        orchestrator = LangChainOrchestrator(rag_system=mock_rag)
        result = orchestrator.process_query("I need help")
        
        assert result["needs_clarification"] is True
        assert result["confidence"] == 0.4
        assert "clarify" in result["response"].lower() or "understand" in result["response"].lower()

    
    @patch('langchain_service.get_ollama_client')
    @patch('langchain_service.RAGRetrievalSystem')
    def test_process_query_medium_confidence_disclaimer(self, mock_rag_class, mock_ollama):
        """Test query processing with medium confidence adds disclaimer."""
        # Mock RAG retrieval with medium confidence
        mock_rag = Mock()
        mock_rag.retrieve_with_context.return_value = {
            "documents": [
                {
                    "content": "Some legal information",
                    "metadata": {"source": "IPC", "section": "100"}
                }
            ],
            "average_relevance": 0.65
        }
        mock_rag_class.return_value = mock_rag
        
        # Mock Ollama response
        mock_ollama_client = Mock()
        mock_ollama_client.generate.return_value = {
            "response": "Here is some legal information.",
            "model": "mistral:7b",
            "done": True
        }
        mock_ollama.return_value = mock_ollama_client
        
        orchestrator = LangChainOrchestrator(rag_system=mock_rag)
        result = orchestrator.process_query("Tell me about this law")
        
        assert result["confidence"] == 0.65
        assert "⚠️" in result["response"]
        assert "legal professional" in result["response"].lower()
    
    @patch('langchain_service.get_ollama_client')
    @patch('langchain_service.RAGRetrievalSystem')
    def test_process_query_with_conversation_context(self, mock_rag_class, mock_ollama):
        """Test query processing with conversation context."""
        mock_rag = Mock()
        mock_rag.retrieve_with_context.return_value = {
            "documents": [{"content": "Legal info", "metadata": {}}],
            "average_relevance": 0.8
        }
        mock_rag_class.return_value = mock_rag
        
        mock_ollama_client = Mock()
        mock_ollama_client.generate.return_value = {
            "response": "Based on our previous discussion...",
            "model": "mistral:7b",
            "done": True
        }
        mock_ollama.return_value = mock_ollama_client
        
        context = [
            {"role": "user", "content": "What is defamation?"},
            {"role": "assistant", "content": "Defamation is..."}
        ]
        
        orchestrator = LangChainOrchestrator(rag_system=mock_rag)
        result = orchestrator.process_query("Can you explain more?", conversation_context=context)
        
        # Verify context was passed to Ollama
        mock_ollama_client.generate.assert_called_once()
        call_kwargs = mock_ollama_client.generate.call_args[1]
        assert call_kwargs["context"] == context
    
    @patch('langchain_service.get_ollama_client')
    @patch('langchain_service.RAGRetrievalSystem')
    def test_process_query_ollama_error(self, mock_rag_class, mock_ollama):
        """Test query processing handles Ollama errors gracefully."""
        mock_rag = Mock()
        mock_rag.retrieve_with_context.return_value = {
            "documents": [{"content": "Legal info", "metadata": {}}],
            "average_relevance": 0.8
        }
        mock_rag_class.return_value = mock_rag
        
        mock_ollama_client = Mock()
        mock_ollama_client.generate.side_effect = RuntimeError("Ollama service unavailable")
        mock_ollama.return_value = mock_ollama_client
        
        orchestrator = LangChainOrchestrator(rag_system=mock_rag)
        result = orchestrator.process_query("What is the law?")
        
        assert "error" in result
        assert "technical issue" in result["response"].lower()
        assert result["confidence"] == 0.0
    
    def test_format_context_with_documents(self):
        """Test context formatting with documents."""
        orchestrator = LangChainOrchestrator()
        
        documents = [
            {
                "content": "IPC Section 499 defines defamation",
                "metadata": {
                    "source": "IPC",
                    "category": "Criminal Law",
                    "section": "499"
                }
            },
            {
                "content": "CrPC Section 200 deals with examination of complainant",
                "metadata": {
                    "source": "CrPC",
                    "category": "Procedure",
                    "section": "200"
                }
            }
        ]
        
        context = orchestrator._format_context(documents)
        
        assert "Document 1:" in context
        assert "Document 2:" in context
        assert "IPC Section 499" in context
        assert "CrPC Section 200" in context
        assert "Source: IPC" in context
        assert "Category: Criminal Law" in context
    
    def test_format_context_empty(self):
        """Test context formatting with no documents."""
        orchestrator = LangChainOrchestrator()
        context = orchestrator._format_context([])
        
        assert context == "No relevant legal documents found."
    
    def test_extract_citations_ipc(self):
        """Test citation extraction for IPC sections."""
        orchestrator = LangChainOrchestrator()
        
        response = "According to [IPC Section 499], defamation is defined as..."
        docs = []
        
        citations = orchestrator._extract_citations(response, docs)
        
        assert len(citations) >= 1
        assert any(c["type"] == "IPC" and c["section"] == "499" for c in citations)
    
    def test_extract_citations_crpc(self):
        """Test citation extraction for CrPC sections."""
        orchestrator = LangChainOrchestrator()
        
        response = "Under [CrPC Section 200], the magistrate shall examine the complainant."
        docs = []
        
        citations = orchestrator._extract_citations(response, docs)
        
        assert len(citations) >= 1
        assert any(c["type"] == "CrPC" and c["section"] == "200" for c in citations)
    
    def test_extract_citations_case_law(self):
        """Test citation extraction for case laws."""
        orchestrator = LangChainOrchestrator()
        
        response = "As established in [Case: Vishaka v. State of Rajasthan], workplace harassment..."
        docs = []
        
        citations = orchestrator._extract_citations(response, docs)
        
        assert len(citations) >= 1
        assert any(c["type"] == "Case Law" and "Vishaka" in c["case_name"] for c in citations)
    
    def test_extract_citations_from_retrieved_docs(self):
        """Test citation extraction from retrieved documents."""
        orchestrator = LangChainOrchestrator()
        
        response = "Here is some information about defamation."
        docs = [
            {
                "content": "Legal content",
                "metadata": {
                    "source": "IPC",
                    "category": "Criminal Law",
                    "section": "499"
                }
            }
        ]
        
        citations = orchestrator._extract_citations(response, docs)
        
        assert len(citations) >= 1
        assert any(c["source"] == "IPC" and c["section"] == "499" for c in citations)
    
    def test_extract_citations_no_duplicates(self):
        """Test citation extraction avoids duplicates."""
        orchestrator = LangChainOrchestrator()
        
        response = "According to [IPC Section 499], defamation..."
        docs = [
            {
                "content": "Legal content",
                "metadata": {
                    "source": "IPC",
                    "category": "Criminal Law",
                    "section": "499"
                }
            }
        ]
        
        citations = orchestrator._extract_citations(response, docs)
        
        # Should not have duplicate IPC 499 citations
        ipc_499_citations = [c for c in citations if c.get("section") == "499"]
        assert len(ipc_499_citations) <= 2  # One from response, one from docs
    
    @patch('langchain_service.get_ollama_client')
    def test_generate_clarification_success(self, mock_ollama):
        """Test clarification generation."""
        mock_ollama_client = Mock()
        mock_ollama_client.generate.return_value = {
            "response": "1. What type of case?\n2. When did it happen?\n3. What evidence?",
            "model": "mistral:7b",
            "done": True
        }
        mock_ollama.return_value = mock_ollama_client
        
        orchestrator = LangChainOrchestrator()
        clarification = orchestrator._generate_clarification("I need help")
        
        assert "understand" in clarification.lower() or "clarify" in clarification.lower()
        assert "?" in clarification  # Should contain questions
    
    @patch('langchain_service.get_ollama_client')
    def test_generate_clarification_error_fallback(self, mock_ollama):
        """Test clarification generation with error uses fallback."""
        mock_ollama_client = Mock()
        mock_ollama_client.generate.side_effect = RuntimeError("Service error")
        mock_ollama.return_value = mock_ollama_client
        
        orchestrator = LangChainOrchestrator()
        clarification = orchestrator._generate_clarification("I need help")
        
        assert "understand" in clarification.lower()
        assert "circumstances" in clarification.lower()
    
    def test_calculate_confidence_score_high(self):
        """Test confidence calculation with high relevance."""
        orchestrator = LangChainOrchestrator()
        
        docs = [{"content": "doc1"}, {"content": "doc2"}, {"content": "doc3"}]
        scores = [0.9, 0.85, 0.8]
        
        confidence = orchestrator.calculate_confidence_score(docs, scores)
        
        assert 0.8 <= confidence <= 1.0
    
    def test_calculate_confidence_score_low(self):
        """Test confidence calculation with low relevance."""
        orchestrator = LangChainOrchestrator()
        
        docs = [{"content": "doc1"}]
        scores = [0.3]
        
        confidence = orchestrator.calculate_confidence_score(docs, scores)
        
        assert 0.0 <= confidence <= 0.5
    
    def test_calculate_confidence_score_empty(self):
        """Test confidence calculation with no documents."""
        orchestrator = LangChainOrchestrator()
        
        confidence = orchestrator.calculate_confidence_score([], [])
        
        assert confidence == 0.0
    
    def test_calculate_confidence_score_bounds(self):
        """Test confidence score is bounded between 0 and 1."""
        orchestrator = LangChainOrchestrator()
        
        # Test upper bound
        docs = [{"content": f"doc{i}"} for i in range(10)]
        scores = [1.0] * 10
        confidence = orchestrator.calculate_confidence_score(docs, scores)
        assert confidence <= 1.0
        
        # Test lower bound
        docs = [{"content": "doc"}]
        scores = [0.0]
        confidence = orchestrator.calculate_confidence_score(docs, scores)
        assert confidence >= 0.0


def test_get_langchain_orchestrator_singleton():
    """Test get_langchain_orchestrator returns singleton instance."""
    # Reset singleton
    import langchain_service
    langchain_service._langchain_orchestrator = None
    
    orchestrator1 = get_langchain_orchestrator()
    orchestrator2 = get_langchain_orchestrator()
    
    assert orchestrator1 is orchestrator2


def test_get_langchain_orchestrator_creates_instance():
    """Test get_langchain_orchestrator creates LangChainOrchestrator instance."""
    # Reset singleton
    import langchain_service
    langchain_service._langchain_orchestrator = None
    
    orchestrator = get_langchain_orchestrator()
    assert isinstance(orchestrator, LangChainOrchestrator)
