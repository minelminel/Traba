# Traba
import os
import re
import ast
import json
import lorem
import random
import string
import datetime
import operator
import urllib.parse
import requests as HTTP
from pprint import pprint
from functools import wraps, reduce
from collections import OrderedDict
from distutils.util import strtobool
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
    PasswordField, SelectField, BooleanField,
    IntegerField, SubmitField, RadioField,
)
from wtforms.fields.html5 import EmailField 
from wtforms.validators import (
    DataRequired, Length, Email, EqualTo,
    ValidationError, InputRequired, Optional
)
from passlib.hash import sha256_crypt
from flask_mail import Mail, Message
from flask_wtf.csrf import CSRFProtect, CSRFError
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from data.data_import import (
    get_state_names_from_json,
    get_state_abbreviations_from_json,
    get_state_abbreviation,
    loadStatesEnMasse,
    loadCitiesEnMasse
)

"""-----------------------------------------------------------------------------
        # __init__
-----------------------------------------------------------------------------"""
project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(os.path.join(project_dir, "site.db"))
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


"""-----------------------------------------------------------------------------
        # models.py
-----------------------------------------------------------------------------"""
# Production
def generate_api_token(bits=32):
    """
    Generates an api token based from random alphanumeric characters
    """
    return ''.join(random.choices(string.ascii_letters + string.digits, k=bits))


