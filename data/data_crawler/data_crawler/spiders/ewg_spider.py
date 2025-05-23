#crawl_all_product_links in  ewg skindeep

import scrapy

class EwgSpiderSpider(scrapy.Spider):
    name = "ewg_spider"
    allowed_domains = ["www.ewg.org"]
    start_urls = ["https://www.ewg.org/skindeep/"]
    base_url = "https://www.ewg.org"

    def parse(self, response):
        yield from self.parse_link(response)

    def complete_url(self, relative_url):
        if relative_url.startswith("http"):
            return relative_url
        return self.base_url + relative_url

    def parse_link(self, response):
        all_links = {}
        tags = response.css(".mobile-menu .menu-card")
        tags = tags[2:]

        for tag in tags:
            bases = tag.css("li")
            tags_name = tag.css("li span::text").get()

            if tags_name is None:
                continue

            tags_name = tags_name.strip()

            if tags_name not in all_links:
                all_links[tags_name] = {}

            for base in bases:
                base_name = base.css("div::text").get()
                base_link = base.css("a::attr(href)").get()

                if not base_name or not base_link:
                    continue

                base_name = base_name.strip()

                if base_name not in all_links[tags_name]:
                    all_links[tags_name][base_name] = []

                all_links[tags_name][base_name].append({
                    "link": self.complete_url(base_link.strip()),
                    "product_links": []
                })

        for tag_name, sections in all_links.items():
            for section_name, products in sections.items():
                for product in products:
                    link = product["link"]
                    yield scrapy.Request(
                        url=link,
                        callback=self.parse_product_page,
                        errback=self.handle_error,
                        meta={
                            "product_info": product,
                            "tag_name": tag_name,
                            "section_name": section_name
                        }
                    )

    def handle_error(self, failure):
        self.logger.error(f"Request failed: {failure.request.url}, Error: {failure.value}")
        return

    def parse_product_page(self, response):
        if response.status == 429:
            self.logger.warning(f"Received 429 Too Many Requests on {response.url}. Retrying later.")
            return

        product_info = response.meta["product_info"]
        tag_name = response.meta["tag_name"]
        section_name = response.meta["section_name"]
        product_data = product_info

        try:
            product_links = response.css('.listings-pagination-wrapper .product-listings .product-tile a::attr(href)').getall()
            if not product_links:
                product_links = response.css('.product-tile a::attr(href)').getall()

            product_links = [self.complete_url(link.strip()) for link in product_links if link.strip()]
            product_links = product_links[::2]

            if not product_links:
                self.logger.debug(
                    f"No product links found on page: {response.url} for tag: {tag_name}, section: {section_name}"
                )
                return  # Dừng phân trang nếu trang trống
            else:
                product_data["product_links"].extend(product_links)
                self.logger.debug(f"Found {len(product_links)} product links on page: {response.url}")
                yield {
                    "tag": tag_name,
                    "section": section_name,
                    "product": section_name,
                    "link": product_data["link"],
                    "product_links": product_links,
                    "page_url": response.url  # Thêm URL trang để dễ theo dõi
                }

        except Exception as e:
            self.logger.error(
                f"Error extracting product links on page: {response.url} for tag: {tag_name}, section: {section_name}. Error: {str(e)}"
            )
            product_links = []

        next_page = response.css(".listings-pagination-wrapper a.next_page::attr(href)").get()
        if next_page is not None:
            next_page_url = self.complete_url(next_page.strip())
            yield scrapy.Request(
                url=next_page_url,
                callback=self.parse_product_page,
                errback=self.handle_error,
                meta={
                    "product_info": product_info,
                    "tag_name": tag_name,
                    "section_name": section_name
                }
            )