# Cosafe System - Hệ Thống Kiểm Tra An Toàn Mỹ Phẩm# Cosafe System



## 🎯 Tổng QuanCosafe System là một ứng dụng kiểm tra an toàn sản phẩm (mỹ phẩm) phục vụ mục tiêu tìm kiếm, phân tích thành phần, và cung cấp cảnh báo về các chất có nguy cơ. Hệ thống kết hợp backend FastAPI, frontend React (Vite), và Elasticsearch chạy trong Docker để phục vụ tính năng tìm kiếm nhanh, autocomplete và lọc sản phẩm.



**Cosafe System** là ứng dụng web giúp người dùng kiểm tra an toàn sản phẩm mỹ phẩm dựa trên thành phần hóa học. Hệ thống cung cấp:Tài liệu này mô tả kiến trúc, các thành phần chính, hướng dẫn cài đặt, cách import dữ liệu (bao gồm crawler bằng Scrapy), và cách debug các vấn đề thường gặp.



- ✅ **Tìm kiếm thông minh** với autocomplete---

- ✅ **Phân tích nguyên liệu** tự động (NER)

- ✅ **Nhận diện ảnh** bằng AI (Google Gemini)## Tổng quan kiến trúc

- ✅ **Cơ sở dữ liệu** 8,600+ sản phẩm từ EWG (Environmental Working Group)

- ✅ **Đánh giá an toàn** từ 1-10 cho từng nguyên liệu và sản phẩm- **Backend**: FastAPI (Python)

  - Chịu trách nhiệm cung cấp API REST, xử lý logic tìm kiếm, NER (phân tích tên thực thể), xử lý ảnh, gửi email.

---  - Cấu trúc nằm trong `app/` với các phần chính: `api/routes`, `core`, `services`, `models`.



## 📊 Thông Tin Sản Phẩm- **Search engine**: Elasticsearch (chạy trong Docker)

  - Lưu trữ index `cs_products_data` chứa sản phẩm và trường cần thiết cho tìm kiếm, autocomplete.

Mỗi sản phẩm trong hệ thống bao gồm:

- **Frontend**: React + Vite

### Thông tin cơ bản  - Giao diện tìm kiếm, autocomplete, hiển thị kết quả, trang chi tiết sản phẩm và tính năng tìm kiếm bằng ảnh.

- **Tên sản phẩm**: Tên đầy đủ của mỹ phẩm

- **Safety Score (1-10)**: Điểm an toàn tổng thể- **Crawler**: Scrapy

  - 🟢 **1-2**: Very Safe (Rất an toàn)  - Thu thập dữ liệu sản phẩm (JSON/NDJSON) từ các nguồn công khai, sinh NDJSON để import vào Elasticsearch.

  - 🟡 **3-4**: Safe (An toàn)

  - 🟠 **5-6**: Moderate (Trung bình)---

  - 🔴 **7-10**: High Concern (Cần cân nhắc)

- **Hình ảnh**: Link ảnh sản phẩm## Công nghệ chính

- **Link EWG**: Liên kết đến trang đánh giá chi tiết trên EWG.org

- Python 3.10+ (đã test với 3.12)

### Danh sách nguyên liệu (Ingredients)- FastAPI, Uvicorn

Mỗi nguyên liệu có:- Elasticsearch 8.x (server) + `elasticsearch` Python client 8.x

- **Tên**: Tên hóa học (ví dụ: Water, Glycerin, Retinol)- React 18 + Vite

- **Score (1-10)**: Điểm an toàn riêng của nguyên liệu- Scrapy cho crawling

  - 1: Hoàn toàn an toàn- Docker / docker-compose cho Elasticsearch

  - 3-4: An toàn với hầu hết người

  - 5-6: Cần thận trọng với da nhạy cảm---

  - 7-10: Nguy cơ cao, có thể gây kích ứng/độc hại

- **Link EWG**: Liên kết chi tiết đến trang phân tích nguyên liệu## Yêu cầu trước khi chạy



### Mối lo ngại (Ingredient Concerns)- Docker Desktop (kích hoạt)

Hệ thống hiển thị 4 loại mối lo ngại chính:- Python (cài đặt hệ thống, hoặc dùng `py` launcher trên Windows)

