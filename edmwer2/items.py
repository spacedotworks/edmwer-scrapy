# -*- coding: utf-8 -*-

import scrapy

class EdmwerThread(scrapy.Item):
    title = scrapy.Field()
    ts = scrapy.Field()
    url = scrapy.Field()
    _id = scrapy.Field()
    replies = scrapy.Field()

class EdmwerPost(scrapy.Item):
    url = scrapy.Field()
    title = scrapy.Field()
    poster = scrapy.Field()
    date = scrapy.Field()
    content = scrapy.Field()
    _id = scrapy.Field()
    image_urls = scrapy.Field()
    likes = scrapy.Field()
    quoted = scrapy.Field()

class EdmwerUser(scrapy.Item):
    user = scrapy.Field()
    last_post = scrapy.Field()
    _id = scrapy.Field()
    avatar_url = scrapy.Field()
    post_count = scrapy.Field()
    rank = scrapy.Field()
    deluxe = scrapy.Field()
    join_date = scrapy.Field()

class EdmwerImage(scrapy.Item):
    image_url = scrapy.Field()
    _id = scrapy.Field()

