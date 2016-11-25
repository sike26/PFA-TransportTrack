from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, DateTime, Text, Table
from sqlalchemy.orm import relationship
from project import db
import disturbance

class TransportStop(db.Model):

    __tablename__ = 'transportstop'
    id = Column(Integer, primary_key=True)
    name = Column(String(20))
    line = Column(Integer)
    typeTransport = Column(String(5))
    disturbanceId = Column(Integer, ForeignKey('disturbance.id'))

    def __init__(self, name, line, typeTransport='TRAM'):
        self.name = name
        self.line = line
        self.typeTransport = typeTransport


    def to_json(self):
        return dict(name=self.name,
                    line=self.line,
                    typeTransport=self.typeTransport
        )
