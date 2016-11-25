import scrapy

### ----------- Item pour le scraper pannes de infotbc et mobilinfotbc ---------- ###


class scrap_tbc_1(scrapy.Item):
    messages = scrapy.Field()
    links = scrapy.Field()


class scrap_tbc_cont(scrapy.Item):
    contents = scrapy.Field()
    links = scrapy.Field()


class scrap_mobiltbc(scrapy.Item):
    messages = scrapy.Field()
    links = scrapy.Field() 


class scrap_mobiltbc_link(scrapy.Item):
    links = scrapy.Field()
    lignes = scrapy.Field()
    infos = scrapy.Field()
    
