from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, DateTime, Text, Table
from sqlalchemy.orm import relationship
from project import db
import transportStop

class SubPath(db.Model):

    __tablename__ = 'subpath'
    id = Column(Integer, primary_key=True)
    line = Column(Integer)
    direction = Column(String(50))
    pathId = Column(Integer, ForeignKey('path.id'))
    startId = Column(Integer, ForeignKey('transportstop.id'))
    transportStopStart = relationship('TransportStop', foreign_keys="SubPath.startId")
    finishId = Column(Integer, ForeignKey('transportstop.id'))
    transportStopFinish = relationship('TransportStop', foreign_keys="SubPath.finishId")


    def __init__(self, line, direction, transportStopStart, transportStopFinish):
        self.line = line
        self.direction = direction
        self.transportStopStart = transportStopStart
        self.transportStopFinish = transportStopFinish


    def to_json(self):
        return dict(line=self.line,
                    direction=self.direction,
                    startStop=self.transportStopStart.to_json(),
                    finishStop=self.transportStopFinish.to_json(),
        )
