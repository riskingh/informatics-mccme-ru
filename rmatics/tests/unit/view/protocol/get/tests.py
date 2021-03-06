import mock
from hamcrest import (
    assert_that,
    has_entries,
)
from collections import OrderedDict

from rmatics.model.ejudge_run import EjudgeRun
from rmatics.testutils import TestCase
from rmatics.view.protocol import get_protocol


class TestView__get_protocol(TestCase):
    def setUp(self):
        super(TestView__get_protocol, self).setUp()

        self.contest_id = 1234
        self.run_id = 5678

    def _get_mocked_run(self,
                        count,
                        status_string,
                        host=None,
                        tests=None,
                        sample_tests=None,
                        ):
        """
        Создает замоканый run
        """
        run = mock.Mock()
        run.user.statement.filter = lambda *args: run.user.statement
        run.user.statement.count = lambda *args: count
        run.status_string = status_string
        run.tests = tests or {}
        run.host = host
        run.problem.sample_tests = ','.join(list(map(str, sample_tests or [1])))
        run.get_test_full_protocol = lambda str_num: 'full %s' % str_num
        run.compiler_output = ''
        return run

    def test_compilation_error(self):
        """
        В случае ошибки компиляции должна вернуться ошибка, которая лежит в run.compiler_output
        """
        run = self._get_mocked_run(count=0, status_string='CE')
        compiler_output = 'mocked compiler output'
        run.compiler_output = compiler_output

        with mock.patch.object(EjudgeRun, 'get_by', mock.Mock(return_value=run)):
            response = get_protocol(contest_id=self.contest_id, run_id=self.run_id)

        assert_that(
            response.json,
            has_entries({
                'compiler_output': compiler_output,
                'host': None,
                'tests': {},
            })
        )

    def test_ok(self):
        """
        Проверка формата в случае успешной посылки
        """
        tests = {
            '1': 'first',
            '2': 'second',
        }
        tests_protocol = {**tests, '1': 'full 1'}
        host = 'some host'
        run = self._get_mocked_run(
            count=0,
            status_string='OK',
            tests=tests,
            host=host,
        )
        compiler_output = 'mocked compiler output'
        run.compiler_output = compiler_output

        with mock.patch.object(EjudgeRun, 'get_by', mock.Mock(return_value=run)):
            response = get_protocol(contest_id=self.contest_id, run_id=self.run_id)

        assert_that(
            response.json,
            has_entries({
                'compiler_output': compiler_output,
                'host': host,
                'tests': OrderedDict(sorted(tests_protocol.items())),
            })
        )

    def test_samples(self):
        """
        Проверка обработки тестов из условия
        """
        tests = {
            '1': 'first',
            '2': 'second',
            '3': 'third',
            '4': 'forth'
        }
        tests_protocol = {**tests, '2': 'full 2', '3': 'full 3'}
        run = self._get_mocked_run(
            count=0,
            status_string='OK',
            tests=tests,
            sample_tests=[2, 3],
        )

        with mock.patch.object(EjudgeRun, 'get_by', mock.Mock(return_value=run)):
            response = get_protocol(contest_id=self.contest_id, run_id=self.run_id)

        assert_that(
            response.json,
            has_entries({
                'tests': OrderedDict(sorted(tests_protocol.items())),
            })
        )

