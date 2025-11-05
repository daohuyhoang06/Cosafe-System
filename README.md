# Cosafe System

Cosafe System là một ứng dụng kiểm tra an toàn sản phẩm (mỹ phẩm) phục vụ mục tiêu tìm kiếm, phân tích thành phần, và cung cấp cảnh báo về các chất có nguy cơ. Hệ thống kết hợp backend FastAPI, frontend React (Vite), và Elasticsearch chạy trong Docker để phục vụ tính năng tìm kiếm nhanh, autocomplete và lọc sản phẩm.

Tài liệu này mô tả kiến trúc, các thành phần chính, hướng dẫn cài đặt, cách import dữ liệu (bao gồm crawler bằng Scrapy), và cách debug các vấn đề thường gặp.

---

## Tổng quan kiến trúc

- **Backend**: FastAPI (Python)
  - Chịu trách nhiệm cung cấp API REST, xử lý logic tìm kiếm, NER (phân tích tên thực thể), xử lý ảnh, gửi email.
  - Cấu trúc nằm trong `app/` với các phần chính: `api/routes`, `core`, `services`, `models`.

- **Search engine**: Elasticsearch (chạy trong Docker)
  - Lưu trữ index `cs_products_data` chứa sản phẩm và trường cần thiết cho tìm kiếm, autocomplete.

- **Frontend**: React + Vite
  - Giao diện tìm kiếm, autocomplete, hiển thị kết quả, trang chi tiết sản phẩm và tính năng tìm kiếm bằng ảnh.

- **Crawler**: Scrapy
  - Thu thập dữ liệu sản phẩm (JSON/NDJSON) từ các nguồn công khai, sinh NDJSON để import vào Elasticsearch.

---

## Công nghệ chính

- Python 3.10+ (đã test với 3.12)
- FastAPI, Uvicorn
- Elasticsearch 8.x (server) + `elasticsearch` Python client 8.x
- React 18 + Vite
- Scrapy cho crawling
- Docker / docker-compose cho Elasticsearch

---

## Yêu cầu trước khi chạy

- Docker Desktop (kích hoạt)
- Python (cài đặt hệ thống, hoặc dùng `py` launcher trên Windows)
- Node.js (v18+)

---

## Thiết lập nhanh (Windows / PowerShell)

1. Sao chép cấu hình môi trường:

```powershell
copy .env.example .env
# Mở .env và điền API keys/credentials nếu cần (Google API, SMTP nếu muốn gửi mail)
```

2. Khởi động Elasticsearch (Docker):

```powershell
docker-compose up -d
```

3. (Chỉ lần đầu) Import dữ liệu vào Elasticsearch:

```powershell
.\import_data.ps1
# Hoặc dùng import_data.py nếu bạn thích chạy bằng Python
```

4. Tạo virtualenv và cài dependencies backend (nếu chưa có `venv`):

```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

5. Chạy backend và frontend:

```powershell
# Backend
py -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend (mở terminal khác)
cd frontend
npm install
npm run dev
```

Hoặc dùng `start.bat` để khởi chạy tự động (Windows).

**Truy cập:**

- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- API Docs (Swagger): http://localhost:8000/docs
- Elasticsearch: http://localhost:9200

---

## Lưu ý về phiên bản Elasticsearch

Server Elasticsearch trong repository đang chạy phiên bản 8.x (ví dụ 8.11.0). Do đó phải sử dụng client Python tương thích (8.x). Trong `requirements.txt` project đã quy định `elasticsearch>=8.0.0,<9.0.0` để tránh lỗi không tương thích.

Nếu bạn dùng server 9.x, cần kiểm tra lại client và API tương ứng.

---

## Import dữ liệu (chi tiết)

Source data: file NDJSON nằm trong `data/data_elasticsearch/part_*.ndjson`.

**Hai cách import:**

- PowerShell script `import_data.ps1` (Windows) — đã tối ưu để gọi Bulk API và xử lý newline cuối file.
- Python script `import_data.py` sử dụng `elasticsearch.helpers.bulk` (cross-platform).

**Quy trình import:**

1. Kiểm tra Elasticsearch reachable
2. Tạo index `cs_products_data` (với mapping cho `name`, `name.keyword`, `score`, `ingredients`, `link_image` …)
3. Bulk import từng file NDJSON (xử lý newline cuối, báo tiến trình)

Ví dụ nhanh (Python):

```python
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import json

es = Elasticsearch(["http://localhost:9200"])

def gen_actions(path):
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                yield {"_index": "cs_products_data", "_source": json.loads(line)}

