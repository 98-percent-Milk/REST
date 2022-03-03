from sqlalchemy import Column, Integer, String, DateTime
from base import Base
from datetime import datetime


class EmployeeResume(Base):
    """ SQLite declaretive representation of employee resume event """

    __tablename__ = "employee_resume"
    id = Column(Integer, primary_key=True)
    resume_id = Column(String, nullable=False)
    trace_id = Column(String, nullable=False)
    date_created = Column(DateTime, nullable=False)
    experience = Column(String, nullable=False)
    field = Column(String, nullable=False)
    position = Column(String, nullable=False)

    def __init__(self, resume_id, trace_id, experience, field, position):
        self.resume_id = resume_id
        self.trace_id = trace_id
        self.date_created = datetime.now().replace(microsecond=0)
        self.experience = experience
        self.field = field
        self.position = position

    def to_dict(self):
        """ Dictionary Representation of a employee resume """
        temp = dict()
        temp["id"] = self.id
        temp["date_created"] = self.date_created
        temp["experience"] = self.experience
        temp["field"] = self.experience
        temp["position"] = self.position
        temp["resume_id"] = self.resume_id
        temp["trace_id"] = self.trace_id

        return temp
