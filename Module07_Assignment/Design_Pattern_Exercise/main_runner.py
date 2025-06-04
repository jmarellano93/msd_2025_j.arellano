# Design_Pattern_Exercise/main_runner.py

import random
from sequence_utils import SequenceConverter  # Import from the local file


# --- Q3 & Q4: SequenceStorage (Singleton Pattern) ---
class SequenceStorage:
    """
    Q3: Stores sequences.
    Q4: Implemented as a Singleton to ensure only one instance exists.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(SequenceStorage, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        # Initialize data only if it hasn't been initialized before
        # This check prevents re-initialization if __init__ is called multiple times on the singleton
        if not hasattr(self, '_initialized'):
            self.data = {}
            self._initialized = True
            print("SequenceStorage initialized.")

    def save(self, name: str, seq: str):
        self.data[name] = seq
        print(f"Sequence '{name}' saved.")

    def read(self, name: str) -> str | None:
        return self.data.get(name)


# --- Q5: DNASequenceGenerator ---
class DNASequenceGenerator:
    """
    Q5: Generates random DNA sequences.
    (Adapted from the provided dna2protein.py)
    """
    NUCLEOTIDES = ['A', 'C', 'G', 'T']

    def create_sequence(self, length: int) -> str:
        if length <= 0:
            return ""
        return "".join(random.choice(self.NUCLEOTIDES) for _ in range(length))


# --- Q6 & Q7: Sequence Classes and Factory ---
class Sequence:
    """Base class for biological sequences."""

    def __init__(self, data: str, seq_type: str):
        self.data = data
        self.seq_type = seq_type

    def __str__(self):
        return f"{self.seq_type} Sequence: {self.data}"


class DNASequence(Sequence):
    """Represents a DNA sequence."""

    def __init__(self, data: str):
        super().__init__(data.upper(), "DNA")
        if not all(base in "ACGT" for base in self.data):
            raise ValueError("Invalid characters in DNA sequence. Must be A, C, G, or T.")


class ProteinSequence(Sequence):
    """
    Q6: Represents a Protein sequence.
    """
    # A more comprehensive list of valid amino acids could be added for validation
    VALID_AMINO_ACIDS = "ACDEFGHIKLMNPQRSTVWYX*"  # Including X for unknown and * for stop

    def __init__(self, data: str):
        super().__init__(data.upper(), "Protein")
        # Basic validation, can be expanded
        if not all(aa in self.VALID_AMINO_ACIDS for aa in self.data):
            # Be cautious with this validation if 'X' isn't always used for unknowns from translation
            pass  # print(f"Warning: Protein sequence '{data}' contains potentially non-standard characters.")


class SequenceFactory:
    """
    Q7: Factory for creating DNA or Protein sequence objects.
    """

    @staticmethod
    def create_sequence(seq_type: str, data: str) -> Sequence | None:
        """
        Creates a sequence object based on the type.
        :param seq_type: "dna" or "protein"
        :param data: The sequence string
        :return: DNASequence or ProteinSequence object, or None if type is invalid
        """
        if seq_type.lower() == "dna":
            return DNASequence(data)
        elif seq_type.lower() == "protein":
            return ProteinSequence(data)
        else:
            print(f"Error: Unknown sequence type '{seq_type}'. Cannot create sequence.")
            return None


def run_exercise():
    """Main function to demonstrate solutions to the exercise questions."""

    print("--- Medical Software Development - Design Patterns Exercise ---")

    # --- Q1: Translate the given DNA sequence ---
    print("\n--- Q1: Translate DNA to Protein ---")
    dna_given = "GTGGCCATTGTAATGGGCCGCTGAAAGGGTGCCCGATAG"
    print(f"Original DNA: {dna_given}")

    # Using SequenceConverter from sequence_utils.py
    rna_from_given_dna = SequenceConverter.transcribe_dna_to_rna(dna_given)
    print(f"Transcribed RNA: {rna_from_given_dna}")

    protein_from_given_rna = SequenceConverter.translate_rna_to_protein(rna_from_given_dna)
    print(f"Translated Protein: {protein_from_given_rna}")
    # Expected: VAIVMGR (GUG GCC AUU GUA AUG GGC CGC UGA...) UGA is STOP

    # --- Q2: Utility Class ---
    # The SequenceConverter class in sequence_utils.py fulfills this.
    # Its usage is demonstrated in Q1.
    print("\n--- Q2: Utility Class (SequenceConverter) ---")
    print("SequenceConverter class is defined in sequence_utils.py and used for Q1.")
    print("Example: SequenceConverter.transcribe_dna_to_rna('ATGC') ->",
          SequenceConverter.transcribe_dna_to_rna('ATGC'))

    # --- Q3: Store sequence in SequenceStorage ---
    print("\n--- Q3: Store in SequenceStorage ---")
    storage1 = SequenceStorage()
    storage1.save("my_dna", dna_given)
    retrieved_dna = storage1.read("my_dna")
    print(f"Retrieved DNA from storage: {retrieved_dna}")

    # --- Q4: SequenceStorage as Singleton ---
    print("\n--- Q4: SequenceStorage as Singleton ---")
    print("The SequenceStorage class is now a Singleton.")
    storage2 = SequenceStorage()  # Should be the same instance as storage1

    # Demonstrate singleton property
    print(f"Is storage1 the same instance as storage2? {storage1 is storage2}")
    storage2.save("another_dna", "ATGC")
    print(f"Reading 'my_dna' from storage2 (should exist if singleton): {storage2.read('my_dna')}")
    print(f"Reading 'another_dna' from storage1 (should exist if singleton): {storage1.read('another_dna')}")

    # --- Q5: Create a random sequence with DNASequenceGenerator ---
    print("\n--- Q5: Random DNA Sequence ---")
    generator = DNASequenceGenerator()
    random_dna_seq = generator.create_sequence(30)  # Generate a random DNA sequence of length 30
    print(f"Generated Random DNA (len 30): {random_dna_seq}")

    # Store and translate the random DNA sequence
    rna_random = SequenceConverter.transcribe_dna_to_rna(random_dna_seq)
    protein_random = SequenceConverter.translate_rna_to_protein(rna_random)
    print(f"Transcribed RNA from random DNA: {rna_random}")
    print(f"Translated Protein from random DNA: {protein_random}")
    storage1.save("random_dna_sample", random_dna_seq)

    # --- Q6 & Q7: Protein Sequences and SequenceFactory ---
    print("\n--- Q6 & Q7: Protein Sequences and SequenceFactory ---")
    # Q6 is about extending the program to work with protein sequences (ProteinSequence class)
    # Q7 is about the factory.

    # Using the factory
    print("\nUsing SequenceFactory:")
    dna_obj_from_factory = SequenceFactory.create_sequence("dna", "GATTACA")
    protein_obj_from_factory = SequenceFactory.create_sequence("protein", "MGRVA")
    invalid_obj_from_factory = SequenceFactory.create_sequence("lipid", "CHCHCH")  # Example of invalid type

    if dna_obj_from_factory:
        print(dna_obj_from_factory)
        # You can store factory-created objects in SequenceStorage as well,
        # though SequenceStorage currently stores strings.
        # You might adapt SequenceStorage to store Sequence objects if needed.
        storage1.save("factory_dna_seq_data", dna_obj_from_factory.data)

    if protein_obj_from_factory:
        print(protein_obj_from_factory)
        storage1.save("factory_protein_seq_data", protein_obj_from_factory.data)

    # Demonstrate handling ProteinSequence objects
    my_protein = ProteinSequence("TESTPROTEINX")
    print(f"Created directly: {my_protein}")

    print("\nContents of SequenceStorage at the end:")
    for name, seq_data in storage1.data.items():
        print(f"- {name}: {seq_data}")

    print("\n--- Exercise Demonstration Complete ---")


if __name__ == '__main__':
    run_exercise()