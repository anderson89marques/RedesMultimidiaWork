from pyramid.security import Everyone, Allow, ALL_PERMISSIONS


class Root(object):

    #Access Control List
    __acl__ = [(Allow, Everyone, 'view'),
               (Allow, 'role_admin', ALL_PERMISSIONS),
               (Allow, 'role_user', 'ROLE_USER'),
               (Allow, 'role_teacher', 'ROLE_TEACHER')]

    def __init__(self, request):
        pass