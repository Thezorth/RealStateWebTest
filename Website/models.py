from . import db, ma
from flask_login import UserMixin

###################################### CLASSES ######################################

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    unique_id = db.Column(db.String(150), unique=True)
    email = db.Column(db.String(150), unique=True)
    username = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))

class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))

    properties = db.relationship('Property', back_populates='locations', lazy=True)

    def __repr__(self):
        return f'city:{self.city}, state:{self.state}'

class Property(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    saletype = db.Column(db.String(50))
    owner = db.Column(db.String(150))
    value = db.Column(db.Integer)
    address = db.Column(db.String(150))
    thumbnail = db.Column(db.String)

    locations_id = db.Column(db.Integer, db.ForeignKey('location.id'))
    locations = db.relationship('Location', back_populates='properties', lazy=True)

    pictures = db.relationship('Pictures', back_populates='property', lazy=True)

    uploaded_by = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'Saletype:{self.saletype}, Owner:{self.owner}, Value:{self.value}, Address:{self.address}'

class Pictures(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    link = db.Column(db.String(150))

    property_id = db.Column(db.Integer, db.ForeignKey('property.id'))
    property = db.relationship('Property', back_populates='pictures', lazy=True)
    
    def __repr__(self):
        return f'Link:{self.link}'

###################################### SCHEMAS ######################################
    
class PropertiesSchema(ma.SQLAlchemySchema):
    class Meta():
        model = Property
    
    id = ma.auto_field()
    saletype = ma.auto_field()
    owner = ma.auto_field()
    value = ma.auto_field()
    address = ma.auto_field()
    thumbnail = ma.auto_field()

class LocationSchema(ma.SQLAlchemySchema):
    class Meta():
        model = Location

    id = ma.auto_field()
    city = ma.auto_field()
    state = ma.auto_field()

class PicturesSchema(ma.SQLAlchemySchema):
    class Meta():
        model = Pictures

    id = ma.auto_field()
    link = ma.auto_field()