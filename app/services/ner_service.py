from app.core import get_es_client, settings
from fastapi import HTTPException
import re

class NERService:
    def __init__(self):
        self.es = get_es_client()
        self.index = settings.ES_INDEX
    
    async def analyze_ingredients(self, content: str):
        """Analyze ingredients from text and return scores"""
        try:
            ingredients = re.split(r',|\s+và\s+|\s+hoặc\s+', content)
            
            if not ingredients:
                return {"ingredients": [], "message": "Không tìm thấy thành phần trong văn bản"}
            
            ingredient_list = []
            for ingredient in ingredients:
                result = self.es.search(
                    index=self.index,
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
