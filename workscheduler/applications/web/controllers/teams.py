# -*- coding: utf-8 -*-

from flask import Blueprint, request, render_template, Response, flash
from flask_login import login_required
from workscheduler.applications.services.team_query import TeamQuery
from workscheduler.applications.services.user_query import UserQuery
from .. import get_db_session
from ..adapters import TeamCommandAdapter
from ..forms import TeamCategoryForm
from workscheduler.domains.models.team import TeamCategory


bp = Blueprint('teams', __name__)


@bp.route('/teams/show_team_categories')
@login_required
def show_team_categories():
    team_repository = TeamQuery(get_db_session())
    return render_template('team_categories.html', team_categories=team_repository.get_team_categories())

@bp.route('/teams/append_team_category')
@login_required
def show_append_page():
    return render_template('append_team_category.html')

@bp.route('/teams/append_team_category/store', methods=['POST'])
@login_required
def store_team_category():
    response = Response()

    session = get_db_session()
    try:
        TeamCommandAdapter(session).append_team_category(TeamCategoryForm())

        session.commit()

        # session.query(TeamCategory).order_by(TeamCategory.id.desc()).first()
        response.status_code = 200
    except:
        response.status_code = 400
        session.rollback()
    return response

@bp.route('/teams/edit_team_category', methods=['POST'])
@login_required
def show_edit_page():
    session = get_db_session()
    team_repository = TeamQuery(session)
    user_repository = UserQuery(session)
    return render_template('edit_team_category.html', team_category=team_repository.get_team_category(request.form.get('team_category_id')), all_users=user_repository.get_users())
