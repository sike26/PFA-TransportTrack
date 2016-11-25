from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, DateTime, Text, Table
from project import db
from sqlalchemy.orm import relationship
import path

class User(db.Model):

    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    firstName = Column(String(50))
    lastName = Column(String(50))
    email = Column(String(120), unique=True)
    password = Column(String(10))
    tokenDevice = Column(String(100))
    OS = Column(String(10))
    paths = relationship('Path', lazy='dynamic')

    def __init__(self, id, firstName, lastName, email, password, tokenDevice=None, OS="ANDROID", paths=""):
        self.id = id
        self.firstName = firstName
        self.lastName = lastName
        self.email = email
        self.password = password
        self.tokenDevice = tokenDevice
        self.OS = OS
        self.paths = paths

    def to_json(self):
        return dict(id=self.id,
                    firstName=self.firstName,
                    lastName=self.lastName,
                    email=self.email,
                    password=self.password
        )

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    @property
    def is_authenticated(self):
        return True

    def get_id(self):
            return unicode(self.id)
