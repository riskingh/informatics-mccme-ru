import mock
from flask import g
from hamcrest import (
    assert_that,
    contains_inanyorder
)

from rmatics.model import db
from rmatics.model.ejudge_run import EjudgeRun
from rmatics.model.problem import EjudgeProblem, Problem
from rmatics.model.pynformatics_run import PynformaticsRun
from rmatics.model.statement import Statement
from rmatics.model.user import SimpleUser
from rmatics.testutils import TestCase
from rmatics.view.problem import problem_runs


class TestView__problem_runs(TestCase):
    def setUp(self):
        super(TestView__problem_runs, self).setUp()

        self.create_problems()
        self.create_statements()
        self.create_users()

        self.user1 = self.users[0]
        self.user2 = self.users[1]
        self.problem = self.problems[0]

        self.runs = [
            [
                EjudgeRun(
                    run_id=i + user.ejudge_id * 3,
                    problem=self.problem,
                    user=user
                )
                for i in range(3)
            ]
            for user in [self.user1, self.user2]
        ]
        db.session.add_all(self.runs[0])  # user1 runs
        db.session.add_all(self.runs[1])  # user2 runs
        db.session.flush()

        # self.request.matchdict = {'problem_id': self.problem.id}
        # self.mock_context = mock.Mock()
        # self.mock_context.problem = self.session.query(Problem).all()[0]
        # self.mock_context.user = self.user1

    def test_filters_by_user_id(self):
        with mock.patch('rmatics.model.ejudge_run.EjudgeRun.serialize', autospec=True) as serialize_mock:
            serialize_mock.side_effect = lambda self, *args: 'serialized'
            with self.app.test_request_context():
                g.user = self.user1
                response = problem_runs(self.problem.id)

        assert_that(
            response.json.keys(),
            contains_inanyorder(
                *[str(run.run_id) for run in self.runs[0]]
            )
        )

    def test_filter_by_statement_id(self):
        # Для двух посылок их трех у каждого пользователя задаем statement_id
        for i in range(2):
            for (statement, run) in zip(self.statements, self.runs[i]):
                db.session.add(
                    PynformaticsRun(
                        run=run,
                        statement_id=statement.id
                    )
                )

        with mock.patch('rmatics.model.ejudge_run.EjudgeRun.serialize', autospec=True) as serialize_mock, \
                mock.patch('rmatics.model.ejudge_run.EjudgeRun.get_sources', mock.Mock(return_value='')):
            serialize_mock.side_effect = lambda self, *args: 'serialized'
            with self.app.test_request_context(query_string={'statement_id': self.statements[0].id}):
                g.user = self.user1
                response = problem_runs(self.problems[0].id)

        assert_that(
            response.json.keys(),
            contains_inanyorder(
                str(self.runs[0][0].run_id),
                str(self.runs[1][0].run_id),
            )
        )
