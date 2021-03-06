# -*- coding: utf-8 -*-

import os
import sys
from datetime import (
    date
)

import click
from flask import (
    Flask, g, current_app
)
from flask.cli import with_appcontext
from flask_login import (
    LoginManager, current_user
)
from jinja2 import FileSystemLoader

from mypackages.utils.date import (
    to_year_month_string, get_next_month
)
from workscheduler.applications.services import (
    AffiliationQuery, OperatorQuery
)
from workscheduler.infrastructures import Database


def get_db_session(echo=False):
    if 'db_session' not in g:
        g.db_session = Database(current_app.config['DATABASE'], echo).create_session()
    return g.db_session


def close_db_session(e=None):
    db_session = g.pop('db_session', None)
    if db_session:
        db_session.commit()
        db_session.close()


def create_app(test_config=None):
    # create the application instance
    app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'statics'))
    app.jinja_loader = FileSystemLoader(os.path.join(os.path.dirname(__file__), 'views'))
    app.config.from_object(__name__)

    app.config.from_mapping(
        SECRET_KEY='jlk32dasf4562erHUI378sdf',
        DATABASE=os.path.join(app.instance_path, 'workscheduler.db')
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.update(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    app.config.from_envvar('WORK_SCHEDULER_SETTING', silent=True)

    sys.path.append(os.path.dirname(__file__))

    # todo: need to refactor below configure setting

    app.teardown_appcontext(close_db_session)

    # cli action
    @click.command('init-db')
    @with_appcontext
    def init_db_command():
        Database(current_app.config['DATABASE']).init()
        click.echo('Initialized the database.')
    app.cli.add_command(init_db_command)
    
    @click.command('set-test-db')
    @with_appcontext
    def set_test_db_command():
        Database(current_app.config['DATABASE']).set_test()
        click.echo('Set the database to test.')
    app.cli.add_command(set_test_db_command)

    from .controllers import (
        auths, menus, schedules, schedulers,
        operators, users, affiliations,
        skills, teams
    )

    app.register_blueprint(auths.bp)
    app.register_blueprint(menus.bp)
    app.register_blueprint(schedules.bp)
    app.register_blueprint(schedulers.bp)
    app.register_blueprint(operators.bp)
    app.register_blueprint(users.bp)
    app.register_blueprint(affiliations.bp)
    app.register_blueprint(skills.bp)
    app.register_blueprint(teams.bp)

    @app.errorhandler(404)
    def not_found(error):
        from flask import render_template
        return render_template('not-found.html'), 404
    
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auths.index'

    from workscheduler.applications.services import UserQuery

    @login_manager.user_loader
    def load_user(user_id):
        return UserQuery(get_db_session()).get_user(user_id)
    
    from flask_wtf import CSRFProtect
    
    csrf = CSRFProtect()
    csrf.init_app(app)

    @app.before_request
    def extend_jinja_env():
        app.jinja_env.globals['today'] = date.today()
        app.jinja_env.globals['next_month'] = to_year_month_string(get_next_month())
    
        def get_default_affiliation():
            return next(filter(lambda x: not x.is_not_affiliation(), AffiliationQuery(get_db_session()).get_affiliations()))
    
        app.jinja_env.globals['default_affiliation_id'] = get_default_affiliation().id
    
        def get_operator_id():
            operator_query = OperatorQuery(get_db_session())
            return operator_query.get_operator_of_user_id(current_user.id).id if current_user.is_authenticated else ""
    
        app.jinja_env.globals['operator_id'] = get_operator_id()
    
    return app
