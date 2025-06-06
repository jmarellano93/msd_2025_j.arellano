# Enhancements to the Data Collection Service Documentation

Details the systematic enhancements applied to the "Data Collection Service" backend, as outlined in "Exercise Data Collection Service I". The objective is to address tasks 2 through 9, encompassing API testing, code quality improvements via static analysis, performance evaluation, logging implementation, assertion integration, unit testing, and version control practices.

### I. Introduction

The Data Collection Service is a foundational component for gathering patient data in experimental settings. The subsequent sections will elaborate on the procedures undertaken to test, refine, and extend its functionality. The process begins with initial API testing and progresses through code linting, performance profiling, and the introduction of robust error handling and verification mechanisms.

### II. System Architecture

**Table 1: Critical System File Summary**

| Filename              | File Purpose                                                                                                                                                                                                                                         | File Dependencies                                                   | Coding Language   | Category                       | Key Components/Features                                                                                                                       | Executable/Runnable                               |
|-----------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------|------------------|-------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------|
| pylintrc              | Configuration file for Pylint, allows customizing checks like disabling rules, naming conventions, and line limits.                                                                                                                                | Consumed by the Pylint tool.                                        | INI-like Config   | Configuration, Code Quality    | Sections like [MESSAGES CONTROL], [FORMAT], disables, max-line-length.                                                                        | No                                                |
| app.py                | Main Flask app file: defines endpoints for patient/experiment/data, uses HTTPBasicAuth, loads env settings, handles memory profiling.                                                                                                             | json, os, random, logging, flask, psutil, datastructure (local)     | Python            | Application Logic, API Server  | Flask instance, routes like `/patient`, logging, environment loader.                                                                           | Yes (Main app)                                    |
| datastructure.py      | Defines models for Patient, Experiment, DataPoint, their JSON encoding, and a DataStorage singleton for CRUD and persistence.                                                                                                                     | json, os, idgenerator (local), logging                              | Python            | Data Storage, Data Modeling    | Classes for entities and their encoders, plus centralized data store.                                                                          | No                                                |
| datastructure_test.py | Unit tests using `unittest` for validating CRUD operations, edge cases, and cascading deletions.                                                                                                           | unittest, datastructure                                              | Python            | Testing                        | test methods, assertion checks for each CRUD action.                                                                                           | Yes (via `python -m unittest`)                   |
| memory.py             | Illustrates memory usage and profiling with `@profile` decorator. Demonstrates memory_profiler functionality.                                                                                              | logging, memory_profiler                                             | Python            | Utility, Performance           | Single example function wrapped with `@profile`.                                                                                                | Yes (direct or `-m memory_profiler`)             |
| requirements.txt      | Lists Python package dependencies (Flask, psutil, etc.) to create a consistent environment via `pip install -r`.                                                                                           | Consumed by `pip`                                                    | Plain Text        | Dependency Management          | Library names and pinned versions.                                                                                                             | No                                                |
| dev_env.json          | Contains environment-specific variables like `log_level`, used during service boot in `app.py`.                                                                                                           | Loaded via `load_environment()` in `app.py`.                         | JSON              | Configuration                  | Key-value config data.                                                                                                                         | No                                                |
| idgenerator.py        | Defines ID generation via UUID and random number methods using abstract classes.                                                                                                                           | abc, uuid, random, logging                                           | Python            | Utility, ID Generation         | `IDGenerator`, `AlphaNumericIDGenerator`, `NumericIDGenerator`.                                                                                | Yes (has main test runner)                       |
| backend_service.log   | Runtime application log capturing server activities, requests, warnings, and errors. Useful for debugging and auditing system behavior.                                                                   | Generated by `app.py` via Python's `logging` module.                | Plain Text        | Logging, Monitoring            | Timestamped log entries, log levels (INFO, WARNING, ERROR), endpoint access logs.                                                             | No                                                |

**Table 2: System Generated JSON files for object storage**

| JSON Filename    | Generating File  | Purpose                                                       | Structure Example                                                                                                                                                                                                  |
|------------------|------------------|----------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| patients.json    | datastructure.py | Stores patient objects, where each key is a patient ID.       | {"bf9eb35c-41ce-11f0-b73e-9b1ea4d95ba0": {"name": "Billy Blaze", "id": "...", "blood_pressure": "120/80", ...}, ...}                                                                                                                       |
| experiments.json | datastructure.py | Stores experiment objects, where each key is an experiment ID.| {} (empty in the provided file, but would be {"exp_id1": {"name": "Study A", "id": "exp_id1"}, ...} when populated)                                                                                                                        |
| data.json        | datastructure.py | Stores data point objects, where each key is a data point ID. | [] (empty array in the provided file, but would be {"dp_id1": {"id": "dp_id1", "patient_id": "...", "experiment_id": "...", "data": {...}}, ...} when populated as a dictionary of data points, or an array if the structure was different) |


### III. Project Setup & Initial Environment Configuration


Before interacting with or modifying the Data Collection Service, a proper development environment must be established by:

**A. Setting Up a Virtual Environment**

It is a best practice in Python development to use virtual environments. Virtual environments isolate project dependencies, preventing conflicts between different projects.

1. Create a virtual environment by navigatting to the project's root directory (backendservice) and execute:


    Bash
    python -m venv venv


This creates a directory named venv containing the Python interpreter and 

2. Activate the virtual environment using 


    .\venv\Scripts\activate


Once activated, your terminal prompt will usually change to indicate the active virtual environment.

**B. Installing Dependencies**

The project likely has a requirements.txt file listing all necessary Python packages. Install these dependencies into the active virtual environment.


    Bash
    pip install -r requirements.txt


This command reads the requirements.txt file and installs the specified versions of each package. If a requirements.txt file is not present, dependencies like Flask (for the web service) and any others used by the project would need to be installed manually (e.g., pip install Flask).
With these steps completed, the development environment is ready for running, testing, and extending the Data Collection Service.


### IV. Task 2: Basic API Testing with Postman


Postman is a popular API platform for building and using APIs. It provides a user-friendly interface for sending HTTP requests to a server and viewing the responses. This section covers basic API testing for the Data Collection Service as per Exercise 2.1


**IV.I. Pre-requisites and Initial Setup**


Before commencing any API testing, it is essential to establish the correct operational environment. This section outlines the necessary system dependencies, service initialization steps, and basic Postman configuration required for successful test execution. Adherence to these prerequisites will ensure that the testing process is both efficient and yields reliable results.

A. System Dependencies
    To ensure the backend service operates as expected and that Postman can interact with it, the following software components must be installed and configured:

        •	Python: The backend service is developed using Python. It is recommended to use a recent stable version of Python 3 (e.g., Python 3.8 or newer).
        •	pip: The Python package installer (pip) is required to install the service's dependencies. It is typically included with Python installations.
        •	Postman: The latest version of the Postman desktop application should be installed. This tool will be used to send requests to the API and verify responses.
        •	Service Dependencies: The backend service relies on specific Python libraries detailed in a requirements.txt file. These must be installed within the appropriate Python environment.

B. Service Initialization
    
The backend Flask service (app.py) must be running to respond to API requests.

Procedure for Starting the Service:

    1.	Open a terminal or command prompt.
    2.	Navigate to the directory containing the main application file, typically app.py within the backendservice-main-src directory.
    3.	Execute the service by running the command: python app.py
    4.	Upon successful startup, the service will typically output a message indicating it is running and listening for requests. By default, this is http://127.0.0.1:5000. An example message might be: * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
    
It is crucial to verify this console output. Simply executing python app.py does not guarantee a successful launch; errors during initialization could prevent the service from starting correctly. The confirmation message in the console serves as an initial check that the service is operational.

The service's default listening address (http://127.0.0.1:5000) is used throughout these test procedures. While convenient for local development and testing, this hardcoded address can be a limitation if the service needs to be deployed to different environments or ports. To address this, Section IV.B details the use of Postman Environment Variables, allowing for a configurable base_url that can be easily adapted without modifying individual test requests. This practice significantly enhances the portability and maintainability of the test suite.
    
C. Postman Setup
    With the service running, Postman must be prepared for test execution.
    Procedure for Postman Preparation:

    1.	Launch the Postman application.
    2.	To organize the tests effectively, it is highly recommended to create a new Postman Collection. This collection will house all the individual API requests defined in this document (see Section IV.A for more details on structuring the collection).
    3.	For enhanced flexibility and to avoid repeated manual entry of common values like the base URL and authentication credentials, setting up Postman Environment Variables is strongly advised. This involves defining variables such as {{base_url}}, {{username}}, and {{password}} (see Section IV.B).

