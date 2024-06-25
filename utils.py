# utils.py

from flask import Request
from werkzeug.datastructures import FileStorage
import os
from typing import Dict, Any

def validate_input(request: Request, schema: Dict[str, Any]) -> Dict[str, Any]:
    validated_data = {}

    # check required fields
    for field in schema['required_fields']:
        if field not in request.form:
            raise ValueError(f"Missing required field: {field}")
        validated_data[field] = request.form[field]

    # check optional fields
    for field, default_value in schema['optional_fields'].items():
        validated_data[field] = request.form.get(field, default_value)

    # check file fields
    for field in schema['file_fields']:
        file = request.files.get(field)
        if not file:
            raise ValueError(f"Missing required file: {field}")
        new_filename = f"{field}-{validated_data['assignment_id']}{os.path.splitext(file.filename)[1]}"
        validated_data[field] = save_file(file, new_filename)

    # check text or file fields
    for field in schema['text_or_file_fields']:
        value = request.files.get(field) or request.form.get(field)
        if not value:
            raise ValueError(f"Missing required field or file: {field}")
        if isinstance(value, FileStorage):
            new_filename = f"{field}-{validated_data['assignment_id']}{os.path.splitext(value.filename)[1]}"
            validated_data[field] = save_file(value, new_filename)
        else:
            validated_data[field] = value

    # convert types as needed
    validated_data['max_completion_tokens'] = int(validated_data['max_completion_tokens'])
    validated_data['temperature'] = float(validated_data['temperature'])

    return validated_data

def save_file(file: FileStorage, new_filename: str) -> str:
    file_path = os.path.join('uploaded_files', new_filename)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    file.save(file_path)
    return file_path