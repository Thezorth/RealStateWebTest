import io
from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import current_user, login_required
from . import db
from .models import Property, PropertiesSchema, Location, LocationSchema, Pictures, PicturesSchema
from werkzeug.utils import secure_filename
from PIL import Image
from dotenv import load_dotenv
import boto3
import uuid as uuid
import os
from openpyxl import Workbook, load_workbook

views = Blueprint('views', __name__)
load_dotenv()
ACCEPTED_EXTENTIONS = {'png', 'jpeg', 'jpg'}

@views.route('/')
def home():
    return render_template('index.html', sitetitle = 'Home Page', user=current_user)

@views.route('/property/<int:idd>', methods=['GET', 'POST'])
def view_property(idd):
    prev = request.referrer
    prop = db.session.query(Property).filter_by(id=idd).scalar()
    prop_schema = PropertiesSchema()
    ps = prop_schema.dump(prop)
    prop_pics = db.session.query(Pictures).filter_by(property_id=idd).all()
    pics_schema = PicturesSchema(many = True)
    pics = pics_schema.dump(prop_pics)
    return render_template('property.html', sitetitle = 'property_id:{idd}', user=current_user, property=ps, pictures=pics, prev_url = prev)

@views.route('/mainpage')
def mainpage():
    return render_template('mainpage.html', sitetitle = 'Home', user = current_user)

@views.route('/employee')
@login_required
def employee():
    return render_template('employee.html', sitetitle = 'XXX', user = current_user)

def sort_by_city(list):
    return list['city']
def sort_by_state(list):
    return list['state']

@views.route('/filterLocation', methods=['GET', 'POST'])
def filter_properties():

    if request.method == 'POST':
        jsonData = request.get_json()

        loc = db.session.query(Location).filter_by(city=jsonData).distinct()
        loc_schema = LocationSchema(many=True)
        location = loc_schema.dump(loc)
        
        return sorted(location, key=sort_by_state)

    loc = db.session.query(Location.city).distinct()
    loc_schema = LocationSchema(many=True)
    location = loc_schema.dump(loc)

    return sorted(location, key=sort_by_city)

def allowed_extentions(files):
    return '.' in files and files.rsplit('.', 1)[1].lower() in ACCEPTED_EXTENTIONS

@views.route('/addProperty', methods=['POST'])
def add_property():
    if request.method == 'POST':
        owner = request.form['formOwnerE']
        value = request.form['formValueE']
        sale_type = request.form['formSaleTypeE']
        city = request.form['formCityE']
        state = request.form['formStateE']
        address = request.form['AddressE']
        pictures = request.files.getlist('formFileMultiple')

        for p in pictures:  
            if not allowed_extentions(p.filename):
                return 'ERROR! EXTENTIONS ALLOWED ARE THE FOLLOWING - JPEG / JPG / PNG'
        
        location = Location.query.filter_by(city=city, state=state).first()
        location_schema = LocationSchema()
        location_id = location_schema.dump(location)

        property = Property(saletype=sale_type, value=value, address=address, owner=owner, locations_id=location_id['id'])

        db.session.add(property)
        db.session.commit()
        idd = property.id

        session = boto3.Session(
            aws_access_key_id=os.getenv('AWS_KEY'),
            aws_secret_access_key=os.getenv('AWS_SEC_KEY'),
        )

        s3 = session.resource('s3')
        bucket_name = os.getenv('BUCKET_NAME')

        for index, picture in enumerate(pictures):
            
            filename = uuid.uuid4().hex + '_' + secure_filename(picture.filename)
            
            if index == 0:
                image = Image.open(picture)
                thumb_size = 300, 150
                in_mem_file = io.BytesIO()
                pic_image = image.copy()
                pic_image.thumbnail(thumb_size, Image.Resampling.LANCZOS)  
                pic_image.save(in_mem_file, format="PNG")
                in_mem_file.seek(0)
                s3.Bucket(bucket_name).upload_fileobj(in_mem_file, "thumbnails/"+filename)
                property.thumbnail = "thumbnails/"+filename
                db.session.commit()

            s3.Bucket(bucket_name).upload_fileobj(picture, "images/"+filename)
            file = Pictures(link = "images/"+filename, property_id = idd )
            db.session.add(file)
            db.session.commit()


                
        return redirect(url_for(add_property))


@views.route('/get-properties', methods=['POST'])
def get_properties():  
    jsonData = request.get_json()
    if len(jsonData.keys()) == 1:
        if 'type' in jsonData:
            properties = Property.query.filter(Property.saletype == jsonData['type']).all()
            sProperties = PropertiesSchema(many=True)
            listado = sProperties.dump(properties)
            return listado

    elif len(jsonData.keys()) == 2:
        if 'city' in jsonData:
            properties = db.session.query(Property).join(Property.locations).filter(Property.saletype == jsonData['type'], Location.city == jsonData['city']).all()
            sProperties = PropertiesSchema(many=True)
            listado = sProperties.dump(properties)
            print(listado)
            return listado

    elif len(jsonData.keys()) == 3:
        if 'state' in jsonData:
            properties = db.session.query(Property).join(Property.locations).filter(Property.saletype == jsonData['type'], Location.city == jsonData['city'], Location.state == jsonData['state']).all()
            sProperties = PropertiesSchema(many=True)
            listado = sProperties.dump(properties)
            return listado

