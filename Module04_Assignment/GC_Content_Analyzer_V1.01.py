'''
--------------------DNA Sequences in FASTA Format Preface--------------------

FASTA format is a simple and widely used text-based format for representing
nucleotide sequences (DNA or RNA) or protein sequences.

FASTA format structure:

1) Header line (starts with a > sign)
This line contains a description or identifier for the sequence.
Example:
>CD28_Human_Chromosome_2

2) Sequence lines
The actual DNA sequence follows on the next lines (can be split over multiple lines).
Example:
ATGGCAGAGTCTCTGGAGCTTGGCTGGAGATGAAAGTG
GTGTGTGACCTGGTCTTGGAGTTTTTGCTGCTGCTGCT

Example of full FASTA file content
>CD28_Human
ATGGCTAGCTAGCTACGATCGATCGTACGTAGCTAGCTAGCTAGC
TGACTGACTGACTGACTGACTGACTGACTGACTGACTGACTGAC

There is no fixed or "correct" biological length for a DNA sequence in FASTA
format — it depends entirely on the actual sequence being represented
(e.g., a gene, a chromosome, or a synthetic fragment).
However, there are formatting conventions for how the sequence is displayed in the FASTA file:
1) Biological length
The length of the DNA sequence depends on the actual gene or genomic region.
For example:
A short gene might be ~500–1500 base pairs (bp).
A full chromosome might be millions of bp long.
2) FASTA formatting convention
The sequence can be any length, but it’s typically wrapped at 60 or 80 characters per line for readability.
This line wrapping is just visual and doesn’t affect the data.

The GC-content of a DNA string is given by the percentage of symbols in the string that are either ’C’ or ’G’.

Key notes:
1) It supports multiple sequences in one file (each starts with its own > header).
2) It's case-insensitive (A = a, T = t, etc.).
3) It’s used widely in bioinformatics tools for tasks like alignment, annotation, and GC-content analysis.
4) Sequence length depends on your biological data but is conventionally 60 of 80 characters long.
5) GC content = percentage of string composed of 'C' and/or 'G' symbols.

---------------------------------------------------------------------
'''

# This software performs the following functions:
# 1) Prompts the user to either:
    # A) enter their own DNA sequence of up to 1 billion bases in FASTA format for GC-content processing;
    # B) load and process a FASTA file of up to 1GB (uncompressed) for GC-content processing; or
    # C) generate a random DNA sequence of 1 billion bases in FASTA format.
# 2) If the user chooses to generate a random sequence, the software will:
    # A) Generate a random sequence of the desired number of characters in length using the DNA bases: 'A', 'T', 'C', and 'G'.
    # B) Format the sequence to wrap lines (every 80 characters).
    # C) Add a FASTA header line starting with >Random_DNA_Seq_(random number from 01-99).
    # D) Print to console.
# 3) Using the user's DNA sequence OR the uploaded FASTA file OR the randomly generated sequence, compute the GC
# 4) WARNING: This program can only analyze sequences formatted in accordance with the FASTA structure described in the preface.

# Importing packages:
import random
import textwrap
import os

# Type of DNA sequence data choice function.
def get_user_choice():
    while True:
        print("Choose an option:")
        print("A) Enter your own DNA sequence in FASTA format (up to 1 billion bases)")
        print("B) Load and process a FASTA file (up to 1GB uncompressed)")
        print("C) Generate a random DNA sequence (50,000–1,000,000,000 bases)")
        choice = input("Enter A, B, or C: ").strip().upper()
        if choice in {'A', 'B', 'C'}:
            return choice
        print("Invalid input. Please enter 'A', 'B', or 'C'.\n")

