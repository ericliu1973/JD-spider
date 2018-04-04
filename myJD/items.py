# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class MyjdItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    price=scrapy.Field()
    shop=scrapy.Field()
    comment=scrapy.Field()
    link=scrapy.Field()
    good_rate=scrapy.Field()
    poor_rate=scrapy.Field()
    gere_rate=scrapy.Field()
    # top10comments=scrapy.Field()
    # pass
