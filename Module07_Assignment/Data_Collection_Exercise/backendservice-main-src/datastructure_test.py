"""
Unit tests for the DataStorage class and its associated data model classes.
"""
import unittest
import os
from datastructure import DataStorage, Patient, Experiment, DataPoint

class TestDataStructure(unittest.TestCase):
    """Test suite for the DataStorage class and data models."""

    def setUp(self):
        """Set up for test methods. This method is called before each test."""
        # Get the singleton instance
        self.ds = DataStorage()
        # Clear previous data for test isolation
        self.ds.patients.clear()
        self.ds.experiments.clear()
        self.ds.data_points.clear()

        # Create and add a patient
        self.patient_attributes = {"age": 42, "condition": "stable"}
        self.patient_obj = Patient(name="Jane Doe", **self.patient_attributes)
        self.ds.add_patient(self.patient_obj)
        self.patient_id = self.patient_obj.id

        # Create and add an experiment
        self.experiment_obj = Experiment(name="Vital Signs Study")
        self.ds.add_experiment(self.experiment_obj)
        self.experiment_id = self.experiment_obj.id

    def tearDown(self):
        """Clean up after tests if necessary, e.g., deleting test files."""
        files_to_remove = ['patients.json', 'experiments.json', 'data.json']
        for f_name in files_to_remove:
            if os.path.exists(f_name):
                try:
                    # The os.remove call is commented out for safety. If it were active,
                    # this try/except block would handle potential OS-level errors,
                    # such as permissions issues during file deletion.
                    # os.remove(f_name)
                    pass
                except OSError:
                    # This 'except' block fixes the SyntaxError.
                    # It completes the 'try' statement and handles file errors.
                    pass

    def test_add_and_get_patient(self):
        """Test adding and retrieving a new patient."""
        retrieved_patient = self.ds.get_patient(self.patient_id)
        self.assertIsNotNone(retrieved_patient)
        self.assertEqual(retrieved_patient.name, "Jane Doe")
        self.assertEqual(retrieved_patient.id, self.patient_id)
        self.assertEqual(retrieved_patient.age, 42)
        self.assertEqual(retrieved_patient.condition, "stable")

    def test_get_non_existent_patient(self):
        """Test retrieving a non-existent patient."""
        patient_info = self.ds.get_patient("non_existent_id")
        self.assertIsNone(patient_info)

    def test_get_all_patients(self):
        """Test retrieving all patients."""
        patients = self.ds.get_all_patients()
        self.assertEqual(len(patients), 1)
        self.assertEqual(patients[0].id, self.patient_id)

        # Add another patient
        p2 = Patient(name="John Smith")
        self.ds.add_patient(p2)
        patients = self.ds.get_all_patients()
        self.assertEqual(len(patients), 2)


    def test_update_patient(self):
        """Test updating an existing patient."""
        update_data = {"name": "Jane Smith", "age": 43, "new_field": "added"}
        updated_patient = self.ds.update_patient(self.patient_id, update_data)
        self.assertIsNotNone(updated_patient)
        self.assertEqual(updated_patient.name, "Jane Smith")
        self.assertEqual(updated_patient.age, 43)
        self.assertTrue(hasattr(updated_patient, "new_field"))
        self.assertEqual(updated_patient.new_field, "added")

        # Test updating a non-existent patient
        non_updated_patient = self.ds.update_patient("non_existent_id", update_data)
        self.assertIsNone(non_updated_patient)

    def test_delete_patient(self):
        """Test deleting an existing patient."""
        # Add a data point for this patient to test cascading delete
        dp = DataPoint(patient_id=self.patient_id, experiment_id=self.experiment_id, data_payload={"value":1})
        self.ds.add_data(dp)
        self.assertIsNotNone(self.ds.get_data_point(dp.id))

        deleted_id = self.ds.delete_patient(self.patient_id)
        self.assertEqual(deleted_id, self.patient_id)
        self.assertIsNone(self.ds.get_patient(self.patient_id))
        self.assertIsNone(
            self.ds.get_data_point(dp.id),
            "Data point associated with deleted patient should also be deleted."
        )

        # Test deleting a non-existent patient
        non_deleted_id = self.ds.delete_patient("non_existent_id")
        self.assertIsNone(non_deleted_id)


    def test_add_and_get_experiment(self):
        """Test adding and retrieving an experiment."""
        retrieved_experiment = self.ds.get_experiment(self.experiment_id)
        self.assertIsNotNone(retrieved_experiment)
        self.assertEqual(retrieved_experiment.name, "Vital Signs Study")
        self.assertEqual(retrieved_experiment.id, self.experiment_id)

    def test_get_non_existent_experiment(self):
        """Test retrieving a non-existent experiment."""
        exp_info = self.ds.get_experiment("non_existent_id")
        self.assertIsNone(exp_info)

    def test_get_all_experiments(self):
        """Test retrieving all experiments."""
        experiments = self.ds.get_all_experiments()
        self.assertEqual(len(experiments), 1)
        self.assertEqual(experiments[0].id, self.experiment_id)

         # Add another experiment
        e2 = Experiment(name="Sleep Study")
        self.ds.add_experiment(e2)
        experiments = self.ds.get_all_experiments()
        self.assertEqual(len(experiments), 2)

    def test_update_experiment(self):
        """Test updating an existing experiment."""
        update_data = {"name": "Advanced Vital Signs"}
        updated_exp = self.ds.update_experiment(self.experiment_id, update_data)
        self.assertIsNotNone(updated_exp)
        self.assertEqual(updated_exp.name, "Advanced Vital Signs")

    def test_delete_experiment(self):
        """Test deleting an existing experiment."""
         # Add a data point for this experiment to test cascading delete
        dp = DataPoint(patient_id=self.patient_id, experiment_id=self.experiment_id, data_payload={"value":1})
        self.ds.add_data(dp)
        self.assertIsNotNone(self.ds.get_data_point(dp.id))

        deleted_id = self.ds.delete_experiment(self.experiment_id)
        self.assertEqual(deleted_id, self.experiment_id)
        self.assertIsNone(self.ds.get_experiment(self.experiment_id))
        self.assertIsNone(
            self.ds.get_data_point(dp.id),
            "Data point associated with deleted experiment should also be deleted."
        )

    def test_add_data_point(self):
        """Test adding a data point."""
        data_payload = {"heart_rate": 75, "temperature": 36.6}
        dp = DataPoint(patient_id=self.patient_id,
                       experiment_id=self.experiment_id,
                       data_payload=data_payload)
        self.ds.add_data(dp)
        self.assertIn(dp.id, self.ds.data_points)
        retrieved_dp = self.ds.get_data_point(dp.id)
        self.assertIsNotNone(retrieved_dp)
        self.assertEqual(retrieved_dp.patient_id, self.patient_id)
        self.assertEqual(retrieved_dp.experiment_id, self.experiment_id)
        self.assertEqual(retrieved_dp.data, data_payload)

    def test_add_data_point_for_non_existent_patient_or_experiment(self):
        """Test adding data point for non-existent patient or experiment."""
        with self.assertRaises(ValueError): # Expecting add_data to raise error
            dp_bad_patient = DataPoint(patient_id="non_existent_patient",
                                       experiment_id=self.experiment_id,
                                       data_payload={"hr": 60})
            self.ds.add_data(dp_bad_patient)

        with self.assertRaises(ValueError): # Expecting add_data to raise error
            dp_bad_experiment = DataPoint(patient_id=self.patient_id,
                                          experiment_id="non_existent_experiment",
                                          data_payload={"hr": 60})
            self.ds.add_data(dp_bad_experiment)


    def test_get_data_points_for_patient(self):
        """Test retrieving data points for a patient, with and without experiment filter."""
        dp1_payload = {"hr": 70}
        dp1 = DataPoint(patient_id=self.patient_id, experiment_id=self.experiment_id, data_payload=dp1_payload)
        self.ds.add_data(dp1)

        exp2 = Experiment(name="Metabolic Test")
        self.ds.add_experiment(exp2)
        dp2_payload = {"glucose": 90}
        dp2 = DataPoint(patient_id=self.patient_id, experiment_id=exp2.id, data_payload=dp2_payload)
        self.ds.add_data(dp2)

        # Get all data for patient
        patient_data_points = self.ds.get_data_points_for_patient(self.patient_id)
        self.assertEqual(len(patient_data_points), 2)
        ids_retrieved = {dp.id for dp in patient_data_points}
        self.assertIn(dp1.id, ids_retrieved)
        self.assertIn(dp2.id, ids_retrieved)


        # Get data for patient filtered by specific experiment
        patient_data_filtered = self.ds.get_data_points_for_patient(self.patient_id, self.experiment_id)
        self.assertEqual(len(patient_data_filtered), 1)
        self.assertEqual(patient_data_filtered[0].id, dp1.id)
        self.assertEqual(patient_data_filtered[0].data, dp1_payload)

    def test_get_data_for_patient_with_no_data_points(self):
        """Test retrieving data for a patient who has no data points recorded yet."""
        new_patient = Patient(name="NoData Nelly")
        self.ds.add_patient(new_patient)
        retrieved_data = self.ds.get_data_points_for_patient(new_patient.id)
        self.assertEqual(retrieved_data, [])

    def test_update_data_point(self):
        """Test updating an existing data point."""
        dp = DataPoint(patient_id=self.patient_id,
                       experiment_id=self.experiment_id,
                       data_payload={"value": 100, "unit": "mg/dL"})
        self.ds.add_data(dp)

        new_payload = {"value": 105, "unit": "mg/dL", "notes": "fasting"}
        updated_dp = self.ds.update_data_point(dp.id, self.patient_id, new_payload)
        self.assertIsNotNone(updated_dp)
        self.assertEqual(updated_dp.data["value"], 105)
        self.assertEqual(updated_dp.data["notes"], "fasting")

        # Test updating non-existent data point
        non_updated_dp = self.ds.update_data_point("non_existent_dp_id", self.patient_id, new_payload)
        self.assertIsNone(non_updated_dp)

        # Test updating with patient_id mismatch
        other_patient = Patient(name="Other Guy")
        self.ds.add_patient(other_patient)
        mismatch_updated_dp = self.ds.update_data_point(dp.id, other_patient.id, new_payload)
        self.assertIsNone(mismatch_updated_dp)


    def test_delete_data_point(self):
        """Test deleting an existing data point."""
        dp = DataPoint(patient_id=self.patient_id,
                       experiment_id=self.experiment_id,
                       data_payload={"value": 100})
        self.ds.add_data(dp)
        self.assertIsNotNone(self.ds.get_data_point(dp.id))

        deleted_dp_id = self.ds.delete_data_point(dp.id, self.patient_id)
        self.assertEqual(deleted_dp_id, dp.id)
        self.assertIsNone(self.ds.get_data_point(dp.id))

        # Test deleting non-existent data point
        non_deleted_dp_id = self.ds.delete_data_point("non_existent_dp_id", self.patient_id)
        self.assertIsNone(non_deleted_dp_id)

if __name__ == '__main__':
    unittest.main()