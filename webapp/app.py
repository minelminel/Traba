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
from wtforms import (
    Form, StringField, TextAreaField,
    PasswordField, validators, SelectField,
    IntegerField, SubmitField, RadioField,
    validators
)
from wtforms.fields.html5 import EmailField 
from passlib.hash import sha256_crypt
from data.data_import import get_state_names_from_json, get_state_abbreviations_from_json, get_state_abbreviation

"""-----------------------------------------------------------------------------"""
project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(os.path.join(project_dir, "trabaDB.db"))
app = Flask(__name__)
api = Api(app)
app.config["SQLALCHEMY_DATABASE_URI"] = database_file
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

"""-----------------------------------------------------------------------------"""
def generateToken(bits=16):
	return ''.join(random.choices(string.ascii_letters + string.digits, k=bits))
"""-----------------------------------------------------------------------------"""
"""
note on db columns... if __attr__ is Titled: whitelist[], else: blacklist[]
blacklist attributes are NOT safe to display to user return in query !!!!!!!
"""

class Users(db.Model, SerializerMixin):
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    created_at = db.Column(db.DateTime(), nullable=False, default=datetime.datetime.utcnow())
    modified_at = db.Column(db.DateTime(), unique=False, nullable=True)
    token = db.Column(db.String(16), unique=True, nullable=False, default=generateToken())
    confirmed = db.Column(db.Boolean, unique=False, default=False)
    name = db.Column(db.String(64), unique=False, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    username = db.Column(db.String(32), unique=True, nullable=False)
    password = db.Column(db.String(100), unique=False, nullable=False)


class Interaction_db(db.Model, SerializerMixin):
    Id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    created_at = db.Column(db.DateTime(), nullable=False, default=datetime.datetime.utcnow())
    modified_at = db.Column(db.DateTime(), unique=False, nullable=True)
    Channel = db.Column(db.String(32), nullable=False)
    Company = db.Column(db.String(60), nullable=False)
    City = db.Column(db.String(32), nullable=False)
    State = db.Column(db.String(2), nullable=False)
    Summary = db.Column(db.Text(), nullable=True)
    username = db.Column(db.String(32), unique=False, nullable=False)


class City_dbII(db.Model, SerializerMixin):
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


    # def __repr__(self):
    #     return "<ID: {}><City: {}><State: {}><Salary: {}><Median Rent: {}><Median Home: {}>\
    #         <Cost of Living Index: {}><State Tax: {}><Local Tax: {}><Property Tax: {}>\
    #         <Living Cost: {}><Food Cost: {}><Transit Index: {}><Companies: {}>\
    #         <Neighborhoods: {}><Notes: {}><Modified: {}><Created: {}>"\
    #         .format(self.id,self.City,self.State,self.Salary,self.Rent,self.Home,self.Coli,
    #         self.StateTax,self.LocalTax,self.PropertyTax,self.Living,self.Food,
    #         self.Transit,self.Companies,self.Neighborhoods,self.Notes,self.modified_at,self.created_at)


class Job_db(db.Model, SerializerMixin):
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

    # def __repr__(self):
    #     return "<ID: {}><City: {}><State: {}><Position: {}><Level: {}><Company: {}>\
    #         <Type: {}><Salary: {}><Link: {}><Contact: {}><Title: {}><Phone: {}>\
    #         <Email: {}><Description: {}><Experience: {}><Notes: {}><Modified: {}><Created: {}>"\
    #         .format(self.id,self.City,self.State,self.Position,self.Level,self.Company,self.Type,
    #         self.Salary,self.Link,self.Contact,self.Title,self.Phone,
    #         self.Email,self.Description,self.Experience,self.Notes,self.modified_at,self.created_at)


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

# replace '-' or ' ' with space, title(), replace to '_' 
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


@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))


"""-----------------------------------------------------------------------------"""
class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=64), validators.DataRequired()])
    email = EmailField('Email', [validators.InputRequired("Please enter your email address."), validators.Email("This field requires a valid email address")])
    username = StringField('Username', [validators.Length(min=4, max=32), validators.DataRequired()])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
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
class LoginForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=32), validators.DataRequired()])
    password = PasswordField('Password', [validators.DataRequired()])


