import logging
from tornado.web import RequestHandler
from tornado.websocket import WebSocketHandler
from domain.models import Usuario, Principal
import codecs
from codecs import utf_8_decode, utf_8_encode
import base64



class MainHandler(RequestHandler):
    @property
    def db(self):
        return self.application.db

    def get_user(self):
        """
        esse método retorna o usuário logado.
        como vem redirecionado do app pyramid, no header da requisição é passado o login e senha
        do usuário
        :return:
        """
        return self.db.query(Usuario).filter(Usuario.login == 'anderson').first()

    def get_principals(self):
        pass

    def b64unicode(self, v):
        return utf_8_decode(self.b64decode(v))[0]

    def b64decode(self, v):
        print(type(v))
        return v

    def get(self, room):
        print([k for k in self.request.headers.get_all()])
        #usuario = self.get_user()
        #print(usuario)
        self.render('index.html')


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