bulk(es, gen_actions('data/data_elasticsearch/part_1.ndjson'))
```

---

## Crawler (Scrapy)

Folder `data/data_crawler` chứa project Scrapy (nếu bạn muốn crawl thêm dữ liệu). Ghi chú:

- `spiders/` chứa các spider (ví dụ `products_spider.py`, `ewg_spider.py`).
- `pipelines.py` và `settings.py` đã cấu hình để xuất JSON/NDJSON.
- Quy trình khuyến nghị:
  1. Chạy spider kiểm tra: `scrapy crawl products_spider -o output.jl` (JL = JSON Lines / NDJSON)
  2. Kiểm tra dữ liệu output, chuẩn hóa các trường (name, ingredients, link_image, score)
  3. Sau khi dữ liệu sạch, sử dụng `import_data.ps1` hoặc `import_data.py` để import vào ES

**Tips khi crawl:**

- Tôn trọng robots.txt và rate limits của website
- Sử dụng user-agent hợp lý và backoff
- Thực hiện clean/normalize dữ liệu (loại bỏ HTML, chuyển mã ký tự)
- Lưu trữ raw crawl outputs (tạm thời) nhưng không commit vào git — đã thêm `.gitignore` để loại trừ các file data

---

## Backend (chi tiết kỹ thuật)

- Entry point: `app/main.py` — tạo FastAPI app, load CORS, đăng ký routers
- Core: `app/core/`
  - `config.py`/`__init__.py` — quản lý biến môi trường (`.env`)
  - `elasticsearch.py` — wrapper client (lazy init, xử lý retry/timeout)
- API routes: `app/api/routes/*.py` — product, ner, image, email
- Services: `app/services/` — business logic (ProductService, NERService, ImageService, EmailService)
- Models/Schemas: `app/models/schemas.py` — Pydantic models cho request/response

Một vài lưu ý đã được áp dụng trong source:

- Tránh khởi tạo các service có phụ thuộc (ES) khi import module — dùng factory / lazy init để tránh crash khi ES chưa sẵn sàng.
- Kiểm soát phiên bản `elasticsearch` client để phù hợp với server 8.x.

---

## Frontend (chi tiết)

- Code React nằm trong `frontend/` (Vite): components, pages, services.
- `frontend/src/services/api.js` dùng Axios để gọi backend tại `http://localhost:8000`.

Những điểm cần lưu ý khi frontend báo lỗi kết nối (ERR_CONNECTION_REFUSED):

- Kiểm tra backend đã chạy tại `http://localhost:8000` hay chưa
- Kiểm tra CORS trong backend (`app/main.py`) đã cho phép origin `http://localhost:5173`
- Kiểm tra URL base trong `frontend/src/services` có trỏ đúng tới backend

---

## Debug & Troubleshooting

- Backend không start / crash ngay khi start:
  - Nguyên nhân phổ biến: import module khởi tạo service (ES) khi ES chưa ready; thiếu dependency (ví dụ `email-validator` cho Pydantic email).
  - Fix: kiểm tra log terminal khi chạy `uvicorn`, sửa code để lazy init services, cài packages thiếu.

- Frontend báo `ERR_CONNECTION_REFUSED`:
  - Kiểm tra backend (port, process): `netstat -ano | findstr :8000` (Windows)
  - Kiểm tra backend root `/` và `/health` trả về

- Elasticsearch client error (media-type / BadRequest):
  - Xảy ra nếu client 9.x dùng với server 8.x hoặc header không phù hợp
  - Fix: dùng `elasticsearch` client 8.x

---

## Công cụ phát triển & scripts

- `start.bat` — script Windows để up docker, tạo venv, cài dependencies và chạy backend + frontend
- `import_data.ps1` — PowerShell script để import NDJSON vào Elasticsearch (có xử lý newline cuối và mapping)
- `data/data_crawler/` — project Scrapy để thu thập dữ liệu

---

## Contributing

Nếu bạn muốn đóng góp:

1. Fork repo, tạo branch feature.
2. Viết unit tests nếu thay đổi logic quan trọng.
3. Mở PR và mô tả thay đổi/kiểm tra tương thích ES/versions.

---

## License

Mã nguồn được chia sẻ theo giấy phép MIT (nếu bạn muốn thay đổi license, cập nhật file LICENSE tương ứng).

---

## Liên hệ / Ghi chú cuối

Nếu cần hỗ trợ chạy local hoặc debug kết nối, gửi log terminal của backend (uvicorn) và nội dung `.env` (không gửi secrets), mình sẽ hỗ trợ tiếp.
