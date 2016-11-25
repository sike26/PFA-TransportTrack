import json

from ScrapInfotbc.items import scrap_tbc_1
from ScrapInfotbc.items import scrap_tbc_cont
from ScrapInfotbc.items import scrap_mobiltbc
from ScrapInfotbc.items import scrap_mobiltbc_link

from scrapy.exceptions import DropItem

import pandas as pd
import pickle


file_infotbc = "data_infotbc"
file_mobilinfotbc = "data_mobilinfotbc"
file_infotbc_link = "data_infotbc_link"


class JsonWriterPipeline(object):
    """

       Classe JsonXriterPipelin

       Methode process_item :
       Stocke les items des spiders infotbc dans 2 fichiers JSON, messages.jl et contents.jl

    """
    def __init__(self):
        self.messages_file = open('messages.jl', 'ab')
        self.contents_file = open('contents.jl', 'ab')
        # self.mobil_file = open('mobil.jl', 'ab')

    def process_item(self, item, spider):
        if isinstance(item, scrap_tbc_1):
            line = json.dumps(item['messages'], encoding='utf-8') + "\n"
            self.messages_file.write(line)

        elif isinstance(item, scrap_tbc_cont):       
            line = json.dumps(item['contents'], encoding='utf-8') + "\n"
            self.contents_file.write(line)
        return item



class IsEmptyPipeline(object):
    """

       Classe IsEmptyPipeline

       Methode process_item :
       Leve un excemtion DropItem lorqu'elle tourve un item vide.

    """

    def __init__(self):
        self.log = open("parse.log", "a+b")

    def open_spider(self, spider):
        s = "Scrap begin\n\n"
        self.log.write(s)

    def close_spider(self, spider):
        s = "\nScrap END\n\n"
        self.log.write(s)

    def process_item(self, item, spider):
        if isinstance(item, scrap_tbc_1):
            if item['messages']:
                return item
            else:
                raise DropItem("Missing item field messages")
                
        elif isinstance(item, scrap_tbc_cont):
            if item['contents']:        
                return item
            else:
                raise DropItem("No content on the page")
        elif isinstance(item, scrap_mobiltbc_link):

            if item['lignes'] == [] or item['lignes'] == ["", " "]:
                s = "Parse fail :" + item['links'] + "\n"
                self.log.write(s)

        return item


class EncodePipeline(object):
    """
       Classe EncodePipeline

       Attribut : enc_format. Ca valeur des par default utf-8

        Methode process_item :
        Encode les chaine unicode des items en format enc_format.

    """    
    enc_format = 'utf-8'
    
    def process_item(self, item, spider):
        if isinstance(item, scrap_tbc_1):
            for i in range(0, len(item['messages'])): 
                item['messages'][i] = item['messages'][i].encode(self.enc_format)

        if isinstance(item, scrap_mobiltbc):
            for i in range(0, len(item['messages'])): 
                item['messages'][i] = item['messages'][i].encode(self.enc_format)

        if isinstance(item, scrap_mobiltbc_link):
            if item['lignes']:
                item['lignes'][0] = item['lignes'][0].encode(self.enc_format)

        return item


class StockItemPipeline(object):
    """
       
       Classe StockItemPipeline 

       Methode process_item :
       Stocke les items des spiders infotbc et mobilinfotbc dans un fichier. Les nom de ces fichiers sont definie dans les variables file_infotbc et file_mobilinfotbc. Les donnees issue des items sont convertie en dataFrame (cf module Pandas) et ecrit dans un fichier avec le module Pickle.

    """
    def process_item(self, item, spider):
        if isinstance(item, scrap_tbc_1):

            data_infotbc = open(file_infotbc, 'rb')
            pi = pickle.Unpickler(data_infotbc)

            try:
                df = pi.load()
            except:
                df = pd.DataFrame()
            
            d_list = []
            for i in range(0, len(item['messages'])):
                d = dict()
                d['messages'] = item['messages'][i]
                d['links'] = item['links'][i]
                d_list.append(d)

            df_new = pd.DataFrame(d_list)
            df = df.append(df_new)

            data_infotbc.close()
            data_infotbc = open(file_infotbc, 'wb')
            pi = pickle.Pickler(data_infotbc)
            pi.dump(df)
            data_infotbc.close()

        elif isinstance(item, scrap_mobiltbc):

            data_mobilinfotbc = open(file_mobilinfotbc, 'rb')
            p = pickle.Unpickler(data_mobilinfotbc)

            try:
                df = p.load()
            except:
                df = pd.DataFrame()
            
            d_list = []
            for i in range(0, len(item['messages'])):
                d = dict()
                d['messages'] = item['messages'][i]
                d['links'] = item['links'][i]
                d_list.append(d)

            df_new = pd.DataFrame(d_list)
            df = df.append(df_new)
            
            data_mobilinfotbc.close()
            data_mobilinfotbc = open(file_mobilinfotbc, 'wb')
            p = pickle.Pickler(data_mobilinfotbc)
            p.dump(df)
            data_mobilinfotbc.close()

        elif isinstance(item, scrap_tbc_cont): 
            data_infotbc_link = open(file_infotbc_link, 'rb')
            p = pickle.Unpickler(data_infotbc_link)

            try:
                df = p.load()
            except:
                df = pd.DataFrame()
            
            d_list = []
            d = dict()
            d['contents'] = item['contents']

            s = "http://www.infotbc.com"
            d['links'] = item['links'][len(s):]
            d_list.append(d)

            df_new = pd.DataFrame(d_list)
            df = df.append(df_new)
            
            data_infotbc_link.close()
            data_infotbc_link = open(file_infotbc_link, 'wb')
            p = pickle.Pickler(data_infotbc_link)
            p.dump(df)
            data_infotbc_link.close()
        return item



class ToListPipiline(object):

    list_dict = []
    s = "http://www.mobilinfotbc.com"
    
    def __init__(self):
        self.data_mobilinfotbc_l = open("data_mobilinfotbc_l", 'wb')
        self.p = pickle.Pickler(self.data_mobilinfotbc_l)

    
    def process_item(self, item, spider):
        if isinstance(item, scrap_mobiltbc_link):
            item['links'] = item['links'][len(self.s):] 
            self.list_dict.append(item)
        return item


    def close_spider(self, spider):
        df = pd.DataFrame(self.list_dict)
        self.p.dump(df)
        self.data_mobilinfotbc_l.close()

