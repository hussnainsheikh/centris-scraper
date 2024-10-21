import scrapy
from scrapy.selector import Selector
from scrapy_splash import SplashRequest
import json

class ListingsSpider(scrapy.Spider):
    name = "listings"
    allowed_domains = ["www.centris.ca", "www.centris.ca/fr"]
    position = {
        'startPosition': 0
    }
    
    script = '''
        function main(splash, args)
            splash:on_request(function(request)
                if request.url:find("css") then
                    request.abort()
                end
            end)
            splash.images_enabled = false
            splash.js_enabled = false
            assert(splash:go(args.url))
            assert(splash:wait(0.5))
            return splash:html()
        end
    '''
    
    def start_requests(self):
        
        yield scrapy.Request(
            url="https://www.centris.ca/UserContext/Lock",
            method='POST',
            headers={
                'x-requested-with': 'XMLHttpRequest',
                'Content-Type': 'application/json'
            },
            body=json.dumps({'uc': 0}),
            callback=self.generate_uck
        )
    
    def generate_uck(self, respone):
        
        uck = respone.body
        print(uck)
        query = {
            "query": {
                "UseGeographyShapes": 0,
                "Filters": [
                    {
                        "MatchType": "CityDistrictAll",
                        "Text": "Montréal (All boroughs)",
                        "Id": 5
                    }
                ],
                "FieldsValues": [
                    {
                        "fieldId": "CityDistrictAll",
                        "value": 5,
                        "fieldConditionId": "",
                        "valueConditionId": ""
                    },
                    {
                        "fieldId": "Category",
                        "value": "Residential",
                        "fieldConditionId": "",
                        "valueConditionId": ""
                    },
                    {
                        "fieldId": "SellingType",
                        "value": "Rent",
                        "fieldConditionId": "",
                        "valueConditionId": ""
                    },
                    {
                        "fieldId": "LivingArea",
                        "value": "SquareFeet",
                        "fieldConditionId": "IsResidentialNotLot",
                        "valueConditionId": ""
                    },
                    {
                        "fieldId": "LandArea",
                        "value": "SquareFeet",
                        "fieldConditionId": "IsLandArea",
                        "valueConditionId": ""
                    },
                    {
                        "fieldId": "RentPrice",
                        "value": 0,
                        "fieldConditionId": "ForRent",
                        "valueConditionId": ""
                    },
                    {
                        "fieldId": "RentPrice",
                        "value": 1750,
                        "fieldConditionId": "ForRent",
                        "valueConditionId": ""
                    }
                ]
            },
            "isHomePage": True
        }
        yield scrapy.Request(
            url = "https://www.centris.ca/property/UpdateQuery",
            method = "POST",
            body=json.dumps(query),
            headers={
                'x-requested-with': 'XMLHttpRequest',
                'Content-Type': 'application/json',
                'charset': 'UTF-8',
                'x-centris-uck': uck,
                'x-centris-uc': 0
            },
            callback=self.update_query
        )
        
    def update_query(self, response):
        yield scrapy.Request(
            url='https://www.centris.ca/Property/GetInscriptions',
            method='POST',
            body=json.dumps(self.position),
            headers={
                'Content-Type': 'application/json'
            },
            callback=self.parse
        )

    def parse(self, response):
        resp_dict = json.loads(response.body)
        html = resp_dict.get('d').get('Result').get('html')
        sel = Selector(text=html)
        listings = sel.xpath("//div[@class='property-thumbnail-item thumbnailItem col-12 col-sm-6 col-md-4 col-lg-3']")
        for listing in listings:
            category = listing.xpath("normalize-space(.//div[@class='location-container']//span[@class='category']/div/text())").get()
            features = listing.xpath(".//div[contains(@class, 'features')]/div/text()").get()
            price = listing.xpath("normalize-space(.//div[@class='price']/span/text())").get()
            city = listing.xpath(".//div[@class='location-container']/span[@class='address']/div/text()").get()
            url = listing.xpath(".//a[@class='a-more-detail']/@href").get()
            abs_url = f"https://www.centris.ca{url}"
            
            yield SplashRequest(
                url=abs_url,
                endpoint='execute',
                callback=self.parse_summary,
                args={
                    'lua_source': self.script
                },
                meta={
                    'cat': category.strip(),
                    'fea': features,
                    'city': city,
                    'price': price.replace('\xa0', ''),
                    'url': abs_url
                }
            )

        count = resp_dict.get('d').get('Result').get('count')
        increment_num = resp_dict.get('d').get('Result').get('inscNumberPerPage')
        
        if self.position['startPosition'] <= count:
            self.position['startPosition'] += increment_num
            yield scrapy.Request(
                url='https://www.centris.ca/Property/GetInscriptions',
                method='POST',
                body=json.dumps(self.position),
                headers={
                    'Content-Type': 'application/json'
                },
                callback=self.parse
            )
    
    def parse_summary(self, response):
        address = response.xpath("normalize-space(//h2[@itemprop='address']/text())").get()
        description = response.xpath("normalize-space(//div[@itemprop='description']/text())").get()
        category = response.request.meta['cat']
        features = response.request.meta['fea']
        city = response.request.meta['city']
        price = response.request.meta['price']
        url = response.request.meta['url']
        
        yield {
            'address': address,
            'description': description,
            'category': category,
            'features': features,
            'price': price,
            'city': city,
            'url': url
        }