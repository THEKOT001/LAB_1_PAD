# import necessary packages and dependencies
from flask import Flask, jsonify, request
import pymongo

# initialize Flask app
app = Flask(__name__)

# connect to MongoDB database
mongo_client = pymongo.MongoClient('mongodb://localhost:27017/')
mongo_db = mongo_client['games_db']
games_collection = mongo_db['games']

# define game schema for MongoDB collection
game_schema = {
    'name': str,
    'author': str,
    'studio': str,
    'date_of_release': str,
    'availability': bool,
    'price': float
}


# # insert some sample games data for testing purposes
# sample_games = [
#     {'name': 'Game 1', 'author': 'Author 1', 'studio': 'Studio 1', 'date_of_release': '2022-01-01',
#      'availability': True, 'price': 49.99},
#     {'name': 'Game 2', 'author': 'Author 2', 'studio': 'Studio 2', 'date_of_release': '2022-02-01',
#      'availability': False, 'price': 29.99},
#     {'name': 'Game 3', 'author': 'Author 3', 'studio': 'Studio 3', 'date_of_release': '2022-03-01',
#      'availability': True, 'price': 39.99}
# ]
# games_collection.insert_many(sample_games)


# define endpoint to get games from the MongoDB database
@app.route('/games', methods=['GET'])
def get_games():
    # get games from MongoDB database
    games = list(games_collection.find({}, {'_id': 0}))
    # return retrieved games data
    return jsonify({'games': games}), 201


# define endpoint to add games to the MongoDB database
@app.route('/games', methods=['PUT'])
def add_game():
    # get game data from request body
    game_data = request.get_json()
    # validate game data
    for key in game_schema.keys():
        if key not in game_data.keys():
            return jsonify({'message': f'Missing {key} parameter in request.'}), 400
        elif type(game_data[key]) != game_schema[key]:
            return jsonify({'message': f'{key} parameter has incorrect data type.'}), 400
    # insert game data into MongoDB database
    games_collection.insert_one(game_data)
    # return success message
    return jsonify({'message': f'{game_data["name"]} added to games collection hui.'}), 201

    # define endpoint to delete games from the MongoDB database


@app.route('/games', methods=['DELETE'])
def delete_game():
    # get game name from request parameters
    game_name = request.args.get('name')
    # delete game from MongoDB database
    result = games_collection.delete_one({'name': game_name})
    # return success or failure message
    if result.deleted_count > 0:
        return jsonify({'message': f'{game_name} deleted from games collection.'})
    else:
        return jsonify({'message': f'{game_name} not found in games collection.'}), 404



# define endpoint to check the availability and functionality of the Second API
@app.route('/status')
def status():
    # check if MongoDB database is connected
    mongo_status = 'MongoDB database connected.' if mongo_client.server_info() else 'MongoDB database not connected.'
    # return status of Second API and MongoDB database
    return jsonify({'second_api': 'Second API connected.', 'mongo': mongo_status})


# # define endpoint to delete all games from the MongoDB database
# @app.route('/games/delete_all', methods=['DELETE'])
# def delete_all_games():
#     # delete all games from MongoDB database
#     result = games_collection.delete_many({})
#     # return success message
#     return jsonify({'message': f'{result.deleted_count} games deleted from games collection.'}), 200



# run Flask app if executed as main module
if __name__ == '__main__':
    app.run(debug=True, port=5001)
