from app.core import get_es_client, settings
from fastapi import HTTPException
import re

class NERService:
    def __init__(self):
        self.es = get_es_client()
        self.index = settings.ES_INDEX
    
    async def analyze_ingredients(self, content: str):
        """Analyze ingredients from text and return scores (tối ưu hóa với bulk query)"""
        try:
            # Parse ingredients
            ingredients = re.split(r',|\s+và\s+|\s+hoặc\s+', content)
            ingredients = [ing.strip() for ing in ingredients if ing.strip()]
            
            if not ingredients:
                return {"ingredients": [], "message": "Không tìm thấy thành phần trong văn bản"}
            
            # OPTIMIZATION: Query tất cả ingredients trong 1 lần thay vì N queries riêng lẻ
            # Sử dụng bool query với should clauses
            should_clauses = []
            for ingredient in ingredients:
                should_clauses.append({
                    "exists": {"field": f"ingredients.{ingredient.upper()}"}
                })
            
            # Query 1 lần duy nhất để lấy tất cả ingredients
            result = self.es.search(
                index=self.index,
                query={
                    "bool": {
                        "should": should_clauses,
                        "minimum_should_match": 1
                    }
                },
                size=100,  # Lấy nhiều kết quả để cover tất cả ingredients
                _source=["ingredients"]
            )
            
            # Parse kết quả
            ingredient_list = []
            found_ingredients = set()
            
            for hit in result.get("hits", {}).get("hits", []):
                if "_source" in hit and "ingredients" in hit["_source"]:
                    ingredients_data = hit["_source"]["ingredients"]
                    
                    # Check từng ingredient trong danh sách
                    for ingredient in ingredients:
                        ing_upper = ingredient.upper()
                        if ing_upper in ingredients_data and ing_upper not in found_ingredients:
                            score_data = ingredients_data[ing_upper]
                            if isinstance(score_data, dict) and "score" in score_data:
                                ingredient_list.append({
                                    "name": ingredient,
                                    "score": score_data["score"]
                                })
                                found_ingredients.add(ing_upper)
            
            if not ingredient_list:
                return {"ingredients": [], "message": "Không tìm thấy thành phần"}
            
            return {"ingredients": ingredient_list}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
