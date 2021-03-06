import time
import mock
from hamcrest import (
    assert_that,
    calling,
    equal_to,
    raises,
)

from rmatics.model import db
from rmatics.model.statement import Statement
from rmatics.model.user import User
from rmatics.testutils import TestCase
from rmatics.utils.exceptions import (
    StatementFinished,
    StatementNotStarted,
    StatementNotOlympiad,
)


class TestModel__statement_start(TestCase):
    def setUp(self):
        super(TestModel__statement_start, self).setUp()

        self.now = int(time.time())
        self.time_start = self.now - 60
        self.time_stop = self.now + 30

        self.statement = Statement(
            olympiad=1,
            time_start=self.time_start,
            time_stop=self.time_stop,
        )
        db.session.add(self.statement)

        self.user = User()
        db.session.add(self.user)

        db.session.flush()

    def test_simple(self):
        with mock.patch('rmatics.model.statement.time.time', mock.Mock(return_value=self.now)), \
                mock.patch('rmatics.model.statement.Statement.start_participant', mock.Mock()) as mock_start:
            self.statement.start(self.user)

        mock_start.assert_called_once_with(
            user=self.user,
            duration=self.time_stop - self.now,
            password=None,
        )

    def test_not_olympiad(self):
        statement = Statement(olympiad=0)
        db.session.add(statement)
        assert_that(
            calling(statement.start).with_args(self.user),
            raises(StatementNotOlympiad)
        )

    def test_not_started(self):
        with mock.patch('rmatics.model.statement.time.time', mock.Mock(return_value=self.time_start - 1)):
            assert_that(
                calling(self.statement.start).with_args(user=self.user),
                raises(StatementNotStarted)
            )

    def test_finished(self):
        with mock.patch('rmatics.model.statement.time.time', mock.Mock(return_value=self.time_stop)):
            assert_that(
                calling(self.statement.start).with_args(user=self.user),
                raises(StatementFinished)
            )

        with mock.patch('rmatics.model.statement.time.time', mock.Mock(return_value=self.time_stop + 10)):
            assert_that(
                calling(self.statement.start).with_args(user=self.user),
                raises(StatementFinished)
            )