While individual requests can be created and sent ad-hoc, adopting Collections and Environment Variables from the outset significantly improves the efficiency, organization, and reusability of the tests. For a comprehensive test suite as outlined in this document, these Postman features transition the effort from simple request execution to the management of a structured and scalable test suite.


**IV.II. Core API Endpoint Test Procedures**


This section details the specific test procedures for each core API endpoint of the Digital Biomarker Data Collection Service. Each test case follows a standardized format, specifying the HTTP method, request URL, authorization details, request body (if applicable), and the expected response, including status code and body structure.

**Table 3: Summary of the API Endpoints**

| Endpoint Path                              | HTTP Method(s)   | Function Handler                    | Brief Description                                                                                                   | Authentication   | Request Body (POST/PUT)                                                                      | Key Response Details (Success)                                                                                                                             |
|-------------------------------------------|------------------|-------------------------------------|----------------------------------------------------------------------------------------------------------------------|------------------|-----------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| /                                         | GET              | index                               | Retrieves service info (name, mail, system, date).                                                                  | Required          | N/A                                                                                           | 200 OK: JSON with system info.                                                                                                                                                                     |
| /memory                                   | GET              | memory_test                         | Simulates memory usage, returns current list size and memory in MB.                                                 | Required          | N/A                                                                                           | 200 OK: JSON with list size and memory usage.                                                                                                                                                       |
| /patient                                  | POST             | create_patient                      | Creates a new patient, requires `name`.                                                                             | Required          | JSON with `name` and other attributes                                                         | 201 Created: JSON patient object with message.                                                                                                                                                       |
| /patient/<patient_id>                     | GET              | specific_patient_actions            | Retrieve a single patient.                                                                                          | Required          | N/A                                                                                           | 200 OK: JSON of patient or 404.                                                                                                                                                                     |
| /patient/<patient_id>                     | PUT              | specific_patient_actions            | Update a patient by ID.                                                                                             | Required          | JSON with updated fields                                                                      | 200 OK: JSON updated patient or 404.                                                                                                                                                                |
| /patient/<patient_id>                     | DELETE           | specific_patient_actions            | Delete patient and their data.                                                                                      | Required          | N/A                                                                                           | 200 OK: JSON with deleted ID or 404.                                                                                                                                                                |
| /patients                                 | GET              | get_all_patients                    | Retrieve all patients.                                                                                              | Required          | N/A                                                                                           | 200 OK: Array of patient objects.                                                                                                                                                                   |
| /experiment                               | POST             | create_experiment                   | Create an experiment, requires `name`.                                                                              | Required          | JSON with `name`                                                                             | 201 Created: JSON experiment object.                                                                                                                                                                |
| /experiment/<experiment_id>               | GET              | specific_experiment_actions         | Get a specific experiment.                                                                                          | Required          | N/A                                                                                           | 200 OK: JSON of experiment or 404.                                                                                                                                                                  |
| /experiment/<experiment_id>               | PUT              | specific_experiment_actions         | Update experiment fields.                                                                                           | Required          | JSON with updated values                                                                      | 200 OK: JSON updated experiment or 404.                                                                                                                                                             |
| /experiment/<experiment_id>               | DELETE           | specific_experiment_actions         | Delete experiment and related data.                                                                                 | Required          | N/A                                                                                           | 200 OK: JSON with deleted ID or 404.                                                                                                                                                                |
| /experiments                              | GET              | get_all_experiments                 | Retrieve all experiments.                                                                                           | Required          | N/A                                                                                           | 200 OK: Array of experiments.                                                                                                                                                                       |
| /patient/<patient_id>/data                | POST             | patient_data_actions                | Add a data point to a patient for a given experiment.                                                               | Required          | JSON with `experimentId` and payload                                                         | 201 Created: JSON with patientId, experimentId, dataPointId, and payload.                                                                                                                           |
| /patient/<patient_id>/data                | GET              | patient_data_actions                | Get all data points for a patient (optionally filtered).                                                            | Required          | Optional query param: `experimentId`                                                         | 200 OK: Array of data points.                                                                                                                                                                       |
| /patient/<patient_id>/data/<data_point_id>| GET              | specific_patient_data_point_actions | Get a specific data point.                                                                                          | Required          | N/A                                                                                           | 200 OK: JSON of data point or 404.                                                                                                                                                                  |
| /patient/<patient_id>/data/<data_point_id>| PUT              | specific_patient_data_point_actions | Update an existing data point.                                                                                      | Required          | JSON with new data keys and values                                                           | 200 OK: JSON updated data point or 404.                                                                                                                                                             |
| /patient/<patient_id>/data/<data_point_id>| DELETE           | specific_patient_data_point_actions | Delete a data point for a patient.                                                                                  | Required          | N/A                                                                                           | 200 OK: JSON with deleted ID or 404.                                                                                                                                                                |
| /store                                    | POST             | store_data_route                    | Saves current in-memory patient, experiment, and data point information to disk.                                    | Required          | N/A                                                                                           | 200 OK: JSON success message or 500 error.                                                                                                                                                          |

A. Testing the / (Root) Endpoint

This test verifies the basic availability and identity of the service. It serves as an initial "smoke test."

Procedure:

