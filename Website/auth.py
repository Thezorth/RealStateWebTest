import json
import os
import requests
from dotenv import load_dotenv
from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
from oauthlib.oauth2 import WebApplicationClient

auth = Blueprint('auth', __name__)

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

load_dotenv()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_DISCOVERY_URL = ("https://accounts.google.com/.well-known/openid-configuration")

client = WebApplicationClient(GOOGLE_CLIENT_ID)

def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        exist = db.session.query(User.id).filter_by(
            username=username).scalar() is not None

        if exist == True:

            user = User.query.filter_by(username=username).scalar()
        
            if check_password_hash(user.password, password):
                login_user(user,remember=True)
                return redirect('mainpage')
            else:
                flash('Incorrect password', category='error')
        else:
            flash('Username does not exist.', category='error')

            
    return render_template('login.html', user=current_user)

@auth.route('/google-login')
def google_login():
    google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)

@auth.route("/google-login/callback")
def callback():
    code = request.args.get("code")
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )

    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    client.parse_request_body_response(json.dumps(token_response.json()))
    
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]

    uri, headers, body = client.add_token(userinfo_endpoint)

    userinfo_response = requests.get(uri, headers=headers, data=body)

    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["given_name"]
    else:
        return "User email not available or not verified by Google.", 400

    if not db.session.query(User.id).filter_by(
            unique_id=unique_id).scalar() is not None:
        new_user = User(unique_id=unique_id, email=users_email, username=users_name)
        db.session.add(new_user)
        db.session.commit()

    log = User.query.filter_by(unique_id=unique_id).scalar()

    login_user(log, remember=True)

    return redirect(url_for("views.mainpage"))

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/sign-up', methods=['GET', 'POST'])
def sing_up():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        check_mail = db.session.query(User.id).filter_by(
            email=email).scalar() is not None
        check_username = db.session.query(User.id).filter_by(
            username=username).scalar() is not None

        if len(email) < 4:
            flash('Email must be a valid email.', category='error')
        elif len(username) < 3:
            flash('Username must contain more than 3 characters.',
                  category='error')
        elif len(password1) < 7:
            flash('Password must contain at least 7 characters.',
                  category='error')
        elif password1 != password2:
            flash('Password does not match.', category='error')
        else:
            if check_mail:
                flash('Email already in use', category='error')
            elif check_username:
                flash('Username already in use', category='error')
            else:
                new_user = User(email=email, username=username, password=generate_password_hash(
                    password1, method='sha256'))
                db.session.add(new_user)
                db.session.commit()
                flash('Your account has been created.', category='success')

                log = User.query.filter_by(id=new_user.id).scalar()
                login_user(log, remember=True)
                return redirect(url_for('views.mainpage'))
    return render_template('sign_up.html', user=current_user)
