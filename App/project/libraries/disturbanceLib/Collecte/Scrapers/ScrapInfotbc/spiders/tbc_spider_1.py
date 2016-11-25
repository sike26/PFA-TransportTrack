import scrapy
from ScrapInfotbc.items import scrap_tbc_1
from ScrapInfotbc.items import scrap_tbc_cont
from ScrapInfotbc.items import scrap_mobiltbc
from ScrapInfotbc.items import scrap_mobiltbc_link
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor


##-------------------------------------Scrap de la page principale--------------------------------------------##


class Infotbc_Spider_1(CrawlSpider):
    
    name = "infotbc"
    allowed_domains = ["infotbc.com"]
    start_urls = ["http://www.infotbc.com/"]



    def parse(self, response):
        item = scrap_tbc_1()

        item['messages'] = response.xpath('//div[@id ="block-views-liste_alerte-block_1"]/*//ol/*//a/text()').extract()
        
        item['links'] = response.xpath('//div[@id ="block-views-liste_alerte-block_1"]/*//ol/*//a/@href').extract()

        yield item
              
  
##----------------------------------Scrap des liens de la page principale-------------------------------------##


class Infotbc_Spider_2(CrawlSpider):

    name = "infotbc_link"
    allowed_domains = ["infotbc.com"]
    start_urls = ["http://www.infotbc.com/"]
    

    rules = {
        Rule(LinkExtractor(restrict_xpaths='//div[@id ="block-views-liste_alerte-block_1"]/*//ol/*//a'), callback='parse_dir_contents'),
    }

    def parse_dir_contents(self, response):

        # Parse la page et recupere des informations complementaires
        item = scrap_tbc_cont()
        item['contents'] = response.xpath('//div[@id="content"]/div/div//strong/text()').extract()
        item['links'] = response.url

        yield item



##----------------------------------Scrap du site mobile-------------------------------------##

       
class Mobilinfotbc_Spider_1(CrawlSpider):

    name = "mobilinfotbc"
    allowed_domains = ["mobilinfotbc.com"]
    start_urls = ["http://www.mobilinfotbc.com/trafic-infos"]

    rules = (
        Rule(LinkExtractor(), callback='parse_dir_contents'),
    )
        

    def parse(self, response):
        item = scrap_mobiltbc()

        url_tbc = "http://www.mobilinfotbc.com"

        item['messages'] = response.xpath('//div[@id="section"]//tbody//td[@class="views-field views-field-title"]/a/text()').extract()
        
        item['links'] = response.xpath('//div[@id="section"]//tbody//td[@class="views-field views-field-title"]/a/@href').extract()

        yield item


##----------------------------------Scrap des liens du site mobile-------------------------------------##


class Mobilinfotbc_Spider_2(CrawlSpider):

    name = "mobilinfotbc_link"
    allowed_domains = ["mobilinfotbc.com"]
    start_urls = ["http://www.mobilinfotbc.com/trafic-infos"]
    deny_url = ['http://www.mobilinfotbc.com/alertes/attention-pensez-reserver-votre-trajet',
                'http://www.mobilinfotbc.com/en/trafic-infos',
                'http://www.mobilinfotbc.com/es/trafic-infos',
                'http://www.mobilinfotbc.com/montbc',
    ]
    rules = (
        Rule(LinkExtractor(deny='http://www.mobilinfotbc.com/alertes/attention-pensez-reserver-votre-trajet'), callback='parse_dir_contents'),
    )
    

    def parse_dir_contents(self, response):
        item = scrap_mobiltbc_link()
        

        # A revoir !!!!
        # Reflechir a un systeme permettant de recuperer le numero de la ligne de facon plus
        # generique pour en recuprer le plus possible...
        #

        path_list = ['//div[@id="section"]/div/div/div/div/h2/strong/text()',
                     '//div[@class="content clear-block"]/h2/p/strong/text()',
                     '//div[@class="content clear-block"]/h2/p/strong/br/text()',
                     '//div[@id="section"]/div/div/div/div/div/div/h4/strong/a/text()',
                     '//div[@id="section"]/div/div/h2/strong/a/text()',
                     '//div[@id="section"]/div/div/div/div/h2/strong/a/text()',
                     
        ]



        item['lignes'] = response.xpath('//div[@class="content clear-block"]/h2/strong/text()').extract()

        for p in path_list:
            if item['lignes'] == [] or item['lignes'] == ["", " "]:
                item['lignes'] = response.xpath(p).extract()
        
        item['infos'] = response.xpath('//div[@id="section"]/div/div//strong/text()').extract()
        item['links'] = response.url

                
        yield item



        

