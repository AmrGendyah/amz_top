import scrapy
from urllib.parse import urlencode
from urllib.parse import urlparse
import json
from scraper_api import ScraperAPIClient
import pandas as pd
import pkgutil  
from io import BytesIO


def create_google_url(query, site=''):
    google_dict = {'q': query, 'num': 10, 'gl':'us' ,'hl' : 'en' }
    if site:
        web = urlparse(site).netloc
        google_dict['as_sitesearch'] = web
    print('https://www.google.com/search?' + urlencode(google_dict))
    return 'https://www.google.com/search?' + urlencode(google_dict)


class TopSpider(scrapy.Spider):
    name = 'top'
    lkns_list=[]
    azlink_list=[]
    
    data = pkgutil.get_data("top_results","resources/kws.csv")
    words_pd = pd.read_csv(BytesIO((data)))
    wordslist = words_pd['keywords'].tolist()

    client = ScraperAPIClient('210b5733e8691413c0bdcdb73c9ed554')
    
    def start_requests(self):
        
        
        for word in self.wordslist:
            print(word)
            link = create_google_url(str(word))
            yield scrapy.Request(
                self.client.scrapyGet(url = link, autoparse= True, country_code='us'), 
                callback=self.parse,
                meta={'kywrd':word})


    def parse(self, response):
       
        di = json.loads(response.text)
        for result in di['organic_results']:         
           link = result['link']

           yield scrapy.Request(
               url =link,
               callback=self.parse_amz,
               meta={'kywrd':response.meta['kywrd']}
           )

    
    def parse_amz(self, response):
        pets = response.xpath("//a")
        ptod_list = []
        for pet in pets:
            link = pet.xpath('.//@href[contains(., "amazon") or contains(., "amz")]').extract_first()
            
            if link != None and link not in ptod_list :
                ptod_list.append(link)
                self.lkns_list.append(link)
        
        for lnk in ptod_list:
            yield scrapy.Request(
                self.client.scrapyGet(url = str(lnk), country_code='us'),
                callback=self.parse_amzdata,
                meta={
                    'kywrd':response.meta['kywrd'], 
                    'orglnk':lnk
                    }
                )
    
    
    def parse_amzdata(self, response):
        name = response.xpath('normalize-space(//div[@id="titleSection"]//span[@id="productTitle"]//text())').extract_first()
        price = response.xpath('normalize-space(//*[@id="price_inside_buybox"]//text())').extract_first()
        if price == '':
            price = response.xpath('normalize-space(//span[@id="priceblock_ourprice"]//text())').extract_first()

        stock = response.xpath('normalize-space(//div[@id="availability"]//span//text())').extract_first()
        if stock == '':
            stock = response.xpath('(//div[@id="availability_feature_div"]/div[@id="availability"]/span[@class="a-size-medium a-color-price"]/text())').extract_first()
           
        if (price == '' or price == None) and (stock == 'None' or stock == '' or stock == None):
            stock = 'Currently unavailable.'
   
        pro_link = response.xpath('//link[@rel="canonical"]//@href').extract_first()
        if pro_link not in self.azlink_list:
            self.azlink_list.append(pro_link)
            if name :
                yield{
                    'keyword': response.meta['kywrd'],
                    'product_name' : name,
                    'price': price,
                    'stock': stock,
                    'amazon_link': pro_link
                }



    