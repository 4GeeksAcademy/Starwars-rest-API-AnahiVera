"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, People, Planet, Favorite_people, Favorite_planet
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
MIGRATE = Migrate(app, db)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code



# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)


@app.route('/people', methods=['GET'])
def get_people():

    people = People.query.all()
    people =list(map(lambda people: people.serialize(), people))

    return jsonify(people), 200

@app.route('/people/<int:people_id>', methods=['GET'])
def get_person(people_id):

    person = People.query.get(people_id)
    
    return jsonify(person.serialize()), 200

@app.route('/planets', methods=['GET'])
def get_planets():

    planets = Planet.query.all()
    planets =list(map(lambda planet: planet.serialize(), planets))

    return jsonify(planets), 200

@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):

    planet = Planet.query.get(planet_id)
    
    return jsonify(planet.serialize()), 200


@app.route('/users', methods=['GET'])
def get_user():

    users = User.query.all()
    users =list(map(lambda user: user.serialize(), users))

    return jsonify(users), 200

@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():

    user = User.query.get(1)
    favorite_people = favorite_people.query.filter_by(user_id=user.id)
    favorite_planet = favorite_planet.query.filter_by(user_id=user.id)

    favoritos = {
        "favorite_people": favorite_people.serialize(),
        "favorite_planet": favorite_planet.serialize(),
    }

    return jsonify(favoritos), 200


@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):

    user= User.query.get(1)
    planet = Planet.query.get(planet_id)

    existing_favorite = Favorite_planet.query.filter_by(user_id=user.id, planet_id=planet.id).first()
    if existing_favorite:
        return jsonify({"message": "Planet already in favorites."}), 400

    favorite = Favorite_planet(user_id=user.id, planet_id= planet.id)

    db.session.add(favorite)
    db.session.commit()
    return jsonify(favorite.serialize()), 201


@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_people(people_id):

    user= User.query.get(1)
    people = People.query.get(people_id)

    existing_favorite = Favorite_people.query.filter_by(user_id=user.id, people_id=people.id).first()
    if existing_favorite:
        return jsonify({"message": "Person already in favorites."}), 400
    
    favorite = Favorite_people(user_id=user.id, people_id= people.id)

    db.session.add(favorite)
    db.session.commit()
    return jsonify(favorite.serialize()), 201


@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    user= User.query.get(1)
    planet = Planet.query.get(planet_id)
    favorite = Favorite_planet.query.filter_by(user_id=user.id, planet_id= planet.id).first()

    db.session.delete(favorite)
    db.session.commit()
    return jsonify({"message": "Favorite planet deleted."}), 200

@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_people(people_id):
    user= User.query.get(1)
    people = People.query.get(people_id)
    favorite = Favorite_people.query.filter_by(user_id=user.id, people_id= people.id).first()

    db.session.delete(favorite)
    db.session.commit()
    return jsonify({"message": "Favorite person deleted."}), 200

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
