import tweepy
import pandas as pd
import pickle



class Tweet(object):
    """
    /**
    * The tweet object.
    * @Name : Tweet
    * @attribute : struct Game * - Game structure
    * @attribute : int - Tweet Id (real ID)
    * @attribute : datetime - Tweet Date 
    * @attribute : String - Tweet source
    * @attribute : String - Tweet user (account name)
    * @attribute : String - Tweet content
    **/
    """
    def __init__(self, date, source, user, content, id):
        self.id = id
        self.date = date
        self.source = source
        self.user = user
        self.content = content

    
    def is_new_tweets(self, last):
        """
        /**
        * The tweet pass to the function is the last one ?.
        * @Name : is_new_tweet
        * @Param : Tweet - a Tweet object
        * @Return: boolean - True if the tweet is the last one, else False
        **/
        """
        return self.data > last.date and self.line == last.line
        


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
        /**
        * Return the count lasts tweet from the user account
        * @Name : user_timeline
        * @Param : String - a tweet account
        * @Param : String - encoding norme, default None
        * @Param : int - nombers of tweet, default 200
        * @Return: a list on Tweet object.
        **/
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
    



    def get_last(self, user, encoding=None):
        """
        /**
        * Return the lasts tweet from the user account
        * @Name : gest_last
        * @Param : String - a tweet account
        * @Param : String - encoding norme, default None
        * @Return: a Tweet object.
        **/ 
        """
        count = 1
        tweets = self.api.user_timeline(user, encoding, count=count)
        tweet = tweets[0]
        t = Tweet(tweet.created_at, tweet.source, user, tweet.text, tweet.id)
        return t




    def user_timeline_timedtext(self, user='tbc_trama', encoding=None, count=200):
        """
        /**
        * Return the count lasts tweet from the user account
        * @Name : user_timeline_timedtext
        * @Param : String - a tweet account
        * @Param : String - encoding norme, default None
        * @Param : int - nombers of tweet, default 200
        * @Return: a list on Tweet object.
        **/
        """
        public_tweets = self.user_timeline(user, encoding, count)
        for i in range(0, len(public_tweets)):
            tweet = public_tweets[i]
            public_tweets[i] = Tweet(tweet.created_at, tweet.source, user, tweet.text, tweet.id)
        return public_tweets




    def get_all_users_timeline(self, encoding=None, count=200):
        """
        /**
        * Return every tweet from the account creation
        * @Name : user_timeline
        * @Param : String - a tweet account
        * @Param : String - encoding norme, default None
        * @Param : int - nombers of tweet per request, max is 200, default 200
        * @Return: a list on Tweet object.
        **/
        """
        public_tweets = dict()
        dict_tweets = dict()
                    
        for user in self.Users:
            public_tweets = self.user_timeline_timedtext(user, encoding, count)
            dict_tweets[user] = public_tweets
                    
        self.write_dict(dict_tweets)

        return dict_tweets



    def last_tweets(self):
        """
        /**
        * Return the count lasts tweet from user's accounts in self.Users
        * @Name : user_timeline
        * @Param : String - a tweet account
        * @Param : String - encoding norme, default None
        * @Param : int - nombers of tweet, default 200
        * @Return: a list on Tweet object.
        **/
        """
        last_tweets = []

        for user in self.Users:
            last = self.get_last(user)
            last_tweets.append(last)

        return last_tweets

        
    def write_file(self):
        """
        Decricated
        """
        d = self.read_dict()
        with open("tweet_content.txt", 'wb') as f:
            for k in d.keys():
                for t in d[k]:
                    s = t.content + "\n"
                    f.write(s)


    def write_dict(self, dict_tweets):
        """
        Decricated
        """
        with open(self.data_tweets, "wb") as f:
            p = pickle.Pickler(f)
            p.dump(dict_tweets)
    

    def read_dict(self):
        """
        Decricated
        """
        with open(self.data_tweets, 'rb') as f:
            p = pickle.Unpickler(f)
            data_dict = p.load()
        
        return data_dict


    def read_dict_df(self):
        """
        Decricated
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
        Decrecated
        """
        data_dict = self.read_dict()
        user = tweet.get_user()
        data_dict[user].insert(0, tweet)
        self.write_dict(data_dict)
        
