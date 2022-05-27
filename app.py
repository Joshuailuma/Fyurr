#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import json
import dateutil.parser
import babel
import dateutil.parser
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from sqlalchemy.orm.exc import NoResultFound
from models import db, Venue, Artist, Show

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.app = app
db.init_app(app)
migrate = Migrate(app, db)


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
# Display list of venues
def venues():
  
  # The list of data =  we want to display
  data = [] 
 
  final_dictionary = {}

  # Perform a query in our database for venues
  venue_data = Venue.query.all()

  # Loop through the result, so we can use each data =  from it
  for location in venue_data:
    key = f'{location.city}, {location.state}'

    final_dictionary.setdefault(key, []).append({
      "id": location.id,
      "name": location.name,
      "city": location.city,
      "state": location.state,
      "num_upcoming_shows": len(location.shows),
    })

  # This adds the final dictionary to the list variable called data = 
  for value in final_dictionary.values():
    
      data.append({
        'city': value[0]['city'],
        'state': value[0]['state'],
        'venues': value
      })
    
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form.get('search_term', '')
  venue_result = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()

  response = {
    "count": len(venue_result),
    "data": []
  }

  for venue in venue_result:
    response["data"].append({
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows": len(venue.shows)
    })
  
  print(venue_result)
  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
# DIsplay venue detail according to its ID
def show_venue(venue_id):
  # shows the venue page with the given venue_id
 

  # To get the venue by id
  venues = Venue.query.filter_by(id=venue_id).all()

  past_shows = []
  upcoming_shows = []
  final_dictionary = {}

  for venue in venues:
    # Get the show object after iterating over venue
    # shows = venue.shows
    shows = db.session.query(Show).join(Venue.shows)
    
    # iterate over shows object
    for new_venue in shows:
       print(Show)
        # Put the different items in shows in a dictionary
       venues_in_shows = {
       "artist_id": new_venue.artist_id,
       "start_time": new_venue.start_time.strftime('%m/%d/%Y, %H:%M:%S')
       }

        # Use the artist id to get its details from the artist table
       artists = Artist.query.filter_by(id=new_venue.artist_id).all()
       for artist in artists:
         artists_in_artist = {
           "artist_name": artist.name,
           "artist_image_link": artist.image_link,
         }
          # Add the needed items to final_dictionary
         final_dictionary.update({
           "artist_id": venues_in_shows["artist_id"],
           "artist_name": artists_in_artist["artist_name"],
           "artist_image_link": artists_in_artist["artist_image_link"],
           "start_time": venues_in_shows["start_time"]
         })
         
         # To gruop shows according to time (past or future)
         if new_venue.start_time <= datetime.now():
           past_shows.append(final_dictionary)
         else:
           upcoming_shows.append(final_dictionary)

  data ={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows)
  }
   
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
# Store venue in database after creation
def create_venue_submission():
  form = VenueForm(request.form)

  if form.validate():
    
    # Get the data from our front-end
    name = form.name.data
    city = form.city.data
    state = form.state.data
    address = form.address.data
    phone = form.phone.data
    image_link = form.image_link.data
    facebook_link = form.facebook_link.data
    website_link = form.website_link.data
    seeking_description = form.seeking_description.data
    genres = form.genres.data
    seeking_talent = True if form.seeking_talent.data else False

    # Assign the data to the properties of the Venue table  
    new_venue = Venue(name=name,city=city,state=state,address=address,phone=phone,
    image_link=image_link,facebook_link=facebook_link,website=website_link,
    seeking_description=seeking_description,seeking_talent=seeking_talent, genres=genres)
    # Add the data to our database and handle exceptions
    try:
      db.session.add(new_venue)
      db.session.commit()
      error = False
    except:
      db.session.rollback()
      error = True      
    finally:
      db.session.close()
      # To show notification if succesful or not.
    if error :
      flash('An error occurred. Venue ' + form.name.data  + ' could not be listed.')
      return render_template('pages/home.html')
    elif not error:
      flash('Venue ' + form.name.data  + ' was successfully listed!')
      return render_template('pages/home.html')
  else:
    flash('Please fill out the form before submitting')
    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
# Delete a venue from database
def delete_venue(venue_id):

  try:
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
    error = False

  except:
    db.session.rollback()
    error = True

  finally:
    db.session.close()

  if error:
    flash('An error occurred. Venue couldn\'t be deleted')
    return render_template('pages/home.html')
  elif not error:
    flash('Venue was successfully deleted!')
    return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
# Display name of artists
def artists():
  # A list that will hold the artists
  data = []
  artists = Artist.query.all()

