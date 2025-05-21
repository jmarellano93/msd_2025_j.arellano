class Patient:
    def __init__(self, name, id):
        self.name = name
        self.id = id

#Class Experiment???

class DataStorage:
    def __init__(self):
        self.patients = {}

    def add_patient(self, obj):
        self.patients[obj.id] = obj