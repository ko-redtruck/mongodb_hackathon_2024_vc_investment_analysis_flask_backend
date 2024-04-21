from flask import Flask, request, jsonify, json
from flask import render_template
from pymongo import MongoClient
import numpy as np
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

ATLAS_URI = "mongodb+srv://kettererkonstantin:7GNfXDPi9Z5SpOyP@hackathon0.1wyzy.mongodb.net/?retryWrites=true&w=majority&appName=hackathon0"

atlas_client = MongoClient(ATLAS_URI)

from openai import OpenAI

client = OpenAI(
    api_key="hack-with-upstage-solar-0420",
    base_url="https://api.upstage.ai/v1/solar"
)
# define pipeline

def get_search_pipeline(vector):
    pipeline = [
    {
        '$vectorSearch': {

        'index': 'embeddings_vector_search', 

        'path': 'embeddings', 

            'queryVector': vector,
        'numCandidates': 150, 

        'limit': 10

        }

    }

    ]
    return pipeline





@app.route("/")
def hello_world():
    return render_template("index.html")

import random
@app.route("/analyse_startup", methods=["POST"])
def analyse_starup():
    content = request.json
    print(request.get_json())
    print(content)
    if "description" not in content:
        response = jsonify([])
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response
    
    document_result = client.embeddings.create(
        model = "solar-1-mini-embedding-passage",
        input = content["description"] 
    )

    embedding = document_result.data[0].embedding

    search_pipeline = get_search_pipeline(embedding)
    result = atlas_client["HACKATHON"]["HACKATHON"].aggregate(search_pipeline)

    results = [{
        "company": x["Organization Name"],
        "website": x["Organization Name URL"],
        "description": x["Full Description"],
        "industries": [i.strip() for i in x["Industries"].split(",")],
        "similarity": random.randint(1, 100),
        "totalFunding": x["Total Funding Amount Currency (in USD)"]
    } for x in result]

    results_dict = {result["company"]: result for result in results}
    response = jsonify(json.loads(json.htmlsafe_dumps(list(results_dict.values()))))
    response.headers.add("Access-Control-Allow-Origin", "*")

    print(response.headers)
    return response

