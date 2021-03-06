import mock
from hamcrest import (
    assert_that,
    calling,
    equal_to,
    raises,
)

from rmatics.model.standings import StatementStandings
from rmatics.testutils import TestCase
from rmatics.utils.exceptions import GroupNotFound


class TestModel__statement_standings_serialize(TestCase):
    def setUp(self):
        super(TestModel__statement_standings_serialize, self).setUp()

        self.create_statements()
        self.create_user_groups()

    def test_simple(self):
        standings = StatementStandings(statement=self.statements[0])
        standings.json = {'some': 'data'}
        assert_that(
            standings.serialize(),
            equal_to(standings.json)
        )

    def test_filter_by_group_id(self):
        standings = StatementStandings(statement=self.statements[0])
        standings.json = {
            str(user.id): ''
            for user in self.users
        }
        assert_that(
            standings.serialize(group_id=self.groups[0].id),
            equal_to({
                '1': '',
            })
        )

    def test_group_not_found(self):
        standings = StatementStandings(statement=self.statements[0])
        assert_that(
            calling(standings.serialize).with_args(group_id='bad'),
            raises(GroupNotFound),
        )
