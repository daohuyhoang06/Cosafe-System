from fastapi import FastAPI, HTTPException, File, UploadFile
from elasticsearch import Elasticsearch
from pydantic import BaseModel
import re
import os
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
import json
from dotenv import load_dotenv
from pydantic import EmailStr
from fastapi import BackgroundTasks
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
# Load environment variables
load_dotenv()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict this for safety
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Elasticsearch config
ES_CLOUD_URL = os.getenv("ES_CLOUD_URL")
ES_API_KEY = os.getenv("ES_API_KEY")
if not ES_CLOUD_URL or not ES_API_KEY:
    raise ValueError("Missing ES_CLOUD_URL or ES_API_KEY. Please set in .env or environment.")

# Gemini API config
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("Missing GOOGLE_API_KEY. Please set in .env or environment.")
genai.configure(api_key=GEMINI_API_KEY)

es = Elasticsearch(
    [ES_CLOUD_URL],
    api_key=ES_API_KEY,
    headers={"Content-Type": "application/json"}
)

if not es.ping():
    raise ValueError("Cannot connect to Elasticsearch!")

# Request models
class SafetyRequest(BaseModel):
    name: str

class NERRequest(BaseModel):
    content: str

class SearchRequest(BaseModel):
    keyword: str
    page: int = 1
    size: int = 20
    sort: str = "default"  # "default", "asc", "desc"

class GuideEmailRequest(BaseModel):
    email: EmailStr

