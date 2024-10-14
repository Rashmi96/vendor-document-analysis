import os
from flask import request, jsonify, Blueprint, send_from_directory, abort

from app import Config
from app.services.text_extractor import extract_text
from app.utils.validators import allowed_file
from app.utils.loggers import log_message
from flask_restful import Api, Resource
from app.services.text_extractor import extract
from app.services.llm_processor import extract_fields_with_llm

main = Blueprint('main', __name__)
api = Api(main)
os.environ['WERKZEUG_DEBUG_PIN'] = 'off'


@main.route('/ping', methods=['GET'])
def get_health():
    log_message("Checking the app health")
    response_data = {'project': 'You are into Vendor Document Analysis project'}
    return response_data, 200

@main.route('/execute-prompt', methods=['GET'])
def execute_prompt():
    log_message("executing the prompt")
    extract_fields_with_llm()
    return 200


@main.route('/extract', methods=['GET'])
def extract_file():
    try:
        return extract()
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@main.route('/list-files', methods=['GET'])
def list_files():
    # Map known directory paths to actual folder paths
    path_map = {
        "uploads": Config.UPLOAD_FOLDER,
        "downloads": Config.DOWNLOAD_FOLDER
    }

    # Get the directory path from the query parameter
    dir_path = request.args.get('dir_path')

    if not dir_path:
        return jsonify({'error': 'No directory path provided'}), 400

    # Fetch the actual path using the dir_path provided, or return 404 if not valid
    path = path_map.get(dir_path)

    if not path:
        return jsonify({'error': 'Invalid directory path'}), 404

    # Check if the directory exists
    if not os.path.isdir(path):
        return jsonify({'error': 'Directory not found'}), 404

    try:
        # List files efficiently using generator expression
        files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
        return jsonify({'files': files}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


class UploadDocument(Resource):
    def post(self):
        if 'files' not in request.files:
            log_message("No file part in the request", "error")
            return {'error': 'No files part'}, 400
        print(request.form)
        print(request.files)

        files = request.files.getlist('files')
        uploaded_files = []
        try:
            for file in files:
                if allowed_file(file.filename):
                    file_path = os.path.join(Config.UPLOAD_FOLDER, file.filename)
                    file.save(file_path)
                    uploaded_files.append(file_path)
                    response_data = {"message": "File uploaded successfully!"}
                    return response_data, 200
                else:
                    log_message("Unsupported file type", "error")
                    return {"error": "Unsupported file type"}, 400
        except Exception as e:
            log_message(f"Error during extraction: {str(e)}", "error")
            return {"error": "File processing failed"}, 500


class ReportDownload(Resource):
    def get(self, filename):
        try:
            file_path = os.path.join(Config.DOWNLOAD_FOLDER, filename)
            if not os.path.isfile(file_path):
                log_message(f"File not found: {file_path}", "error")
                abort(404)
            return send_from_directory(Config.DOWNLOAD_FOLDER, filename, as_attachment=True)
        except Exception as e:
            log_message(f"Error during extraction: {str(e)}", "error")
            raise e


api.add_resource(UploadDocument, '/uploadDocument')
api.add_resource(ReportDownload, '/reportDownload/<string:filename>')
