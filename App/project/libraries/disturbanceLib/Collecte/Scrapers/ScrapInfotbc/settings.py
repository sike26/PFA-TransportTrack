# -*- coding: utf-8 -*-

# Scrapy settings for Scraper Infotbc.com project
#


BOT_NAME = 'ScrapInfotbc'

SPIDER_MODULES = ['ScrapInfotbc.spiders']
NEWSPIDER_MODULE = 'ScrapInfotbc.spiders'

ITEM_PIPELINES = {
    'ScrapInfotbc.pipelines.JsonWriterPipeline': 200,
    'ScrapInfotbc.pipelines.IsEmptyPipeline': 1, 
    'ScrapInfotbc.pipelines.EncodePipeline': 2,
    'ScrapInfotbc.pipelines.StockItemPipeline': 201,
    'ScrapInfotbc.pipelines.ToListPipiline': 3
}
