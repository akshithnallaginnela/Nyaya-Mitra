"""
Tests for document ingestion pipeline.

Tests cover:
- JSON file ingestion
- IPC section ingestion
- CrPC section ingestion
- Case law ingestion
- Constitution article ingestion
- Batch processing

Requirements: 10.2
"""

import json
import os
import pytest
import shutil

from document_ingestion import DocumentIngestionPipeline
from vector_db import VectorDatabase


@pytest.fixture
def test_pipeline():
    """Create a test ingestion pipeline with isolated vector database."""
    import uuid
    test_dir = "./test_ingestion_db"
    collection_name = f"test_ingestion_{uuid.uuid4().hex[:8]}"
    
    # Clean up before creating
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
    
    # Create test vector database
    vector_db = VectorDatabase(
        persist_directory=test_dir,
        collection_name=collection_name
    )
    
    # Create pipeline
    pipeline = DocumentIngestionPipeline(vector_db=vector_db)
    
    yield pipeline
    
    # Clean up after
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
    
    # Clean up test data
    if os.path.exists("./test_legal_data"):
        shutil.rmtree("./test_legal_data")


class TestJSONIngestion:
    """Test JSON file ingestion."""
    
    def test_ingest_from_json_file(self, test_pipeline):
        """Test ingesting documents from JSON file."""
        # Create test JSON file
        os.makedirs("./test_legal_data", exist_ok=True)
        test_file = "./test_legal_data/test_docs.json"
        
        test_data = [
            {
                "id": "test_1",
                "text": "Test document 1",
                "metadata": {"source": "Test", "category": "test"}
            },
            {
                "id": "test_2",
                "text": "Test document 2",
                "metadata": {"source": "Test", "category": "test"}
            }
        ]
        
        with open(test_file, 'w') as f:
            json.dump(test_data, f)
        
        # Ingest
        count = test_pipeline.ingest_from_json(test_file)
        
        assert count == 2
        assert test_pipeline.vector_db.count_documents() == 2
    
    def test_ingest_empty_json_returns_zero(self, test_pipeline):
        """Test that ingesting empty JSON returns 0."""
        os.makedirs("./test_legal_data", exist_ok=True)
        test_file = "./test_legal_data/empty.json"
        
        with open(test_file, 'w') as f:
            json.dump([], f)
        
        count = test_pipeline.ingest_from_json(test_file)
        
        assert count == 0
        assert test_pipeline.vector_db.count_documents() == 0


class TestIPCIngestion:
    """Test IPC section ingestion."""
    
    def test_ingest_ipc_sections(self, test_pipeline):
        """Test ingesting IPC sections."""
        sections = [
            {
                "section_number": "302",
                "title": "Punishment for murder",
                "description": "Whoever commits murder shall be punished with death or imprisonment for life.",
                "category": "criminal",
                "language": "en"
            },
            {
                "section_number": "304",
                "title": "Culpable homicide not amounting to murder",
                "description": "Whoever commits culpable homicide not amounting to murder shall be punished.",
                "category": "criminal",
                "language": "en"
            }
        ]
        
        count = test_pipeline.ingest_ipc_sections(sections)
        
        assert count == 2
        assert test_pipeline.vector_db.count_documents() == 2
        
        # Verify document structure
        doc = test_pipeline.vector_db.get_document("ipc_302")
        assert doc is not None
        assert "302" in doc['document']
        assert doc['metadata']['source'] == 'IPC'
        assert doc['metadata']['section'] == '302'
    
    def test_ipc_document_id_format(self, test_pipeline):
        """Test that IPC documents have correct ID format."""
        sections = [
            {
                "section_number": "123",
                "title": "Test Section",
                "description": "Test description"
            }
        ]
        
        test_pipeline.ingest_ipc_sections(sections)
        
        doc = test_pipeline.vector_db.get_document("ipc_123")
        assert doc is not None


class TestCrPCIngestion:
    """Test CrPC section ingestion."""
    
    def test_ingest_crpc_sections(self, test_pipeline):
        """Test ingesting CrPC sections."""
        sections = [
            {
                "section_number": "154",
                "title": "Information in cognizable cases",
                "description": "Every information relating to the commission of a cognizable offence shall be reduced to writing.",
                "category": "procedure",
                "language": "en"
            }
        ]
        
        count = test_pipeline.ingest_crpc_sections(sections)
        
        assert count == 1
        assert test_pipeline.vector_db.count_documents() == 1
        
        # Verify document structure
        doc = test_pipeline.vector_db.get_document("crpc_154")
        assert doc is not None
        assert "154" in doc['document']
        assert doc['metadata']['source'] == 'CrPC'


