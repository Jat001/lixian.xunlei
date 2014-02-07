# -*- encoding: utf-8 -*-

from model import *

from tornado.options import options
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import SQLAlchemyError

engine = create_engine(options.database_engine, echo=options.database_echo, pool_recycle=10)

metadata = Base.metadata
metadata.create_all(engine)

Session = scoped_session(sessionmaker(bind=engine))
