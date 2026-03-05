"""
Vector database configuration and management using Chroma.

This module sets up ChromaDB for storing and retrieving legal documents
using semantic search with embeddings.

Requirements: 10.1 (Vector database for RAG)
"""

import os
from typing import Dict, List, Optional, Any

import chromadb
from sentence_transformers import SentenceTransformer


class VectorDatabase:
    """
    Vector database manager using ChromaDB.
    
    Handles:
    - ChromaDB client initialization with persistent storage
    - Collection management for legal documents
    - Embedding generation using sentence-transformers
    - Document storage and retrieval
    """
    
    def __init__(
        self,
        persist_directory: str = "./chroma_db",
        collection_name: str = "legal_documents",
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    ):
        """
        Initialize vector database.
        
        Args:
            persist_directory: Directory for persistent storage
            collection_name: Name of the collection for legal documents
            embedding_model: Name of the sentence-transformers model
        """
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        
        # Create persist directory if it doesn't exist
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize ChromaDB client with persistent storage
        self.client = chromadb.PersistentClient(
            path=persist_directory
        )
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer(embedding_model)
        
        # Get or create collection
        self.collection = self._get_or_create_collection()
    
    def _get_or_create_collection(self):
        """
        Get existing collection or create new one.
        
        Returns:
            Collection: ChromaDB collection
        """
        try:
            # Try to get existing collection
            collection = self.client.get_collection(name=self.collection_name)
        except Exception:
            # Create new collection if it doesn't exist
            collection = self.client.create_collection(
                name=self.collection_name,
                metadata={
                    "description": "Legal documents for RAG system",
                    "embedding_model": "sentence-transformers/all-MiniLM-L6-v2"
                }
            )
        
        return collection
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for text using sentence-transformers.
        
        Args:
            text: Text to embed
            
        Returns:
            List[float]: Embedding vector
        """
        embedding = self.embedding_model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    
    def add_document(
        self,
        document_id: str,
        text: str,
        metadata: Optional[Dict] = None
    ) -> None:
        """
        Add a document to the collection.
        
        Args:
            document_id: Unique identifier for the document
            text: Document text content
            metadata: Optional metadata (source, category, language, date, etc.)
        """
        # Generate embedding
        embedding = self.generate_embedding(text)
        
        # Add to collection
        self.collection.add(
            ids=[document_id],
            embeddings=[embedding],
            documents=[text],
            metadatas=[metadata] if metadata else None
        )
    
    def add_documents_batch(
        self,
        document_ids: List[str],
        texts: List[str],
        metadatas: Optional[List[Dict]] = None
    ) -> None:
        """
        Add multiple documents to the collection in batch.
        
        Args:
            document_ids: List of unique identifiers
            texts: List of document text contents
            metadatas: Optional list of metadata dictionaries
        """
        # Generate embeddings for all texts
        embeddings = [self.generate_embedding(text) for text in texts]
        
        # Add to collection
        self.collection.add(
            ids=document_ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas
        )
    
    def query(
        self,
        query_text: str,
        n_results: int = 5,
        where: Optional[Dict] = None
    ) -> Dict:
        """
        Query the collection for similar documents.
        
        Args:
            query_text: Query text
            n_results: Number of results to return (default: 5)
            where: Optional metadata filter
            
        Returns:
            Dict: Query results with ids, documents, metadatas, and distances
        """
        # Generate query embedding
        query_embedding = self.generate_embedding(query_text)
        
        # Query collection
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where
        )
        
        return results
    
    def get_document(self, document_id: str) -> Optional[Dict]:
        """
        Get a specific document by ID.
        
        Args:
            document_id: Document identifier
            
        Returns:
            Optional[Dict]: Document data or None if not found
        """
        try:
            result = self.collection.get(ids=[document_id])
            if result['ids']:
                return {
                    'id': result['ids'][0],
                    'document': result['documents'][0],
                    'metadata': result['metadatas'][0] if result['metadatas'] else None
                }
        except Exception:
            pass
        
        return None
    
    def delete_document(self, document_id: str) -> None:
        """
        Delete a document from the collection.
        
        Args:
            document_id: Document identifier
        """
        self.collection.delete(ids=[document_id])
    
    def count_documents(self) -> int:
        """
        Get the total number of documents in the collection.
        
        Returns:
            int: Number of documents
        """
        return self.collection.count()
    
    def reset_collection(self) -> None:
        """
        Delete all documents from the collection.
        
        WARNING: This will delete all data!
        """
        self.client.delete_collection(name=self.collection_name)
        self.collection = self._get_or_create_collection()


# Global vector database instance
_vector_db: Optional[Any] = None


def get_vector_db() -> Any:
    """
    Get or create the global vector database instance.
    
    Returns:
        VectorDatabase or OpenSearchVectorDB: Vector database instance
    """
    global _vector_db
    
    if _vector_db is None:
        db_type = os.getenv("VECTOR_DB_TYPE", "chroma").lower()
        
        if db_type == "opensearch":
            from vector_db_opensearch import OpenSearchVectorDB
            _vector_db = OpenSearchVectorDB(
                endpoint=os.getenv("OPENSEARCH_URL", ""),
                region=os.getenv("AWS_REGION", "ap-south-1")
            )
        else:
            _vector_db = VectorDatabase()
    
    return _vector_db


def init_vector_db() -> Any:
    """
    Initialize the vector database.
    
    Returns:
        VectorDatabase: Initialized vector database instance
    """
    global _vector_db
    _vector_db = None
    return get_vector_db()
