# -*- coding: utf-8 -*-

from calendar import (
    Calendar, SUNDAY, day_abbr
)
from collections import namedtuple
from datetime import (
    datetime, date
)
from flask import (
    Blueprint, render_template, redirect,
    jsonify, request,url_for
)
from flask_login import login_required
from workscheduler.applications.services import (
    BelongQuery, ScheduleQuery, SkillQuery,
    OperatorQuery
)
from ..adapters import ScheduleCommandAdapter
from ..forms import (
    SchedulerOptionForm, SchedulerDateSettingForm
)
from ..util import get_next_month
from .. import get_db_session
from . import admin_required


bp = Blueprint('schedules', __name__)


@bp.route('/schedules')
@login_required
def show_schedules():
    return render_template('schedules.html')


@bp.route('/schedules/scheduler-option/belongs/<belong_id>')
@login_required
@admin_required
def show_scheduler_option(belong_id: str):
    session = get_db_session()
    
    scheduler = ScheduleQuery(session).get_scheduler_of_belong_id(belong_id)
    
    action = url_for('schedules.append_scheduler_option', belong_id=belong_id) if not scheduler\
        else url_for('schedules.update_scheduler_option', scheduler_id=scheduler.id, belong_id=belong_id)
    url = url_for('schedules.show_scheduler_option', belong_id="")

    belongs = BelongQuery(session).get_belongs_without_default()
    skills = SkillQuery(session).get_skills()
    operators = OperatorQuery(session).get_operators()
    
    return render_template('scheduler-option.html', action=action, url=url,
                           form=SchedulerOptionForm(obj=scheduler), belong_id=belong_id,
                           belongs=belongs, skills=skills, operators=operators)


@bp.route('/schedules/scheduler-option/belongs/<belong_id>', methods=['POST'])
@login_required
@admin_required
def append_scheduler_option(belong_id):
    session = get_db_session()
    try:
        req = ScheduleCommandAdapter(session).append_scheduler(SchedulerOptionForm(request=request.form))
        session.commit()
        response = jsonify({
            'redirect': url_for('schedules.show_scheduler_date_setting',
                                belong_id=belong_id, schedule_of=get_next_month())
        })
    except Exception as e:
        session.rollback()
        print(e)
        response = jsonify()
        response.status_code = 400
    return response


@bp.route('/schedules/scheduler-option/<scheduler_id>/belongs/<belong_id>', methods=['POST'])
@login_required
@admin_required
def update_scheduler_option(scheduler_id, belong_id):
    session = get_db_session()
    try:
        req = ScheduleCommandAdapter(session).update_scheduler(SchedulerOptionForm(request=request.form))
        session.commit()
        response = jsonify({
            'redirect': url_for('schedules.show_scheduler_date_setting',
                                belong_id=belong_id, schedule_of=get_next_month())
        })
    except Exception as e:
        session.rollback()
        print(e)
        response = jsonify()
        response.status_code = 400
    return response


@bp.route('/schedules/scheduler-date-setting/belong-id/<belong_id>/schedule-of/<schedule_of>')
@login_required
@admin_required
def show_scheduler_date_setting(belong_id: str, schedule_of: str):
    if schedule_of and not isinstance(schedule_of, date):
        schedule_of = datetime.strptime(schedule_of, '%Y-%m').date()

    CalendarDay = namedtuple('CalendarDay', ('day', 'week_day'))
    calender = Calendar()

    def create_date(_date):
        return CalendarDay(_date.day, day_abbr[_date.weekday()])

    calender.setfirstweekday(SUNDAY)
    date_set = [create_date(_date) for week in calender.monthdatescalendar(schedule_of.year, schedule_of.month)
                for _date in week if _date.year == schedule_of.year and _date.month == schedule_of.month]
    
    session = get_db_session()
    operators = OperatorQuery(session).get_operators()
    
    form = SchedulerDateSettingForm(obj=type('temp', (object,), {
        'schedule_of': schedule_of,
        'belong': BelongQuery(session).get_belong(belong_id)
    }))
    
    return render_template('scheduler-date-setting.html', form=form,
                           date_set=date_set, operators=operators)


@bp.route('/schedules/schedule/belongs/<belong_id>', methods=['POST'])
@login_required
@admin_required
def create_schedule(belong_id: str):
    pass
