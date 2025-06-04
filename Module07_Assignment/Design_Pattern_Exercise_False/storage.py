# Design_Pattern_Exercise/storage.py

class SingletonMeta(type):
    """
    A metaclass for creating Singleton classes. Ensures only one instance
    of a class exists.
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            # Create the new instance BEFORE storing it, to allow __init__ to run fully.
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

class SequenceStorage(metaclass=SingletonMeta):
    def __init__(self):
        """
        Initializes the sequence storage. This method is called only once
        when the first instance is created due to the SingletonMeta metaclass.
        """
        self.data = {}
        # print("SequenceStorage __init__ called (should be once)") # For debugging

    def save(self, name: str, seq: str):
        if not isinstance(name, str) or not isinstance(seq, str):
            raise TypeError("Name and sequence must be strings.")
        self.data[name] = seq

    def read(self, name: str) -> str | None:
        if not isinstance(name, str):
            raise TypeError("Name must be a string.")
        return self.data.get(name) # Use.get() for safer access, returns None if not found

    def list_sequences(self) -> list:
        return list(self.data.keys())

    def clear_storage(self):
        """Clears all data from storage. Useful for testing or reset."""
        self.data = {}