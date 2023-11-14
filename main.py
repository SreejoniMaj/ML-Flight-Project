from flask import Flask, request, render_template
from flask import *
import pickle
import sklearn
import pandas as pd
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import asc, desc
import pymysql
import json
from datetime import datetime

import warnings
warnings.filterwarnings("ignore")


with open('config.json', 'r') as c:
    params =json.load(c)["params"]
    

app = Flask(__name__)


model = pickle.load(open("models\RandomForest.pkl", "rb"))


app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']

#app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql://demoT3:Team3Pwd@demo-team3-server.mysql.database.azure.com/flyhigh'
    


app.secret_key = 'supersecretkey'


    
db = SQLAlchemy(app)


class Contacts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    msg = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    email = db.Column(db.String(20), nullable=False)

class Admin(db.Model):
    ID = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False)
 
 
class User(db.Model):
    ID = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False)
 

@app.route("/")
def home():
    
    return render_template("aboutus.html")



@app.route("/index")
def indexx():
    if 'name' in session:
        msg = 'Login Succesful'
        return render_template('index.html',lmsg=msg , username=session['name'])
    else:
        return redirect('/login')


@app.route("/contact", methods = ['GET', 'POST'])
def contact():
    if(request.method=='POST'):
        '''Add entry to the database'''
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        entry = Contacts(name=name,  msg = message, date= datetime.now(),email = email )
        db.session.add(entry)
        db.session.commit()
        return render_template('contact.html',feedback="Thank you For Your Valuable Feedback")
    
    return render_template('contact.html')



@app.route("/aboutus")
def aboutus():
    
    return render_template('aboutus.html')



@app.route("/posts")
def posts():
    posts = Contacts.query.all()
    return render_template("posts.html", params=params, posts=posts)



@app.route("/prediction")
def prediction():
    return render_template("prediction.html", params=params, posts=posts)



@app.route('/admin')
def admin():
    if 'name' in session:
        msg = 'Login Succesful'
        return render_template('admin.html',msg=msg , usernam=session['name'])
    else:
        return redirect('/login')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'name' in session:
            redirect ('/logout')
    if request.method == 'POST':
        
        email = request.form['email']
        passw = request.form['password']
        user = User.query.filter_by(email=email).first()
        auser = Admin.query.filter_by(email=email).first()
        if user and user.password==passw :
            session['name'] = user.name
            session['id'] = user.ID
            session['email'] = user.email
                        
            return redirect('/index')
        elif auser and auser.password==passw :
            session['name'] = auser.name
            session['id'] = auser.ID
            session['email'] = auser.email
                        
            return redirect('/admin')
        
        else:
            msg = 'Invalid login credentials. Please try again.Or You could Rgister with us'
            return render_template('login.html',msg=msg)
    else:
        return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('email', None)
    session.pop('id', None)
    session.pop('name', None)
    return render_template('login.html')


@app.route("/register", methods = ['GET', 'POST'])
def register():
    if(request.method=='POST'):
        '''Add entry to the database'''
        name = request.form.get('signupUsername')
        email = request.form.get('signupEmail')
        passw=request.form.get('signupPassword')
        #passwc=request.form.get('confirmPassword')
        entry = User(name=name, password =passw,email = email )
        db.session.add(entry)
        db.session.commit()
        return render_template('login.html',msgr="Thank You for Registering {}".format(name))
        
        
    
    return render_template('login.html')


@app.route("/registera", methods = ['GET', 'POST'])
def registera():
    if(request.method=='POST'):
        '''Add entry to the database'''
        name = request.form.get('signupUsername')
        email = request.form.get('signupEmail')
        passw=request.form.get('signupPassword')
        #passwc=request.form.get('confirmPassword')
        entry = Admin(name=name, password =passw,email = email )
        db.session.add(entry)
        db.session.commit()
        return render_template('admin.html',signmsg="Admin {} added successfully".format(name))
        
        
    
    return render_template('admin.html')





@app.route("/predict", methods = ["GET", "POST"])

