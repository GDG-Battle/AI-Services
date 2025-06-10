# build a flask app with two endpoints:
# 1. for generating qcm or code
# 2. for evaluating user code and providing feedback

from flask import Flask, request, jsonify
from dotenv import load_dotenv
from .agents.eval_exo_agent import evaluate_and_feedback
from .services.generate_code_or_exo import generate_lab
from .agents.router_agent import route_query
import os
load_dotenv()

app = Flask(__name__)

@app.route('/')
def index():
    return "Welcome to the Code and Exercise Generation API!"

# a json to test the API
# {
#     "context": "",
#     "number_of_questions": 5,
#     "user_query": "generative AI QCM",
#     "task": "qcm",
#     "difficulty": "easy"
# }

# {
#     "context": "",
#     "number_of_questions": 0,
#     "user_query": "reverse string",
#     "task": "code",
#     "difficulty": "easy"
# }


@app.route('/generate', methods=['POST'])
def generate_exercise():
    data = request.json
    context = data.get("context", "")
    number_of_questions = data.get("number_of_questions", 1)
    user_query = data.get("user_query", "")
    task = data.get("task", "qcm")
    difficulty = data.get("difficulty", "easy")

    try:
        results = generate_lab(context, number_of_questions, user_query, task, difficulty)
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# Test data for evaluation endpoint
# {
#     "exercise": "Write a function called reverse_string that takes a string as input and returns the reversed string. The function signature is def reverse_string(s: str) -> str:",
#     "user_code": "def reverse_string(s: str) -> str:\n    return s[::-1]",
#     "inputs": [
#         "hello",
#         "world",
#         "python"
#     ],
#     "outputs": [
#         "olleh",
#         "dlrow",
#         "nohtyp"
#     ]
# }

@app.route('/evaluate', methods=['POST'])
def evaluate_exercise():
    data = request.json
    exercise = data.get("exercise", "")
    user_code = data.get("user_code", "")
    inputs = data.get("inputs", [])
    outputs = data.get("outputs", [])

    try:
        results = evaluate_and_feedback(exercise, user_code, inputs, outputs)
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    

# Remove the /mentor and /hint routes
# Add the new unified endpoint:
@app.route('/aiassistant', methods=['POST'])
def ai_assistant():
    data = request.json
    query = data.get("query", "")
    
    if not query:
        return jsonify({"error": "Query is required"}), 400
    
    try:
        result = route_query(query)
        return jsonify({
            "type": result["type"],
            "response": result["response"]
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# run app for production
if __name__ == '__main__':
    app.run( debug=True)