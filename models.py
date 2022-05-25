
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_moment import Moment
import datetime
app = Flask(__name__)
db = SQLAlchemy(app)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(), nullable=False)
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String()), nullable=False)
    website = db.Column(db.String(100))
    seeking_talent = db.Column(db.Boolean(), default=False)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref='Venue', lazy=True)

    def __repr__(self):
        return f'<Venue {self.id} {self.name} {self.city} {self.state} {self.address} {self.phone} {self.image_link} {self.facebook_link} {self.genres} {self.website} {self.seeking_talent} {self.seeking_description} {self.shows}>'

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.ARRAY(db.String()), nullable=False)
    image_link = db.Column(db.String(), nullable=False)
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(100))
    seeking_venue = db.Column(db.Boolean(), default=False)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref='Artist', lazy=True)
    
    def __repr__(self):
        return f'<Artist {self.id} {self.name}>'


class Show(db.Model):
    __tablename__ = 'Show'
    
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey(
        'Artist.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f'<Show {self.id} {self.artist_id} {self.venue_id} {self.start_time}>'