NOTE: Ensure prerequisites from Section I are met (dependencies installed, service running, Postman launched).

    1.	Create a new request in Postman.
    2.	Set the method to GET.
    3.	Enter the Request URL: {{base_url}}/ (e.g., http://127.0.0.1:5000/).
    4.	Go to the "Authorization" tab.
        4.1. Set Auth Type: Basic Auth.
        4.2. Username: {{username}} (e.g., user).
        4.3. Password: {{password}} (e.g., password).
    5.	Send the request.
    6.	Expected Response:
        6.1. Status Code: 200 OK.
        6.2 Body: 

            JSON
            {
                "Date": "June 5, 2025",
                "Server_Component_Version": "1.0.0",
                "System": "Digital Biomarker Course Project - Data Collection Service",
                "mail": "john.arellano@students.fhnw.ch",
                "name": "John Arellano"
            }

    7. Action: Verify all fields in the response body. The "Date" field will reflect the current date and time of the server at the moment of the request and will be dynamic. Therefore, for the "Date" field, verification should focus on its presence and correct format rather than an exact match to a static value. The requirement for authentication even on this root/status endpoint is a specific design characteristic of this API, implying a security posture where no information, not even service metadata, is provided without valid credentials.

B. Testing Patient Management Endpoints

This subsection details tests for Create, Read, Update, and Delete (CRUD) operations related to patient resources.

1. POST /patient (Create Patient)

This test validates the creation of a new patient record.

Procedure:

    1.1. Create a new request in Postman.
    1.2. Set the method to POST.
    1.3. Enter the Request URL: {{base_url}}/patient.
    1.4. Go to the "Authorization" tab:
        o	Set Auth Type: Basic Auth.
        o	Username: {{username}}.
        o	Password: {{password}}.
    1.5. Go to the "Body" tab.
        o	Select "raw". 
        o	Choose "JSON" from the dropdown menu.
    1.6. Enter the following sample JSON payload: 
       
           JSON
           {
               "name": "John Doe",
               "age": 30
           }
    
    1.7. Send the request.
    1.8. Expected Response:
      
        o	Status Code: 201 Created.
        o	Body: A JSON object containing the newly created patient's ID and other details.
        o	Body: A JSON object containing the newly created patient's ID and other details.
    
    The exact structure may vary, but a common pattern is: 
    
           JSON
           {
               "id": "<generated_patient_id>", // This ID is generated by the server
               "name": "John Doe",
               "age": 30,
               "message": "Patient created successfully" // Or a similar confirmation message
           }
    
    
    The provided example documentation suggests a response like {"id": "<generated_id>", "name": "John Doe"}. The test should verify against the API's actual response structure.
    
    1.9. Action: Note down the id value from the response body. This patient_id is crucial for subsequent tests that target a specific patient (e.g., retrieving, updating, or deleting this patient record, or adding data for this patient). It is highly recommended to store this ID in a Postman environment variable (e.g., {{patient_id}}) for easy reuse, as detailed in Section IV.C. While this test verifies the "happy path," a comprehensive test suite (see Section III) should also include tests with invalid payloads (e.g., missing name, age as a string) to check the API's input validation.


2. GET /patient/<patient_id> (Retrieve Specific Patient)

This test verifies the retrieval of a specific patient's details using their unique ID.

Procedure:

    •	Prerequisite: A valid patient_id obtained from a successful POST /patient request (see II.B.1). Use the {{patient_id}} environment variable if set.
    2.1.	Create a new request in Postman.
    2.2.	Set the method to GET.
    2.3.	Enter the Request URL: {{base_url}}/patient/{{patient_id}}. Replace {{patient_id}} with an actual, existing patient ID if not using environment variables.
    2.4.	Go to the "Authorization" tab:
        o	Set Auth Type: Basic Auth.
        o	Username: {{username}}.
        o	Password: {{password}}. (Note: The initial documentation for this endpoint omitted the Authorization step. It is assumed here that all endpoints accessing patient data require authentication, consistent with other protected endpoints. This should be verified.)
    2.5.	Send the request.
    2.6.	Expected Response (Successful Retrieval):
        o	Status Code: 200 OK.
        o	Body: A JSON object containing the patient's details. This should match the data provided during creation or last update.
       
    
           JSON
           {
               "id": "<patient_id_used_in_request>",
               "name": "John Doe", // Or the name used during creation/update
               "age": 30 // Or the age used during creation/update
           }
    
    2.7.	Expected Response (Patient Not Found):
        o	If an invalid or non-existent patient_id is used.
        o	Status Code: 404 Not Found.
        o	Body: A JSON object indicating the error. 
    
               JSON
               {
                   "error": "Patient not found"
               }
    
    2.8.	Action:
        o	For a successful request, verify that the retrieved data (name, age, id) matches the data that was originally posted or subsequently updated for that patient_id. This confirms data integrity.
        o	Explicitly test with a known non-existent patient_id (e.g., "invalid_id_123") to confirm that the API returns a 404 Not Found status and the specified error message. This verifies correct error handling for missing resources.


3. GET /patients (Retrieve All Patients - Assumed Endpoint)

This test attempts to retrieve a list of all patient records. This endpoint is assumed based on common REST API design patterns for resource collections. Its existence and behavior should be confirmed.

Procedure:

    •	Prerequisite: It is advisable to have created at least two distinct patients using POST /patient to properly observe the list structure and potentially test pagination features if implemented.
    3.1.	Create a new request in Postman.
    3.2.	Set the method to GET.
    3.3.	Enter the Request URL: {{base_url}}/patients.
    3.4.	Go to the "Authorization" tab:
        o	Set Auth Type: Basic Auth.
        o	Username: {{username}}.
        o	Password: {{password}}.
    3.5.	Send the request.
    3.6.	Expected Response:
        o	Status Code: 200 OK.
        o	Body: A JSON array of patient objects. If no patients exist in the system, an empty JSON array `` is expected.
    3.7.	Action: Verify that the response is an array and that each object in the array has the expected patient structure (id, name, age). If the API supports pagination (e.g., through query parameters like ?page=1&limit=10), these features should also be tested to ensure they function correctly, especially with a larger number of patient records. Lack of pagination on list endpoints can lead to performance issues if the number of resources grows significantly.


4. PUT /patient/<patient_id> (Update Patient - Assumed Endpoint)

This test validates the functionality for updating an existing patient's information. This is an assumed endpoint.

Procedure:

    •	Prerequisite: A valid patient_id from a previously created patient (e.g., stored in {{patient_id}}).
    4.1.	Create a new request in Postman.
    4.2.	Set the method to PUT.
    4.3.	Enter the Request URL: {{base_url}}/patient/{{patient_id}}.
    4.4.	Go to the "Authorization" tab:
        o	Set Auth Type: Basic Auth.
        o	Username: {{username}}.
        o	Password: {{password}}.
    4.5.	Go to the "Body" tab.
        o	Select "raw".
        o	Choose "JSON" from the dropdown.
    4.6.	Enter a JSON payload with the fields to be updated. For example, to update the patient's age: 
    
            JSON
            {
                "name": "John Doe", // Assuming name remains the same, or provide an updated name
                "age": 31
            }
    
    It is important to understand whether the PUT operation requires the complete patient object for replacement or if it supports partial updates. Standard RESTful PUT implies a full replacement of the resource. If only partial updates are intended, a PATCH method is typically more appropriate. This test should help determine the API's behavior.
    
    4.7.	Send the request.
    4.8.	Expected Response:
        o	Status Code: Typically 200 OK (if the updated resource is returned in the body) or 204 No Content (if no body is returned).
        o	Body (for 200 OK): The updated patient object. 
    
                JSON
                {
                    "id": "<patient_id_used_in_request>",
                    "name": "John Doe",
                    "age": 31,
                    "message": "Patient updated successfully" // Optional confirmation message
                }
    
    4.9.	Action:
        o	Verify the status code and, if a body is returned, its structure and content.
        o	Crucially, perform a subsequent GET /patient/{{patient_id}} request (as in II.B.2) to confirm that the patient's data in the system reflects the changes made by the PUT request.
        o	Test with an invalid or non-existent patient_id to ensure a 404 Not Found response is returned.
        o	Consider testing the idempotency of the PUT request (see Section III.D).

5. DELETE /patient/<patient_id> (Delete Patient - Assumed Endpoint)

This test validates the deletion of a patient record. This is an assumed endpoint.

Procedure:

    •	Prerequisite: A valid patient_id from a patient created specifically for this test (to avoid deleting data needed for other tests, or ensure cleanup procedures are in place).
    5.1.	Create a new request in Postman.
    5.2.	Set the method to DELETE.
    5.3.	Enter the Request URL: {{base_url}}/patient/{{patient_id}}.
    5.4.	Go to the "Authorization" tab:
        o	Set Auth Type: Basic Auth.
        o	Username: {{username}}.
        o	Password: {{password}}.
    5.5.	Send the request.
    5.6.	Expected Response:
        o	Status Code: Typically 200 OK (if a confirmation message is returned) or 204 No Content (standard for successful deletion with no body).
        o	Body (if 200 OK): A confirmation message. 
    
                JSON
                {
                    "message": "Patient deleted successfully",
                    "id": "<patient_id_deleted>"
                }
    
    5.7.	Action:
        o	Verify the status code.
        o	The most important verification step is to attempt to retrieve the deleted patient using a GET /patient/{{patient_id}} request. This subsequent GET request should return a 404 Not Found status, confirming the patient record has been removed.
        o	Test attempting to delete a patient with a non-existent patient_id. This should also result in a 404 Not Found response.
        o	An important consideration for the system's data integrity is how the deletion of a patient affects associated data, such as data points collected under /patient/<patient_id>/data. Depending on design and regulatory requirements, this related data might be cascade-deleted, anonymized, or orphaned. While full verification of such cascading effects may be complex, it is a critical aspect of the API's behavior.

**C. Testing Experiment Management Endpoints**

This subsection details tests for CRUD operations related to experiment resources. The structure of these tests mirrors those for patient management.

1. POST /experiment (Create Experiment)

This test validates the creation of a new experiment.

Procedure:

    1.1.	Create a new request in Postman.
    1.2.	Set the method to POST.
    1.3.	Enter the Request URL: {{base_url}}/experiment.
    1.4.	Go to the "Authorization" tab:
        o	Set Auth Type: Basic Auth.
        o	Username: {{username}}.
        o	Password: {{password}}.
    1.5.	Go to the "Body" tab.
        o	Select "raw".
        o	Choose "JSON" from the dropdown.
    1.6.	Enter the following sample JSON payload: 
    
           JSON
           {
               "name": "Heart Rate Study"
           }
    
    The example payload only includes a "name". Further testing (see Section III.A) should explore if other fields are supported or required (e.g., "description", "start_date").
    
    1.7.	Send the request.
    1.8.	Expected Response:
        o	Status Code: 201 Created.
        o	Body: 
    
            JSON
            {
                "id": "<generated_experiment_id>",
                "name": "Heart Rate Study"
            }
    
    1.9.	Action: Note down the id value from the response. This experiment_id is essential for associating patient data with this specific experiment (e.g., in POST /patient/<patient_id>/data requests). Store this ID in a Postman environment variable (e.g., {{experiment_id}}) for reuse. Experiments serve as a crucial mechanism for scoping or categorizing patient data; this linkage is a fundamental part of the API's data model.


2. GET /experiment/<experiment_id> (Retrieve Specific Experiment - Assumed Endpoint)

This test validates retrieving a specific experiment by its ID. Assumed endpoint.

Procedure:

    •	Prerequisite: A valid experiment_id from POST /experiment (e.g., {{experiment_id}}).
    2.1.	Create a new request in Postman.
    2.2.	Set the method to GET.
    2.3.	Enter the Request URL: {{base_url}}/experiment/{{experiment_id}}.
    2.4.	Go to the "Authorization" tab (Basic Auth: {{username}}/{{password}}).
    2.5.	Send the request.
    2.6.	Expected Response (Successful):
        o	Status Code: 200 OK.
        o	Body:
    
           JSON
           {
               "id": "<experiment_id_used_in_request>",
               "name": "Heart Rate Study" // Or the name used during creation
           }
    
    2.7.	Expected Response (Experiment Not Found):
        o	Status Code: 404 Not Found.
        o	Body: {"error": "Experiment not found"} (or similar).
    2.8.	Action: Verify retrieved data. Test with a valid and an invalid experiment_id.

3. GET /experiments (Retrieve All Experiments - Assumed Endpoint)

This test validates retrieving a list of all experiments. Assumed endpoint.

Procedure:

    3.1.	Create a new request in Postman.
    3.2.	Set the method to GET.
    3.3.	Enter the Request URL: {{base_url}}/experiments.
    3.4.	Go to the "Authorization" tab (Basic Auth: {{username}}/{{password}}).
    3.5.	Send the request.
    3.6.	Expected Response:
        o	Status Code: 200 OK.
        o	Body: An array of experiment objects. An empty array `` if no experiments exist.
    3.7.	Action: Verify the response structure. Consider pagination if applicable.

4. PUT /experiment/<experiment_id> (Update Experiment - Assumed Endpoint)

This test validates updating an existing experiment's details. Assumed endpoint.

Procedure:

    •	Prerequisite: A valid experiment_id (e.g., {{experiment_id}}).
    4.1.	Create a new request in Postman.
    4.2.	Set the method to PUT.
    4.3.	Enter the Request URL: {{base_url}}/experiment/{{experiment_id}}.
    4.4.	Go to the "Authorization" tab (Basic Auth: {{username}}/{{password}}).
    4.5.	Go to the "Body" tab (raw, JSON). Payload example: 
    
           JSON
           {
               "name": "Advanced Heart Rate Study"
           }
    
    4.6.	Send the request.
    4.7.	Expected Response:
        o	Status Code: 200 OK (with updated experiment) or 204 No Content.
        o	Body (if 200 OK): 
    
            JSON
            {
                "id": "<experiment_id_used_in_request>",
                "name": "Advanced Heart Rate Study"
            }
    
    4.8.	Action: Verify with a subsequent GET /experiment/{{experiment_id}}. Test with non-existent ID for 404.

5. DELETE /experiment/<experiment_id> (Delete Experiment - Assumed Endpoint)

This test validates deleting an experiment. Assumed endpoint.

Procedure:

    •	Prerequisite: A valid experiment_id (e.g., {{experiment_id}}).
    5.1.	Create a new request in Postman.
    5.2.	Set the method to DELETE.
    5.3.	Enter the Request URL: {{base_url}}/experiment/{{experiment_id}}.
    5.4.	Go to the "Authorization" tab (Basic Auth: {{username}}/{{password}}).
    5.5.	Send the request.
    5.6.	Expected Response:
        o	Status Code: 200 OK (with message) or 204 No Content.
    5.7.	Action: Verify deletion with a subsequent GET /experiment/{{experiment_id}} (expect 404). Test with non-existent ID (expect 404). A critical aspect to consider is the impact on patient data linked to this experiment. After deleting an experiment, attempting to POST /patient/<patient_id>/data using the deleted experiment_id should ideally result in an error (e.g., 400 Bad Request or 404 Not Found for the experiment reference), preventing data from being orphaned or miscategorized. This behavior ensures referential integrity.

**D. Testing Patient Data Endpoints**

This subsection focuses on endpoints for managing data collected for patients, typically linked to specific experiments.

1. POST /patient/<patient_id>/data (Add Data for Patient within an Experiment)

This test validates adding a data point for a specific patient, associated with a specific experiment.

Procedure:

    •	Prerequisites: 
        o	A valid patient_id (e.g., from {{patient_id}}).
        o	A valid experiment_id (e.g., from {{experiment_id}}).
    1.1.	Create a new request in Postman.
    1.2.	Set the method to POST.
    1.3.	Enter the Request URL: {{base_url}}/patient/{{patient_id}}/data.
    1.4.	Go to the "Authorization" tab:
         o	Set Auth Type: Basic Auth.
         o	Username: {{username}}.
         o	Password: {{password}}.
    1.5.	Go to the "Body" tab.
         o	Select "raw".
         o	Choose "JSON" from the dropdown.
    1.6.	Enter a sample JSON payload, including the experimentId: 
    
           JSON
           {
               "experimentId": "{{experiment_id}}",
               "heart_rate": 72,
               "unit": "bpm",
               "timestamp": "2025-06-05T10:30:00Z"
           }
    
    The example documentation for GET /patient/<patient_id>/data implies other data types like "blood_pressure" might be logged. The flexibility of the submitted_data schema (i.e., the fields beyond experimentId, like heart_rate) should be explored. Does the API enforce a specific schema per experiment, or is it a flexible key-value store for measurements? This has significant implications for data consistency and downstream analysis.
    
    1.7.	Send the request.
    1.8.	Expected Response:
        o	Status Code: 201 Created.
        o	Body: 
    
               JSON
               {
                   "message": "Data point added successfully for patient.",
                   "patientId": "<the_patient_id_you_used>",
                   "experimentId": "<the_experiment_id_you_used>",
                   "dataPointId": "<generated_data_point_id>",
                   "submitted_data": {
                       "experimentId": "<the_experiment_id_you_used>",
                       "heart_rate": 72,
                       "unit": "bpm",
                       "timestamp": "2025-06-05T10:30:00Z"
                   }
               }
    
    1.9.	Action: Verify all details in the response, ensuring patientId and experimentId match the request. Note the dataPointId returned by the server. This ID is crucial if the API supports operations on individual data points (e.g., retrieving, updating, or deleting a specific measurement). Store it in a Postman environment variable (e.g., {{data_point_id}}) if such operations are anticipated.

2. GET /patient/<patient_id>/data (Retrieve All Data for a Patient)

This test fetches all collected data points for a specific patient.

Procedure:

    •	Prerequisite: A valid patient_id for whom data has been previously posted using POST /patient/<patient_id>/data.
    2.1.	Create a new request in Postman.
    2.2.	Set the method to GET.
    2.3.	Enter the Request URL: {{base_url}}/patient/{{patient_id}}/data.
    2.4.	Go to the "Authorization" tab (Basic Auth: {{username}}/{{password}}).
    2.5.	Send the request.
    2.6.	Expected Response:
        o	Status Code: 200 OK.
        o	Body: The structure of this response requires careful verification. The initial documentation example ({"blood_pressure": "120/80", "heart_rate": 70}) suggests an aggregated summary of the latest or combined values. This is less common for an endpoint named to imply retrieval of all data. A more conventional RESTful response for retrieving multiple data entries would be a JSON array, where each element is a distinct data point object, including its timestamp and specific measurements: 
    
               [
                   {
                       "data": {
                           "experimentId": "af0464a9-4216-11f0-92b4-9b1ea4d95ba0",
                           "heart_rate": 72,
                           "timestamp": "2025-06-05T10:30:00Z",
                           "unit": "bpm"
                       },
                       "experiment_id": "af0464a9-4216-11f0-92b4-9b1ea4d95ba0",
                       "id": "78f4d9df-4217-11f0-9ea7-9b1ea4d95ba0",
                       "patient_id": "444fa9b9-4206-11f0-9b93-9b1ea4d95ba0"
                   }
               ]
    
        If the patient has no data, an empty array `` might be returned, or if the patient_id itself is invalid, a 404 Not Found is expected. The API's behavior for a valid patient with no data versus an invalid patient ID should be distinct and documented.
    
    2.7.	Action: Carefully examine the response structure. If it is an aggregate, determine how this aggregation is performed (e.g., latest value per metric type, average over a period). If it's an array, verify the structure of individual data point objects. If a patient has a large volume of data across numerous experiments, retrieving all data in a single, unfiltered response could be inefficient. This naturally leads to considering the need for filtering capabilities.

3. GET /patient/<patient_id>/data?experimentId=<experiment_id> (Retrieve Data for a Patient filtered by Experiment - Assumed Endpoint/Enhancement)

This test validates fetching patient data filtered by a specific experiment. This is an assumed capability, enhancing the usability of data retrieval.

Procedure:

    •	Prerequisites: 
        o	A valid patient_id who has data.
        o	A valid experiment_id for which this patient has logged data.
        o	Preferably, the patient should have data logged under multiple experiments to verify the filter's exclusivity.
    3.1.	Create a new request in Postman.
    3.2.	Set the method to GET.
    3.3.	Enter the Request URL: {{base_url}}/patient/{{patient_id}}/data?experimentId={{experiment_id}}.
    3.4.	Go to the "Authorization" tab (Basic Auth: {{username}}/{{password}}).
    3.5.	Send the request.
    3.6.	Expected Response:
        o	Status Code: 200 OK.
        o	Body: A JSON array of data point objects. All data points in the array must have an experimentId matching the one specified in the query parameter.
    
    If the patient has no data for the specified experiment_id, an empty array `` is expected.
    
    3.7.	Action: Verify that only data points associated with the queried experimentId are returned. Test with an experimentId for which the patient has no data (expect an empty array). The ability to filter data is fundamental for practical applications, allowing clients to request only relevant subsets of information. Other useful filters could include date ranges (?startDate=...&endDate=...) or specific data types (?dataType=heart_rate), which might be considered for future API enhancements.

4. GET /patient/<patient_id>/data/<data_point_id> (Retrieve Specific Data Point - Assumed Endpoint)

This test validates fetching a single, specific data point using its ID. This endpoint is assumed, given that POST /patient/<patient_id>/data returns a dataPointId.

Procedure:

    •	Prerequisites: 
        o	A valid patient_id.
        o	A valid dataPointId obtained from a successful POST /patient/<patient_id>/data response (e.g., stored in {{data_point_id}}).
    4.1.	Create a new request in Postman.
    4.2.	Set the method to GET.
    4.3.	Enter the Request URL: {{base_url}}/patient/{{patient_id}}/data/{{data_point_id}}.
    4.4.	Go to the "Authorization" tab (Basic Auth: {{username}}/{{password}}).
    4.5.	Send the request.
    4.6.	Expected Response (Successful):
         o	Status Code: 200 OK.
         o	Body: The specific data point object.
    
               JSON
               {
                   "dataPointId": "<data_point_id_used_in_request>",
                   "experimentId": "<associated_experiment_id>",
                   "heart_rate": 72, // Or other specific data fields
                   "unit": "bpm",
                   "timestamp": "2025-06-05T10:30:00Z"
               }
    
    4.7.	Expected Response (Data Point Not Found): 
            o	Status Code: 404 Not Found.
            o	Body: {"error": "Data point not found"} (or similar).
    4.8.	Action: Verify that the retrieved data point matches the data that was originally posted. Test with an invalid or non-existent data_point_id to confirm 404 Not Found handling. The existence of a dataPointId upon creation implies its utility for later retrieval or management of that specific entry.

5. PUT /patient/<patient_id>/data/<data_point_id> (Update Specific Data Point - Assumed Endpoint)

This test validates updating an existing specific data point. This is an assumed endpoint.

Procedure:

    •	Prerequisites: 
        o	A valid patient_id.
        o	A valid dataPointId for an existing data point (e.g., {{data_point_id}}).
    5.1.	Create a new request in Postman.
    5.2.	Set the method to PUT.
    5.3.	Enter the Request URL: {{base_url}}/patient/{{patient_id}}/data/{{data_point_id}}.
    5.4.	Go to the "Authorization" tab (Basic Auth: {{username}}/{{password}}).
    5.5.	Go to the "Body" tab (raw, JSON). Enter a payload with the fields to be updated. For example, correcting a heart rate value: 
    
           JSON
           {
               "experimentId": "{{experiment_id}}", // Typically, experimentId might not be updatable
               "heart_rate": 75, // Updated value
               "unit": "bpm",
               "timestamp": "2025-06-05T10:30:00Z" // Timestamp might also be corrected
           }
    
    It is important to determine which fields of a data point are mutable. For instance, changing the experimentId or timestamp of an existing record might have significant implications for data analysis and audit trails. Some systems may enforce immutability for certain fields or for data points altogether once logged.
    
    5.6.	Send the request.
    5.7.	Expected Response: 
         o	Status Code: 200 OK (if the updated data point is returned) or 204 No Content.
         o	Body (if 200 OK): The updated data point object.
    5.8.	Action: Verify the status code and response body. Critically, perform a subsequent GET /patient/{{patient_id}}/data/{{data_point_id}} request to confirm that the data point reflects the changes. Test with an invalid data_point_id (expect 404). The API's policy on data mutability (i.e., whether historical data can be altered) is a key characteristic revealed by this endpoint's behavior.

6. DELETE /patient/<patient_id>/data/<data_point_id> (Delete Specific Data Point - Assumed Endpoint)

This test validates deleting a specific data point. This is an assumed endpoint.

Procedure:

    •	Prerequisites: 
        o	A valid patient_id.
        o	A valid dataPointId for an existing data point created for this test (e.g., {{data_point_id}}).
    6.1.	Create a new request in Postman.
    6.2.	Set the method to DELETE.
    6.3.	Enter the Request URL: {{base_url}}/patient/{{patient_id}}/data/{{data_point_id}}.
    6.4.	Go to the "Authorization" tab (Basic Auth: {{username}}/{{password}}).
    6.5.	Send the request.
    6.6.	Expected Response:
         o	Status Code: 200 OK (with a confirmation message) or 204 No Content.
    6.7.	Action: Verify the status code. Confirm deletion by attempting a GET /patient/{{patient_id}}/data/{{data_point_id}} request for the deleted ID; this should return 404 Not Found. Test deleting a non-existent data_point_id (expect 404). This granular deletion capability is useful for data hygiene, allowing for the removal of erroneous individual entries without affecting other valid data for the patient or experiment.

**E. Testing Authentication & Authorization**

This section consolidates tests specifically focused on verifying the API's authentication and authorization mechanisms. The consistent specification of Basic Auth across various endpoints in the provided documentation implies that most, if not all, endpoints are protected.

Test Cases:

1. Accessing Endpoints without Credentials:


    o	Procedure: For each representative protected endpoint (e.g., GET /, POST /patient, GET /patient/{{patient_id}}, POST /experiment, POST /patient/{{patient_id}}/data), attempt to send the request without including an "Authorization" header, or by providing an empty/malformed header.
    o	Expected Response: 401 Unauthorized status code. The response body might contain an error message, e.g.:
    
                JSON
                {
                    "error": "Authentication required"
                }
    
    o	Action: Verify the 401 Unauthorized status code and, if present, the structure and content of the error message.


2. Accessing Endpoints with Invalid Credentials:


    o	Procedure: For each representative protected endpoint, send a request using Basic Auth but provide an incorrect username, an incorrect password, or both (e.g., username: invalid_user, password: wrong_password).
    o	Expected Response: 401 Unauthorized status code. (Some systems might use 403 Forbidden for failed authentication, but 401 is more standard for credential issues).
    o	Action: Verify the 401 Unauthorized status code and any accompanying error message.


3. Consistency of Authentication Requirement:


    o	The initial documentation for GET /patient/<patient_id> (step 5 in the user's example) notably omits the Authorization setup step, whereas other endpoints like GET / (root) and all POST examples explicitly include it. This could be an oversight in the example documentation or reflect an actual inconsistency in the API's security model. If GET /patient/<patient_id> were indeed unauthenticated while POST /patient (creation) and POST /patient/<patient_id>/data (data submission) are authenticated, this would represent an unusual and potentially insecure design.
    o	Action: For these test procedures, it is assumed that all endpoints handling patient, experiment, or patient-specific data require authentication. Tests should verify this assumption across all relevant GET, POST, PUT, and DELETE operations. Any endpoint found to be accessible without authentication when it should be protected constitutes a significant security finding.


4. (If Applicable) Role-Based Access Control (RBAC) Testing:


    o	If the API implements different user roles (e.g., 'administrator', 'researcher', 'data-entry personnel') with varying levels of permissions, specific tests must be designed to verify RBAC. This is an advanced scenario not explicitly detailed in the initial documentation but is a common feature in multi-user systems.
    o	Example Scenario: If a 'researcher' role can read patient data (GET /patient/<id>/data) but cannot delete patients (DELETE /patient/<id>), while an 'administrator' role can perform deletions.
    o	Procedure: This would require multiple sets of Basic Auth credentials, each corresponding to a different role. Tests would involve attempting actions permitted and denied for each role.
    o	Expected Response: For denied actions, a 403 Forbidden status code is typically expected, indicating that the authenticated user does not have the necessary permissions for the requested operation.
    o	Action: Verify that users are restricted to actions appropriate for their assigned roles.

The pervasive use of Basic Authentication means that credentials (username and password) are sent with every request, Base64 encoded. While this encoding makes them unreadable at a glance, it is not encryption. Therefore, Basic Auth is only secure when transmitted over an encrypted connection (HTTPS). For any production deployment or when handling sensitive data over non-local networks, the use of HTTPS is non-negotiable to protect credentials from interception. This is a critical deployment consideration, further discussed in Section V.D.

### V. Task 3: Pylint for Code Quality Enhancement

Static code analysis: Pylint is a widely adopted tool for Python that checks for errors, enforces a coding standard, and looks for code smells. The goal is to achieve a Pylint score of at least 4.0 for the project's Python files.

**A. Installation and Execution**

Installation: If not already part of the project environment, Pylint can be installed via pip:

    Bash
    pip install pylint

This is already in requirements.txt, so they should be present if pip install -r requirements.txt was run.

Execution: Navigate to the backendservice-main-src directory in the terminal and run Pylint on each Python file:

    Bash
    pylint app.py
    pylint datastructure.py
    pylint idgenerator.py
    pylint memory.py
    Alternatively, to lint multiple files:

    Bash
    pylint app.py datastructure.py idgenerator.py memory.py

**B. Addressing Pylint Issues**

Pylint provides a detailed report, including a score out of 10. Common issues include:

1. Missing docstrings (C0114: missing-module-docstring, C0115: missing-class-docstring, C0116: missing-function-docstring)
2. Invalid constant names (C0103: invalid-name, for constants not in UPPER_CASE)
3. Invalid variable/argument/function names (C0103: invalid-name, for variables not in snake_case)
4. Line too long (C0301: line-too-long)
5. Unused imports (W0611: unused-import)
6. Too few public methods (R0903: too-few-public-methods)

**C . Pylint Configuration File (.pylintrc)**

For more fine-grained control or to disable specific checks project-wide (e.g., if R0903: too-few-public-methods is deemed acceptable for certain simple classes), a .pylintrc file can be generated and customized:

    Bash
    pylint --generate-rcfile >.pylintrc
    Then, edit this file to adjust settings. For this exercise, direct code modifications are the primary focus to meet the score requirement.

### VI. Task 4: Embedding a Code Checker in the Development Environment (IDE)

Integrating static analysis tools directly into the Integrated Development Environment (IDE) provides real-time feedback to developers, allowing for immediate correction of code style and potential errors. This streamlines the development process and helps maintain code quality continuously. For PyCharm, Pylint can be configured as an external tool or, more commonly, PyCharm's built-in inspection capabilities (which often include Pylint or Pylint-like checks) are utilized.

**A. Configuring Pylint in PyCharm**

    1) Ensure Pylint is installed in the Python interpreter configured for the project.
    2) Enable Pylint integration in PyCharm:
        2.1) Go to File > Settings (or PyCharm > Preferences on macOS).
        2.2) Navigate to Tools > External Tools.
        2.3) Click the + icon to add a new tool.
        2.4) Configuration:
            2.4.1) Name: Pylint Current File
            2.4.2)Program: Specify the path to the pylint executable. This can often be found using which pylint (Linux/macOS) or where pylint (Windows) in the project's virtual environment terminal. For example: $PyInterpreterDirectory$/python -m pylint or the direct path to pylint.exe.
            2.4.3)Arguments: $FilePath$ (to lint the currently open file).
            2.4.4)Working directory: $ProjectFileDir$/backendservice-main-src (or simply $FileDir$).
        Click OK.
    3) Running the External Tool:
        3.1) Open a Python file (e.g., app.py).
        3.2) Go to Tools > External Tools > Pylint Current File.
        3.3) The Pylint output will appear in the "Run" tool window.

