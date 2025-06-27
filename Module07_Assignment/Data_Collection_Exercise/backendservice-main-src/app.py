# File: app.py
"""
Main Flask application for the Data Collection Service.

This service provides API endpoints to manage patients, experiments,
and associated data points. It includes basic authentication,
logging, and data persistence to JSON files.
"""
import json
import os
import random
import logging
from datetime import datetime, timezone
from flask import request, Flask, jsonify, make_response
from flask_httpauth import HTTPBasicAuth
import psutil
from memory_profiler import profile

import datastructure

# Initialize Flask app
app = Flask(__name__)
auth = HTTPBasicAuth()

# Configure logging
logging.basicConfig(
    filename="backend_service.log",
    encoding='utf-8',
    level=logging.INFO,
    format=('%(asctime)s - %(levelname)s - %(name)s - '
            '%(threadName)s : %(message)s')
)
module_logger = logging.getLogger(__name__)

# --- Authentication ---
users = {
    "user": "password"  # Simple user store for basic auth
}


@auth.verify_password
def verify_password(username, password):
    """Verifies username and password for Basic Auth."""
    if username in users and users[username] == password:
        module_logger.info(f"User '{username}' authenticated successfully.")
        return username
    module_logger.warning(f"Authentication failed for user '{username}'.")
    return None


