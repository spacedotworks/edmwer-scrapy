# -*- coding: utf-8 -*-
import sys
import pymongo
import hashlib
from scrapy.exceptions import DropItem
from scrapy.http import Request
from scrapy.conf import settings
from scrapy import log

class MongoDBPipeline(object):

    def __init__(self):
        connection = pymongo.MongoClient(
            settings['MONGODB_SERVER'],
            settings['MONGODB_PORT']
        )
        db = connection[settings['MONGODB_DB']]
        self.col_threads = db['threads']
        self.col_posts = db['posts']
        self.col_images = db['images']
        self.col_users = db['users']

    def process_item(self, item, spider):
        # for threads
        if 'ts' in item:
            _id = item['_id']
            item.pop('_id', None)
            self.col_threads.update({
                '_id' : _id
            }, {
                '$set': item
            }, upsert=True)
        elif 'image_url' in item:
            _id = item['_id']
            item.pop('_id', None)
            self.col_images.update({
                '_id' : _id
            }, {
                '$set': item
            }, upsert=True)
        elif 'poster' in item:
            _id = item['_id']
            item.pop('_id', None)
            self.col_posts.update({
                '_id' : _id
            }, {
                '$set': item
            }, upsert=True)
        elif 'join_date' in item:
            last_post = item['last_post']
            item.pop('last_post', None)
            _id = item['_id']
            item.pop('_id', None)
            self.col_users.update({
                '_id' : _id
            }, {
                '$set': item,
                '$max': {
                  'last_post': last_post
                }
            }, upsert=True)
