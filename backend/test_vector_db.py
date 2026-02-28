"""
Tests for vector database functionality.

Tests cover:
- ChromaDB initialization
- Document addition and retrieval
- Embedding generation
- Similarity search
- Metadata filtering

Requirements: 10.1
"""

import pytest
import shutil
import os

from vector_db import VectorDatabase


@pytest.fixture
def test_vector_db():
    """Create a test vector database and clean up after."""
    test_dir = "./test_chroma_db"
    
    # Create test database
    db = VectorDatabase(
        persist_directory=test_dir,
        collection_name="test_legal_documents"
    )
    
    yield db
    
    # Clean up
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)


class TestVectorDatabaseInitialization:
    """Test vector database initialization."""
    
    def test_creates_persist_directory(self, test_vector_db):
        """Test that persist directory is created."""
        assert os.path.exists(test_vector_db.persist_directory)
    
    def test_creates_collection(self, test_vector_db):
        """Test that collection is created."""
        assert test_vector_db.collection is not None
        assert test_vector_db.collection.name == "test_legal_documents"
    
    def test_loads_embedding_model(self, test_vector_db):
        """Test that embedding model is loaded."""
        assert test_vector_db.embedding_model is not None


class TestEmbeddingGeneration:
    """Test embedding generation."""
    
    def test_generates_embedding_for_text(self, test_vector_db):
        """Test that embeddings are generated for text."""
        text = "Section 302 of IPC deals with murder"
        embedding = test_vector_db.generate_embedding(text)
        
        assert isinstance(embedding, list)
        assert len(embedding) > 0
        assert all(isinstance(x, float) for x in embedding)
    
    def test_embedding_dimension_consistency(self, test_vector_db):
        """Test that embeddings have consistent dimensions."""
        text1 = "Section 302 of IPC"
        text2 = "Article 21 of Constitution"
        
        embedding1 = test_vector_db.generate_embedding(text1)
        embedding2 = test_vector_db.generate_embedding(text2)
        
        assert len(embedding1) == len(embedding2)
    
    def test_similar_texts_have_similar_embeddings(self, test_vector_db):
        """Test that similar texts produce similar embeddings."""
        import numpy as np
        
        text1 = "murder under IPC section 302"
        text2 = "homicide under section 302 IPC"
        text3 = "traffic violation fine"
        
        emb1 = np.array(test_vector_db.generate_embedding(text1))
        emb2 = np.array(test_vector_db.generate_embedding(text2))
        emb3 = np.array(test_vector_db.generate_embedding(text3))
        
        # Cosine similarity
        sim_12 = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
        sim_13 = np.dot(emb1, emb3) / (np.linalg.norm(emb1) * np.linalg.norm(emb3))
        
        # Similar texts should have higher similarity
        assert sim_12 > sim_13


class TestDocumentOperations:
    """Test document addition and retrieval."""
    
    def test_add_single_document(self, test_vector_db):
        """Test adding a single document."""
        test_vector_db.add_document(
            document_id="ipc_302",
            text="Section 302: Punishment for murder",
            metadata={"source": "IPC", "category": "criminal", "language": "en"}
        )
        
        assert test_vector_db.count_documents() == 1
    
    def test_add_multiple_documents_batch(self, test_vector_db):
        """Test adding multiple documents in batch."""
        ids = ["ipc_302", "ipc_304", "ipc_307"]
        texts = [
            "Section 302: Punishment for murder",
            "Section 304: Culpable homicide not amounting to murder",
            "Section 307: Attempt to murder"
        ]
        metadatas = [
            {"source": "IPC", "category": "criminal", "section": "302"},
            {"source": "IPC", "category": "criminal", "section": "304"},
            {"source": "IPC", "category": "criminal", "section": "307"}
        ]
        
        test_vector_db.add_documents_batch(ids, texts, metadatas)
        
        assert test_vector_db.count_documents() == 3
    
    def test_get_document_by_id(self, test_vector_db):
        """Test retrieving a document by ID."""
        test_vector_db.add_document(
            document_id="ipc_302",
            text="Section 302: Punishment for murder",
            metadata={"source": "IPC"}
        )
        
        doc = test_vector_db.get_document("ipc_302")
        
        assert doc is not None
        assert doc['id'] == "ipc_302"
        assert "murder" in doc['document'].lower()
        assert doc['metadata']['source'] == "IPC"
    
    def test_get_nonexistent_document_returns_none(self, test_vector_db):
        """Test that getting a nonexistent document returns None."""
        doc = test_vector_db.get_document("nonexistent")
        assert doc is None
    
    def test_delete_document(self, test_vector_db):
        """Test deleting a document."""
        test_vector_db.add_document(
            document_id="ipc_302",
            text="Section 302: Punishment for murder"
        )
        
        assert test_vector_db.count_documents() == 1
        
        test_vector_db.delete_document("ipc_302")
        
        assert test_vector_db.count_documents() == 0


