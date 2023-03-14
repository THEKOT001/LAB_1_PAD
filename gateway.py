from flask import Flask, jsonify, redirect, url_for, request
import json
import requests

# initialize Flask app
app = Flask(__name__)

redis_urls = {'list': ["http://localhost:5000/games", "http://localhost:5000/games"], 'current_index': 0}
mongo_urls = {'list': ["http://localhost:5001/games", "http://localhost:5001/games"], 'current_index': 0}
# for testing purposes is now repeating the same address
# add new addresses for round-robin


def round_robin(urls):
    index = urls['current_index']
    array = urls['list']
    index = (index + 1) % len(array)
    urls['current_index'] = index

    return array[index]


@app.route('/db_sync', methods=['GET'])
def call_db_sync():
    if request.method == 'GET':
        mongo_url = round_robin(mongo_urls)
        response = requests.get(mongo_url)
    else:
        # even if we add a method this prevents us from an error
        return jsonify({'message': f'The method {request.method} is not allowed for the requested URL.'}), 400

    # accessing the mongo database from the gateway with put and get data
    return response.json(), response.status_code


@app.route('/api', methods=['GET', 'PUT'])
def call_api():
    if request.method == 'PUT':
        mongo_url = round_robin(mongo_urls)
        json_data = request.get_json()
        response = requests.put(mongo_url, json=json_data)
    elif request.method == 'GET':
        redis_url = round_robin(redis_urls)
        response = requests.get(redis_url)
    else:
        # even if we add a method this prevents us from an error
        return jsonify({'message': f'The method {request.method} is not allowed for the requested URL.'}), 400

    # accessing the mongo database from the gateway with put and get data
    return response.json(), response.status_code


@app.route('/api/rating', methods=['PUT'])
def call_api_api_rating():
    json_data = request.get_json()
    mongo_url = round_robin(mongo_urls)+'/rating'
    response = requests.put(mongo_url, json=json_data)
    return response.json(), 201

# @app.route('/status', methods=['GET'])
# def status():
#     # define endpoint to check the availability and functionality of the Gateway API
#     try:
#         response = requests.get('http://localhost:5000/status')
#         second_api_status = 'Second API connected.' if response.ok else 'Second API not connected.'
#     except requests.exceptions.ConnectionError:
#         second_api_status = 'Second API not connected.'
#     # return status of both Gateway API and Second API
#     return jsonify({'gateway': 'Gateway API connected.', 'redis': redis_status, 'second_api': second_api_status})
#     # check if Redis database is connected
#     # check if Second API is available
#     try:
#         response = requests.get('http://localhost:5001/status')
#         second_api_status = 'Second API connected.' if response.ok else 'Second API not connected.'
#     except requests.exceptions.ConnectionError:
#         second_api_status = 'Second API not connected.'
#     # return status of both Gateway API and Second API
#     return jsonify({'gateway': 'Gateway API connected.', 'redis': redis_status, 'second_api': second_api_status})


# run Flask app if executed as main module
if __name__ == '__main__':
    app.run(debug=True, port=8000)