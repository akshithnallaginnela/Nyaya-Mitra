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
    Pipeline for ingesting legal documents into vector database.
    
    Handles document loading, preprocessing, embedding generation,
    and storage with metadata.
    """
    
    def __init__(self, vector_db: Optional[VectorDatabase] = None):
        """
        Initialize document ingestion pipeline.
        
        Args:
            vector_db: Vector database instance (uses global if not provided)
        """
        self.vector_db = vector_db or get_vector_db()
    
    def ingest_from_json(self, file_path: str) -> int:
        """
        Ingest documents from a JSON file.
        
        Expected JSON format:
        [
            {
                "id": "ipc_302",
                "text": "Section 302: Punishment for murder...",
                "metadata": {
                    "source": "IPC",
                    "category": "criminal",
                    "section": "302",
                    "language": "en"
                }
            },
            ...
        ]
        
        Args:
            file_path: Path to JSON file
            
        Returns:
            int: Number of documents ingested
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            documents = json.load(f)
        
        return self.ingest_documents(documents)
    
    def ingest_documents(self, documents: List[Dict]) -> int:
        """
        Ingest a list of documents.
        
        Args:
            documents: List of document dictionaries with id, text, and metadata
            
        Returns:
            int: Number of documents ingested
        """
        if not documents:
            return 0
        
        # Extract components
        ids = []
        texts = []
        metadatas = []
        
        for doc in documents:
            # Validate document structure
            if 'id' not in doc or 'text' not in doc:
                continue
            
            ids.append(doc['id'])
            texts.append(doc['text'])
            
            # Add metadata with ingestion timestamp
            metadata = doc.get('metadata', {})
            metadata['ingested_at'] = datetime.utcnow().isoformat()
            metadatas.append(metadata)
        
        # Batch ingest
        if ids:
            self.vector_db.add_documents_batch(ids, texts, metadatas)
        
        return len(ids)
    
    def ingest_ipc_sections(self, sections: List[Dict]) -> int:
        """
        Ingest IPC (Indian Penal Code) sections.
        
        Args:
            sections: List of IPC section dictionaries
            
        Returns:
            int: Number of sections ingested
        """
        documents = []
        
        for section in sections:
            doc = {
                'id': f"ipc_{section['section_number']}",
                'text': f"Section {section['section_number']} IPC: {section['title']}. {section['description']}",
                'metadata': {
                    'source': 'IPC',
                    'category': section.get('category', 'criminal'),
                    'section': section['section_number'],
                    'language': section.get('language', 'en'),
                    'title': section['title']
                }
            }
            documents.append(doc)
        
        return self.ingest_documents(documents)
    
    def ingest_crpc_sections(self, sections: List[Dict]) -> int:
        """
        Ingest CrPC (Code of Criminal Procedure) sections.
        
        Args:
            sections: List of CrPC section dictionaries
            
        Returns:
            int: Number of sections ingested
        """
        documents = []
        
        for section in sections:
            doc = {
                'id': f"crpc_{section['section_number']}",
                'text': f"Section {section['section_number']} CrPC: {section['title']}. {section['description']}",
                'metadata': {
                    'source': 'CrPC',
                    'category': section.get('category', 'procedure'),
                    'section': section['section_number'],
                    'language': section.get('language', 'en'),
                    'title': section['title']
                }
            }
            documents.append(doc)
        
        return self.ingest_documents(documents)
    
    def ingest_case_laws(self, cases: List[Dict]) -> int:
        """
        Ingest case law documents.
        
        Args:
            cases: List of case law dictionaries
            
        Returns:
            int: Number of cases ingested
        """
        documents = []
        
        for case in cases:
            doc = {
                'id': f"case_{case['case_id']}",
                'text': f"{case['case_name']}. {case['summary']}",
                'metadata': {
                    'source': 'CaseLaw',
                    'category': case.get('category', 'precedent'),
                    'case_id': case['case_id'],
                    'case_name': case['case_name'],
                    'court': case.get('court', 'Unknown'),
                    'year': case.get('year', 'Unknown'),
                    'language': case.get('language', 'en')
                }
            }
            documents.append(doc)
        
        return self.ingest_documents(documents)
    
    def ingest_constitution_articles(self, articles: List[Dict]) -> int:
        """
        Ingest Constitution of India articles.
        
        Args:
            articles: List of constitution article dictionaries
            
        Returns:
            int: Number of articles ingested
        """
        documents = []
        
        for article in articles:
            doc = {
                'id': f"const_{article['article_number']}",
                'text': f"Article {article['article_number']}: {article['title']}. {article['description']}",
                'metadata': {
                    'source': 'Constitution',
                    'category': article.get('category', 'fundamental_rights'),
                    'article': article['article_number'],
                    'language': article.get('language', 'en'),
                    'title': article['title']
                }
            }
            documents.append(doc)
        
        return self.ingest_documents(documents)
    
    def create_sample_legal_corpus(self) -> str:
        """
        Create a sample legal corpus JSON file for testing.
        
        Returns:
            str: Path to created sample file
        """
        sample_documents = [
            {
                "id": "ipc_302",
                "text": "Section 302 IPC: Punishment for murder. Whoever commits murder shall be punished with death or imprisonment for life, and shall also be liable to fine.",
                "metadata": {
                    "source": "IPC",
                    "category": "criminal",
                    "section": "302",
                    "language": "en",
                    "title": "Punishment for murder"
                }
            },
            {
                "id": "ipc_304",
                "text": "Section 304 IPC: Punishment for culpable homicide not amounting to murder. Whoever commits culpable homicide not amounting to murder shall be punished with imprisonment for life, or imprisonment for a term which may extend to ten years, and shall also be liable to fine.",
                "metadata": {
                    "source": "IPC",
                    "category": "criminal",
                    "section": "304",
                    "language": "en",
                    "title": "Culpable homicide not amounting to murder"
                }
            },
            {
                "id": "ipc_307",
                "text": "Section 307 IPC: Attempt to murder. Whoever does any act with such intention or knowledge, and under such circumstances that, if he by that act caused death, he would be guilty of murder, shall be punished with imprisonment of either description for a term which may extend to ten years, and shall also be liable to fine.",
                "metadata": {
                    "source": "IPC",
                    "category": "criminal",
                    "section": "307",
                    "language": "en",
                    "title": "Attempt to murder"
                }
            },
            {
                "id": "crpc_154",
                "text": "Section 154 CrPC: Information in cognizable cases. Every information relating to the commission of a cognizable offence, if given orally to an officer in charge of a police station, shall be reduced to writing by him or under his direction, and be read over to the informant; and every such information, whether given in writing or reduced to writing as aforesaid, shall be signed by the person giving it.",
                "metadata": {
                    "source": "CrPC",
                    "category": "procedure",
                    "section": "154",
                    "language": "en",
                    "title": "Information in cognizable cases (FIR)"
                }
            },
            {
                "id": "crpc_156",
                "text": "Section 156 CrPC: Police officer's power to investigate cognizable case. Any officer in charge of a police station may, without the order of a Magistrate, investigate any cognizable case which a Court having jurisdiction over the local area within the limits of such station would have power to inquire into or try under the provisions of Chapter XIII.",
                "metadata": {
                    "source": "CrPC",
                    "category": "procedure",
                    "section": "156",
                    "language": "en",
                    "title": "Police officer's power to investigate"
                }
            },
            {
                "id": "const_21",
                "text": "Article 21: Protection of life and personal liberty. No person shall be deprived of his life or personal liberty except according to procedure established by law.",
                "metadata": {
                    "source": "Constitution",
                    "category": "fundamental_rights",
                    "article": "21",
                    "language": "en",
                    "title": "Right to life and personal liberty"
                }
            },
            {
                "id": "const_14",
                "text": "Article 14: Equality before law. The State shall not deny to any person equality before the law or the equal protection of the laws within the territory of India.",
                "metadata": {
                    "source": "Constitution",
                    "category": "fundamental_rights",
                    "article": "14",
                    "language": "en",
                    "title": "Equality before law"
                }
            },
            {
                "id": "const_19",
                "text": "Article 19: Protection of certain rights regarding freedom of speech, etc. All citizens shall have the right to freedom of speech and expression, to assemble peaceably and without arms, to form associations or unions, to move freely throughout the territory of India, to reside and settle in any part of the territory of India, and to practice any profession, or to carry on any occupation, trade or business.",
                "metadata": {
                    "source": "Constitution",
                    "category": "fundamental_rights",
                    "article": "19",
                    "language": "en",
                    "title": "Freedom of speech and expression"
                }
            }
        ]
        
        # Create sample data directory
        os.makedirs("./legal_data", exist_ok=True)
        file_path = "./legal_data/sample_corpus.json"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(sample_documents, f, indent=2, ensure_ascii=False)
        
        return file_path


def ingest_sample_corpus():
    """
    Convenience function to ingest sample legal corpus.
    
    Returns:
        int: Number of documents ingested
    """
    pipeline = DocumentIngestionPipeline()
    
    # Create sample corpus
    file_path = pipeline.create_sample_legal_corpus()
    
    # Ingest documents
    count = pipeline.ingest_from_json(file_path)
    
    print(f"Ingested {count} documents from sample corpus")
    return count


if __name__ == "__main__":
    # Run sample ingestion
    ingest_sample_corpus()
