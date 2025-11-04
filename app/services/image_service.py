import google.generativeai as genai
from app.core import settings
from fastapi import HTTPException, UploadFile
import json

class ImageService:
    def __init__(self):
        if not settings.GOOGLE_API_KEY:
            raise ValueError("Missing GOOGLE_API_KEY in environment")
        genai.configure(api_key=settings.GOOGLE_API_KEY)
    
    async def extract_product_from_image(self, file: UploadFile):
        """Extract product name from image using Gemini AI"""
        try:
            if not file.content_type.startswith("image/"):
                raise HTTPException(status_code=400, detail="File phải là ảnh (jpg, png, v.v.)")
            
            content = await file.read()
            if len(content) > 10 * 1024 * 1024:  # 10MB
                raise HTTPException(status_code=400, detail="File quá lớn, tối đa 10MB")
            
            model = genai.GenerativeModel("gemini-1.5-flash")
            image = {
                "mime_type": file.content_type,
                "data": content
            }
            
            prompt = (
                "Identify and extract the product name from the label on the bottle in this image. "
                "Return the result in JSON format: [{'description': 'product name', 'score': 0.9}, ...]. "
                "Ensure the response is valid JSON and contains only the JSON object"
            )
            
            response = model.generate_content([prompt, image])
            
            if not response.text:
                raise HTTPException(status_code=500, detail="Gemini API không trả về kết quả")
            
            try:
                labels = json.loads(response.text.strip("```json\n").strip("```"))
            except json.JSONDecodeError:
                raise HTTPException(
                    status_code=500,
                    detail="Không thể phân tích JSON từ Gemini API"
                )
            
            return {
                "labels": labels,
                "total_labels": len(labels),
                "message": "Xử lý ảnh thành công" if labels else "Không tìm thấy tên sản phẩm trên nhãn"
            }
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Lỗi server: {str(e)}")
