# Traba
import os
import re
import json
import datetime
import urllib.parse
from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    redirect,
    url_for,
    flash,
    session
)
from flask_api import (
    FlaskAPI,
    status,
    exceptions
)
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin
# from flask_wtf import FlaskForm
# from wtforms import StringField, SubmitField, TextAreaField
from data.data_import import get_state_names_from_json, get_state_abbreviations_from_json

"""-----------------------------------------------------------------------------"""
project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(os.path.join(project_dir, "trabaDB.db"))

app = Flask(__name__)
api = Api(app)
app.config["SQLALCHEMY_DATABASE_URI"] = database_file
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

"""-----------------------------------------------------------------------------"""
# posted_at = db.Column(db.DateTime)
class City_db(db.Model, SerializerMixin):
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
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
    modified_at = db.Column(db.DateTime(), unique=False, nullable=True)
    created_at = db.Column(db.DateTime(), nullable=False, default=datetime.datetime.utcnow())

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
def handleAddCity(request_dict):
    if ''.join(request_dict.values()).strip() == '':
        return None
    else:
        # check if city and state are present - REQUIRED
        # if city and state present, check to see which fields are missing
        # any fields that are missing, add to dict as default values
        titleStrings = ['City','State']
        for string in titleStrings:
            if string not in list(request_dict.keys()):
                return 'required string not in request'
        floatStrings = ['Rent','Home','Coli','Salary','StateTax','LocalTax','PropertyTax','Living','Food','Transit']
        textStrings = ['Companies','Neighborhoods','Notes']
        try:
            for each in titleStrings:
                request_dict[each] = request_dict[each].title()
            for each in floatStrings:
                if each in list(request_dict.keys()):
                    request_dict[each] = None if request_dict[each] == '' else float(request_dict[each])
            for each in textStrings:
                if each in list(request_dict.keys()):
                    if request_dict[each] == '': request_dict[each] = None
            return request_dict
        except:
            return None

"""-----------------------------------------------------------------------------"""
def handleAddJob(request_dict):
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
@app.route('/')
def index():
    return render_template('index.html')

"""-----------------------------------------------------------------------------"""
@app.route("/home", methods=["GET", "POST"])
def home():
    return render_template("home.html")

"""-----------------------------------------------------------------------------"""
@app.route('/settings')
def settings():
    return render_template('settings.html')

"""-----------------------------------------------------------------------------"""
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

"""-----------------------------------------------------------------------------"""
@app.route('/addcity', methods=["GET","POST"])
def addcity():
    if request.method == "POST":
        request_dict = {}
        for field in request.form:
            request_dict[field] = request.form[field]
        Data = handleAddCity(request_dict)
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
def addjob():
    if request.method == "POST":
        request_dict = {}
        for field in request.form:
            request_dict[field] = request.form[field]
        Data = handleAddJob(request_dict)
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
def cities():
    results = City_db.query.all()
    CityList = []
    Flag = True
    if results:
        for result in results:
            CityList.append(result.to_dict())
        Flag = False
    return render_template('cities.html',Cities=CityList,Flag=Flag)

"""-----------------------------------------------------------------------------"""
@app.route('/jobs')
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
def interactions():
    Flag = True
    return render_template('interactions.html',Flag=Flag)

"""-----------------------------------------------------------------------------"""
@app.route('/addinteraction')
def addinteraction():
    return render_template('addinteraction.html')

"""-----------------------------------------------------------------------------"""
@app.route('/calendar')
def calendar():
    return render_template('calendar.html')

"""-----------------------------------------------------------------------------"""
@app.errorhandler(404)
def not_found(e):
    Back = request.referrer or url_for('index')
    return render_template('404.html',Back=Back)

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
        valid_list = list(City_db.query.first().to_dict().keys())
        hidden_keys = ['id','created_at','modified_at']
        for thing in hidden_keys:
            if thing in valid_list: valid_list.remove(thing)
        # valid_list is now good to compare against
        # ** check to make sure City and State are present, otherwise Error. for now assume safe case
        user_keys = list(request.args.keys())
        user_filtered = {}
        for keey in user_keys:
            if keey in valid_list:
                # get the users data and add to dict
                user_filtered[keey] = request.args[keey]
        Data = handleAddCity(user_filtered)
        # check if city already exists in database, respond with error message, for now add new row
        # q = City_db.query().first().filter(City_db.City == Data['City'])
        db_response = False
        try:
            cls = City_db(**Data)
            db.session.add(cls)
            db.session.commit()
            db_response = True
        except:
            pass
        return jsonify({'valid keys':valid_list,
                        'user keys':user_keys,
                        'filtered request':Data,
                        'db response':db_response})

class ApiJob(Resource):
    def get(self):
        data = request.args
        keys = list(request.args.keys())
        values = list(request.args.values())
        return jsonify({'Data':data,'Keys':keys,'Values':values})


"""-----------------------------------------------------------------------------"""
api.add_resource(ApiSplash, '/api')
api.add_resource(ApiCity, '/api/city')
api.add_resource(ApiJob, '/api/job')

"""-----------------------------------------------------------------------------"""
if __name__ == '__main__':
    app.secret_key = 'correcthorsebatterystaple'
    app.run(host='0.0.0.0',port=5000,debug=True)
