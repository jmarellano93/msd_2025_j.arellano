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
from datetime import datetime, timezone  # Added for date formatting
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
    level=logging.INFO,  # Default level, can be overridden by env
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
    """
    Loads environment-specific configurations from a JSON file.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    default_env_file = 'dev_env.json'
    env_file_name_from_var = os.environ.get('WORKING_ENV')

    # Determine the environment file path, preferring an absolute path if provided.
    if env_file_name_from_var and os.path.isabs(env_file_name_from_var):
        env_file_path = os.path.join(base_dir, env_file_name_from_var)
    else:
        # Fallback to default if the environment variable is not set
        env_file = env_file_name_from_var or default_env_file
        env_file_path = os.path.join(base_dir, env_file)

    module_logger.info(f"Attempting to load environment from: {env_file_path}")
    try:
        with open(env_file_path, 'r', encoding='utf-8') as f:
            env_values = json.load(f)
        module_logger.info(f"Environment variables loaded: {env_values}")
        return env_values
    except FileNotFoundError:
        module_logger.error(f"Environment file '{env_file_path}' not found.", exc_info=True)
        return None
    except json.JSONDecodeError:
        module_logger.error(f"Error decoding JSON from '{env_file_path}'.", exc_info=True)
        return None


env_variables = load_environment()

if env_variables is None:
    module_logger.critical(
        "env_variables is None because load_environment() failed. "
        "Defaulting to an empty dict."
    )
    env_variables = {}

log_level_str = env_variables.get("log_level", "INFO").upper()
numeric_level = getattr(logging, log_level_str, None)
if numeric_level is None:
    module_logger.warning(
        f"Invalid log level '{log_level_str}' in environment. Using INFO."
    )
    numeric_level = logging.INFO
logging.getLogger().setLevel(numeric_level)
module_logger.info(f"Log level set to: {logging.getLevelName(numeric_level)}")

# --- Global Data for /memory endpoint (Example) ---
big_data_list = []


# --- API Endpoints ---

@app.route('/memory', methods=['GET'])
@auth.login_required
@profile
def memory_test():
    module_logger.info(
        f"'{memory_test.__name__}' endpoint called by user: {auth.current_user()}."
    )
    for _ in range(100000):
        big_data_list.append(random.random())
    process = psutil.Process(os.getpid())
    memory_mb = process.memory_info().rss / (1024.0 ** 2)
    response_data = {'size': len(big_data_list), 'memory_MB': round(memory_mb, 2)}
    module_logger.info(
        f"Memory test complete. List size: {response_data['size']}, "
        f"Memory: {response_data['memory_MB']}MB"
    )
    return jsonify(response_data)


@app.route('/', methods=['GET'])
@auth.login_required
def index():
    module_logger.info(f"'{index.__name__}' endpoint called by user: {auth.current_user()}.")
    info = {
        'name': 'John Arellano',
        'mail': 'john.arellano@students.fhnw.ch',
        'System': 'Digital Biomarker Course Project - Data Collection Service',
        'Server_Component_Version': '1.0.0',
        'Date': (
            datetime.now(timezone.utc)
            .isoformat(timespec='microseconds')
            .replace('+00:00', 'Z')
        )
    }
    return jsonify(info)


# --- Patient Management Endpoints ---
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


# --- Experiment Management Endpoints ---
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
def get_all_experiments():
    current_user = auth.current_user()
    module_logger.info(f"'/experiments' GET request by '{current_user}'.")
    ds_instance = datastructure.DataStorage()
    all_experiments_list = ds_instance.get_all_experiments()
    return jsonify([e.__dict__ for e in all_experiments_list]), 200


# --- Patient Data Endpoints ---
@app.route('/patient/<patient_id>/data', methods=['POST', 'GET'])
@auth.login_required
def patient_data_actions(patient_id):
    current_user = auth.current_user()
    ds_instance = datastructure.DataStorage()
    action_name = "patient_data_actions"

    patient = ds_instance.get_patient(patient_id)
    if not patient:
        err_msg = f"Patient with ID '{patient_id}' not found."
        module_logger.warning(
            f"'{action_name}' for patient '{patient_id}' failed: {err_msg}"
        )
        return make_response(jsonify({"error": err_msg}), 404)

    if request.method == 'POST':
        module_logger.info(
            f"'{action_name}' POST for patient '{patient_id}' by '{current_user}'."
        )
        try:
            body = request.get_json()
            if not body:
                return make_response(jsonify({"error": "No JSON body provided"}), 400)

            experiment_id = body.get('experimentId')
            if not experiment_id:
                err_msg = {"error": "Missing 'experimentId' in request body"}
                return make_response(jsonify(err_msg), 400)

            if ds_instance.get_experiment(experiment_id) is None:
                err_msg = f"Experiment with ID '{experiment_id}' not found."
                return make_response(jsonify({"error": err_msg}), 404)

            data_obj = datastructure.DataPoint(patient_id=patient_id,
                                               experiment_id=experiment_id,
                                               data_payload=body)
            ds_instance.add_data(data_obj)

            module_logger.info(
                f"Data point added for patient '{patient_id}', exp '{experiment_id}'. "
                f"DP_ID: {data_obj.id}"
            )
            response_payload = {
                "message": "Data point added successfully for patient.",
                "patientId": patient_id,
                "experimentId": experiment_id,
                "dataPointId": data_obj.id,
                "submitted_data": body
            }
            return make_response(jsonify(response_payload), 201)
        except ValueError as ve:
            module_logger.error(
                f"Validation error in POST /patient/{patient_id}/data: {ve}", exc_info=True
            )
            return make_response(jsonify({"error": str(ve)}), 400)
        except Exception as e:
            module_logger.error(
                f"Error in POST /patient/{patient_id}/data: {e}", exc_info=True
            )
            return make_response(jsonify({"error": "Failed to add data point"}), 500)

    if request.method == 'GET':
        module_logger.info(
            f"'{action_name}' GET for patient '{patient_id}' by '{current_user}'."
        )
        filter_experiment_id = request.args.get('experimentId')
        patient_data_points = ds_instance.get_data_points_for_patient(
            patient_id, filter_experiment_id
        )
        return jsonify([dp.__dict__ for dp in patient_data_points]), 200

    return make_response(jsonify({"error": "Method not allowed"}), 405)


@app.route('/patient/<patient_id>/data/<data_point_id>', methods=['GET', 'PUT', 'DELETE'])
@auth.login_required
def specific_patient_data_point_actions(patient_id, data_point_id):
    current_user = auth.current_user()
    ds_instance = datastructure.DataStorage()

    if not ds_instance.get_patient(patient_id):
        return make_response(jsonify({"error": f"Patient with ID '{patient_id}' not found."}), 404)

    if request.method == 'GET':
        data_point = ds_instance.get_data_point(data_point_id)
        if not data_point or data_point.patient_id != patient_id:
            module_logger.warning(
                f"GET /patient/{patient_id}/data/{data_point_id}: "
                f"Data point not found or patient ID mismatch."
            )
            return make_response(jsonify({"error": "Data point not found"}), 404)
        module_logger.info(
            f"Data point '{data_point_id}' for patient '{patient_id}' "
            f"retrieved by '{current_user}'."
        )
        return jsonify(data_point.__dict__), 200

    if request.method == 'PUT':
        module_logger.info(f"PUT request for data point '{data_point_id}' by '{current_user}'.")
        try:
            body = request.get_json()
            if not body:
                return make_response(jsonify({"error": "No JSON body provided for update"}), 400)

            updated_dp = ds_instance.update_data_point(data_point_id, patient_id, body)
            if not updated_dp:
                module_logger.warning(
                    f"PUT /patient/{patient_id}/data/{data_point_id}: "
                    f"Data point not found or patient ID mismatch."
                )
                err_msg = {"error": "Data point not found or patient ID mismatch"}
                return make_response(jsonify(err_msg), 404)

            module_logger.info(f"Data point '{data_point_id}' updated by '{current_user}'.")
            return jsonify(updated_dp.__dict__), 200
        except ValueError as ve:
            module_logger.error(
                f"Validation error updating data point {data_point_id}: {ve}", exc_info=True
            )
            return make_response(jsonify({"error": str(ve)}), 400)
        except Exception as e:
            module_logger.error(f"Error updating data point {data_point_id}: {e}", exc_info=True)
            return make_response(jsonify({"error": "Failed to update data point"}), 500)

    if request.method == 'DELETE':
        deleted_id = ds_instance.delete_data_point(data_point_id, patient_id)
        if not deleted_id:
            module_logger.warning(
                f"DELETE /patient/{patient_id}/data/{data_point_id}: "
                f"Data point not found or patient ID mismatch."
            )
            return make_response(jsonify({"error": "Data point not found"}), 404)

        module_logger.info(
            f"Data point '{data_point_id}' for patient '{patient_id}' "
            f"deleted by '{current_user}'."
        )
        return jsonify({"message": "Data point deleted successfully", "id": deleted_id}), 200

    return make_response(jsonify({"error": "Method not allowed"}), 405)


# --- Utility/Admin Endpoints ---
@app.route('/store', methods=['POST'])
@auth.login_required
def store_data_route():
    current_user = auth.current_user()
    module_logger.info(f"'{store_data_route.__name__}' POST request by '{current_user}'.")
    ds_instance = datastructure.DataStorage()
    try:
        ds_instance.store_data()
        module_logger.info("Data stored successfully to files.")
        return make_response(jsonify({"message": "Data stored successfully"}), 200)
    except Exception as e:
        module_logger.error(f"Error storing data: {e}", exc_info=True)
        return make_response(jsonify({"error": "Failed to store data"}), 500)


# --- Main Application Execution ---
if __name__ == '__main__':
    module_logger.info("Starting Data Collection Service...")
    assert isinstance(env_variables, dict), "env_variables is not a dictionary."

    data_storage_main_instance = datastructure.DataStorage()
    try:
        data_storage_main_instance.load_data()
        module_logger.info("Initial data loaded from files (if any existed).")
    except Exception as e:
        module_logger.error(f"Error loading initial data: {e}", exc_info=True)

    SERVICE_PORT = 5000
    if env_variables and 'port' in env_variables:
        try:
            SERVICE_PORT = int(env_variables['port'])
        except ValueError:
            module_logger.warning(
                f"Invalid port value '{env_variables['port']}'. Using default {SERVICE_PORT}."
            )

    module_logger.info(f"Service will run on host 0.0.0.0, port {SERVICE_PORT}")
    app.run(host='0.0.0.0', port=SERVICE_PORT, debug=True)
    module_logger.info("Data Collection Service stopped.")