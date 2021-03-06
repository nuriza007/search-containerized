import boto3
import json
import requests
from requests_aws4auth import AWS4Auth
from flask import Flask, request
from flask_cors import CORS

app = Flask(__name__)


CORS(app, resources={r"*": {"origins": "*"}})
region = 'us-east-1'
service = 'es'
credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)

host = 'https://search-search-6havcvqeo64r5nzeemtdi6bgym.us-east-1.es.amazonaws.com'
index = 'movies'
url = host + '/' + index + '/_search?'

# Lambda execution starts here
@app.route('/', methods=['GET'])
def search():
    args = request.args.get('q')
    # Put the user query into the query DSL for more accurate search results.
    # Note that certain fields are boosted (^).
    print(args)
    query = {
        "size": 25,
        "query": {
            "multi_match": {
                "query": args,
                "fields": ["title^4", "plot^2", "actors", "directors"]
            }
        }
    }

    # Elasticsearch 6.x requires an explicit Content-Type header
    headers = { "Content-Type": "application/json" }

    # Make the signed HTTP request
    r = requests.get(url, auth=awsauth, headers=headers, data=json.dumps(query))

    # Create the response and add some extra content to support CORS
    response = {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": '*'
        },
        "isBase64Encoded": False
    }

    # Add the search results to the response
    response['body'] = r.text
    print(response)
    return response