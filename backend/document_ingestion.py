"""
Document ingestion pipeline for loading legal documents into vector database.

This module handles:
- Loading legal documents from various sources (IPC, CrPC, case laws)
- Generating embeddings for documents
- Storing documents in Chroma with metadata
- Batch processing for efficient ingestion

Requirements: 10.2 (Document ingestion)
"""

import json
import os
from typing import Dict, List, Optional
from datetime import datetime

from vector_db import get_vector_db, VectorDatabase


class DocumentIngestionPipeline:
    """
    Pipeline for ingesting legal documents into the vector database.
    
    Handles document loading, preprocessing, and storage with metadata.
    """
    
    def __init__(self, vector_db: Optional[VectorDatabase] = None):
        """
        Initialize the ingestion pipeline.
        
        Args:
            vector_db: Vector database instance (uses global instance if None)
        """
        self.vector_db = vector_db or get_vector_db()
    
    def load_documents_from_json(self, file_path: str) -> List[Dict]:
        """
        Load documents from a JSON file.
        
        Args:
            file_path: Path to JSON file
            
        Returns:
            List[Dict]: List of document dictionaries
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            documents = json.load(f)
        
        return documents
    
    def preprocess_document(self, document: Dict) -> Dict:
        """
        Preprocess a document before ingestion.
        
        Args:
            document: Raw document dictionary
            
        Returns:
            Dict: Preprocessed document with standardized fields
        """
        # Ensure required fields exist
        if 'id' not in document:
            raise ValueError("Document must have an 'id' field")
        
        if 'text' not in document and 'content' not in document:
            raise ValueError("Document must have a 'text' or 'content' field")
        
        # Standardize text field
        text = document.get('text') or document.get('content', '')
        
        # Create metadata - handle nested metadata dict from corpus files
        doc_metadata = document.get('metadata', {}) if isinstance(document.get('metadata'), dict) else {}
        
        metadata = {
            'source': doc_metadata.get('source', document.get('source', 'unknown')),
            'category': doc_metadata.get('category', document.get('category', 'general')),
            'language': doc_metadata.get('language', document.get('language', 'en')),
            'date': doc_metadata.get('date', document.get('date', datetime.utcnow().isoformat())),
            'title': doc_metadata.get('title', document.get('title', '')),
            'section': doc_metadata.get('section', document.get('section', '')),
        }
        
        # Add any additional metadata fields (only scalar values)
        for key, value in document.items():
            if key not in ['id', 'text', 'content', 'metadata'] and key not in metadata:
                if isinstance(value, (str, int, float, bool)):
                    metadata[key] = value
        
        return {
            'id': document['id'],
            'text': text,
            'metadata': metadata
        }
    
    def ingest_document(self, document: Dict) -> None:
        """
        Ingest a single document into the vector database.
        
        Args:
            document: Document dictionary with id, text, and optional metadata
        """
        # Preprocess document
        processed = self.preprocess_document(document)
        
        # Add to vector database
        self.vector_db.add_document(
            document_id=processed['id'],
            text=processed['text'],
            metadata=processed['metadata']
        )
    
    def ingest_documents_batch(self, documents: List[Dict], batch_size: int = 100) -> int:
        """
        Ingest multiple documents in batches.
        
        Args:
            documents: List of document dictionaries
            batch_size: Number of documents to process in each batch
            
        Returns:
            int: Number of documents successfully ingested
        """
        total_ingested = 0
        
        # Process in batches
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            
            # Preprocess batch
            processed_batch = []
            for doc in batch:
                try:
                    processed = self.preprocess_document(doc)
                    processed_batch.append(processed)
                except Exception as e:
                    print(f"Error preprocessing document {doc.get('id', 'unknown')}: {e}")
                    continue
            
            if not processed_batch:
                continue
            
            # Extract data for batch insertion
            ids = [doc['id'] for doc in processed_batch]
            texts = [doc['text'] for doc in processed_batch]
            metadatas = [doc['metadata'] for doc in processed_batch]
            
            # Add batch to vector database
            try:
                self.vector_db.add_documents_batch(ids, texts, metadatas)
                total_ingested += len(processed_batch)
                print(f"Ingested batch {i // batch_size + 1}: {len(processed_batch)} documents")
            except Exception as e:
                print(f"Error ingesting batch {i // batch_size + 1}: {e}")
        
        return total_ingested
    
    def ingest_from_file(self, file_path: str, batch_size: int = 100) -> int:
        """
        Load and ingest documents from a JSON file.
        
        Args:
            file_path: Path to JSON file containing documents
            batch_size: Number of documents to process in each batch
            
        Returns:
            int: Number of documents successfully ingested
        """
        print(f"Loading documents from {file_path}...")
        documents = self.load_documents_from_json(file_path)
        print(f"Loaded {len(documents)} documents")
        
        print("Starting ingestion...")
        total_ingested = self.ingest_documents_batch(documents, batch_size)
        print(f"Ingestion complete: {total_ingested} documents ingested")
        
        return total_ingested
    
    def ingest_ipc_sections(self, file_path: str) -> int:
        """
        Ingest IPC (Indian Penal Code) sections.
        
        Args:
            file_path: Path to JSON file containing IPC sections
            
        Returns:
            int: Number of sections ingested
        """
        documents = self.load_documents_from_json(file_path)
        
        # Ensure proper metadata for IPC sections
        for doc in documents:
            doc['source'] = 'IPC'
            doc['category'] = 'criminal'
            if 'language' not in doc:
                doc['language'] = 'en'
        
        return self.ingest_documents_batch(documents)
    
    def ingest_crpc_sections(self, file_path: str) -> int:
        """
        Ingest CrPC (Criminal Procedure Code) sections.
        
        Args:
            file_path: Path to JSON file containing CrPC sections
            
        Returns:
            int: Number of sections ingested
        """
        documents = self.load_documents_from_json(file_path)
        
        # Ensure proper metadata for CrPC sections
        for doc in documents:
            doc['source'] = 'CrPC'
            doc['category'] = 'procedure'
            if 'language' not in doc:
                doc['language'] = 'en'
        
        return self.ingest_documents_batch(documents)
    
    def ingest_case_laws(self, file_path: str) -> int:
        """
        Ingest case laws and judgments.
        
        Args:
            file_path: Path to JSON file containing case laws
            
        Returns:
            int: Number of case laws ingested
        """
        documents = self.load_documents_from_json(file_path)
        
        # Ensure proper metadata for case laws
        for doc in documents:
            doc['source'] = 'Case Law'
            doc['category'] = 'judgment'
            if 'language' not in doc:
                doc['language'] = 'en'
        
        return self.ingest_documents_batch(documents)
    
    def get_ingestion_stats(self) -> Dict:
        """
        Get statistics about ingested documents.
        
        Returns:
            Dict: Statistics including total count and breakdown by source
        """
        total_count = self.vector_db.count_documents()
        
        return {
            'total_documents': total_count,
            'timestamp': datetime.utcnow().isoformat()
        }


def create_sample_corpus(output_path: str = "backend/data/sample_legal_documents.json") -> None:
    """
    Create a sample corpus of legal documents for testing.
    
    Args:
        output_path: Path where the sample corpus will be saved
    """
    sample_documents = [
        {
            "id": "ipc_302",
            "text": "Section 302: Punishment for murder - Whoever commits murder shall be punished with death, or imprisonment for life, and shall also be liable to fine.",
            "source": "IPC",
            "category": "criminal",
            "language": "en",
            "section": "302",
            "title": "Punishment for murder"
        },
        {
            "id": "ipc_304",
            "text": "Section 304: Punishment for culpable homicide not amounting to murder - Whoever commits culpable homicide not amounting to murder shall be punished with imprisonment for life, or imprisonment of either description for a term which may extend to ten years, and shall also be liable to fine.",
            "source": "IPC",
            "category": "criminal",
            "language": "en",
            "section": "304",
            "title": "Culpable homicide not amounting to murder"
        },
        {
            "id": "ipc_307",
            "text": "Section 307: Attempt to murder - Whoever does any act with such intention or knowledge, and under such circumstances that, if he by that act caused death, he would be guilty of murder, shall be punished with imprisonment of either description for a term which may extend to ten years, and shall also be liable to fine.",
            "source": "IPC",
            "category": "criminal",
            "language": "en",
            "section": "307",
            "title": "Attempt to murder"
        },
        {
            "id": "ipc_375",
            "text": "Section 375: Rape - A man is said to commit rape if he has sexual intercourse with a woman under circumstances falling under any of the six following descriptions.",
            "source": "IPC",
            "category": "criminal",
            "language": "en",
            "section": "375",
            "title": "Rape"
        },
        {
            "id": "ipc_420",
            "text": "Section 420: Cheating and dishonestly inducing delivery of property - Whoever cheats and thereby dishonestly induces the person deceived to deliver any property to any person, or to make, alter or destroy the whole or any part of a valuable security, shall be punished with imprisonment of either description for a term which may extend to seven years, and shall also be liable to fine.",
            "source": "IPC",
            "category": "criminal",
            "language": "en",
            "section": "420",
            "title": "Cheating"
        },
        {
            "id": "crpc_154",
            "text": "Section 154: Information in cognizable cases - Every information relating to the commission of a cognizable offence, if given orally to an officer in charge of a police station, shall be reduced to writing by him or under his direction, and be read over to the informant; and every such information, whether given in writing or reduced to writing as aforesaid, shall be signed by the person giving it, and the substance thereof shall be entered in a book to be kept by such officer in such form as the State Government may prescribe in this behalf. This is commonly known as FIR (First Information Report).",
            "source": "CrPC",
            "category": "procedure",
            "language": "en",
            "section": "154",
            "title": "FIR - First Information Report"
        },
        {
            "id": "crpc_161",
            "text": "Section 161: Examination of witnesses by police - Any police officer making an investigation may examine orally any person supposed to be acquainted with the facts and circumstances of the case.",
            "source": "CrPC",
            "category": "procedure",
            "language": "en",
            "section": "161",
            "title": "Examination of witnesses"
        },
        {
            "id": "crpc_41",
            "text": "Section 41: When police may arrest without warrant - Any police officer may without an order from a Magistrate and without a warrant, arrest any person who has been concerned in any cognizable offence, or against whom a reasonable complaint has been made, or credible information has been received.",
            "source": "CrPC",
            "category": "procedure",
            "language": "en",
            "section": "41",
            "title": "Arrest without warrant"
        },
        {
            "id": "const_21",
            "text": "Article 21: Protection of life and personal liberty - No person shall be deprived of his life or personal liberty except according to procedure established by law.",
            "source": "Constitution",
            "category": "fundamental_rights",
            "language": "en",
            "section": "21",
            "title": "Right to life and personal liberty"
        },
        {
            "id": "const_14",
            "text": "Article 14: Equality before law - The State shall not deny to any person equality before the law or the equal protection of the laws within the territory of India.",
            "source": "Constitution",
            "category": "fundamental_rights",
            "language": "en",
            "section": "14",
            "title": "Equality before law"
        }
    ]
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Write to file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(sample_documents, f, indent=2, ensure_ascii=False)
    
    print(f"Sample corpus created at {output_path}")


if __name__ == "__main__":
    # Create sample corpus
    create_sample_corpus()
    
    # Initialize pipeline
    pipeline = DocumentIngestionPipeline()
    
    # Ingest sample documents
    total = pipeline.ingest_from_file("backend/data/sample_legal_documents.json")
    
    # Print stats
    stats = pipeline.get_ingestion_stats()
    print(f"\nIngestion Statistics:")
    print(f"Total documents: {stats['total_documents']}")
    print(f"Timestamp: {stats['timestamp']}")
