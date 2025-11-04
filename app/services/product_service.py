from app.core import get_es_client, settings
from fastapi import HTTPException

class ProductService:
    def __init__(self):
        self.es = get_es_client()
        self.index = settings.ES_INDEX
    
    async def get_product_safety(self, product_name: str):
        """Get product safety information for display"""
        try:
            result = self.es.search(
                index=self.index,
                query={"term": {"name.keyword": product_name}},
                size=1
            )
            
            if not result["hits"]["hits"]:
                return {"message": "Không tìm thấy sản phẩm"}
            
            hit = result["hits"]["hits"][0]["_source"]
            return {
                "name": hit["name"],
                "score": hit["score"],
                "link_image": hit["link_image"]
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
    
    async def get_product_details(self, product_name: str):
        """Get all product information"""
        try:
            result = self.es.search(
                index=self.index,
                query={"term": {"name.keyword": product_name}},
                size=1
            )
            
            if not result["hits"]["hits"]:
                return {"message": "Không tìm thấy sản phẩm"}
            
            return result["hits"]["hits"][0]["_source"]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
    
    async def search_products(self, keyword: str, page: int = 1, size: int = 20, sort: str = "default"):
        """Search products with pagination and sorting"""
        try:
            from_value = (page - 1) * size
            
            # Simple wildcard search
            query = {
                "bool": {
                    "should": [
                        {"wildcard": {"name": f"*{keyword.lower()}*"}},
                        {"match": {"name": {"query": keyword, "fuzziness": "AUTO"}}}
                    ],
                    "minimum_should_match": 1
                }
            }
            
            # Handle sorting
            sort_option = None
            if sort == "asc":
                sort_option = [{"name.keyword": "asc"}]
            elif sort == "desc":
                sort_option = [{"name.keyword": "desc"}]
            
            search_params = {
                "index": self.index,
                "query": query,
                "from_": from_value,
                "size": size
            }
            
            if sort_option:
                search_params["sort"] = sort_option
            
            result = self.es.search(**search_params)
            
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
            
            return {
                "products": products,
                "total": result["hits"]["total"]["value"]
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
    
    async def autocomplete(self, keyword: str, size: int = 10):
        """Get autocomplete suggestions"""
        try:
            size = min(size, 10)
            keywords = keyword.split()
            should_clauses = []
            
            for kw in keywords:
                should_clauses.extend([
                    {"prefix": {"name": {"value": kw, "boost": 3.0}}},
                    {"match_phrase_prefix": {"name": {"query": kw, "boost": 2.0}}},
                    {"fuzzy": {"name": {"value": kw, "fuzziness": "AUTO", "boost": 1.0}}}
                ])
            
            should_clauses.append({
                "match_phrase_prefix": {"name": {"query": keyword, "boost": 5.0}}
            })
            
            result = self.es.search(
                index=self.index,
                query={
                    "bool": {
                        "should": should_clauses,
                        "minimum_should_match": 1
                    }
                },
                size=size,
                _source=["name", "score", "link_image"]
            )
            
            if not result["hits"]["hits"]:
                return {"products": [], "message": "Không tìm thấy gợi ý"}
            
            products = []
            for hit in result["hits"]["hits"]:
                source = hit["_source"]
                products.append({
                    "name": source["name"],
                    "score": source.get("score", 0),
                    "search_score": hit["_score"],
                    "link_image": source.get("link_image", "assets/images/product-placeholder.jpg")
                })
            
            return {
                "products": products,
                "total": result["hits"]["total"]["value"]
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