@app.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        username = request.form['username']
        password_candidate = request.form['password']
        result = Users.query.filter_by(username=username).first()
        if result is not None:
            # Username exists
            if sha256_crypt.verify(password_candidate, result.password):
                app.logger.info('LOGIN SUCCESSFUL')
                session['logged_in'] = True
                session['username'] = username
                session['api_request_token'] = result.token
                flash('You are now logged in', 'success')
                return redirect(url_for('dashboard'))
            else:
                app.logger.info('PASSWORD NOT MATCHED')
                error = 'Invalid password'
                return render_template('login.html', error=error, form=form)
        else:
            app.logger.info('NO USER')
            error = 'Username not found'
            return render_template('login.html', error=error, form=form)
    return render_template('login.html',form=form)


"""-----------------------------------------------------------------------------"""
@app.route('/search',methods=['GET','POST'])
@is_logged_in
def search_results():
    _data = request.args.get('search')
    return render_template('search.html',_data=_data)


"""-----------------------------------------------------------------------------"""
@app.route('/reset_city',methods=['POST'])
@is_logged_in
def reset_city():
    try:
        num_rows_deleted = db.session.query(City_dbII).delete()
        db.session.commit()
        flash('Reset cities','success')
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
        flash('Reset jobs','success')
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
        flash('Reset interactions','success')
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
    return render_template('dashboard.html',now=now)


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
class InteractionForm(Form):
    Channel = RadioField('Channel', validators=[validators.DataRequired()],
        choices=[('email', 'Email'), ('call', 'Call'), ('irl', 'In-Person'), ('social', 'Social Media')], default='email')
    Company = StringField('Company', [validators.Length(min=1, max=200), validators.DataRequired()])
    # City = IntegerField('City', [validators.DataRequired()])
    City = StringField('City', [validators.Length(min=1, max=30), validators.DataRequired()])
    Summary = TextAreaField('Summary')
    State = SelectField('State', choices=list(zip(get_state_abbreviations_from_json(), get_state_names_from_json())))


@app.route('/addinteraction',methods=['GET','POST'])
@is_logged_in
def addinteraction():
    form = InteractionForm(request.form)
    if request.method == 'POST' and form.validate():
        _data = form.data
        _data['username'] = session['username']
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
 #proto       # return jsonify({'data':_data})
                # Channel = form.Channel.data
                # Company = form.Company.data
                # City = form.City.data
                # Summary = form.Summary.data
                # State = form.State.data
                # return jsonify({'Channel':Channel,'Company':Company,'City':City,'Summary':Summary,'State':State})
                
                # cur = mysql.connection.cursor()
                # cur.execute("INSERT INTO articles(title, body, author) VALUES(%s, %s, %s)",
                #             (title, body, session['username']))
                # mysql.connection.commit()
                # cur.close()
                # flash('Saved', 'success')
                # return redirect(url_for('dashboard'))
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


"""-----------------------------------------------------------------------------"""
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


def verifyToken(_data):
    _res = Users.query.filter_by(username=_data['username']).first()
    if _res:
        _res = _res.to_dict()
        if _res['token'] != _data['token']:
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


class ApiAuth(Resource):
    def get(self):
        _req = request.args.to_dict()
        try:
            _data = {key:_req[key] for key in ['token','username']}
        except:
            return {'route':'auth','response':'1 or more required keys missing'}
        if verifyToken(_data):
            return {'route':'auth','response':'verified'}
        else:
            return {'route':'auth','response':'false'}

"""-----------------------------------------------------------------------------"""
api.add_resource(ApiSplash, '/api')
api.add_resource(ApiCity, '/api/city')
api.add_resource(ApiJob, '/api/job')
api.add_resource(ApiAuth, '/api/auth')


"""-----------------------------------------------------------------------------"""
if __name__ == '__main__':
    CreateDB()
    app.secret_key = 'correcthorsebatterystaple'
    app.run(host='0.0.0.0',port=5000,debug=True)
    # app.run(host='0.0.0.0')
