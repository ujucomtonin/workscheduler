# -*- coding: utf-8 -*-

from workscheduler.domains.utils.uuid import UuidFactory
from workscheduler.domains.models import OrmBase
from sqlalchemy import Column, Table, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.types import String, DateTime
from sqlalchemy.sql.functions import current_timestamp


team_users\
    = Table("team_users", OrmBase.metadata,
            Column('team_id', String, ForeignKey('teams.id')),
            Column('user_id', String, ForeignKey('users.id'))
            )


class Team(OrmBase):
    __tablename__ = 'teams'
    id = Column(String, primary_key=True)
    name = Column(String(50))
    team_category_id = Column(String, ForeignKey('team_categories.id'))
    create_at = Column(DateTime, server_default=current_timestamp())

    users = relationship("User", secondary=team_users, backref="teams")

    def __init__(self, id: str, team_category_id: str, name: str):
        self.id = id
        self.team_category_id = team_category_id
        self.name = name

class TeamFactory:
    @classmethod
    def register_a_test_team(cls, id: str, team_category_id: str, name: str):
        return Team(id, team_category_id, name)