"""
Tests for RAG retrieval system.

Tests cover:
- Query embedding and retrieval
- Top-N document retrieval
- Metadata filtering (language, category, source)
- Relevance score calculation
- Context formatting

Requirements: 10.1, 1.3
"""

import os
import pytest
import shutil

from rag_system import RAGRetrievalSystem, RetrievedDocument, RetrievalResult
from vector_db import VectorDatabase
from document_ingestion import DocumentIngestionPipeline


@pytest.fixture
def test_vector_db():
    """Create a test vector database with sample documents."""
    import uuid
    test_dir = "./test_rag_chroma_db"
    collection_name = f"test_rag_{uuid.uuid4().hex[:8]}"
    
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
    
    db = VectorDatabase(
        persist_directory=test_dir,
        collection_name=collection_name
    )
    
    # Add sample documents
    sample_docs = [
        {
            "id": "ipc_302",
            "text": "Section 302 IPC: Punishment for murder. Whoever commits murder shall be punished with death or imprisonment for life.",
            "source": "IPC",
            "category": "criminal",
            "language": "en",
            "section": "302",
            "title": "Murder"
        },
        {
            "id": "ipc_304",
            "text": "Section 304 IPC: Culpable homicide not amounting to murder. Punishment with imprisonment for life or up to ten years.",
            "source": "IPC",
            "category": "criminal",
            "language": "en",
            "section": "304"
        },
        {
            "id": "crpc_154",
            "text": "Section 154 CrPC: Information in cognizable cases. FIR must be registered by police for cognizable offences.",
            "source": "CrPC",
            "category": "procedure",
            "language": "en",
            "section": "154",
            "title": "FIR"
        },
        {
            "id": "const_21",
            "text": "Article 21: Right to life and personal liberty. No person shall be deprived of life or liberty except by law.",
            "source": "Constitution",
            "category": "fundamental_rights",
            "language": "en",
            "section": "21"
        },
        {
            "id": "ipc_420",
            "text": "Section 420 IPC: Cheating and dishonestly inducing delivery of property. Punishment up to seven years.",
            "source": "IPC",
            "category": "criminal",
            "language": "en",
            "section": "420"
        }
    ]
    
    pipeline = DocumentIngestionPipeline(vector_db=db)
    pipeline.ingest_documents_batch(sample_docs)
    
    yield db
    
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)


@pytest.fixture
def rag_system(test_vector_db):
    """Create a RAG retrieval system."""
    return RAGRetrievalSystem(vector_db=test_vector_db, default_n_results=5)


class TestBasicRetrieval:
    """Test basic retrieval functionality."""
    
    def test_retrieve_returns_results(self, rag_system):
        """Test that retrieve returns results for a valid query."""
        result = rag_system.retrieve("what is the punishment for murder")
        
        assert isinstance(result, RetrievalResult)
        assert result.total_retrieved > 0
        assert len(result.documents) > 0
    
    def test_retrieve_respects_n_results(self, rag_system):
        """Test that retrieve returns requested number of results."""
        result = rag_system.retrieve("legal section", n_results=3)
        
        assert result.total_retrieved <= 3
        assert len(result.documents) <= 3
    
    def test_retrieve_returns_relevant_documents(self, rag_system):
        """Test that retrieved documents are relevant to query."""
        result = rag_system.retrieve("murder punishment IPC")
        
        # Should retrieve IPC 302 (murder) as most relevant
        assert result.total_retrieved > 0
        assert any("302" in doc.id or "murder" in doc.text.lower() 
                  for doc in result.documents)
    
    def test_retrieve_empty_query_returns_empty_result(self, rag_system):
        """Test that empty query returns empty result."""
        result = rag_system.retrieve("")
        
        assert result.total_retrieved == 0
        assert len(result.documents) == 0
    
    def test_retrieve_calculates_relevance_scores(self, rag_system):
        """Test that relevance scores are calculated."""
        result = rag_system.retrieve("murder")
        
        assert all(0.0 <= doc.relevance_score <= 1.0 for doc in result.documents)
        assert result.avg_relevance > 0.0


class TestMetadataFiltering:
    """Test metadata filtering functionality."""
    
    def test_retrieve_by_language(self, rag_system):
        """Test filtering by language."""
        result = rag_system.retrieve_by_language("legal section", language="en")
        
        assert all(doc.metadata.get('language') == 'en' for doc in result.documents)
    
    def test_retrieve_by_category(self, rag_system):
        """Test filtering by category."""
        result = rag_system.retrieve_by_category("punishment", category="criminal")
        
        assert all(doc.metadata.get('category') == 'criminal' for doc in result.documents)
    
    def test_retrieve_by_source(self, rag_system):
        """Test filtering by source."""
        result = rag_system.retrieve_by_source("section", source="IPC")
        
        assert all(doc.metadata.get('source') == 'IPC' for doc in result.documents)
    
    def test_retrieve_with_multiple_filters(self, rag_system):
        """Test filtering with multiple criteria."""
        result = rag_system.retrieve(
            query="punishment",
            language="en",
            category="criminal",
            source="IPC"
        )
        
        for doc in result.documents:
            assert doc.metadata.get('language') == 'en'
            assert doc.metadata.get('category') == 'criminal'
            assert doc.metadata.get('source') == 'IPC'
    
    def test_retrieve_with_no_matching_filters_returns_empty(self, rag_system):
        """Test that non-matching filters return empty results."""
        result = rag_system.retrieve(
            query="murder",
            source="NonExistentSource"
        )
        
        assert result.total_retrieved == 0


