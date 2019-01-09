# -*- coding: utf-8 -*-

from workscheduler.domains.models.operator import Operator
from workscheduler.domains.models.user import User


class OperatorQuery:
    def __init__(self, session):
        self._session = session
    
    def get_operator(self, id: str):
        return self._session.query(Operator).get(id)
    
    def get_operator_of_user_id(self, user_id: str):
        return self._session.query(Operator)\
            .filter(Operator.user.has(User.id == user_id)).one()
    
    def get_operators(self):
        return self._session.query(Operator)\
            .filter(Operator.user.has(User.is_operator)).all()
