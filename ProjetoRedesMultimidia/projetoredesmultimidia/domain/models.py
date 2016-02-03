from passlib.context import CryptContext
from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    Text,
    String,
    ForeignKey
    )

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    relationship
    )

from sqlalchemy_enum34 import EnumType

from zope.sqlalchemy import ZopeTransactionExtension

from projetoredesmultimidia.domain.Enuns import TipoCurso

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


class Usuario(Base):
    __tablename__ = "usuario"
    id = Column(Integer, primary_key=True)
    login = Column(Text, nullable=True)
    senha = Column(Text, nullable=True)
    principals = relationship("Principal", secondary="usuario_principal")

    def add_senha(self, senha):
        #Criando um objeto que usará criptografia do método shs256, rounds default de 80000
        cripto = CryptContext(schemes="sha256_crypt")
        #Encriptografando uma string
        self.senha = cripto.encrypt(senha)

    def validate_senha(self, senha):
         #Criando um objeto que usará criptografia do método shs256, rounds default de 80000
        cripto = CryptContext(schemes="sha256_crypt")
        #Comparando o valor da string com o valor criptografado
        okornot = cripto.verify(senha, self.senha)
        return okornot


class Usuario_profiler(Base):
    __tablename__ = "usuario_profiler"
    id = Column(Integer, primary_key=True)


class Usuario_Principal(Base):
    __tablename__ = "usuario_principal"

    usuario_id = Column(Integer, ForeignKey("usuario.id"), primary_key=True)
    principal_id = Column(Integer, ForeignKey("principal.id"), primary_key=True)


class Principal(Base):
    __tablename__ = "principal"
    id = Column(Integer, primary_key=True)
    nome = Column(Text, nullable=True)
    usuarios = relationship("Usuario", secondary="usuario_principal")


class Curso(Base):
    __tablename__ = "curso"

    id = Column(Integer, primary_key=True)
    nome = Column(Text, nullable=True)
    dateCreated = Column(DateTime, nullable=True)
    lastUpdated = Column(DateTime, nullable=True)
    Column(EnumType(TipoCurso, name="tipo_curso"), nullable=True)
    duracao = Column(DateTime, nullable=True)
    topicos = relationship("Topico", back_populates="curso", cascade="all, delete-orphan")

    def __repr__(self):
        return "id: %d, nome: %s, dateCreated: %r" % (self.id, self.nome, self.dateCreated)


class Comentario(Base):
    __tablename__ = "comentario"
    id = Column(Integer, primary_key=True)


class TopicoAbstrato(Base):
    __tablename__ = "topico_abstrato"
    id = Column(Integer, primary_key=True)
    nome = Column(Text)
    type = Column(String(50)) #aqui e que vai ser escrito qual e a classe na tabela

    __mapper_args__ = {
        'polymorphic_on': type,
        'polymorphic_identity': 'topico_abstrato'

    }

    def __repr__(self):
        return "id: %d, nome: %s" % (self.id, self.nome)


class Topico(TopicoAbstrato):
    curso_id = Column(Integer, ForeignKey("curso.id"))
    curso = relationship("Curso", back_populates="topicos")

    subtopicos = relationship("SubTopico", uselist=True, back_populates="topico",
                              cascade="all")

    #para identificar a classe na tabela
    __mapper_args__ = {
        'polymorphic_identity': 'Topico'
    }

    def __init__(self):
        TopicoAbstrato.__init__(self)

    def __repr__(self):
        return "subtopicos: %r" % self.subtopicos


class SubTopico(TopicoAbstrato):
    topico_id = Column(Integer, ForeignKey("topico_abstrato.id"))
    topico = relationship("Topico", uselist=False, back_populates="subtopicos", remote_side=[TopicoAbstrato.id])
    video = relationship("Video", uselist=False, back_populates="subtopico", cascade="all, delete-orphan")

    #para identificar a classe na tabela
    __mapper_args__ = {
        'polymorphic_identity': 'SubTopico'
    }

    def __init__(self):
        TopicoAbstrato.__init__(self)

    def __repr__(self):
        return "topico: %r" % self.topico


class Video(Base):
    __tablename__ = "video"

    id = Column(Integer, primary_key=True)
    nome = Column(Text, nullable=True)
    path = Column(Text, nullable=True)
    dateCreated = Column(DateTime, nullable=True)
    lastUpdate = Column(DateTime, nullable=True)
    subtopico_id = Column(Integer, ForeignKey("topico_abstrato.id"))
    subtopico = relationship("SubTopico", uselist=False, back_populates="video")