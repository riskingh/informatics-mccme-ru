from hamcrest import (
    assert_that,
    equal_to,
)

from pynformatics.testutils import TestCase
from pynformatics.contest.ejudge.submit_queue import peek_all_submits


class TestAPI__problem_submits_v2(TestCase):
    def setUp(self):
        super(TestAPI__problem_submits_v2, self).setUp()

        self.create_problems()
        self.create_users()
    
    def send_request(self, user_id=None, problem_id=None):
        if user_id:
            self.set_session({'user_id': user_id})
        response = self.app.post(
            url=f'/problem/{problem_id}/submit_v2',
            params={
                'lang_id': 27,
            },
            upload_files=[('file', 'source.py', b'print(1)')],
        )
        return response
    
    def test_simple(self):
        response = self.send_request(
            user_id=self.users[0].id,
            problem_id=self.problems[0].id,
        )
        
        assert_that(
            response.json,
            equal_to({
                'id': 1,
                'user_id': self.users[0].id,
                'problem_id': self.problems[0].id,
                'source': 'print(1)',
                'language_id': 27,
            })
        )
        assert_that(
            len(peek_all_submits()),
            equal_to(1)
        )
