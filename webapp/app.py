# Traba
import os
import re
import json
import datetime
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
from flask_sqlalchemy import SQLAlchemy
# from flask_wtf import FlaskForm
# from wtforms import StringField, SubmitField, TextAreaField
from data.data_import import get_states_from_json

"""-----------------------------------------------------------------------------"""
project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(os.path.join(project_dir, "trabaDB.db"))

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = database_file
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


"""-----------------------------------------------------------------------------"""
# posted_at = db.Column(db.DateTime)
class City_db(db.Model):
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
    
    def __repr__(self):
        return "<ID: {}><City: {}><State: {}><Salary: {}><Median Rent: {}><Median Home: {}>\
            <Cost of Living Index: {}><State Tax: {}><Local Tax: {}><Property Tax: {}>\
            <Living Cost: {}><Food Cost: {}><Transit Index: {}><Companies: {}>\
            <Neighborhoods: {}><Notes: {}>"\
            .format(self.id,self.City,self.State,self.Salary,self.Rent,self.Home,self.Coli,
            self.StateTax,self.LocalTax,self.PropertyTax,self.Living,self.Food,
            self.Transit,self.Companies,self.Neighborhoods,self.Notes)


class Job_db(db.Model):
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

    def __repr__(self):
        return "<ID: {}><City: {}><State: {}><Position: {}><Level: {}><Company: {}>\
            <Type: {}><Salary: {}><Link: {}><Contact: {}><Title: {}><Phone: {}>\
            <Email: {}><Description: {}><Experience: {}><Notes: {}>"\
            .format(self.id,self.City,self.State,self.Position,self.Level,self.Company,self.Type,
            self.Salary,self.Link,self.Contact,self.Title,self.Phone,
            self.Email,self.Description,self.Experience,self.Notes)

"""-----------------------------------------------------------------------------"""
# de_comma = lambda x: x.replace(',', '')
def handleAddCity(request_dict):
    if ''.join(request_dict.values()).strip() == '':
        return None
    else:
        safeStrings = ['State']
        titleStrings = ['City']
        floatStrings = ['Rent','Home','Coli','Salary','StateTax','LocalTax','PropertyTax','Living','Food','Transit']
        textStrings = ['Companies','Neighborhoods','Notes']
        try:
            for each in safeStrings:
                if request_dict[each] == '':
                    request_dict[each] = None
                else:
                    pass
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
            for each in textStrings:
                if request_dict[each] == '':
                    request_dict[each] = None
                else:
                    pass
            return request_dict
        except:
            return None


def handleAddJob(request_dict):
    if ''.join(request_dict.values()).strip() == '':
        return None
    else:
        safeStrings = ['State','Link','Email']
        titleStrings = ['City','Position','Level','Company','Type','Contact','Title']
        floatStrings = ['Salary']
        intStrings = ['Phone']
        textStrings = ['Description','Experience','Notes']
        try:
            for each in safeStrings:
                if request_dict[each] == '':
                    request_dict[each] = None
                else:
                    pass
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
    States = get_states_from_json()
    return render_template('addcity.html',States=States)
    # if city already exists, pop error msg and redirect user to edit existing page

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
    States = get_states_from_json()
    return render_template('addjob.html',States=States)


"""-----------------------------------------------------------------------------"""
@app.route('/cities')
def cities():
    Cities = City_db.query.all()
    return render_template('cities.html',Cities=Cities)

"""-----------------------------------------------------------------------------"""
@app.route('/jobs')
def jobs():
    Jobs = Job_db.query.all()
    return render_template('jobs.html',Jobs=Jobs)


"""-----------------------------------------------------------------------------"""
@app.route('/interactions')
def interactions():
    return render_template('interactions.html')


"""-----------------------------------------------------------------------------"""
@app.route('/calendar')
def calendar():
    return render_template('calendar.html')


"""-----------------------------------------------------------------------------"""
if __name__ == '__main__':
    app.secret_key = 'correcthorsebatterystaple'
    app.run(host='0.0.0.0',debug=True)






    # state = request_data['State']                         Safe, empty str->None
    # city = request_data['City']                           Sanitize, Title
    # coli = request_data['Coli']                           Decimal
    # salary = request_data['Salary']                       Decimal _,2
    # rent = request_data['Rent']                           Int
    # home = request_data['Home']                           Int
    # stateTax = request_data['StateTax']                   Decimal
    # localTax = request_data['LocalTax']                   Decimal
    # propertyTax = request_data['PropertyTax']             Decimal
    # living = request_data['Living']                       Decimal _,2
    # food = request_data['Food']                           Decimal _,2
    # transit = request_data['Transit']                     Decimal _,2
    # companies = request_data['Companies']                 Sanitize, long text str
    # neighborhoods = request_data['Neighborhoods']         Sanitize, long text str
    # notes = request_data['Notes']                         Sanitize, long text str