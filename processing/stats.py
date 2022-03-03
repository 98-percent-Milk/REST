from ipaddress import collapse_addresses
from sqlalchemy import Column, Integer, String, DateTime
from base import Base


class Stats(Base):
    """ Processing Statistics """

    __tablename__ = "stats"

    id = Column(Integer, primary_key=True)
    num_employees = Column(Integer, nullable=False)
    popular_field = Column(String, nullable=False)
    unpopular_field = Column(String, nullable=False)
    desp_employer = Column(String, nullable=False)
    least_desp_employer = Column(String, nullable=False)
    last_updated = Column(DateTime, nullable=False)

    def __init__(self, num_emp, pop_field, unpop_field, desp, least_desp, updated):
        self.num_employees = num_emp
        self.popular_field = pop_field
        self.unpopular_field = unpop_field
        self.desp_employer = desp
        self.least_desp_employer = least_desp
        self.last_updated = updated

    def to_dict(self) -> dict:
        """ Dictionary Representation of a statistics """
        dict = {}
        dict['num_employees'] = self.num_employees
        dict['popular_field'] = self.popular_field
        dict['unpopular_field'] = self.unpopular_field
        dict['desp_employer'] = self.desp_employer
        dict['least_desp_employer'] = self.least_desp_employer
        dict['last_updated'] = self.last_updated
        return dict
