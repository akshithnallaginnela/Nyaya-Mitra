import boto3
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import os
from typing import List, Dict, Optional, Any

class OpenSearchVectorDB:
    def __init__(
        self,
        endpoint: str,
        index_name: str = "legal_documents",
        region: str = "ap-south-1"
    ):
        self.index_name = index_name
        
        # Determine authentication method
        # If in AWS (ECS), use IAM credentials from the task role
        if os.environ.get("AWS_CONTAINER_CREDENTIALS_RELATIVE_URI"):
            service = 'es'
            credentials = boto3.Session().get_credentials()
            awsauth = AWS4Auth(
                credentials.access_key, 
                credentials.secret_key, 
                region, 
                service, 
                session_token=credentials.token
            )
            
            self.client = OpenSearch(
                hosts=[{'host': endpoint.replace("https://", ""), 'port': 443}],
                http_auth=awsauth,
                use_ssl=True,
                verify_certs=True,
                connection_class=RequestsHttpConnection
            )
        else:
            # Fallback for local testing if needed
            self.client = OpenSearch(
                hosts=[{'host': endpoint.replace("https://", ""), 'port': 443}],
                use_ssl=True,
                verify_certs=False
            )

    def add_documents(self, documents: List[str], metadatas: List[Dict], ids: List[str]):
        """
        Add documents to OpenSearch index.
        Note: For simplicity, we assume embeddings are generated outside or by OpenSearch.
        In a real RAG, we would store the vector too.
        """
        for doc, meta, doc_id in zip(documents, metadatas, ids):
            body = {
                "text": doc,
                "metadata": meta
            }
            # Add vector if provided (this is a simplified placeholder)
            if "vector" in meta:
                body["vector"] = meta.pop("vector")
                
            self.client.index(
                index=self.index_name,
                id=doc_id,
                body=body,
                refresh=True
            )

    def query(self, query_text: str, n_results: int = 5, where: Optional[Dict] = None) -> Dict:
        """
        Query the OpenSearch index.
        """
        # This is a simplified keyword search. 
        # For actual vector search, we need a k-NN query.
        query = {
            "size": n_results,
            "query": {
                "match": {
                    "text": query_text
                }
            }
        }
        
        if where:
            # Add filtering logic here
            pass
            
        res = self.client.search(index=self.index_name, body=query)
        
        # Format to match ChromaDB style response for compatibility
        formatted = {
            "ids": [[]],
            "documents": [[]],
            "metadatas": [[]],
            "distances": [[]]
        }
        
        hits = res.get("hits", {}).get("hits", [])
        for hit in hits:
            formatted["ids"][0].append(hit["_id"])
            formatted["documents"][0].append(hit["_source"]["text"])
            formatted["metadatas"][0].append(hit["_source"]["metadata"])
            formatted["distances"][0].append(1.0 - hit["_score"]/10.0) # Dummy distance
            
        return formatted
