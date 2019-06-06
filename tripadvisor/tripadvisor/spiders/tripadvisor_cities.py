import scrapy
from scrapy.selector import Selector
from scrapy.http import Request, FormRequest
import urlparse
from scrapy import signals
from scrapy.xlib.pydispatch import dispatcher
import MySQLdb

class TripAdvisor(scrapy.Spider):
    name = 'tripadvisor'
    start_urls = ['https://www.tripadvisor.in']

    def __init__(self, *args, **kwargs):
        super(TripAdvisor, self).__init__(*args, **kwargs)
        self.domain = 'https://www.tripadvisor.in'
        self.conn = MySQLdb.connect(
            host='localhost', user='root', passwd='root', db='TRIPADVISORDB', charset="utf8", use_unicode=True)
        self.cur = self.conn.cursor()
        self.url_q = 'insert into tripadvisor_crawl (sk, content_type, crawl_status, url, created_at, modified_at) values (%s,%s,%s,%s, now(), now()) on duplicate key update modified_at=now(), sk=%s, content_type=%s, crawl_status=%s, url=%s'
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def spider_closed(self, spider):
        self.conn.close()

    def AddDomain(self, url):
        return urlparse.urljoin(self.domain, url)

    def parse(self, response):
        sel = Selector(response)
        list_of_cities = sel.xpath('//div[@class="customSelection"]//div[@class="ui_columns"]//a/@href').extract()
        for url in list_of_cities:
            sk = url.strip('/').replace('.html', '')
            url = self.AddDomain(url)
            vals = (
                    sk, 'city', '0', url,
                    sk, 'city', '0', url
                )
            self.cur.execute(self.url_q, vals)
        self.conn.commit()


