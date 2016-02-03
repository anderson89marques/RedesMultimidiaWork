from sqlalchemy import engine_from_config

from pyramid.config import Configurator
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from projetoredesmultimidia.auth.security import groupfinder

from projetoredesmultimidia.domain.models import (
    DBSession,
    Base,
    )
from projetoredesmultimidia.scripts.fixture import Initialize

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    Base.metadata.create_all()
    config = Configurator(settings=settings, root_factory='projetoredesmultimidia.auth.resource.Root')

    #criando uma estrutura de objetos para poder testar a aplicação.
    init = Initialize()
    init.create_users_and_principals()
    init.createObjects()
    #Politica de segurança
    print("Configurando a Autenicação e configuração ")
    autenticacao_po = AuthTktAuthenticationPolicy(settings['app.secret'], callback=groupfinder, hashalg='sha512')
    autorizacao_po = ACLAuthorizationPolicy()
    config.set_authentication_policy(autenticacao_po)
    config.set_authorization_policy(autorizacao_po)

    config.include('pyramid_jinja2')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('cursos', '/cursos')
    config.add_route('curso', '/cursos/curso')
    config.add_route('video_aula', '/cursos/curso/video_aula')
    config.add_route('live', '/live')
    config.add_route('liveroom', '/live/{room}')
    #config.add_route('signaling', '/ws/{room}')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    config.add_route('iptest', '/iptest')

    config.scan()
    return config.make_wsgi_app()
