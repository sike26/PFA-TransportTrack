import tweepy
import pandas as pd
import pickle



class Tweet(object):

    def __init__(self, date, source, user, content, id):
        self.date = date
        self.source = source
        self.user = user
        self.content = content
        self.id = id

    

    def get_date(self):
        """
           Retourne la date de post du tweet
        """
        return self.date

        
    def get_source(self):
        """
           Retourne l'auteur du tweet
        """
        return self.source
        

    def get_user(self):
        """
           Retourne le compte sur lequel le tweet a ete poste
        """
        return self.user


    def get_content(self):
        """
           Retourne le message du tweet
        """
        return self.content


    def get_id(self):
        """
           Retourne l'id d'un tweet.
        """
        return self.id

    
    def is_new_tweets(self, dict_tweets):
        """
        Retourne True si le tweet passe en parametre n'est pas dans le dictionnaires des tweets du compte user,
        i.e qu'il est nouveau. Retourne False sinon.
        """
        data = dict_tweets[self.user]
        l = len(data)
        return self.get_id() != data[0].get_id()


    def to_dict(self):
        return {'id': self.id, 'date': self.date, 'source': self.source, 'user': self.user, 'content': self.content}




class TweetCollect(Tweet):
    
    access_token = '197100735-qwhLbS8KcYpcoQ46E69ZV0NT0RVI7kFG7hAhEeOF'
    access_token_secret = 'jWyfyfgvRiuJP9wm3Emed5unoLskWAdIAzAddlm2z4rzJ'
    consumer_key = 'OiOMSvys4Sz4lXvRsCJghg16z'
    consumer_secret = 'xeo9wHedaNBN8labCInxKVfopDqjfssj67gJMqwKk222TKjYrE'
    

    data_tweets = "Data_Tweets"

    Users = ['tbc_trama',
             'tbc_tramb',
             'tbc_tramc',
             'tbc_lianes1',
             'tbc_lianes3',
            'tbc_lianes8']


    def __init__(self):
        self.auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)
        self.auth.set_access_token(self.access_token, self.access_token_secret)
        self.api = tweepy.API(self.auth)
        


    def user_timeline(self, user='tbc_trama', encoding=None, count=200):
        """
        Recupere tout les tweets de l'utilisateur "user" par paquets de "count" (count doit etre inferieur de 200),
        tweets depuis la creation du compte.
        Retourne une liste de tweets, de type tweepy.models.Status definie dans le module tweepy.
        """
        public_tweets = []
        tweets = self.api.user_timeline(user, count=count)
        l = len(tweets)
        public_tweets.extend(tweets)
        id_min = public_tweets[l-1].__dict__['id']

        while len(tweets) > 1:
            id_min = id_min = public_tweets[l-1].__dict__['id']
            tweets = self.api.user_timeline(user, max_id=id_min, count=count)
            public_tweets.extend(tweets)
            l += len(tweets)
 
        return public_tweets
    



    def get_last(self, user, encoding=None, count=1):
        """
           Recupere le dernier tweet de compte user.   
        """
        tweets = self.api.user_timeline(user, encoding, count=count)
        tweet = tweets[0]
        t = Tweet(tweet.created_at, tweet.source, user, tweet.text, tweet.id)
        return t




    def user_timeline_timedtext(self, user='tbc_trama', encoding=None, count=200):
        """
        Recupere tout les tweets de l'utilisateur "user" par paquets de "count" (count doit etre inferieur de 200),
        tweets depuis la creation du compte.
        Retourne une liste de tweets
        """
        public_tweets = self.user_timeline(user, encoding, count)
        for i in range(0, len(public_tweets)):
            tweet = public_tweets[i]
            public_tweets[i] = Tweet(tweet.created_at, tweet.source, user, tweet.text, tweet.id)
        return public_tweets




    def get_all_users_timeline(self, encoding=None, count=200):
        """
        Collecte tout les tweets des comptes users et les stockent dans un dictionnaire de liste de tweets.
        """
        public_tweets = dict()
        dict_tweets = dict()
                    
        for user in self.Users:
            public_tweets = self.user_timeline_timedtext(user, encoding, count)
            # df = pd.DataFrame.from_dict(public_tweets, orient='index')
            dict_tweets[user] = public_tweets
                    
        self.write_dict(dict_tweets)

        return dict_tweets



    def new_tweet(self):
        """
        Parmis les Users, verifie qu'il n'y a pas de nouveau tweets.
        Retourne une liste de dictionaires de la forme :
        """
        dict_update = []
    
        data = self.read_dict()
        for user in self.Users:
            d = dict()
            last = self.get_last(user)
            d['user'] = user
            d['isnew'] = last.is_new_tweets(data)
            dict_update.append(d)

        return dict_update

        

    def write_dict(self, dict_tweets):
        """
        Ecrit l'objet dict_tweets dans un fichier.
        Le nom du ficher est contenue dans la variable data_tweets.
        """
        with open(self.data_tweets, "wb") as f:
            p = pickle.Pickler(f)
            p.dump(dict_tweets)
    

    def read_dict(self):
        """
        Lit le fichier data_tweets et retourne l'objet qu'il contient.
        """
        with open(self.data_tweets, 'rb') as f:
            p = pickle.Unpickler(f)
            data_dict = p.load()
        
        return data_dict


    def read_dict_df(self):
        """
        Lit le fichier data_tweets et retourne l'objet qu'il contient sous forme d'un dataFrame pandas.
        """
        data = self.read_dict()
        data_dict = dict()
        index = []
        for user in self.Users:
            L = data[user]
            for i in range(0, len(L)):
                L[i] = L[i].to_dict()
            data_dict[user] = pd.DataFrame(L)
        
        return data_dict

    def add_tweet_to_data(self, tweet):
        """
        Ajoute le tweet passe en parametre au fichier data_tweets contenant tout les tweets des comptes de 
        la tbc.
        """
        data_dict = self.read_dict()
        user = tweet.get_user()
        data_dict[user].insert(0, tweet)
        self.write_dict(data_dict)
        
