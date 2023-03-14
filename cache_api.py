# import necessary packages and dependencies
from flask import Flask, jsonify
import redis
import requests
import threading
import time

# initialize Flask app
app = Flask(__name__)

# connect to Redis database
container_ip_address = "localhost"
redis_db = redis.Redis(host=container_ip_address, port=6379)


# define endpoint to get games from the Second API via the Gateway API
@app.route('/games', methods=['GET'])
def get_games():
    # get remaining TTL of Redis cache
    ttl = redis_db.ttl('games')
    # check if games data is available in Redis cache
    if redis_db.exists('games') and ttl > 0:
        # retrieve games data from Redis cache
        games = eval(redis_db.get('games'))
    else:
        # retrieve games data from the Second API
        games_data = requests.get('http://localhost:8000/db_sync').json()['games']
        # get only the name and price of each game
        games = [{game['name']: game['price']} for game in games_data]
        # cache games data in Redis
        redis_db.set('games', str(games))
        # set a 60-second expiration time for the cache
        redis_db.expire('games', 60)
        # get remaining TTL of Redis cache
        ttl = redis_db.ttl('games')
        # print message to indicate cache has been updated
        print('Redis cache updated.')
    # get remaining TTL of Redis cache
    ttl = redis_db.ttl('games')
    # return retrieved games data and remaining TTL
    return jsonify({'games': games, 'ttl': ttl})

# define endpoint to check the availability and functionality of the Gateway API
@app.route('/status')
def status():
    # check if Redis database is connected
    redis_status = 'Redis database connected.' if redis_db.ping() else 'Redis database not connected.'
    # check if Second API is available
    try:
        response = requests.get('http://localhost:5001/status')
        second_api_status = 'Second API connected.' if response.ok else 'Second API not connected.'
    except requests.exceptions.ConnectionError:
        second_api_status = 'Second API not connected.'
    # return status of both Gateway API and Second API
    return jsonify({'gateway': 'Gateway API connected.', 'redis': redis_status, 'second_api': second_api_status})


# run Flask app if executed as main module
if __name__ == '__main__':
    app.run(debug=True)
