from project import *
from project.models.user import User
from login import *

@server.route('/users/<int:userId>', methods=['GET', 'DELETE', 'PUT'])
@login_required
def user(userId):
    permission = ManageUserPermission(userId)

    user = User.query.filter(User.id == userId).first()
    if user is None:
        abort(404)
    else:
        if permission.can():
            if request.method == 'GET':
                return json.dumps(user.to_json())

            elif request.method == 'DELETE':
                db.session.delete(user)
                db.session.commit()
                return 'User {} deleted'.format(user.email)

            elif request.method == 'PUT':
                data = json.loads(request.data)
                if data['id'] != current_user.id:
                    abort(403)
                else:
                    update_user = User(data['id'], data['firstName'], data['lastName'], data['email'], data['password'], data['paths'])
                    db.session.delete(user)
                    db.session.add(update_user)
                    db.session.commit()
                    return "Success"

        else:
            abort(403)


@server.route('/users', methods=['POST'])
def creatUser():
    error = None
    data = json.loads(request.data)
    new_user = User(data['id'], data['firstName'], data['lastName'], data['email'], data['password'])

    old_user = User.query.filter(User.email == new_user.email).first()
    if old_user is None:
        db.session.add(new_user)
        db.session.commit()
        return "Sucess"
    else:
        error = 'User already exist'
        return error, 404
