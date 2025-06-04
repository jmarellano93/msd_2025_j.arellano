# Design_Pattern_Exercise/sequence_utils.py

# Standard RNA Codon Table (maps RNA codons to amino acids)
CODON_TABLE_UTIL = {
    'AUA': 'I', 'AUC': 'I', 'AUU': 'I', 'AUG': 'M',
    'ACA': 'T', 'ACC': 'T', 'ACG': 'T', 'ACU': 'T',
    'AAC': 'N', 'AAU': 'N', 'AAA': 'K', 'AAG': 'K',
    'AGC': 'S', 'AGU': 'S', 'AGA': 'R', 'AGG': 'R',
    'CUA': 'L', 'CUC': 'L', 'CUG': 'L', 'CUU': 'L',
    'CCA': 'P', 'CCC': 'P', 'CCG': 'P', 'CCU': 'P',
    'CAC': 'H', 'CAU': 'H', 'CAA': 'Q', 'CAG': 'Q',
    'CGA': 'R', 'CGC': 'R', 'CGG': 'R', 'CGU': 'R',
    'GUA': 'V', 'GUC': 'V', 'GUG': 'V', 'GUU': 'V',
    'GCA': 'A', 'GCC': 'A', 'GCG': 'A', 'GCU': 'A',
    'GAC': 'D', 'GAU': 'D', 'GAA': 'E', 'GAG': 'E',
    'GGA': 'G', 'GGC': 'G', 'GGG': 'G', 'GGU': 'G',
    'UCA': 'S', 'UCC': 'S', 'UCG': 'S', 'UCU': 'S',
    'UUC': 'F', 'UUU': 'F', 'UUA': 'L', 'UUG': 'L',
    'UAC': 'Y', 'UAU': 'Y', 'UAA': '*', 'UAG': '*',
    'UGC': 'C', 'UGU': 'C', 'UGA': '*', 'UGG': 'W',
}


class SequenceConverter:
    @staticmethod
    def transcribe_dna_to_rna(dna_sequence: str) -> str:
        """Converts a DNA sequence to an RNA sequence."""
        if not isinstance(dna_sequence, str):
            raise TypeError("Input DNA sequence must be a string.")
        return dna_sequence.upper().replace('T', 'U')

    @staticmethod
    def translate_rna_to_protein(rna_sequence: str) -> str:
        """Translates an RNA sequence into a protein sequence."""
        if not isinstance(rna_sequence, str):
            raise TypeError("Input RNA sequence must be a string.")

        protein =
        rna_upper = rna_sequence.upper()

        # Ensure the sequence is valid RNA (contains A, U, G, C)
        valid_rna_chars = set("AUGC")
        if not all(char in valid_rna_chars for char in rna_upper if char.isalpha()):
            # This check is basic; more robust validation might be needed.
            # For now, we allow processing and let CODON_TABLE_UTIL handle unknown codons.
            pass

        for i in range(0, len(rna_upper) - (len(rna_upper) % 3), 3):
            codon = rna_upper[i:i + 3]
            amino_acid = CODON_TABLE_UTIL.get(codon, '?')  # '?' for unknown/invalid codons

            if amino_acid == '*':  # Stop codon
                protein.append(amino_acid)  # Optionally include the stop codon
                break  # Stop translation
            protein.append(amino_acid)

        return "".join(protein)