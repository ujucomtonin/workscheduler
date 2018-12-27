# -*- coding: utf-8 -*-

from calendar import (
    Calendar, SUNDAY, day_abbr
)
from collections import namedtuple
from datetime import (
    datetime, date
)
from flask import (
    Blueprint, render_template
)
from flask_login import login_required
from workscheduler.applications.services import BelongQuery
from .. import get_db_session
from . import admin_required


bp = Blueprint('schedules', __name__)


@bp.route('/schedules/show_schedules')
@login_required
def show_schedules():
    return render_template('schedules.html')


@bp.route('/schedules/show_scheduler/<belong_id>/<month_year>')
@login_required
@admin_required
def show_scheduler(belong_id: str, month_year: str):
    if month_year and not isinstance(month_year, date):
        month_year = datetime.strptime(month_year, '%Y-%m').date()

    CalendarDay = namedtuple('CalendarDay', ('day', 'week_day'))

    calender = Calendar()

    def create_date(_date):
        return CalendarDay(_date.day, day_abbr[_date.weekday()])

    calender.setfirstweekday(SUNDAY)
    date_set = [create_date(_date) for week in calender.monthdatescalendar(month_year.year, month_year.month)
                for _date in week if _date.year == month_year.year and _date.month == month_year.month]

    belong_query = BelongQuery(get_db_session())
    default_belong = belong_query.get_default_belong()
    belongs = [b for b in belong_query.get_belongs() if not b.id == default_belong.id]
    belong = belong_query.get_belong(belong_id)
    return render_template('scheduler.html', selected_belong=belong, belongs=belongs,
                           month_year=month_year, date_set=date_set)


@bp.route('/schedules/create_schedule/<belong_id>')
@login_required
@admin_required
def create_schedule(belong_id: str):
    pass