class TestRelevanceScoring:
    """Test relevance score calculation."""
    
    def test_relevance_scores_are_normalized(self, rag_system):
        """Test that relevance scores are between 0 and 1."""
        result = rag_system.retrieve("murder punishment")
        
        for doc in result.documents:
            assert 0.0 <= doc.relevance_score <= 1.0
    
    def test_more_relevant_documents_have_higher_scores(self, rag_system):
        """Test that more relevant documents have higher scores."""
        result = rag_system.retrieve("murder IPC 302")
        
        if len(result.documents) >= 2:
            # First document should be most relevant
            assert result.documents[0].relevance_score >= result.documents[1].relevance_score
    
    def test_min_relevance_filter(self, rag_system):
        """Test minimum relevance threshold filtering."""
        result = rag_system.retrieve("legal", min_relevance=0.5)
        
        assert all(doc.relevance_score >= 0.5 for doc in result.documents)


class TestContextFormatting:
    """Test context formatting for LLM."""
    
    def test_retrieve_with_context_returns_formatted_string(self, rag_system):
        """Test that context is properly formatted."""
        context, result = rag_system.retrieve_with_context("murder punishment")
        
        assert isinstance(context, str)
        assert len(context) > 0
        assert isinstance(result, RetrievalResult)
    
    def test_context_includes_document_metadata(self, rag_system):
        """Test that context includes source and section info."""
        context, result = rag_system.retrieve_with_context("IPC 302")
        
        if result.total_retrieved > 0:
            # Context should include document markers
            assert "[Document" in context
    
    def test_context_for_empty_results(self, rag_system):
        """Test context formatting when no documents found."""
        context, result = rag_system.retrieve_with_context(
            "nonexistent query xyz123",
            source="NonExistent"
        )
        
        assert "No relevant documents found" in context or result.total_retrieved == 0


class TestRetrievalStatistics:
    """Test retrieval statistics."""
    
    def test_get_retrieval_stats(self, rag_system):
        """Test getting retrieval statistics."""
        result = rag_system.retrieve("murder")
        stats = rag_system.get_retrieval_stats(result)
        
        assert 'total_documents' in stats
        assert 'avg_relevance' in stats
        assert 'min_relevance' in stats
        assert 'max_relevance' in stats
        assert 'sources' in stats
        assert 'categories' in stats
        assert 'languages' in stats
    
    def test_stats_counts_by_source(self, rag_system):
        """Test that stats count documents by source."""
        result = rag_system.retrieve("section")
        stats = rag_system.get_retrieval_stats(result)
        
        assert isinstance(stats['sources'], dict)
        assert sum(stats['sources'].values()) == result.total_retrieved
    
    def test_stats_for_empty_result(self, rag_system):
        """Test stats for empty retrieval result."""
        result = rag_system.retrieve("", n_results=0)
        stats = rag_system.get_retrieval_stats(result)
        
        assert stats['total_documents'] == 0
        assert stats['avg_relevance'] == 0.0


class TestRetrievalResult:
    """Test RetrievalResult dataclass."""
    
    def test_retrieval_result_structure(self, rag_system):
        """Test RetrievalResult has correct structure."""
        result = rag_system.retrieve("test query")
        
        assert hasattr(result, 'query')
        assert hasattr(result, 'documents')
        assert hasattr(result, 'total_retrieved')
        assert hasattr(result, 'avg_relevance')
    
    def test_retrieved_document_structure(self, rag_system):
        """Test RetrievedDocument has correct structure."""
        result = rag_system.retrieve("murder")
        
        if result.documents:
            doc = result.documents[0]
            assert hasattr(doc, 'id')
            assert hasattr(doc, 'text')
            assert hasattr(doc, 'metadata')
            assert hasattr(doc, 'relevance_score')


class TestDefaultBehavior:
    """Test default behavior and configuration."""
    
    def test_default_n_results_is_5(self, test_vector_db):
        """Test that default n_results is 5."""
        rag = RAGRetrievalSystem(vector_db=test_vector_db)
        
        assert rag.default_n_results == 5
    
    def test_custom_default_n_results(self, test_vector_db):
        """Test setting custom default n_results."""
        rag = RAGRetrievalSystem(vector_db=test_vector_db, default_n_results=3)
        
        result = rag.retrieve("legal")
        assert result.total_retrieved <= 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