**B. Utilizing PyCharm's Built-in Inspections**

PyCharm has powerful built-in code inspection capabilities that cover many of the same checks as Pylint (e.g., PEP 8 compliance, error detection). These are usually enabled by default.

    Code issues are highlighted directly in the editor.
    Hovering over highlighted code provides a description of the issue.
    Alt+Enter (or Option+Enter on macOS) on highlighted code often suggests quick fixes.
    The "Problems" tool window (View > Tool Windows > Problems) lists all issues found in the current file or project.
    By embedding a code checker, developers receive immediate visual cues about deviations from coding standards or potential bugs. This proactive approach is more efficient than running linters manually after writing significant amounts of code, fostering a habit of writing cleaner code from the outset. This is particularly beneficial in collaborative projects and for maintaining long-term code health.

### VII. Task 5: Executing Performance Tests

Performance testing is critical for identifying bottlenecks, optimizing resource usage (CPU, memory), ensuring scalability and responsiveness, and preventing issues like crashes due to out-of-memory errors. Effective performance testing involves looking at various metrics. The goal is not merely to collect data but to derive actionable insights that can lead to informed optimization decisions.

Table 4: Key Performance Metrics and Tools

| Metric Category | Specific Metric                        | Tool(s) for Measurement       | What to Look For                                                                                                                                                                                                 |
|-----------------|----------------------------------------|-------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Memory Usage    | Line-by-line memory consumption and increment | `memory_profiler` (line mode) | Specific lines of code causing large memory allocations or unexpected increases.                                                                                                                                |
| Memory Usage    | Memory usage over time                | `memory_profiler` (`mprof`)   | Steadily increasing memory usage (potential memory leak), sudden spikes, overall memory footprint under typical load. A positive slope on a trend line from `mprof plot -s` can indicate a leak.               |
| Memory Usage    | Total process memory (RSS, VMS)       | `psutil`                      | The overall Resident Set Size (RSS) and Virtual Memory Size (VMS) of the application process. High RSS can indicate heavy memory use.                                                                           |
| Memory Usage    | Process memory utilization (%)        | `psutil`                      | The percentage of total system physical memory used by the process.                                                                                                                                              |
| CPU Usage       | CPU user time, system time            | `psutil` (`process.cpu_times()`) | High overall CPU utilization, imbalance between user/system time, specific functions consuming excessive CPU (can be further investigated with CPU profilers like `cProfile` and visualized with `snakeviz`). |

