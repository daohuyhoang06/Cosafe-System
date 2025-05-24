import scrapy
import re
import json
from collections import defaultdict

class EwgSpiderSpider(scrapy.Spider):
    name = "product_spider"
    allowed_domains = ["www.ewg.org"]
    
    # Xóa start_urls và base_url
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.product_links = self.load_product_links()

    def load_product_links(self):
        """Đọc tất cả product_links từ file JSON"""
        try:
            with open("Face_and_Body_Face.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                all_links = []
                for group in data:
                    all_links.extend(group["product_links"])
                self.logger.info(f"Loaded {len(all_links)} product links")
                return all_links
        except Exception as e:
            self.logger.error(f"Error loading JSON: {str(e)}")
            return []

    def start_requests(self):
        """Tạo request cho từng sản phẩm"""
        for url in self.product_links:
            yield scrapy.Request(url, callback=self.parse)

    def parse(self, response):
        """Xử lý từng trang sản phẩm"""
        item = defaultdict(lambda: None)
        
        # Gọi các hàm con và merge kết quả
        item.update(self.parse_name(response))
        item.update(self.parse_score(response))
        item.update(self.parse_ingredient_concerns(response))
        item.update(self.parse_ingredient(response))
        
        yield item

    def parse_score(self, response):
        img_src = response.css('.product-score-name-wrapper img::attr(src)').get()
        return {'score': self.extract_score(img_src)}

    def extract_score(self, src):
        if not src: return 0
        if src == "https://static.ewg.org/upload/png/EWG_Verified_logo.png" : return 0
        match = re.search(r'score-(\d{2})', src)
        match = int(match.group(1)) if match else None
        if match is None : 
            match = re.search(r'(\d+)\.png$', src)
            match = int(match.group(1)) if match else None
        if match is None : 
            match = 0
        return match 
    
    def parse_name(self, response): 
        name = response.css('.product-score-name-wrapper h2.product-name::text').get().strip()
        if name == "": name = response.css('.product-score-name-wrapper h2.product-name h1::text').get().strip()
        link_image = response.css('.product-wrapper .product-upper img::attr(srcset)').get()
        return {
            'name': name if name else None,
            'link_image': link_image,
            'product_url': response.url  # Thêm URL sản phẩm
        }
    
    def parse_ingredient_concerns(self, response): 
        ingredient_concerns = response.css('.product-ingredient-info-wrapper .ingredient-concerns ul li')
        result = {}
        for concern in ingredient_concerns:
            level_elements = concern.css('div.level::text').getall()
            level = level_elements[1].strip() if len(level_elements) > 1 else None
            attribute = concern.css('div.level + .concern-text::text').get()
            if attribute and level:
                result[attribute.strip()] = level
        return {'ingredient_concerns': result}
    
    def parse_ingredient(self, response):
        ingredients = response.css('.ingredient-overview-tr')
        more = response.css('.ingredient-more-info-wrapper')
        result = {}
        
        for idx in range(len(ingredients)):
            name_element = ingredients[idx].css('.td-ingredient-interior::text').get()
            if not name_element: continue
            
            name = name_element.strip().title()
            img_src = ingredients[idx].css('img.ingredient-score::attr(src)').get()
            link = more[idx].css('td a.underline-hover::attr(href)').get() if idx < len(more) else None
            
            result[name] = {
                'score': self.extract_score(img_src),
                'link': response.urljoin(link) if link else None  # Chuyển thành URL tuyệt đối
            }
        
        return {'ingredients': result}
