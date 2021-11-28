import flask
from application import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Document):
    user_id = db.IntField(unique=True, nullabe=False)
    first_name = db.StringField(max_length=50, nullabe=False)
    last_name = db.StringField(max_length=50, nullabe=False)
    email = db.StringField(max_length=30, unique=True, nullabe=False)
    password = db.StringField(nullabe=False)
    vaccinated = db.StringField(nullabe=False)
    choice  = db.StringField()
    faculty_key = db.StringField(max_length=5)
    course_id = db.StringField(max_length=4)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def get_password(self, password):
        return check_password_hash(self.password, password)

class Course(db.Document):
    courseID   =   db.StringField( max_length=10, unique=True )
    title       =   db.StringField( max_length=100 )
    description =   db.StringField( max_length=255 )
    credits     =   db.IntField()
    term        =   db.StringField( max_length=25 )

class Enrollment(db.Document):
    user_id     =   db.IntField()
    courseID    =   db.StringField(max_length=10 )

class Post(db.Document):
    title = db.StringField(max_length=20)
    content = db.StringField(max_length=50)

class Preferences(db.Document):
    user_id     = db.IntField()
    courseID    = db.StringField(max_length=10)
    choice  = db.StringField(max_length=3)

class Date(db.Document):
    user_id     = db.IntField()
    startdate   = db.DateTimeField()
    enddate     = db.DateTimeField()