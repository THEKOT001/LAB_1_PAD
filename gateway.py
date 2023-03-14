from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

REDIS_URLS = (["http://localhost:5000/games", "http://localhost:5000/games"], 0)
MONGO_URLS = (["http://localhost:5001/games", "http://localhost:5001/games"], 0)
NEWS_URLS = (["http://localhost:5002/news", "http://localhost:5002/news"], 0)


def round_robin(urls):
    array, index = urls
    index = (index + 1) % len(array)
    print
    urls = (array, index)

    return array[index]


@app.route('/db_sync', methods=['GET'])
def call_db_sync():
    if request.method == 'GET':
        mongo_url = round_robin(MONGO_URLS)
        response = requests.get(mongo_url)
        return response.json(), response.status_code
    return jsonify({'message': f'The method {request.method} is not allowed for the requested URL.'}), 400


@app.route('/api', methods=['GET', 'PUT'])
def call_api():
    if request.method == 'PUT':
        mongo_url = round_robin(MONGO_URLS)
        json_data = request.get_json()
        response = requests.put(mongo_url, json=json_data)
    elif request.method == 'GET':
        redis_url = round_robin(REDIS_URLS)
        response = requests.get(redis_url)
    else:
        return jsonify({'message': f'The method {request.method} is not allowed for the requested URL.'}), 400
    return response.json(), response.status_code


@app.route('/api/rating', methods=['PUT'])
def call_api_rating():
    json_data = request.get_json()
    mongo_url = round_robin(MONGO_URLS)[0] + '/rating'
    response = requests.put(mongo_url, json=json_data)
    return response.json(), 201


@app.route('/api/news', methods=['GET', 'PUT'])
def call_news_api():
    if request.method == 'PUT':
        news_url = round_robin(NEWS_URLS)
        json_data = request.get_json()
        response = requests.put(news_url, json=json_data)
    elif request.method == 'GET':
        news_url = round_robin(NEWS_URLS)
        response = requests.get(news_url)
    else:
        return jsonify({'message': f'The method {request.method} is not allowed for the requested URL.'}), 400
    return response.json(), response.status_code


@app.route('/api/news/comment', methods=['PUT'])
def call_news_comments():
    json_data = request.get_json()
    news_url = round_robin(NEWS_URLS)[0] + '/comments'
    response = requests.put(news_url, json=json_data)
    return response.json(), 201


@app.route('/api/status', methods=['GET'])
def call_status_api():
    url = round_robin(REDIS_URLS)
    url_news = round_robin(NEWS_URLS)
    response = requests.get(url + '/status')
    news_response = requests.get(url_news + '/status')
    gateway_response = response.json()
    gateway_response['gateway'] = 'gateway active'
    gateway_response.update(news_response.json())
    return gateway_response, response.status_code


if __name__ == '__main__':
    app.run(debug=True, port=8000)
