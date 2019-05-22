# Traba
import os
import re
import ast
import json
import random
import string
import datetime
import urllib.parse
from functools import wraps
from createDB import CreateDB
from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    redirect,
    url_for,
    flash,
    session,
    logging
)
from flask_api import (
    FlaskAPI,
    status,
    exceptions
)
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin
from flask_wtf import Form, FlaskForm
from wtforms import (
    StringField, TextAreaField, DecimalField,
    PasswordField, validators, SelectField,
    IntegerField, SubmitField, RadioField,
    BooleanField,
)
from wtforms.fields.html5 import EmailField 
from passlib.hash import sha256_crypt
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask_mail import Mail, Message
from flask_wtf.csrf import CSRFProtect, CSRFError

from data.data_import import get_state_names_from_json, get_state_abbreviations_from_json, get_state_abbreviation

"""-----------------------------------------------------------------------------"""
project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(os.path.join(project_dir, "trabaDB.db"))
app = Flask(__name__)
csrf = CSRFProtect()
api = Api(app, decorators=[csrf.exempt])
app.config["SQLALCHEMY_DATABASE_URI"] = database_file
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "correcthorsebatterystaple"
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('TRABA_EMAIL')
app.config['MAIL_PASSWORD'] = os.environ.get('TRABA_PASSW')
mail = Mail(app)
db = SQLAlchemy(app)
csrf.init_app(app)

"""-----------------------------------------------------------------------------"""
# HELPER FUNCTIONS
def pop_underscored_keys(dic):
	"""
    Removes all keys beginning with an underscore.
    Function DOES NOT CREATE A NEW DICT, rather,
        it modifies the dict in-place.
    """
	list_keys = list(dic.keys())
	for k in list_keys:
		if k.startswith('_'):
			dic.pop(k)
	return dic


def remove_empty_keys(dic):
    """
    Returns a new dictionary with empty string values removed
    """
    return {k: v for k, v in dic.items() if v is not ''}


def y_to_boolean(dic):
    for k in dic.keys():
        if dic[k] == 'y':
            dic[k] = True
        else:
            pass


def only_updated_keys(old,new):
	"""
	Function takes in 2 dictionaries and returns a dictionary
	containing ONLY key-value pairs which have been changed.
	Function DOES modify NEW dictionary in-place.
	"""
	for k in list(new.keys()):
		if (old[k] == new[k]) or (old[k] == None and new[k] == ""):
			new.pop(k)
	return new


def generate_api_token(bits=16):
    """
    Generates an api token based from random alphanumeric characters
    """
    return ''.join(random.choices(string.ascii_letters + string.digits, k=bits))



