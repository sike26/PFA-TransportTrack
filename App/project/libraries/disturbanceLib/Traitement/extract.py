import os.path
from pattern.fr import parse, split
from pattern.fr import parsetree
from pattern.search import search, taxonomy
from pattern.fr import ngrams, tokenize
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
import unicodedata
from timex import *
from spell_checker import SpellChecker




def suppr_ret_char(s):
    if s[len(s)-1] == '\n':
        return s[:len(s)-1]
    else:
        return s


class Extract(object):
    """
    Cette classe permet de extraire certaines les entitees nommes comme les nom d'arrets dans un tweet.
    """
    lexique = {'arrets': "lexique/arrets.txt"} 
    

    def __init__(self, s):
        Sc = SpellChecker()
        self.s = Sc.corrections(s)
        self.Lex_learn = dict()
        self.Lex_arret = list()
        self._read_lexique()
        self.clf = self._learn_arret()



    def _read_lexique(self):
        """
        Cette methode lit les fichier de la variable lexique et les stockent dans le dictionnaire Lex_learn. 
        Ce dictionnaire sert, en autre, comme donnees d'apprentissage pour les divers algorithmes de machin 
        learning
        """
        path_learn_dirname = os.path.dirname(os.path.realpath(__file__))
        for k in self.lexique.keys():
            with open(os.path.join(path_learn_dirname, self.lexique[k]), 'rb') as f:
                lines = f.readlines()
                self.Lex_learn[k] = lines
        


    def _learn_arret(self):
        """
        Cette methode creer un classifier de type Naive Bayes et le nouri des donnees des arrets. Ce classifier 
        sert a reconnaitre le nom des arrets.
        """
        arrets = self.Lex_learn['arrets']
        # represente les categories possibles de la classification 
        y = []
        # Represente les donnees d'apprentissage relatives a chaque categories
        corpus = []
        for l in arrets:
            l_split = l.split('|')
            y.append(l_split[0])
            if len(l_split[0]) == len(l):
                corpus.append(l_split[0])
                #corpus.append("")
            else:
                s = l_split[1]
                corpus.append(s)
                
        tweet_clf = Pipeline([('vect', CountVectorizer()),
                              ('tfidf', TfidfTransformer()),
                              ('clf', MultinomialNB()),])
        
        for i in range(0,len(y)):
                y[i] = suppr_ret_char(y[i])
        self.Lex_arret = y

        return tweet_clf.fit(corpus, y)
        


    def _to_tbc_arret(self, s):
        """
        Convertie, le nom de arrets trouve dans un tweet en un nom arrets "officiel".
        Par exemple :
        le nom d'arret "B. flot" (trouve dans un tweet) et le convertie en "BASSINS A FLOT" 
        """
        return self.clf.predict([s])[0], self.clf.predict_proba([s]).max()



    def _lev_distance(self, str1, str2):
        """
        Calcule la Distance de Levenshtein entre 2 chaines de caracteres
        """
        m = len(str1) 
        n = len(str2) 
        lensum = float(m + n)
    
        d = []           
        # D est une matrice de dimension n * m
        for i in range(m+1):
            d.append([i])        
        del d[0][0]    
        for j in range(n+1):
            d[0].append(j) 
      
        for j in range(1,n+1):
            for i in range(1,m+1):
                if str1[i-1] == str2[j-1]:
                    d[i].insert(j,d[i-1][j-1])           
                else:
                    minimum = min(d[i-1][j]+1, d[i][j-1]+1, d[i-1][j-1]+2)         
                    d[i].insert(j, minimum)

        ldist = d[-1][-1]
        ratio = (lensum - ldist)/lensum

        return {'distance':ldist, 'ratio':ratio}



    def _is_in_lev(self, s, L): 
        """
        Retourne vrai si dans la liste L il existe une chaine de caractere dont dont la distance de Levenshtein 
        est inferieur a un certain seuil (0.90%)
        """
        for i in range(0, len(L)):
            l = L[i]
            if self._lev_distance(s, l)['ratio'] > 0.90:
                return i
                    
        return False


    def _is_neighbour(self, w1, w2):
        tok = tokenize(self.s, punctuation=".,;:!?()[]{}@$^&*+-|=~_", replace={})
        l_split = tok[0].split()
        try:
            i = l_split.index(w1)
            j = l_split.index(w2)
        except:
            # print "No such item"
            i = 0
            j = 0

        if i == j-1:
            return True
        else:
            return False


    def get_arrets(self):
        """
        Cette methode prend en parametre une chaine de caractere et retourne, s'il y en a, le nom des arrets 
        """
        # initialisation
        stop_found = []
        irrelevent = ['GARE', 'SAINT', 'SAINTE']
        accepted_tags = ['NN', 'NNP', 'NNS']
        stop = self.Lex_learn['arrets']
        tax = []


        # apprentissage du lexique des arrets
        for l in stop:
            l_split = l.split('|')
            tax.append(l_split[0])
            if len(l_split[0]) == len(l):
                tax.append(l_split[0])
            else:
                tax.append(l_split[0])
                tax.extend(l_split[1].split(','))
        for a in tax:
            a = suppr_ret_char(a)
            taxonomy.append(a, type='ARRET')
            

        # recherche des mots cles dans le tweet (self.s)
        s = self.s
        t = parsetree(s)
        s = search('ARRET', t)
        stop_found = []
        for m in s:
            for w in m.words:
                if w.tag in accepted_tags and len(w.string) > 2 and not w.string.upper() in irrelevent:
                    stop_found.append(w.string)
                elif self._is_in_lev(w.string.upper(), self.Lex_arret):
                    stop_found.append(w.string)
        

        # recherche des arrets composes 
        # pas encore fonctionel
        to_remove = []
        compound_found = []
        for i in range(0, len(stop_found)):
            for j in range(i, len(stop_found)):
                if self._is_neighbour(stop_found[i], stop_found[j]):
                    w_compound = stop_found[i] + " " + stop_found[j]
                    compound_found.append(w_compound)
                    to_remove.append(stop_found[i])
                    to_remove.append(stop_found[j])
                    
        stop_found.extend(compound_found)
        to_remove = list(set(to_remove))

        for w in to_remove:
            stop_found.remove(w)


        # traduction des arrets trouves en arrets reels
        for i in range(0, len(stop_found)):
            stop_found[i] = self._to_tbc_arret(stop_found[i])[0]
            

        # suppression des arrets non coherents
        try:
            stop_found.remove('AAAA')
            return list(set(stop_found))
        except:
            return list(set(stop_found))
            

    def get_datetime(self):
        """
        Repere les donnes temporelle dans la chaine s et retourne une clsse datetime.
        """
        ex = ExtractTime()
        s = unicodedata.normalize('NFD', self.s).encode('ascii', 'ignore')
        s_tag = ex.tag(s)
        return ex.extract_time(s_tag)
        
        

    def get_direction(self, line, stops):
        """
        Essaye de determiner la ou les directions qui sont affectee par une/un panne/ralentissement/reprise.
        
        sens 0: tram A : Le Haillan/Rostand --->  La Gardette/Floirac Dravemont
        sens 1: tram A : La Gardette/Floirac Dravemont ---> Le Haillan/Rostand

        sens 0: tram B : Pessac Centre / France Alouette ---> Berge Garonne
        sens 1: tram B : Berge Garonne ---> Pessac Centre / France Alouette 

        sens 0: tram C : Lycee Valclv Havel ---> Parc des Expo
        sens 1: tram C : Parc des Expo ---> Lycee Valclv Havel
        
        sens 2: les 2 sens
        """
        hashstop = {'TBC TramA': {'LE HAILLAN ROSTAND': 1,
                                  'LA GARDETTE': 0,
                                  'FLOIRAC DRAVEMONT': 0},
                    'TBC TramB': {'BERGE DE LA GARONNE': 0,
                                  'FRANCE ALOUETTE': 1,
                                  'PESSAC CENTRE': 1},
                    'TBC TramC': {'LYCEE VALCAL HAVEL': 1,
                                  'PARC DES EXPOSITIONS': 0,
                                  'NOUVEAU STADE': 0}
        }
        
        if len(stops) == 1:
            try:
                return hashstop[line][stops[0]]
            except:
                return "Unknow"

        elif len(stops) >= 2:
            try:
                stop_hash = []
                for i in range(0, len(stops)):
                    stop_hash.append(hashstop[line][stops[i]])
                for i in range(0, len(stop_hash)):
                    if stop_hash[0] != stop_hash[i]:
                        return "Unknow"
                return stop_hash[0]
            except:
                return 2
        else:
            return "Unknow"
            


        
