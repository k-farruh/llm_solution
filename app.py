from flask import Flask, request, jsonify, render_template
import json
from llm_service import LLMService
import jwt
from functools import wraps

app = Flask(__name__)

# Define a secret key for JWT token
SECRET_KEY = 'lOtxle2-0K5kCebOXK9Pd7n8_q9QFZ4beTbSkQ7G0HA'

# Define a decorator function to enforce JWT token authentication
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            # Get the JWT token from the request header
            auth_header = request.headers.get('Authorization', '')
            token = auth_header.split(' ')[1]

            # Decode the JWT token
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        except Exception as e:
            # If JWT token is invalid, return an error response
            error = {'message': 'Invalid token'}
            return jsonify(error), 401

        # If JWT token is valid, call the decorated function
        return f(*args, **kwargs)
    return decorated

# Initialize the LLMService object with the configuration
with open('config.json') as f:
    cfg = json.load(f)
    solver = LLMService(cfg)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
@token_required  # Requires authentication for this endpoint
def upload():
    solver.upload_custom_knowledge()
    return jsonify({'message': 'Upload successful'})

@app.route('/query', methods=['POST'])
@token_required  # Requires authentication for this endpoint
def query():
    user_query = request.json['query']
    user_prompt_template = solver.create_user_query_prompt(user_query)
    answer = solver.user_query(user_query)
    return jsonify({'answer': answer})

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False, port=5000)
