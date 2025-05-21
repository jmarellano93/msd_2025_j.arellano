import json
from flask import Flask, request
import datastructure
import id_generator

app = Flask(__name__)


@app.route('/', methods=['GET'])
def index():
    return json.dumps({'name': 'David',
                       'mail': 'david.herzig@roche.com'})


@app.route('/experiment', methods=['POST', 'GET'])
def create_experiment():
    pass


@app.route('/patient', methods=['POST', 'GET'])
def create_patient():
    ds = datastructure.DataStorage()
    if request.method == 'POST':
        body = request.get_json()
        name = body['name']
        id_gen = id_generator.AlphaNumericIDGenerator()
        patient_obj = datastructure.Patient(name, id_gen.get_id())
        ds.add_patient(patient_obj)
    if request.method == 'GET':
        print('not yet implemented')

    print(ds.__dict__)

    return "123"


@app.route('/store', methods=['POST'])
def store_data():
    pass

@app.route('/upload', methods=['POST'])
def upload_data(data):
    pass


if __name__ == '__main__':
    print('Starting service...')
    app.debug = True
    app.run(host='0.0.0.0')