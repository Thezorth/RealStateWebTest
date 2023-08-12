import io
import json
import re
from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from flask_login import current_user, login_required
import requests
from . import db
from .models import Property, PropertiesSchema, Location, LocationSchema, Pictures, PicturesSchema
from werkzeug.utils import secure_filename
from PIL import Image
from dotenv import load_dotenv
import boto3
import uuid as uuid
import os

views = Blueprint('views', __name__)
load_dotenv()
ACCEPTED_EXTENTIONS = {'png', 'jpeg', 'jpg'}

def allowed_extentions(files):
    return '.' in files and files.rsplit('.', 1)[1].lower() in ACCEPTED_EXTENTIONS

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

@views.route('/my_properties')
@login_required
def my_properties():
    
    a = db.session.query(Property).filter_by(uploaded_by = current_user.id).all()
    b = PropertiesSchema(many = True)
    c = b.dump(a)

    return render_template('my_properties.html', sitetitle = 'XXX', user = current_user, c = c)

@views.route('/mainpage')
def mainpage():
    return render_template('mainpage.html', sitetitle = 'Home', user = current_user)

@views.route('/profile')
@login_required
def employee():
    return render_template('profile.html', sitetitle = 'XXX', user = current_user)

@views.route('/my_properties/<user>/<int:idd>') 
@login_required
def edit_property(user, idd):

    if user == current_user.username:

        prop = db.session.query(Property).filter_by(id=idd).scalar()
        prop_schema = PropertiesSchema()
        ps = prop_schema.dump(prop)
        prop_pics = db.session.query(Pictures).filter_by(property_id=idd).all()
        pics_schema = PicturesSchema(many = True)
        pics = pics_schema.dump(prop_pics)

        return render_template('edit_property.html', sitetitle = 'XXX', user=current_user, property=ps, pictures=pics)
    else:
        return 'error: access denied'

@views.route('/deleteproperty', methods=['POST'])
def deleteproperty():
    if request.method == 'POST':
        txt = request.form.get('card')
        cardid = re.split('card', txt)[1]

        prop = db.session.query(Property).filter_by(id=cardid).scalar()
        prop_img = db.session.query(Pictures).filter_by(property_id = cardid).all()

        session = boto3.Session(
            aws_access_key_id=os.getenv('AWS_KEY'),
            aws_secret_access_key=os.getenv('AWS_SEC_KEY'),
        )

        s3 = session.resource('s3')

        bucket_name = os.getenv('BUCKET_NAME')
        bucket_link = os.getenv('BUCKET_LINK')

        for img in prop_img:
            link = re.split(bucket_link, img.link)[1]
            obj = s3.Object(bucket_name, link)
            obj.delete()
        
        prop_thumb = re.split(bucket_link, prop.thumbnail)[1]
        obj = s3.Object(bucket_name, prop_thumb)
        obj.delete()

        db.session.query(Pictures).filter_by(property_id = cardid).delete()
        db.session.query(Property).filter_by(id=cardid).delete()

        db.session.commit()
        
    return jsonify(200) 


