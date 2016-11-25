from project import *
from project.models.user import User
from project.models.path import Path
from project.models.subPath import SubPath
from project.models.transportStop import TransportStop
from login import *
from flask import json



@server.route('/paths/<int:pathId>', methods=['GET', 'DELETE', 'PUT'])
@login_required
def path(pathId):

    permission = ManagePathPermission(pathId)
    p = Path.query.filter(Path.id == pathId).first()
    # Path doesn't exist
    if p is None:
        abort(404)
    else:
        if permission.can():
            if request.method == 'GET':
                return json.dumps(p.to_json())

            elif request.method == 'DELETE':
                db.session.delete(p)
                db.session.commit()
                return "Success"

            elif request.method == 'PUT':
                update_path = from_json(request.data)
                db.session.delete(p)
                db.session.add(update_path)
                db.session.commit()
                return "Success"
        else:
            abort(403)


@server.route('/paths', methods=['POST'])
@login_required
def creatPath():

    error = ""
    data = json.loads(request.data)
    old_path = Path.query.filter(User.id == data['id']).first()

    # new_path doesn't exit
    if old_path is None:
        if current_user.id != data['userId']:
            abort(403)
        else:
            new_path = from_json(request.data)
            db.session.add(new_path)
            db.session.commit()
            return "success, new path created"

    # new_path already exit
    else:
        error = "Path already exist"
        return error, 400


@server.route('/users/<int:userId>/paths', methods=['GET'])
@login_required
def userPaths(userId):

    permission = ManageUserPermission(userId)
    user = User.query.filter(User.id == userId).first()

    if user is None:
        abort(404)
    else:
        if permission.can():
            paths = Path.query.filter(Path.userId == userId).all()
            if len(paths) == 0:
                return 204
            else:
                return json.dumps(map(lambda p: p.to_json(), paths))
        else:
            abort(403)

def from_json(json_file):
        data = json.loads(json_file)
        sp_list = []
        for subpath in data['subpaths']:
            start = TransportStop(subpath['startStop']['line'], subpath['startStop']['name'], subpath['startStop']['typeTransport'])
            finish = TransportStop(subpath['finishStop']['line'], subpath['finishStop']['name'], subpath['finishStop']['typeTransport'])
            sp_list.append(SubPath(subpath['line'], subpath['direction'], start, finish))

        return Path(data['id'], data['userId'], data['active'], data['day'], data['beginHour'], data['endHour'], sp_list)