**A. Preparing for Memory Profiling**

The memory_profiler package is a Python module for monitoring memory consumption of a process as well as line-by-line analysis of memory consumption for Python programs.8
Installation:


    Bash
    pip install memory_profiler matplotlib


matplotlib is required for the plotting capabilities of mprof.

**B. Line-by-Line Memory Usage**

This mode provides a detailed breakdown of memory usage for each line of code within a decorated function.

1.	Decorate functions: Import the profile decorator and apply it to the Python functions you want to analyze.


        Python
        from memory_profiler import profile

        @profile
        def process_incoming_data(data):
            # Example: Simulating data processing
            processed_data = [x * 2 for x in data.get("values",)]
            large_temp_structure = {"results": processed_data * 100}
            #... more operations...
            return len(large_temp_structure["results"])


2.	Run the script: Execute your script using the Python interpreter with the -m memory_profiler flag.


    Bash
    python -m memory_profiler your_script_containing_profiled_functions.py


3.	Interpreting output: The output will show:
    o	Line #: The line number.
    o	Mem usage: Memory usage of the Python interpreter after that line has been executed.
    o	Increment: The difference in memory usage from the previous line. Large positive increments highlight memory-intensive operations.
    o	Occurrences: How many times the line was executed (for loops, etc.).
    o	Line Contents: The code itself.
