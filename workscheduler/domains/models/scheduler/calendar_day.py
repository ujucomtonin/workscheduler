# -*- coding: utf-8 -*-

from sqlalchemy import (
    Column, Table, ForeignKey
)
from sqlalchemy.orm import (
    relationship
)
from sqlalchemy.types import (
    String, DateTime,
    Integer
)

from mypackages.utils.date import is_holiday
from mypackages.utils.uuid import UuidFactory
from . import (
    WorkCategory, CalendarDayDetail
)
from .. import OrmBase

associated_calendar_day_details_table\
    = Table("associated_calendar_day_details", OrmBase.metadata,
            Column("left_id", String, ForeignKey('calendar_days.id')),
            Column("right_id", String, ForeignKey('calendar_day_details.id')))


class CalendarDay(OrmBase):
    __tablename__ = "calendar_days"
    id = Column(String, primary_key=True)
    day = Column(Integer)
    day_name = Column(String)
    details = relationship("CalendarDayDetail", secondary=associated_calendar_day_details_table)

    def __init__(self, id_: str, day: int, day_name: str,
                 details: []):
        self.id = id_
        self.day = day
        self.day_name = day_name
        self.details = details
    
    def add_category(self, work_catgory: WorkCategory):
        self.details.append(CalendarDayDetail.new_detail(work_catgory, 0))
        
    @staticmethod
    def new_day(date: DateTime, date_name: str, work_categories: [WorkCategory]):
        details = [CalendarDayDetail.new_detail(x, x.week_day_require if not is_holiday(date) else x.holiday_require)
                   for x in work_categories]
        return CalendarDay(UuidFactory.new_uuid(), date.day, date_name, details)
