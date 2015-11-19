import os
from flask import Flask, render_template, flash, request, session, url_for, redirect, g, escape, abort, jsonify
from flask.ext.login import LoginManager, login_user, logout_user, current_user, login_required, UserMixin
from flask.ext.googlemaps import GoogleMaps
from flask.ext.sqlalchemy import SQLAlchemy

from wtforms import BooleanField, TextField, PasswordField, validators
from wtforms.fields.core import StringField, BooleanField
from wtforms.fields.simple import PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo

from passlib.hash import sha256_crypt
from functools import wraps

import gc

from flask.ext.wtf import Form

from datetime import datetime

#from app import db, login_manager

# lager og initialiserer appen
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:\\Users\\Eirik\\myproject\\Prosjekt 2\\alpinklubben.db'
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = 'Qh\x84J\xbb^\xeb\x8d\x96\x07\xa1\xf2Q\x905(\xbca\x06\x13\x1a\xb5\xf6\xad'
app.config['DEBUG'] = True

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

GoogleMaps(app)

#pakke = "ski package" - alder = "age" leietid = "rental time, hourly, daily or weekly" leieantall = "How many hours, days or weeks they want to rent for (min 1 max 6)"
class Utleie(db.Model):
    __tablename__="utleie"
    id = db.Column(db.Integer, primary_key=True)
    pakke = db.Column(db.String(64), nullable=False)
    alder = db.Column(db.Integer, nullable=False)
    leietid = db.Column(db.String(64), nullable=False)
    leieantall = db.Column(db.Integer, nullable=False)
    

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), nullable=False, unique=True, index=True)
    username = db.Column(db.String(64), nullable=False, unique=True, index=True)
    password = db.Column(db.String(128))
#   password_hash does not work, look after.
#    utleie = db.relationship("Utleie") <-- need to connect the tables together so I know what user rented what

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/', methods=['GET', 'POST'])
def homepage():
    return render_template("forside.html")

@app.route('/index')
def index():
    return render_template("index.html")

@app.route('/kontaktoss')
def kontaktoss():
    return render_template("kontaktoss.html")

@property
def password(self):
    raise ArithmeticError("not a readable attribute")

@password.setter
def password(self, password):
    self.password_hash = generate_password_hash(password)

def verify(self, password):
    return check_password_hash(self.password_hash, password)

class RegistrationForm(Form):
    username = TextField('Username', [validators.Length(min=4, max=20)])
    email = TextField('Email Address', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [validators.Required(),
    validators.EqualTo('confirm', message="Passordene er ikke like.")])
    confirm = PasswordField('Gjenta Passord')

#is using email? Not correct, change to user
class LoginForm(Form):
    username = TextField('username', [validators.Length(min=4, max=20)])
    password = PasswordField("Password", validators=[DataRequired("Cannot be empty")])
    remember_me = BooleanField("Keep me logged in")
    submit = SubmitField("Login")

#Login page (something not working)
@app.route('/login', methods=["GET", "POST"])
def login():    
    form = LoginForm()        
    if form.validate_on_submit():
        print("validated")
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.verify(form.password.data):
            flash("Invalid username or password", category="warning")
            return redirect(url_for("auth.login"))
        login_user(user, form.remember_me.data)
        flash("Du er logget inn!")
        return redirect(url_for("index"))
    return render_template("login.html", forms=form)


#Registration page, something not working.  NoForeignKeysError: 
@app.route('/registrer', methods=["GET", "POST"])
def register():
    form = RegistrationForm(request.form)
    if request.method == "POST":
        if form.validate_on_submit():
            print(form.data)
            user = User(email=form.data['email'], username=form.data['username'], password=form.data['password'])
            db.session.add(user)
            db.session.commit()
            login_user(user, True)
            flash('Du er logget inn som:'+str(form.data['username']))
            return redirect(url_for("index"))
    return render_template("registrer.html", form=form) 


#Log out function - getting error here. (fixed needed login_manager.init_app(app)
@app.route('/loggut')
#@login_required - removed due to cookies making the webpage autologin without users in DB.
def logout():
    logout_user()
    flash("Du er logget ut")
    return redirect(url_for("index"))

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")

@app.errorhandler(405)
def method_not_found(e):
    return render_template("405.html")

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logget_inn' in session:
            return f(*args, **kwargs)
        else:
            flash('Du maa logge inn for aa se denne siden')
            return redirect(url_for('login_page'))
    return wrap

#utleie (rental page) - Where the user rent ski-packages (total of 5) - send him to oppsummering to show what user bought after.
@app.route('/utleie', methods = ['GET','POST'])
@login_required
def utleie():
    error = ''
    try:        
        if request.method == "POST":
            pakke = request.form.get('optionsRadios', '')
            alder = 'tileggbox' in request.form
            leietid = request.form['leietid']
            leieantall = request.form['leieantall']
            if not pakke:
                flash('Vennligst velg en pakke')
                return render_template("utleie.html", error = error)
            else:
                utleie = Utleie(user_id=current_user.id, pakke=pakke,alder=alder,leietid=leietid)
                db.session.add(utleie)
                db.session.commit()
#               flash('Takk for ditt kjop')
                gc.collect()
                return redirect(url_for('oppsummering'))

        else:
            return render_template("utleie.html", error = error)
    except Exception as e:
        return (str(e))

#What the user "rented" on "utleie.html" - display here.
@app.route('/oppsummering')
@login_required
def oppsummering():
    pass    
    #return render_template('oppsummering.html', utleies=utleies)


#@app.route('/heiskort')
#@login_required
#def heiskort():
#    return render_template('heiskort.html')


if __name__ == "__main__":
    app.run()