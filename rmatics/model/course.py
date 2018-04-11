from rmatics.model import db
from rmatics.utils.functions import attrs_to_dict


class Course(db.Model):
    __table_args__ = {'schema': 'moodle'}
    __tablename__ = 'mdl_course'

    id = db.Column(db.Integer, primary_key=True)

    full_name = db.Column('fullname', db.Unicode(254))
    short_name = db.Column('shortname', db.Unicode(100))

    category = db.Column(db.Integer)
    password = db.Column(db.Unicode(50))
    visible = db.Column(db.Boolean)

    def require_password(self):
        return bool(self.password)

    def serialize(self, attributes=None):
        if not attributes:
            attributes = (
                'id',
                'full_name',
                'short_name',
                'require_password',
            )
        serialized = attrs_to_dict(self, *attributes)
        if 'require_password' in attributes:
            serialized['require_password'] = self.require_password()
        return serialized