# Iterate over artists andd add them to a dictionary
  for artist in artists:
    final_dictionary = {
      "id": artist.id,
      "name": artist.name
    }

  # Add the values in the dictionary to the data list
    data.append(final_dictionary)

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
# Implement Artist search
def search_artists():
  search_term = request.form.get('search_term', '')
  artist_result = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()

  response = {
    "count": len(artist_result),
    "data": []
  }

  for artist in artist_result:
    response["data"].append({
      "id": artist.id,
      "name": artist.name,
      "num_upcoming_shows": len(artist.shows)
    })

  return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
# Display details of Artist according to its ID
def show_artist(artist_id):
  # Get the artist by id
  artists = Artist.query.filter_by(id=artist_id).all()

  past_shows = []
  upcoming_shows = []
  final_dictionary = {}

  for artist in artists:
    # Get the artist object after iterating over artists
    shows = db.session.query(Show).join(Artist.shows)
    
    # iterate over shows object
    for new_artist in shows:
        # Put the different items in shows in a dictionary
       artists_in_shows = {
       "artist_id": new_artist.artist_id,
       "start_time": new_artist.start_time.strftime('%m/%d/%Y, %H:%M:%S')
       }

        # Use the artist id to get its details from the venues table
       venues = Venue.query.filter_by(id=new_artist.venue_id).all()
       for venue in venues:
         venues_in_venue = {
           "venue_id": venue.id,
           "venue_name": venue.name,
           "venue_image_link": venue.image_link,
         }
          # Add the needed items to final_dictionary
         final_dictionary.update({
          "venue_id": venues_in_venue["venue_id"],
           "venue_name": venues_in_venue["venue_name"],
           "venue_image_link": venues_in_venue["venue_image_link"],
           "start_time": artists_in_shows["start_time"]
         })
         
         # To group shows according to time (past or future)
         if new_artist.start_time <= datetime.now():
           past_shows.append(final_dictionary)
         else:
           upcoming_shows.append(final_dictionary)