# Processing manually entered sequence function.
def get_user_sequence():
    while True:
        try:
            print("\nEnter your DNA sequence in FASTA format (example):")
            print(">CD28_Human")
            print("ATGGCTAGCTAGCTACGATCGATCGTACGTAGCTAGCTAGCTAGC")
            print("TGACTGACTGACTGACTGACTGACTGACTGACTGACTGACTGAC")
            print("Note: Press Enter on an empty line when you're done.")

            header = input("Header line (must start with '>'): ").strip()
            if not header.startswith(">"):
                raise ValueError("FASTA header must start with '>'")

            sequence_lines = []
            while True:
                line = input()
                if line == "":
                    break
                sequence_lines.append(line.strip().upper())

            sequence = ''.join(sequence_lines)
            if not all(base in "ATCGN" for base in sequence):
                raise ValueError("Invalid DNA characters found.")

            return header, sequence
        except Exception as e:
            print(f"\nError: {e}\nPlease re-enter your sequence.\n")

# Random sequence generation function with user-defined length.
def generate_random_sequence():
    random.seed(42)  # For reproducibility
    while True:
        try:
            length = int(input("Enter desired DNA sequence length (50,000 to 1,000,000,000 bases): ").strip())
            if not 50000 <= length <= 1_000_000_000:
                raise ValueError("Length must be between 50,000 and 1,000,000,000 bases.")
            break
        except ValueError as e:
            print(f"\nError: {e}\nPlease enter a valid integer.\n")

    bases = ['A', 'T', 'C', 'G']
    sequence = ''.join(random.choices(bases, k=length))

    header = f">Random_DNA_Seq_{random.randint(1, 99):02}"
    wrapped_sequence = '\n'.join(textwrap.wrap(sequence, 80))

    print("\nGenerated FASTA Format:")
    print(header)
    print(wrapped_sequence[:160] + "\n... [Output Truncated] ...")

    return header, sequence

#Processing FASTA file function:
def load_fasta_file():
    while True:
        try:
            filepath = input("Enter the path to the FASTA file (max 1GB): ").strip()

            if not os.path.isfile(filepath):
                raise FileNotFoundError("The file was not found.")
            if os.path.getsize(filepath) > 1 * 1024 * 1024 * 1024:
                raise ValueError("File exceeds 1GB. Please use a smaller file.")

            sequences = {}
            current_header = None
            current_sequence = []

            with open(filepath, 'r') as file:
                for line in file:
                    line = line.strip()
                    if not line:
                        continue
                    if line.startswith(">"):
                        if current_header:
                            full_seq = ''.join(current_sequence).upper()
                            if not all(base in "ATCGN" for base in full_seq):
                                raise ValueError(f"Invalid DNA characters in sequence: {current_header}")
                            sequences[current_header] = full_seq
                        current_header = line
                        current_sequence = []
                    else:
                        current_sequence.append(line)

                # Add the last sequence
                if current_header:
                    full_seq = ''.join(current_sequence).upper()
                    if not all(base in "ATCGN" for base in full_seq):
                        raise ValueError(f"Invalid DNA characters in sequence: {current_header}")
                    sequences[current_header] = full_seq

            if not sequences:
                raise ValueError("No sequences found in the FASTA file.")

            return sequences
        except Exception as e:
            print(f"\nError: {e}\nPlease try again.\n")

# Calculating GC Content function:
def calculate_gc_content(sequence):
    gc_count = sum(1 for base in sequence if base in ['G', 'C'])
    return (gc_count / len(sequence)) * 100 if sequence else 0.0


def main():
    try:
        choice = get_user_choice()

        if choice == 'A':
            header, sequence = get_user_sequence()
            sequences = {header: sequence}
        elif choice == 'B':
            sequences = load_fasta_file()
        elif choice == 'C':
            header, sequence = generate_random_sequence()
            sequences = {header: sequence}
        else:
            print("Invalid input. Please enter 'A', 'B', or 'C'.")
            return

        print("\nGC-content analysis results:")
        for header, sequence in sequences.items():
            gc_content = calculate_gc_content(sequence)
            print(f"{header}\nGC-content: {gc_content:.6f}%\n")

    except Exception as e:
        print(f"\nError: {e}")

if __name__ == "__main__":
    main()
