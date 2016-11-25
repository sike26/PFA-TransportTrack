from project import *
import datetime
from project import models
from project.libraries.graphLib.graphe_tbc import *
from project.libraries.disturbanceLib.Collecte.tweets_tbc import *
from project.libraries.disturbanceLib.Perturbation import *
from project.models.tweet import Tweet
from project.models.disturbance import Disturbance


hash_line = {'tbc_lianes1':1,
             'tbc_li anes3':3,
             'tbc_lianes8': 8,
             'tbc_trama': 59,
             'tbc_tramb': 60,
             'tbc_tramc': 61
}


@celery.task(name='project.libraries.celeryLib.tasks.get_tweets')
def get_tweets():
    """
    /**
    * get last tweets of tbc accounts, treat them and store them in the database.
    * @Name : get_tweet
    * @Param : void
    * @Return: void
    **/
    """
    collect = TweetCollect()
    last_tweets = collect.last_tweets()
    pannes = []
    new_tweets = []

    print db.metadata
    
    for t in last_tweets:
        print t.id
        T = Tweet(t.date, t.source, t.user, t.content, t.id+2)
        if is_new(t):
            # add tweets to the database
            T = Tweet(t.date, t.source, t.user, t.content, t.id)

            # extract disturbances from tweets
            d = Disturbance(t)
            t_disturbances = d.extract_all()
            line = hash_line(disturbance.tweet.user)

            # add disturbances to the database
            for d in t_disturbances:
                D = Disturbance(d.state, d.class_type, line, d.date_start[0], d.direction, False)
                for stop in d.interval:
                    transportStop = TransportStop(stop, d.line)
                    D.stops.append(transportStop)
                T.disturbances.append(D)

            print T.to_json()

            db.session.add(T)
            db.session.commit()

#######################################
# Prendre en comptes les trajet actif #
#######################################
def get_affected_paths():
    """
    /**
    * get all user's path affected from a disturbance
    * @Name : get_affected_paths
    * @Param : void
    * @Return: a list on path (from models)
    **/
    """
    paths = Path.query.all()
    affected_paths = []
    for p in paths:
        if G.is_path_disturb(p):
            affected_paths.append(p)

    return affected_paths


@celery.task(name='tasks.disturb_treatment')
def disturb_treatment():
    """
    /**
    * treat all none treat disturbance on a the database and send notifications to concern users
    * @Name : penguin_first__placement
    * @Param : void
    * @Return: 
    **/
    """
    now = datetime.datetime.now()
    disturbances = get_none_treat_disturbances()
    paths = []
    for d in disturbances:
        if d.date < now:
            affected_stops = G.disturbance_affected_stops(d)
            G.update(affected_stops, d.class_type) # Fonction a definir dans le graphe
            d.update({"trated": True})
    db.session.commit()
    paths = G.get_affected_paths()
    send_notifications(paths)



def is_new(tweet):
    """
    /**
    * the tweet is new ?
    * @Name : is_new
    * @Param : a tweet object (from models) 
    * @Return: if the tweet is not in the database return True, else False 
    **/
    """
    return Tweet.query.filter(Tweet.id == tweet.id).first() is None

def get_none_treat_disturbances():
    return Disturbance.query.filter(Disturbance.treated == False).all()
