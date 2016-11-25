import sys

sys.path.append("./ScrapInfotbc/spiders")

import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from tbc_spider_1 import Infotbc_Spider_1, Infotbc_Spider_2, Mobilinfotbc_Spider_1, Mobilinfotbc_Spider_2

import pandas as pd
import pickle


BOT_NAME = 'ScrapInfotbc'
    
SPIDER_MODULES = ['ScrapInfotbc.spiders']
NEWSPIDER_MODULE = 'ScrapInfotbc.spiders'
LOG_FILE = "scrapy_log"
LOG_STDOUT = True
ITEM_PIPELINES = {
    'ScrapInfotbc.pipelines.JsonWriterPipeline': 200,
    'ScrapInfotbc.pipelines.IsEmptyPipeline': 1, 
    'ScrapInfotbc.pipelines.EncodePipeline': 2,
    'ScrapInfotbc.pipelines.StockItemPipeline': 201,
    'ScrapInfotbc.pipelines.ToListPipiline': 3
    }


data_infotbc = "data_infotbc"
data_mobilinfotbc = "data_mobilinfotbc"
data_mobilinfotbc_l = "data_mobilinfotbc_l" 
data_infotbc_link = "data_infotbc_link"

l_data = [data_mobilinfotbc,
          data_mobilinfotbc_l,
          data_infotbc,
          data_infotbc_link]



def read_dict(filename):

    with open(filename, 'rb') as f:
        p = pickle.Unpickler(f)
        data_dict = p.load()
    
    return data_dict


def get_data():
    """
       Cette fonction lance les differents scrapers des sites de la tbc et regroupe les donnees collectes 
       dans un dictionnaire de dataframe (cf Pandas)
    """

    for f in l_data:
        with open(f, "wb") as tmp_file:
            tmp_file.close()

    
    s = Settings()
    s.set('BOT_NAME', BOT_NAME)
    s.set('SPIDER_MODULES', SPIDER_MODULES)
    s.set('NEWSPIDER_MODULE', NEWSPIDER_MODULE)
    s.set('LOG_FILE', LOG_FILE)
    s.set('ITEM_PIPELINES', ITEM_PIPELINES)

    

    process = CrawlerProcess(s)
    process.crawl(Infotbc_Spider_1)
    process.crawl(Infotbc_Spider_2)
    process.crawl(Mobilinfotbc_Spider_1)
    process.crawl(Mobilinfotbc_Spider_2)
    process.start()

    l_df = []

    for f in l_data:
        l_df.append(pd.DataFrame(read_dict(f)))
    
    df_infotbc = pd.merge(l_df[2], l_df[3])
    df_mobiltbc = pd.merge(l_df[0], l_df[1])

    return {'infotbc': df_infotbc, 'mobilinfotbc': df_mobiltbc}
