from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from wtforms import  DateField, DateTimeField
from application.models import User

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = StringField("Password", validators=[DataRequired(), Length(min=6, max=15)])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Login")


class RegisterForm(FlaskForm):
    email = StringField("Email",validators=[DataRequired(), Email()])
    password = StringField("Password", validators=[DataRequired(), Length(min=6, max=15)])
    password_confirm = StringField("Confirm Password", validators=[DataRequired(), Length(min=6, max=15),
     EqualTo('password')])
    first_name = StringField("First Name", validators=[DataRequired(), Length(min=2, max=55)])
    last_name = StringField("Last Name", validators=[DataRequired(), Length(min=2, max=55)])
    vaccinated = StringField("Vaccination Status", default="Not Vaccinated")
    faculty_key = StringField("Faculty Secret Key")
    course_id =  StringField("Course ID")

    submit = SubmitField("Register Now")

    def validate_email(self,email):
        user = User.objects(email=email.data).first()
        if user:
            raise ValidationError("Email is already in use, use another one")

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = StringField('Content',validators=[DataRequired()])
    submit = SubmitField("Post")

class PreferenceForm(FlaskForm):
    myChoices = ["In-person","Remote"]
    vaccinationChoices = ["Not Vaccinated", "Partially Vaccinated", "Fully Vaccinated"]
    choice = SelectField(u'Please choose your preference:', choices = myChoices, validators = [DataRequired()])
    vaccinated = SelectField(u'Vaccination Status:', choices = vaccinationChoices, validators = [DataRequired()])
    submit = SubmitField("Post")
    
class DateForm(FlaskForm):
    startdate   = DateField('Start Date ',  format='%Y-%m-%d', validators=[DataRequired()])
    enddate   = DateField('End Date ', format="%Y-%m-%d", validators=[DataRequired()])
    submit = SubmitField("Submit")

