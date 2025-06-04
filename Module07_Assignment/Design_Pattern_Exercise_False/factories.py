# Design_Pattern_Exercise/factories.py
from sequences import Sequence, DNASequence, ProteinSequence
from generators import DNASequenceGenerator, ProteinSequenceGenerator


class SequenceFactory:
    def __init__(self):
        # These generators are stateless, so they could be class-level if preferred,
        # or instantiated once if they had state or expensive setup.
        self._dna_generator = DNASequenceGenerator()
        self._protein_generator = ProteinSequenceGenerator()

    def create_sequence(self, sequence_type: str, length: int = 0, data: str = None) -> Sequence:
        """
        Creates a sequence object (DNA or Protein).
        If data is provided, it's used. Otherwise, a random sequence of 'length' is generated.
        Length must be positive if data is not provided.
        """
        if not isinstance(sequence_type, str):
            raise TypeError("Sequence type must be a string.")

        sequence_type_upper = sequence_type.upper()

        if data is not None and not isinstance(data, str):
            raise TypeError("Provided data must be a string.")
        if not isinstance(length, int):
            raise TypeError("Length must be an integer.")

        if sequence_type_upper == "DNA":
            if data is not None:
                return DNASequence(data)
            elif length > 0:
                return DNASequence(self._dna_generator.create_sequence(length))
            else:
                raise ValueError("For DNA sequence, provide data or a positive length for generation.")
        elif sequence_type_upper == "PROTEIN":
            if data is not None:
                return ProteinSequence(data)
            elif length > 0:
                return ProteinSequence(self._protein_generator.create_sequence(length))
            else:
                raise ValueError("For Protein sequence, provide data or a positive length for generation.")
        else:
            raise ValueError(f"Unknown sequence type: '{sequence_type}'. Supported types are 'DNA', 'Protein'.")