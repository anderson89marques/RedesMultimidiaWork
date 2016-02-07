import logging
from tornado.web import RequestHandler
from tornado.websocket import WebSocketHandler
from domain.models import Usuario, Principal


class LoginException(Exception):
    pass


class BaseHandler(RequestHandler):
    @property
    def db(self):
        return self.application.db

    def get_current_user(self):
        return self.get_secure_cookie("user")


class MainHandler(BaseHandler):
    def get_principals(self, user):
        """
        esse método retorna o usuário logado.
        como vem redirecionado do app pyramid, no header da requisição é passado o login e senha
        do usuário
        :return:
        """
        usuario = self.db.query(Usuario).filter(Usuario.login == user.decode("utf8")).first()
        if usuario:
            return [p.nome for p in usuario.principals]

    def get(self, room):
        if not self.current_user:
            self.redirect('/login/{}'.format(room))
            return
        principals = self.get_principals(self.current_user)
        print(principals)
        self.render("live_page.html", principals=principals)


class LoginHandler(BaseHandler):
    def get_user(self, login, senha):
        """
        esse método retorna o usuário logado.
        como vem redirecionado do app pyramid, no header da requisição é passado o login e senha
        do usuário
        :return:
        """
        usuario = self.db.query(Usuario).filter(Usuario.login == login).first()
        if usuario.validate_senha(senha):
            return usuario
        else:
            raise LoginException("erro ao logar")

    def get(self, room):
        print("Login")
        self.render('login.html', room=room)

    def post(self, *args, **kwargs):
        print("POST LOGIN")
        req_arguments = self.request.body_arguments
        login = req_arguments['username'][0].decode("utf8")
        passwd = req_arguments['senha'][0].decode("utf8")
        room = req_arguments['room'][0].decode("utf8")

        try:
            usuario = self.get_user(login, passwd)
            self.set_secure_cookie("user", login)
            self.redirect("/live/{}".format(room))
        except LoginException as l:
            print(l)
            self.write("Erro ao realizar login")
        print(usuario)


class LogoutHandler(BaseHandler):
    def get(self):
        print('Logout')
        print(self.current_user)
        self.clear_cookie('user')


class EchoWebSocket(WebSocketHandler):
    clients = []

    def open(self, room):
        logging.info('WebSocket opened from %s', self.request.remote_ip)
        logging.info('room %s', room)
        self.write_message(room)
        EchoWebSocket.clients.append(self)

    def on_message(self, message):
        logging.info('got message from %s: %s', self.request.remote_ip, message)
        for client in EchoWebSocket.clients:
            if client is self:
                continue
            client.write_message(message)

    def on_close(self):
        logging.info('WebSocket closed')
        EchoWebSocket.clients.remove(self)
