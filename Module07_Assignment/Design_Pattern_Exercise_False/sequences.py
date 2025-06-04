# Design_Pattern_Exercise/sequences.py

class Sequence:
    def __init__(self, data: str, seq_type: str):
        if not isinstance(data, str) or not isinstance(seq_type, str):
            raise TypeError("Data and sequence type must be strings.")
        self.data = data
        self.type = seq_type

    def __str__(self):
        return f"Type: {self.type}, Length: {len(self.data)}, Sequence: {self.data}"

    def get_data(self) -> str:
        return self.data

    def get_type(self) -> str:
        return self.type

class DNASequence(Sequence):
    def __init__(self, data: str):
        # Basic validation for DNA sequence characters
        valid_chars = set("ACGT")
        if not all(char.upper() in valid_chars for char in data if char.isalpha()):
            # A more sophisticated validation might raise an error or clean the sequence.
            # For this exercise, we assume input might be somewhat clean or gets uppercased.
            pass # Or raise ValueError(f"Invalid characters in DNA sequence: {data}")
        super().__init__(data.upper(), "DNA")

class ProteinSequence(Sequence):
    def __init__(self, data: str):
        # Basic validation for Protein sequence characters could be added here
        # (e.g., ensuring they are among the 20 standard amino acids + '*')
        super().__init__(data.upper(), "Protein")