import math
import os.path
import numpy as np

from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn import svm
from pattern.fr import tokenize
from ..Collecte.tweets_tbc import Tweet
import re



regexp1 = "(" + "depart" + " '*?'" + " : " + "\d{1,2}h\d{1,2} " + "non assure." + ")"
regexp2 = "(" + "prochain depart" + " = " + "\d{1,2}h\d{1,2}" + ")"

reg1 = re.compile(regexp1, re.IGNORECASE)
reg2 = re.compile(regexp2, re.IGNORECASE)



def list_to_string(l):
    """
    /**
    * Convert a list of String in a String
    * @Name : list_to_string
    * @Param : list on sting - a list of word result of split()
    * @Return: String - the reserve operation to split()
    **/
    """
    s = ""
    for w in l:
        if len(s) == 0:
            s = w
        else:
            s = s + " " + w
    return s



def is_int(s):
    """
    /**
    * Is the string pass in parameter represent an int ?
    * @Name : is_int
    * @Param : String - a String
    * @Return: boolean - True if ths string represent an int, else False
    **/
    """
    try:
        int(s)
        return True
    except:
        return False




class Classifier(object):
    
    data_file = [
        './learn2/TRAM/NonPertinant.learn',
        './learn2/TRAM/Panne.learn',
        './learn2/TRAM/Reprise.learn',
        './learn2/TRAM/Ralentissement.learn'
    ]
    
    data_file_bus = [
        './learn2/BUS/NonPertinant.learn',
        './learn2/BUS/Reprise.learn',
        './learn2/BUS/Ralentissement.learn'
    ]
    
    y = np.array(['NONPERTINANT', 'PANNE', 'REPRISE', 'RALENTISSEMENT'])
    y_bus = np.array(['NONPERTINANT', 'REPRISE', 'RALENTISSEMENT'])

    def __init__(self, transport='TRAM'):
        self.transport = transport
        self.corpus = self.get_corpus()
        self.default_clf = self.learn_bayes()
        

    def get_corpus(self):
        """
        /**
        * get the learning data set
        * @Name : get_corpus 
        * @Param : void
        * @Return: list - return the learning data set 
        **/
        """
        corpus = []
        path_learn_dirname = os.path.dirname(os.path.realpath(__file__))
        data = []
        if self.transport == 'TRAM':
            data = self.data_file
        elif self.transport == 'BUS':
            data = self.data_file_bus
        else:
            print "Ce transport n'est pas pris en charge"

        # print data
        # print self.y

        for filename in data:
            with open(os.path.join(path_learn_dirname, filename), 'rb') as f:
                corpus.append(f.read())
            
        return corpus

    
    
        
    def learn_bayes(self):
        """
        /**
        * Train the bayes classifier
        * @Name : learn_bayes
        * @Return: void
        **/
        """
        tweet_clf = Pipeline([('vect', CountVectorizer()),
                              ('tfidf', TfidfTransformer()),
                              ('clf', MultinomialNB()),])
        if  self.transport == 'TRAM':
            return tweet_clf.fit(self.corpus, self.y)
        elif self.transport == 'BUS':
            return tweet_clf.fit(self.corpus, self.y_bus)


    def learn_SVM(self):
        """
        /**
        * Train the SVM classifier
        * @Name : learn_SVM
        * @Return: void
        **/
        """
        tweet_clf = Pipeline([('vect', CountVectorizer()),
                              ('tfidf', TfidfTransformer()),
                              ('clf', svm.SVC()),])
        
        if  self.transport == 'TRAM':
            return tweet_clf.fit(self.corpus, self.y)
        elif self.transport == 'BUS':
            return tweet_clf.fit(self.corpus, self.y_bus)


    def get_class(self, s, tweet_clf, predict=False):
        """
        /**
        * CLass the tweet s with the classifier pass parameter
        * @Name : get_class 
        * @Param : String - a Tweet content
        * @Param : Fonction - a classifier
        * @Param : boolean - defalt False
        * @Return: String - return the class of the string using the classifier. If predict is True, return also probabilities 
        **/
        """
        if predict:
            print "probability :",tweet_clf.predict_proba([s])[0]

        if len(s) <= 3:
            return 'NONPERTINANT'
        elif self.transport == 'BUS':
            if reg1.search(s) or reg1.search(s):
                return 'RALENTISSEMENT'
            else:
                return tweet_clf.predict([s])[0]
        else:
            return tweet_clf.predict([s])[0]





class TweetTreatment(Tweet):

    tram = ['tbc trama', 'tbc tramb', 'tbc tramc']
    
    def __init__(self, tweet, predict=False):
        super(TweetTreatment, self).__init__(tweet.date, tweet.source, tweet.user, tweet.content, tweet.id)
        if self.source.lower() in self.tram:
            self.clf = Classifier('TRAM')
        else:
            self.clf = Classifier('BUS')
        self.tweet_clf = self.clf.learn_bayes()
        self.contents = self._split_content()
        self.classes = self._set_class(predict)


    def _clean_tokens(self, s_tok):
        """
        /**
        * Clean the string, delete # and links
        * @Name : _clean_tokens
        * @Param : String list - A list of string 
        * @Return: String  list 
        **/
        """
        for i in range(0, len(s_tok)):
            l = s_tok[i]
            t = l.split()
            to_remove = []
            for w in t:
                if w[0] == '#' or w[0] == '@':
                    to_remove.append(w)
                elif len(w) > 4 and w[:4] == "http":
                    to_remove.append(w)
            for w in to_remove:
                t.remove(w)
            
            s_tok[i] = list_to_string(t)

        # print s_tok

        return s_tok
        

    def _split_content(self):
        """
        Seprare le contenue du tweet en plusieurs partie correspondant a des phrases. Il supprime 
        egalement les hastags et les liens present dans le tweet. 

        Par exemple, "Tram A interrompu entre Roustaing et St Nicolas. Reprise dans la soiree. #tramb #tbc"
        deviens : ["Tram A interrompu entre Roustaing et St Nicolas", "Reprise dans la soiree"]
        """

        s_tok = tokenize(self.content, punctuation=".,;:!?()[]{}`''\"@$^&*+-|=~_", replace={})
        s_tok = self._clean_tokens(s_tok)
            
        to_remove = []
        for i in range(0, len(s_tok)):
            tokens = s_tok[i].split()
            for j in range(0, len(tokens)):
                t = tokens[j]
                if not is_int(t[0]):
                    tokens[j] = t.replace('/', ' ')
            
            s_tok[i] = list_to_string(tokens)
            if len(s_tok[i]) == 0:
                    s_tok.remove(s_tok[i])
                    i -= 1
        
        if self.clf.transport == 'TRAM':
            return s_tok
        else:
            return [list_to_string(s_tok)]

    

    def _set_class(self, predict=False):
        """
        Classe chaque partie du contenue d'un tweet.
        """
        classes = []
        for s in self.contents:
            classes.append(self.clf.get_class(s, self.tweet_clf, predict))
        return classes
    
            
