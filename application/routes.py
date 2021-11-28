from application import app
from flask import render_template, request, Response, redirect, flash, url_for, session, jsonify
from bson.json_util import dumps, loads
import json
import os, sys
from application.models import User, Course, Enrollment, Post, Date
from application.forms import LoginForm, RegisterForm, PostForm, DateForm, PreferenceForm
from flask_login import login_user, current_user, logout_user, login_required

@app.route("/")
@app.route("/index")
@app.route("/home")
def index():
    return render_template("index.html", index=True)


@app.route("/login", methods=['GET','POST'])
def login():

    if session.get('username'):
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        email       = form.email.data
        password    = form.password.data

        user = User.objects(email=email).first()

        if user and user.get_password(password):

            session['user_id'] = user.user_id
            session['username'] = user.first_name
            session['last_name'] = user.last_name
            session['vaccinated'] = user.vaccinated
            session['faculty_key'] = user.faculty_key
            session['course_id'] = user.course_id

            if user.faculty_key=="12345":
                flash(f"{user.first_name}, Sir/Madam you are successfully logged in!", "success")
                return redirect("/students")

            else:
       
                flash(f"{user.first_name}, you are successfully logged in!", "success")        
                return redirect("/user_profile")

        else:   
            flash("Sorry, something went wrong.","danger")
    return render_template("login.html", title="Login", form=form, login=True )

@app.route("/logout")
def logout():
    session['user_id'] = False
    session.pop('username',None)
    return redirect(url_for('index'))

@app.route("/courses/")
@app.route("/courses/<term>")
def courses(term=None):
    if term is None:
        term = "Odd"
    classes = Course.objects.order_by("courseID")
    return render_template("courses.html",courses=True, courseData=classes, term=term)

@app.route("/register", methods=['GET', 'POST'])
def register():
    if session.get('username'):
        return redirect(url_for('index'))
    form = RegisterForm()
    if form.validate_on_submit():
        user_id     = User.objects.count()
        print(user_id)
        user_id     += 1

        email       = form.email.data
        password    = form.password.data
        first_name  = form.first_name.data
        last_name   = form.last_name.data
       # if not form.faculty_key.data:
        #    faculty_key = "None"
        #else:
        faculty_key = form.faculty_key.data
        course_id = form.course_id.data    
        user = User(user_id=user_id, email=email, first_name=first_name, last_name=last_name, faculty_key=faculty_key, course_id=course_id)

        user.set_password(password)
        user.save()
        flash("You are successfully registered!","success")
        return redirect(url_for('enrollment'))
    return render_template("register.html", title="Register", form=form, register=True)


@app.route("/enrollment", methods=["GET","POST"])
def enrollment():
    if not session.get('username'):
        return redirect(url_for('login'))

    courseID = request.form.get('courseID')
    courseTitle = request.form.get('title')
    user_id = session.get('user_id')

    if courseID:
        if Enrollment.objects(user_id=user_id,courseID=courseID):
            flash(f"Oops! You are already registered in this course {courseTitle}!", "danger")
            return redirect(url_for("courses"))
        else:
            Enrollment(user_id=user_id,courseID=courseID).save()
            flash(f"You are enrolled in {courseTitle}!", "success")

    classes = list( User.objects.aggregate(*[
            {
                '$lookup': {
                    'from': 'enrollment', 
                    'localField': 'user_id', 
                    'foreignField': 'user_id', 
                    'as': 'r1'
                }
            }, {
                '$unwind': {
                    'path': '$r1', 
                    'includeArrayIndex': 'r1_id', 
                    'preserveNullAndEmptyArrays': False
                }
            }, {
                '$lookup': {
                    'from': 'course', 
                    'localField': 'r1.courseID', 
                    'foreignField': 'courseID', 
                    'as': 'r2'
                }
            }, {
                '$unwind': {
                    'path': '$r2', 
                    'preserveNullAndEmptyArrays': False
                }
            }, {
                '$match': {
                    'user_id': user_id
                }
            }, {
                '$sort': {
                    'courseID': 1
                }
            }
        ]))
    
    return render_template("enrollment.html", enrollment=True, title="Enrollment", classes=classes)    

@app.route("/api")
@app.route("/api/<idx>")
def api(idx=None):
    if(idx==None):
        jdata = courseData
    else:
        jdata = courseData[int(idx)]

    return Response(json.dumps(jdata), mimetype="application/json")

@app.route("/user")
def user():
    #User(user_id=1, first_name="Aishwarya", last_name="Deshmukh", email="ad@gmail.com", password = "ffs7789").save()
    users = User.objects.all()
    return render_template("user.html", users=users)

@app.route("/post/new",methods=['GET','POST'])
#@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        flash("Your post has been created","success")
        return redirect(url_for('index'))
    return render_template('new_post.html',title='New Post', new_post=True, form=form)

@app.route("/preferences", methods=['GET','POST'])
def preferences():
    form = PreferenceForm()

    if form.validate_on_submit():
        choice = form.choice.data
        vaccinated = form.vaccinated.data
        user_id = session.get("user_id")
        user = User.objects(user_id=user_id).first()
        user.update(choice=choice, vaccinated=vaccinated)        
        flash("Thank you for your preference","success")
        return redirect(url_for('user_profile'))
    return render_template("preferences.html", form=form, preferences=True)

