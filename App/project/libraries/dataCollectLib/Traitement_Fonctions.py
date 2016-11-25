import pandas as pd
import numpy as np
import time

"""
   Ce fichier contient l'ensemble des fonctions assurant le traitement des donnees recuperees
"""


# Variables Globales



# Fonctions

#TODO Gestion des erreurs (retour d'erreur des protocoles WFS...)
def Dict_to_Data(list_dict):
    """
       Cette fonction tranforme une liste de dictionnaires en un Data_Frame. Index avec le 
       champ GID.
    """
    list_GID = []
    for i in range(0, len(list_dict)):
        list_GID.append(list_dict[i]['GID'])

    return pd.DataFrame(list_dict, index=[list_GID])



def is_nan(s):
    if len(s) == 0:
        return True
    else:
        return False



def is_int(s):
    """
       Retourne True si la chaine passe en parametre est un int, false sinon
       Exemple :

       is_int("2.33") => false
       is_int("33") => true
       is_int("Test") => false
    """
    try:
        int(s)
        return True
    except:
        return False



def is_number(s):
    """
       Retourne True si la chaine passe en parametre est un nombre, false sinon.
       Exemple :
    
       is_number("2.33") => true
       is_number("33") => true
       is_number("Test") => false
    """
    try:
        float(s)
        return True
    except:
        return False



def is_float(s):
    """
       Retourne True si la chaine passe en parametre est un float, false sinon.
       Exemple :

       is_float("2.33") => true
       is_float("33") => false
       is_float("Test") => false
    """
    return (not is_int(s)) and is_number(s)



def is_date(s):
    """
       Retourne True si la chaine est une Date avec le formatage suivant : "2010-08-04T00:00:00",
       False sinon.
       Exemple :

       is_date("2010-08-04T00:00:00") => True
       is_date("2002 02 23 02 03 02") => False
    """
    try:
        time.strptime(s, "%Y-%m-%dT%H:%M:%S")
        return True
    except:
        return False
        


# def to_date(s):
#     """
#        Convertie une Chaine en strut_time celon le formatage suivant "%Y-%m-%dT%H:%M:%S".
#     """
#     return time.strptime(s, "%Y-%m-%dT%H:%M:%S")




def lenght(s):
    """
       Retourne le longueur du premier terme de la chaine s.
       Exemple :

       lenght("Salut Patrick") => 5
       lenght("Salut,Salut 225 5") => 11
    """
    l = len(s)
    if l == 0:
        return 0
    else:
        i = 0
        while i < l and s[i] != " ":
            i += 1
        return i
            


def is_pos(s):
    """
       Retourne True si la chaine s represente des coordonnees sous la forme "latitude longitude", 
       avec latitude et longitude des float.
       Exemple :

       is_pos("1426479 4196958.3400") => False
       is_pos("1426479.3325 4196958.3400") => True
       is_pos("1426479.3325 4196958.3400 123365,2256") => False
    """
    i = lenght(s)
    if is_float(s[:i]) and is_float(s[i+1:]):
        return True
    else:
        return False
    


def to_pos(s):
    """
       Convertie une chaine de caractere en un dictionaire {'latitude' : , 'longitude' : }.
       Si la chaine est vide (ie ""), retourne NaN.
    """
    if len(s) > 0:
        pos = []
        i = lenght(s)
        pos.append(s[:i])
        pos.append(s[i+1:])

        return pos



def is_pos_list_rec(s):
    """
       Appel recursif de la fonction is_pos_list.
    """
    if len(s) > 0:
        i = lenght(s)
        j = lenght(s[i+1:])
        return is_pos(s[:j+i+1]) and is_pos_list_rec(s[j+i+2:])
    else:
        return True



