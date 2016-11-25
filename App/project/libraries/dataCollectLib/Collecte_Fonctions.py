import pandas as pd
from owslib.wfs import WebFeatureService
from lxml import etree
import requests
import unicodedata

"""
   Ce fichier contient les fonctions permettant de recuperer les donnees provenant de 
   l'API wfs de data bordeaux metropole.
"""







# Variables Globales Constantes

url_wfs = 'http://data.bordeaux-metropole.fr/wfs?key=GVY1ZR3Y0B'
url_wps = 'http://data.lacub.fr/wps'
vrsn = '1.1.0'



# Fonctions

def local_name(s):
    """
       Simple fonction qui sert a compter le nombre de caractere du namespace local du 
       fichier xml recupere grace a l'API.
    """
    i = 0;
    while s[i] != '}':
        i += 1
     
    i += 1       
    return i



def get_elem_content(element):
    """
       Cette fonction prend en argument un element du type lxml.etree._Element issue 
       du parse d'un fichier xml et retourne un dictionnaire contenant les donnees.
       
       Elle effectue quelques modifications au niveau du type des donnees. Le dictionnaire
       en sortie ne contient que des str.
    """
    dic = dict()
    for select in element.getiterator():
        if isinstance(select.text, unicode):
            s = select.text.encode('utf-8')
        elif isinstance(select.text, type(None)):
            s = ""
        else :
            s = select.text
        
        if  len(s) > 1:
            if s[0] == '\n':
                s = ""
                
        dic[select.tag[local_name(select.tag):]] = s

    return dic



def make_file(tp, s):
    """
       Cette fonction copie dans un fichier, tp.xml, le contenue de "s" et retourne
       le nom du fichier.
    """
    filename = tp + ".xml"
    with open(filename, 'wb') as f:
        f.write(s)

    return filename



def to_dataframe(element_list):
    """
       Prend en parametre une list element etree (resultat du parse de la reponse de l'API
       et retourne un DataFrame pandas des données
    """
    dico = dict()

    list_dict = []
    nb_elem = len(element_list)
    for i in range(0, nb_elem):
        list_dict.append(get_elem_content(element_list[i]))

    list_GID = []
    for i in range(0, nb_elem):
        dico = list_dict[i]
        list_GID.append(dico['GID'])

    return pd.DataFrame(list_dict, index=list_GID)



# --------------- WFS --------------- #

def get_data_wfs(tp):
    """
       Cette fonction prend en argument une chaine de caractere desigant l'identifiant 
       (wfs.contents) des donnees a recuperer, effectue les requetes sur l'API WFS, parse 
       la reponse et retourne une liste d'elements etree.
    """
    wfs = WebFeatureService(url_wfs, version=vrsn)
    response = wfs.getfeature(typename=tp)
    s = response.getvalue()
    filename = make_file(tp, s)

    tree = etree.parse(filename)
    element_list = tree.xpath('//*[local-name()="FeatureCollection"]/*[local-name()="featureMember"]')
    
    return element_list
    

# --------------- WPS --------------- #  


def get_data_wps(tp):
    """
       Prend en parametre un identifiant des donnes de lapi de bordeaux metropole. Cette fonction effectue un requetes au serveur WPS, la parse et retourne une list d'element etre
    """
    playload = {'key': 'GVY1ZR3Y0B', 
            'Service': 'wps', 
            'request': 'Execute', 
            'Identifier': tp, 
            'version': '1.0.0',}

    r = requests.get(url_wps, params=playload)
    s = r.content
    filename = make_file(tp, s)

    tree = etree.parse(filename)

    element_list = tree.xpath('//*[local-name()="ExecuteResponse"]/*[local-name()="ProcessOutputs"]/*[local-name()="Output"]')

    return element_list



# def get_data_wps(tp):
#     """
#        Cette fonction prend en argument une chaine de caractere desigant l'identifiant 
#        (wfs.contents) des donnees a recuperer et construit une liste de dictionnaires 
#        les contenants et la retourne.
#     """
#     wfs = WebFeatureService(url_wfs, version=vrsn)
#     response = wfs.getfeature(typename=tp)
#     s = response.getvalue()
#     filename = make_file(tp, s)

#     tree = etree.parse(filename)
#     element_list = tree.xpath('//*[local-name()="FeatureCollection"]/*[local-name()="featureMember"]')
#     nb_elem = len(element_list)

#     list_dict = []
#     for i in range(0, nb_elem):
#         list_dict.append(get_elem_content(element_list[i]))
        
#     return list_dict
    
 
   
# END
