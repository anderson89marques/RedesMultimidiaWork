import asyncio
import uuid
import logging
import json
from pyramid.view import HTTPFound, view_config, forbidden_view_config
from pyramid.security import remember, forget, authenticated_userid, effective_principals
from pyramid.response import Response
from pyramid.httpexceptions import HTTPUnauthorized
from projetoredesmultimidia.domain.models import (Curso, Usuario, Principal, DBSession)
from aiopyramid.websocket.view import WebsocketConnectionView
from aiopyramid.websocket.config import WebsocketMapper


class Home:
    def __init__(self, request):
        self.request = request
        self.view = authenticated_userid

    @view_config(route_name='home', renderer='templates/principal/home.jinja2')
    def home(self):
        return {'project': 'ProjetoRedesMultimidia', 'view': self.view}


class Cursos:
    def __init__(self, request):
        self.request = request

    @view_config(route_name='cursos', renderer='templates/cursos/cursos.jinja2', permission="ROLE_USER")
    def cursos(request):
        return {'project': 'ProjetoRedesMultimidia'}

    @view_config(route_name='curso', renderer='templates/cursos/curso.jinja2', permission="ROLE_USER")
    def curso(request):
        return {'project': 'ProjetoRedesMultimidia'}

    @view_config(route_name='video_aula', renderer='templates/cursos/video_aula_home.jinja2', permission="ROLE_USER")
    def videoAula(request):
        curso = DBSession.query(Curso).first()
        return {'curso': curso}


class Live:
    def __init__(self, request):
        self.request = request

    @view_config(route_name="live", permission="ROLE_USER")
    def live_method(self):

        application_url = self.request.url
        print(application_url)
        print(application_url.replace('6543', '6544'))
        uuidroom = uuid.uuid4().hex[:6]
        headers = [('user_id', self.request.authenticated_userid)]
        #Redirecionando para o servidor do tornado
        #Vou redirecionar para a tela de login do aplicação realtime,
        #que vai funcionar como se fosse apenas um serviço acoplado ao sistema.

        print("REDIRECIOANDO %r" % self.request.headers)
        return HTTPFound(location=application_url.replace('6543', '6544') + "/%s" % uuidroom, headers=headers)

    @view_config(route_name="liveroom", renderer="templates/cursos/video_aula_live_new.jinja2", permission="ROLE_USER")
    def live_room(self):
        print("LIVEROOM: %s" % self.request.url)
        return {"msg": "ok"}


global_rooms = {}
"""
    terei que criar uma rota que seja seja que tenha uma parâmetro
    tipo /live/abck2, onde abck2 é gerado altomaticamente e representa a sala de bate papo,
    então basta outra pessoa se conectar nessa mesma sala que entrarão em contato.
"""


class Room:
    def __init__(self, name, clientes=[]):
        self.name = name
        self.clientes = clientes

    def __repr__(self):
        return "Room Name: %s" % self.name


#@view_config(route_name="signaling", permission="ROLE_USER")
class LiveWebSocket(WebsocketConnectionView):
    __view_mapper__ = WebsocketMapper

    clients = []

    def on_open(self):
        logging.info('WebSocket opened from %s', self.request.remote_addr)
        LiveWebSocket.clients.append(self)
        return []

    def on_message(self, message):
        logging.info('got message from %s: %s', self.request.remote_addr, message)
        for client in LiveWebSocket.clients:
            if client is self:
                continue
            yield from self.send(message)
            #client.write_message(message)

    def on_close(self):
        logging.info('WebSocket closed')
        LiveWebSocket.clients.remove(self)
        yield from []