# List of data required by html
  data = {
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows)
  }
 
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
# Implement editing of Artists
def edit_artist(artist_id):
  form = ArtistForm(request.form)

  # Access the database
  artists = Artist.query.filter_by(id=artist_id).all()

  for item in artists:
    artist = {
    "id": item.id,
    "name": item.name,
    "genres": item.genres,
    "city": item.city,
    "state": item.state,
    "phone": item.phone,
    "website": item.website,
    "facebook_link": item.facebook_link,
    "seeking_venue": item.seeking_venue,
    "seeking_description": item.seeking_description,
    "image_link": item.image_link,
  }

  # Assign data gotten from the database to the form
  form.name.data = item.name
  form.city.data = item.city
  form.state.data = item.state
  form.phone.data = item.phone
  form.genres.data = item.genres
  form.facebook_link.data = item.facebook_link
  form.image_link.data = item.image_link
  form.website_link.data = item.website
  form.seeking_description.data = item.seeking_description
  form.seeking_venue.data = item.seeking_venue

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
# implement updating database after edit
def edit_artist_submission(artist_id):
  form = ArtistForm(request.form)
  artist = Artist.query.get(artist_id)
  if form.validate():

    try:
      # Assign new data gotten from form to database
      artist.name = form.name.data
      artist.city = form.city.data
      artist.state = form.state.data
      artist.phone = form.phone.data
      artist.image_link = form.image_link.data
      artist.facebook_link = form.facebook_link.data
      artist.website = form.website_link.data
      artist.seeking_description = form.seeking_description.data
      artist.genres = form.genres.data
      artist.seeking_venue = True if form.seeking_venue.data else False

      db.session.commit()
      flash('Artist ' + artist.name  + ' was successfully updated!')
    except:
      flash('An error occurred. Artist ' + artist.name  + ' could not be updated.')
      db.session.rollback()
    finally:
      db.session.close()
  
    return redirect(url_for('show_artist', artist_id=artist_id))
  else:
    flash('There is an error within the form')
    return redirect(url_for('show_artist', artist_id=artist_id))
  

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
# Implement Edit venue
def edit_venue(venue_id):
  form = VenueForm(request.form)

  # Access the database
  venues = Venue.query.filter_by(id=venue_id).all()

  for item in venues:
    venue = {
    "id": item.id,
    "name": item.name,
    "genres": item.genres,
    "address": item.address,
    "city": item.city,
    "state": item.state,
    "phone": item.phone,
    "website": item.website,
    "facebook_link": item.facebook_link,
    "seeking_talent": item.seeking_talent,
    "seeking_description": item.seeking_description,
    "image_link": item.image_link,
  }


  # Assign data gotten from the database to the form
  form.name.data = item.name
  form.city.data = item.city
  form.state.data = item.state
  form.phone.data = item.phone
  form.genres.data = item.genres
  form.facebook_link.data = item.facebook_link
  form.image_link.data = item.image_link
  form.website_link.data = item.website
  form.seeking_description.data = item.seeking_description
  form.seeking_talent.data = item.seeking_talent

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # Take values from the form submitted, and update existing
  # venue record 
  form = VenueForm(request.form)
  if form.validate():
    venue = Venue.query.get(venue_id)
    # Assign new data gotten from form to database
    try:
      venue.name = form.name.data
      venue.city = form.city.data
      venue.state = form.state.data
      venue.phone = form.phone.data
      venue.image_link = form.image_link.data
      venue.facebook_link = form.facebook_link.data
      venue.website = form.website_link.data
      venue.seeking_description = form.seeking_description.data
      venue.genres = form.genres.data
      venue.seeking_talent = True if form.seeking_talent.data else False

      db.session.commit()
      flash('Venue ' + form.name.data  + ' was successfully updated!')
    except:
      flash('An error occurred. Venue ' + form.name.data  + ' could not be updated.')
      db.session.rollback()
    finally:
      db.session.close()
    return redirect(url_for('show_venue', venue_id=venue_id))
  else:
    flash('Please fill out the fields before submitting')
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # Called upon submitting the new artist listing form
  form = ArtistForm(request.form)
  if form.validate():

    name = form.name.data
    city = form.city.data
    state = form.state.data
    phone = form.phone.data
    image_link = form.image_link.data
    facebook_link = form.facebook_link.data
    website_link = form.website_link.data
    seeking_description = form.seeking_description.data
    genres = form.genres.data
    seeking_venue = True if form.seeking_venue.data else False

    
    new_artist = Artist(name=name,city=city,state=state,phone=phone,
    image_link=image_link,facebook_link=facebook_link,website=website_link,
    seeking_description=seeking_description,seeking_venue=seeking_venue, genres=genres)


    try:
      db.session.add(new_artist)
      db.session.commit()
      error = False
    except:
      db.session.rollback()
      error = True
    finally:
      db.session.close()
    if error :
      flash('An error occurred. Artist ' + form.name.data  + ' could not be listed.')
      print(sys.exc_info())
      return render_template('pages/home.html')
    elif not error:
      flash('Artist ' + form.name.data  + ' was successfully listed!')
      return render_template('pages/home.html')
  else:
    flash('Please fill out the fields before submitting')
    return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
# Display shows
def shows():

  # The list of data =  we want to display
  data = []

  final_dictionary = {}

  # Perform a query in our database for shows
  show_data = Show.query.all()

  # Loop through the result, so we can use each data =  from it
  for shows in show_data:
    key = f'{shows.artist_id}, {shows.venue_id}'
    artist = Artist.query.get(shows.artist_id)
    venue = Venue.query.get(shows.venue_id)

    final_dictionary.setdefault(key, []).append({
      "venue_id": shows.venue_id,
      "venue_name": venue.name,
      "artist_id": shows.artist_id,
      "artist_name": artist.name,
      "artist_image_link": artist.image_link,
      "start_time": shows.start_time.strftime('%m/%d/%Y, %H:%M:%S'),
    })



  # This adds the final dictionary to the list variable called data = 
  for value in final_dictionary.values():  
      data.append({
        'venue_id': value[0]['venue_id'],
        'venue_name': value[0]['venue_name'],
        'artist_id': value[0]['artist_id'],
        'artist_name': value[0]['artist_name'],
        'artist_image_link': value[0]['artist_image_link'],
        'start_time': value[0]['start_time'],
      })

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  form = ShowForm(request.form)

  if form.validate():
    
    artist_id = form.artist_id.data
    venue_id = form.venue_id.data
    start_time = form.start_time.data

    
    new_show = Show(artist_id=artist_id,venue_id=venue_id,start_time=start_time)

    try:
      db.session.add(new_show)
      db.session.commit()
      error = False
    except:
      db.session.rollback()
      error = True
        
    finally:
      db.session.close()
    if error :
      flash('An error occurred. Show could not be listed.')
      return render_template('pages/home.html')
    elif not error:
      flash('Show was successfully listed!')
      return render_template('pages/home.html')
  else:
    flash('Please fill out the fields before submitting')
    return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
