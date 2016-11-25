import os
from project import server
from project import celery
from project import db
from project.libraries.database import init_db

if __name__ == '__main__':

    with server.app_context():
        init_db(panne_detection=True)
        celery.start()
