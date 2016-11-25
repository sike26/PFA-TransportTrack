from project import db
from disturbanceLib.Collecte.tweets_tbc import TweetCollect
from project.models.tweet import *

def init_db(panne_detection=False):
    # Creation de la base
    db.create_all()

    # Initialisation pour celery et la recolte des tweets
    if panne_detection:
        collect = TweetCollect()
        first_tweets = collect.last_tweets()
        for t in first_tweets:
            entry = Tweet(t.date, t.source, t.user, t.content, t.id)
            db.session.add(entry)
            db.session.commit()

def del_db():
    db.drop_all()