This detailed view helps pinpoint exact lines causing significant memory allocations.

**C. Time-Based Memory Usage**

For a broader view of memory consumption over the lifetime of a process, memory_profiler provides the mprof utility.

1.	Record memory usage: Run your application using mprof run.


        Bash
        mprof run python your_application.py


Or, for a non-Python executable:


        Bash
        mprof run <executable_with_args>


This creates a .dat file in the current directory containing memory usage samples over time.

2.	Plot the data: Use mprof plot to generate a graph.


        Bash
        mprof plot


This will display a graph of memory usage (in MiB) versus time (in seconds).

- Look for trends: Is memory usage stable, or does it continuously increase (suggesting a leak)?

- mprof plot -s: This option plots trend lines and their numeric slopes. A slope significantly greater than zero over a substantial period can be a strong indicator of a memory leak.


**D. Tracking Forked Child Processes**

If your application uses multiprocessing and spawns child processes, mprof can track their memory usage 9:
- mprof run --include-children python your_application.py: Sums the memory of all child processes to the parent's usage for a combined view.
- mprof run --multiprocess python your_application.py: Tracks each child process independently, generating separate lines on the plot.

**E. Process Information with psutil**

psutil (process and system utilities) is a cross-platform library for retrieving information on running processes and system utilization (CPU, memory, disks, network, sensors) in Python.10 It provides an OS-level view of the process's memory footprint.

Installation:


    Bash
    pip install psutil


Getting Process Memory Information:

You can integrate psutil into your application or a separate monitoring script to get memory details of the running service.


    Python
    import os
    import psutil

    # Get the current process
    process = psutil.Process(os.getpid())
    
    # Get memory info
    mem_info = process.memory_info()
    rss_mb = mem_info.rss / (1024 * 1024)  # Resident Set Size in MB
    vms_mb = mem_info.vms / (1024 * 1024)  # Virtual Memory Size in MB
    
    print(f"Process PID: {process.pid}")
    print(f"RSS: {rss_mb:.2f} MB") # RSS: memory unique to the process
    print(f"VMS: {vms_mb:.2f} MB") # VMS: total virtual address space
    
    # Get memory utilization percentage
    mem_percent = process.memory_percent()
    print(f"Memory Percent: {mem_percent:.2f}% of total system memory")
    
    # Get CPU times
    cpu_times = process.cpu_times()
    print(f"CPU Times: User={cpu_times.user}s, System={cpu_times.system}s")

        •	Resident Set Size (RSS): The portion of memory occupied by a process that is held in RAM. It does not include memory that is swapped out. This is often the most relevant figure for actual physical memory usage by the process.11
        •	Virtual Memory Size (VMS): The total amount of virtual address space the process is using. This includes all code, data, and shared libraries, plus swapped out pages and mapped files.11


