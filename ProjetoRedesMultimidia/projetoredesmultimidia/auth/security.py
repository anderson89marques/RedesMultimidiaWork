from projetoredesmultimidia.domain.models import Usuario, DBSession


def groupfinder(userid, request):
    print("Request do group finder %r: userid: %r" % (request.params, userid))
    user = DBSession.query(Usuario).filter(Usuario.login == userid).first()
    print("USER: %r" % user)
    if user:
        print("Principals %r" % user.principals[0].nome)
        return [principal.nome for principal in user.principals]

