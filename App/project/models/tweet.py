from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, DateTime, Text, Table
from sqlalchemy.orm import relationship
from project import db
import disturbance

correspond_table = Table('correspond', db.metadata,
                         Column('tweetId', Integer, ForeignKey('tweet.id')),
                         Column('disturbanceId', Integer, ForeignKey('disturbance.id'))
)

class Tweet(db.Model):

    __table__name = 'tweet'
    id = Column(Integer, primary_key=True)
    date = Column(DateTime)
    source = Column(String(20))
    user = Column(String(20))
    content = Column(Text)
    disturbances = relationship('Disturbance', secondary=correspond_table)

    def __init__(self, date, source, user, content, tweet_id, disturbances=[]):
        self.id = tweet_id
        self.date = date
        self.source = source
        self.user = user
        self.content = content
        self.disturbances = disturbances

    def to_json(self):
        return dict(id=self.id,
                    date=self.date,
                    source=self.source,
                    user=self.user,
                    content=self.content,
                    disturbances=map(lambda s: s.to_json(), self.disturbances)
        )