@app.post("/safety")
async def safety_check(request: SafetyRequest):
    try:
        result = es.search(
            index="cs_products_data",
            query={
                "term": {
                    "name.keyword": request.name
                }
            },
            size=1
        )
        if not result["hits"]["hits"]:
            return {"message": "Không tìm thấy sản phẩm"}
        hit = result["hits"]["hits"][0]["_source"]
        return {"name": hit["name"], "score": hit["score"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@app.post("/name-entity-recognition")
async def ner_and_score(request: NERRequest):
    try:
        ingredients = re.split(r',|\s+và\s+|\s+hoặc\s+', request.content)
        if not ingredients:
            return {"ingredients": [], "message": "Không tìm thấy thành phần trong văn bản"}
        ingredient_list = []
        for ingredient in ingredients:
            result = es.search(
                index="cs_products_data",
                query={
                    "bool": {
                        "filter": [
                            {"exists": {"field": f"ingredients.{ingredient.upper()}"}}
                        ]
                    }
                },
                size=1
            )
            hits = result.get("hits", {}).get("hits", [])
            if hits:
                hit = hits[0]
                if "_source" in hit and "ingredients" in hit["_source"]:
                    ingredients_data = hit["_source"]["ingredients"]
                    if ingredient in ingredients_data and "score" in ingredients_data[ingredient]:
                        ingredient_list.append({
                            "name": ingredient,
                            "score": ingredients_data[ingredient]["score"]
                        })
        if not ingredient_list:
            return {"ingredients": [], "message": "Không tìm thấy thành phần"}
        return {"ingredients": ingredient_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@app.post("/get-all")
async def get_all(request: SafetyRequest):
    try:
        result = es.search(
            index="cs_products_data",
            query={
                "term": {
                    "name.keyword": request.name
                }
            },
            size=1
        )
        if not result["hits"]["hits"]:
            return {"message": "Không tìm thấy sản phẩm"}
        hit = result["hits"]["hits"][0]["_source"]
        return hit
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@app.post("/search")
async def productsSearch(request: SearchRequest):
    try:
        keywords = request.keyword.split()
        should_clauses = []
        for keyword in keywords:
            should_clauses.extend([
                {
                    "fuzzy": {
                        "name": {
                            "value": keyword,
                            "fuzziness": "AUTO",
                            "boost": 1.0
                        }
                    }
                },
                {
                    "match": {
                        "name": {
                            "query": keyword,
                            "boost": 2.0
                        }
                    }
                },
                {
                    "prefix": {
                        "name": {
                            "value": keyword,
                            "boost": 1.0
                        }
                    }
                }
            ])
        should_clauses.extend([
            {
                "match_phrase": {
                    "name": {
                        "query": request.keyword,
                        "boost": 5.0
                    }
                }
            },
            {
                "fuzzy": {
                    "name": {
                        "value": request.keyword,
                        "fuzziness": "AUTO",
                        "boost": 3.0
                    }
                }
            }
        ])
        from_value = (request.page - 1) * request.size

        # Handle sorting
        sort_option = None
        if request.sort == "asc":
            sort_option = [{"name.keyword": "asc"}]
        elif request.sort == "desc":
            sort_option = [{"name.keyword": "desc"}]
        # "default" means don't set sort (Elasticsearch will sort by score)

        es_search_kwargs = {
            "index": "cs_products_data",
            "query": {
                "bool": {
                    "should": should_clauses,
                    "minimum_should_match": 1
                }
            },
            "from_": from_value,
            "size": request.size
        }
        if sort_option:
            es_search_kwargs["sort"] = sort_option

        result = es.search(**es_search_kwargs)
        if not result["hits"]["hits"]:
            return {"products": [], "message": "Không tìm thấy sản phẩm"}
        products = []
        for hit in result["hits"]["hits"]:
            source = hit["_source"]
            products.append({
                "name": source["name"],
                "score": source.get("score", 0),
                "search_score": hit["_score"],
                "link_image": source.get("link_image", "assets/images/product-placeholder.jpg")
            })
        return {"products": products, "total": result["hits"]["total"]["value"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@app.post("/image-process")
async def extract_labels(file: UploadFile = File(...)):
    try:
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File phải là ảnh (jpg, png, v.v.)")
        content = await file.read()
        if len(content) > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File quá lớn, tối đa 10MB")
        model = genai.GenerativeModel("gemini-1.5-flash")
        image = {
            "mime_type": file.content_type,
            "data": content
        }
        prompt = "Identify and extract the product name from the label on the bottle in this image. Return the result in JSON format: [{'description': 'product name', 'score': 0.9}, ...]. Ensure the response is valid JSON and contains only the JSON object."
        response = model.generate_content([prompt, image])
        if not response.text:
            raise HTTPException(status_code=500, detail="Gemini API không trả về kết quả")
        try:
            labels = json.loads(response.text.strip("```json\n").strip("```"))
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="Không thể phân tích JSON từ Gemini API")
        return {
            "labels": labels,
            "total_labels": len(labels),
            "message": "Xử lý ảnh thành công" if labels else "Không tìm thấy tên sản phẩm trên nhãn"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi server: {str(e)}")

def send_guide_email_task(to_email: str):
    # Thông tin cấu hình email
    SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
    SMTP_USER = os.getenv("SMTP_USER")  # Ví dụ: yourmail@gmail.com
    SMTP_PASS = os.getenv("SMTP_PASS")  # App password
    if not (SMTP_USER and SMTP_PASS):
        print("Missing SMTP_USER or SMTP_PASS in environment!")
        return

    subject = "Your Free Copy of EWG’s Quick Tips for Safer Personal Care Products"

    text = (
        "Thank you for requesting EWG’s Quick Tips for Choosing Safer Personal Care Products!\n\n"
        "Please find your free guide attached to this email.\n\n"
        "This guide will help you make smarter, healthier choices for you and your family. "
        "Explore ingredient safety, learn how to spot EWG VERIFIED® products, and see how easy it is to shop with confidence.\n\n"
        "Stay informed and empowered—visit EWG’s Skin Deep® database any time to search for safety scores and ingredient information on thousands of personal care products.\n\n"
        "Thank you for supporting EWG’s mission to make safer products available for everyone!\n\n"
        "With care,\n"
        "The EWG Team"
    )

    # Tạo message đa phần (multipart)
    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg["From"] = SMTP_USER
    msg["To"] = to_email
    msg.attach(MIMEText(text, "plain", "utf-8"))

    # Đính kèm file PDF
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    pdf_path = os.path.join(BASE_DIR, "front_end", "assets", "ewg-guide.pdf")
    try:
        with open(pdf_path, "rb") as f:
            part = MIMEBase("application", "pdf")
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f'attachment; filename="EWG-Quick-Tips-Guide.pdf"'
            )
            msg.attach(part)
    except Exception as e:
        print(f"Error attaching PDF: {e}")

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_USER, [to_email], msg.as_string())
    except Exception as e:
        print(f"Error sending guide email to {to_email}: {e}")

@app.post("/send-guide-email")
async def send_guide_email(request: GuideEmailRequest, background_tasks: BackgroundTasks):
    # Gửi email trong background thread
    background_tasks.add_task(send_guide_email_task, request.email)
    return {"message": "Thanks! Check your email for the guide."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)