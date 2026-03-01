"""
Tests for document ingestion pipeline.

Tests cover:
- Document loading from JSON
- Document preprocessing
- Single document ingestion
- Batch document ingestion
- Metadata handling

Requirements: 10.2
"""

import json
import os
import pytest
import shutil
import tempfile

from document_ingestion import DocumentIngestionPipeline, create_sample_corpus
from vector_db import VectorDatabase


@pytest.fixture
def test_vector_db():
    """Create a test vector database."""
    import uuid
    test_dir = "./test_ingestion_chroma_db"
    collection_name = f"test_ingestion_{uuid.uuid4().hex[:8]}"
    
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
    
    db = VectorDatabase(
        persist_directory=test_dir,
        collection_name=collection_name
    )
    
    yield db
    
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)


@pytest.fixture
def pipeline(test_vector_db):
    """Create a document ingestion pipeline."""
    return DocumentIngestionPipeline(vector_db=test_vector_db)


@pytest.fixture
def sample_documents():
    """Create sample documents for testing."""
    return [
        {
            "id": "test_doc_1",
            "text": "This is a test legal document about Section 302 IPC",
            "source": "IPC",
            "category": "criminal",
            "language": "en",
            "section": "302"
        },
        {
            "id": "test_doc_2",
            "content": "Another test document about CrPC Section 154",
            "source": "CrPC",
            "category": "procedure",
            "language": "en"
        }
    ]


