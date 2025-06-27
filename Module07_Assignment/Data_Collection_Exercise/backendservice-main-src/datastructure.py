"""
Handles in-memory data storage for patients, experiments, and data points.
Includes functionality to persist and load data from JSON files.
Uses a singleton pattern for the DataStorage class.
"""
import json
import os
import logging
from memory_profiler import profile # memory_profiler might not be needed here
                                    # unless specific methods are profiled
import idgenerator

module_logger = logging.getLogger(__name__)

# --- Data Model Classes ---
class Patient:
    """Represents a patient with a name and a unique ID, and other dynamic attributes."""
    def __init__(self, name, patient_id=None, **additional_attributes):
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Patient name cannot be empty.")
        self.name = name
        self.id = (patient_id if patient_id
                   else idgenerator.AlphaNumericIDGenerator().get_id())
        for key, value in additional_attributes.items():
            setattr(self, key, value)
        attrs_for_log = {k: v for k, v in self.__dict__.items()}
        module_logger.debug(f"Patient initialized/updated: {attrs_for_log}")

class PatientEncoder(json.JSONEncoder):
    def default(self, o): # pylint: disable=method-hidden
        if isinstance(o, Patient):
            return o.__dict__
        return super().default(o)

class Experiment:
    """Represents an experiment with a name and a unique ID."""
    def __init__(self, name, experiment_id=None, **additional_attributes):
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Experiment name cannot be empty.")
        self.name = name
        self.id = (experiment_id if experiment_id
                   else idgenerator.AlphaNumericIDGenerator().get_id())
        for key, value in additional_attributes.items():
            setattr(self, key, value)
        module_logger.debug(f"Experiment initialized: ID '{self.id}', Name '{self.name}'")

class ExperimentEncoder(json.JSONEncoder):
    def default(self, o): # pylint: disable=method-hidden
        if isinstance(o, Experiment):
            return o.__dict__
        return super().default(o)

class DataPoint:
    """Represents a data point collected for a patient in an experiment."""
    def __init__(self,
                 patient_id,
                 experiment_id,
                 data_payload,  # This will now be the individual data object from the app
                 data_point_id=None):
        if (not patient_id or
                not experiment_id or
                not isinstance(data_payload, dict)):
            raise ValueError(
                "Invalid parameters for DataPoint: patient_id, experiment_id, "
                "and data_payload (dict) are required."
            )
        self.id = (data_point_id if data_point_id
                   else idgenerator.AlphaNumericIDGenerator().get_id())
        self.patient_id = patient_id
        self.experiment_id = experiment_id
        # The entire data_payload from the app is stored in the 'data' field.
        # This preserves the full structure sent by the client.
        self.data = data_payload
        module_logger.debug(
            f"DataPoint initialized: ID '{self.id}' for Patient '{patient_id}', "
            f"Exp '{experiment_id}'"
        )

class DataPointEncoder(json.JSONEncoder):
    def default(self, o): # pylint: disable=method-hidden
        if isinstance(o, DataPoint):
            return o.__dict__
        return super().default(o)

