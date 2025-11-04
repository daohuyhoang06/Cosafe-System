# Cosafe System - Hệ thống kiểm tra an toàn mỹ phẩm

## Cài đặt nhanh

### 1. Chuẩn bị
- Docker Desktop (phải bật)
- Python 3.9+
- Node.js 18+

### 2. Setup môi trường
```bash
# Copy file .env.example thành .env
copy .env.example .env

# Sửa .env - điền API keys của bạn:
GOOGLE_API_KEY=your_key_here
SMTP_USER=your_email@gmail.com
SMTP_PASS=your_password
```

### 3. Import dữ liệu vào Elasticsearch
```powershell
# Chạy Docker Elasticsearch
docker-compose up -d

# Import dữ liệu (CHỈ LẦN ĐẦU)
.\import_data.ps1

# Kết quả: ~8,600 products được import
```

### 4. Chạy dự án
```bash
# Cách 1: Tự động (khuyến nghị)
.\start.bat

# Cách 2: Thủ công
docker-compose up -d
py -m venv venv
venv\Scripts\activate
py -m pip install -r requirements.txt
py -m uvicorn app.main:app --reload

# Terminal mới
cd frontend
npm install
npm run dev
```

### 5. Truy cập
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Elasticsearch: http://localhost:9200

## Import dữ liệu lại (nếu cần)

Nếu cần import lại dữ liệu hoặc thêm dữ liệu mới:

```powershell
.\import_data.ps1
```

Script sẽ:
- Xóa index cũ
- Tạo index mới với mapping
- Import tất cả files từ `data/data_elasticsearch/part_*.ndjson`
- Hiển thị tiến trình và tổng số documents

## Cấu trúc dự án

```
app/              # Backend FastAPI
  api/routes/     # API endpoints
  core/           # Config & Elasticsearch
  services/       # Business logic
  models/         # Data schemas

frontend/         # React + Vite
  src/
    components/   # UI components
    pages/        # Pages
    services/     # API calls

data/             # Web crawler
docker-compose.yml # Elasticsearch config
```

## Import dữ liệu

```python
# Tạo file import_data.py
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import json

es = Elasticsearch(["http://localhost:9200"])

# Tạo index
es.indices.create(
    index="cs_products_data",
    body={
        "mappings": {
            "properties": {
                "name": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
                "score": {"type": "integer"},
                "link_image": {"type": "text"},
                "ingredients": {"type": "object"}
            }
        }
    }
)

# Import từ file NDJSON
def generate_actions(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                doc = json.loads(line)
                yield {"_index": "cs_products_data", "_source": doc}

bulk(es, generate_actions("your_data.ndjson"))
```

Hoặc sử dụng script PowerShell có sẵn:
```powershell
.\import_data.ps1
```

## Troubleshooting

**Docker không chạy?**
- Bật Docker Desktop
- Check port: `netstat -an | findstr 9200`

**Backend lỗi?**
- Kiểm tra .env có đúng không
- Python version: `python --version` (>= 3.9)
- Elasticsearch đã chạy chưa: http://localhost:9200

**Frontend lỗi?**
- Xóa node_modules: `rm -r node_modules`
- Cài lại: `npm install`

## Tắt dự án
```bash
docker-compose down
# Ctrl+C ở terminal backend và frontend
```