def predict():
    if request.method == "POST":
        # Date_of_Journey
        date_dep = request.form["deparure"]
        Journey_day = int(pd.to_datetime(date_dep, format="%m/%d/%Y").day)
        Journey_month = int(pd.to_datetime(date_dep, format ="%m/%d/%Y").month)
        # Arrival
       
        
        Total_stops = int(request.form["stops"])
        print(Total_stops)

        # Airline
        # AIR ASIA = 0 (not in column)
        airline=request.form['airline']
        if(airline=='Jet Airways'):
            Jet_Airways = 1
            IndiGo = 0
            Air_India = 0
            Multiple_carriers = 0
            SpiceJet = 0
            Vistara = 0
            GoAir = 0
            Multiple_carriers_Premium_economy = 0
            Jet_Airways_Business = 0
            Vistara_Premium_economy = 0
            Trujet = 0 

        elif (airline=='IndiGo'):
            Jet_Airways = 0
            IndiGo = 1
            Air_India = 0
            Multiple_carriers = 0
            SpiceJet = 0
            Vistara = 0
            GoAir = 0
            Multiple_carriers_Premium_economy = 0
            Jet_Airways_Business = 0
            Vistara_Premium_economy = 0
            Trujet = 0 

        elif (airline=='Air India'):
            Jet_Airways = 0
            IndiGo = 0
            Air_India = 1
            Multiple_carriers = 0
            SpiceJet = 0
            Vistara = 0
            GoAir = 0
            Multiple_carriers_Premium_economy = 0
            Jet_Airways_Business = 0
            Vistara_Premium_economy = 0
            Trujet = 0 
            
        elif (airline=='Multiple carriers'):
            Jet_Airways = 0
            IndiGo = 0
            Air_India = 0
            Multiple_carriers = 1
            SpiceJet = 0
            Vistara = 0
            GoAir = 0
            Multiple_carriers_Premium_economy = 0
            Jet_Airways_Business = 0
            Vistara_Premium_economy = 0
            Trujet = 0 
            
        elif (airline=='SpiceJet'):
            Jet_Airways = 0
            IndiGo = 0
            Air_India = 0
            Multiple_carriers = 0
            SpiceJet = 1
            Vistara = 0
            GoAir = 0
            Multiple_carriers_Premium_economy = 0
            Jet_Airways_Business = 0
            Vistara_Premium_economy = 0
            Trujet = 0 
            
        elif (airline=='Vistara'):
            Jet_Airways = 0
            IndiGo = 0
            Air_India = 0
            Multiple_carriers = 0
            SpiceJet = 0
            Vistara = 1
            GoAir = 0
            Multiple_carriers_Premium_economy = 0
            Jet_Airways_Business = 0
            Vistara_Premium_economy = 0
            Trujet = 0

        elif (airline=='GoAir'):
            Jet_Airways = 0
            IndiGo = 0
            Air_India = 0
            Multiple_carriers = 0
            SpiceJet = 0
            Vistara = 0
            GoAir = 1
            Multiple_carriers_Premium_economy = 0
            Jet_Airways_Business = 0
            Vistara_Premium_economy = 0
            Trujet = 0

        elif (airline=='Multiple carriers Premium economy'):
            Jet_Airways = 0
            IndiGo = 0
            Air_India = 0
            Multiple_carriers = 0
            SpiceJet = 0
            Vistara = 0
            GoAir = 0
            Multiple_carriers_Premium_economy = 1
            Jet_Airways_Business = 0
            Vistara_Premium_economy = 0
            Trujet = 0

        elif (airline=='Jet Airways Business'):
            Jet_Airways = 0
            IndiGo = 0
            Air_India = 0
            Multiple_carriers = 0
            SpiceJet = 0
            Vistara = 0
            GoAir = 0
            Multiple_carriers_Premium_economy = 0
            Jet_Airways_Business = 1
            Vistara_Premium_economy = 0
            Trujet = 0

        elif (airline=='Vistara Premium economy'):
            Jet_Airways = 0
            IndiGo = 0
            Air_India = 0
            Multiple_carriers = 0
            SpiceJet = 0
            Vistara = 0
            GoAir = 0
            Multiple_carriers_Premium_economy = 0
            Jet_Airways_Business = 0
            Vistara_Premium_economy = 1
            Trujet = 0
            
        elif (airline=='Trujet'):
            Jet_Airways = 0
            IndiGo = 0
            Air_India = 0
            Multiple_carriers = 0
            SpiceJet = 0
            Vistara = 0
            GoAir = 0
            Multiple_carriers_Premium_economy = 0
            Jet_Airways_Business = 0
            Vistara_Premium_economy = 0
            Trujet = 1

        else:
            Jet_Airways = 0
            IndiGo = 0
            Air_India = 0
            Multiple_carriers = 0
            SpiceJet = 0
            Vistara = 0
            GoAir = 0
            Multiple_carriers_Premium_economy = 0
            Jet_Airways_Business = 0
            Vistara_Premium_economy = 0
            Trujet = 0

        # Source
        # Banglore = 0 (not in column)
        Source = request.form["from"]
        if (Source == 'Delhi'):
            s_Delhi = 1
            s_Kolkata = 0
            s_Mumbai = 0
            s_Chennai = 0

        elif (Source == 'Kolkata'):
            s_Delhi = 0
            s_Kolkata = 1
            s_Mumbai = 0
            s_Chennai = 0

        elif (Source == 'Mumbai'):
            s_Delhi = 0
            s_Kolkata = 0
            s_Mumbai = 1
            s_Chennai = 0

        elif (Source == 'Chennai'):
            s_Delhi = 0
            s_Kolkata = 0
            s_Mumbai = 0
            s_Chennai = 1

        else:
            s_Delhi = 0
            s_Kolkata = 0
            s_Mumbai = 0
            s_Chennai = 0

        # Destination
        
        # Banglore = 0 (not in column)
        Dest=request.form["to"]
        if Source == Dest:
            return render_template('index.html',Predictive_text="Error..Source and destination same")
        
        if (Dest == 'Cochin'):
            d_Cochin = 1
            d_Delhi = 0
            d_New_Delhi = 0
            d_Hyderabad = 0
            d_Kolkata = 0
        
        elif (Dest == 'Delhi'):
            d_Cochin = 0
            d_Delhi = 1
            d_New_Delhi = 0
            d_Hyderabad = 0
            d_Kolkata = 0

        elif (Dest == 'New_Delhi'):
            d_Cochin = 0
            d_Delhi = 0
            d_New_Delhi = 1
            d_Hyderabad = 0
            d_Kolkata = 0

        elif (Dest == 'Hyderabad'):
            d_Cochin = 0
            d_Delhi = 0
            d_New_Delhi = 0
            d_Hyderabad = 1
            d_Kolkata = 0

        elif (Dest == 'Kolkata'):
            d_Cochin = 0
            d_Delhi = 0
            d_New_Delhi = 0
            d_Hyderabad = 0
            d_Kolkata = 1

        else:
            d_Cochin = 0
            d_Delhi = 0
            d_New_Delhi = 0
            d_Hyderabad = 0
            d_Kolkata = 0

        
        adi=request.form["addi"]
        if adi== 'no-info':
            Additional_Info_1_Short_layover=0
            Additional_Info_2Long_layover=0
            Additional_Info_Business_class=0
            Additional_Info_Change_airports=0
            Additional_Info_Inflight_meal_not_included=0
            Additional_Info_No_checkin_baggage_included=0
            Additional_Info_No_info=1
            Additional_Info_Red_eye_flight=0
        elif adi== 'no-meal':
            Additional_Info_1_Short_layover=0
            Additional_Info_2Long_layover=0
            Additional_Info_Business_class=0
            Additional_Info_Change_airports=0
            Additional_Info_Inflight_meal_not_included=1
            Additional_Info_No_checkin_baggage_included=0
            Additional_Info_No_info=0
            Additional_Info_Red_eye_flight=0
        elif adi== 'no-baggage':
            Additional_Info_1_Short_layover=0
            Additional_Info_2Long_layover=0
            Additional_Info_Business_class=0
            Additional_Info_Change_airports=0
            Additional_Info_Inflight_meal_not_included=0
            Additional_Info_No_checkin_baggage_included=1
            Additional_Info_No_info=0
            Additional_Info_Red_eye_flight=0
        elif adi== '1-long-layover':
            Additional_Info_1_Short_layover=1
            Additional_Info_2Long_layover=0
            Additional_Info_Business_class=0
            Additional_Info_Change_airports=0
            Additional_Info_Inflight_meal_not_included=0
            Additional_Info_No_checkin_baggage_included=0
            Additional_Info_No_info=0
            Additional_Info_Red_eye_flight=0
        elif adi== '2-long-layover':
            Additional_Info_1_Short_layover=0
            Additional_Info_2Long_layover=1
            Additional_Info_Business_class=0
            Additional_Info_Change_airports=0
            Additional_Info_Inflight_meal_not_included=0
            Additional_Info_No_checkin_baggage_included=0
            Additional_Info_No_info=0
            Additional_Info_Red_eye_flight=0
        elif adi== 'change-airport':
            Additional_Info_1_Short_layover=0
            Additional_Info_2Long_layover=0
            Additional_Info_Business_class=0
            Additional_Info_Change_airports=1
            Additional_Info_Inflight_meal_not_included=0
            Additional_Info_No_checkin_baggage_included=0
            Additional_Info_No_info=0
            Additional_Info_Red_eye_flight=0
        elif adi== 'Red-eye flight':
            Additional_Info_1_Short_layover=0
            Additional_Info_2Long_layover=0
            Additional_Info_Business_class=0
            Additional_Info_Change_airports=0
            Additional_Info_Inflight_meal_not_included=0
            Additional_Info_No_checkin_baggage_included=0
            Additional_Info_No_info=0
            Additional_Info_Red_eye_flight=1
        elif adi== 'business-class':
            Additional_Info_1_Short_layover=0
            Additional_Info_2Long_layover=0
            Additional_Info_Business_class=1
            Additional_Info_Change_airports=0
            Additional_Info_Inflight_meal_not_included=0
            Additional_Info_No_checkin_baggage_included=0
            Additional_Info_No_info=0
            Additional_Info_Red_eye_flight=0
        else:
            Additional_Info_1_Short_layover=0
            Additional_Info_2Long_layover=0
            Additional_Info_Business_class=0
            Additional_Info_Change_airports=0
            Additional_Info_Inflight_meal_not_included=0
            Additional_Info_No_checkin_baggage_included=0
            Additional_Info_No_info=0
            Additional_Info_Red_eye_flight=0
        
        
        prediction=model.predict([[Total_stops, 
                                   Journey_day,
                                   Journey_month,
                                   Air_India,
                                   GoAir,
                                   IndiGo,
                                   Jet_Airways,
                                   Jet_Airways_Business,
                                   Multiple_carriers,
                                   Multiple_carriers_Premium_economy,
                                   SpiceJet,
                                   Trujet,
                                   Vistara,
                                   Vistara_Premium_economy,
                                   s_Chennai,
                                   s_Delhi,
                                   s_Kolkata,
                                   s_Mumbai,
                                   d_Cochin,
                                   d_Hyderabad,
                                   d_Kolkata,
                                   d_New_Delhi,
                                   Additional_Info_1_Short_layover,
                                   Additional_Info_2Long_layover,
                                   Additional_Info_Business_class,
                                   Additional_Info_Change_airports,
                                   Additional_Info_Inflight_meal_not_included,
                                   Additional_Info_No_checkin_baggage_included,
                                   Additional_Info_No_info,
                                   Additional_Info_Red_eye_flight
                                   ]])
            

        output=round(prediction[0],2)
        
        return render_template( 'prediction.html',
                               fro= Source,
                               rd="--/--/----",
                               to= Dest,
                               dd=date_dep ,
                               stop=Total_stops,
                               air= airline,
                               addi=adi,
                               way= "One Way",
                               ans="Your Flight price is Rs. {}".format(output),
                               Predictive_text="Your Flight price is Rs. {}".format(output)
                               )


    return render_template("index.html")