class TestCaseLawIngestion:
    """Test case law ingestion."""
    
    def test_ingest_case_laws(self, test_pipeline):
        """Test ingesting case laws."""
        cases = [
            {
                "case_id": "2023_SC_001",
                "case_name": "State v. Accused",
                "summary": "This case deals with the interpretation of Section 302 IPC.",
                "court": "Supreme Court",
                "year": "2023",
                "category": "precedent",
                "language": "en"
            }
        ]
        
        count = test_pipeline.ingest_case_laws(cases)
        
        assert count == 1
        assert test_pipeline.vector_db.count_documents() == 1
        
        # Verify document structure
        doc = test_pipeline.vector_db.get_document("case_2023_SC_001")
        assert doc is not None
        assert "State v. Accused" in doc['document']
        assert doc['metadata']['source'] == 'CaseLaw'
        assert doc['metadata']['court'] == 'Supreme Court'


class TestConstitutionIngestion:
    """Test Constitution article ingestion."""
    
    def test_ingest_constitution_articles(self, test_pipeline):
        """Test ingesting Constitution articles."""
        articles = [
            {
                "article_number": "21",
                "title": "Protection of life and personal liberty",
                "description": "No person shall be deprived of his life or personal liberty except according to procedure established by law.",
                "category": "fundamental_rights",
                "language": "en"
            }
        ]
        
        count = test_pipeline.ingest_constitution_articles(articles)
        
        assert count == 1
        assert test_pipeline.vector_db.count_documents() == 1
        
        # Verify document structure
        doc = test_pipeline.vector_db.get_document("const_21")
        assert doc is not None
        assert "Article 21" in doc['document']
        assert doc['metadata']['source'] == 'Constitution'


class TestBatchIngestion:
    """Test batch document ingestion."""
    
    def test_ingest_multiple_document_types(self, test_pipeline):
        """Test ingesting multiple types of documents."""
        # Ingest IPC
        ipc_sections = [
            {
                "section_number": "302",
                "title": "Murder",
                "description": "Punishment for murder"
            }
        ]
        test_pipeline.ingest_ipc_sections(ipc_sections)
        
        # Ingest CrPC
        crpc_sections = [
            {
                "section_number": "154",
                "title": "FIR",
                "description": "Information in cognizable cases"
            }
        ]
        test_pipeline.ingest_crpc_sections(crpc_sections)
        
        # Ingest Constitution
        articles = [
            {
                "article_number": "21",
                "title": "Right to life",
                "description": "Protection of life and personal liberty"
            }
        ]
        test_pipeline.ingest_constitution_articles(articles)
        
        # Verify all documents are ingested
        assert test_pipeline.vector_db.count_documents() == 3
    
    def test_ingest_documents_adds_timestamp(self, test_pipeline):
        """Test that ingestion adds timestamp to metadata."""
        documents = [
            {
                "id": "test_1",
                "text": "Test document",
                "metadata": {"source": "Test"}
            }
        ]
        
        test_pipeline.ingest_documents(documents)
        
        doc = test_pipeline.vector_db.get_document("test_1")
        assert 'ingested_at' in doc['metadata']


class TestSampleCorpus:
    """Test sample corpus creation and ingestion."""
    
    def test_create_sample_corpus(self, test_pipeline):
        """Test creating sample legal corpus."""
        file_path = test_pipeline.create_sample_legal_corpus()
        
        assert os.path.exists(file_path)
        
        # Verify file content
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        assert len(data) > 0
        assert all('id' in doc and 'text' in doc for doc in data)
    
    def test_ingest_sample_corpus(self, test_pipeline):
        """Test ingesting sample corpus."""
        file_path = test_pipeline.create_sample_legal_corpus()
        count = test_pipeline.ingest_from_json(file_path)
        
        assert count > 0
        assert test_pipeline.vector_db.count_documents() == count


class TestMetadataHandling:
    """Test metadata handling during ingestion."""
    
    def test_metadata_preserved(self, test_pipeline):
        """Test that metadata is preserved during ingestion."""
        documents = [
            {
                "id": "test_1",
                "text": "Test document",
                "metadata": {
                    "source": "Test",
                    "category": "test_category",
                    "custom_field": "custom_value"
                }
            }
        ]
        
        test_pipeline.ingest_documents(documents)
        
        doc = test_pipeline.vector_db.get_document("test_1")
        assert doc['metadata']['source'] == 'Test'
        assert doc['metadata']['category'] == 'test_category'
        assert doc['metadata']['custom_field'] == 'custom_value'
    
    def test_missing_metadata_handled(self, test_pipeline):
        """Test that documents without metadata are handled."""
        documents = [
            {
                "id": "test_1",
                "text": "Test document"
            }
        ]
        
        count = test_pipeline.ingest_documents(documents)
        
        assert count == 1
        doc = test_pipeline.vector_db.get_document("test_1")
        assert doc is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