class SignalingWebSocket(WebsocketConnectionView):
    __view_mapper__ = WebsocketMapper

    mensagem = None

    def on_open(self):
        #sempre tenho que retornar um iterable
        print("ONOPen REQUEST: %r" % self.request.client_addr)
        print("ONOPen REQUEST: %r" % self.request.remote_addr)
        print("ONOPen REQUEST: %r" % self.request.host)
        print("ONOPen REQUEST: %r" % self.request.url)
        print("ONOPen REQUEST: %r" % self.request.application_url)
        roomkey = self.request.matchdict["room"]
        print("Roomkey: %s" % roomkey)
        if roomkey in global_rooms:
            global_rooms[roomkey].clientes.append(self)
        else:
            global_rooms[roomkey] = Room(roomkey, clientes=[self])

        #Criando a variável room para que eu controle a room criada.
        self.room = global_rooms[roomkey]

        if len(global_rooms[roomkey].clientes) > 2:
            print('full')
            yield from self.send("fullhouse")
        elif len(global_rooms[roomkey].clientes) == 1:
            print('init')
            yield from self.send("initiator")
        else:
            print('not')
            yield from self.send("not initiator")
        print("Remote addres: %s" % self.request.remote_addr)

        return []

    def on_message(self, message):
        print("Recebendo mensagem de : %r" % self.request.remote_addr)
        print("Mensagem: %s" % message)
        #aqui está dando erro pq eu mesmo pego a minha msg e envio para mim mesmo
        #então é precido pegar a mensagem do outro
        jsonmsg = json.loads(message)
        print("Mensagem json %r" % jsonmsg)
        self.mensagem = message
        print("Mensagem: %s" % self.mensagem)
        loop = True
        while loop:
            for cliente in self.room.clientes:
                print("CLIENTE: %r" % cliente)
                print("Self: %r" % self)
                print("Clientes size: %r" % len(self.room.clientes))
                if cliente is self:
                    continue
                else:
                    print("Else")
                    print("Mensagem do cliente: %r" % cliente.mensagem)
                    if cliente.mensagem:
                        print("here")
                        yield from self.send(cliente.mensagem)
                    else:
                        print("hahhehe")
                        yield from self.send(json.dumps({"msg": "entrou novo cliente"}))
            print("//////////////////////////")
            yield from asyncio.sleep(3)
            #if len(self.room.clientes) == 2:
                #loop = False

    def on_close(self):
        print("Connction closed")
        #self.room.clientes.remove(self)
        return []


class Login:
    def __init__(self, request):
        self.request = request
        self.logged_in = request.authenticated_userid

    @forbidden_view_config()
    def sem_auth_control(self):

        """
        Se o usuário está logado e veio parar aqui quer dizer que ele não tem autorização para acessar
        alguma view. então devo retornar uma mensagem dizendo que ele não tem permissão, ou uma página de não permissão.
        Se o usuário não estiver logado ele vai para a tela de login
        :return:
        """

        print("Sem auth control")
        print(effective_principals(self.request))
        if 'system.Authenticated' in effective_principals(self.request):
            print("Usuário sem permissão: %r" % self.logged_in)
            return HTTPUnauthorized() #mudar para HTTPFound e criar uma tela de não permissão.
        else:
            print("Usuário não logado. redirecionando para login")
            return HTTPFound(location=self.request.application_url + '/login') #redirecionado pra tela de login

    @view_config(route_name="login", renderer="templates/login.jinja2")
    def login(self):
        print("Login")
        print(self.request.params)

        if "login" in self.request.params:
            print("AQUI")
            username = self.request.params["username"]
            senha = self.request.params["senha"]

            usuario = DBSession.query(Usuario).filter(Usuario.login == username).first()
            print(usuario)
            print(username)
            if(usuario):
                ok = usuario.validate_senha(senha)
                if ok:
                    print("Login ok")
                    headers = remember(self.request, username)
                    print("HEADERS %r" % headers)
                    return HTTPFound(location=self.request.route_url("home"), headers=headers)
            msg = "Login Falhou! Usuário e/ou senha inválidos"

            if msg:
                Response(msg, content_type='text/plain', status_int=500)

        return {"msg": "okokokokoko"}

    @view_config(route_name="logout")
    def logout(self):
        print("Logout!")

        print(self.request.params)
        #user = DBSession.query(Usuario).filter(Usuario.nome == self.request.authenticated_userid).first()

        headers = forget(self.request)
        url = self.request.route_url('home')

        return HTTPFound(location=url, headers=headers)


@view_config(route_name="iptest", renderer="templates/cursos/getIpTeste.jinja2")
def get_ip_test(request):
    return {"msg": "ok"}