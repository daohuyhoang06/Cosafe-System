from elasticsearch import Elasticsearch
import os
from dotenv import load_dotenv

load_dotenv()

class ElasticsearchClient:
    _instance = None
    _client = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ElasticsearchClient, cls).__new__(cls)
        return cls._instance
    
    def _initialize(self):
        """Initialize Elasticsearch connection for local Docker (lazy load)"""
        if self._client is not None:
            return self._client
            
        ES_HOST = os.getenv("ES_HOST", "http://localhost:9200")
        
        # Elasticsearch 9.x simplified initialization
        self._client = Elasticsearch(
            ES_HOST,
            verify_certs=False,
            request_timeout=30,
            headers={"accept": "application/json", "content-type": "application/json"}
        )
        
        # Test connection
        try:
            info = self._client.info()
            print(f"✓ Connected to Elasticsearch {info['version']['number']}")
        except Exception as e:
            print(f"WARNING: Elasticsearch connection error: {e}")
        
        return self._client
    
    def get_client(self):
        if self._client is None:
            self._initialize()
        return self._client

# Global Elasticsearch instance
def get_es_client():
    return ElasticsearchClient().get_client()
