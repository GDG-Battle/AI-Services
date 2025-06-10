# build a flask app with two endpoints:
# 1. for generating qcm or code
# 2. for evaluating user code and providing feedback

from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from .agents.eval_exo_agent import evaluate_and_feedback
from .services.generate_code_or_exo import generate_lab
from .agents.router_agent import route_query
from .services.documents_pipeline import add_new_documents
from .utils.file_helpers import allowed_file, save_uploaded_files
import os
import time
load_dotenv()

app = Flask(__name__)

# File upload configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'uploads')
PROCESSED_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'extracted_data')

# Create upload folders if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 30 * 1024 * 1024  # 30MB max-limit

# set up langsmith tracing for all the invocations

if 'LANGSMITH_API_KEY' in os.environ:
    os.environ['LANGSMITH_PROJECT'] = os.getenv('LANGSMITH_PROJECT', 'code-exercise-generation')
    os.environ['LANGSMITH_API_KEY'] = os.getenv('LANGSMITH_API_KEY', 'your-api-key')
    os.environ['LANGSMITH_TRACING_V2'] = os.getenv('LANGSMITH_TRACING_V2', 'true')


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

@app.route('/process-documents', methods=['POST'])
def process_documents():
    if 'files' not in request.files:
        return jsonify({"error": "No files provided"}), 400
        
    files = request.files.getlist('files')
    if not files or all(file.filename == '' for file in files):
        return jsonify({"error": "No selected files"}), 400

    try:
        start_time = time.time()
        
        # Save uploaded files using imported helper
        saved_files = save_uploaded_files(files, app.config['UPLOAD_FOLDER'])
        if not saved_files:
            return jsonify({"error": "No valid files uploaded"}), 400

        # Process the documents
        results = add_new_documents(
            input_files=saved_files,
            output_dir=PROCESSED_FOLDER
        )

        # Clean up uploaded files
        for filepath in saved_files:
            try:
                os.remove(filepath)
            except Exception as e:
                print(f"Error removing temporary file {filepath}: {e}")

        # Add total processing time
        total_time = time.time() - start_time
        
        return jsonify({
            "message": "Documents processed successfully",
            "results": results,
            "total_processing_time_seconds": round(total_time, 2)
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# run app for production
if __name__ == '__main__':
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 8000))
    app.run(host=HOST, port=PORT)