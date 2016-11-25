from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, DateTime, Text, Table
from sqlalchemy.orm import relationship
from project import db
import transportStop

class Disturbance(db.Model):

    __table__name = 'disturbance'
    id = Column(Integer, primary_key=True)
    state = Column(String(20))
    classType = Column(String(20))
    date = Column(DateTime)
    direction = Column(Integer)
    treated = Column(Boolean)
    line = Column(Integer)
    stops = relationship('TransportStop', lazy='dynamic')


    def __init__(self, state, classType, line, date, direction, treated, stops=[]):
        self.state = state
        self.classType = classType
        self.line = line
        self.stops = stops
        self.date = date
        self.direction = direction
        self.treated = treated


    def to_json(self):
        return dict(state=self.state,
                    classType=self.classType,
                    line=self.line,
                    stops=map(lambda s: s.to_json(), self.stops),
                    date=self.date,
                    direction=self.direction,
                    treated=self.treated
        )
