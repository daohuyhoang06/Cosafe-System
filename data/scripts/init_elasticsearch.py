"""
Script to create Elasticsearch index and import sample data
Run: python data/scripts/init_elasticsearch.py
"""

from elasticsearch import Elasticsearch
import os
from pathlib import Path
from dotenv import load_dotenv

# Load env from project root
project_root = Path(__file__).parent.parent.parent
load_dotenv(project_root / ".env")

ES_HOST = os.getenv("ES_HOST", "http://localhost:9200")
ES_INDEX = os.getenv("ES_INDEX", "cs_products_data")


def create_index():
    """Create Elasticsearch index with proper mappings"""
    
    es = Elasticsearch([ES_HOST])
    
    if not es.ping():
        print("❌ Cannot connect to Elasticsearch!")
        print("   Make sure Docker is running: docker-compose up -d")
        return False
    
    print("✅ Connected to Elasticsearch")
    
    # Delete index if exists
    if es.indices.exists(index=ES_INDEX):
        print(f"⚠️  Index '{ES_INDEX}' already exists. Deleting...")
        es.indices.delete(index=ES_INDEX)
    
    # Create index with mappings
    mapping = {
        "mappings": {
            "properties": {
                "name": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "score": {
                    "type": "integer"
                },
                "link_image": {
                    "type": "text"
                },
                "brand": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "category": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "ingredients": {
                    "type": "object",
                    "enabled": True
                }
            }
        },
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0,
            "max_result_window": 10000
        }
    }
    
    es.indices.create(index=ES_INDEX, body=mapping)
    print(f"✅ Index '{ES_INDEX}' created successfully")
    
    # Add sample data
    add_sample_data(es)
    
    return True


def add_sample_data(es):
    """Add sample products for testing"""
    
    sample_products = [
        {
            "name": "Dove Deep Moisture Body Wash",
            "score": 3,
            "link_image": "https://example.com/dove.jpg",
            "brand": "Dove",
            "category": "Body Wash",
            "ingredients": {
                "WATER": {"score": 1},
                "SODIUM LAURETH SULFATE": {"score": 4},
                "GLYCERIN": {"score": 1},
                "COCAMIDOPROPYL BETAINE": {"score": 3}
            }
        },
        {
            "name": "CeraVe Hydrating Facial Cleanser",
            "score": 2,
            "link_image": "https://example.com/cerave.jpg",
            "brand": "CeraVe",
            "category": "Facial Cleanser",
            "ingredients": {
                "WATER": {"score": 1},
                "GLYCERIN": {"score": 1},
                "CERAMIDES": {"score": 1},
                "HYALURONIC ACID": {"score": 1}
            }
        },
        {
            "name": "Neutrogena Hydro Boost Water Gel",
            "score": 4,
            "link_image": "https://example.com/neutrogena.jpg",
            "brand": "Neutrogena",
            "category": "Moisturizer",
            "ingredients": {
                "WATER": {"score": 1},
                "DIMETHICONE": {"score": 3},
                "GLYCERIN": {"score": 1},
                "FRAGRANCE": {"score": 6}
            }
        },
        {
            "name": "Cetaphil Gentle Skin Cleanser",
            "score": 2,
            "link_image": "https://example.com/cetaphil.jpg",
            "brand": "Cetaphil",
            "category": "Facial Cleanser",
            "ingredients": {
                "WATER": {"score": 1},
                "CETYL ALCOHOL": {"score": 2},
                "PROPYLENE GLYCOL": {"score": 3},
                "SODIUM LAURYL SULFATE": {"score": 5}
            }
        },
        {
            "name": "L'Oreal Paris Revitalift Day Cream",
            "score": 5,
            "link_image": "https://example.com/loreal.jpg",
            "brand": "L'Oreal",
            "category": "Anti-Aging Cream",
            "ingredients": {
                "WATER": {"score": 1},
                "GLYCERIN": {"score": 1},
                "RETINOL": {"score": 2},
                "FRAGRANCE": {"score": 6},
                "PARABENS": {"score": 7}
            }
        }
    ]
    
    print(f"📦 Adding {len(sample_products)} sample products...")
    
    for product in sample_products:
        es.index(index=ES_INDEX, document=product)
    
    # Refresh index to make data searchable
    es.indices.refresh(index=ES_INDEX)
    
    # Check count
    count = es.count(index=ES_INDEX)
    print(f"✅ Successfully added {count['count']} products")
    print(f"\n📊 Sample products:")
    for p in sample_products:
        print(f"   - {p['name']} (Score: {p['score']})")


if __name__ == "__main__":
    print("🚀 Initializing Elasticsearch...")
    print(f"   Host: {ES_HOST}")
    print(f"   Index: {ES_INDEX}")
    print()
    
    if create_index():
        print("\n🎉 Initialization completed successfully!")
        print("\nYou can now:")
        print("1. Start backend: python -m uvicorn app.main:app --reload")
        print("2. Start frontend: cd frontend && npm run dev")
        print("3. Open: http://localhost:5173")
    else:
        print("\n❌ Initialization failed!")
        print("   Please check if Elasticsearch is running:")
        print("   docker-compose up -d")
