from flask import (
    g,
    jsonify,
    Blueprint,
)

from rmatics.ejudge.submit_queue import peek_user_submits
from rmatics.view import require_auth

submit = Blueprint('submit', __name__, url_prefix='/submit')


@submit.route('/')
@require_auth
def submit_get():
    submits = peek_user_submits(user_id=g.user.id)
    return jsonify([
        submit.serialize()
        for submit in submits
    ])

