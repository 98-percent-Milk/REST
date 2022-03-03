from sqlalchemy import Column, Integer, String, DateTime, null
from base import Base
import datetime


class JobDescription(Base):
    """ SQLite declaretive for job description event """

    __tablename__ = 'job_description'

    id = Column(Integer, primary_key=True)
    ad_id = Column(String(250), nullable=False)
    trace_id = Column(String(250), nullable=False)
    date_created = Column(DateTime, nullable=False)
    description = Column(String(250), nullable=False)
    employer = Column(String(100), nullable=False)
    field = Column(String(100), nullable=False)
    position = Column(String(100), nullable=False)

    def __init__(self, ad_id, trace_id, description, employer, field, position):
        self.ad_id = ad_id
        self.trace_id = trace_id
        self.date_created = datetime.datetime.now()
        self.description = description
        self.employer = employer
        self.field = field
        self.position = position

    def to_dict(self):
        """ Dictionary Representation of a job advertisement description """
        temp = dict()
        temp["id"] = self.id
        temp["ad_id"] = self.ad_id
        temp["trace_id"] = self.trace_id
        temp["date_created"] = self.date_created
        temp["employer"] = self.employer
        temp["field"] = self.field
        temp["position"] = self.position

        return temp
