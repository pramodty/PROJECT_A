import scrapy
from scrapy.selector import Selector
from scrapy.http import Request, FormRequest
import urlparse
from scrapy import signals
from scrapy.xlib.pydispatch import dispatcher
import MySQLdb
import re
import json

class TripAdvisorHotelsDetails(scrapy.Spider):
    name = 'hotels_details'
    start_urls = []

    def __init__(self, *args, **kwargs):
        super(TripAdvisorHotelsDetails, self).__init__(*args, **kwargs)
        self.limit = kwargs.get('limit', '1')
        self.domain = 'https://www.tripadvisor.in'
        self.conn = MySQLdb.connect(
            host='localhost', user='root', passwd='root', db='TRIPADVISORDB', charset="utf8", use_unicode=True)
        self.cur = self.conn.cursor()
        self.details_q = 'insert into property_details(sk, name, address, amenities, features, ota_deals, latitude, longitude, url, created_at, modified_at) values (%s,%s,%s,%s,%s,%s,%s,%s,%s, now(), now()) on duplicate key update modified_at=now(), sk=%s, name=%s, address=%s, amenities=%s, features=%s, ota_deals=%s, latitude=%s, longitude=%s, url=%s'
        self.cities_queue = 'select * from tripadvisor_hotels where crawl_status=0 limit %s'%self.limit
        self.update_status = 'update tripadvisor_hotels set crawl_status="9" where sk = "%s"'
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def start_requests(self):
        self.cur.execute(self.cities_queue)
        url_list = self.cur.fetchall()
        for url_li in url_list:
            self.cur.execute(self.update_status%url_li[0])
            yield Request(url_li[6], callback=self.parse, meta={'sk':url_li[0]})
        #yield Request('https://www.tripadvisor.in/Hotel_Review-g1638802-d1948824-Reviews-Amritara_Ambatty_Greens_Resort-Virajpet_Kodagu_Coorg_Karnataka.html', callback=self.parse, meta={'sk':'1948824'})


    def spider_closed(self, spider):
        self.conn.close()

    def AddDomain(self, url):
        return urlparse.urljoin(self.domain, url)

    def parse(self, response):
        sel = Selector(response)
        sk = response.meta.get('sk', '')
        name = ''.join(sel.xpath('//h1[@id="HEADING"]//text()').extract())
        address = ' '.join(sel.xpath('//div[@class="hotelActions"]//div[@class="content hidden"]/span//text()').extract())
        amenity = ','.join(sel.xpath('//span[@data="amenity_text"]//text()').extract())
        feature = ','.join(sel.xpath('//div[contains(text(), "Room features")]/parent::div//span[@data="amenity_text"]//text()').extract())
        ota_dict = {''.join(node.xpath('./@data-vendorname').extract()):''.join(node.xpath('./@data-pernight').extract()) for node in sel.xpath('//div[@class="ui_columns is-mobile is-multiline"]//div')}
        latitude = re.findall('\"latitude\":(\d+.\d+),', response.body)[0]
        longitude = re.findall('\"longitude\":(\d+.\d+),', response.body)[0]
        vals = (
                sk, name, address, amenity, feature, json.dumps(ota_dict), latitude, longitude, response.url,
                sk, name, address, amenity, feature, json.dumps(ota_dict), latitude, longitude, response.url
            )
        self.cur.execute(self.details_q, vals)
