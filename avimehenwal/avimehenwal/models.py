import datetime #<- will be used to set default dates on models

from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
    Unicode,     #<- will provide Unicode field
    UnicodeText, #<- will provide Unicode text field
    DateTime,    #<- time abstraction field
    )

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


import sqlalchemy as sa
from paginate_sqlalchemy import SqlalchemyOrmPage # for db pagination
from webhelpers2.text import urlify #<- will generate slugs
from webhelpers2.date import distance_of_time_in_words #<- human friendly dates


class MyModel(Base):
    __tablename__ = 'models'
    id = Column(Integer, primary_key=True)
    name = Column(Text)
    value = Column(Integer)

Index('my_index', MyModel.name, unique=True, mysql_length=255)


class BlogRecord(Base):
    __tablename__ = 'entries'
    id       = Column(Integer, primary_key=True)
    title    = Column(Unicode(255), unique=True, nullable=False)
    body     = Column(UnicodeText, default=u'')
    author   = Column(UnicodeText, default=u'avimehenwal')
    created  = Column(DateTime, default=datetime.datetime.utcnow)
    modified = Column(DateTime, default=datetime.datetime.utcnow)

    @property
    def slug(self):
        return urlify(self.title)

    @property
    def created_in_words(self):
        return distance_of_time_in_words(self.created, datetime.datetime.utcnow())


class BlogRecordService(object):
    
    @classmethod
    def all(cls):
        return DBSession.query(BlogRecord).order_by(sa.desc(BlogRecord.created))
        
    @classmethod
    def by_id(cls, id):
        return DBSession.query(BlogRecord).fliter(BlogRecord.id == id).first()
        
    @classmethod
    def get_paginator(cls, request, page=1):
        query = DBSession.query(BlogRecord).order_by(sa.desc(BlogRecord.created))
        query_params = request.GET.mixed()

        def url_maker(link_page):
            # replace page params with value generated by paginator
            query_params['page'] = link_page
            return request.current_route_url(_query=query_params)

        return SqlalchemyOrmPage(query, page, items_per_page=5, url_maker=url_maker)
