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
from models import db, User, People, FavPeople, Planets, FavPlanet
import json
#from models import Person
# import jwt
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
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

# GET para Listar todos los usuarios   

@app.route('/user', methods=['GET'])
def get_User():
    all_user = User.query.all()
    serializados = list(map(lambda user: user.serialize(),all_user))
    print(all_user)
    return jsonify({
        "mensaje": "Todos los Usuarios",
        "users": serializados
    }), 200
# njxbwsx
# GET para Listar todos los registros de people

@app.route('/people', methods=['GET'])
def getPeople():
    all_people = People.query.all()
    serializados = list( map( lambda people: people.serialize(), all_people))
    print(all_people)

    return jsonify({
        "mensaje": "Todos los Personajes",
        "people": serializados
    }), 200

# Get para Listar la información de una sola people

@app.route('/people/<int:idpeople>', methods=['GET'])
def dinamycPeople(idpeople):
    one = People.query.filter_by(uid=idpeople).first()
    if(one):
        return jsonify({
            "id": idpeople,
            "people": one.serialize()
        }), 200
        
    else:
        return jsonify({
                "id": idpeople,
                "people": "not found!"
        }), 404

# GET para  Listar los registros de planets

@app.route('/planets', methods=['GET'])
def getPlanets():
    all_planets = Planets.query.all()
    serializados = list( map( lambda planets: planets.serialize(), all_planets))
    print(all_planets)

    return jsonify({
        "mensaje": "Todos los Planetas",
        "planets": serializados
    }), 200

    # GET para Listar la información de un solo planet

@app.route('/planets/<int:idplanets>', methods=['GET'])
def dinamycPlanets(idplanets):
    one = Planets.query.filter_by(uid=idplanets).first()
    if(one):
        return jsonify({
            "id": idplanets,
            "planets": one.serialize()
        }), 200
        
    else:
        return jsonify({
                "id": idplanets,
                "planets": "not found!"
        }), 404

        # POST para añadir una nueva people

@app.route("/favorite/people/<int:people_id>", methods=['POST'])
def postPeopleFav(people_id):
    body = request.get_json() #recibir datos del usuario
    #people_id = 4
    #email = freddyloboq@gmail.com
    newFav = FavPeople(user=body['email'], people = people_id)
    db.session.add(newFav)
    db.session.commit()
    return "nuevo favorito agregado"

    # POST para añadir un nuevo planet

@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def postFavPlanet(planet_id):
    body = request.get_json() #recibir datos del usuario
    one = Planets.query.get(planet_id)
    oneSerializado = one.serialize()
    newFav = FavPeople(user=body['email'], planets=oneSerializado["name"])
    db.session.add(newFav)
    db.session.commit()
    return "nuevo favorito agregado"

    # DELETE para Elimina una people

@app.route("/favorite/people/<int:position>", methods=['DELETE'])
def deletePeopleFav(position):
    delete_people = FavPeople.query.filter(FavPeople.id == position).delete()
    
    if delete is None:
        response_body = {"msg":"People not found"}
        return jsonify(response_body), 400
    
    db.session.delete(delete_people)
    db.session.commit()
    response_body = {"msg":"People borrado"}
    return jsonify(response_body), 200

    # DELETE para Elimina un planet

@app.route("/favorite/planets/<int:position>", methods=['DELETE'])
def deletePlanetsFav(position):
    delete_planets =FavPlanet.query.filter(FavPlanet.id == position).delete()

    if delete is None:
         response_body = {"msg":"Planet not found"}
         return jsonify(response_body), 400
   
    db.session.delete(delete_planets)
    db.session.commit()
    response_body = {"msg":"Planet borrado"}
    return jsonify(response_body), 200

# Create a route to authenticate your users and return JWTs. The
# create_access_token() function is used to actually generate the JWT.
@app.route("/login", methods=["POST"])
def login():
    email = request.json.get("email", None)
    password = request.json.get("password", None)

    user = User.query.filter_by(email=email).first()

    if user is None:
        return jsonify({"msg": "user no existe"}), 404
    
    if email != user.email or password != user.password:
        return jsonify({"msg": "Bad email or password"}), 401
    
    access_token = create_access_token(identity=email)
    
    response_body = {
        "access_token":access_token, 
        "user": user.serialize()}   

    return jsonify(response_body), 200

# Protect a route with jwt_required, which will kick out requests
# without a valid JWT present.
@app.route("/profile", methods=["GET"])
@jwt_required()
def protected():
    
    current_user = get_jwt_identity()
    print(current_user)
    user = User.query.filter_by(email=current_user).first()
    
    if user is None:
        return jsonify({"msg": "user no existe"}), 404

    response_body = { 
        "user": user.serialize()} 

    return jsonify(response_body), 200

    @app.route("/profile", methods=["GET"])
    @jwt_required()
    def protected():
    
        current_user = get_jwt_identity()
    user = User.query.filter_by(email=current_user).first()
    
    if user is None:
        return jsonify({"msg":"User doesn't exist"}), 404
    
    response_body = {
    "user": user.serialize()
        
    }
    return jsonify(response_body), 200


@app.route("/valid-token", methods=["GET"])
@jwt_required()
def valid_token():
    
    current_user = get_jwt_identity()
    user = User.query.filter_by(email=current_user).first()
    
    if user is None:
        return jsonify({"status":False}), 404
    
    response_body = {
        "status": True,
        "user": user.serialize()
        
    }
    return jsonify(response_body), 200     

# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
