# Design_Pattern_Exercise/main_runner.py
from sequence_utils import SequenceConverter
from storage import SequenceStorage
from generators import DNASequenceGenerator, ProteinSequenceGenerator
from factories import SequenceFactory


def run_exercise_demonstrations():
    print("--- Starting Exercise Demonstrations ---")

    # --- Question 1: Translate DNA to Protein (using SequenceConverter for consistency) ---
    print("\n--- Question 1: Translate DNA to Protein ---")
    dna_sequence_given = "GTGGCATTGTAATGGGCTCCGAAAGGGTGCCCGATAG"
    print(f"Original DNA Sequence: {dna_sequence_given}")

    rna_sequence = SequenceConverter.transcribe_dna_to_rna(dna_sequence_given)
    print(f"Transcribed RNA Sequence: {rna_sequence}")

    protein_sequence_q1 = SequenceConverter.translate_rna_to_protein(rna_sequence)
    print(f"Translated Protein Sequence (Q1): {protein_sequence_q1}")

    # --- Question 2: Utility Class (SequenceConverter is already this) ---
    print("\n--- Question 2: Utility Class ---")
    print("SequenceConverter class in 'sequence_utils.py' demonstrates this.")
    dna_q2 = "AATTCCGG"
    rna_q2 = SequenceConverter.transcribe_dna_to_rna(dna_q2)
    protein_q2 = SequenceConverter.translate_rna_to_protein(rna_q2)
    print(f"Utility test - DNA: {dna_q2}, RNA: {rna_q2}, Protein: {protein_q2}")

    # --- Question 3 & 4: SequenceStorage and Singleton ---
    print("\n--- Question 3 & 4: SequenceStorage (Singleton) ---")
    storage1 = SequenceStorage()  # Get/create instance
    storage2 = SequenceStorage()  # Get same instance

    print(f"Is storage1 the same object as storage2? {id(storage1) == id(storage2)}")

    storage1.save("protein_from_q1", protein_sequence_q1)
    retrieved_protein = storage2.read("protein_from_q1")
    print(f"Protein from Q1 stored and retrieved via Singleton: {retrieved_protein}")
    print(f"Currently stored sequences: {storage1.list_sequences()}")
    storage1.clear_storage()  # Clean up for next runs or other tests
    print(f"Storage cleared. Currently stored: {storage1.list_sequences()}")

    # --- Question 5: Random DNA Sequence Generation ---
    print("\n--- Question 5: Random DNA Sequence Generation ---")
    dna_gen = DNASequenceGenerator()
    random_dna_seq_q5 = dna_gen.create_sequence(50)
    print(f"Generated Random DNA (len {len(random_dna_seq_q5)}): {random_dna_seq_q5}")

    # Process and store it using Singleton storage
    rna_random_q5 = SequenceConverter.transcribe_dna_to_rna(random_dna_seq_q5)
    protein_random_q5 = SequenceConverter.translate_rna_to_protein(rna_random_q5)
    print(f"Processed Random Protein (Q5): {protein_random_q5}")

    current_storage = SequenceStorage()  # Get instance
    current_storage.save("random_dna_q5", random_dna_seq_q5)
    current_storage.save("random_protein_q5", protein_random_q5)
    print(f"Random DNA Q5 from storage: {current_storage.read('random_dna_q5')}")

    # --- Question 6: Extending for Protein Sequences (ProteinSequenceGenerator) ---
    print("\n--- Question 6: Protein Sequence Generation ---")
    protein_gen = ProteinSequenceGenerator()
    random_protein_seq_q6 = protein_gen.create_sequence(30)
    print(f"Generated Random Protein (Q6, len {len(random_protein_seq_q6)}): {random_protein_seq_q6}")
    current_storage.save("random_protein_q6_direct", random_protein_seq_q6)
    print(f"Random Protein Q6 from storage: {current_storage.read('random_protein_q6_direct')}")

    # --- Question 7: SequenceFactory Implementation ---
    print("\n--- Question 7: SequenceFactory ---")
    factory = SequenceFactory()

    # Create a random DNA sequence using the factory
    dna_obj_factory = factory.create_sequence(sequence_type="DNA", length=45)
    print(f"Factory created DNA: {dna_obj_factory}")  # Uses __str__ from Sequence class
    current_storage.save("factory_dna_obj_data", dna_obj_factory.get_data())

    # Create a protein sequence from existing data using the factory
    existing_protein_data = "MVLSPADKTNVKAAWGKVGAHAGEYGAEALERMF"
    protein_obj_factory = factory.create_sequence(sequence_type="Protein", data=existing_protein_data)
    print(f"Factory created Protein: {protein_obj_factory}")
    current_storage.save("factory_protein_obj_data", protein_obj_factory.get_data())

    print(f"All sequences in storage: {current_storage.list_sequences()}")
    print(f"Data for 'factory_dna_obj_data': {current_storage.read('factory_dna_obj_data')}")

    print("\n--- All Demonstrations Complete ---")


if __name__ == "__main__":
    run_exercise_demonstrations()