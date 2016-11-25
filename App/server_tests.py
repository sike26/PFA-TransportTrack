import os
from project import server
from project import db

from project.libraries import database
from project.models.user import User
from project.models.path import Path
from project.models.subPath import SubPath
from project.models.transportStop import TransportStop
import unittest
import tempfile
import sys
import json
import project.controllers.paths
import project.controllers.login
import project.controllers.user

class ServerTestCase(unittest.TestCase):


    def setUp(self):
        server.config['TESTING'] = True
        self.app = server.test_client()
        database.init_db()



    def tearDown(self):
        database.del_db()



    def login(self, email, password):
        return self.app.get('/users/login', data=json.dumps(dict(email=email, password=password)), content_type="application/json")



    def logout(self):
        return self.app.get('/users/logout')



    def test_getUser(self):

        p = User(1, 'Perceval', 'De Galle', 'Perceval@grall.com', 'sloubi', paths='')
        db.session.add(p)
        db.session.commit()

        rv = self.app.get('/users/1')
        assert "401 Unauthorized" in rv.data

        self.login('Perceval@grall.com', 'sloubi')

        rv = self.app.get('/users/1')

        assert '{"email": "Perceval@grall.com", "firstName": "Perceval", "id": 1, "lastName": "De Galle", "password": "sloubi"}' in rv.data

        rv = self.app.get('/users/2')
        assert "404 Not Found" in rv.data

        p2 = User(2, 'Karadoc', 'De Vanne', 'Karadoc@grall.com', 'jambon', paths='')
        db.session.add(p2)
        db.session.commit()

        rv = self.app.get('/users/2')
        assert "403 Forbidden" in rv.data



    def test_delUser(self):

        p = User(1, 'Perceval', 'De Galle', 'Perceval@grall.com', 'sloubi', paths='')
        db.session.add(p)
        db.session.commit()

        self.login('Perceval@grall.com', 'sloubi')
        rv = self.app.delete('/users/1')

        assert 'User Perceval@grall.com deleted' in rv.data

        rv = self.app.get('/users/1')
        assert "404 Not Found" in rv.data or "401 Unauthorized" in rv.data

        p2 = User(2, 'Karadoc', 'De Vanne', 'Karadoc@grall.com', 'jambon', paths='')
        db.session.add(p2)
        db.session.commit()

        rv = self.app.delete('/users/2')
        assert "401 Unauthorized" in rv.data



    def test_creatUser(self):

        p = User(1, 'Perceval', 'De Galle', 'Perceval@grall.com', 'sloubi', paths='')
        db.session.add(p)
        db.session.commit()

        rv = self.app.post('/users', data=json.dumps(dict(id=2, firstName='Bohort', lastName='Lejeune', email='Bohort@mecrean.fr', password='gaune', paths=' ')), content_type="application/json")
        assert 'Sucess' in rv.data
        self.login('Bohort@mecrean.fr', 'gaune')

        rv = self.app.get('/users/2')
        assert '{"email": "Bohort@mecrean.fr", "firstName": "Bohort", "id": 2, "lastName": "Lejeune", "password": "gaune"}' in rv.data

        rv = self.app.post('/users', data=json.dumps(dict(id=2, firstName='Bohort', lastName='Lejeune', email='Bohort@mecrean.fr', password='gaune', paths=' ')))
        assert  'User already exist' in rv.data



    def test_getPath(self):

        p = User(1, 'Perceval', 'De Galle', 'Perceval@grall.com', 'sloubi', paths='')
        db.session.add(p)
        db.session.commit()
        self.login('Perceval@grall.com', 'sloubi')

        R = TransportStop('ROUSTAING', 1, 'TRAM')
        V1 = TransportStop('VICTOIRE', 1, 'TRAM')
        V2 = TransportStop('VICTOIRE', 101, 'BUS')
        A = TransportStop('AEROPORT', 101, 'BUS')

        db.session.add(R)
        db.session.add(V1)
        db.session.add(V2)
        db.session.add(A)
        db.session.commit()

        subpath1 = SubPath(1, "TEST DIRECTION", R, V1)
        subpath2 = SubPath(101, "TEST DIRECTION", V2, A)

        db.session.add(subpath1)
        db.session.add(subpath2)
        db.session.commit()

        P = Path(1, 1, True, 1, 7, 10, [subpath1, subpath2])
        db.session.add(P)
        db.session.commit()

        subpath3 = SubPath(1, "TEST DIRECTION", R, V1)
        subpath4 = SubPath(101, "TEST DIRECTION", V2, A)
        db.session.add(subpath3)
        db.session.add(subpath4)
        db.session.commit()

        P2 = Path(2, 2, True, 1, 7, 10, [subpath3, subpath4])
        db.session.add(P2)
        db.session.commit()

        rv = self.app.get('/paths/3')
        assert "404 Not Found" in rv.data

        rv = self.app.get('/paths/2')
        assert "403 Forbidden" in rv.data

        rv = self.app.get('/paths/1')



    def test_delPath(self):
        p = User(1, 'Perceval', 'De Galle', 'Perceval@grall.com', 'sloubi', paths='')
        db.session.add(p)
        db.session.commit()
        self.login('Perceval@grall.com', 'sloubi')

        R = TransportStop('ROUSTAING', 1, 'TRAM')
        V1 = TransportStop('VICTOIRE', 1, 'TRAM')
        V2 = TransportStop('VICTOIRE', 101, 'BUS')
        A = TransportStop('AEROPORT', 101, 'BUS')

        db.session.add(R)
        db.session.add(V1)
        db.session.add(V2)
        db.session.add(A)
        db.session.commit()

        subpath1 = SubPath(1, "TEST DIRECTION", R, V1)
        subpath2 = SubPath(101, "TEST DIRECTION", V2, A)

        db.session.add(subpath1)
        db.session.add(subpath2)
        db.session.commit()

        P = Path(1, 1, True, 1, 7, 10, [subpath1, subpath2])
        db.session.add(P)
        db.session.commit()

        rv = self.app.delete('paths/1')
        assert 'Success' in rv.data

        rv = self.app.get('/paths/1')
        assert "404 Not Found" in rv.data



    def test_creatPath(self):
        p = User(1, 'Perceval', 'De Galle', 'Perceval@grall.com', 'sloubi', paths='')
        db.session.add(p)
        db.session.commit()
        self.login('Perceval@grall.com', 'sloubi')

        R = TransportStop('ROUSTAING', 1, 'TRAM')
        V1 = TransportStop('VICTOIRE', 1, 'TRAM')
        V2 = TransportStop('VICTOIRE', 101, 'BUS')
        A = TransportStop('AEROPORT', 101, 'BUS')

        subpath1 = SubPath(1, "TEST DIRECTION", R, V1)
        subpath2 = SubPath(101, "TEST DIRECTION", V2, A)

        P = Path(1, 1, True, 1, 7, 10, [subpath1, subpath2])
        rv = self.app.post('/paths', data=json.dumps(P.to_json()), content_type="application/json")
        assert "success, new path created" in rv.data

        rv = self.app.get('/paths/1')



    def test_updateUser(self):
        p = User(1, 'Perceval', 'De Galle', 'Perceval@grall.com', 'sloubi', paths='')
        db.session.add(p)
        db.session.commit()
        self.login('Perceval@grall.com', 'sloubi')

        self.app.put('/users/1',  data=json.dumps(dict(id=1, firstName='Bohort', lastName='Lejeune', email='Bohort@mecrean.fr', password='gaune', paths=' ')), content_type="application/json")

        rv = self.app.get('/users/1')
        assert '{"email": "Bohort@mecrean.fr", "firstName": "Bohort", "id": 1, "lastName": "Lejeune", "password": "gaune"}' in rv.data




    def test_updatePath(self):
        p = User(1, 'Perceval', 'De Galle', 'Perceval@grall.com', 'sloubi', paths='')
        db.session.add(p)
        db.session.commit()
        self.login('Perceval@grall.com', 'sloubi')

        R = TransportStop('ROUSTAING', 1, 'TRAM')
        V1 = TransportStop('VICTOIRE', 1, 'TRAM')
        V2 = TransportStop('VICTOIRE', 101, 'BUS')
        A = TransportStop('AEROPORT', 101, 'BUS')

        db.session.add(R)
        db.session.add(V1)
        db.session.add(V2)
        db.session.add(A)
        db.session.commit()

        subpath1 = SubPath(1, "TEST DIRECTION", R, V1)
        subpath2 = SubPath(101, "TEST DIRECTION", V2, A)

        db.session.add(subpath1)
        db.session.add(subpath2)
        db.session.commit()

        P = Path(1, 1, True, 1, 7, 10, [subpath1, subpath2])
        db.session.add(P)
        db.session.commit()

        A2 = TransportStop('AEROPORT', 12225, 'BUS')
        C = TransportStop('CAP', 12225, 'BUS')
        subpath3 = SubPath(12225, "TEST DIRECTION", A2, C)

        update_P = Path(1, 1, True, 1, 7, 10, [subpath1, subpath2, subpath3])
        rv = self.app.put('/paths/1', data=json.dumps(update_P.to_json()), content_type="application/json")
        assert "Success" in rv.data



    def test_getUserPaths(self):

        p = User(1, 'Perceval', 'De Galle', 'Perceval@grall.com', 'sloubi', paths='')
        db.session.add(p)
        db.session.commit()
        self.login('Perceval@grall.com', 'sloubi')

        R = TransportStop('ROUSTAING', 1, 'TRAM')
        V1 = TransportStop('VICTOIRE', 1, 'TRAM')
        V2 = TransportStop('VICTOIRE', 101, 'BUS')
        A = TransportStop('AEROPORT', 101, 'BUS')

        db.session.add(R)
        db.session.add(V1)
        db.session.add(V2)
        db.session.add(A)
        db.session.commit()

        subpath1 = SubPath(1, "TEST DIRECTION", R, V1)
        subpath2 = SubPath(101, "TEST DIRECTION", V2, A)

        db.session.add(subpath1)
        db.session.add(subpath2)
        db.session.commit()

        P = Path(1, 1, True, 1, 7, 10, [subpath1, subpath2])
        db.session.add(P)
        db.session.commit()

        A2 = TransportStop('AEROPORT', 12225, 'BUS')
        C = TransportStop('CAP', 12225, 'BUS')
        subpath3 = SubPath(12225, "TEST DIRECTION", A2, C)

        P2 = Path(2, 1, True, 1, 7, 10, [subpath3])
        db.session.add(subpath3)
        db.session.add(P2)
        db.session.commit()

        rv = self.app.get('/users/1/paths')
        # print rv.data


if __name__ == '__main__':
    unittest.main()