@app.route("/date", methods=['GET','POST'])
def date_index():
    form = DateForm()
    if form.validate_on_submit():
        session['startdate'] = form.startdate.data
        session['enddate'] = form.enddate.data
        startdate = form.startdate.data
        enddate = form.enddate.data
        date = Date(startdate=startdate, enddate=enddate, user_id=session['user_id'])
        date.save()
        return redirect(url_for('reminder'))
    return render_template("date_index.html", form=form )

@app.route("/reminder", methods=['GET','POST'])
def reminder():
        user_id = session.get('user_id')
        user_reminders = list(Date.objects.aggregate([
        {
            '$lookup': {
                'from': 'date', 
                'localField': 'user_id', 
                'foreignField': 'user_id', 
                'as': 'r1'
            }
        }, {
            '$unwind': {
                'path': '$r1', 
                'includeArrayIndex': 'string', 
                'preserveNullAndEmptyArrays': False
            }
        }
        ]))
        return render_template("reminder.html", reminder=True, user_reminders=user_reminders)


@app.route("/date/display", methods=['GET','POST'])
def date():
    user_id = session['username']
    startdate = session['startdate']
    enddate = session['enddate']
    return render_template('date.html')

@app.route("/update_date", methods=["GET", "POST"])
def update_date():
    date = Date.objects(user_id=session["user_id"]).first()
    date.delete()
    return redirect(url_for('reminder'))

@app.route("/delete_date", methods=["GET","POST"])
def delete_date():

    user_id = request.form.get('user_id')
    date = Date.objects(user_id=user_id).first()
    date.delete()
    return redirect(url_for('reminder'))

@app.route("/delete_user", methods=["GET","POST"])
def delete_user():
    user_id = request.form.get('user_id')
    user = User.objects(user_id=user_id).first()
    user.delete()
    return redirect(url_for('students'))

@app.route("/students", methods=["GET","POST"])
def students():

    # Find out courseID of current faculty

    user = User.objects(user_id=session["user_id"]).first()
    courseID = "0000"
    if user:
        courseID = user.course_id
    #print(courseID)
    extractStudents = [
    {
        '$lookup': {
            'from': 'enrollment', 
            'localField': 'courseID', 
            'foreignField': 'courseID', 
            'as': 'r1'
        }
    }, {
        '$unwind': {
            'path': '$r1', 
            'includeArrayIndex': 'r1_id', 
            'preserveNullAndEmptyArrays': False
        }
    }, {
        '$lookup': {
            'from': 'user', 
            'localField': 'r1.user_id', 
            'foreignField': 'user_id', 
            'as': 'r2'
        }
    }, {
        '$unwind': {
            'path': '$r2', 
            'preserveNullAndEmptyArrays': False
        }
    }, {
        '$match': {
            'courseID': courseID
        }
    }, {
        '$sort': {
            'user_id': 1
        }
    }
]
    enrolled_students = list(Course.objects.aggregate(extractStudents))
    getStudentsData = dumps(enrolled_students, indent = 2)
    jsonStudentData = json.loads(getStudentsData)

    getListOfStudents = []
    students_count = len(jsonStudentData)

    # 50% available seats as per Covid-19 criteria
    available_seats = 5

    for d in range(len(jsonStudentData)):
        if jsonStudentData[d]["r2"]:
            if jsonStudentData[d]["r2"]["vaccinated"]=="Fully Vaccinated" and jsonStudentData[d]["r2"]["choice"]=="In-person":
                if available_seats>0:
                    getListOfStudents.append(jsonStudentData[d]["r2"]["first_name"])
                    available_seats-=1

    #checkCriteria(getListOfStudents)
    return render_template('students_enrolled.html', students=True,getListOfStudents=getListOfStudents, enrolled_students=jsonStudentData)

@app.route("/students_cleared", methods=["GET","POST"])
def students_cleared():
    l1 = students()
    
    print(dir(l1))
    cleared_students = None
    # User.objects(email=="abc@g.com").first()
    #print(cleared_students)
    return render_template("students_cleared.html", cleared_students=cleared_students)

@app.route("/user_profile", methods=["GET","POST"])
def user_profile():

    if not session.get('username'):
        return redirect(url_for('login'))

    user_id = session.get('user_id')
    first_name = session.get('username')
    last_name = session.get('last_name')
    email = session.get('email')
    vaccinated = session.get('vaccinated')
    choice = session.get('preference')

    return render_template("user_profile.html", user_profile=True, first_name=first_name,
    last_name=last_name, email=email, vaccinated=vaccinated, choice=choice)    


    clearedStudents = total_seats - clearedStudents
    print("No of vacant seats: ", clearedStudents)

@app.route("/guidelines", methods=["GET","POST"])
def guidelines():
    return render_template("guidelines.html")

# URL Error
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")

# Server Error
@app.errorhandler(500)
def page_not_found(e):
    return render_template("500.html")