class TestSimilaritySearch:
    """Test similarity search functionality."""
    
    def test_query_returns_similar_documents(self, test_vector_db):
        """Test that query returns similar documents."""
        # Add documents
        ids = ["ipc_302", "ipc_304", "ipc_307", "crpc_154"]
        texts = [
            "Section 302 IPC: Punishment for murder - whoever commits murder shall be punished",
            "Section 304 IPC: Culpable homicide not amounting to murder",
            "Section 307 IPC: Attempt to murder",
            "Section 154 CrPC: Information in cognizable cases - FIR registration"
        ]
        metadatas = [
            {"source": "IPC", "category": "criminal"},
            {"source": "IPC", "category": "criminal"},
            {"source": "IPC", "category": "criminal"},
            {"source": "CrPC", "category": "procedure"}
        ]
        
        test_vector_db.add_documents_batch(ids, texts, metadatas)
        
        # Query for murder-related documents
        results = test_vector_db.query("what is the punishment for murder", n_results=2)
        
        assert len(results['ids'][0]) == 2
        assert "ipc_302" in results['ids'][0]
    
    def test_query_respects_n_results(self, test_vector_db):
        """Test that query returns requested number of results."""
        # Add 5 documents
        ids = [f"doc_{i}" for i in range(5)]
        texts = [f"Document {i} about legal matters" for i in range(5)]
        
        test_vector_db.add_documents_batch(ids, texts)
        
        # Query for 3 results
        results = test_vector_db.query("legal matters", n_results=3)
        
        assert len(results['ids'][0]) == 3
    
    def test_query_with_metadata_filter(self, test_vector_db):
        """Test querying with metadata filters."""
        # Add documents with different sources
        ids = ["ipc_302", "crpc_154", "const_21"]
        texts = [
            "Section 302 IPC: Murder",
            "Section 154 CrPC: FIR",
            "Article 21: Right to life"
        ]
        metadatas = [
            {"source": "IPC"},
            {"source": "CrPC"},
            {"source": "Constitution"}
        ]
        
        test_vector_db.add_documents_batch(ids, texts, metadatas)
        
        # Query only IPC documents
        results = test_vector_db.query(
            "legal section",
            n_results=5,
            where={"source": "IPC"}
        )
        
        assert len(results['ids'][0]) == 1
        assert results['ids'][0][0] == "ipc_302"


class TestCollectionManagement:
    """Test collection management operations."""
    
    def test_count_documents(self, test_vector_db):
        """Test counting documents in collection."""
        assert test_vector_db.count_documents() == 0
        
        test_vector_db.add_document("doc1", "Test document")
        assert test_vector_db.count_documents() == 1
        
        test_vector_db.add_document("doc2", "Another document")
        assert test_vector_db.count_documents() == 2
    
    def test_reset_collection(self, test_vector_db):
        """Test resetting collection."""
        # Add documents
        test_vector_db.add_document("doc1", "Test document")
        test_vector_db.add_document("doc2", "Another document")
        
        assert test_vector_db.count_documents() == 2
        
        # Reset collection
        test_vector_db.reset_collection()
        
        assert test_vector_db.count_documents() == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
