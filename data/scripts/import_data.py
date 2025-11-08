"""
Import all product data from NDJSON files to Elasticsearch
"""

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import json
import os
from pathlib import Path

ES_HOST = "http://localhost:9200"
ES_INDEX = "cs_products_data"

def create_index(es_client, index_name):
    """Create Elasticsearch index with proper mappings"""
    
    if es_client.indices.exists(index=index_name):
        print(f"⚠️  Index '{index_name}' đã tồn tại. Xóa và tạo lại...")
        es_client.indices.delete(index=index_name)
    
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
            "index": {
                "max_result_window": 50000
            }
        }
    }
    
    es_client.indices.create(index=index_name, body=mapping)
    print(f"✅ Index '{index_name}' đã được tạo")


def generate_actions(file_path, index_name):
    """Generate bulk actions from NDJSON file"""
    count = 0
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                try:
                    doc = json.loads(line)
                    count += 1
                    yield {
                        "_index": index_name,
                        "_source": doc
                    }
                except json.JSONDecodeError as e:
                    print(f"   ⚠️  Lỗi parse JSON: {e}")
    print(f"   📄 Đọc được {count} documents từ {os.path.basename(file_path)}")


def import_data():
    """Import all data files to Elasticsearch"""
    
    print("🔗 Kết nối tới Elasticsearch...")
    es = Elasticsearch([ES_HOST])
    
    if not es.ping():
        print("❌ Không thể kết nối tới Elasticsearch!")
        print("   Hãy chắc chắn Docker đã chạy: docker-compose up -d")
        return False
    
    print("✅ Đã kết nối thành công!")
    
    # Create index
    create_index(es, ES_INDEX)
    
    # Find all NDJSON files - updated path from data/scripts/
    script_dir = Path(__file__).parent
    data_dir = script_dir.parent / "data_elasticsearch"
    ndjson_files = sorted(data_dir.glob("part_*.ndjson"))
    
    if not ndjson_files:
        print(f"❌ Không tìm thấy file dữ liệu trong {data_dir}")
        return False
    
    print(f"\n📦 Tìm thấy {len(ndjson_files)} files dữ liệu")
    
    # Import each file
    total_success = 0
    total_failed = 0
    
    for idx, file_path in enumerate(ndjson_files, 1):
        print(f"\n[{idx}/{len(ndjson_files)}] Đang import {file_path.name}...")
        
        try:
            success, failed = bulk(
                es,
                generate_actions(file_path, ES_INDEX),
                chunk_size=500,
                raise_on_error=False,
                max_retries=3,
                request_timeout=60
            )
            
            total_success += success
            if failed:
                total_failed += len(failed)
                print(f"   ⚠️  {len(failed)} documents lỗi")
            
            print(f"   ✅ Import thành công {success} documents")
            
        except Exception as e:
            print(f"   ❌ Lỗi khi import: {str(e)}")
            total_failed += 1
    
    # Refresh index
    print("\n🔄 Đang refresh index...")
    es.indices.refresh(index=ES_INDEX)
    
    # Get final count
    count_result = es.count(index=ES_INDEX)
    total_docs = count_result['count']
    
    print("\n" + "="*50)
    print(f"🎉 HOÀN TẤT!")
    print(f"✅ Tổng số documents thành công: {total_success}")
    if total_failed > 0:
        print(f"⚠️  Tổng số documents lỗi: {total_failed}")
    print(f"📊 Tổng số documents trong index: {total_docs}")
    print("="*50)
    
    return True


if __name__ == "__main__":
    print("="*50)
    print("COSAFE SYSTEM - ELASTICSEARCH DATA IMPORT")
    print("="*50)
    
    if import_data():
        print("\n✨ Dữ liệu đã được import thành công!")
        print("🚀 Bây giờ bạn có thể chạy backend và frontend:")
        print("   Backend: python -m uvicorn app.main:app --reload")
        print("   Frontend: cd frontend && npm run dev")
    else:
        print("\n❌ Import thất bại! Vui lòng kiểm tra lại.")
