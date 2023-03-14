from flask import Flask, jsonify, request
import pymongo
from bson.objectid import ObjectId
from datetime import datetime

# initialize Flask app
app = Flask(__name__)

# connect to MongoDB database
mongo_client = pymongo.MongoClient('mongodb://localhost:27017/')
mongo_db = mongo_client['games_db']
# games_collection = mongo_db['games']
# rating_collection = mongo_db['ratings']
news_collection = mongo_db['news']

# define game schema for MongoDB collection
news_schema = {
    "title": str,
    "author": str,
    "content": str,
    "comments": list
}


# define endpoint to get games from the MongoDB database
@app.route('/news', methods=['GET'])
def get_all_news():
    news_list = []
    for news in news_collection.find():
        news['_id'] = str(news['_id'])
        news_list.append(news)
    return jsonify(news_list), 201


# define endpoint to add games to the MongoDB database
@app.route('/news', methods=['PUT'])
def add_news():
    # Get the current datetime as a UTC timestamp
    timestamp = datetime.utcnow()

    # get game data from request body
    news_data = request.get_json()
    # validate game data
    # game_data['rating'] = []
    # game_data['final_rating'] = 0
    news_data.update({'comments': [], 'timestamp': timestamp})  # add 'timestamp' field
    for key, value_type in news_schema.items():
        # Using dict.items() to loop through dict key-value pairs
        if key not in news_data:
            return jsonify({'message': f'Missing {key} parameter in request.'}), 400
        elif not isinstance(news_data[key], value_type):  # Use isinstance() to check value type
            return jsonify({'message': f'{key} parameter has incorrect data type.'}), 400
    # insert game data into MongoDB database
    news_collection.insert_one(news_data)
    # return success message
    return jsonify({'message': f'{news_data["title"]} added to news collection.'}), 201


@app.route('/news/comment', methods=['PUT'])
def add_comment():
    news_id = request.json.get('_id')
    new_comment = request.json.get('comments')
    news = news_collection.find_one({'_id': ObjectId(news_id)})
    if not news:
        return {'error': 'News not found'}, 404
    # Calculate the medium rating
    comment = news.get('comment', [])
    comment.append(new_comment)
    news_collection.update_one({'_id': ObjectId(news_id)},
                               {'$set': {'comments': comment}})
    return {'comments': comment}, 201


@app.route('/news', methods=['DELETE'])
def delete_news():
    # get game name from request parameters
    news_title = request.args.get('title')
    # delete news from MongoDB database
    result = news_collection.delete_one({'title': news_title})
    # return success or failure message
    if result.deleted_count > 0:
        return jsonify({'message': f'{news_title} deleted from games collection.'})
    else:
        return jsonify({'message': f'{news_title} not found in games collection.'}), 404


# define endpoint to check the availability and functionality of the Second API
@app.route('/news/status')
def status():
    # check if MongoDB database is connected
    mongo_status = 'MongoDB database for news connected.' if mongo_client.server_info() else 'MongoDB database for ' \
                                                                                             'news  not connected.'
    # return status of Second API and MongoDB database
    return jsonify({'News_Api': 'News API connected.', 'mongo': mongo_status})


# # define endpoint to delete all games from the MongoDB database
# @app.route('/games/delete_all', methods=['DELETE'])
# def delete_all_games():
#     # delete all games from MongoDB database
#     result = games_collection.delete_many({})
#     # return success message
#     return jsonify({'message': f'{result.deleted_count} games deleted from games collection.'}), 200


# run Flask app if executed as main module
if __name__ == '__main__':
    app.run(debug=True, port=5002)