# --- Data Storage Singleton ---
class DataStorage:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            module_logger.info("Creating new DataStorage instance.")
            cls._instance = super().__new__(cls)
            cls._instance.experiments = {}
            cls._instance.patients = {}
            cls._instance.data_points = {}
        return cls._instance

    def __init__(self):
        # The actual initialization of attributes (patients, experiments, data_points)
        # should happen in __new__ to ensure it's done only once.
        # __init__ will be called every time DataStorage() is invoked,
        # but self.patients etc. will refer to the same dicts due to the singleton __new__.
        module_logger.debug("DataStorage __init__ called.")

    def add_patient(self, patient_obj: Patient):
        if patient_obj.id in self.patients:
            module_logger.warning(
                f"Attempted to add patient with duplicate ID '{patient_obj.id}'."
            )
            # Or raise an error: raise ValueError(f"Duplicate patient ID '{patient_obj.id}'.")
            return
        self.patients[patient_obj.id] = patient_obj
        module_logger.info(
            f"Patient added: ID '{patient_obj.id}', Name '{patient_obj.name}'"
        )

    def get_patient(self, patient_id: str) -> Patient | None:
        patient = self.patients.get(patient_id)
        status = 'retrieved' if patient else 'not found'
        module_logger.debug(f"Patient {status}: ID '{patient_id}'")
        return patient

    def get_all_patients(self) -> list[Patient]:
        """Returns a list of all patient objects."""
        all_p = list(self.patients.values())
        module_logger.debug(f"Retrieved all {len(all_p)} patients.")
        return all_p

    def update_patient(self, patient_id: str, update_data: dict) -> Patient | None:
        """Updates an existing patient's attributes."""
        patient = self.get_patient(patient_id)
        if not patient:
            module_logger.warning(
                f"Update failed: Patient with ID '{patient_id}' not found."
            )
            return None

        for key, value in update_data.items():
            if key == 'id':
                module_logger.warning(
                    f"Attempt to update patient 'id' (to '{value}') "
                    f"for patient '{patient_id}' was ignored."
                )
                continue # Do not allow changing the ID
            if hasattr(patient, key):
                setattr(patient, key, value)
                module_logger.debug(
                    f"Patient '{patient_id}': Attribute '{key}' updated to '{value}'."
                )
            else:
                # Optionally handle new attributes or log a warning
                setattr(patient, key, value) # Allow adding new attributes
                module_logger.debug(
                    f"Patient '{patient_id}': New attribute '{key}' "
                    f"added with value '{value}'."
                )

        # Validate critical fields like name after update if necessary
        if not isinstance(patient.name, str) or not patient.name.strip():
            module_logger.error(
                f"Patient update for ID '{patient_id}' resulted in an invalid name: "
                f"'{patient.name}'. Reverting name or handling error."
            )
            # This part would need robust error handling, potentially reverting the change
            # or raising a specific error. For now, we assume app.py's validation or
            # API contract prevents this, or the user accepts dynamic attributes.
            # If name becomes invalid, the object might be in an inconsistent state.
            # A simple approach for now: raise ValueError for critical fields.
            raise ValueError(
                f"Patient name cannot be empty after update for patient ID '{patient_id}'."
            )

        module_logger.info(f"Patient '{patient_id}' updated successfully.")
        return patient


    def delete_patient(self, patient_id: str) -> str | None:
        """
        Deletes a patient and their associated data points.
        Returns patient_id if successful, None otherwise.
        """
        if patient_id in self.patients:
            del self.patients[patient_id]
            ids_to_delete = [
                dp_id for dp_id, dp in self.data_points.items()
                if dp.patient_id == patient_id
            ]
            for dp_id in ids_to_delete:
                del self.data_points[dp_id]
            module_logger.info(
                f"Patient '{patient_id}' and {len(ids_to_delete)} associated "
                f"data points deleted."
            )
            return patient_id
        module_logger.warning(
            f"Attempted to delete non-existent patient '{patient_id}'."
        )
        return None

    def add_experiment(self, exp_obj: Experiment):
        if exp_obj.id in self.experiments:
            module_logger.warning(
                f"Attempted to add experiment with duplicate ID '{exp_obj.id}'."
            )
            # Or raise an error
            return
        self.experiments[exp_obj.id] = exp_obj
        module_logger.info(
            f"Experiment added: ID '{exp_obj.id}', Name '{exp_obj.name}'"
        )

    def get_experiment(self, exp_id: str) -> Experiment | None:
        experiment = self.experiments.get(exp_id)
        status = 'retrieved' if experiment else 'not found'
        module_logger.debug(f"Experiment {status}: ID '{exp_id}'")
        return experiment

    def get_all_experiments(self) -> list[Experiment]:
        """Returns a list of all experiment objects."""
        all_e = list(self.experiments.values())
        module_logger.debug(f"Retrieved all {len(all_e)} experiments.")
        return all_e

    def update_experiment(self, experiment_id: str, update_data: dict) -> Experiment | None:
        """Updates an existing experiment's attributes."""
        experiment = self.get_experiment(experiment_id)
        if not experiment:
            module_logger.warning(
                f"Update failed: Experiment with ID '{experiment_id}' not found."
            )
            return None

        for key, value in update_data.items():
            if key == 'id':
                module_logger.warning(
                    f"Attempt to update experiment 'id' (to '{value}') "
                    f"for experiment '{experiment_id}' was ignored."
                )
                continue # Do not allow changing the ID
            if hasattr(experiment, key):
                setattr(experiment, key, value)
                module_logger.debug(
                    f"Experiment '{experiment_id}': Attribute '{key}' updated to '{value}'."
                )
            else:
                setattr(experiment, key, value) # Allow adding new attributes
                module_logger.debug(
                    f"Experiment '{experiment_id}': New attribute '{key}' "
                    f"added with value '{value}'."
                )

        if not isinstance(experiment.name, str) or not experiment.name.strip():
            module_logger.error(
                f"Experiment update for ID '{experiment_id}' resulted in an invalid name: "
                f"'{experiment.name}'."
            )
            raise ValueError(
                f"Experiment name cannot be empty after update for experiment ID "
                f"'{experiment_id}'."
            )

        module_logger.info(f"Experiment '{experiment_id}' updated successfully.")
        return experiment

    def delete_experiment(self, exp_id: str) -> str | None:
        """
        Deletes an experiment and its associated data points.
        Returns exp_id if successful, None otherwise.
        """
        if exp_id in self.experiments:
            del self.experiments[exp_id]
            ids_to_delete = [
                dp_id for dp_id, dp in self.data_points.items()
                if dp.experiment_id == exp_id
            ]
            for dp_id in ids_to_delete:
                del self.data_points[dp_id]
            module_logger.info(
                f"Experiment '{exp_id}' and {len(ids_to_delete)} associated "
                f"data points deleted."
            )
            return exp_id
        module_logger.warning(
            f"Attempted to delete non-existent experiment '{exp_id}'."
        )
        return None

    def add_data(self, data_point_obj: DataPoint):
        if data_point_obj.id in self.data_points:
            module_logger.warning(
                f"Attempted to add data point with duplicate ID '{data_point_obj.id}'."
            )
            # Or raise an error
            return
        # Basic validation that referenced patient and experiment exist
        if data_point_obj.patient_id not in self.patients:
            module_logger.error(
                f"Cannot add data point: Patient ID '{data_point_obj.patient_id}' "
                f"does not exist."
            )
            raise ValueError(
                f"Patient ID '{data_point_obj.patient_id}' for data point does not exist."
            )
        if data_point_obj.experiment_id not in self.experiments:
            module_logger.error(
                f"Cannot add data point: Experiment ID "
                f"'{data_point_obj.experiment_id}' does not exist."
            )
            raise ValueError(
                f"Experiment ID '{data_point_obj.experiment_id}' for data point "
                f"does not exist."
            )

        self.data_points[data_point_obj.id] = data_point_obj
        module_logger.info(
            f"DataPoint added: ID '{data_point_obj.id}' for patient "
            f"'{data_point_obj.patient_id}'"
        )

    def get_data_point(self, data_point_id: str) -> DataPoint | None:
        dp = self.data_points.get(data_point_id)
        status = 'retrieved' if dp else 'not found'
        module_logger.debug(f"DataPoint {status}: ID '{data_point_id}'")
        return dp

    def get_data_points_for_patient(
        self, patient_id: str, experiment_id: str = None
    ) -> list:
        results = []
        for dp in self.data_points.values():
            if dp.patient_id == patient_id:
                if experiment_id is None or dp.experiment_id == experiment_id:
                    results.append(dp)
        module_logger.debug(
            f"Retrieved {len(results)} data points for patient '{patient_id}' "
            f"(exp filter: {experiment_id})."
        )
        return results

    def update_data_point(
            self,
            data_point_id: str,
            patient_id_context: str,
            new_data_payload: dict
    ) -> DataPoint | None:
        """
        Updates an existing data point's payload.
        patient_id_context is used for validation against the data point's patient_id.
        """
        dp = self.get_data_point(data_point_id)
        if not dp:
            module_logger.warning(
                f"Update failed: DataPoint with ID '{data_point_id}' not found."
            )
            return None

        if dp.patient_id!= patient_id_context:
            module_logger.warning(
                f"Update failed for DataPoint '{data_point_id}': Mismatch patient context. "
                f"Expected '{dp.patient_id}', got '{patient_id_context}'."
            )
            return None

        # new_data_payload is the entire new 'data' field for the DataPoint
        # It should not contain 'id', 'patient_id', 'experiment_id' meant to change
        # the DataPoint's identity or association.
        # If such fields are present, they should ideally be stripped or validated.
        # For example, app.py passes the whole request body.

        # We only update the 'data' field (payload) of the DataPoint.
        # If experimentId is in new_data_payload and it's different from dp.experiment_id,
        # app.py should handle this logic before calling update_data_point,
        # or this method needs more rules.
        # Current app.py doesn't seem to try to change experimentId via this update.

        # Check if new_data_payload contains fields that shouldn't be changed or are managed
        # elsewhere
        restricted_keys = ['id', 'patient_id', 'experiment_id']
        for key in restricted_keys:
            if key in new_data_payload and getattr(dp, key)!= new_data_payload[key]:
                module_logger.warning(
                    f"DataPoint '{data_point_id}' update: "
                    f"Attempt to change '{key}' via payload ignored."
                )
                # We could raise ValueError or simply not update that field from payload
                # For now, we assume new_data_payload is meant to replace dp.data entirely.

        if not isinstance(new_data_payload, dict):
            raise ValueError("new_data_payload for DataPoint update must be a dictionary.")

        dp.data = new_data_payload # Replace the old data payload with the new one
        module_logger.info(
            f"DataPoint '{data_point_id}' (Patient: '{dp.patient_id}') "
            f"data payload updated."
        )
        return dp


    def delete_data_point(self, data_point_id: str, patient_id_context: str) -> str | None:
        """
        Deletes a data point. Validates patient_id_context.
        Returns data_point_id if successful, None otherwise.
        """
        dp = self.get_data_point(data_point_id)
        if not dp:
            module_logger.warning(
                f"Delete failed: DataPoint ID '{data_point_id}' not found."
            )
            return None

        if dp.patient_id!= patient_id_context:
            module_logger.warning(
                f"Delete failed for DataPoint '{data_point_id}': Mismatch patient context. "
                f"Expected '{dp.patient_id}', got '{patient_id_context}'."
            )
            return None

        del self.data_points[data_point_id]
        module_logger.info(
            f"DataPoint '{data_point_id}' for patient '{patient_id_context}' deleted."
        )
        return data_point_id

    #@profile # remove if memory_profiler is not used or needed for this method
    def store_data(self):
        module_logger.info("Storing data to JSON files...")
        try:
            # Storing dictionaries directly
            with open('patients.json', 'w', encoding='utf-8') as pf:
                json.dump(self.patients, pf, cls=PatientEncoder, indent=4)
            module_logger.info(f"{len(self.patients)} patients stored.")

            with open('experiments.json', 'w', encoding='utf-8') as ef:
                json.dump(self.experiments, ef, cls=ExperimentEncoder, indent=4)
            module_logger.info(f"{len(self.experiments)} experiments stored.")

            with open('data.json', 'w', encoding='utf-8') as df:
                json.dump(self.data_points, df, cls=DataPointEncoder, indent=4)
            module_logger.info(f"{len(self.data_points)} data points stored.")
        except IOError as e:
            module_logger.error(f"IOError during data storage: {e}", exc_info=True)
            raise # Re-raise to allow app.py to handle and return 500
        except Exception as e:
            module_logger.error(
                f"Unexpected error during data storage: {e}", exc_info=True
            )
            raise # Re-raise

    def load_data(self):
        module_logger.info("Attempting to load data from JSON files...")
        patient_file = 'patients.json'
        if os.path.exists(patient_file):
            try:
                with open(patient_file, 'r', encoding='utf-8') as file:
                    patient_data_dict = json.load(file)
                for pid, p_details in patient_data_dict.items():
                    name = p_details.pop('name', 'Unknown')
                    self.patients[pid] = Patient(name=name, patient_id=pid, **p_details)
                module_logger.info(f"{len(self.patients)} patients loaded.")
            except Exception as e:
                module_logger.error(
                    f"Error loading or parsing {patient_file}: {e}", exc_info=True
                )
                self.patients.clear()
        else:
            module_logger.info(f"{patient_file} not found. No patients loaded.")

        experiment_file = 'experiments.json'
        if os.path.exists(experiment_file):
            try:
                with open(experiment_file, 'r', encoding='utf-8') as file:
                    exp_data_dict = json.load(file)
                for eid, e_details in exp_data_dict.items():
                    name = e_details.pop('name', 'Unknown Experiment')
                    self.experiments[eid] = Experiment(
                        name=name, experiment_id=eid, **e_details
                    )
                module_logger.info(f"{len(self.experiments)} experiments loaded.")
            except Exception as e:
                module_logger.error(
                    f"Error loading or parsing {experiment_file}: {e}", exc_info=True
                )
                self.experiments.clear()
        else:
            module_logger.info(f"{experiment_file} not found. No experiments loaded.")

        data_points_file = 'data.json'
        if os.path.exists(data_points_file):
            try:
                with open(data_points_file, 'r', encoding='utf-8') as file:
                    dp_data_raw = json.load(file)

                if isinstance(dp_data_raw, list):
                    for dp_details in dp_data_raw:
                        dp_id = dp_details.get('id') or idgenerator.AlphaNumericIDGenerator().get_id()
                        pat_id = dp_details.get('patient_id')
                        exp_id = dp_details.get('experiment_id')
                        payload = dp_details.get('data')

                        if pat_id and exp_id and isinstance(payload, dict):
                            if pat_id not in self.patients:
                                module_logger.warning(
                                    f"Skipping data point (ID: {dp_id}): "
                                    f"Associated patient ID '{pat_id}' not found."
                                )
                                continue
                            if exp_id not in self.experiments:
                                module_logger.warning(
                                    f"Skipping data point (ID: {dp_id}): "
                                    f"Associated experiment ID '{exp_id}' not found."
                                )
                                continue

                            self.data_points[dp_id] = DataPoint(
                                patient_id=pat_id,
                                experiment_id=exp_id,
                                data_payload=payload,
                                data_point_id=dp_id
                            )
                        else:
                            module_logger.warning(
                                f"Skipping invalid data point entry (ID: {dp_id}): "
                                f"Missing required fields or invalid payload type in "
                                f"{data_points_file}"
                            )
                elif isinstance(dp_data_raw, dict):
                    for dp_id, dp_details in dp_data_raw.items():
                        pat_id = dp_details.get('patient_id')
                        exp_id = dp_details.get('experiment_id')
                        payload = dp_details.get('data')

                        if pat_id and exp_id and isinstance(payload, dict):
                            if pat_id not in self.patients:
                                module_logger.warning(
                                    f"Skipping data point (ID: {dp_id}): "
                                    f"Associated patient ID '{pat_id}' not found."
                                )
                                continue
                            if exp_id not in self.experiments:
                                module_logger.warning(
                                    f"Skipping data point (ID: {dp_id}): "
                                    f"Associated experiment ID '{exp_id}' not found."
                                )
                                continue

                            self.data_points[dp_id] = DataPoint(
                                patient_id=pat_id,
                                experiment_id=exp_id,
                                data_payload=payload,
                                data_point_id=dp_id
                            )
                        else:
                            module_logger.warning(
                                f"Skipping invalid data point entry (ID: {dp_id}): "
                                f"Missing required fields or invalid payload type in "
                                f"{data_points_file}"
                            )
                else:
                    module_logger.warning(f"Unexpected data format in {data_points_file}. Expected dict or list.")

                module_logger.info(f"{len(self.data_points)} data points loaded.")
            except Exception as e:
                module_logger.error(
                    f"Error loading or parsing {data_points_file}: {e}", exc_info=True
                )
                self.data_points.clear()
        else:
            module_logger.info(f"{data_points_file} not found. No data points loaded.")
