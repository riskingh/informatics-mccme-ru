from rmatics.model import db


class CourseModule(db.Model):
    __table_args__ = {'schema': 'moodle'}
    __tablename__ = 'mdl_course_modules'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column('course', db.Integer, db.ForeignKey('moodle.mdl_course.id'))
    instance = db.Column(db.Integer)
    module = db.Column(db.Integer)

    course = db.relationship('Course', backref='course_module')
