from Collecte.tweets_tbc import Tweet
from Detection.Detection import TweetTreatment
from Traitement.extract import Extract
import datetime


class Disturbance(object):
    
    def __init__(self, tweet, state='PROGRESS', class_type='Unknow', line='Unknow', interval='Unknow', date_start='Unknow', duration='Unknow', direction='Unknow'):
        self.tweet = tweet
        self.state = state  # "PROGESS", "LATER", "PAST"
        self.class_type = class_type
        self.line = line
        self.interval = interval
        self.date_start = date_start
        self.duration = duration
        self.direction = direction


    def extract_all(self):
        """
        Effectue tout les traitement sur un tweet (classification et extraction)
        """
        now = datetime.datetime.now()
        list_tweet = self._split_tweet()

        list_disturbance = []
        for t, class_t in list_tweet:

            self.class_type = class_t
            extract = Extract(t.content)
            
            # ARRETS
            self.interval = extract.get_arrets()

            # DATETIME
            self.date_start = extract.get_datetime()
            if len(self.date_start) == 0:
                self.date_start.append([now, 0])
            # SOURCE
            if t.source != "Hootsuite":
                self.line = t.source
            else:
                self.type_class = "NONPERTINANT" 
                
            # STATE
            if self.date_start != []:
            # pour le moment, aucune prise en compte du parametre error
                if self.date_start[0][0] > now:
                    self.state = "LATER"
                elif self.date_start[0][0] <= now:
                    self.state = "PROGRESS"
                    
                else:
                    self.date_start = [now, 0]
                    
            # ARRETS
            if len(self.interval) <= 1:
                token = self.tweet.content.split()
                for i in range(0, len(token)):
                    token[i] = token[i].lower()
                if extract._is_in_lev("antennes", token):
                    self.interval.extend(self._antenne_trad())
            
            self.direction = extract.get_direction(self.line, self.interval)
            
            d = Disturbance(t, self.state, self.class_type, self.line, self.interval, self.date_start, self.duration, self.direction)
            list_disturbance.extend(self._split_disturbance(d))

        return list_disturbance
        
        
    def _antenne_trad(self):

        if self.line == "TBC TramA":
            return ["FLOIRAC DRAVEMONT", "LA GARDETTE"]
        elif self.line == "TBC TramB":
            return ["FRANCE ALOUETTE", "PESSAC CENTRE"]


    def _split_tweet(self):
        """
        Split un tweet traite (ie decoupe en phrase) en 2 tweets
        """
        list_tweet = []
        tweet_t = TweetTreatment(self.tweet)

        for i in range(0, len(tweet_t.contents)):
            t = Tweet(tweet_t.date, tweet_t.source, tweet_t.user, tweet_t.contents[i], tweet_t.id)
            list_tweet.append([t, tweet_t.classes[i]])

        return list_tweet


    def _split_disturbance(self, d):
        """
        Split les disturbances qu'il possedes plusieurs dates de debut.
        """
        list_disturbance = []
        if len(d.date_start) > 0:
            for i in range(0, len(d.date_start)):
                dis = Disturbance(d.tweet, d.state, d.class_type, d.line, d.interval, d.date_start[i], d.duration, d.direction)
                list_disturbance.append(dis)
        else:
            list_disturbance.append(d)

        return list_disturbance