# --- Environment Loading ---
def load_environment():
    """Loads environment-specific configurations from a JSON file."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    default_env_file = 'dev_env.json'
    env_file_name_from_var = os.environ.get('WORKING_ENV')

    if env_file_name_from_var and os.path.isabs(env_file_name_from_var):
        env_file_path = os.path.join(base_dir, env_file_name_from_var)
    else:
        env_file = env_file_name_from_var or default_env_file
        env_file_path = os.path.join(base_dir, env_file)

    module_logger.info(f"Attempting to load environment from: {env_file_path}")
    try:
        with open(env_file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        module_logger.error(f"Failed to load environment from {env_file_path}: {e}", exc_info=True)
        return None


env_variables = load_environment() or {}

log_level_str = env_variables.get("log_level", "INFO").upper()
numeric_level = getattr(logging, log_level_str, logging.INFO)
logging.getLogger().setLevel(numeric_level)
module_logger.info(f"Log level set to: {logging.getLevelName(numeric_level)}")


# --- API Endpoints ---

@app.route('/', methods=['GET'])
@auth.login_required
def index():
    """Provides basic information about the service."""
    module_logger.info(f"'{index.__name__}' endpoint called by user: {auth.current_user()}.")
    info = {
        'name': 'John Arellano',
        'mail': 'john.arellano@students.fhnw.ch',
        'System': 'Digital Biomarker Course Project - Data Collection Service',
        'Server_Component_Version': '1.0.3',  # Incremented version
        'Date': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    }
    return jsonify(info)


# --- Patient Management (Placeholders) ---
@app.route('/patient', methods=['POST'])
@auth.login_required
def create_patient():
    current_user = auth.current_user()
    ds_instance = datastructure.DataStorage()
    module_logger.info(f"'create_patient' POST request by '{current_user}'.")
    try:
        body = request.get_json()
        if not body:
            err_msg = {"error": "Request body is missing or not JSON"}
            return make_response(jsonify(err_msg), 400)
        if 'name' not in body:
            module_logger.warning("Patient creation failed: 'name' missing in request body.")
            err_msg = {"error": "Missing 'name' in request body"}
            return make_response(jsonify(err_msg), 400)

        attributes_for_patient = body.copy()
        name_from_attrs = attributes_for_patient.pop('name')

        patient_obj = datastructure.Patient(name=name_from_attrs, **attributes_for_patient)
        ds_instance.add_patient(patient_obj)

        response_data = patient_obj.__dict__.copy()
        response_data["message"] = "Patient created successfully"

        log_attrs = {k: v for k, v in patient_obj.__dict__.items() if k not in ['id', 'name']}
        module_logger.info(
            f"Patient '{patient_obj.name}' (ID: {patient_obj.id}) created "
            f"by '{current_user}'. Attributes: {log_attrs}"
        )
        return jsonify(response_data), 201
    except ValueError as ve:
        module_logger.error(f"Validation error creating patient: {ve}", exc_info=True)
        return make_response(jsonify({"error": str(ve)}), 400)
    except Exception as e:
        module_logger.error(f"Error creating patient: {e}", exc_info=True)
        return make_response(jsonify({"error": "Failed to create patient"}), 500)

@app.route('/patient/<patient_id>', methods=['GET', 'PUT', 'DELETE'])
@auth.login_required
def specific_patient_actions(patient_id):
    current_user = auth.current_user()
    ds_instance = datastructure.DataStorage()

    if request.method == 'GET':
        patient = ds_instance.get_patient(patient_id)
        if not patient:
            module_logger.warning(f"GET /patient/{patient_id}: Patient not found.")
            return make_response(jsonify({"error": "Patient not found"}), 404)
        module_logger.info(f"Patient '{patient_id}' retrieved by '{current_user}'.")
        return jsonify(patient.__dict__), 200

    if request.method == 'PUT':
        patient = ds_instance.get_patient(patient_id)  # Get patient first to update
        if not patient:
            module_logger.warning(f"PUT /patient/{patient_id}: Patient not found.")
            return make_response(jsonify({"error": "Patient not found"}), 404)
        module_logger.info(f"PUT request for patient '{patient_id}' by '{current_user}'.")
        try:
            body = request.get_json()
            if not body:
                err_msg = {"error": "No JSON body provided for update"}
                return make_response(jsonify(err_msg), 400)

            updated_patient_obj = ds_instance.update_patient(patient_id, body)
            if not updated_patient_obj:
                err_msg = {"error": "Patient not found during update"}
                return make_response(jsonify(err_msg), 404)

            module_logger.info(f"Patient '{patient_id}' updated by '{current_user}'.")
            response_data = updated_patient_obj.__dict__.copy()
            response_data["message"] = "Patient updated successfully"
            return jsonify(response_data), 200
        except ValueError as ve:
            module_logger.error(
                f"Validation error updating patient {patient_id}: {ve}", exc_info=True
            )
            return make_response(jsonify({"error": str(ve)}), 400)
        except Exception as e:
            module_logger.error(f"Error updating patient {patient_id}: {e}", exc_info=True)
            return make_response(jsonify({"error": "Failed to update patient"}), 500)

    if request.method == 'DELETE':
        deleted_id = ds_instance.delete_patient(patient_id)
        if not deleted_id:
            module_logger.warning(f"DELETE /patient/{patient_id}: Patient not found.")
            return make_response(jsonify({"error": "Patient not found"}), 404)

        module_logger.info(f"Patient '{patient_id}' deleted by '{current_user}'.")
        return jsonify({"message": "Patient deleted successfully", "id": deleted_id}), 200

    return make_response(jsonify({"error": "Method not allowed"}), 405)

@app.route('/patients', methods=['GET'])
@auth.login_required
def get_all_patients():
    current_user = auth.current_user()
    module_logger.info(f"'/patients' GET request by '{current_user}'.")
    ds_instance = datastructure.DataStorage()
    all_patients_list = ds_instance.get_all_patients()
    return jsonify([p.__dict__ for p in all_patients_list]), 200

# --- Experiment Management (Placeholders) ---
@app.route('/experiment', methods=['POST'])
@auth.login_required
def create_experiment():
    current_user = auth.current_user()
    ds_instance = datastructure.DataStorage()
    module_logger.info(f"'create_experiment' POST request by '{current_user}'.")
    try:
        body = request.get_json()
        if not body or 'name' not in body:
            module_logger.warning("Experiment creation failed: 'name' missing.")
            return make_response(jsonify({"error": "Missing 'name' in request body"}), 400)

        name = body['name']
        experiment_obj = datastructure.Experiment(name)
        ds_instance.add_experiment(experiment_obj)
        module_logger.info(
            f"Experiment '{name}' (ID: {experiment_obj.id}) created by '{current_user}'."
        )
        return jsonify(experiment_obj.__dict__), 201
    except ValueError as ve:
        module_logger.error(f"Validation error creating experiment: {ve}", exc_info=True)
        return make_response(jsonify({"error": str(ve)}), 400)
    except Exception as e:
        module_logger.error(f"Error creating experiment: {e}", exc_info=True)
        return make_response(jsonify({"error": "Failed to create experiment"}), 500)

@app.route('/experiment/<experiment_id>', methods=['GET', 'PUT', 'DELETE'])
@auth.login_required
def specific_experiment_actions(experiment_id):
    current_user = auth.current_user()
    ds_instance = datastructure.DataStorage()

    if request.method == 'GET':
        experiment = ds_instance.get_experiment(experiment_id)
        if not experiment:
            module_logger.warning(f"GET /experiment/{experiment_id}: Experiment not found.")
            return make_response(jsonify({"error": "Experiment not found"}), 404)
        module_logger.info(f"Experiment '{experiment_id}' retrieved by '{current_user}'.")
        return jsonify(experiment.__dict__), 200

    if request.method == 'PUT':
        module_logger.info(
            f"PUT request for experiment '{experiment_id}' by '{current_user}'."
        )
        try:
            body = request.get_json()
            if not body:
                err_msg = {"error": "No JSON body provided for update"}
                return make_response(jsonify(err_msg), 400)

            # Check for updatable fields
            updatable_fields_provided = 'name' in body or any(
                key in body for key in vars(datastructure.Experiment("temp")).keys()
                if key != 'id'
            )
            if not updatable_fields_provided:
                err_msg = {"error": "No updatable fields provided in request body"}
                return make_response(jsonify(err_msg), 400)

            updated_exp = ds_instance.update_experiment(experiment_id, body)
            if not updated_exp:
                module_logger.warning(
                    f"PUT /experiment/{experiment_id}: Experiment not found for update."
                )
                return make_response(jsonify({"error": "Experiment not found"}), 404)

            module_logger.info(f"Experiment '{experiment_id}' updated by '{current_user}'.")
            return jsonify(updated_exp.__dict__), 200
        except ValueError as ve:
            module_logger.error(
                f"Validation error updating experiment {experiment_id}: {ve}", exc_info=True
            )
            return make_response(jsonify({"error": str(ve)}), 400)
        except Exception as e:
            module_logger.error(
                f"Error updating experiment {experiment_id}: {e}", exc_info=True
            )
            return make_response(jsonify({"error": "Failed to update experiment"}), 500)

    if request.method == 'DELETE':
        deleted_id = ds_instance.delete_experiment(experiment_id)
        if not deleted_id:
            module_logger.warning(f"DELETE /experiment/{experiment_id}: Experiment not found.")
            return make_response(jsonify({"error": "Experiment not found"}), 404)

        module_logger.info(f"Experiment '{experiment_id}' deleted by '{current_user}'.")
        return jsonify({"message": "Experiment deleted successfully", "id": deleted_id}), 200

    return make_response(jsonify({"error": "Method not allowed"}), 405)

@app.route('/experiments', methods=['GET'])
@auth.login_required
@auth.login_required
def get_all_experiments():
    current_user = auth.current_user()
    module_logger.info(f"'/experiments' GET request by '{current_user}'.")
    ds_instance = datastructure.DataStorage()
    all_experiments_list = ds_instance.get_all_experiments()
    return jsonify([e.__dict__ for e in all_experiments_list]), 200

# --- Patient Data Endpoints ---

@app.route('/patient/<patient_id>/data/bulk', methods=['POST'])
@auth.login_required
def patient_data_bulk_upload(patient_id):
    """
    Receives a bulk upload of data points for a patient.
    The request body must be a JSON object: {"experimentId": "...", "data": [...]}.
    """
    current_user = auth.current_user()
    ds_instance = datastructure.DataStorage()
    action_name = "patient_data_bulk_upload"

    module_logger.info(f"'{action_name}' POST for patient '{patient_id}' by '{current_user}'.")

    if not ds_instance.get_patient(patient_id):
        err_msg = f"Patient with ID '{patient_id}' not found."
        module_logger.warning(f"'{action_name}' failed: {err_msg}")
        return make_response(jsonify({"error": err_msg}), 404)

    try:
        body = request.get_json()
        if not body:
            return make_response(jsonify({"error": "Request body is missing or not JSON"}), 400)

        experiment_id = body.get('experimentId')
        data_array = body.get('data')

        if not experiment_id:
            return make_response(jsonify({"error": "Missing 'experimentId' in request body"}), 400)
        if not isinstance(data_array, list):
            return make_response(jsonify({"error": "Missing or invalid 'data' array in request body"}), 400)

        if ds_instance.get_experiment(experiment_id) is None:
            module_logger.info(f"Experiment '{experiment_id}' not found. Creating it.")
            new_exp = datastructure.Experiment(name=f"Experiment {experiment_id}", experiment_id=experiment_id)
            ds_instance.add_experiment(new_exp)

        created_dp_ids = []
        for item in data_array:
            if not isinstance(item, dict):
                module_logger.warning(f"Skipping non-dictionary item in bulk upload for patient {patient_id}.")
                continue

            data_obj = datastructure.DataPoint(patient_id=patient_id,
                                               experiment_id=experiment_id,
                                               data_payload=item)
            ds_instance.add_data(data_obj)
            created_dp_ids.append(data_obj.id)

        module_logger.info(
            f"Bulk data processed for patient '{patient_id}', exp '{experiment_id}'. "
            f"Added {len(created_dp_ids)} data points."
        )

        ds_instance.store_data()

        response_payload = {
            "message": f"Bulk data received and stored for {len(created_dp_ids)} data points.",
            "patientId": patient_id,
            "experimentId": experiment_id,
            "dataPointIds": created_dp_ids
        }
        return make_response(jsonify(response_payload), 201)

    except ValueError as ve:
        module_logger.error(f"Validation error in {action_name}: {ve}", exc_info=True)
        return make_response(jsonify({"error": str(ve)}), 400)
    except Exception as e:
        module_logger.error(f"Error in {action_name}: {e}", exc_info=True)
        return make_response(jsonify({"error": "Failed to process bulk data"}), 500)


@app.route('/patient/<patient_id>/data', methods=['GET'])
@auth.login_required
def get_patient_data(patient_id):
    """
    Retrieves all data points for a specific patient.
    Can be filtered by experimentId.
    """
    current_user = auth.current_user()
    ds_instance = datastructure.DataStorage()

    # Check if patient exists
    if not ds_instance.get_patient(patient_id):
        return make_response(jsonify({"error": f"Patient with ID '{patient_id}' not found."}), 404)

    module_logger.info(f"GET request for data of patient '{patient_id}' by '{current_user}'.")

    # Check for optional experimentId filter in query parameters
    filter_experiment_id = request.args.get('experimentId')

    patient_data_points = ds_instance.get_data_points_for_patient(
        patient_id, filter_experiment_id
    )

    # Convert the list of DataPoint objects to a list of dictionaries for JSON serialization
    response_data = [dp.__dict__ for dp in patient_data_points]

    return jsonify(response_data), 200

# --- Main Application Execution ---
if __name__ == '__main__':
    module_logger.info("Starting Data Collection Service...")

    data_storage_main_instance = datastructure.DataStorage()
    try:
        data_storage_main_instance.load_data()
        module_logger.info("Initial data loaded from files (if any existed).")
    except Exception as e:
        module_logger.error(f"Error loading initial data: {e}", exc_info=True)

    SERVICE_PORT = env_variables.get('port', 8080)
    try:
        SERVICE_PORT = int(SERVICE_PORT)
    except (ValueError, TypeError):
        module_logger.warning(f"Invalid port '{SERVICE_PORT}'. Using default 8080.")
        SERVICE_PORT = 8080

    # **ADDED**: Explicit print to confirm host and port before starting.
    print(f"--- Preparing to run on http://0.0.0.0:{SERVICE_PORT}/ ---")
    module_logger.info(f"Service will run on host 0.0.0.0, port {SERVICE_PORT}")

    app.run(host='0.0.0.0', port=SERVICE_PORT, debug=True)
    module_logger.info("Data Collection Service stopped.")

