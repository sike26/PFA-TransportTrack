from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, DateTime, Text, Table
from sqlalchemy.orm import relationship
from project import db
import subPath, transportStop

class Path(db.Model):

    __tablename__ = 'path'
    id = Column(Integer, primary_key=True)
    userId = Column(Integer, ForeignKey('user.id'))
    active = Column(Boolean)
    day = Column(Integer)
    beginHour = Column(Integer)
    endHour = Column(Integer)
    tokenDevice = Column(Integer)
    subpaths = relationship('SubPath', lazy='dynamic')


    def __init__(self, id, userId, active, day, beginHour, endHour, subpaths=None, tokenDevice="unknow"):
        self.id = id
        self.userId = userId
        self.active = active
        self.day = day
        self.beginHour = beginHour
        self.endHour = endHour
        self.tokenDevice = tokenDevice
        self.subpaths = subpaths


    def to_json(self):
        return dict(id=self.id,
                    userId=self.userId,
                    active=self.active,
                    day=self.day,
                    beginHour=self.beginHour,
                    endHour=self.endHour,
                    tokenDevice="",
                    subpaths=map(lambda s: s.to_json(), self.subpaths)
        )
