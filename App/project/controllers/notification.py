from project import *
from project.models import *
from flask.ext.principal import identity_loaded, Permission, RoleNeed, UserNeed
from collections import namedtuple
from functools import partial
from server import *


def send_notifications(affected_paths):
    APNS_notifs = []
    GCM_notifs = []

    for p in affected_paths:
        alert = dict()
        notif = dict()
        user = user.query.filter(User.id == p.userId).first()

        token = user.tokenDevice

        alert['userId'] = user.id
        alert['pathId'] = p.id
        notif = {'token': token, 'alert': alert}

        if user.OS == "ANDROID":
            GCM_notifs.append(notif)
        elif user.OS == "iOS":
            APNS_notifs.append(notif)

    for n in GCM_notifs:
        res = client_GCM.send(n['token'], n['alert'])
    for n in APNS_notifs:
        res = client_APNS.send(n['token'], n['alert'])
