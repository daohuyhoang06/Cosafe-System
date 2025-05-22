from fastapi import APIRouter, HTTPException, File, UploadFile
import google.generativeai as genai
import json
import os
from dotenv import load_dotenv

router = APIRouter()

# Load environment variables
load_dotenv()

# Gemini API config
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("Missing GOOGLE_API_KEY. Please set in .env or environment.")
genai.configure(api_key=GEMINI_API_KEY)

@router.post("/image-process")
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
        prompt = "Identify and extract the product name from the label on the bottle in this image. Return the result in JSON format: [{'description': 'product name', 'score': 0.9}, ...]. Ensure the response is valid JSON and contains only the JSON object"
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