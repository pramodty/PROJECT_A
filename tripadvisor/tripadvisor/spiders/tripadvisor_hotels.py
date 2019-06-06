import scrapy
from scrapy.selector import Selector
from scrapy.http import Request, FormRequest
import urlparse
from scrapy import signals
from scrapy.xlib.pydispatch import dispatcher
import MySQLdb
import re
import json

class TripAdvisorHotels(scrapy.Spider):
    name = 'tripadvisor_hotels'
    start_urls = []

    def __init__(self, *args, **kwargs):
        super(TripAdvisorHotels, self).__init__(*args, **kwargs)
        self.limit = kwargs.get('limit', '1')
        self.domain = 'https://www.tripadvisor.in'
        self.conn = MySQLdb.connect(
            host='localhost', user='root', passwd='root', db='TRIPADVISORDB', charset="utf8", use_unicode=True)
        self.cur = self.conn.cursor()
        self.hotel_q = 'insert into tripadvisor_hotels(hotal_id, name, best_price, rating, no_of_reviews, address, amenities, features, ota_deals, latitude, longitude, url, created_at, modified_at) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s, now(), now())'
        self.cities_queue = 'select * from tripadvisor_crawl where crawl_status=0 limit %s'%self.limit
        self.update_status = 'update tripadvisor_crawl set crawl_status="9" where sk = "%s"'
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def start_requests(self):
        self.cur.execute(self.cities_queue)
        url_list = self.cur.fetchall()
        for url_li in url_list:
            self.cur.execute(self.update_status%url_li[0])
            yield Request(url_li[3], callback=self.parse)


    def spider_closed(self, spider):
        self.conn.close()

    def AddDomain(self, url):
        return urlparse.urljoin(self.domain, url)

    def parse(self, response):
        sel = Selector(response)
        list_of_hotels = set(sel.xpath('//div[@class="relWrap"]//div[@class="ppr_rup ppr_priv_hsx_hotel_list_lite"]//div//a/@id').extract())
        for hotel in list_of_hotels:
            hotel_name = ''.join(sel.xpath('//a[@id="%s"]//text()'%hotel).extract())
            hotel_url = self.AddDomain(''.join(sel.xpath('//a[@id="%s"]//@href'%hotel).extract()))
            hotel_id = hotel.split('_')[-1]
            best_deal_val = ''.join(sel.xpath('//a[@id="%s"]/parent::div/parent::div/following-sibling::div[@class="main-cols"]//div[@class="premium_offer_container"]/div/@data-pernight'%hotel).extract())
            best_deal_ota = ''.join(sel.xpath('//a[@id="%s"]/parent::div/parent::div/following-sibling::div[@class="main-cols"]//div[@class="premium_offer_container"]/div/@data-vendorname'%hotel).extract())
            no_of_reviews = ''.join(sel.xpath('//a[@id="%s"]/parent::div/parent::div/following-sibling::div[@class="main-cols"]//div[@class="info-col"]//a[@class="review_count"]//text()'%hotel).extract()).split(' ')[0].strip()
            rating = ''.join(sel.xpath('//a[@id="%s"]/parent::div/parent::div/following-sibling::div[@class="main-cols"]//div[@class="info-col"]//@alt'%hotel).extract())
            rating = ''.join(re.findall('(\d.\d) ', rating))
            values = (
                    hotel_id, hotel_name, json.dumps({best_deal_ota:best_deal_val}), rating, no_of_reviews, '0', hotel_url,
                    hotel_id, hotel_name, json.dumps({best_deal_ota:best_deal_val}), rating, no_of_reviews, '0', hotel_url
                )
            yield Request(hotel_url, callback=self.parse_data, meta={'hotel_id':hotel_id, 'data':values})


    def parse_data(self, response):
        sel = Selector(response)
        hotal_id = response.meta.get('hotel_id', '')
        data = response.meta.get('data', ['']*5)
        name = ''.join(sel.xpath('//h1[@id="HEADING"]//text()').extract())
        address = ' '.join(sel.xpath('//div[@class="hotelActions"]//div[@class="content hidden"]/span//text()').extract())
        amenity = ','.join(sel.xpath('//span[@data="amenity_text"]//text()').extract())
        feature = ','.join(sel.xpath('//div[contains(text(), "Room features")]/parent::div//span[@data="amenity_text"]//text()').extract())
        ota_dict = {''.join(node.xpath('./@data-vendorname').extract()):''.join(node.xpath('./@data-pernight').extract()) for node in sel.xpath('//div[@class="ui_columns is-mobile is-multiline"]//div')}
        latitude = re.findall('\"latitude\":(\d+.\d+),', response.body)[0]
        longitude = re.findall('\"longitude\":(\d+.\d+),', response.body)[0]
        vals = (
                hotal_id, name, data[2], data[3], data[4], address, amenity, feature, json.dumps(ota_dict), latitude, longitude, response.url
            )
        self.cur.execute(self.hotel_q, vals)