@app.route("/predictr", methods = ["GET", "POST"])

def predictr():
    if request.method == "POST":
        # Date_of_Journey
        date_dep = request.form["deparure"]
        Journey_day = int(pd.to_datetime(date_dep, format="%m/%d/%Y").day)
        Journey_month = int(pd.to_datetime(date_dep, format ="%m/%d/%Y").month)
        # Arrival
       
        date_r = request.form["return"]
        Journey_daya = int(pd.to_datetime(date_r, format="%m/%d/%Y").day)
        Journey_montha = int(pd.to_datetime(date_r, format ="%m/%d/%Y").month)
         # Total Stops
        Total_stops = int(request.form["stops"])
        print(Total_stops)

        # Airline
        # AIR ASIA = 0 (not in column)
        airline=request.form['airline']
        if(airline=='Jet Airways'):
            Jet_Airways = 1
            IndiGo = 0
            Air_India = 0
            Multiple_carriers = 0
            SpiceJet = 0
            Vistara = 0
            GoAir = 0
            Multiple_carriers_Premium_economy = 0
            Jet_Airways_Business = 0
            Vistara_Premium_economy = 0
            Trujet = 0 

        elif (airline=='IndiGo'):
            Jet_Airways = 0
            IndiGo = 1
            Air_India = 0
            Multiple_carriers = 0
            SpiceJet = 0
            Vistara = 0
            GoAir = 0
            Multiple_carriers_Premium_economy = 0
            Jet_Airways_Business = 0
            Vistara_Premium_economy = 0
            Trujet = 0 

        elif (airline=='Air India'):
            Jet_Airways = 0
            IndiGo = 0
            Air_India = 1
            Multiple_carriers = 0
            SpiceJet = 0
            Vistara = 0
            GoAir = 0
            Multiple_carriers_Premium_economy = 0
            Jet_Airways_Business = 0
            Vistara_Premium_economy = 0
            Trujet = 0 
            
        elif (airline=='Multiple carriers'):
            Jet_Airways = 0
            IndiGo = 0
            Air_India = 0
            Multiple_carriers = 1
            SpiceJet = 0
            Vistara = 0
            GoAir = 0
            Multiple_carriers_Premium_economy = 0
            Jet_Airways_Business = 0
            Vistara_Premium_economy = 0
            Trujet = 0 
            
        elif (airline=='SpiceJet'):
            Jet_Airways = 0
            IndiGo = 0
            Air_India = 0
            Multiple_carriers = 0
            SpiceJet = 1
            Vistara = 0
            GoAir = 0
            Multiple_carriers_Premium_economy = 0
            Jet_Airways_Business = 0
            Vistara_Premium_economy = 0
            Trujet = 0 
            
        elif (airline=='Vistara'):
            Jet_Airways = 0
            IndiGo = 0
            Air_India = 0
            Multiple_carriers = 0
            SpiceJet = 0
            Vistara = 1
            GoAir = 0
            Multiple_carriers_Premium_economy = 0
            Jet_Airways_Business = 0
            Vistara_Premium_economy = 0
            Trujet = 0

        elif (airline=='GoAir'):
            Jet_Airways = 0
            IndiGo = 0
            Air_India = 0
            Multiple_carriers = 0
            SpiceJet = 0
            Vistara = 0
            GoAir = 1
            Multiple_carriers_Premium_economy = 0
            Jet_Airways_Business = 0
            Vistara_Premium_economy = 0
            Trujet = 0

        elif (airline=='Multiple carriers Premium economy'):
            Jet_Airways = 0
            IndiGo = 0
            Air_India = 0
            Multiple_carriers = 0
            SpiceJet = 0
            Vistara = 0
            GoAir = 0
            Multiple_carriers_Premium_economy = 1
            Jet_Airways_Business = 0
            Vistara_Premium_economy = 0
            Trujet = 0

        elif (airline=='Jet Airways Business'):
            Jet_Airways = 0
            IndiGo = 0
            Air_India = 0
            Multiple_carriers = 0
            SpiceJet = 0
            Vistara = 0
            GoAir = 0
            Multiple_carriers_Premium_economy = 0
            Jet_Airways_Business = 1
            Vistara_Premium_economy = 0
            Trujet = 0

        elif (airline=='Vistara Premium economy'):
            Jet_Airways = 0
            IndiGo = 0
            Air_India = 0
            Multiple_carriers = 0
            SpiceJet = 0
            Vistara = 0
            GoAir = 0
            Multiple_carriers_Premium_economy = 0
            Jet_Airways_Business = 0
            Vistara_Premium_economy = 1
            Trujet = 0
            
        elif (airline=='Trujet'):
            Jet_Airways = 0
            IndiGo = 0
            Air_India = 0
            Multiple_carriers = 0
            SpiceJet = 0
            Vistara = 0
            GoAir = 0
            Multiple_carriers_Premium_economy = 0
            Jet_Airways_Business = 0
            Vistara_Premium_economy = 0
            Trujet = 1

        else:
            Jet_Airways = 0
            IndiGo = 0
            Air_India = 0
            Multiple_carriers = 0
            SpiceJet = 0
            Vistara = 0
            GoAir = 0
            Multiple_carriers_Premium_economy = 0
            Jet_Airways_Business = 0
            Vistara_Premium_economy = 0
            Trujet = 0

        # Source
        # Banglore = 0 (not in column)
        Source = request.form["fromr"]
        if (Source == 'Delhi'):
            s_Delhi = 1
            s_Kolkata = 0
            s_Mumbai = 0
            s_Chennai = 0

        elif (Source == 'Kolkata'):
            s_Delhi = 0
            s_Kolkata = 1
            s_Mumbai = 0
            s_Chennai = 0

        elif (Source == 'Mumbai'):
            s_Delhi = 0
            s_Kolkata = 0
            s_Mumbai = 1
            s_Chennai = 0

        elif (Source == 'Chennai'):
            s_Delhi = 0
            s_Kolkata = 0
            s_Mumbai = 0
            s_Chennai = 1

        else:
            s_Delhi = 0
            s_Kolkata = 0
            s_Mumbai = 0
            s_Chennai = 0

        # Destination
        
        # Banglore = 0 (not in column)
        Dest=request.form["tor"]
        if Source == Dest:
            return render_template('index.html',Predictive_text="Error..Source and destination same")
        
        if (Dest == 'Cochin'):
            d_Cochin = 1
            d_Delhi = 0
            d_New_Delhi = 0
            d_Hyderabad = 0
            d_Kolkata = 0
        
        elif (Dest == 'Delhi'):
            d_Cochin = 0
            d_Delhi = 1
            d_New_Delhi = 0
            d_Hyderabad = 0
            d_Kolkata = 0

        elif (Dest == 'New_Delhi'):
            d_Cochin = 0
            d_Delhi = 0
            d_New_Delhi = 1
            d_Hyderabad = 0
            d_Kolkata = 0

        elif (Dest == 'Hyderabad'):
            d_Cochin = 0
            d_Delhi = 0
            d_New_Delhi = 0
            d_Hyderabad = 1
            d_Kolkata = 0

        elif (Dest == 'Kolkata'):
            d_Cochin = 0
            d_Delhi = 0
            d_New_Delhi = 0
            d_Hyderabad = 0
            d_Kolkata = 1

        else:
            d_Cochin = 0
            d_Delhi = 0
            d_New_Delhi = 0
            d_Hyderabad = 0
            d_Kolkata = 0

        adi=request.form["addi"]
        if adi== 'no-info':
            Additional_Info_1_Short_layover=0
            Additional_Info_2Long_layover=0
            Additional_Info_Business_class=0
            Additional_Info_Change_airports=0
            Additional_Info_Inflight_meal_not_included=0
            Additional_Info_No_checkin_baggage_included=0
            Additional_Info_No_info=1
            Additional_Info_Red_eye_flight=0
        elif adi== 'no-meal':
            Additional_Info_1_Short_layover=0
            Additional_Info_2Long_layover=0
            Additional_Info_Business_class=0
            Additional_Info_Change_airports=0
            Additional_Info_Inflight_meal_not_included=1
            Additional_Info_No_checkin_baggage_included=0
            Additional_Info_No_info=0
            Additional_Info_Red_eye_flight=0
        elif adi== 'no-baggage':
            Additional_Info_1_Short_layover=0
            Additional_Info_2Long_layover=0
            Additional_Info_Business_class=0
            Additional_Info_Change_airports=0
            Additional_Info_Inflight_meal_not_included=0
            Additional_Info_No_checkin_baggage_included=1
            Additional_Info_No_info=0
            Additional_Info_Red_eye_flight=0
        elif adi== '1-long-layover':
            Additional_Info_1_Short_layover=1
            Additional_Info_2Long_layover=0
            Additional_Info_Business_class=0
            Additional_Info_Change_airports=0
            Additional_Info_Inflight_meal_not_included=0
            Additional_Info_No_checkin_baggage_included=0
            Additional_Info_No_info=0
            Additional_Info_Red_eye_flight=0
        elif adi== '2-long-layover':
            Additional_Info_1_Short_layover=0
            Additional_Info_2Long_layover=1
            Additional_Info_Business_class=0
            Additional_Info_Change_airports=0
            Additional_Info_Inflight_meal_not_included=0
            Additional_Info_No_checkin_baggage_included=0
            Additional_Info_No_info=0
            Additional_Info_Red_eye_flight=0
        elif adi== 'change-airport':
            Additional_Info_1_Short_layover=0
            Additional_Info_2Long_layover=0
            Additional_Info_Business_class=0
            Additional_Info_Change_airports=1
            Additional_Info_Inflight_meal_not_included=0
            Additional_Info_No_checkin_baggage_included=0
            Additional_Info_No_info=0
            Additional_Info_Red_eye_flight=0
        elif adi== 'Red-eye flight':
            Additional_Info_1_Short_layover=0
            Additional_Info_2Long_layover=0
            Additional_Info_Business_class=0
            Additional_Info_Change_airports=0
            Additional_Info_Inflight_meal_not_included=0
            Additional_Info_No_checkin_baggage_included=0
            Additional_Info_No_info=0
            Additional_Info_Red_eye_flight=1
        elif adi== 'business-class':
            Additional_Info_1_Short_layover=0
            Additional_Info_2Long_layover=0
            Additional_Info_Business_class=1
            Additional_Info_Change_airports=0
            Additional_Info_Inflight_meal_not_included=0
            Additional_Info_No_checkin_baggage_included=0
            Additional_Info_No_info=0
            Additional_Info_Red_eye_flight=0
        else:
            Additional_Info_1_Short_layover=0
            Additional_Info_2Long_layover=0
            Additional_Info_Business_class=0
            Additional_Info_Change_airports=0
            Additional_Info_Inflight_meal_not_included=0
            Additional_Info_No_checkin_baggage_included=0
            Additional_Info_No_info=0
            Additional_Info_Red_eye_flight=0
         
        
        prediction=model.predict([[Total_stops, 
                                   Journey_day,
                                   Journey_month,
                                   Air_India,
                                   GoAir,
                                   IndiGo,
                                   Jet_Airways,
                                   Jet_Airways_Business,
                                   Multiple_carriers,
                                   Multiple_carriers_Premium_economy,
                                   SpiceJet,
                                   Trujet,
                                   Vistara,
                                   Vistara_Premium_economy,
                                   s_Chennai,
                                   s_Delhi,
                                   s_Kolkata,
                                   s_Mumbai,
                                   d_Cochin,
                                   d_Hyderabad,
                                   d_Kolkata,
                                   d_New_Delhi,
                                   Additional_Info_1_Short_layover,
                                   Additional_Info_2Long_layover,
                                   Additional_Info_Business_class,
                                   Additional_Info_Change_airports,
                                   Additional_Info_Inflight_meal_not_included,
                                   Additional_Info_No_checkin_baggage_included,
                                   Additional_Info_No_info,
                                   Additional_Info_Red_eye_flight
                                   ]])
            

        output=round(prediction[0],2)
        
        predictionr=model.predict([[Total_stops,Journey_daya,Journey_montha,Air_India,
                                   GoAir,IndiGo, Jet_Airways, Jet_Airways_Business,
                                   Multiple_carriers, Multiple_carriers_Premium_economy,
                                   SpiceJet,  Trujet, Vistara, Vistara_Premium_economy,
                                   s_Chennai,s_Delhi,s_Kolkata,s_Mumbai,d_Cochin,
                                   d_Hyderabad,d_Kolkata,d_New_Delhi,
                                   Additional_Info_1_Short_layover,Additional_Info_2Long_layover,
                                   Additional_Info_Business_class,
                                   Additional_Info_Change_airports,
                                   Additional_Info_Inflight_meal_not_included,
                                   Additional_Info_No_checkin_baggage_included,
                                   Additional_Info_No_info,
                                   Additional_Info_Red_eye_flight
                                   ]])
        outputr=round(predictionr[0],2)
        t=output+outputr
        return render_template('prediction.html',
                               fro= Source,
                               to= Dest,
                               dd=date_dep ,
                               rd=date_r,
                               stop=Total_stops,
                               air= airline,
                               addi=adi,
                               way= "Round Trip",
                               ans="Your Flight price is Rs. {}".format(t),
                               Predictive_text="Your Flight price is Rs. {}".format(t)
                               )

    return render_template("index.html")


@app.route("/ans")
def ans():
    
    return render_template("ans.html")







if __name__ == "__main__":
    app.run(debug=True)
