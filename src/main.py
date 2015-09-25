# -*- coding=utf-8 -*- 
import searchengine
from searchengine import crawler
import datas

crawler = searchengine.crawler('wikipython.db')
#crawler.createIndexTables()
crawler.crawl(datas.pages)