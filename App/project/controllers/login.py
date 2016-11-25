from project import *
from project.models.user import User
from flask.ext.principal import identity_loaded, Permission, RoleNeed, UserNeed
from collections import namedtuple
from functools import partial

@login_manager.user_loader
def load_user(userid):
    return User.query.filter(User.id == userid).first()


@server.route('/users/login', methods=['GET'])
def login():

    error = None
    data = json.loads(request.data)

    if valid_login(data['email'], data['password']):
        user = User.query.filter(User.email == data['email']).first()
        login_user(user, remember=True)

        identity_changed.send(current_app._get_current_object(), identity=Identity(user.id))

        return "You are now login"
    else:
        error = 'Invalid email/password'
        return error, 400


@server.route('/users/logout', methods=['GET'])
@login_required
def logout():
    logout_user()

    for key in ('identity.name', 'identity.auth_type'):
        session.pop(key, None)

    identity_changed.send(current_app._get_current_object(), identity=AnonymousIdentity())

    return "You are now logout"


@identity_loaded.connect_via(server)
def on_identity_loaded(sender, identity):

    identity.user = current_user

    if hasattr(current_user, 'id'):
        identity.provides.add(UserNeed(current_user.id))
        identity.provides.add(ManageUserNeed(unicode(current_user.id)))

    if hasattr(current_user, 'paths'):
        for path in current_user.paths:
            identity.provides.add(ManagePathNeed(unicode(path.id)))

def valid_login(email, password):
    user = User.query.filter(User.email == email).first()
    if user is None:
        return False
    else:
        return email == user.email and password == user.password

# Permission pour la gestion des trajets
PathNeed = namedtuple('path_need', ['method', 'value'])
ManagePathNeed = partial(PathNeed, 'manage')

class ManagePathPermission(Permission):
    def __init__(self, path_id):
        need = ManagePathNeed(unicode(path_id))
        super(ManagePathPermission, self).__init__(need)


# Permission pour la gestion des users
UsersNeed = namedtuple('user_need', ['method', 'value'])
ManageUserNeed = partial(UsersNeed, 'manage')

class ManageUserPermission(Permission):
    def __init__(self, user_id):
        need = ManageUserNeed(unicode(user_id))
        super(ManageUserPermission, self).__init__(need)