class User_db(db.Model, SerializerMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    created_at = db.Column(db.DateTime(), nullable=False, default=datetime.datetime.utcnow())
    modified_at = db.Column(db.DateTime(), unique=False, nullable=True, onupdate=datetime.datetime.utcnow())
    apitoken = db.Column(db.String(32), unique=True, nullable=False, default=generate_api_token())
    confirmed = db.Column(db.Boolean, unique=False, default=False)
    name = db.Column(db.String(64), unique=False, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    username = db.Column(db.String(32), unique=True, nullable=False)
    password = db.Column(db.String(100), unique=False, nullable=False)
    is_admin = db.Column(db.Boolean, unique=False, default=False)

    def get_reset_token(self, expires_sec=60*30):
        s = Serializer(app.config["SECRET_KEY"], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User_db.query.get(user_id)


class Interaction_db(db.Model, SerializerMixin):
    __tablename__ = 'interactions'

    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    created_at = db.Column(db.DateTime(), nullable=False, default=datetime.datetime.utcnow())
    modified_at = db.Column(db.DateTime(), unique=False, nullable=True, onupdate=datetime.datetime.utcnow())
    author = db.Column(db.String(32), unique=False, nullable=False)
    channel = db.Column(db.String(32), nullable=False)
    company = db.Column(db.String(60), nullable=False)
    city = db.Column(db.String(32), nullable=False)
    state = db.Column(db.String(2), nullable=False)
    summary = db.Column(db.Text(), nullable=True)


class State_db(db.Model, SerializerMixin):
    __tablename__ = 'states'

    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    author = db.Column(db.String(100), unique=False, nullable=False)
    created_at = db.Column(db.DateTime(), nullable=False, default=datetime.datetime.utcnow())
    modified_at = db.Column(db.DateTime(), unique=False, nullable=True, onupdate=datetime.datetime.utcnow())
    name = db.Column(db.String(50), unique=True, nullable=False)
    abbreviation = db.Column(db.String(2), unique=True, nullable=False)
    capital = db.Column(db.String(100), unique=False, nullable=True, default='')
    taxfree = db.Column(db.Boolean, unique=False, nullable=True, default=False)
    flattax = db.Column(db.Boolean, unique=False, nullable=True, default=False)
    taxbrackets = db.Column(db.Integer, unique=False, nullable=True)
    lowrate = db.Column(db.Float, unique=False, nullable=True)
    highrate = db.Column(db.Float, unique=False, nullable=True)
    notes = db.Column(db.Text, unique=False, nullable=True, default="")
    # threshold = db.Column(db.String(40), unique=False, nullable=True, primary_key=False)


class City_db(db.Model, SerializerMixin):
    __tablename__ = 'city'

    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    created_at = db.Column(db.DateTime(), nullable=False, default=datetime.datetime.utcnow())
    modified_at = db.Column(db.DateTime(), unique=False, nullable=True, onupdate=datetime.datetime.utcnow())
    author = db.Column(db.String(32), unique=False, nullable=False)
    city = db.Column(db.String(50), unique=False, nullable=False, primary_key=False)
    state = db.Column(db.String(2), unique=False, nullable=False, primary_key=False)
    purchasing_power_index = db.Column(db.String(50), unique=False, nullable=True, primary_key=False)
    safety_index = db.Column(db.String(50), unique=False, nullable=True, primary_key=False)
    health_care_index = db.Column(db.String(50), unique=False, nullable=True, primary_key=False)
    climate_index = db.Column(db.String(50), unique=False, nullable=True, primary_key=False)
    cost_of_living_index = db.Column(db.String(50), unique=False, nullable=True, primary_key=False)
    property_price_to_income_ratio = db.Column(db.String(50), unique=False, nullable=True, primary_key=False)
    traffic_commute_time_index  = db.Column(db.String(50), unique=False, nullable=True, primary_key=False)
    pollution_index = db.Column(db.String(50), unique=False, nullable=True, primary_key=False)
    quality_sum = db.Column(db.String(50), unique=False, nullable=True, primary_key=False)
    notes = db.Column(db.Text, unique=False, nullable=True, primary_key=False)
    # salary = db.Column(db.Float, unique=False, nullable=True, primary_key=False)
    # rent = db.Column(db.Float, unique=False, nullable=True, primary_key=False)
    # home = db.Column(db.Float, unique=False, nullable=True, primary_key=False)
    # local_tax = db.Column(db.Float, unique=False, nullable=True, primary_key=False)
    # property_tax = db.Column(db.Float, unique=False, nullable=True, primary_key=False)
    # living_index = db.Column(db.Float, unique=False, nullable=True, primary_key=False)
    # food_index = db.Column(db.Float, unique=False, nullable=True, primary_key=False)
    # transit_index = db.Column(db.Float, unique=False, nullable=True, primary_key=False)
    # companies = db.Column(db.Text, unique=False, nullable=True, primary_key=False)
    # neighborhoods = db.Column(db.Text, unique=False, nullable=True, primary_key=False)
    # notes = db.Column(db.Text, unique=False, nullable=True, primary_key=False)


class Job_db(db.Model, SerializerMixin):
    __tablename__ = 'jobs'

    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    modified_at = db.Column(db.DateTime(), unique=False, nullable=True, onupdate=datetime.datetime.utcnow())
    created_at = db.Column(db.DateTime(), nullable=False, default=datetime.datetime.utcnow())
    author = db.Column(db.String(32), unique=False, nullable=False)
    position = db.Column(db.String(50), unique=False, nullable=False, primary_key=False)
    level = db.Column(db.String(50), unique=False, nullable=True, primary_key=False)
    company = db.Column(db.String(80), unique=False, nullable=False, primary_key=False)
    city = db.Column(db.String(50), unique=False, nullable=False, primary_key=False)
    state = db.Column(db.String(50), unique=False, nullable=False, primary_key=False)
    cotype = db.Column(db.String(20), unique=False, nullable=True, primary_key=False)
    salary = db.Column(db.Float, unique=False, nullable=True, primary_key=False)
    link = db.Column(db.String(500), unique=False, nullable=True, primary_key=False)
    contact = db.Column(db.String(80), unique=False, nullable=True, primary_key=False)
    hrtitle = db.Column(db.String(80), unique=False, nullable=True, primary_key=False)
    phone = db.Column(db.Integer, unique=False, nullable=True, primary_key=False)
    email = db.Column(db.String(80), unique=False, nullable=True, primary_key=False)
    description = db.Column(db.Text, unique=False, nullable=True, primary_key=False)
    experience = db.Column(db.Text, unique=False, nullable=True, primary_key=False)
    notes = db.Column(db.Text, unique=False, nullable=True, primary_key=False)


"""-----------------------------------------------------------------------------
        # utilities.py
-----------------------------------------------------------------------------"""
# unused
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

# unused
def remove_empty_keys(dic):
    """
    Returns a new dictionary with empty string values removed
    """
    return {k: v for k, v in dic.items() if v is not ''}

# unused
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

# Production
def execute_request(_request,_method,_route):
    _params = dict(_request.form)
    _params.pop('csrf_token')
    _path = os.path.join(_request.url_root,f'api/{_route}')
    _headers = {'Token': session['api_request_token']}
    if _method.upper() == 'POST':
        response = HTTP.post(_path,params=_params,headers=_headers)
    else:
        response = HTTP.get(_path,params=_params,headers=_headers)
    return response

# Beta
def get_states_from_db():
    # res = db.session.query(State_db).filter_by(author='admin').all()
    res = db.session.query(State_db).all()
    if res:
        name_long = []
        name_short = []
        for result in res:
            x = result.to_dict()
            name_long.append(x['name'])
            name_short.append(x['abbreviation'])
        return list(zip(name_short, name_long))
    return [('','')]

"""-----------------------------------------------------------------------------
        # decorators.py
-----------------------------------------------------------------------------"""
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

# Check if user is author of row
def is_author_of(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'nonexistant_parameter' in session:
            return f(*args, **kwargs)
        else:
            # flash('@is_author_of else condition', 'info')
            # return redirect(url_for('index'))
            _args = []
            for arg in args:
                _args.append(arg)
            _dict = {}
            for k, v in kwargs.items():
                _dict[k] = v
            return jsonify({'_args':_args,'_dict':_dict})
    return wrap

"""-----------------------------------------------------------------------------
        # users.py
-----------------------------------------------------------------------------"""
class RegisterForm(FlaskForm):
    name = StringField('Name', [Length(min=4, max=64), DataRequired()])
    email = EmailField('Email', [InputRequired("Please enter your email address."),
                                Email("This field requires a valid email address")])
    username = StringField('Username', [Length(min=4, max=32), DataRequired()])
    password = PasswordField('Password', [
        DataRequired('Please enter a password'),
        EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')

    def validate_username(self, username):
        if not (re.match('^[\w-]+$', username.data) is not None):
            raise ValidationError('Username can only contain alphanumeric characters with no spaces')
        res = User_db.query.filter_by(username=username.data).first()
        if res:
            raise ValidationError('This username is taken, please choose another.')

    def validate_email(self, email):
        res = User_db.query.filter_by(email=email.data).first()
        if res:
            raise ValidationError('This email is taken, please use another.')


class LoginForm(FlaskForm):
    username = StringField('Username', [Length(min=4, max=32), DataRequired()])
    password = PasswordField('Password', [DataRequired()])


class RequestResetForm(FlaskForm):
    email = EmailField('Email', [DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', [
        DataRequired(),
        EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')
    submit = SubmitField('Reset Password')


@app.route('/register', methods=['GET', 'POST'])
@is_logged_out
def register():
    form = RegisterForm(request.form)
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))
        db_data = {'name':name,'email':email,'username':username,'password':password}
        try:
            cls = User_db(**db_data)
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
            return render_template('site_register.html',form=form, error=error)
    return render_template('site_register.html',form=form)

@app.route('/login', methods=['GET','POST'])
@is_logged_out
def login():
    form = LoginForm(request.form)
    if form.validate_on_submit():
        username = request.form['username']
        password_candidate = request.form['password']
        result = User_db.query.filter_by(username=username).first()
        if result is not None:
            # Username exists
            if sha256_crypt.verify(password_candidate, result.password):
                session['logged_in'] = True
                session['username'] = username
                session['api_request_token'] = result.apitoken
                session['email'] = result.email
                session['name'] = result.name
                if result.is_admin == True: session['is_admin'] = True
                flash('You are now logged in', 'success')
                return redirect(url_for('dashboard'))
            else:
                error = 'Invalid password'
                return render_template('site_login.html', error=error, form=form)
        else:
            app.logger.info('NO USER')
            error = 'Username not found'
            return render_template('site_login.html', error=error, form=form)
    return render_template('site_login.html',form=form)

@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))

def send_reset_email(user):
    token = User_db.get_reset_token(user)
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
        user = User_db.query.filter_by(email=form.email.data).first()
        if user is None:
            flash('There is no account with that email, try registering first','info')
            return redirect(url_for('reset_request'))
        send_reset_email(user)
        flash(f'An email has been sent to {form.email.data} with instructions to reset your password','info')
        return redirect(url_for('login'))
    return render_template('site_reset_request.html',form=form)

@app.route('/reset_password/<token>',methods=['GET','POST'])
@is_logged_out
def reset_token(token):
    user = User_db.verify_reset_token(token)
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
    return render_template('site_reset_token.html', form=form)

@app.route('/new/token',methods=['POST'])
@is_logged_in
def new_token():
    result = User_db.query.filter_by(username=session['username']).first().to_dict()
    if result['apitoken'] == session['api_request_token']:
        try:
            new_token = generate_api_token()
            rows_changed = User_db.query.filter_by(username=session['username']).update(dict(apitoken=new_token))
            db.session.commit()
            session['api_request_token'] = new_token
            return redirect(url_for('settings'))
        except:
            db.session.rollback()
            flash('Internal server error','info')
            return redirect(url_for('settings'))
    else:
        flash('Internal server error', 'warning')
        return redirect(url_for('settings'))
    return redirect(url_for('settings'))

@app.route('/reset/user',methods=['POST'])
@is_logged_in
@is_admin
def reset_user():
    try:
        num_rows_deleted = db.session.query(User_db).filter(User_db.username != 'admin').delete()
        db.session.commit()
        flash(f'Reset {num_rows_deleted} users','success')
    except:
        db.session.rollback()
        flash('Internal server error','info')
    return redirect(url_for('admin_panel'))

"""-----------------------------------------------------------------------------
        # search.py
-----------------------------------------------------------------------------"""
@app.route('/search',methods=['GET','POST'])
@is_logged_in
def search_results():
    q = str(request.args.get('search'))
    username = session['username']
    job_list = []
    interaction_list = []
    city_list = []

    res = db.session.query(Job_db).filter_by(author=username).all()
    if res:
        for result in res:
            job_list.append(result.to_dict())

    res = db.session.query(Interaction_db).filter_by(author=username).all()
    if res:
        for result in res:
            interaction_list.append(result.to_dict())

    res = db.session.query(City_db).filter_by(author=username).all()
    if res:
        for result in res:
            city_list.append(result.to_dict())

    _dict =  {'job':job_list,
            'interaction':interaction_list,
            'city':city_list}
    _data = json.dumps(_dict, sort_keys=True, indent=4)

    return render_template('site_search.html',_data=_data,_q=q)

"""-----------------------------------------------------------------------------
        # admin.py
-----------------------------------------------------------------------------"""
@app.route('/admin')
@is_logged_in
@is_admin
def admin_panel():
    users = User_db.query.all()
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
    
    cities = City_db.query.all()
    all_cities = []
    if cities:
        for each in cities:
            x = each.to_dict()
            all_cities.append(x)

    jobs = Job_db.query.all()
    all_jobs = []
    if jobs:
        for each in jobs:
            x = each.to_dict()
            all_jobs.append(x)

    interactions = Interaction_db.query.all()
    all_interactions = []
    if interactions:
        for each in interactions:
            x = each.to_dict()
            all_interactions.append(x)

    return render_template('_admin_panel.html',_users=all_users,
        _states=all_states,_cities=all_cities,_jobs=all_jobs,_interactions=all_interactions)

@app.route('/export/users')
@is_logged_in
@is_admin
def export_users():
    res = User_db.query.all()
    DataList = []
    if res:
        for result in res:
            x = result.to_dict()
            del x['password']
            DataList.append(x)
    return jsonify(DataList)

@app.route('/export/states')
@is_logged_in
@is_admin
def export_states():
    res = State_db.query.all()
    DataList = []
    if res:
        for result in res:
            x = result.to_dict()
            DataList.append(x)
    return jsonify(DataList)

@app.route('/export/cities')
@is_logged_in
@is_admin
def export_cities():
    res = City_db.query.all()
    DataList = []
    if res:
        for result in res:
            x = result.to_dict()
            DataList.append(x)
    return jsonify(DataList)

@app.route('/export/interactions')
@is_logged_in
@is_admin
def export_interactions():
    res = Interaction_db.query.all()
    DataList = []
    if res:
        for result in res:
            x = result.to_dict()
            DataList.append(x)
    return jsonify(DataList)

@app.route('/export/jobs')
@is_logged_in
@is_admin
def export_jobs():
    res = Job_db.query.all()
    DataList = []
    if res:
        for result in res:
            x = result.to_dict()
            DataList.append(x)
    return jsonify(DataList)

@app.route('/email_users',methods=['GET'])
@is_logged_in
@is_admin
def email_users():
    return jsonify(request.args)

"""-----------------------------------------------------------------------------
        # views.py
-----------------------------------------------------------------------------"""
@app.route('/')
def index():
    return render_template('site_index.html')

# beta template for fancy home page
@app.route("/home", methods=['GET', 'POST'])
def home():
    return render_template("site_home.html")

@app.route('/api')
@app.route('/api/')
def api_splash():
    return render_template('site_api.html')

@app.route('/settings')
@is_logged_in
def settings():
    # get User config json from DB
    return render_template('user_settings.html')

@app.route('/dashboard')
@is_logged_in
def dashboard():
    now = datetime.datetime.now().strftime("%I:%M %p") + ' on ' + datetime.datetime.now().strftime("%a, %B %d 20%y")
    num_city = City_db.query.filter_by(author=session['username']).count()
    num_job = Job_db.query.filter_by(author=session['username']).count()
    num_inter = Interaction_db.query.filter_by(author=session['username']).count()
    return render_template('user_dashboard.html',now=now,num_city=num_city,num_job=num_job,num_inter=num_inter)

@app.route('/calendar')
@is_logged_in
def calendar():
    return render_template('user_calendar.html')

@app.route('/beta')
@is_logged_in
@is_author_of
def beta():
    return jsonify({'Response':'My response message'})
"""-----------------------------------------------------------------------------
        # city.py
-----------------------------------------------------------------------------"""
class CityForm(FlaskForm):
    id = IntegerField('ID *', [Optional()])
    author = StringField('Author *', [Optional()])
    city = StringField('City *', [Length(min=2, max=32), DataRequired()])
    state = SelectField('State *', choices=get_states_from_db())
    # state = SelectField('State *', choices=list(zip(get_state_abbreviations_from_json(), get_state_names_from_json())))
    purchasing_power_index = StringField('Purchasing Power Index', [Optional()])
    safety_index = StringField('Safety Index', [Optional()])
    health_care_index = StringField('Health Care Index', [Optional()])
    climate_index = StringField('Climate Index', [Optional()])
    cost_of_living_index = StringField('Cost Of Living Index', [Optional()])
    property_price_to_income_ratio = StringField('Property Price To Income Ratio', [Optional()])
    traffic_commute_time_index = StringField('Traffic Commute Time Index', [Optional()])
    pollution_index = StringField('Pollution Index', [Optional()])
    quality_sum = StringField('Quality Sum', [Optional()])
    notes = TextAreaField('Notes', [Optional()])


@app.route('/cities')
@is_logged_in
def cities():
    res = City_db.query.filter_by(author=session['username']).all()
    DataList = []
    if res:
        for result in res:
            DataList.append(result.to_dict())
    return render_template('view_cities.html',_cities=DataList)

@app.route('/add/city', methods=['GET','POST'])
@is_logged_in
def add_city():
    form = CityForm()
    if form.validate_on_submit():
        response = execute_request(_request=request,
                                    _method="POST",
                                    _route="city")
        # return jsonify(response.json()) # debugging
        if response.status_code == 200:
            flash(f'Successfully added {form.city.data}','success')
            return redirect(url_for('cities'))
        else:
            flash(f'Unable to add city, status code {response.status_code}','warning')
            return redirect(url_for('cities'))
    return render_template('add_city.html',form=form)

@app.route('/edit/city/<id>',methods=['GET','POST'])
@is_logged_in
def edit_city(id):
    form = CityForm()
    City = db.session.query(City_db).filter_by(id=id).first().to_dict()
    form.id.data = City['id']
    form.author.data = City['author']
    form.city.data = City['city']
    form.state.data = City['state']
    form.purchasing_power_index.data = City['purchasing_power_index']
    form.safety_index.data = City['safety_index']
    form.health_care_index.data = City['health_care_index']
    form.climate_index.data = City['climate_index']
    form.cost_of_living_index.data = City['cost_of_living_index']
    form.property_price_to_income_ratio.data = City['property_price_to_income_ratio']
    form.traffic_commute_time_index.data = City['traffic_commute_time_index']
    form.pollution_index.data = City['pollution_index']
    form.quality_sum.data = City['quality_sum']
    if form.validate_on_submit():
        response = execute_request(_request=request,
                                    _method="POST",
                                    _route="city")
        # return jsonify(response.json()) # DEBUGGING
        if response.status_code == 202:
            flash(f'Saved changes for {form.city.data}','success')
            return redirect(url_for('cities'))
        else:
            flash(f'Unable to update {form.city.data}, status code {response.status_code}','warning')
            return redirect(url_for('cities'))
    return render_template('edit_city.html',form=form,Back=request.referrer or url_for('cities'))

@app.route('/detail/city/<id>',methods=['GET'])
@is_logged_in
def detail_city(id):
    form = CityForm()
    City = db.session.query(City_db).filter_by(id=id).first().to_dict()
    form.id.data = City['id']
    form.author.data = City['author']
    form.city.data = City['city']
    form.state.data = City['state']
    form.purchasing_power_index.data = City['purchasing_power_index']
    form.safety_index.data = City['safety_index']
    form.health_care_index.data = City['health_care_index']
    form.climate_index.data = City['climate_index']
    form.cost_of_living_index.data = City['cost_of_living_index']
    form.property_price_to_income_ratio.data = City['property_price_to_income_ratio']
    form.traffic_commute_time_index.data = City['traffic_commute_time_index']
    form.pollution_index.data = City['pollution_index']
    form.quality_sum.data = City['quality_sum']
    Back = request.referrer or url_for('cities')
    return render_template('detail_city.html',form=form,Back=Back)

@app.route('/delete/city/<id>',methods=['GET'])
@is_logged_in
def delete_city(id):
    try:
        num_rows_deleted = db.session.query(City_db).filter_by(id=id).delete()
        db.session.commit()
        flash(f'Deleted {num_rows_deleted} city','success')
    except:
        db.session.rollback()
        flash('Internal server error','info')
    return redirect(url_for('cities'))

@app.route('/load/cities',methods=['POST'])
@is_logged_in
@is_admin
def load_cities():
    try:
        passed, failed = loadCitiesEnMasse(header_token=session['api_request_token'],debug=False)
        flash(f'Successfully loaded {passed}/{failed} cities from JSON','success')
        return redirect(url_for('admin_panel'))
    except:
        flash('Unable to load cities from JSON','warning')
        return redirect(url_for('admin_panel'))

@app.route('/reset/city',methods=['POST'])
@is_logged_in
def reset_city():
    try:
        username = session['username']
        if username == 'admin':
            num_rows_deleted = db.session.query(City_db).delete()
        else:
            num_rows_deleted = db.session.query(City_db).filter_by(author=username).delete()
        db.session.commit()
        flash(f'Reset {num_rows_deleted} cities','success')
    except:
        db.session.rollback()
        flash('Internal server error','info')
    return redirect(url_for('admin_panel')) if username == 'admin' else redirect(url_for('dashboard'))

"""-----------------------------------------------------------------------------
        # state.py
-----------------------------------------------------------------------------"""
class StateForm(FlaskForm):
    id = IntegerField('ID *',[Optional()])
    name = StringField('State *',[DataRequired()])
    abbreviation = StringField('Abbreviation *',[DataRequired()])
    capital = StringField('Capital',[Optional()])
    taxfree = BooleanField('Tax Free',[Optional()])
    flattax = BooleanField('Flat Tax',[Optional()])
    taxbrackets = IntegerField('Tax Brackets',[Optional()])
    lowrate = DecimalField('Low Rate (%)',[Optional()])
    highrate = DecimalField('High Rate (%)',[Optional()])
    notes = TextAreaField('Notes',[Optional()])
    author = StringField('Author *',[Optional()])


@app.route('/states')
@is_logged_in
def view_states():
    res = db.session.query(State_db).filter_by(author='admin').all()
    DataList = []
    for result in res:
        DataList.append(result.to_dict())
    return render_template('view_states.html',_states=DataList)

@app.route('/add/state',methods=['GET','POST'])
@is_logged_in
@is_admin
def add_state():
    form = StateForm()
    if form.validate_on_submit():
        response = execute_request(_request=request,
                                    _method="POST",
                                    _route="state")
        # return jsonify(response.json()) # debugging
        if response.status_code == 200:
            flash(f'Successfully added state','success')
            return redirect(url_for('view_states'))
        else:
            flash(f'Unable to add state, status code {response.status_code}','warning')
            return redirect(url_for('view_states'))
    return render_template('add_state.html',form=form)

@app.route('/edit/state/<id>',methods=['GET','POST'])
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

    if form.validate_on_submit():
        # hack-y solution to disappearing check boxes...
        _params = dict(request.form)
        checkboxes = ['flattax','taxfree']
        for box in checkboxes:
            if box not in request.form.keys():
                _params.update({box:'n'})

        _params.pop('csrf_token')
        _path = os.path.join(request.url_root,'api/state')
        _headers = {'Token': session['api_request_token']}
        response = HTTP.post(_path,params=_params,headers=_headers)
        if response.status_code == 202:
            flash(f'Saved changes for {form.name.data}','success')
            return redirect(url_for('admin_panel'))
        else:
            flash(f'Unable to update {form.name.data}','warning')
            return redirect(url_for('admin_panel'))
    return render_template('edit_state.html',form=form,Back=request.referrer or url_for('admin_panel'))

@app.route('/detail/state/<id>',methods=['GET'])
@is_logged_in
def detail_state(id):
    form = StateForm()
    State = db.session.query(State_db).filter_by(id=id).first().to_dict()
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
    Back = request.referrer or url_for('view_states')
    return render_template('detail_state.html',form=form,Back=Back)

@app.route('/delete/state/<id>',methods=['GET'])
@is_logged_in
@is_admin
def delete_state(id):
    try:
        num_rows_deleted = db.session.query(State_db).filter_by(id=id).delete()
        db.session.commit()
        flash(f'Deleted {num_rows_deleted} state','success')
    except:
        db.session.rollback()
        flash('Internal server error','info')
    return redirect(url_for('view_states'))

@app.route('/reset/states',methods=['POST'])
@is_logged_in
@is_admin
def reset_states():
    try:
        username = session['username']
        if username == 'admin':
            num_rows_deleted = db.session.query(State_db).delete()
        else:
            num_rows_deleted = db.session.query(State_db).filter_by(author=username).delete()
        db.session.commit()
        flash(f'Reset {num_rows_deleted} states','success')
    except:
        db.session.rollback()
        flash('Internal server error','info')
    return redirect(url_for('admin_panel')) if username == 'admin' else redirect(url_for('dashboard'))

@app.route('/load/states',methods=['POST'])
@is_logged_in
@is_admin
def load_states():
    try:
        passed, failed = loadStatesEnMasse(header_token=session['api_request_token'],debug=False)
        flash(f'Successfully loaded {passed}/{failed} states from JSON','success')
        return redirect(url_for('admin_panel'))
    except:
        flash('Unable to load states from JSON','warning')
        return redirect(url_for('admin_panel'))

"""-----------------------------------------------------------------------------
        # job.py
-----------------------------------------------------------------------------"""
class JobForm(FlaskForm):
    id = IntegerField('ID *')
    author = StringField('Author *')
    position = StringField('Position *', [DataRequired()])
    level = StringField('Level', [Optional()])
    company = StringField('Company *', [Length(min=1, max=200), DataRequired()])
    city = StringField('City *', [Length(min=1, max=30), DataRequired()])
    state = SelectField('State *', choices=get_states_from_db())
    # state = SelectField('State *', choices=list(zip(get_state_abbreviations_from_json(), get_state_names_from_json())))
    cotype = SelectField('Company Type', choices=[
                                        ('',''),('pub','Public'),
                                        ('priv','Private'),('np','Nonprofit'),
                                        ('gov','Government'),('edu','Education'),
                                        ('tp','3rd Party')],
                                        validators=[Optional()])
    salary = DecimalField('Salary',[Optional()])
    link = StringField('Link', [Optional()])
    contact = StringField('HR Contact', [Optional()])
    hrtitle = StringField('HR Title', [Optional()])
    phone = IntegerField('Phone #', [Optional()])
    email = EmailField('HR Email',[Optional()])
    description = TextAreaField('Description', [Optional()])
    experience = TextAreaField('Experience', [Optional()])
    notes = TextAreaField('Notes', [Optional()])


@app.route('/jobs')
@is_logged_in
def jobs():
    res = Job_db.query.filter_by(author=session['username']).all()
    DataList = []
    if res:
        for result in res:
            DataList.append(result.to_dict())
    return render_template('view_jobs.html',_data=DataList)

@app.route('/add/job', methods=['GET','POST'])
@is_logged_in
def add_job():
    form = JobForm()
    if form.validate_on_submit():
        response = execute_request(_request=request,
                                    _method="POST",
                                    _route="job")
        # return jsonify(response.json()) # debugging
        if response.status_code == 200:
            flash(f'Successfully added job','success')
            return redirect(url_for('jobs'))
        else:
            flash(f'Unable to add job, status code {response.status_code}','warning')
            return redirect(url_for('jobs'))
    return render_template('add_job.html',form=form)

@app.route('/detail/job/<id>', methods=['GET'])
@is_logged_in
def detail_job(id):
    form = JobForm()
    Data = db.session.query(Job_db).filter_by(id=id).first().to_dict()
    form.id.data = Data['id']
    form.author.data = Data['author']
    form.position.data = Data['position']
    form.level.data = Data['level']
    form.company.data = Data['company']
    form.city.data = Data['city']
    form.state.data = Data['state']
    form.cotype.data = Data['cotype']
    form.salary.data = Data['salary']
    form.link.data = Data['link']
    form.contact.data = Data['contact']
    form.hrtitle.data = Data['hrtitle']
    form.phone.data = Data['phone']
    form.email.data = Data['email']
    form.description.data = Data['description']
    form.experience.data = Data['experience']
    form.notes.data = Data['notes']
    return render_template('detail_job.html',form=form,Back=url_for('jobs'))

@app.route('/edit/job/<id>', methods=['GET','POST'])
@is_logged_in
def edit_job(id):
    form = JobForm()
    Data = db.session.query(Job_db).filter_by(id=id).first().to_dict()
    form.id.data = Data['id']
    form.author.data = Data['author']
    form.position.data = Data['position']
    form.level.data = Data['level']
    form.company.data = Data['company']
    form.city.data = Data['city']
    form.state.data = Data['state']
    form.cotype.data = Data['cotype']
    form.salary.data = Data['salary']
    form.link.data = Data['link']
    form.contact.data = Data['contact']
    form.hrtitle.data = Data['hrtitle']
    form.phone.data = Data['phone']
    form.email.data = Data['email']
    form.description.data = Data['description']
    form.experience.data = Data['experience']
    form.notes.data = Data['notes']
    if form.validate_on_submit():
        response = execute_request(_request=request,
                                    _method="POST",
                                    _route="job")
        # return jsonify(response.json()) # debugging
        if response.status_code == 202:
            flash(f'Saved changes','success')
            return redirect(url_for('jobs'))
        else:
            flash(f'Unable to update job, status code {response.status_code}','warning')
            return redirect(url_for('jobs'))
    return render_template('edit_job.html',form=form,Back=url_for('jobs'))

@app.route('/delete/job/<id>',methods=['GET'])
@is_logged_in
def delete_job(id):
    try:
        num_rows_deleted = db.session.query(Job_db).filter_by(id=id).delete()
        db.session.commit()
        flash(f'Deleted {num_rows_deleted} job','success')
    except:
        db.session.rollback()
        flash('Internal server error','info')
    return redirect(url_for('jobs'))

@app.route('/reset/job',methods=['POST'])
@is_logged_in
def reset_job():
    try:
        username = session['username']
        if username == 'admin':
            num_rows_deleted = db.session.query(Job_db).delete()
        else:
            num_rows_deleted = db.session.query(Job_db).filter_by(author=username).delete()
        db.session.commit()
        flash(f'Reset {num_rows_deleted} jobs','success')
    except:
        db.session.rollback()
        flash('Internal server error','info')
    return redirect(url_for('admin_panel')) if username == 'admin' else redirect(url_for('dashboard'))

"""-----------------------------------------------------------------------------
        # interaction.py
-----------------------------------------------------------------------------"""
class InteractionForm(FlaskForm):
    id = IntegerField('ID *')
    author = StringField('Author *')
    channel = RadioField('Channel *', validators=[DataRequired()],
        choices=[('EMAIL', 'Email'), ('CALL', 'Call'), ('INTERVIEW', 'Interview'),
                ('IRL', 'In-Person'), ('SOCIAL', 'Social Media')], default='EMAIL')
    company = StringField('Company *', [Length(min=1, max=200), DataRequired()])
    city = StringField('City *', [Length(min=1, max=30), DataRequired()])
    summary = TextAreaField('Summary')
    state = SelectField('State *', choices=get_states_from_db())
    # state = SelectField('State *', choices=list(zip(get_state_abbreviations_from_json(), get_state_names_from_json())))


@app.route('/interactions')
@is_logged_in
def interactions():
    res = Interaction_db.query.filter_by(author=session['username']).all()
    DataList = []
    if res:
        for result in res:
            DataList.append(result.to_dict())
    return render_template('view_interactions.html',_data=DataList)

@app.route('/add/interaction',methods=['GET','POST'])
@is_logged_in
def add_interaction():
    form = InteractionForm()
    if form.validate_on_submit():
        response = execute_request(_request=request,
                                    _method="POST",
                                    _route="interaction")
        # return jsonify(response.json()) # debugging
        if response.status_code == 200:
            flash(f'Saved changes','success')
            return redirect(url_for('interactions'))
        else:
            flash(f'Unable to add interaction, status code {response.status_code}','warning')
            return redirect(url_for('interactions'))
    return render_template('add_interaction.html',form=form)

@app.route('/detail/interaction/<id>',methods=['GET','POST'])
@is_logged_in
def detail_interaction(id):
    form = InteractionForm()
    Data = db.session.query(Interaction_db).filter_by(id=id).first().to_dict()
    form.id.data = Data['id']
    form.channel.data = Data['channel']
    form.company.data = Data['company']
    form.city.data = Data['city']
    form.state.data = Data['state']
    form.summary.data = Data['summary']
    form.author.data = Data['author']
    return render_template('detail_interaction.html',form=form,Back=url_for('interactions'))

@app.route('/edit/interaction/<id>',methods=['GET','POST'])
@is_logged_in
def edit_interaction(id):
    form = InteractionForm()
    Data = db.session.query(Interaction_db).filter_by(id=id).first().to_dict()
    form.id.data = Data['id']
    form.author.data = Data['author']
    form.channel.data = Data['channel']
    form.company.data = Data['company']
    form.city.data = Data['city']
    form.state.data = Data['state']
    form.summary.data = Data['summary']
    if form.validate_on_submit():
        response = execute_request(_request=request,
                                    _method="POST",
                                    _route="interaction")
        # return jsonify(response.json()) # debugging
        if response.status_code == 202:
            flash(f'Saved changes','success')
            return redirect(url_for('interactions'))
        else:
            flash(f'Unable to update interaction, status code {response.status_code}','warning')
            return redirect(url_for('interactions'))
    return render_template('edit_interaction.html',form=form,Back=request.referrer or url_for('interactions'))

@app.route('/delete/interaction/<id>',methods=['GET'])
@is_logged_in
def delete_interaction(id):
    try:
        num_rows_deleted = db.session.query(Interaction_db).filter_by(id=id).delete()
        db.session.commit()
        flash(f'Deleted {num_rows_deleted} interaction','success')
    except:
        db.session.rollback()
        flash('Internal server error','info')
    return redirect(url_for('interactions'))

@app.route('/reset/interaction',methods=['POST'])
@is_logged_in
def reset_interaction():
    try:
        username = session['username']
        if username == 'admin':
            num_rows_deleted = db.session.query(Interaction_db).delete()
        else:
            num_rows_deleted = db.session.query(Interaction_db).filter_by(author=session['username']).delete()
        db.session.commit()
        flash(f'Reset {num_rows_deleted} interactions','success')
    except:
        db.session.rollback()
        flash('Internal server error','info')
    return redirect(url_for('admin_panel')) if username == 'admin' else redirect(url_for('dashboard'))

"""-----------------------------------------------------------------------------
        # errors.py
-----------------------------------------------------------------------------"""
@app.errorhandler(404)
def not_found(e):
    Back = request.referrer or url_for('view_states')
    return render_template('error_404.html',Back=Back)

@app.errorhandler(CSRFError)
def csrf_error(reason):
    flash('Security alert','danger')
    return render_template('error_csrf.html', reason=reason), 400

"""-----------------------------------------------------------------------------
        # handlers.py
-----------------------------------------------------------------------------"""
def type_conversion(dic,convert_to,lst):

    def _string(arg):
        try:
            return str(arg)
        except:
            pass

    def _title(arg):
        try:
            return arg.title()
        except:
            pass

    def _upper(arg):
        try:
            return arg.upper()
        except:
            pass

    def _integer(arg):
        if arg.isdigit():
            return int(arg)
        else:
            pass

    def _float(arg):
        try:
            return float(arg)
        except:
            pass

    def _bool(arg):
        try:
            return strtobool(arg)
        except:
            pass

    def _pass(arg):
        return arg

    switcher = {
        'string': _string,
        'title': _title,
        'upper': _upper,
        'integer': _integer,
        'float': _float,
        'bool': _bool,
        'pass': _pass
    }

    func = switcher.get(convert_to, lambda: None)
    for each in lst:
        if each in dic:
            dic[each] = func(dic[each])
    return {k: v for k, v in dic.items() if v is not None}

def validate_credentials(headr):
    if 'Token' not in headr:
        return False
    header_token = str(headr.get('Token'))
    res = User_db.query.filter_by(apitoken=header_token).first()
    if not res:
        return False
    return res.to_dict()['username']

def parse_post_request(_db,_request,_instr):
    # Discard empty requests
    if not _request.args: return {'Error':'Empty request'}, 400
    # Validate request token
    username = validate_credentials(_request.headers)
    if not username: return {'Error':'Unauthorized request'}, 401
    # Convert from immutable dictionary
    _data = dict(_request.args)
    # Remove invalid keys from request
    valid_keys = reduce(operator.iconcat, _instr.values(), [])
    for k in list(_data.keys()):
        if k not in valid_keys:
            del _data[k]
    # Discard empty washed request
    if not _data: return {'Error':'No valid keys request'}, 400
    # Append author
    _data['author'] = username
    for k, v in _instr.items():
        _data = type_conversion(dic=_data,convert_to=k,lst=v)
    if 'id' not in _data:
        try:
            cls = _db(**_data)
            db.session.add(cls)
            db.session.commit()
            db_response, _code = (True, 200)
        except:
            db_response, _code = (False, 406)
    else:
        try:
            _id = _data.pop('id')
            # Validate author permission
            res = db.session.query(_db).filter_by(id=_id).first()
            if res:
                original_author = res.to_dict()['author']
            else:
                raise ValueError('No entry exists for id')
            if original_author == _data['author']:
                _ = db.session.query(_db).filter_by(id=_id).update(_data)
                db.session.commit()
                db_response, _code = (True, 202)
            else:
                raise ValueError('User does not have edit rights to this entry')
        except:
            db_response, _code = (False, 409)
    return {'data':_data,'db_response':db_response}, _code

def echo_request(request,route):
    try:
        _echo = OrderedDict()
        _echo['Route'] = os.path.join('/api',route)
        _echo['Token'] = request.headers.get('Token') if 'Token' in request.headers else None
        _echo['Data'] = request.args if request.args else None
        _echo['Keys'] = list(request.args.keys()) if request.args else None
        _echo['Values'] = list(request.args.values()) if request.args else None
        if _echo['Token'] is None and 'Token' in request.args.keys():
            _echo['Message'] = 'Token should be sent in request header'
        elif 'Token' in request.headers.keys():
            _echo['Message'] = 'Token acknowledged'
        else:
            _echo['Message'] = 'No token detected'
    except:
        _echo['Message'] = 'Unable to process request'
    return _echo

"""-----------------------------------------------------------------------------
        # api.py
-----------------------------------------------------------------------------"""
class ApiCity(Resource):
    def get(self):
        return echo_request(request=request,route='city')

    def post(self):
        to_string = ['purchasing_power_index',
                    'safety_index',
                    'health_care_index',
                    'climate_index',
                    'cost_of_living_index',
                    'property_price_to_income_ratio',
                    'traffic_commute_time_index',
                    'pollution_index',
                    'quality_sum',
                    'notes'
                    ]
        to_float = []
        to_integer = ['id']
        to_title = ['city']
        to_upper = ['state']
        to_bool = []
        to_pass = ['author']

        _instr = {
            'string':to_string,
            'float':to_float,
            'integer':to_integer,
            'title':to_title,
            'upper':to_upper,
            'bool':to_bool,
            'pass':to_pass
        }
        resp, code = parse_post_request(_db=City_db,
                                        _request=request,
                                        _instr=_instr)
        return resp, code


class ApiJob(Resource):
    def get(self):
        return echo_request(request=request,route='job')

    def post(self):
        to_string = ['position',
                    'level',
                    'company',
                    'link',
                    'contact',
                    'hrtitle',
                    'email',
                    'description',
                    'experience',
                    'notes'
                    ]
        to_float = ['salary']
        to_integer = ['id','phone']
        to_title = ['city']
        to_upper = ['state','cotype']
        to_bool = []
        to_pass = ['author']

        _instr = {
            'string':to_string,
            'float':to_float,
            'integer':to_integer,
            'title':to_title,
            'upper':to_upper,
            'bool':to_bool,
            'pass':to_pass
        }
        resp, code = parse_post_request(_db=Job_db,
                                        _request=request,
                                        _instr=_instr)
        return resp, code


class ApiInteraction(Resource):
    def get(self):
        return echo_request(request=request,route='interaction')

    def post(self):
        to_string = ['summary','company','channel']
        to_float = []
        to_integer = ['id']
        to_title = ['name','city']
        to_upper = ['abbreviation','state']
        to_bool = []
        to_pass = ['author']

        _instr = {
            'string':to_string,
            'float':to_float,
            'integer':to_integer,
            'title':to_title,
            'upper':to_upper,
            'bool':to_bool,
            'pass':to_pass
        }
        resp, code = parse_post_request(_db=Interaction_db,
                                        _request=request,
                                        _instr=_instr)
        return resp, code


class ApiState(Resource):
    def get(self):
        return echo_request(request=request,route='state')

    def post(self):
        to_string = ['notes']
        to_float = ['highrate','lowrate']
        to_integer = ['id','taxbrackets']
        to_title = ['name','capital']
        to_upper = ['abbreviation']
        to_bool = ['taxfree','flattax']
        to_pass = ['author']

        _instr = {
            'string':to_string,
            'float':to_float,
            'integer':to_integer,
            'title':to_title,
            'upper':to_upper,
            'bool':to_bool,
            'pass':to_pass
        }
        resp, code = parse_post_request(_db=State_db,
                                        _request=request,
                                        _instr=_instr)
        return resp, code


class ApiAuth(Resource):
    def get(self):
        return echo_request(request=request,route='auth')

    def post(self):
        if validate_credentials(request.headers) or validate_credentials(request.args):
            return {'Response':True}, 200
        else:
            return {'Response':False}, 410


"""-----------------------------------------------------------------------------
        # resources.py
-----------------------------------------------------------------------------"""
api.add_resource(ApiInteraction, '/api/interaction')
api.add_resource(ApiCity, '/api/city')
api.add_resource(ApiJob, '/api/job')
api.add_resource(ApiState, '/api/state')
api.add_resource(ApiAuth, '/api/auth')

"""-----------------------------------------------------------------------------
        # setup.py
-----------------------------------------------------------------------------"""
# CREATE ADMIN
def initialize_admin():
    result = User_db.query.filter_by(name='admin').first()
    if result is None:
        _data = {'name':'admin',
                'email':os.environ.get('TRABA_EMAIL'),
                'username':'admin',
                # 'password':sha256_crypt.encrypt(str(os.environ.get('TRABA_PASSW'))),
                'password':sha256_crypt.encrypt(str('!!')),
                'is_admin':True,
                }
        cls = User_db(**_data)
        db.session.add(cls)
        db.session.commit()
        app.logger.info(' * ADMIN CREATED')
    else:
        app.logger.info(' * ADMIN UNABLE TO BE CREATED')
        pass

# CREATE TESTER
def initialize_tester():
    result = User_db.query.filter_by(name='tester').first()
    if result is None:
        _data = {'name':'tester',
                'email':'test@test.test',
                'username':'tester',
                # 'password':sha256_crypt.encrypt(str(os.environ.get('TRABA_PASSW'))),
                'password':sha256_crypt.encrypt(str('!!')),
                'is_admin':False,
                }
        cls = User_db(**_data)
        db.session.add(cls)
        db.session.commit()
        app.logger.info(' * TESTER CREATED')
    else:
        app.logger.info(' * TESTER UNABLE TO BE CREATED')
        pass

"""-----------------------------------------------------------------------------
        # run.py
-----------------------------------------------------------------------------"""
if __name__ == '__main__':
    CreateDB()
    initialize_admin()
    initialize_tester()
    app.host = '0.0.0.0'
    app.port = 5000
    app.debug = True
    app.run()


# end of script