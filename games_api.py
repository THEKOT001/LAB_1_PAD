from flask import Flask, jsonify, request
import pymongo
from bson.objectid import ObjectId

# initialize Flask app
app = Flask(__name__)

# connect to MongoDB database
mongo_client = pymongo.MongoClient('mongodb://localhost:27017/')
mongo_db = mongo_client['games_db']
games_collection = mongo_db['games']
rating_collection = mongo_db['ratings']

# define game schema for MongoDB collection
game_schema = {
    'name': str,
    'author': str,
    'studio': str,
    'date_of_release': str,
    'availability': bool,
    'price': float,
    'rating': list,
    'final_rating': float
}
# rating_schema = {
#     # the name should be taken from the schema above, so it will be the same
#     "name": str,
#     # the average will change every time then the new rating is added
#     "average": float,
#     "rating_1": int
#     # "rating_2": int,
#     # "rating_3": int
#     # add more rating fields as needed
# }
# comment_schema = {
#     "game": str,
#     "user": str,
#     "type": str,
#     "lvl": int,
#     "comment": str,
#     "rating": int
#
# }

# define endpoint to get games from the MongoDB database
@app.route('/games', methods=['GET'])
def get_all_games():
    game_list = []
    for game in games_collection.find():
        game['_id'] = str(game['_id'])
        game_list.append(game)
    return jsonify(game_list),201


# define endpoint to add games to the MongoDB database
@app.route('/games', methods=['POST'])
def add_game():
    # get game data from request body
    game_data = request.get_json()
    # validate game data
    game_data['rating'] = []
    game_data['final_rating'] = 0
    for key, value_type in game_schema.items(): # Using dict.items() to loop through dict key-value pairs
        if key not in game_data:
            return jsonify({'message': f'Missing {key} parameter in request.'}), 400
        elif not isinstance(game_data[key], value_type): # Use isinstance() to check value type
            return jsonify({'message': f'{key} parameter has incorrect data type.'}), 400
    # insert game data into MongoDB database
    games_collection.insert_one(game_data)
    # return success message
    return jsonify({'message': f'{game_data["name"]} added to games collection.'}), 201

@app.route('/games/rating', methods=['PUT'])
def add_rating():
    game_id = request.json['_id']
    new_rating = request.json['rating']
    game = games_collection.find_one({'_id': ObjectId(game_id)})
    if not game:
        return {'error': 'Game not found'}, 404
    # Calculate the medium rating
    rating = game['rating']
    rating.append(new_rating)
    final_rating = sum(rating) / len(rating)

    rating = game['rating']
    result = games_collection.update_one({'_id': ObjectId(game_id)}, {'$set': {'rating': rating, 'final_rating': final_rating}})
    return {'final_rating': final_rating}, 201

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