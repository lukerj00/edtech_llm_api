# app.py

import os
from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
from openai_handler import OpenAIHandler
from anthropic_handler import AnthropicHandler
from utils import validate_input

load_dotenv()  # load env vars from .env file

app = Flask(__name__)

# API schema
API_SCHEMA = {
    'required_fields': ['assignment_id', 'assignment_title', 'question_id', 'question_title', 'subject', 'qualification'],
    'optional_fields': {
        'model': 'openai',
        'max_completion_tokens': 1000,
        'temperature': 1 # 0.0001
    },
    'file_fields': ['mark_scheme'],
    'text_or_file_fields': ['submission']
}

# set up rate limiting
limiter = Limiter(
    get_remote_address,
    app=app,
    # default_limits=["200 per day", "50 per hour"]
)

openai_handler = OpenAIHandler()
anthropic_handler = AnthropicHandler()

@app.route('/api/feedback', methods=['POST'])
@limiter.limit("10 per minute")
def handle_feedback_request():
    try:
        # validate input data
        data = validate_input(request, API_SCHEMA)

        # choose the appropriate handler based on the 'model' field
        if data['model'].lower() == 'anthropic':
            handler = anthropic_handler
        else:
            handler = openai_handler
        
        # generate feedback
        feedback = handler.generate_feedback(
            assignment_id=data['assignment_id'],
            assignment_title=data['assignment_title'],
            question_id=data['question_id'],
            question_title=data['question_title'],
            subject=data['subject'],
            qualification=data['qualification'],
            submission=data['submission'],
            mark_scheme=data['mark_scheme'],
            max_completion_tokens=data['max_completion_tokens'],
            temperature=data['temperature']
        )
        
        # format feedback as JSON
        return jsonify(feedback), 200
    
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        app.logger.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": "An unexpected error occurred"}), 500

if __name__ == '__main__':
    app.config['DEBUG'] = False
    # app.config['PROPAGATE_EXCEPTIONS'] = True
    app.run(port=int(os.getenv('PORT', 5000))) #, debug=os.getenv('DEBUG', 'True').lower() == 'true')