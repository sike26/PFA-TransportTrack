import os
from project import server
from project import db
from project.libraries.database import init_db

if __name__ == '__main__':
    print "initialisation de la base de donnee"
    init_db(panne_detection=True)
    print "serveur :", db
    port = int(os.environ.get("PORT", 8000))
    server.run('0.0.0.0', port=port)