@views.route('/editproperty', methods=['POST'])
def changeproperty():
    if request.method == 'POST':
        txt = request.form
        pictures = request.files
        delete_images = json.loads(request.form.get('delete'))
        text = json.loads(txt['usertext'])

        for p in pictures:  
            if not allowed_extentions(p.filename):
                return 'ERROR! EXTENTIONS ALLOWED ARE THE FOLLOWING - JPEG / JPG / PNG'
        
        prop = db.session.query(Property).filter_by(id = text['id']).scalar()
        first_pic = db.session.query(Pictures).filter_by(property_id = text['id']).first()
        if first_pic is not None:
            first_pic = first_pic.link
        prop.saletype = text['saletype']
        prop.value = text['value']
        prop.address = text['address']

        db.session.commit()

        session = boto3.Session(
            aws_access_key_id=os.getenv('AWS_KEY'),
            aws_secret_access_key=os.getenv('AWS_SEC_KEY'),
        )

        s3 = session.resource('s3')
        bucket_name = os.getenv('BUCKET_NAME')
        bucket_link = os.getenv('BUCKET_LINK')

        
        
        for img in delete_images: 
           
            new_delete = db.session.query(Pictures).filter_by(id = img).first()
            if new_delete is not None:
                new_delete = new_delete.link
            txt_split = re.split(bucket_link, new_delete)[1]
            obj = s3.Object(bucket_name, txt_split)
            obj.delete()
            db.session.query(Pictures).filter_by(id=img).delete()
            db.session.commit()


        for picture in pictures:

            first_delete = db.session.query(Pictures).filter_by(id = picture).first()
            if first_delete is not None:
                txt_split = re.split(bucket_link, first_delete.link)[1]
                obj = s3.Object(bucket_name, txt_split)
                obj.delete()
                
                pic = request.files.get(picture)
                filename = uuid.uuid4().hex + '_' + secure_filename(pic.filename)
                s3.Bucket(bucket_name).upload_fileobj(pic, "images/"+filename)

                first_delete.link = bucket_link+'images/'+filename
                db.session.commit()
        
        new_image = db.session.query(Pictures).filter_by(property_id=text['id']).first()

        if new_image is not None:
            if first_pic != new_image.link:
                
                old_thumb = prop.thumbnail
                txt_split3 = re.split(bucket_link, old_thumb)[1]
                obj = s3.Object(bucket_name, txt_split3)

                response = requests.get(new_image.link)
                image = Image.open(io.BytesIO(response.content))
                thumb_size = 150, 300
                in_mem_file = io.BytesIO()
                pic_image = image.copy()
                pic_image.thumbnail(thumb_size, Image.Resampling.LANCZOS)  
                pic_image.save(in_mem_file, format="PNG")
                in_mem_file.seek(0)

                txt_split2 = re.split(bucket_link, new_image.link)[1]
                s3.Bucket(bucket_name).upload_fileobj(in_mem_file, txt_split2)
                prop.thumbnail = bucket_link+"thumbnails/"+txt_split2
                db.session.commit()
                
    return 'ok'

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

        property = Property(saletype=sale_type, value=value, address=address, owner=owner, locations_id=location_id['id'], uploaded_by=current_user.id)

        db.session.add(property)
        db.session.commit()
        idd = property.id

        session = boto3.Session(
            aws_access_key_id=os.getenv('AWS_KEY'),
            aws_secret_access_key=os.getenv('AWS_SEC_KEY'),
        )

        s3 = session.resource('s3')
        bucket_name = os.getenv('BUCKET_NAME')
        bucket_link = os.getenv('BUCKET_LINK')

        for index, picture in enumerate(pictures):
            
            filename = uuid.uuid4().hex + '_' + secure_filename(picture.filename)
            
            if index == 0:
                image = Image.open(picture)
                thumb_size = 150, 300
                in_mem_file = io.BytesIO()
                in_mem_file2 = io.BytesIO()
                pic_image = image.copy()
                pic_image.thumbnail(thumb_size, Image.Resampling.LANCZOS)  
                pic_image.save(in_mem_file, format="PNG")
                in_mem_file.seek(0)
                s3.Bucket(bucket_name).upload_fileobj(in_mem_file, "thumbnails/"+filename)
                property.thumbnail = bucket_link+"thumbnails/"+filename
                image.save(in_mem_file2, format="PNG")
                in_mem_file2.seek(0)
                s3.Bucket(bucket_name).upload_fileobj(in_mem_file2, "images/"+filename)
                file = Pictures(link = bucket_link+"images/"+filename, property_id = idd )
                db.session.add(file)
                db.session.commit()
            
            else:
                s3.Bucket(bucket_name).upload_fileobj(picture, "images/"+filename)
                file = Pictures(link = bucket_link+"images/"+filename, property_id = idd )
                db.session.add(file)
                db.session.commit()


                
        return redirect(url_for('views.employee'))


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
            return listado

    elif len(jsonData.keys()) == 3:
        if 'state' in jsonData:
            properties = db.session.query(Property).join(Property.locations).filter(Property.saletype == jsonData['type'], Location.city == jsonData['city'], Location.state == jsonData['state']).all()
            sProperties = PropertiesSchema(many=True)
            listado = sProperties.dump(properties)
            return listado