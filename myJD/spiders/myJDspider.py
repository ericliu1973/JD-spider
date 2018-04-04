# -*- coding: utf-8 -*-
import scrapy
from myJD.items import  MyjdItem
import time
class MyjdspiderSpider(scrapy.Spider):
    name = 'myJDspider'
    allowed_domains = ['jd.com']
    start_urls = ['http://jd.com/']
    count = 1
    start_url = 'https://search.jd.com/Search?keyword=python&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&wq=python&page={0}&s={1}&click=0'
    search_url='https://search.jd.com/s_new.php?keyword=python&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&wq=python&page={0}&s={1}&scrolling=y&log_id={2}&tpl=2_M&show_items={3}'
    rank_url = 'https://sclub.jd.com/comment/productPageComments.action?productId={}&score=0&sortType=3&page=0&pageSize=10&isShadowSku=0'
    # comments_url="https://club.jd.com/comment/productPageComments.action?callback=fetchJSON_comment98vv1049&productId={0}&score=0&sortType=5&page={1}&pageSize=10"
    # 这是准备用来抓取评论的，但是懒得写了

    def start_requests(self):
        s=3
        m=30
        for i in range(1,4):
            page = i * 2 - 1
            url = self.start_url.format(str(page), str(s))
            # url='https://search.jd.com/Search?keyword=python&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&wq=python&page=1&s=1$click=0'
            s=3+i*52
            m=30+(i-1)*52
            yield scrapy.Request(url, meta={'search_page': page + 1,'m':m,},callback=self.parse_url)  # 这里使用meta想回调函数传入数据，回调函数使用response.meta['search-page']接受数据
            # yield scrapy.Request(url,callback=self.parse_url)
    def parse_url(self, response):
        if response.status == 200:
            print (response.url)
            pids = set()
            try:
                all_goods = response.xpath("//div[@id='J_goodsList']/ul/li")

                for goods in all_goods:
                    items = MyjdItem()
                    pid = goods.xpath("@data-sku").extract()[0]
                    price = goods.xpath('div//div[@class="p-price"]/strong/i/text()').extract()[0]  # 价格
                    tt = goods.xpath('div//div[@class="p-name"]/a/em')
                    name=tt.xpath('string(.)').extract()[0]
                    shop_id = goods.xpath("div/div[@class='p-shopnum']/a/@title").extract()
                    if len(shop_id)==0:
                        shop_id=['京东自营']
                    link = 'https://item.jd.com/' + str(pid)+'.html'
                    comment = goods.xpath("div//div[@class='p-commit']/strong/a/text()").extract()[0]
                    if pid:
                        pids.add(pid)
                    if price:
                         items['price'] = price
                    if name:
                        items['name'] = name
                    if shop_id:
                        items['shop'] = shop_id[0]
                    if link:
                        items['link'] = link
                    if comment:
                        items['comment'] = comment

                    comment_url=self.rank_url.format(pid)
                    yield scrapy.Request(url=comment_url,meta={'items':items},callback=self.comment)
                print(pids)

            except Exception:
                print("********************************************ERROR**********************************************************************")
            log_id = str(time.time())[:-2]
            half_url=self.search_url.format(str(response.meta['search_page']),str(response.meta['m']),log_id, ",".join(pids))
            # print ('********************************THIS IS THE SECOND HALF URL*************************************************************')
            # print(half_url)
            # print('********************************THIS IS THE SECOND HALF URL*************************************************************')
            yield scrapy.Request(url=half_url,callback=self.next_half_parse)

    # 分析异步加载的网页
    def next_half_parse(self, response):
        if response.status == 200:
            print ("**************************************SECOND START   ****************************************************")
            print(response.url)

            # scrapy.shell.inspect_response(response,self)    #y用来调试的
            try:
                lis = response.xpath("//li[@class='gl-item']")
                for li in lis:
                    items = MyjdItem()
                    pid = li.xpath("@data-sku").extract()[0]
                    price = li.xpath('div//div[@class="p-price"]/strong/i/text()').extract()[0]  # 价格
                    tt =li.xpath('div//div[@class="p-name"]/a/em')
                    name = tt.xpath('string(.)').extract()[0]
                    shop_id = li.xpath("div/div[@class='p-shopnum']/a/@title").extract()
                    if len(shop_id) == 0:
                        shop_id = ['京东自营']
                    link = 'https://item.jd.com/' + str(pid) + '.html'
                    comment = li.xpath("div//div[@class='p-commit']/strong/a/text()").extract()[0]

                    if link:
                        items['link'] = link
                    if name:
                        items['name'] = name
                    if price:
                        items['price'] = price
                    if shop_id:
                        items['shop'] = shop_id[0]
                    if comment:
                        items['comment'] = comment
                    # yield items
                    comment_url = self.rank_url.format(pid)
                    yield scrapy.Request(url=comment_url, meta={'items': items}, callback=self.comment)
            except Exception:
                print("**************************************************")

    def comment(self,response):
        print("*******************          COMMENT CREATED                *******************************")
        import json
        item=response.meta['items']
        # item['good_rate'] = "无人评价"
        # item['poor_rate'] = "无人评价"
        # item['gere_rate'] ="无人评价"
        data=response.body.decode('cp936')
        data_json=json.loads(data)
        # if data_json["productCommentSummary"]["goodRate"] and data_json["productCommentSummary"]["poorRate"] and data_json["productCommentSummary"]["generalRate"]:
        item['good_rate']=str(format(data_json["productCommentSummary"]["goodRate"],'.2%'))
        item['poor_rate']=str(format(data_json["productCommentSummary"]["poorRate"],'.2%'))
        item['gere_rate']=str(format(data_json["productCommentSummary"]["generalRate"],'.2%'))
        yield item