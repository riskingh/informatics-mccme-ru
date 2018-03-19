import logging
import pickle
import transaction

from pynformatics.contest.ejudge.ejudge_proxy import submit
from pynformatics.models import DBSession
from pynformatics.model.pynformatics_run import PynformaticsRun
from pynformatics.utils.context import Context
from pynformatics.utils.notify import notify_user


log = logging.getLogger('submit_queue')


def ejudge_error_notification(ejudge_response=None):
    code = None
    message = 'Ошибка отправки задачи'
    try:
        code = ejudge_response['code']
        message = ejudge_response['message']
    except Exception:
        pass
    return {
        'ejudge_error': {
            'code': code,
            'message': message,
        }
    }


class Submit:
    def __init__(self,
                 user_id,
                 file,
                 language_id,
                 ejudge_contest_id, # problem.ejduge_contest_id
                 ejudge_problem_id, # prob_id
                 ejudge_user_login,
                 ejudge_user_password,
                 ejudge_url,
                 statement_id=None,
                 ):
        self.user_id = user_id
        self.file = file
        self.language_id = language_id
        self.ejudge_contest_id = ejudge_contest_id
        self.ejudge_problem_id = ejudge_problem_id
        self.ejudge_user_login = ejudge_user_login
        self.ejudge_user_password = ejudge_user_password
        self.ejudge_url = ejudge_url
        self.statement_id = statement_id

    def encode(self):
        return pickle.dumps(self)

    @staticmethod
    def decode(encoded):
        return pickle.loads(encoded)

    def send(self):
        try:
            ejudge_response = submit(
                run_file=self.file.file,
                contest_id=self.ejudge_contest_id,
                prob_id=self.ejudge_problem_id,
                lang_id=self.language_id,
                login=self.ejudge_user_login,
                password=self.ejudge_user_password,
                filename=self.file.filename,
                url=self.ejudge_url,
                user_id=self.user_id
            )
        except Exception:
            log.exception('Unknown Ejudge submit error')
            notify_user(
                user_id=self.user_id,
                data=ejudge_error_notification(),
            )
            return

        try:
            if ejudge_response['code'] != 0:
                notify_user(
                    user_id=self.user_id,
                    data=ejudge_error_notification(ejudge_response)
                )
                return

            run_id = ejudge_response['run_id']
        except Exception:
            log.exception('ejudge_proxy.submit returned bad value')
            notify_user(
                user_id=self.user_id,
                data=ejudge_error_notification(),
            )
            return

        pynformatics_run = PynformaticsRun(
            run_id=run_id,
            contest_id=self.ejudge_contest_id,
            statement_id=self.statement_id,
            source=self.file.value.decode('unicode_escape'),
        )
        pynformatics_run = DBSession.merge(pynformatics_run)
        DBSession.flush([pynformatics_run])
        # DBSession.refresh(pynformatics_run)
        DBSession.refresh(pynformatics_run.run)

        notify_user(
            user_id=self.user_id,
            runs=[
                pynformatics_run.run.serialize(
                    Context(
                        user_id=self.user_id,
                        problem_id=self.problem_id,
                        statement_id=self.statement_id,
                    )
                )
            ],
        )

        transaction.commit()
