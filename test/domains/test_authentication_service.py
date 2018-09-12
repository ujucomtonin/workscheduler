# -*- coding: utf-8 -*-

from applications.services.authentication_service import AuthenticationService
from test.db_test_set import DbTestSetting
from infrastructures.db_connection import SessionContextFactory


class TestAuthenticationService:
    @classmethod
    def setup_class(cls):
        setting = DbTestSetting()
        setting.sqlite_db_initialize()
        cls.session = SessionContextFactory(setting.get_db_path())
    
    def test_login_true(self):
        with self.session.create() as session:
            user = AuthenticationService(session).login('admin', 'minAd')
        assert user is not None
    
    def test_login_false(self):
        user = AuthenticationService().login('admin', 'noNe')
        assert user is None
        user = AuthenticationService().login('none', 'minAd')
        assert user is None
        user = AuthenticationService().login('none', 'noNe')
        assert user is None