Performance requirements are often contextual; what is "good" performance can vary. However, these tools allow developers to establish baselines, identify regressions after code changes, and diagnose specific performance issues like memory leaks or excessive CPU usage.

### VIII. Task 6: Extending the Code with a Log File

Effective logging is indispensable for monitoring application behavior, diagnosing issues, and auditing operations. This task involves integrating Python's built-in logging module into app.py to record important events to a file named backendservice.log. 

**A. Importing and Configuring the logging Module**

Modifications are made to app.py:

1. Import the logging module:


    Python
    import logging


2. Configure basic logging: This should be done early in the script, before the Flask app runs, or within the if __name__ == '__main__': block.


    Python
    # In app.py, near the top or before app.run()
    logging.basicConfig(
        filename='backendservice.log',
        level=logging.INFO, # Or logging.DEBUG for more verbosity
        format='%(asctime)s - %(levelname)s - %(name)s - %(threadName)s : %(message)s'
    )

- filename='backendservice.log': Specifies the output file.
    
- level=logging.INFO: Sets the minimum severity level to log (DEBUG, INFO, WARNING, ERROR, CRITICAL).
    
- format='...': Defines the log message format. This example includes timestamp, log level, logger name, thread name, and the message.

**B. Adding Log Statements**

Log statements should be strategically placed to capture meaningful events. Flask applications have a built-in logger accessible via app.logger. When logging.basicConfig() is called before the app is fully configured, Flask's default handlers might be overridden. It's often better to configure Flask's own logger or ensure basicConfig coexists properly.

A simpler approach for this exercise, if app.logger is not pre-configured to the desired file, is to use the root logger directly after basicConfig.

Example Log Statements in app.py:

    Python
    
    # At the beginning of app.py, after basicConfig
    logger = logging.getLogger(__name__) # Get a logger instance
    
    #... (Flask app initialization: app = Flask(__name__))...
    # It's also common to use app.logger if configured appropriately.
    # For simplicity with basicConfig, using the logger obtained above or logging.info directly.
    
    @app.route('/')
    def hello():
        """Greets the user."""
        logging.info("Root endpoint '/' was accessed.") # Using the root logger
        # Or: app.logger.info("Root endpoint '/' was accessed.") if app.logger is configured
        return jsonify({"message": "Hello, welcome to the data collection service!"})
    
    @app.route('/patient', methods=)
    def create_patient():
        """Creates a new patient."""
        #... (request handling code)...
        if not data or 'name' not in data or 'age' not in data:
            logging.warning("Failed to create patient: Missing name or age in request.")
            return jsonify({"error": "Missing name or age"}), 400
        #...
        logging.info(f"Patient created with ID: {patient_id}")
        return jsonify({"id": patient_id, "message": "Patient created successfully"}), 201
    
    # Add similar logging in other routes for:
    # - Receiving requests (e.g., GET /patient/<id>, POST /patient/<id>/data)
    # - Successful operations
    # - Errors or exceptional conditions (using logging.error() or logging.exception())
    
    if __name__ == '__main__':
        logging.info("Application starting up...")
        # Use the host and port as defined, or default to 0.0.0.0 for accessibility
        app.run(host='0.0.0.0', port=5000, debug=True) 
        logging.info("Application shutting down...") # This line might not be reached if app.run() blocks indefinitely until interrupted

**C. Verifying Log Output**

    1. Run app.py.
    2. Make requests to various endpoints using Postman or curl.
    3. Check the backendservice-main-src/backendservice.log file. It should contain entries corresponding to the configured format and the logged events.

Example log entry:

    2023-10-27 10:30:00,123 - INFO - app - MainThread : Root endpoint '/' was accessed.
    2023-10-27 10:30:05,456 - INFO - app - MainThread : Patient created with ID: some_generated_id
    Structured logging moves beyond simple print statements, offering configurable levels of detail, standardized formats, and dedicated output streams. This is crucial for production systems where direct console access is limited and long-term records of application activity are necessary for operational insight and forensic analysis in case of failures.

### IX. Task 7: Extending the Code with an Assertion

Assertions (assert statements) are a debugging aid used to declare conditions that must be true at a certain point in the code. If the condition is false, an AssertionError is raised. They are primarily used to detect internal programming errors or violations of logical invariants, not for handling runtime errors like invalid user input (which should be managed with exceptions like ValueError or custom error responses).

**A. Identifying a Suitable Location for an Assertion**

A good place for an assertion is where the code relies on a specific internal state that should have been established by prior operations.

- In datastructure.py: Inside a method that manipulates the self.patients dictionary, one could assert that a patient ID exists before attempting to modify its data, assuming other parts of the class are responsible for ensuring its creation. However, for operations like add_data_to_patient, it's more common to check and return False or raise a specific error if the patient doesn't exist, as this is a foreseeable runtime condition rather than a purely internal logic error.

A more fitting assertion might check an invariant. For example, if a patient record is expected to always have a 'name' and 'age' field after creation.

- In app.py: An assertion could be used to check a condition that is expected to be true due to the program's logic, not due to external input. For example, after calling idgenerator.generate_id(), assert that the returned ID is not None or empty.

**B. Implementing an Assertion**

Let's add an assertion to datastructure.py in the add_patient method to ensure the generated ID is valid before adding it to the internal dictionary. This assumes idgenerator.generate_id() is guaranteed to return a non-empty string if successful.

Modification to datastructure.py:

    Python
    
    #... (other code in DataStructure class)...
        def add_patient(self, name, age):
            """Creates a new patient and returns their ID."""
            patient_id = idgenerator.generate_id()
            
            # Assertion: The generated ID must be a non-empty string.
            # This checks an assumption about the behavior of idgenerator.generate_id().
            assert patient_id and isinstance(patient_id, str), "Generated patient ID is invalid."
            
            self.patients[patient_id] = {"name": name, "age": age, "data_points": {}}
            return patient_id
    #... (other code)...

**C. Purpose and Behavior of Assertions**

If idgenerator.generate_id() were to (erroneously) return None or a non-string, the assert statement would immediately raise an AssertionError with the message "Generated patient ID is invalid." This halts the program at the point of the violated assumption, making it easier to identify the bug's origin (potentially in idgenerator.py).

Assertions make implicit assumptions about the program's state explicit. They are a form of defensive programming. It's important to note that assertions can be globally disabled in Python by running the interpreter with the -O (optimize) flag. Therefore, they should not be used for input validation or for any error handling that must occur in production environments where optimization might be enabled. They are primarily for development and testing to catch internal inconsistencies.

### X. Task 8: Extending the Code with a Unit Test

Unit testing is a software testing method by which individual units of source code—sets of one or more computer program modules together with associated control data, usage procedures, and operating procedures—are tested to determine whether they are fit for use. Exercise 8 requires the development of unit tests for the Data Collection Service.

A comprehensive suite of unit tests acts as a safety net, allowing developers to refactor code or add new features with greater confidence, as tests are likely to catch regressions if existing functionality is inadvertently broken.

**A. Fundamentals of Unit Testing**

    •	Purpose: To verify that each "unit" of the software (e.g., a function, method, or class) performs as designed in isolation.
    •	Benefits 12: 
        o	Early Bug Detection: Finds problems early in the development cycle.
        o	Facilitates Refactoring: Provides confidence that changes haven't broken existing functionality.
        o	Improves Code Design: Writing testable code often leads to better, more modular designs.
        o	Acts as Documentation: Tests demonstrate how the code is intended to be used and its expected behavior.

**B. Setting up the Test Environment (Flask with pytest)**

For Flask applications, pytest along with pytest-flask is a common and powerful combination for writing unit tests.13

    1.	Installation:

        Bash
        pip install pytest pytest-flask

    2.	Test File and Function Naming Conventions 13:
        o	Test files should be named test_*.py or *_test.py.
        o	Test functions within these files should be named test_*().
        o	Test classes (optional, for grouping tests) should be named Test*.
    3.	Fixtures for Application and Test Client:

pytest uses fixtures to provide a fixed baseline upon which tests can reliably and repeatedly execute.13 These are typically defined in a conftest.py file in the tests directory or the project root. The Flask test client is crucial as it allows tests to interact with the application at the HTTP request level, simulating real client interactions without the overhead of a live server.13

