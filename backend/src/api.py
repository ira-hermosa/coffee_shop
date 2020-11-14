#-------------------------------------------------------------#
# Imports
#-------------------------------------------------------------#

import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

#-------------------------------------------------------------#
# App config
#-------------------------------------------------------------#

app = Flask(__name__)
setup_db(app)
# Set up CORS
CORS(app)

# After_request decorator to set Access-Control-Allow


@app.after_request
def after_request(response):
    response.headers.add(
        'Access-Control-Allow-Headers',
        'Content-Type, Authorization, true')
    response.headers.add(
        'Access-Control-Allow-Methods',
        'GET, PUT, POST, DELETE, PATCH, OPTIONS')
    return response


# Drops all records and starts the db from scratch
db_drop_and_create_all()


#------------------------------------------------------------#
# Endpoints
#------------------------------------------------------------#

# Get short representation of all drinks in the db
@app.route('/drinks')
def get_drinks():
    drinks = list(map(Drink.short, Drink.query.all()))

    return jsonify({
        'success': True,
        'drinks': drinks
    })


# Get long representation of drink details in the db
# Requires the 'get:drinks-detail' permission set on Auth0
@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_details(token):
    try:
        drinks = list(map(Drink.long, Drink.query.all()))

        return jsonify({
            'success': True,
            'drinks': drinks
        })

    except BaseException:
        abort(422)


# Create a new drink in the db
# Requires the 'post:drinks' permission set on Auth0
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_new_drink(token):

    if request.data:
        body = request.get_json()
        title = body.get('title', None)
        recipe = body.get('recipe', None)

        drink = Drink(title=title, recipe=json.dumps(recipe))
        Drink.insert(drink)

        new_drink = Drink.query.filter_by(id=drink.id).first()

        return jsonify({
            'success': True,
            'drinks': [new_drink.long()]
        })
    else:
        abort(422)


# Updates an existing drink in the db
# Requires the 'patch:drinks' permission set on Auth0
@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink_by_id(token, drink_id):

    body = request.get_json()
    title = body.get('title', None)
    recipe = body.get('recipe', None)

    try:
        drink = Drink.query.filter_by(id=drink_id).one_or_none()
        if drink is None:
            return json.dumps({
                'success': False,
                'error': 'Drink #' + id + ' not found to be updated'
            }), 404

        if title is None:
            abort(400)

        if title is not None:
            drink.title = title

        if recipe is not None:
            drink.recipe = json.dumps(recipe)

        drink.update()
        updated_drink = Drink.query.filter_by(id=drink_id).first()

        return jsonify({
            'success': True,
            'drinks': [updated_drink.long()]
        })

    except BaseException:
        abort(422)


# Deletes an existing drink in the db by id
# Requires the 'delete:drinks' permission set on Auth0

@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(token, drink_id):
    try:
        drink = Drink.query.filter_by(id=drink_id).one_or_none()
        if drink is None:
            abort(404)

        drink.delete()

        return jsonify({
            'success': True,
            'deleted': drink_id
        })
    except BaseException:
        abort(422)

#----------------------------------------------------------------#
# Error Handlers
#----------------------------------------------------------------#


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error['description']
    }), error.status_code


@app.errorhandler(401)
def anauthorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": 'Unauthorized'
    }), 401


@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": 'Internal server error'
    }), 500


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": 'Bad request'
    })


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "success": False,
        "error": 405,
        "message": 'Method not allowed'
    })


# if __name__ == '__main__':
    # app.run()