@pytest.fixture
def temp_json_file(sample_documents):
    """Create a temporary JSON file with sample documents."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        json.dump(sample_documents, f)
        temp_path = f.name
    
    yield temp_path
    
    if os.path.exists(temp_path):
        os.unlink(temp_path)


class TestDocumentLoading:
    """Test document loading functionality."""
    
    def test_load_documents_from_json(self, pipeline, temp_json_file):
        """Test loading documents from JSON file."""
        documents = pipeline.load_documents_from_json(temp_json_file)
        
        assert len(documents) == 2
        assert documents[0]['id'] == 'test_doc_1'
        assert documents[1]['id'] == 'test_doc_2'


class TestDocumentPreprocessing:
    """Test document preprocessing."""
    
    def test_preprocess_document_with_text_field(self, pipeline):
        """Test preprocessing document with 'text' field."""
        doc = {
            "id": "test_1",
            "text": "Test content",
            "source": "IPC",
            "category": "criminal"
        }
        
        processed = pipeline.preprocess_document(doc)
        
        assert processed['id'] == 'test_1'
        assert processed['text'] == 'Test content'
        assert processed['metadata']['source'] == 'IPC'
        assert processed['metadata']['category'] == 'criminal'
    
    def test_preprocess_document_with_content_field(self, pipeline):
        """Test preprocessing document with 'content' field instead of 'text'."""
        doc = {
            "id": "test_2",
            "content": "Test content",
            "source": "CrPC"
        }
        
        processed = pipeline.preprocess_document(doc)
        
        assert processed['text'] == 'Test content'
    
    def test_preprocess_document_missing_id_raises_error(self, pipeline):
        """Test that missing ID raises error."""
        doc = {
            "text": "Test content"
        }
        
        with pytest.raises(ValueError, match="must have an 'id' field"):
            pipeline.preprocess_document(doc)
    
    def test_preprocess_document_missing_text_raises_error(self, pipeline):
        """Test that missing text/content raises error."""
        doc = {
            "id": "test_3"
        }
        
        with pytest.raises(ValueError, match="must have a 'text' or 'content' field"):
            pipeline.preprocess_document(doc)
    
    def test_preprocess_adds_default_metadata(self, pipeline):
        """Test that preprocessing adds default metadata."""
        doc = {
            "id": "test_4",
            "text": "Test content"
        }
        
        processed = pipeline.preprocess_document(doc)
        
        assert 'source' in processed['metadata']
        assert 'category' in processed['metadata']
        assert 'language' in processed['metadata']
        assert 'date' in processed['metadata']
    
    def test_preprocess_preserves_custom_metadata(self, pipeline):
        """Test that custom metadata fields are preserved."""
        doc = {
            "id": "test_5",
            "text": "Test content",
            "custom_field": "custom_value",
            "section": "123"
        }
        
        processed = pipeline.preprocess_document(doc)
        
        assert processed['metadata']['custom_field'] == 'custom_value'
        assert processed['metadata']['section'] == '123'


class TestSingleDocumentIngestion:
    """Test single document ingestion."""
    
    def test_ingest_single_document(self, pipeline, test_vector_db):
        """Test ingesting a single document."""
        doc = {
            "id": "single_test",
            "text": "Test document for single ingestion",
            "source": "Test"
        }
        
        pipeline.ingest_document(doc)
        
        assert test_vector_db.count_documents() == 1
        
        # Verify document can be retrieved
        retrieved = test_vector_db.get_document("single_test")
        assert retrieved is not None
        assert "Test document" in retrieved['document']


class TestBatchIngestion:
    """Test batch document ingestion."""
    
    def test_ingest_documents_batch(self, pipeline, test_vector_db, sample_documents):
        """Test ingesting multiple documents in batch."""
        count = pipeline.ingest_documents_batch(sample_documents)
        
        assert count == 2
        assert test_vector_db.count_documents() == 2
    
    def test_ingest_documents_batch_with_custom_batch_size(self, pipeline, test_vector_db):
        """Test batch ingestion with custom batch size."""
        docs = [
            {"id": f"doc_{i}", "text": f"Document {i}"} 
            for i in range(5)
        ]
        
        count = pipeline.ingest_documents_batch(docs, batch_size=2)
        
        assert count == 5
        assert test_vector_db.count_documents() == 5
    
    def test_ingest_documents_batch_handles_errors(self, pipeline, test_vector_db):
        """Test that batch ingestion handles errors gracefully."""
        docs = [
            {"id": "valid_1", "text": "Valid document"},
            {"text": "Missing ID"},  # Invalid - no ID
            {"id": "valid_2", "text": "Another valid document"}
        ]
        
        count = pipeline.ingest_documents_batch(docs)
        
        # Should ingest only valid documents
        assert count == 2
        assert test_vector_db.count_documents() == 2


class TestFileIngestion:
    """Test ingestion from files."""
    
    def test_ingest_from_file(self, pipeline, test_vector_db, temp_json_file):
        """Test ingesting documents from a JSON file."""
        count = pipeline.ingest_from_file(temp_json_file)
        
        assert count == 2
        assert test_vector_db.count_documents() == 2


class TestSpecializedIngestion:
    """Test specialized ingestion methods."""
    
    def test_ingest_ipc_sections(self, pipeline, test_vector_db, temp_json_file):
        """Test ingesting IPC sections."""
        count = pipeline.ingest_ipc_sections(temp_json_file)
        
        assert count == 2
        
        # Verify metadata is set correctly
        doc = test_vector_db.get_document("test_doc_1")
        assert doc['metadata']['source'] == 'IPC'
        assert doc['metadata']['category'] == 'criminal'
    
    def test_ingest_crpc_sections(self, pipeline, test_vector_db, temp_json_file):
        """Test ingesting CrPC sections."""
        count = pipeline.ingest_crpc_sections(temp_json_file)
        
        assert count == 2
        
        # Verify metadata
        doc = test_vector_db.get_document("test_doc_2")
        assert doc['metadata']['source'] == 'CrPC'
        assert doc['metadata']['category'] == 'procedure'
    
    def test_ingest_case_laws(self, pipeline, test_vector_db, temp_json_file):
        """Test ingesting case laws."""
        count = pipeline.ingest_case_laws(temp_json_file)
        
        assert count == 2
        
        # Verify metadata
        doc = test_vector_db.get_document("test_doc_1")
        assert doc['metadata']['source'] == 'Case Law'
        assert doc['metadata']['category'] == 'judgment'


class TestIngestionStats:
    """Test ingestion statistics."""
    
    def test_get_ingestion_stats(self, pipeline, test_vector_db, sample_documents):
        """Test getting ingestion statistics."""
        pipeline.ingest_documents_batch(sample_documents)
        
        stats = pipeline.get_ingestion_stats()
        
        assert 'total_documents' in stats
        assert stats['total_documents'] == 2
        assert 'timestamp' in stats


class TestSampleCorpusCreation:
    """Test sample corpus creation."""
    
    def test_create_sample_corpus(self):
        """Test creating sample corpus file."""
        temp_dir = tempfile.mkdtemp()
        output_path = os.path.join(temp_dir, "test_corpus.json")
        
        try:
            create_sample_corpus(output_path)
            
            assert os.path.exists(output_path)
            
            # Load and verify
            with open(output_path, 'r', encoding='utf-8') as f:
                documents = json.load(f)
            
            assert len(documents) > 0
            assert all('id' in doc for doc in documents)
            assert all('text' in doc for doc in documents)
        finally:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