def is_pos_list(s):
    """
       Retourne True si la chaine s represente une suite de coordonnes sous la forme "latitude longitude ..."
       , False sinon.
       Exemple :

       is_pos_list("1425143.410000 1425143.410000 4197945.620000") => False
       is_pos_list("1425143.410000 1425143.410000 4197945.620000 4197945.620000") => True
    """
    if len(s) == 0:
        return False
    else:
        return is_pos_list_rec(s)



def to_pos_list_rec(s, list_dict):
    """
       Appel recursif de la fonction to_pos_list
    """
    if len(s) > 0:
        i = lenght(s)
        j = lenght(s[i+1:])
        dic = []
        dic.append(s[:i])
        dic.append(s[i+1:j+i+1])
        list_dict.append(dic)
        to_pos_list_rec(s[j+i+2:], list_dict)
        
        
        
def to_pos_list(s):
    """
       Prend en arguments une chaine de caractere telle ue  is_pos_list est  True et retourne pour chaque 
       element de la liste, une liste de dictionnaires du type de retour de la fonction to_pos.
       Si la chaine est vide (ie ""), retourne NaN.
       Exemple :

       Entree : "1425143.410000 1425143.410000 4197945.620000 4197945.620000"
       Sortie : [{'latitude': '1425143.410000', 'longitude': '1425143.410000'},
                 {'latitude': '4197945.620000', 'longitude': '4197945.620000'}] 
    """
    if len(s) > 0:
        list_dict = []
        to_pos_list_rec(s, list_dict)
        return list_dict
    


def get_type(s):
    """
       Prend en argument une chaine de caratere s et retourne une chaine designant le type de la donnees 
       ecrite dans la string.
       Si aucun motif n'est trouve, retourne "str"
       Exemple :
    
       get_type("3220") => "int"
       get_type("122203.3332 12223.0222") => pos
    """
    s_type = ""
    if is_int(s):
        s_type= "int"
    elif is_float(s):
        s_type= "float"
    elif is_date(s):
        s_type= "date"
    elif is_pos(s):
        s_type= "pos"
    elif is_pos_list(s):
        s_type= "pos_list"
    elif is_nan(s):
        s_type= "empty"
    else:
        s_type= "str"

    return s_type




def is_empty(df, column):
    """
       Prend en parametre une DataFrame et l'id d'une colonne et retourne True si la colonne ne contient 
       que des chaines de caractere vide, False sinon. 
    """
    col = df[column]
    l = len(df)

    if l > 500:
        L = 100
    else:
        L = 50

    rand_list = np.random.randint(1, l, L)

    for i in rand_list:
        if not is_nan(col[i]):
            return False
            
    len_col = col.map(lambda x: len(x))
    if len_col.sum() == 0:
        return True
    else:
        return False




def get_element(df, column):
    """
       Usage specifique a la fonction get_col_type.
    """
    col = df[column]
    l = len(df)

    len_col = col.map(lambda x: len(x))

    df_tmp = pd.DataFrame(col)
    df_tmp['LENGHT'] = len_col
    return df_tmp.sort_values(by='LENGHT')[column][len(df_tmp)-1]



def get_col_type(df, column):
    """
       Retourne de type de donnees contenue dans les str de la colonne 'column' du DataFrame 'df'.
       Cette fonction retourne le type sous forme d'une str : "int", "float", "date", "pos", 
       "list_pos", "empty".
    """
    col = df[column]
    element = col[0]

    s = get_type(element)

    if (s == "empty") and (not is_empty(df, column)):
            s = get_type(get_element(df,column))
            
    return s



def get_col_of_type(df, t):
    """
       Prend en parametre une DataFrame et une chaine t representant un type ("int", "float", "date", 
       "pos", "list_pos", "empty") et retourne la liste des colonne dont les donnees sont de ce type.
    """
    list_col_of_t = []
    list_col = []

    for col in df:
        list_col.append(col)

    l = len(list_col)
    for i in range(0, l):
        if get_col_type(df, list_col[i]) == t:
            list_col_of_t.append(list_col[i])

    return list_col_of_t




# End
