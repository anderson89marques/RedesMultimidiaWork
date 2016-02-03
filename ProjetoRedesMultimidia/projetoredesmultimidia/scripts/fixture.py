__author__ = 'anderson'

import datetime
from projetoredesmultimidia.domain.models import (Usuario, Principal, Usuario_Principal,
                                                  Curso, Topico, SubTopico, Video, DBSession)
import transaction


class Initialize:
    def create_users_and_principals(self):
        user = DBSession.query(Usuario).filter(Usuario.login == "anderson").first()
        print(user)
        if not user:
            user = Usuario()
            user.login = "anderson"
            user.add_senha("123456")
            p = Principal()
            p.nome = 'role_user'
            #p.usuarios.append(user)
            user.principals.append(p)

            DBSession.add(p)
            DBSession.add(user)
            transaction.commit()

    def createObjects(self):
        print("createObjects")
        curso = DBSession.query(Curso).all()
        print(curso)
        if not curso:
            print("aqui")
            curso = Curso()
            curso.nome, curso.dateCreated = "Curso sobre Pyramid Framework", datetime.datetime.now()
            topico1 = Topico()
            topico1.nome = "Introdução"
            subtopico1 = SubTopico()
            subtopico1.nome = "conhecendo o pyramid e o hello world"
            video = Video()
            video.nome, video.path = "hello world", "testeSimpleScreeRecoder-2015-08-31_22.08.41.mp4"
            video.dateCreated = datetime.datetime.now()
            subtopico1.video = video
            topico1.subtopicos.append(subtopico1)
            curso.topicos.append(topico1)
            #DBSession.add(curso)

            topico2 = Topico()
            topico2.nome = "Usando o framework"

            subtopico20 = SubTopico()
            subtopico20.nome = "estrutura de diretótios"
            video = Video()
            video.nome, video.path = "diretorios", "aula2Pyramid-2015-08-16_08.24.29.mp4"
            video.dateCreated = datetime.datetime.now()
            subtopico20.video = video
            topico2.subtopicos.append(subtopico20)

            subtopico21 = SubTopico()
            subtopico21.nome = "estrutura de diretótios(sem audio)"
            video = Video()
            video.nome, video.path = "diretorios(sem audio)", "Aula2Pyramid-2015-08-14_08.13.40.mp4"
            video.dateCreated = datetime.datetime.now()
            subtopico21.video = video
            topico2.subtopicos.append(subtopico21)
            curso.topicos.append(topico2)
            DBSession.add(curso)
            transaction.commit()