- 🧬 **Cancer** (Ung thư): LOW / MODERATE / HIGH- Node.js (v18+)

- 🤧 **Allergies & Immunotoxicity** (Dị ứng): LOW / MODERATE / HIGH

- 👶 **Developmental & Reproductive Toxicity** (Sinh sản): LOW / MODERATE / HIGH---

- ⚠️ **Use Restrictions** (Hạn chế sử dụng): LOW / MODERATE / HIGH

## Thiết lập nhanh (Windows / PowerShell)

### Ví dụ dữ liệu sản phẩm

```json1. Sao chép cấu hình môi trường:

{

  "name": "CeraVe Hydrating Facial Cleanser",```powershell

  "score": 2,copy .env.example .env

  "link_image": "https://static.ewg.org/...",# Mở .env và điền API keys/credentials nếu cần (Google API, SMTP nếu muốn gửi mail)

  "product_url": "https://www.ewg.org/skindeep/products/...",```

  "ingredient_concerns": {

    "cancer": "LOW",2. Khởi động Elasticsearch (Docker):

    "allergies_immunotoxicity": "LOW",

    "developmental_reproductive_toxicity": "LOW",```powershell

    "use_restrictions": "MODERATE"docker-compose up -d

  },```

  "ingredients": [

    {3. (Chỉ lần đầu) Import dữ liệu vào Elasticsearch:

      "name": "Water",

      "score": 1,```powershell

      "link": "https://www.ewg.org/skindeep/ingredients/706945-WATER/".\import_data.ps1

    },# Hoặc dùng import_data.py nếu bạn thích chạy bằng Python

    {```

      "name": "Glycerin",

      "score": 1,4. Tạo virtualenv và cài dependencies backend (nếu chưa có `venv`):

      "link": "https://www.ewg.org/skindeep/ingredients/702620-GLYCERIN/"

    },```powershell

    {py -m venv venv

      "name": "Ceramides",.\venv\Scripts\Activate.ps1

      "score": 1,pip install -r requirements.txt

      "link": "https://www.ewg.org/skindeep/ingredients/..."```

    }

  ]5. Chạy backend và frontend:

}

``````powershell

# Backend

---py -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000



## 🏗️ Kiến Trúc Hệ Thống# Frontend (mở terminal khác)

cd frontend

### Backend (FastAPI)npm install

- **Framework**: FastAPI + Uvicornnpm run dev

- **Cấu trúc**: Clean Architecture```

  - `app/api/routes/` - API endpoints

  - `app/core/` - Configuration, Elasticsearch clientHoặc dùng `start.bat` để khởi chạy tự động (Windows).

  - `app/services/` - Business logic (Product, NER, Image, Email)

  - `app/models/` - Pydantic schemas**Truy cập:**



### Search Engine (Elasticsearch 8.x)- Frontend: http://localhost:5173

- **Index**: `cs_products_data`- Backend: http://localhost:8000

- **Documents**: 8,600+ sản phẩm- API Docs (Swagger): http://localhost:8000/docs

- **Features**: Full-text search, autocomplete, fuzzy matching- Elasticsearch: http://localhost:9200

- **Deployment**: Docker container

---

### Frontend (React + Vite)

- **Framework**: React 18## Lưu ý về phiên bản Elasticsearch

- **Build Tool**: Vite (siêu nhanh)

- **Pages**: Home, Search Results, Product DetailServer Elasticsearch trong repository đang chạy phiên bản 8.x (ví dụ 8.11.0). Do đó phải sử dụng client Python tương thích (8.x). Trong `requirements.txt` project đã quy định `elasticsearch>=8.0.0,<9.0.0` để tránh lỗi không tương thích.

- **Components**: Autocomplete, Image Search, Header

Nếu bạn dùng server 9.x, cần kiểm tra lại client và API tương ứng.

### Data Collection (Scrapy)

- **Spider**: EWG product crawler---

- **Output**: NDJSON format

- **Location**: `data/data_crawler/`## Import dữ liệu (chi tiết)



---Source data: file NDJSON nằm trong `data/data_elasticsearch/part_*.ndjson`.



## 🛠️ Công Nghệ Sử Dụng**Hai cách import:**



| Layer | Technology | Version |- PowerShell script `import_data.ps1` (Windows) — đã tối ưu để gọi Bulk API và xử lý newline cuối file.

|-------|-----------|---------|- Python script `import_data.py` sử dụng `elasticsearch.helpers.bulk` (cross-platform).

| **Backend** | FastAPI | 0.115+ |

| | Python | 3.10+ |**Quy trình import:**

| | Elasticsearch Client | 8.x |

| | Google Gemini AI | Latest |1. Kiểm tra Elasticsearch reachable

| **Frontend** | React | 18 |2. Tạo index `cs_products_data` (với mapping cho `name`, `name.keyword`, `score`, `ingredients`, `link_image` …)

| | Vite | Latest |3. Bulk import từng file NDJSON (xử lý newline cuối, báo tiến trình)

| | Axios | Latest |

| **Database** | Elasticsearch | 8.11.0 |Ví dụ nhanh (Python):

| **Data Collection** | Scrapy | Latest |

| **DevOps** | Docker Compose | Latest |```python

from elasticsearch import Elasticsearch

---from elasticsearch.helpers import bulk

import json

## 🚀 Cài Đặt & Chạy

es = Elasticsearch(["http://localhost:9200"])

### Yêu cầu hệ thống

- ✅ Docker Desktop (đang chạy)def gen_actions(path):

- ✅ Python 3.10+ (khuyến nghị 3.12)    with open(path, 'r', encoding='utf-8') as f:

- ✅ Node.js 18+        for line in f:

- ✅ PowerShell hoặc Bash            if line.strip():

                yield {"_index": "cs_products_data", "_source": json.loads(line)}

### Bước 1: Clone & Cấu hình

bulk(es, gen_actions('data/data_elasticsearch/part_1.ndjson'))

```powershell```

# Clone repository

git clone https://github.com/yourusername/Cosafe-System.git---

cd Cosafe-System

## Crawler (Scrapy)

# Sao chép file cấu hình

copy .env.example .envFolder `data/data_crawler` chứa project Scrapy (nếu bạn muốn crawl thêm dữ liệu). Ghi chú:



# Chỉnh sửa .env với API keys của bạn:- `spiders/` chứa các spider (ví dụ `products_spider.py`, `ewg_spider.py`).

# GOOGLE_API_KEY=your_google_api_key- `pipelines.py` và `settings.py` đã cấu hình để xuất JSON/NDJSON.

# SMTP_USER=your_email@gmail.com- Quy trình khuyến nghị:

# SMTP_PASS=your_app_password  1. Chạy spider kiểm tra: `scrapy crawl products_spider -o output.jl` (JL = JSON Lines / NDJSON)

```  2. Kiểm tra dữ liệu output, chuẩn hóa các trường (name, ingredients, link_image, score)

  3. Sau khi dữ liệu sạch, sử dụng `import_data.ps1` hoặc `import_data.py` để import vào ES

### Bước 2: Khởi động Elasticsearch

**Tips khi crawl:**

```powershell

docker-compose up -d- Tôn trọng robots.txt và rate limits của website

```- Sử dụng user-agent hợp lý và backoff

- Thực hiện clean/normalize dữ liệu (loại bỏ HTML, chuyển mã ký tự)

Kiểm tra Elasticsearch đã sẵn sàng:- Lưu trữ raw crawl outputs (tạm thời) nhưng không commit vào git — đã thêm `.gitignore` để loại trừ các file data

```powershell

curl http://localhost:9200---

# Hoặc mở trình duyệt: http://localhost:9200

```## Backend (chi tiết kỹ thuật)



### Bước 3: Import dữ liệu sản phẩm- Entry point: `app/main.py` — tạo FastAPI app, load CORS, đăng ký routers

- Core: `app/core/`

**Sử dụng PowerShell (Windows - Khuyến nghị):**  - `config.py`/`__init__.py` — quản lý biến môi trường (`.env`)

```powershell  - `elasticsearch.py` — wrapper client (lazy init, xử lý retry/timeout)

cd data/scripts- API routes: `app/api/routes/*.py` — product, ner, image, email

.\import_data.ps1- Services: `app/services/` — business logic (ProductService, NERService, ImageService, EmailService)

```- Models/Schemas: `app/models/schemas.py` — Pydantic models cho request/response



**Hoặc sử dụng Python (Cross-platform):**Một vài lưu ý đã được áp dụng trong source:

```powershell

cd data/scripts- Tránh khởi tạo các service có phụ thuộc (ES) khi import module — dùng factory / lazy init để tránh crash khi ES chưa sẵn sàng.

python import_data.py- Kiểm soát phiên bản `elasticsearch` client để phù hợp với server 8.x.

```

---

Script sẽ:

1. ✅ Kiểm tra kết nối Elasticsearch## Frontend (chi tiết)

2. ✅ Tạo index `cs_products_data` với mapping

3. ✅ Import 8,600+ sản phẩm từ `data/data_elasticsearch/part_*.ndjson`- Code React nằm trong `frontend/` (Vite): components, pages, services.

4. ✅ Báo cáo tiến trình và kết quả- `frontend/src/services/api.js` dùng Axios để gọi backend tại `http://localhost:8000`.



**Kết quả mong đợi:**Những điểm cần lưu ý khi frontend báo lỗi kết nối (ERR_CONNECTION_REFUSED):

```

[3/3] Import du lieu...- Kiểm tra backend đã chạy tại `http://localhost:8000` hay chưa

      Tim thay 9 files du lieu- Kiểm tra CORS trong backend (`app/main.py`) đã cho phép origin `http://localhost:5173`

      [9/9] Dang import part_9.ndjson...- Kiểm tra URL base trong `frontend/src/services` có trỏ đúng tới backend

              OK - 598 documents

---

===============================================================

  HOAN TAT!## Debug & Troubleshooting

  Tong so documents da import: 8598

  Tong so documents trong index: 8598- Backend không start / crash ngay khi start:

===============================================================  - Nguyên nhân phổ biến: import module khởi tạo service (ES) khi ES chưa ready; thiếu dependency (ví dụ `email-validator` cho Pydantic email).

```  - Fix: kiểm tra log terminal khi chạy `uvicorn`, sửa code để lazy init services, cài packages thiếu.



### Bước 4: Cài đặt Backend- Frontend báo `ERR_CONNECTION_REFUSED`:

  - Kiểm tra backend (port, process): `netstat -ano | findstr :8000` (Windows)

```powershell  - Kiểm tra backend root `/` và `/health` trả về

# Tạo virtual environment

py -m venv venv- Elasticsearch client error (media-type / BadRequest):

.\venv\Scripts\Activate.ps1  - Xảy ra nếu client 9.x dùng với server 8.x hoặc header không phù hợp

  - Fix: dùng `elasticsearch` client 8.x

# Cài đặt dependencies

pip install -r requirements.txt---



# Chạy backend## Công cụ phát triển & scripts

py -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

```- `start.bat` — script Windows để up docker, tạo venv, cài dependencies và chạy backend + frontend

- `import_data.ps1` — PowerShell script để import NDJSON vào Elasticsearch (có xử lý newline cuối và mapping)

### Bước 5: Cài đặt Frontend- `data/data_crawler/` — project Scrapy để thu thập dữ liệu



Mở terminal mới:---



```powershell## Contributing

cd frontend

npm installNếu bạn muốn đóng góp:

npm run dev

```1. Fork repo, tạo branch feature.

2. Viết unit tests nếu thay đổi logic quan trọng.

### Hoặc Chạy Tự Động (Windows)3. Mở PR và mô tả thay đổi/kiểm tra tương thích ES/versions.



```powershell---

.\start.bat

```## License



Script `start.bat` sẽ:Mã nguồn được chia sẻ theo giấy phép MIT (nếu bạn muốn thay đổi license, cập nhật file LICENSE tương ứng).

1. Khởi động Docker Compose

2. Tạo virtual environment---

3. Cài dependencies

4. Chạy backend và frontend## Liên hệ / Ghi chú cuối



---Nếu cần hỗ trợ chạy local hoặc debug kết nối, gửi log terminal của backend (uvicorn) và nội dung `.env` (không gửi secrets), mình sẽ hỗ trợ tiếp.


## 🌐 Truy Cập Ứng Dụng

| Service | URL | Mô tả |
|---------|-----|-------|
| **Website** | http://localhost:5173 | Giao diện người dùng |
| **API Backend** | http://localhost:8000 | REST API |
| **API Docs** | http://localhost:8000/docs | Swagger UI |
| **Elasticsearch** | http://localhost:9200 | Search engine |

---

## 📂 Cấu Trúc Dự Án

```
Cosafe-System/
├── app/                          # Backend (FastAPI)
│   ├── api/routes/               # API endpoints
│   │   ├── product.py            # Tìm kiếm sản phẩm
│   │   ├── ner.py                # Phân tích nguyên liệu
│   │   ├── image.py              # Xử lý ảnh (AI)
│   │   └── email.py              # Gửi email
│   ├── core/                     # Core configuration
│   │   ├── config.py             # Settings
│   │   └── elasticsearch.py      # ES client
│   ├── services/                 # Business logic
│   │   ├── product_service.py    # Tìm kiếm, autocomplete
│   │   ├── ner_service.py        # Phân tích ingredient
│   │   ├── image_service.py      # Google Gemini AI
│   │   └── email_service.py      # SMTP email
│   ├── models/                   # Pydantic schemas
│   └── main.py                   # Entry point
│
├── frontend/                     # Frontend (React + Vite)
│   └── src/
│       ├── components/           # Reusable components
│       │   ├── Autocomplete.jsx
│       │   ├── ImageSearch.jsx
│       │   └── Header.jsx
│       ├── pages/                # Pages
│       │   ├── HomePage.jsx
│       │   ├── SearchResultPage.jsx
│       │   └── ProductDetailPage.jsx
│       └── services/             # API clients
│           ├── productService.js
│           └── api.js
│
├── data/                         # Data & Scripts
│   ├── data_elasticsearch/       # NDJSON product files
│   │   ├── part_1.ndjson
│   │   ├── part_2.ndjson
│   │   └── ... (9 files total)
│   ├── scripts/                  # Import scripts (MỚI!)
│   │   ├── import_data.ps1       # PowerShell import
│   │   ├── import_data.py        # Python import
│   │   └── init_elasticsearch.py # Quick init với sample data
│   └── data_crawler/             # Scrapy project
│       ├── scrapy.cfg
│       └── data_crawler/
│           ├── spiders/
│           │   ├── ewg_spider.py
│           │   └── products_spider.py
│           ├── pipelines.py
│           └── settings.py
│
├── docker-compose.yml            # Elasticsearch container
├── requirements.txt              # Python dependencies
├── start.bat                     # Auto-start script (Windows)
└── README.md                     # This file
```

---

## 🔧 API Endpoints

### Product APIs
```http
POST /api/products/search
# Tìm kiếm sản phẩm với pagination
Body: {"keyword": "serum", "page": 1, "size": 20, "sort": "asc"}

POST /api/products/autocomplete
# Gợi ý autocomplete
Body: {"keyword": "vita", "size": 10}

POST /api/products/get-all
# Lấy chi tiết đầy đủ sản phẩm
Body: {"name": "CeraVe Hydrating Facial Cleanser"}
```

### NER API
```http
POST /api/ner/name-entity-recognition
# Phân tích danh sách nguyên liệu
Body: {"content": "Water, Glycerin, Niacinamide, Retinol"}
```

### Image API
```http
POST /api/image/image-process
# Upload ảnh sản phẩm để nhận diện
Content-Type: multipart/form-data
Body: file=@product_image.jpg
```

### Email API
```http
POST /api/email/send-guide-email
# Gửi hướng dẫn chọn mỹ phẩm an toàn
Body: {"email": "user@example.com"}
```

---

## 🐛 Troubleshooting

### Elasticsearch không kết nối được

**Lỗi:** `Cannot connect to Elasticsearch`

**Giải pháp:**
```powershell
# Kiểm tra Docker container
docker ps

# Khởi động lại Elasticsearch
docker-compose down
docker-compose up -d

# Kiểm tra logs
docker-compose logs elasticsearch
```

### Backend không khởi động

**Lỗi:** `ModuleNotFoundError` hoặc import error

**Giải pháp:**
```powershell
# Kích hoạt virtual environment
.\venv\Scripts\Activate.ps1

# Cài lại dependencies
pip install -r requirements.txt

# Kiểm tra Python version
py --version  # Phải >= 3.10
```

### Frontend không kết nối backend

**Lỗi:** `ERR_CONNECTION_REFUSED`

**Giải pháp:**
```powershell
# Kiểm tra backend đang chạy
netstat -ano | findstr :8000

# Kiểm tra API endpoint
curl http://localhost:8000/health

# Kiểm tra CORS trong app/main.py
# Đảm bảo có: "http://localhost:5173" trong CORS_ORIGINS
```

### Import data thất bại

**Lỗi:** `Khong tim thay file du lieu`

**Giải pháp:**
```powershell
# Chắc chắn bạn đang ở thư mục data/scripts/
cd data/scripts

# Kiểm tra file NDJSON tồn tại
ls ../data_elasticsearch/part_*.ndjson

# Chạy lại script
.\import_data.ps1
```

---

## 🎨 Tính Năng Nổi Bật

### 1. Tìm kiếm thông minh
- **Autocomplete**: Gợi ý sản phẩm khi gõ
- **Fuzzy matching**: Tìm được cả khi gõ sai chính tả
- **Wildcard search**: Hỗ trợ tìm theo một phần tên

### 2. Phân tích nguyên liệu
- Paste danh sách nguyên liệu → Hệ thống tự động tách và phân tích
- Hiển thị điểm an toàn từng nguyên liệu
- Link đến EWG để xem chi tiết

### 3. Tìm kiếm bằng ảnh
- Chụp hoặc upload ảnh sản phẩm
- AI nhận diện tên sản phẩm từ nhãn
- Tự động tìm kiếm thông tin

### 4. Chi tiết sản phẩm đầy đủ
- Điểm an toàn tổng thể với color coding
- Danh sách đầy đủ nguyên liệu và điểm số
- Mối lo ngại (Cancer, Allergies, Reproductive, Restrictions)
- Link đến EWG report đầy đủ

---

## 🔄 Thu Thập Dữ Liệu (Crawler)

### Sử dụng Scrapy spider

```powershell
cd data/data_crawler

# Crawl sản phẩm mới
scrapy crawl ewg_spider -o output.ndjson

# Kiểm tra dữ liệu
head output.ndjson

# Di chuyển vào thư mục data_elasticsearch
move output.ndjson ../data_elasticsearch/part_10.ndjson

# Import vào Elasticsearch
cd ../scripts
.\import_data.ps1
```

### Lưu ý khi crawl
- ⚠️ Tôn trọng `robots.txt`
- ⚠️ Sử dụng rate limiting (DOWNLOAD_DELAY trong settings.py)
- ⚠️ Chuẩn hóa dữ liệu trước khi import
- ⚠️ Không commit dữ liệu lớn vào Git (đã có trong .gitignore)

---

## 📈 Hiệu Năng & Tối Ưu

Hệ thống đã được tối ưu hóa:

- ✅ **Singleton Pattern** cho services → giảm 80-90% memory allocation
- ✅ **Bulk Query** cho NER → giảm 90% query time
- ✅ **LRU Cache** cho product lookup → cache hit ~1ms
- ✅ **Connection Pooling** → 10 connections/node
- ✅ **GZip Compression** → giảm 70-80% network transfer
- ✅ **Field Filtering** → chỉ lấy fields cần thiết

Chi tiết xem: `OPTIMIZATION.md`

---

## 📚 Tài Liệu Thêm

- `OPTIMIZATION.md` - Chi tiết các tối ưu hiệu năng
- `PRODUCT_DETAIL_UPDATE.md` - Cập nhật trang chi tiết sản phẩm
- `CHANGELOG.md` - Lịch sử thay đổi
- `README_JP.md` - README tiếng Nhật

---

## 🤝 Contributing

Đóng góp cho dự án:

1. Fork repository
2. Tạo branch mới: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Mở Pull Request

---

## 📄 License

Dự án được phân phối dưới giấy phép MIT. Xem `LICENSE` để biết thêm chi tiết.

---

## 👥 Liên Hệ

Nếu cần hỗ trợ hoặc có câu hỏi:

- 📧 Email: daohuyhoang06@gmail.com
- 🐛 Issues: [GitHub Issues](https://github.com/daohuyhoang06/Cosafe-System/issues)
- 📖 Docs: [API Documentation](http://localhost:8000/docs)

---

**Developed with ❤️ by Cosafe Team**