Example:

    tests/conftest.py:
    Python
    import pytest
    from your_application_module import create_app  # Assuming your app is created via a factory

    @pytest.fixture(scope='module')
    def app():
        """Instance of Main flask app"""
        # Configure the app for testing (e.g., use a test database, set TESTING=True)
        # The configuration here depends on how your main Flask app is structured.
        # If you have a create_app factory:
        # app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'})
        # If you have a simple app instance:
        # from your_application_module import app as main_app
        # main_app.config.update({"TESTING": True})
        # app = main_app
    
        # This is a placeholder; adapt to your actual app structure.
        # For the provided backendservice, it's likely a direct import.
        # from backendservice import app as service_app # Assuming app.py is named backendservice.py
        # service_app.config.update({"TESTING": True}) 
        # For simplicity, let's assume an app factory 'create_app' exists in 'backendservice.app'
        # This needs to be adjusted based on the actual structure of 'backendservice'.
        # If 'backendservice' is the name of the main Python file (e.g., backendservice.py)
        # and it contains 'app = Flask(__name__)', then:
    
        # Assuming the main Flask app instance is in 'app.py' (or similar)
        # and can be imported and configured.
        # from..app import app as flask_app # Adjust import path as necessary
        # flask_app.config.update({
        # "TESTING": True,
        # # Add other test-specific configurations, e.g., a test database
        # })
        # yield flask_app
    
        # Simplified example if app is directly available
        from app import app as flask_app # Assuming your Flask app instance is in 'app.py'
        flask_app.config.update({
            "TESTING": True,
            # Potentially override JSON file paths for testing if they are configurable
            # "PATIENTS_FILE": "test_patients.json",
            # "EXPERIMENTS_FILE": "test_experiments.json",
            # "DATA_FILE": "test_data.json",
        })
    
        # If your app uses a factory pattern (e.g., create_app()):
        # app = create_app(test_config={"TESTING": True})
    
        # Setup: e.g., create temporary test JSON files
        # with open(flask_app.config, 'w') as f: f.write("")
        # with open(flask_app.config, 'w') as f: f.write("")
        # with open(flask_app.config, 'w') as f: f.write("")
    
        yield flask_app
    
        # Teardown: e.g., remove temporary test JSON files
        # import os
        # if os.path.exists(flask_app.config): os.remove(flask_app.config)
        # if os.path.exists(flask_app.config): os.remove(flask_app.config)
        # if os.path.exists(flask_app.config): os.remove(flask_app.config)
    
    
    @pytest.fixture(scope='module')
    def client(app):
        """A test client for the app"""
        return app.test_client()
    Fixtures like these help keep tests DRY (Don't Repeat Yourself) by handling common setup and teardown logic.13 The scope='module' means these fixtures are set up once per test module.
    
**C. Writing Unit Tests for the Service**

Unit tests for a Flask service typically involve using the test client to make requests to API endpoints and asserting the responses and any side effects (e.g., data written to files or a database).

Example 

    tests/test_api.py:
    Python
    import json
    
    # Assuming patients.json, experiments.json, data.json are managed by the app
    # and potentially reset or mocked for tests.
    
    def test_get_patients_initially_empty(client):
        """Test GET /patients when no patients exist."""
        response = client.get('/patients')
        assert response.status_code == 200
        assert response.json == # Assuming it returns an empty list
    
    def test_add_patient(client):
        """Test POST /patients to add a new patient."""
        patient_data = {
            "patient_id": "PTEST001",
            "name": "Test Patient One",
            "details": {"age": 30} # Assuming a flexible details structure
        }
        response = client.post('/patients', json=patient_data)
        assert response.status_code == 201  # Or 200 depending on API design
        # Assuming the response returns the created patient or a success message
        assert response.json.get("patient_id") == "PTEST001"
    
        # Verify patient was added by trying to fetch it
        getResponse = client.get('/patients/PTEST001')
        assert getResponse.status_code == 200
        assert getResponse.json.get("name") == "Test Patient One"
    
    def test_get_specific_patient_not_found(client):
        """Test GET /patients/<id> for a non-existent patient."""
        response = client.get('/patients/NONEXISTENT')
        assert response.status_code == 404
    
    def test_submit_data_for_patient(client):
        """Test POST /data to submit experimental data."""
        # First, ensure a patient and experiment could exist (or mock them)
        # For simplicity, we assume they can be implicitly created or tests are ordered
        # or the backend handles unknown patient/experiment gracefully for data submission
        # depending on its design.
        # A more robust test would ensure patient PTEST002 and experiment EXPTEST01 are set up.
        
        data_payload = {
            "patient_id": "PTEST002",
            "experiment_id": "EXPTEST01",
            "timestamp": "2024-08-01T12:00:00Z",
            "payload": {"temperature": 37.5, "notes": "Feeling well"}
        }
        response = client.post('/data', json=data_payload)
        assert response.status_code == 201 # Or 200
        assert response.json.get("message") == "Data received successfully" # Example message
    
        # Verify data was stored (assuming a GET /data endpoint or specific query)
        # This part depends heavily on how data can be retrieved.
        # For example, if GET /data?patient_id=PTEST002&experiment_id=EXPTEST01 exists:
        # data_response = client.get(f'/data?patient_id={data_payload["patient_id"]}&experiment_id={data_payload["experiment_id"]}')
        # assert data_response.status_code == 200
        # assert len(data_response.json) > 0
        # assert data_response.json["payload"]["temperature"] == 37.5
    
    def test_submit_data_missing_fields(client):
        """Test POST /data with missing required fields."""
        incomplete_payload = {
            "patient_id": "PTEST003"
            # experiment_id, timestamp, payload are missing
        }
        response = client.post('/data', json=incomplete_payload)
        assert response.status_code == 400 # Bad Request
        assert "error" in response.json # Expect an error message

Table 5: Example Unit Test Structure (Flask with Pytest)

| Test Aspect            | Example Code Snippet (Conceptual)                                                                                                                                                 | Explanation                                                                                                                                                                                                                                                                             |
|------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Setup (Fixture)        | ```python<br># conftest.py<br>@pytest.fixture<br>def client(app):<br>    return app.test_client()```                                                                               | The `client` fixture (provided by `pytest-flask` or custom) gives a test client instance to interact with the Flask app. The `app` fixture sets up the Flask app in testing mode. This is defined in `conftest.py`.                                                                   |
| Basic GET Test         | ```python<br>def test_get_items(client):<br>    response = client.get('/items')<br>    assert response.status_code == 200```                                                      | Sends a GET request to the `/items` endpoint. Asserts that the HTTP status code of the response is 200 (OK). Further assertions can be made on `response.data` or `response.json`.                                                                                                     |
| POST Test with JSON    | ```python<br>def test_create_item(client):<br>    payload = {'name': 'test_item'}<br>    response = client.post('/items', json=payload)<br>    assert response.status_code == 201``` | Sends a POST request to `/items` with a JSON payload. Asserts that the status code is 201 (Created), which is a common RESTful practice for successful resource creation. `response.json` can be checked for the created resource’s representation.                                     |
| Test with Query Params | ```python<br>def test_get_item_by_id(client):<br>    response = client.get('/items?id=123')<br>    assert response.status_code == 200  # assert specific item is returned```       | Demonstrates sending GET requests with URL query parameters (e.g., for filtering or specific resource retrieval). The `query_string` argument can also be used: `client.get('/items', query_string={'id': '123'})`.                                                                   |
| Testing Error Response | ```python<br>def test_get_nonexistent_item(client):<br>    response = client.get('/items/nonexistent999')<br>    assert response.status_code == 404```                            | Tests how the application handles requests for resources that do not exist. Asserts that the appropriate error status code (404 Not Found) is returned. The response body might also contain an error message in JSON format to assert.                                                |
| Accessing Session      | ```python<br>from flask import session<br>def test_login_sets_session(client):<br>    with client:<br>        client.post('/login', data={'user': 'test'})<br>        assert session.get('user_id') == 'test'``` | For endpoints that interact with Flask’s session, the `with client:` block ensures the request context (and thus the session) is active for assertions after the request. `client.session_transaction()` can be used to modify the session before a request. |

Running Tests:

Navigate to the project's root directory in the terminal and run pytest:

    Bash
    pytest

pytest will automatically discover and run tests from files named test_*.py or *_test.py.

**D. Achieving Good Test Coverage**

Test coverage measures the percentage of your codebase that is executed by your unit tests.

    •	Install pytest-cov: pip install pytest-cov.
    •	Run tests with coverage: pytest --cov=your_application_module (e.g., pytest --cov=app if your main code is in an app directory/module).
    •	This will output a coverage report. Aim for high coverage of critical application logic, but be pragmatic; 100% coverage is not always necessary or cost-effective.

Thorough unit testing is fundamental to building reliable and maintainable software. It ensures that individual components behave as expected and provides a safety net against regressions during development and refactoring.
