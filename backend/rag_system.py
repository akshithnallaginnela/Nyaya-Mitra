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
from dataclasses import dataclass

from vector_db import get_vector_db, VectorDatabase


@dataclass
class RetrievedDocument:
    """
    Represents a retrieved document with metadata and relevance score.
    """
    id: str
    text: str
    metadata: Dict
    relevance_score: float  # 0.0 to 1.0, higher is more relevant
    
    def __repr__(self) -> str:
        return f"<RetrievedDocument(id={self.id}, relevance={self.relevance_score:.3f})>"


@dataclass
class RetrievalResult:
    """
    Represents the result of a RAG retrieval operation.
    """
    query: str
    documents: List[RetrievedDocument]
    total_retrieved: int
    avg_relevance: float
    
    def __repr__(self) -> str:
        return f"<RetrievalResult(query='{self.query[:50]}...', docs={self.total_retrieved}, avg_relevance={self.avg_relevance:.3f})>"


class RAGRetrievalSystem:
    """
    RAG retrieval system for semantic search over legal documents.
    
    Provides:
    - Query embedding generation
    - Similarity-based document retrieval
    - Metadata filtering
    - Relevance scoring
    """
    
    def __init__(
        self,
        vector_db: Optional[VectorDatabase] = None,
        default_n_results: int = 5
    ):
        """
        Initialize RAG retrieval system.
        
        Args:
            vector_db: Vector database instance (uses global if None)
            default_n_results: Default number of documents to retrieve
        """
        self.vector_db = vector_db or get_vector_db()
        self.default_n_results = default_n_results
    
    def _calculate_relevance_score(self, distance: float) -> float:
        """
        Convert distance to relevance score (0.0 to 1.0).
        
        ChromaDB returns L2 (Euclidean) distances. Lower distance = higher relevance.
        We convert to a 0-1 score where 1.0 is most relevant.
        
        Args:
            distance: L2 distance from query
            
        Returns:
            float: Relevance score between 0.0 and 1.0
        """
        # Convert L2 distance to similarity score
        # Using exponential decay: score = e^(-distance)
        import math
        relevance = math.exp(-distance)
        return min(1.0, max(0.0, relevance))
    
    def retrieve(
        self,
        query: str,
        n_results: Optional[int] = None,
        language: Optional[str] = None,
        category: Optional[str] = None,
        source: Optional[str] = None,
        min_relevance: float = 0.0
    ) -> RetrievalResult:
        """
        Retrieve relevant documents for a query.
        
        Args:
            query: Search query text
            n_results: Number of results to retrieve (uses default if None)
            language: Filter by language (e.g., 'en', 'hi')
            category: Filter by category (e.g., 'criminal', 'procedure')
            source: Filter by source (e.g., 'IPC', 'CrPC')
            min_relevance: Minimum relevance score threshold (0.0 to 1.0)
            
        Returns:
            RetrievalResult: Retrieved documents with metadata
        """
        if not query or not query.strip():
            return RetrievalResult(
                query=query,
                documents=[],
                total_retrieved=0,
                avg_relevance=0.0
            )
        
        n_results = n_results or self.default_n_results
        
        # Build metadata filter
        where_filter = {}
        if language:
            where_filter['language'] = language
        if category:
            where_filter['category'] = category
        if source:
            where_filter['source'] = source
        
        # Query vector database
        results = self.vector_db.query(
            query_text=query,
            n_results=n_results,
            where=where_filter if where_filter else None
        )
        
        # Process results
        documents = []
        if results['ids'] and results['ids'][0]:
            for i in range(len(results['ids'][0])):
                doc_id = results['ids'][0][i]
                doc_text = results['documents'][0][i]
                doc_metadata = results['metadatas'][0][i] if results['metadatas'] else {}
                distance = results['distances'][0][i] if results['distances'] else 1.0
                
                # Calculate relevance score
                relevance = self._calculate_relevance_score(distance)
                
                # Apply minimum relevance filter
                if relevance >= min_relevance:
                    documents.append(RetrievedDocument(
                        id=doc_id,
                        text=doc_text,
                        metadata=doc_metadata,
                        relevance_score=relevance
                    ))
        
        # Calculate average relevance
        avg_relevance = (
            sum(doc.relevance_score for doc in documents) / len(documents)
            if documents else 0.0
        )
        
        return RetrievalResult(
            query=query,
            documents=documents,
            total_retrieved=len(documents),
            avg_relevance=avg_relevance
        )
    
    def retrieve_by_language(
        self,
        query: str,
        language: str,
        n_results: Optional[int] = None
    ) -> RetrievalResult:
        """
        Retrieve documents filtered by language.
        
        Args:
            query: Search query
            language: Language code (e.g., 'en', 'hi')
            n_results: Number of results
            
        Returns:
            RetrievalResult: Retrieved documents
        """
        return self.retrieve(
            query=query,
            n_results=n_results,
            language=language
        )
    
    def retrieve_by_category(
        self,
        query: str,
        category: str,
        n_results: Optional[int] = None
    ) -> RetrievalResult:
        """
        Retrieve documents filtered by category.
        
        Args:
            query: Search query
            category: Document category (e.g., 'criminal', 'procedure')
            n_results: Number of results
            
        Returns:
            RetrievalResult: Retrieved documents
        """
        return self.retrieve(
            query=query,
            n_results=n_results,
            category=category
        )
    
    def retrieve_by_source(
        self,
        query: str,
        source: str,
        n_results: Optional[int] = None
    ) -> RetrievalResult:
        """
        Retrieve documents filtered by source.
        
        Args:
            query: Search query
            source: Document source (e.g., 'IPC', 'CrPC', 'Constitution')
            n_results: Number of results
            
        Returns:
            RetrievalResult: Retrieved documents
        """
        return self.retrieve(
            query=query,
            n_results=n_results,
            source=source
        )
    
    def retrieve_with_context(
        self,
        query: str,
        n_results: Optional[int] = None,
        **filters
    ) -> Tuple[str, RetrievalResult]:
        """
        Retrieve documents and format as context for LLM.
        
        Args:
            query: Search query
            n_results: Number of results
            **filters: Additional filters (language, category, source)
            
        Returns:
            Tuple[str, RetrievalResult]: (formatted_context, retrieval_result)
        """
        result = self.retrieve(query=query, n_results=n_results, **filters)
        
        # Format context
        context_parts = []
        for i, doc in enumerate(result.documents, 1):
            source = doc.metadata.get('source', 'Unknown')
            section = doc.metadata.get('section', '')
            title = doc.metadata.get('title', '')
            
            header = f"[Document {i}]"
            if source and section:
                header += f" {source} Section {section}"
            if title:
                header += f": {title}"
            
            context_parts.append(f"{header}\n{doc.text}\n")
        
        context = "\n".join(context_parts) if context_parts else "No relevant documents found."
        
        return context, result
    
    def get_retrieval_stats(self, result: RetrievalResult) -> Dict:
        """
        Get statistics about a retrieval result.
        
        Args:
            result: RetrievalResult to analyze
            
        Returns:
            Dict: Statistics including counts, scores, and metadata breakdown
        """
        if not result.documents:
            return {
                'total_documents': 0,
                'avg_relevance': 0.0,
                'min_relevance': 0.0,
                'max_relevance': 0.0,
                'sources': {},
                'categories': {},
                'languages': {}
            }
        
        # Calculate statistics
        relevance_scores = [doc.relevance_score for doc in result.documents]
        
        # Count by metadata
        sources = {}
        categories = {}
        languages = {}
        
        for doc in result.documents:
            source = doc.metadata.get('source', 'unknown')
            category = doc.metadata.get('category', 'unknown')
            language = doc.metadata.get('language', 'unknown')
            
            sources[source] = sources.get(source, 0) + 1
            categories[category] = categories.get(category, 0) + 1
            languages[language] = languages.get(language, 0) + 1
        
        return {
            'total_documents': result.total_retrieved,
            'avg_relevance': result.avg_relevance,
            'min_relevance': min(relevance_scores),
            'max_relevance': max(relevance_scores),
            'sources': sources,
            'categories': categories,
            'languages': languages
        }


# Global RAG system instance
_rag_system: Optional[RAGRetrievalSystem] = None


def get_rag_system() -> RAGRetrievalSystem:
    """
    Get or create the global RAG system instance.
    
    Returns:
        RAGRetrievalSystem: RAG system instance
    """
    global _rag_system
    
    if _rag_system is None:
        _rag_system = RAGRetrievalSystem()
    
    return _rag_system


def init_rag_system(n_results: int = 5) -> RAGRetrievalSystem:
    """
    Initialize the RAG system.
    
    Args:
        n_results: Default number of results to retrieve
        
    Returns:
        RAGRetrievalSystem: Initialized RAG system
    """
    global _rag_system
    _rag_system = RAGRetrievalSystem(default_n_results=n_results)
    return _rag_system