"""-----------------------------------------------------------------------------"""
# MODELS
"""-----------------------------------------------------------------------------"""
class Users(db.Model, SerializerMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    created_at = db.Column(db.DateTime(), nullable=False, default=datetime.datetime.utcnow())
    modified_at = db.Column(db.DateTime(), unique=False, nullable=True)
    apitoken = db.Column(db.String(16), unique=True, nullable=False, default=generate_api_token())
    confirmed = db.Column(db.Boolean, unique=False, default=False)
    name = db.Column(db.String(64), unique=False, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    username = db.Column(db.String(32), unique=True, nullable=False)
    password = db.Column(db.String(100), unique=False, nullable=False)
    is_admin = db.Column(db.Boolean, unique=False, default=False)

    def get_reset_token(self, expires_sec=1800):
        # default expiration time is 30 minutes
        s = Serializer(app.config["SECRET_KEY"], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return Users.query.get(user_id)


class Interaction_db(db.Model, SerializerMixin):
    __tablename__ = 'interactions'

    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    created_at = db.Column(db.DateTime(), nullable=False, default=datetime.datetime.utcnow())
    modified_at = db.Column(db.DateTime(), unique=False, nullable=True)
    Channel = db.Column(db.String(32), nullable=False)
    Company = db.Column(db.String(60), nullable=False)
    City = db.Column(db.String(32), nullable=False)
    State = db.Column(db.String(2), nullable=False)
    Summary = db.Column(db.Text(), nullable=True)
    username = db.Column(db.String(32), unique=False, nullable=False)


class State_db(db.Model, SerializerMixin):
    __tablename__ = 'states'

    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    created_at = db.Column(db.DateTime(), nullable=False, default=datetime.datetime.utcnow())
    modified_at = db.Column(db.DateTime(), unique=False, nullable=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    abbreviation = db.Column(db.String(2), unique=True, nullable=False)
    # _zipcode = db.Column(db.Text, unique=False, nullable=True, default='0')
    capital = db.Column(db.String(100), unique=False, nullable=True)
    taxfree = db.Column(db.Boolean, unique=False, nullable=True, default=False)
    flattax = db.Column(db.Boolean, unique=False, nullable=True, default=False)
    taxbrackets = db.Column(db.Integer, unique=False, nullable=True)
    lowrate = db.Column(db.Float, unique=False, nullable=True)
    highrate = db.Column(db.Float, unique=False, nullable=True)
    notes = db.Column(db.Text, unique=False, nullable=True, default="")


class City_dbII(db.Model, SerializerMixin):
    __tablename__ = 'city2'

    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    created_at = db.Column(db.DateTime(), nullable=False, default=datetime.datetime.utcnow())
    modified_at = db.Column(db.DateTime(), unique=False, nullable=True)
    
    Purchasing_Power_Index = db.Column(db.String(50), unique=False, nullable=True, primary_key=False)
    Safety_Index = db.Column(db.String(50), unique=False, nullable=True, primary_key=False)
    Health_Care_Index = db.Column(db.String(50), unique=False, nullable=True, primary_key=False)
    Climate_Index = db.Column(db.String(50), unique=False, nullable=True, primary_key=False)
    Cost_of_Living_Index = db.Column(db.String(50), unique=False, nullable=True, primary_key=False)
    Property_Price_to_Income_Ratio = db.Column(db.String(50), unique=False, nullable=True, primary_key=False)
    Traffic_Commute_Time_Index  = db.Column(db.String(50), unique=False, nullable=True, primary_key=False)
    Pollution_Index = db.Column(db.String(50), unique=False, nullable=True, primary_key=False)
    Quality_Sum = db.Column(db.String(50), unique=False, nullable=True, primary_key=False)

    City = db.Column(db.String(50), unique=False, nullable=False, primary_key=False)
    State = db.Column(db.String(50), unique=False, nullable=True, primary_key=False) # eventually not nullable
    Abbreviation = db.Column(db.String(2), unique=False, nullable=True, primary_key=False) # eventually not nullable

    Salary = db.Column(db.Float, unique=False, nullable=True, primary_key=False)
    Coli = db.Column(db.Float, unique=False, nullable=True, primary_key=False)
    Rent = db.Column(db.Float, unique=False, nullable=True, primary_key=False)
    Home = db.Column(db.Float, unique=False, nullable=True, primary_key=False)
    StateBrackets = db.Column(db.String(10), unique=False, nullable=True, primary_key=False)
    Top_Income_Range = db.Column(db.String(40), unique=False, nullable=True, primary_key=False)
    Tax_Rate = db.Column(db.String(30), unique=False, nullable=True, primary_key=False)
    LocalTax = db.Column(db.Float, unique=False, nullable=True, primary_key=False)
    PropertyTax = db.Column(db.Float, unique=False, nullable=True, primary_key=False)
    Living = db.Column(db.Float, unique=False, nullable=True, primary_key=False)
    Food = db.Column(db.Float, unique=False, nullable=True, primary_key=False)
    Transit = db.Column(db.Float, unique=False, nullable=True, primary_key=False)
    Companies = db.Column(db.Text, unique=False, nullable=True, primary_key=False)
    Neighborhoods = db.Column(db.Text, unique=False, nullable=True, primary_key=False)
    Notes = db.Column(db.Text, unique=False, nullable=True, primary_key=False)


class City_db(db.Model, SerializerMixin):
    __tablename__ = 'cities'

    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    modified_at = db.Column(db.DateTime(), unique=False, nullable=True)
    created_at = db.Column(db.DateTime(), nullable=False, default=datetime.datetime.utcnow())
    City = db.Column(db.String(50), unique=False, nullable=False, primary_key=False)
    State = db.Column(db.String(50), unique=False, nullable=False, primary_key=False)
    Salary = db.Column(db.Float, unique=False, nullable=True, primary_key=False)
    Coli = db.Column(db.Float, unique=False, nullable=True, primary_key=False)
    Rent = db.Column(db.Float, unique=False, nullable=True, primary_key=False)
    Home = db.Column(db.Float, unique=False, nullable=True, primary_key=False)
    StateTax = db.Column(db.Float, unique=False, nullable=True, primary_key=False)
    LocalTax = db.Column(db.Float, unique=False, nullable=True, primary_key=False)
    PropertyTax = db.Column(db.Float, unique=False, nullable=True, primary_key=False)
    Living = db.Column(db.Float, unique=False, nullable=True, primary_key=False)
    Food = db.Column(db.Float, unique=False, nullable=True, primary_key=False)
    Transit = db.Column(db.Float, unique=False, nullable=True, primary_key=False)
    Companies = db.Column(db.Text, unique=False, nullable=True, primary_key=False)
    Neighborhoods = db.Column(db.Text, unique=False, nullable=True, primary_key=False)
    Notes = db.Column(db.Text, unique=False, nullable=True, primary_key=False)



class Job_db(db.Model, SerializerMixin):
    __tablename__ = 'jobs'

    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    City = db.Column(db.String(50), unique=False, nullable=False, primary_key=False)
    State = db.Column(db.String(50), unique=False, nullable=False, primary_key=False)
    Position = db.Column(db.String(50), unique=False, nullable=False, primary_key=False)
    Level = db.Column(db.String(50), unique=False, nullable=True, primary_key=False)
    Company = db.Column(db.String(80), unique=False, nullable=False, primary_key=False)
    Type = db.Column(db.String(20), unique=False, nullable=True, primary_key=False)
    Salary = db.Column(db.Float, unique=False, nullable=True, primary_key=False)
    Link = db.Column(db.String(500), unique=False, nullable=True, primary_key=False)
    Contact = db.Column(db.String(80), unique=False, nullable=True, primary_key=False)
    Title = db.Column(db.String(80), unique=False, nullable=True, primary_key=False)
    Phone = db.Column(db.Integer, unique=False, nullable=True, primary_key=False)
    Email = db.Column(db.String(80), unique=False, nullable=True, primary_key=False)
    Description = db.Column(db.Text, unique=False, nullable=True, primary_key=False)
    Experience = db.Column(db.Text, unique=False, nullable=True, primary_key=False)
    Notes = db.Column(db.Text, unique=False, nullable=True, primary_key=False)
    modified_at = db.Column(db.DateTime(), unique=False, nullable=True)
    created_at = db.Column(db.DateTime(), nullable=False, default=datetime.datetime.utcnow())


"""-----------------------------------------------------------------------------"""
def handleAddCityreq(request_dict):
    if ''.join(request_dict.values()).strip() == '':
        return (None, 'Empty request')
    titleStrings = set(['City','State','Abbreviation'])
    request_keys = set(list(request_dict.keys()))
    if not titleStrings.issubset(request_keys):
        return (None, 'Required request keys not present')
    for key, val in request_dict.items():
        if isdigit(val): request_dict[key] = float(val)
    return (request_dict, '[200] handleAddCityreq()')


"""-----------------------------------------------------------------------------"""
def handleAddJobreq(request_dict):
    if ''.join(request_dict.values()).strip() == '':
        return None
    else:
        titleStrings = ['City','Position','Level','Type','Contact','Title']
        floatStrings = ['Salary']
        intStrings = ['Phone']
        textStrings = ['State','Link','Email','Company','Description','Experience','Notes']
        try:
            for each in titleStrings:
                if request_dict[each] == '':
                    request_dict[each] = None
                else:
                    request_dict[each] = request_dict[each].title()
            for each in floatStrings:
                if request_dict[each] == '':
                    request_dict[each] = None
                else:
                    request_dict[each] = float(request_dict[each])
            for each in intStrings:
                if request_dict[each] == '':
                    request_dict[each] = None
                else:
                    request_dict[each] = int(''.join(re.findall(r'\d+',request_dict[each])))
            for each in textStrings:
                if request_dict[each] == '':
                    request_dict[each] = None
                else:
                    pass
            return request_dict
        except:
            return None


"""-----------------------------------------------------------------------------"""
# Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please log in', 'danger')
            return redirect(url_for('login'))
    return wrap


# Check if user is admin
def is_admin(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'is_admin' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized', 'danger')
            return redirect(url_for('index'))
    return wrap


# Check if user logged out
def is_logged_out(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' not in session:
            return f(*args, **kwargs)
        else:
            flash('This action is not available while logged in', 'info')
            return redirect(url_for('dashboard'))
    return wrap


"""-----------------------------------------------------------------------------"""
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))


"""-----------------------------------------------------------------------------"""
class RegisterForm(FlaskForm):
    name = StringField('Name', [validators.Length(min=1, max=64), validators.DataRequired()])
    email = EmailField('Email', [validators.InputRequired("Please enter your email address."), validators.Email("This field requires a valid email address")])
    username = StringField('Username', [validators.Length(min=4, max=32), validators.DataRequired()])
    password = PasswordField('Password', [
        validators.DataRequired('Please enter a password'),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')


@app.route('/register', methods=['GET', 'POST'])
@is_logged_out
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST':
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))
        db_data = {'name':name,'email':email,'username':username,'password':password}
        try:
            cls = Users(**db_data)
            db.session.add(cls)
            db.session.commit()
            db_response = True
        except:
            db_response = False
        if db_response:
            flash('You are now registered and can log in', 'success')
            return redirect(url_for('login'))
        else:
            error = 'Unable to create account'
            return render_template('register.html',form=form, error=error)
    return render_template('register.html',form=form)


"""-----------------------------------------------------------------------------"""
class LoginForm(FlaskForm):
    username = StringField('Username', [validators.Length(min=4, max=32), validators.DataRequired()])
    password = PasswordField('Password', [validators.DataRequired()])


@app.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST':
        username = request.form['username']
        password_candidate = request.form['password']
        result = Users.query.filter_by(username=username).first()
        if result is not None:
            # Username exists
            if sha256_crypt.verify(password_candidate, result.password):
                session['logged_in'] = True
                session['username'] = username
                session['api_request_token'] = result.apitoken
                session['email'] = result.email
                if result.is_admin == True: session['is_admin'] = True
                flash('You are now logged in', 'success')
                return redirect(url_for('dashboard'))
            else:
                error = 'Invalid password'
                return render_template('login.html', error=error, form=form)
        else:
            app.logger.info('NO USER')
            error = 'Username not found'
            return render_template('login.html', error=error, form=form)
    return render_template('login.html',form=form)


"""-----------------------------------------------------------------------------"""
class RequestResetForm(FlaskForm):
    email = EmailField('Email', [validators.DataRequired(), validators.Email()])
    submit = SubmitField('Request Password Reset')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')
    submit = SubmitField('Reset Password')


def send_reset_email(user):
    token = Users.get_reset_token(user)
    msg = Message('Password Reset Request',
                sender='traba.app@gmail.com',
                recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)


@app.route('/reset_password',methods=['GET','POST'])
@is_logged_out
def reset_request():
    form = RequestResetForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            flash('There is no account with that email, try registering first','info')
            return redirect(url_for('reset_request'))
        send_reset_email(user)
        flash(f'An email has been sent to {form.email.data} with instructions to reset your password','info')
        return redirect(url_for('login'))
    return render_template('reset_request.html',form=form)


@app.route('/reset_password/<token>',methods=['GET','POST'])
@is_logged_out
def reset_token(token):
    user = Users.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        password = sha256_crypt.encrypt(str(form.password.data))
        try:
            user.password = password
            db.session.commit()
            db_response = True
        except:
            db_response = False
        if db_response:
            flash('Your password has been updated', 'success')
            return redirect(url_for('login'))
        else:
            flash('Unable reset password', 'warning')
            return redirect(url_for('reset_request'))
    return render_template('reset_token.html', form=form)


"""-----------------------------------------------------------------------------"""
@app.route('/search',methods=['GET','POST'])
@is_logged_in
def search_results():
    q = str(request.args.get('search'))
    # //
    # Fill out logic here
    # //
    return render_template('search.html',_data=q)
# eventually, set a route to POST to handle query, then redirect to GET page


"""-----------------------------------------------------------------------------"""
@app.route('/newtoken',methods=['POST'])
@is_logged_in
def newtoken():
    result = Users.query.filter_by(username=session['username']).first().to_dict()
    if result['apitoken'] == session['api_request_token']:
        try:
            new_token = generate_api_token()
            rows_changed = Users.query.filter_by(username=session['username']).update(dict(apitoken=new_token))
            db.session.commit()
            session['api_request_token'] = new_token
            flash('Re-generated token','success')
            return redirect(url_for('settings'))
        except:
            db.session.rollback()
            flash('Internal server error','info')
            return redirect(url_for('settings'))
    else:
        flash('Internal server error', 'warning')
        return redirect(url_for('settings'))
    return redirect(url_for('settings'))


"""-----------------------------------------------------------------------------"""
@app.route('/reset_city',methods=['POST'])
@is_logged_in
def reset_city():
    try:
        num_rows_deleted = db.session.query(City_dbII).delete()
        db.session.commit()
        flash(f'Reset {num_rows_deleted} cities','success')
    except:
        db.session.rollback()
        flash('Internal server error','info')
    return redirect(url_for('dashboard'))


"""-----------------------------------------------------------------------------"""
@app.route('/reset_job',methods=['POST'])
@is_logged_in
def reset_job():
    try:
        num_rows_deleted = db.session.query(Job_db).delete()
        db.session.commit()
        flash(f'Reset {num_rows_deleted} jobs','success')
    except:
        db.session.rollback()
        flash('Internal server error','info')
    return redirect(url_for('dashboard'))


"""-----------------------------------------------------------------------------"""
@app.route('/reset_interaction',methods=['POST'])
@is_logged_in
def reset_interaction():
    try:
        num_rows_deleted = db.session.query(Interaction_db).delete()
        db.session.commit()
        flash(f'Reset {num_rows_deleted} interactions','success')
    except:
        db.session.rollback()
        flash('Internal server error','info')
    return redirect(url_for('dashboard'))


"""-----------------------------------------------------------------------------"""
@app.route('/reset_states',methods=['POST'])
@is_logged_in
def reset_states():
    try:
        num_rows_deleted = db.session.query(State_db).delete()
        db.session.commit()
        flash(f'Reset {num_rows_deleted} states','success')
    except:
        db.session.rollback()
        flash('Internal server error','info')
    return redirect(url_for('dashboard'))


"""-----------------------------------------------------------------------------"""
@app.route('/')
def index():
    return render_template('index.html')


"""-----------------------------------------------------------------------------"""
# beta template for fancy home page
@app.route("/home", methods=["GET", "POST"])
def home():
    return render_template("home.html")


"""-----------------------------------------------------------------------------"""
@app.route('/admin')
@is_logged_in
@is_admin
def admin_panel():
    # get all Users and make a table
    users = Users.query.all()
    all_users = []
    for each in users:
        x = each.to_dict()
        del x['password']
        all_users.append(x)

    states = State_db.query.all()
    all_states = []
    if states:
        for each in states:
            x = each.to_dict()
            all_states.append(x)
    return render_template('adminpanel.html',_users=all_users,_states=all_states)


"""-----------------------------------------------------------------------------"""
@app.route('/settings')
@is_logged_in
def settings():
    # get User config json from DB
    return render_template('settings.html')


"""-----------------------------------------------------------------------------"""
@app.route('/dashboard')
@is_logged_in
def dashboard():
    now = datetime.datetime.now().strftime("%I:%M %p") + ' on ' + datetime.datetime.now().strftime("%a, %B %d 20%y")
    num_city = City_dbII.query.count()
    num_job = Job_db.query.count()
    num_inter = Interaction_db.query.count()
    return render_template('dashboard.html',now=now,num_city=num_city,num_job=num_job,num_inter=num_inter)


"""-----------------------------------------------------------------------------"""
@app.route('/addcity', methods=["GET","POST"])
@is_logged_in
def addcity():
    if request.method == "POST":
        request_dict = {}
        for field in request.form:
            request_dict[field] = request.form[field]
        Data = handleAddCityreq(request_dict)
        # check if city already exists in database, ask if user wants to edit
        db_response = False
        try:
            cls = City_db(**Data)
            db.session.add(cls)
            db.session.commit()
            db_response = True
        except:
            pass
        flash('City successfully created', 'success') if db_response else flash('Could not create city', 'warning')
        return redirect(url_for('dashboard'))
    States = get_state_abbreviations_from_json()
    return render_template('addcity.html',States=States)


"""-----------------------------------------------------------------------------"""
@app.route('/addjob', methods=["GET","POST"])
@is_logged_in
def addjob():
    if request.method == "POST":
        request_dict = {}
        for field in request.form:
            request_dict[field] = request.form[field]
        Data = handleAddJobreq(request_dict)
        # check if city already exists in database
        db_response = False
        try:
            cls = Job_db(**Data)
            db.session.add(cls)
            db.session.commit()
            db_response = True
        except:
            pass
        flash('Job successfully created', 'success') if db_response else flash('Could not create job', 'warning')
        return redirect(url_for('dashboard'))
    States = get_state_abbreviations_from_json()
    return render_template('addjob.html',States=States)


"""-----------------------------------------------------------------------------"""
    # id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    # created_at = db.Column(db.DateTime(), nullable=False, default=datetime.datetime.utcnow())
    # modified_at = db.Column(db.DateTime(), unique=False, nullable=True)
    # name = db.Column(db.String(50), unique=True, nullable=False)
    # abbreviation = db.Column(db.String(2), unique=True, nullable=False)
    # capital = db.Column(db.String(100), unique=False, nullable=True)
    # taxfree = db.Column(db.Boolean, unique=False, nullable=True, default=False)
    # flattax = db.Column(db.Boolean, unique=False, nullable=True, default=False)
    # taxbrackets = db.Column(db.Integer, unique=False, nullable=True)
    # lowrate = db.Column(db.Float, unique=False, nullable=True)
    # highrate = db.Column(db.Float, unique=False, nullable=True)
    # notes = db.Column(db.Text, unique=False, nullable=True)
class StateForm(FlaskForm):
    id = IntegerField('ID')
    name = StringField('State')
    abbreviation = StringField('Abbreviation')
    capital = StringField('Capital')
    taxfree = BooleanField('Tax Free?')
    flattax = BooleanField('Flat Tax?')
    taxbrackets = IntegerField('Tax Brackets')
    lowrate = DecimalField('Low Rate')
    highrate = DecimalField('High rate')
    notes = TextAreaField('Notes')
    author = StringField('Author')


@app.route('/edit/state/<id>',methods=["GET","POST"])
@is_logged_in
@is_admin
def edit_state(id):
    form = StateForm()
    State = db.session.query(State_db).filter_by(id=id).first().to_dict()
    form.id.data = State['id']
    form.name.data = State['name']
    form.abbreviation.data = State['abbreviation']
    form.capital.data = State['capital']
    form.taxfree.data = State['taxfree']
    form.flattax.data = State['flattax']
    form.taxbrackets.data = State['taxbrackets']
    form.lowrate.data = State['lowrate']
    form.highrate.data = State['highrate']
    form.notes.data = State['notes']
    form.author.data = session['username']
    if request.method == 'POST':
        _data = dict(request.form)
        # _id = _data.pop('id')
        del_list = ['csrf_token','author']
        for each in del_list:
            del _data[each]
        # y_to_boolean(_data)
        try:
            _data = only_updated_keys(State,_data)
            # return jsonify({'_data':_data,'_id':_id}) # debugging
            if not _data: return redirect(url_for('admin_panel'))
            _ = db.session.query(State_db).filter_by(id=id).update(_data)
            db.session.commit()
            db_response = True
        except:
            db_response = False
        if db_response:
            flash(f'Saved changes for {form.name.data}','success')
            return redirect(url_for('admin_panel'))
        else:
            flash(f'Unable to update {form.name.data}','warning')
            return redirect(url_for('admin_panel'))
    return render_template('editstate.html',form=form)


"""-----------------------------------------------------------------------------"""
@app.route('/cities')
@is_logged_in
def cities():
    results = City_dbII.query.all()
    CityList = []
    Flag = True
    if results:
        for result in results:
            CityList.append(result.to_dict())
        Flag = False
    return render_template('cities.html',Cities=CityList,Flag=Flag)


"""-----------------------------------------------------------------------------"""
@app.route('/jobs')
@is_logged_in
def jobs():
    results = Job_db.query.all()
    JobList = []
    Flag = True
    if results:
        for result in results:
            JobList.append(result.to_dict())
        Flag = False
    return render_template('jobs.html',Jobs=JobList,Flag=Flag)


"""-----------------------------------------------------------------------------"""
@app.route('/interactions')
@is_logged_in
def interactions():
    username = session['username']
    result = []
    res = Interaction_db.query.filter_by(username=username).all()
    if len(res):
        Flag = False
        for _, r in enumerate(res):
            result.append(r.to_dict())
        for res in result:
            for key in list(res.keys()):
                if key != key.title():
                    res.pop(key) # scrub result for non-capitalized keys (blacklist)
    else:
        Flag = True
    return render_template('interactions.html',result=result,Flag=Flag)
    # return jsonify({'result':result}) # debugging


"""-----------------------------------------------------------------------------"""
class InteractionForm(FlaskForm):
    Channel = RadioField('Channel', validators=[validators.DataRequired()],
        choices=[('email', 'Email'), ('call', 'Call'), ('interview', 'Interview'), ('irl', 'In-Person'), ('social', 'Social Media')], default='email')
    Company = StringField('Company', [validators.Length(min=1, max=200), validators.DataRequired()])
    City = StringField('City', [validators.Length(min=1, max=30), validators.DataRequired()])
    Summary = TextAreaField('Summary')
    State = SelectField('State', choices=list(zip(get_state_abbreviations_from_json(), get_state_names_from_json())))


@app.route('/addinteraction',methods=['GET','POST'])
@is_logged_in
def addinteraction():
    form = InteractionForm(request.form)
    if form.validate_on_submit():
        _data = form.data
        _data['username'] = session['username']
        del _data['csrf_token']
        try:
            cls = Interaction_db(**_data)
            db.session.add(cls)
            db.session.commit()
            db_response = True
        except:
            db_response = False
        # return jsonify({'_data':_data,'db_response':db_response}) # debugging
        if db_response:
            flash('Saved', 'success')
            return redirect(url_for('interactions'))
        else:
            flash('Server error','error')
            return redirect(url_for('addinteraction'))
    return render_template('addinteraction.html',form=form)


"""-----------------------------------------------------------------------------"""
@app.route('/calendar')
@is_logged_in
def calendar():
    return render_template('calendar.html')


"""-----------------------------------------------------------------------------"""
@app.errorhandler(404)
def not_found(e):
    Back = request.referrer or url_for('index')
    return render_template('404.html',Back=Back)


@app.errorhandler(CSRFError)
def csrf_error(reason):
    flash('Security alert','danger')
    return render_template('csrf_error.html', reason=reason), 400

"""-----------------------------------------------------------------------------"""
# BETA
@app.route('/beta')
def beta():
    return render_template('beta.html')

"""-----------------------------------------------------------------------------"""
class ApiSplash(Resource):

    def get(self):
        return jsonify({
                'host':'localhost:5000',
                'endpoints':['/api/city','/api/job'],
                'methods':['GET','POST'],
                'classes':['cities','jobs','info','query'],
                'message':'welcome, user!',
                'token':'not required'
                })
    def post(self):
        if bool(request.args):
            return jsonify({
                'data':request.args,
                'path':{'url':request.url,
                'encoded':urllib.parse.quote_plus(request.url)}
                })
        else:
            return jsonify({'host':'localhost:5000',
                    'endpoints':['/city','/job'],
                    'methods':['GET','POST'],
                    'message':'welcome, user!',
                    'token':'not required'})


class ApiCity(Resource):
    def get(self):
        data = request.args
        keys = list(request.args.keys())
        values = list(request.args.values())
        return jsonify({'Data':data,'Keys':keys,'Values':values})

    def post(self):
        if not ''.join(list(request.args.values())):
            return {'error':'empty request'}
        requiredArgs = ['State','City']
        db_keys = dict.fromkeys(list(City_dbII.__table__.columns.keys()))
        user_keys = request.args.to_dict()
        # Screen for required keys
        for arg in requiredArgs:
            if arg not in list(user_keys.keys()):
                return {'error':'required args not present'}
            else:
                pass
        # Remove non-capitalized columns (blacklist)
        for arg in list(db_keys.keys()):
            if arg != arg.title(): db_keys.pop(arg)
        # Scrub user request
        for arg in list(user_keys.keys()):
            if arg not in list(db_keys.keys()): user_keys.pop(arg)
        # Replace state abbreviation
        user_keys['State'] = get_state_abbreviation(user_keys['State'])
        try:
            cls = City_dbII(**user_keys)
            db.session.add(cls)
            db.session.commit()
            db_response = True
        except:
            db_response = False
        return {'db_keys':db_keys,'user_keys':user_keys,'db_response':db_response}


        # PROTOTYPE
            # if City_dbII.query.first() is None:
            #     return {'col names':list(City_dbII.__table__.columns.keys())}

            # try:
            #     valid_list = list(City_dbII.query.first().to_dict().keys())
            # except:
            #     return {'Error':'Could not query City DB because it is empty'}
                # try:
                #     db_response = False
                #     cls = City_dbII({'City':''})
                #     db.session.add(cls)
                #     db.session.commit()
                #     db_response = True
                # except:
                #     db_response = False
                # return jsonify({'Error':'City DB is empty, Initializing null row.',
                #         'DB Response':db_response})

            # hidden_keys = ['id','created_at','modified_at']
            # for thing in hidden_keys:
                # if thing in valid_list: valid_list.remove(thing)
            # valid_list is now good to compare against
            # ** check to make sure City and State are present, otherwise Error. for now assume safe case
            # user_keys = list(request.args.keys())
            # >>> items = set([-1, 0, 1, 2])
            # >>> set([1, 2]).issubset(items)
            # user_filtered = {}
            # for keey in user_keys:
            #     if keey in valid_list:
            #         # get the users data and add to dict
            #         user_filtered[keey] = request.args[keey]
            # Data, resp_msg = handleAddCityreq(user_filtered)
            # check if city already exists in database, respond with error message, for now add new row
            # q = City_db.query().first().filter(City_db.City == Data['City'])
            # db_response = False
            # try:
            #     cls = City_dbII(**Data)
            #     db.session.add(cls)
            #     db.session.commit()
            #     db_response = True
            # except:
            #     pass
            # return jsonify({'valid keys':valid_list,
            #                 'user keys':user_keys,
            #                 'filtered request':Data,
            #                 'db response':db_response,
            #                 'function msg':resp_msg})


def verify_api_token(_data):
    _res = Users.query.filter_by(username=_data['username']).first()
    if _res:
        _res = _res.to_dict()
        if _res['apitoken'] != _data['token']:
            is_valid = False
        else:
            is_valid = True
    else:
        is_valid = False
    return is_valid


class ApiJob(Resource):
    def get(self):
        data = request.args
        keys = list(request.args.keys())
        values = list(request.args.values())
        return jsonify({'Data':data,'Keys':keys,'Values':values})


class ApiState(Resource):
    def get(self):
        data = request.args
        keys = list(request.args.keys())
        values = list(request.args.values())
        return jsonify({'Data':data,'Keys':keys,'Values':values})
    
    def post(self):
        data = request.args
        if not bool(data): return {'error':'empty request'}
        # make sure admin token is present and valid, del from dict
        # return jsonify({'Data':data,'Keys':list(request.args.keys()),'Values':list(request.args.values()),'Boolean':bool(data)}) # debugging
        try:
            cls = State_db(**data)
            db.session.add(cls)
            db.session.commit()
            db_response = True
        except:
            db_response = False
        return {'data':data,'db_response':db_response}


class ApiAuth(Resource):
    def get(self):
        _req = request.args.to_dict()
        try:
            _data = {key:_req[key] for key in ['apitoken','username']}
        except:
            return {'route':'auth','response':'1 or more required keys missing'}, 400
        if verify_api_token(_data):
            return {'route':'auth','response':'verified'}, 202
        else:
            return {'route':'auth','response':'false'}, 406

"""-----------------------------------------------------------------------------"""
api.add_resource(ApiSplash, '/api')
api.add_resource(ApiCity, '/api/city')
api.add_resource(ApiJob, '/api/job')
api.add_resource(ApiState, '/api/state')
api.add_resource(ApiAuth, '/api/auth')

"""-----------------------------------------------------------------------------"""
# CREATE ADMIN
def initialize_admin():
    result = Users.query.filter_by(name='admin').first()
    if result is None:
        _data = {'name':'admin',
                'email':os.environ.get('TRABA_EMAIL'),
                'username':'admin',
                'password':sha256_crypt.encrypt(str(os.environ.get('TRABA_PASSW'))),
                'is_admin':True,
                }
        cls = Users(**_data)
        db.session.add(cls)
        db.session.commit()
        app.logger.info(' * ADMIN CREATED')
    else:
        pass

"""-----------------------------------------------------------------------------"""
if __name__ == '__main__':
    CreateDB()
    initialize_admin()
    app.host = '0.0.0.0'
    app.port = 5000
    app.debug = True
    app.run()

