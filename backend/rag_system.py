"""
RAG (Retrieval-Augmented Generation) system for legal document retrieval.

This module implements:
- Query embedding generation
- Similarity search to retrieve top documents
- Metadata filtering by language and category
- Relevance score calculation

Requirements: 10.1, 1.3 (RAG retrieval)
"""

from typing import Dict, List, Optional, Tuple

from vector_db import get_vector_db, VectorDatabase


class RAGRetriever:
    """
    Retrieval-Augmented Generation retriever for legal documents.
    
    Handles semantic search over legal documents using embeddings
    and returns relevant context for query answering.
    """
    
    def __init__(
        self,
        vector_db: Optional[VectorDatabase] = None,
        default_n_results: int = 5
    ):
        """
        Initialize RAG retriever.
        
        Args:
            vector_db: Vector database instance (uses global if not provided)
            default_n_results: Default number of results to retrieve
        """
        self.vector_db = vector_db or get_vector_db()
        self.default_n_results = default_n_results
    
    def retrieve(
        self,
        query: str,
        n_results: Optional[int] = None,
        language: Optional[str] = None,
        category: Optional[str] = None,
        source: Optional[str] = None
    ) -> List[Dict]:
        """
        Retrieve relevant documents for a query.
        
        Args:
            query: User query text
            n_results: Number of results to retrieve (default: 5)
            language: Filter by language (e.g., 'en', 'hi')
            category: Filter by category (e.g., 'criminal', 'procedure')
       